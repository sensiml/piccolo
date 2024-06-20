"""
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
"""

# Authors: C.Knorowski, M.Buehler
import time
from collections import deque
from copy import deepcopy
from uuid import uuid4

from datamanager.datasegments import dataframe_to_datasegments, get_dataframe_datatype
from datamanager.models import Query
from datamanager.tasks import querydata_async
from django.conf import settings
from django.core import serializers
from engine.base.cache_manager import CacheManager, get_cached_pipeline
from engine.base.pipeline_utils import (
    copy_querydata,
    generate_feature_table,
    get_capturefile,
    get_featurefile,
    make_summary,
)
from engine.base.utils import *
from engine import drivers
from engine.executionengine import ExecutionEngine
from library.model_validation.validation_methods import *
from library.models import Transform
from logger.log_handler import LogHandler
from pandas import concat

logger = LogHandler(logging.getLogger(__name__))


class NoInputDataException(Exception):
    pass


class TooLargeDataException(Exception):
    pass


class ProjectNotOptimized(Exception):
    pass


class TooLargeIntermediateResult(Warning):
    pass


class PipelineStepExection(Exception):
    pass


class ParallelExecutionEngine(ExecutionEngine):
    def __init__(
        self,
        task_id,
        user,
        project_id,
        sandbox,
        execution_type,
        execution_id=None,
        err_queue=deque(),
    ):
        """Base class for handling Parallel Shard Execution"""
        super(ParallelExecutionEngine, self).__init__(
            task_id, user, project_id, sandbox, execution_type, execution_id, err_queue
        )
        self.run_parallel = True

    def get_group_split(self, groups, row_memory_size):
        """split the groups up into bins that are less than max memory size"""

        sorted_keys = sorted(groups.groups.keys())
        group_list = {}
        shard_list = []
        counter = 0
        cumsum = 0
        for index, size in enumerate(groups.size()):
            cumsum += size * row_memory_size
            if cumsum > settings.SHARD_MEMORY_SPLIT_SIZE:
                if not len(shard_list):
                    if cumsum > settings.MAX_SHARD_MEMORY_SIZE:
                        raise TooLargeDataException(
                            "The size of the group cannot be processed by the pipeline without splitting up the data."
                        )
                    else:
                        group_list[counter] = [sorted_keys[index]]
                        shard_list = []
                        cumsum = 0
                        counter += 1
                else:
                    group_list[counter] = [sorted_keys[x] for x in shard_list]
                    shard_list = [index]
                    cumsum = size * row_memory_size
                    counter += 1
            else:
                shard_list.append(index)

        if len(shard_list):
            group_list[counter] = [sorted_keys[x] for x in shard_list]

        logger.userlog(
            {
                "message": "Number of Shards: {}".format(len(group_list)),
                "sandbox_uuid": self.pipeline_id,
                "log_type": "PID",
                "task_id": self.task_id,
                "project_uuid": self.project_id,
            }
        )

        return group_list

    def add_data(self, name, data, index):
        self._temp.add_variable_temp(
            name + ".data_{}".format(index), data=data, overwrite=True
        )

    def add_data_cache(self, name, data, index):
        return self._cache_manager.write_file(data, name + ".data_{}".format(index))

    def add_data_cache_no_sufffix(self, name, data):
        return self._cache_manager.write_file(data, name)

    def reduce_data(self, results, step=None, raise_errors=False):
        """Given a list of results stored in the cache, combine them into a
        single dataframe while removing the ones that failed to produce results

        result[0] is 1 or 0
        result[1] is None or Exception
        """

        def get_filename(result):
            if isinstance(result, str):
                return result
            elif isinstance(result, dict):
                return result["filename"]

        data_matrix = []

        for index, result in enumerate(results):
            if result[0] is not None:
                if result[0] == 0:
                    continue
                data = self.get_data_cache(get_filename(result[1]))
                data_matrix.append(data)
            elif raise_errors:
                if step is not None:
                    raise PipelineStepExection(
                        "Step: {}: ".format(step["name"] + get_filename(result[1]))
                    )
                else:
                    raise PipelineStepExection(get_filename(result[1]))

        data = concat(data_matrix).reset_index(drop=True)
        filename = self.add_data_cache(step["outputs"][0], data, 0)

        return [(1, make_summary(data, filename))]

    def reduce_data_names(self, results, step=None, raise_errors=False):
        """Given a list of results stored in the temp_cache, remove the ones
        that failed to produce results and return the names of the successful
        ones

        result[0] is number of rows if it is a dataframe, 1 if it is a json, 0 if there was ane error
        result[1] is filename or Exception Message
        """

        if not isinstance(results, list):
            return results

        data_name_matrix = []

        for _, result in enumerate(results):
            if result[0] is not None:
                if result[0] > 0:
                    data_name_matrix.append(result[1])
            elif raise_errors:
                if step is not None:
                    raise PipelineStepExection(
                        "Step: {}: ".format(step["name"] + result[1])
                    )
                else:
                    raise PipelineStepExection(result[1])

        return data_name_matrix

    def map_datafiles(
        self,
        data,
        output_name,
        cache_index,
        filename,
        group_columns=None,
        data_columns=None,
    ):
        """Maps a DataFrame into multiple shards based on the size"""

        groups = data.groupby(group_columns)
        groups_to_split = self.get_group_split(groups, get_row_memory_size(data))

        if sorted(data.columns) != sorted(group_columns + data_columns):
            raise ValidationError(
                "Invalid data_columns or group_columns, uploaded file {filename} has {columns} for columns. All columns must be specified".format(
                    filename=filename, columns=",".join(data.columns)
                )
            )

        cache_info = []

        for index, _ in enumerate(groups_to_split):
            tmp_data = pd.concat(
                [groups.get_group(key) for key in groups_to_split[index]]
            ).reset_index(drop=True)

            data_segments = dataframe_to_datasegments(
                tmp_data, data_columns, group_columns
            )

            cache_name = self.add_data_cache(output_name, data_segments, cache_index)

            cache_info.append((1, make_summary(data_segments, cache_name)))

            cache_index += 1

        return cache_info, cache_index

    def map_capturefiles(
        self,
        data,
        output_name,
        cache_index,
        filename,
        capture_uuid,
        fill_group_columns=None,
    ):
        """Maps a DataFrame into multiple shards based on the size"""

        # Do a group by split on the group columns

        # Do a check on the memory size of the group
        if get_row_memory_size(data) * len(data) > settings.MAX_SHARD_MEMORY_SIZE:
            raise TooLargeDataException(
                "The size of the input data processed by the pipeline without splitting up the data."
            )

        data_columns = data.columns.values.tolist()

        if fill_group_columns is None:
            fill_group_columns = [
                "segment_uuid",
                "capture_uuid",
                "Subject",
                "capture_name",
            ]
            data["segment_uuid"] = str(uuid4())
            data["capture_uuid"] = capture_uuid
            data["capture_name"] = filename
            data["Subject"] = filename
        else:
            for col in fill_group_columns:
                if col == "segment_uuid":
                    data["segment_uuid"] = str(uuid4())
                elif col == "capture_uuid":
                    data["capture_uuid"] = capture_uuid
                elif col == "capture_name":
                    data["capture_name"] = filename
                elif col == "Subject":
                    data["Subject"] = filename
                else:
                    data[col] = 1

        # TODO For backwards compatibility in DCL we let capture_driver keep its datatype in float
        data_segments = dataframe_to_datasegments(
            data,
            data_columns=data_columns,
            group_columns=fill_group_columns,
            dtype=get_dataframe_datatype(data),
        )

        cache_name = self.add_data_cache(output_name, data_segments, cache_index)

        return [(1, make_summary(data_segments, cache_name))], cache_index + 1

    def _featurefile_driver(self, step):
        if isinstance(step["name"], str):
            step["name"] = [step["name"]]

        M = []
        for name in step["name"]:
            M.append(get_featurefile(self._user, self._sandbox.project.uuid, name)[0])

        feature_vectors = pd.concat(M).reset_index(drop=True)

        feature_table = generate_feature_table(step)

        cache_name = self.add_data_cache_no_sufffix(step["outputs"][0], feature_vectors)
        _ = self.add_data_cache_no_sufffix(step["outputs"][1], feature_table)

        return [(1, make_summary(feature_vectors, cache_name))], {}

    def _datafile_driver(self, step):
        if step.get("group_columns", None) is None:
            raise Exception(
                "No metadata columns. All data requires at least one metadata column."
            )

        if isinstance(step["name"], str):
            step["name"] = [step["name"]]

        tmp_index = 0
        mapped_names = []
        for name in step["name"]:
            tmp_data, _ = get_featurefile(self._user, self._sandbox.project.uuid, name)

            # add simple group columns, may try to pull out the labels and add them here as well
            tmp_mapped_names, tmp_index = self.map_datafiles(
                tmp_data,
                step["outputs"][0],
                tmp_index,
                filename=name,
                group_columns=step.get("group_columns", None),
                data_columns=step.get("data_columns", None),
            )

            mapped_names.extend(tmp_mapped_names)

        return mapped_names, {}

    def _capturefile_driver(self, step):
        tmp_index = 0
        mapped_names = []
        for name in step["name"]:
            tmp_data, capture_uuid, _ = get_capturefile(
                self._user, self._sandbox.project.uuid, name
            )

            tmp_mapped_names, tmp_index = self.map_capturefiles(
                tmp_data,
                output_name=step["outputs"][0],
                cache_index=tmp_index,
                filename=name,
                capture_uuid=capture_uuid,
                fill_group_columns=step.get("group_columns", None),
            )

            mapped_names.extend(tmp_mapped_names)

        return mapped_names, {}

    def _querydata_driver(self, step):
        query = Query.objects.get(name=step["name"], project=self._sandbox.project)

        if query.cache is None:
            if query.task_status in [None, "CACHED", "Cached"]:
                query.task_status = "BUILDING"
                query.save(update_fields=["task_status"])
                querydata_async(
                    user_id=self._user,
                    project_id=query.project.uuid,
                    query_id=query.uuid,
                    pipeline_id=self.pipeline_id,
                    task_id=self.task_id,
                )
                query.refresh_from_db()
            elif query.task_status == "FAILED":
                raise Exception(
                    "The query failed to build. Check the query logs for details."
                )
            else:
                raise Exception(
                    "The query you have selected for this pipeline is currently building, wait until it finishes to execute a pipeline with this query. You can check the progress of the query in the query summary screen."
                )

        logger.userlog(
            {
                "message": "Number of Query Parititions: {}".format(len(query.cache)),
                "sandbox_uuid": self.pipeline_id,
                "log_type": "PID",
                "task_id": self.task_id,
                "project_uuid": self.project_id,
            }
        )

        mapped_names = []
        for size, file_name in query.cache:
            copy_querydata(query, file_name, self.pipeline_id)
            mapped_names.append((1, make_summary(size, file_name)))

        detail = {
            "name": "query",
            "value": serializers.serialize("json", [query]),
        }

        return mapped_names, detail

    def init_cache_manager(self, pipeline):
        self._cache_manager = CacheManager(
            self._sandbox, pipeline, pipeline_id=self.pipeline_id
        )

    def execute(
        self,
        pipeline,
        caching=True,
        compute_cost=True,
        store_errors=True,
        raise_errors=True,
        part_of_automl=False,
    ):
        """Main pipeline execution function.

        Args:
            pipeline (list of dicts): the pipeline to be executed
            caching (boolean): True indicates intermediate results should be cached;
                when False, caching will not happen
            compute_cost (boolean): True indicates feature extraction device costs should
                be computed; False indicates it should be suppressed
            store_errors (boolean): True indicates non-exception-raising errors (e.g. from
                feature generation) should be stored as cache variables for returning with
                pipeline results; when False, non-crashing errors will not be stored/returned;

        Returns:
             a tuple of (data, feature_table) DataFrames
        """

        self.execution_summary = []
        self._pipeline = pipeline
        steps_to_execute = self._pipeline
        data = None

        self.init_cache_manager(pipeline)

        # Initialize a cache_manager for scenarios that require it
        self._cache_manager.evict_key("errors")

        steps_to_execute, outputs = get_cached_pipeline(self._cache_manager, self._temp)
        cached_steps = len(self._pipeline) - len(steps_to_execute)

        logger.userlog(
            {
                "message": "Pipeline Summary",
                "pipeline": self._pipeline,
                "steps_to_execute": steps_to_execute,
                "sandbox_uuid": self.pipeline_id,
                "log_type": "PID",
                "task_id": self.task_id,
                "project_uuid": self.project_id,
                "team_uuid": self._team_id,
            }
        )

        for step_index, step in enumerate(self._pipeline):
            logger.userlog(
                {
                    "message": "Step index: {}".format(step_index),
                    "data": step,
                    "sandbox_uuid": self.pipeline_id,
                    "log_type": "PID",
                    "task_id": self.task_id,
                    "project_uuid": self.project_id,
                }
            )
            step_info = {
                "step_index": step_index + 1,
                "total_steps": len(self._pipeline),
                "step_type": step.get("type"),
                "step_name": step.get("name"),
                "name": step.get("name"),
                "cached": True,
            }

            def get_input_names(outputs):
                if not outputs:
                    return outputs

                if isinstance(outputs, list):
                    for item in outputs:
                        if isinstance(item, str):
                            return sorted(outputs)
                        if isinstance(item, dict):
                            return sorted([x["filename"] for x in outputs])

                raise Exception(outputs)

            if step in steps_to_execute:
                input_data = get_input_names(outputs)
                detail = None

                step_info["runtime"] = time.time()
                step_info["cached"] = False

                self._update_step_info(step_info)

                if step["type"] == "query":
                    data, detail = self._querydata_driver(deepcopy(step))

                elif step["type"] == "featurefile":
                    data, extra = self._featurefile_driver(deepcopy(step))

                elif step["type"] == "datafile":
                    data, extra = self._datafile_driver(deepcopy(step))

                elif step["type"] == "capturefile":
                    data, extra = self._capturefile_driver(deepcopy(step))

                elif step["type"] in ["transform", "segmenter", "sampler"]:
                    transform = Transform.objects.get(name=step["name"])
                    if transform.subtype == "Feature Vector":
                        data, extra = self.pipeline_step(
                            drivers.feature_transform_caller,
                            step,
                            input_data,
                            step_info=step_info,
                        )
                    else:
                        data, extra = self.pipeline_step(
                            drivers.function_caller,
                            step,
                            input_data,
                            step_info=step_info,
                        )

                elif step["type"] == "generatorset":
                    try:
                        data, extra = self.pipeline_step(
                            drivers.feature_generation_driver,
                            step,
                            input_data,
                            step_info=step_info,
                        )
                        data = self.reduce_data(data, step, raise_errors=raise_errors)
                    except Exception as e:
                        # Cache errors before raising the exception
                        self._cache_manager.write_cache_list(
                            self._temp.get_persistent_variables("errors.*"), "errors"
                        )
                        raise e

                elif step["type"] == "augmentationset":
                    data, extra = self.pipeline_step(
                        drivers.augmentation_driver,
                        step,
                        input_data,
                        step_info=step_info,
                    )

                elif step["type"] == "selectorset":
                    data, extra = self.pipeline_step(
                        drivers.feature_selection_driver,
                        step,
                        input_data,
                        step_info=step_info,
                    )

                elif step["type"] == "tvo":
                    data, extra = self._tvo_knowledgepack_driver(
                        step, outputs=input_data, step_info=step_info
                    )

                else:
                    raise Exception("Invalid Pipeline Step.")

                try:
                    if (
                        steps_to_execute[step_index + 1 - cached_steps]["type"]
                        in ["tvo", "selectorset"]
                        and len(data) > 1
                    ):
                        data = self.reduce_data(data, step, raise_errors=raise_errors)
                except IndexError:
                    pass

                outputs = self.reduce_data_names(data, step, raise_errors=raise_errors)

                if not outputs:
                    raise Exception(
                        "Step: {} - "
                        '"{}"'
                        " failed to generate any results check your pipeline parameters.".format(
                            step_index, step_info["name"]
                        )
                    )

                self._cache_manager.write_step(
                    step_index, step, self._temp, outputs, detail
                )

                step_info["runtime"] = time.time() - step_info["runtime"]

            self.execution_summary.append(step_info)

        logger.userlog(
            {
                "message": "Execution Summary",
                "data": self.execution_summary,
                "sandbox_uuid": self.pipeline_id,
                "log_type": "PID",
                "task_id": self.task_id,
                "project_uuid": self.project_id,
                "team_uuid": self._team_id,
            }
        )

        self._cache_manager.save_pipeline_result(self._pipeline, self.pipeline_id)

        self._temp.clean_up_temp()

        return data, None

    def pipeline_step(self, function_driver, step, inputs, step_info):
        temp_steps = []
        if inputs:
            for index, input_data in enumerate(sorted(inputs)):
                temp_steps.append(self.create_temp_step(step, index, input_data))
        else:
            temp_steps = [deepcopy(step)]

        results = self.parallel_pipeline_step(
            function_driver,
            temp_steps,
            self._team_id,
            self.project_id,
            self.pipeline_id,
            self._user.id,
            return_results=False,
            step_info=step_info,
        )

        return results, None

    def create_temp_step(self, step, index, input_data):
        """Create a temporary step and replace the input and cost table with a
           reference to the new index.

        Args:
            step (dict): A pipeline step
            index (int): Index of the current grid step

        Returns:
            dict: A grid point pipeline step.
        """
        temp_step = deepcopy(step)

        # get the index of the input data so we can match up the feature table
        # Note: the index of the input data may not be the same as the index
        # passed in if there was a failure in one of the pipelines

        temp_step["inputs"]["input_data"] = input_data
        temp_step["outputs"][0] = "{}.data_{}".format(step["outputs"][0], index)

        return temp_step


def get_row_memory_size(data):
    """return the size of a row in mb"""
    row_memory_size_bytes = data.iloc[:1].memory_usage()[1:].sum()
    return row_memory_size_bytes / 1e6


def check_columns_exist(data, step):
    if step.get("group_columns", None) is not None:
        for col in step["group_columns"]:
            if col not in data.columns:
                raise Exception(
                    "Specified Group Column {} not in input data!".format(col)
                )

    if step.get("data_columns", None) is not None:
        for col in step["data_columns"]:
            if col not in data.columns:
                raise Exception(
                    "Specified Data Column {} not in input data!".format(col)
                )

    return True
