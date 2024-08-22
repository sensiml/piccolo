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

import copy
import json
from ast import literal_eval
from collections import deque

import pandas as pd
from datamanager.knowledgepack import make_knowledgepack
from datamanager.models import (
    PipelineExecution,
    Query,
)
from datamanager.pipeline_queue import update_sandbox_value
from django.conf import settings
from django.forms.models import model_to_dict
from engine.base import cost_manager
from engine.base.pipeline_steps import parallel_pipeline_step
from engine.base.pipeline_utils import *
from engine.base.pipeline_utils import (
    make_recognition_pipeline,
    save_cache_as_featurefile,
)
from engine.base.temp_table import TempVariableTable
from engine.base.utils import *
from engine import drivers
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


class NoDataColumnsException(Exception):
    pass


class TVOFailedException(Exception):
    pass


class EmptySandbox(object):
    def __init__(self, uuid):
        self.uuid = uuid
        self.cache = None
        self.project = None
        self.cpu_clock_time = 0

    def save(self, **kwargs):
        pass


class ExecutionEngine(object):
    """Base class for the pipeline execution engine."""

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
        self._user = user
        self._team_id = str(user.teammember.team.uuid)
        self._pipeline = {}
        self._sandbox = sandbox
        self.task_id = task_id
        self.project_id = project_id
        self._error_queue = err_queue
        self._current_step_info = {}
        # clean the temp table for this pipeline_id before executing
        if self._sandbox is not None:
            self.pipeline_id = self._sandbox.uuid

        elif execution_id:
            self.pipeline_id = execution_id
            self._sandbox = EmptySandbox(self.pipeline_id)
        else:
            raise Exception("No pipeline id provided.")

        self._temp = TempVariableTable(pipeline_id=self.pipeline_id)
        self._temp.clean_up_temp()
        self._cache_manager = None
        self.execution_summary = []

        self.pipeline_execution = PipelineExecution(
            project_uuid=self.project_id,
            pipeline_uuid=self.pipeline_id,
            task_id=self.task_id,
            execution_type=execution_type,
            status=PipelineExecution.ExecutionStatusEnum.STARTED,
        )

        self.pipeline_execution.save()

    def update_execution_status(self, execution_type, status, wall_time):
        if isinstance(self._sandbox, EmptySandbox):
            return

        self._sandbox.refresh_from_db()
        self.pipeline_execution.refresh_from_db()

        self.pipeline_execution.execution_type = execution_type
        self.pipeline_execution.status = status

        self.pipeline_execution.save()

        return self.pipeline_execution

    def add_data(self, name, data, index=None):
        self._temp.add_variable_temp(name, data=data, overwrite=True)

    def get_data(self, name):
        return self._temp.get_variable_temp(name)

    def remove_data(self, name):
        self._temp.delete_variable(name)

    def add_data_cache(self, name, data, index=None):
        return self._cache_manager.write_file(data, name)

    def get_data_cache(self, name):
        # if isinstance(name, dict):
        #   name = name['filename']
        return self._cache_manager.get_file(name)

    def _query_driver(self, step):
        """
        # Get the query corresponding to its name AND project.
        query = Query.objects.get(name=step["name"], project=self._sandbox.project)
        result, err_report = query_data(
            self._user, query.project.uuid, query.uuid, self.pipeline_id
        )
        for error in err_report:
            context = json.loads(serializers.serialize("json", [query]))
            self._error_queue.append(
                QueryExecutionWarning(detail=error, context=context)
            )

        # Save outputs to temp variable
        for output in step["outputs"]:
            self.add_data_cache(result, output)

        return result, {}
        """
        raise Exception("Query is currently not supported")

    def _update_step_info(self, step_info):
        def add_return_value(step_info, key):
            tmp_dict = {}

            if step_info.get(key) is not None:
                tmp_dict[key] = step_info[key]

            return tmp_dict

        update_dict = {}
        update_dict.update(add_return_value(step_info, "iteration"))
        update_dict.update(add_return_value(step_info, "step_index"))
        update_dict.update(add_return_value(step_info, "step_type"))
        update_dict.update(add_return_value(step_info, "step_name"))
        update_dict.update(add_return_value(step_info, "total_steps"))
        update_dict.update(add_return_value(step_info, "name"))
        update_dict.update(add_return_value(step_info, "type"))
        update_dict.update(add_return_value(step_info, "batch"))
        update_dict.update(add_return_value(step_info, "population_size"))
        update_dict.update(add_return_value(step_info, "total_iterations"))
        update_dict.update(add_return_value(step_info, "iteration_start_index"))

        self._current_step_info = update_dict

        if self._sandbox is not None and self._sandbox.project is not None:
            update_sandbox_value(
                self._sandbox.project.uuid, self.pipeline_id, json.dumps(update_dict)
            )

    def parallel_pipeline_step_batch(
        self,
        func,
        steps,
        team_id,
        project_id,
        pipeline_id,
        user_id,
        return_results=True,
        step_info=None,
        batch_size=None,
    ):
        """Batches the pipelines into blocks before sending to parallel pipeline step for execution"""

        if step_info is None:
            step_info = {}

        if batch_size is None or batch_size > settings.MAX_BATCH_SIZE:
            batch_size = settings.MAX_BATCH_SIZE

        num_batches = len(steps) // batch_size
        results = []

        for batch in range(num_batches):
            step_info["batch"] = "{}/{}".format((batch + 1) * batch_size, len(steps))

            self._update_step_info(step_info)

            results.extend(
                parallel_pipeline_step(
                    func,
                    steps[batch * batch_size : (batch + 1) * batch_size],
                    team_id,
                    project_id,
                    pipeline_id,
                    user_id,
                    return_results,
                )
            )

        if len(steps) - (num_batches * batch_size) > 0:
            step_info["batch"] = "{}/{}".format(
                num_batches * batch_size if num_batches else len(steps), len(steps)
            )

            self._update_step_info(step_info)

            results.extend(
                parallel_pipeline_step(
                    func,
                    steps[num_batches * batch_size :],
                    team_id,
                    project_id,
                    pipeline_id,
                    user_id,
                    return_results,
                )
            )

        return results

    def parallel_pipeline_step(
        self,
        func,
        steps,
        team_id,
        project_id,
        pipeline_id,
        user_id,
        return_results=True,
        step_info=None,
    ):
        """Batches the pipelines into blocks before sending to parallel pipeline step for execution"""

        if step_info is None:
            step_info = {}

        step_info["batch"] = f"{len(steps)}"

        self._update_step_info(step_info)

        results = parallel_pipeline_step(
            func,
            steps,
            team_id,
            project_id,
            pipeline_id,
            user_id,
            return_results,
        )

        return results

    def execute(self, pipeline_json, caching=True, compute_cost=True):
        """Overwrite the main function for specific execution tasks"""

    def get_result(self, page_index=0):
        return self._cache_manager.get_result_from_cache(
            "pipeline_result.{}".format(self.pipeline_id), page_index=page_index
        )[0]

    def update_capture_configurations_object_to_uuid(self, summary):
        if isinstance(summary, dict):
            cn = summary.get("capture_configurations", None)
            uuid_list = []
            if cn:
                for c in cn:
                    uuid_list.append(str(c.uuid))

                summary["capture_configurations"] = uuid_list

        return summary

    def create_pipeline_summary(
        self, step, tvo_config, class_map, pipeline, feature_table
    ):
        # Create the summary artifacts of model generation

        summaries = {"pipeline_summary": pipeline}

        features, selected_features, feature_columns = drivers.get_selected_features(
            feature_table, self.pipeline_id
        )

        if "Sensors" in selected_features.columns and isinstance(
            selected_features.iloc[0]["Sensors"], str
        ):
            selected_features["Sensors"] = selected_features["Sensors"].apply(
                handle_array_formatting
            )

        summaries["feature_summary"] = selected_features.where(
            pd.notnull(selected_features), None
        ).to_dict(orient="records")

        summaries["class_map"] = class_map

        # Persistent transform variables
        persistent_variables = []
        for step_id in [".".join(s["outputs"][0].split(".")[1:]) for s in pipeline]:
            persistent_variables += self._temp.get_persistent_variables(
                "persist.{}.*".format(step_id)
            )

        summaries["transform_summary"] = [i["value"] for i in persistent_variables]

        # Retrieve the query, serialize, and store
        if pipeline[0]["type"] == "query":
            query = model_to_dict(
                Query.objects.get(
                    project=self._sandbox.project, name=pipeline[0]["name"]
                )
            )
            query.pop("task")
            query.pop("id")
            query.pop("project")
            query.pop("segment_info")
            segmenter = model_to_dict(
                Segmenter.objects.get(
                    project=self._sandbox.project, pk=query["segmenter"]
                )
            )

            if segmenter.get("parameters"):
                segmenter["parameters"] = json.loads(segmenter["parameters"])
            if segmenter.get("preprocess"):
                segmenter["preprocess"] = json.loads(segmenter["preprocess"])

            query["segmenter"] = segmenter

            summaries["query_summary"] = (
                self.update_capture_configurations_object_to_uuid(query)
            )

            # Retrieve the query summary, check against the pipeline summary. Find the common sensors
            sensors = [s for s in literal_eval(query["columns"]) if s in pipeline]
            summaries["sensor_summary"] = sensors
        elif pipeline[0]["type"] == "featurefile":
            summaries["query_summary"] = []
            summaries["sensor_summary"] = pipeline[0].get("data_columns", [])
        else:
            summaries["query_summary"] = []
            summaries["sensor_summary"] = []

        # Search the pipeline and attach static device configuration information
        device_config = {}
        for config_property in ["sample_size", "number_of_times", "sample_rate"]:
            values = get_config_values(pipeline, config_property)
            if values:
                device_config[config_property] = max(values)

        # Save config-specific device configuration info
        if tvo_config:
            device_config["classifier"] = tvo_config.get("classifier")
            if device_config["classifier"] in ["PME"]:
                distance_map = {"l1": 0, "lsup": 1, "dtw": 2}
                device_config["distance_mode"] = distance_map[
                    tvo_config.get("distance_mode", "L1").lower()
                ]
                device_config["classification_mode"] = (
                    1
                    if tvo_config.get("classification_mode", "rbf").lower() == "knn"
                    else 0
                )
                device_config["reserved_patterns"] = tvo_config.get(
                    "reserved_patterns", 0
                )
                device_config["reinforcement_learning"] = tvo_config.get(
                    "reinforcement_learning", False
                )
                device_config["num_channels"] = tvo_config.get("num_channels", 1)
                device_config["min_aif"] = tvo_config.get("min_aif", 2)
                device_config["max_aif"] = tvo_config.get("max_aif", 16384)

        summaries["device_configuration"] = device_config

        # Create the cost summary; requires making the recognition pipeline to get the number of ring buffers
        try:
            (
                recognition_pipeline,
                sensor_columns,
                data_columns_ordered,
            ) = make_recognition_pipeline(self._sandbox.project, **summaries)
            number_of_ring_buffers = len(data_columns_ordered)
        except (
            FeatureFileError,
            NoInputDataStreamsError,
            NoSegmentationAlgorithmException,
            FeatureSummaryException,
        ):
            number_of_ring_buffers = 0
            recognition_pipeline = []
            sensor_columns = []
            data_columns_ordered = []

        sample_size = {
            "median_sample_size": get_max_segment_size(
                recognition_pipeline[get_type_index(recognition_pipeline, "segmenter")]
            )
        }

        summaries["cost_summary"] = cost_manager.count_costs(
            features,
            sample_size,
            number_of_ring_buffers,
            self._sandbox.project,
            pipeline,
        )
        summaries["knowledgepack_summary"] = {
            "recognition_pipeline": recognition_pipeline,
            "sensor_columns": sensor_columns,
            "data_columns_ordered": data_columns_ordered,
        }

        return summaries, features

    def _tvo_knowledgepack_driver(
        self,
        step,
        save_knowledgepacks=True,
        config_index=0,
        outputs=None,
        step_info=None,
    ):
        """
        With the current API, multiple validation_methods, classifiers, and optimizers may be described.
        This method converts the above arrays of parameters into a list of allowable permutations, then
        executes the TVO algorithm for each configuration
        """
        temp_step = copy.deepcopy(step)

        if outputs:
            temp_step["input_data"] = outputs[0]

        results = self.parallel_pipeline_step(
            drivers.tvo_driver,
            [temp_step],
            self._team_id,
            self.project_id,
            self.pipeline_id,
            self._user.id,
            return_results=False,
            step_info=step_info,
        )

        if results[0][0] != 1:
            raise TVOFailedException(results[0][1])

        def get_filename(summary):
            if isinstance(summary, dict):
                return summary["filename"]

            return summary

        tvo_results = self.get_data_cache(get_filename(results[0][1]))

        # create a summary of this execution step
        summaries, feature_table = self.create_pipeline_summary(
            temp_step,
            tvo_results["model_stats"]["config"],
            tvo_results["class_map"],
            self._pipeline,
            DataFrame(json.loads(tvo_results["feature_table"])),
        )

        tvo_results["configurations"] = {}
        tvo_results["configurations"][config_index] = (
            self._update_tvo_results_with_knowledgepack(
                tvo_results["model_stats"], config_index, save_knowledgepacks, summaries
            )
        )

        filename = self.add_data_cache(temp_step["outputs"][0], tvo_results, 0)

        # drivers should return a list of the sucessful runs
        return [(1, {"filename": filename})], {}

    def _update_tvo_results_with_knowledgepack(
        self, models_stats, results_key, save_knowledgepacks, summaries
    ):
        # Determine if a KnowledgePack should be created or not.
        if save_knowledgepacks and len(models_stats["models"]) > 0:
            logger.userlog(
                {
                    "message": "Saving Knowledgepacks",
                    "sandbox_uuid": self.pipeline_id,
                    "log_type": "PID",
                    "task_id": self.task_id,
                    "project_uuid": self.project_id,
                }
            )

            # Get input_data from the pipeline
            feature_file = save_cache_as_featurefile(
                self._sandbox.project,
                self.pipeline_id,
                summaries["pipeline_summary"][-1]["input_data"] + ".data_0",
                ".csv.gz",
                label_column=summaries["pipeline_summary"][-1]["label_column"],
            )

            # create feature File Record in DB NewFeatureFile
            for index in models_stats["models"]:
                # Update costs with the cost of the neuron array

                model_size = models_stats["models"][index]["model_size"]
                summaries["cost_summary"]["model_size"] = model_size
                summaries["cost_summary"]["classifier"] = models_stats["models"][index][
                    "classifier_costs"
                ]
                model_stats = copy.deepcopy(models_stats["models"][index])
                model_parameters = model_stats.pop("parameters")

                name = self.get_kp_name(self._sandbox.name, index)

                # Create the KnowledgePack
                kp = make_knowledgepack(
                    name=name,
                    sandbox=self._sandbox,
                    index=index,
                    results_key=results_key,
                    model_stats=model_stats,
                    model_parameters=model_parameters,
                    feature_file=feature_file,
                    **summaries,
                )

                models_stats["models"][index]["KnowledgePackID"] = str(kp.uuid)

        return models_stats

    def get_kp_name(self, sandbox_name, key):
        return "{sandbox_name}_{index}".format(
            sandbox_name=sandbox_name[:30].replace(" ", "_").replace("-", "_"),
            index=key[:9].replace(" ", "_"),
        )
