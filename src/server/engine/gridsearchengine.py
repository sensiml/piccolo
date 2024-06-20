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

# author c.knorowski
import itertools
import logging
import time
from copy import deepcopy

import engine.drivers as drivers
import pandas as pd
from datamanager.models import PipelineExecution
from engine.base.utils import clean_results
from engine.parallelexecutionengine import ParallelExecutionEngine
from library.models import Transform
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


class GridSearchEngine(ParallelExecutionEngine):
    """Base class for the pipeline execution engine."""

    def __init__(self, task_id, user, project_id, sandbox, err_queue):

        super(GridSearchEngine, self).__init__(
            task_id,
            user,
            project_id,
            sandbox,
            PipelineExecution.ExecutionTypeEnum.GRIDSEARCH,
            err_queue=err_queue,
        )

    def execute(self, grid_parameters, pipeline_json, run_parallel=True, caching=False):
        """Grid Search pipeline execution function.

        Args:
            grid_parameters (dict): A dictionary containing
            pipeline_json (json string): a json containing all of the information
             on about the pipeline to be executed
            caching (bool, optional): Turn sandbox pipeline caching on/off

        Returns:
            a tuple (data, None) where data the mean result metric from
                                 executing the pipeline
        """
        self.init_cache_manager(self._pipeline)
        self.execution_summary = []
        self._pipeline = pipeline_json
        steps_to_execute = self._pipeline
        self.grid_parameters = grid_parameters
        self.gridded_pipeline_steps = [{}]
        self.run_parallel = run_parallel
        data = ()

        for i, step in enumerate(self._pipeline):
            logger.userlog(
                {
                    "message": "Executing Pipeline Step Index {}".format(i),
                    "data": step,
                    "sandbox_uuid": self.pipeline_id,
                    "log_type": "PID",
                    "task_id": self.task_id,
                    "project_uuid": self.project_id,
                }
            )

            step_info = {
                "step_index": i + 1,
                "total_steps": len(self._pipeline),
                "step_type": step.get("type", None),
                "step_name": step.get("name"),
                "cached": False,
            }

            if step in steps_to_execute:
                step_info["runtime"] = time.time()
                step_info["cached"] = False

                self._update_step_info(step_info)

                if step["type"] == "query":
                    data, _ = self._query_driver(step)

                elif step["type"] == "featurefile":
                    raise Exception("FeatureFile not currently supported!")
                    # data, _ = self._featurefile_driver(deepcopy(step))

                elif step["type"] == "datafile":
                    data, _ = self._datafile_driver(deepcopy(step))

                elif step["type"] in ["transform", "segmenter", "sampler"]:
                    transform = Transform.objects.get(name=step["name"])
                    if transform.subtype in [
                        "Feature Vector",
                        "Feature Grouping",
                        "Outlier Filter",
                    ]:
                        data = self.grid_function_step(
                            drivers.feature_transform_caller,
                            step,
                            step_info,
                            input_type=".csv.gz",
                        )
                    else:
                        data = self.grid_function_step(
                            drivers.function_caller, step, step_info, input_type=".pkl"
                        )

                elif step["type"] == "generatorset":
                    data = self.grid_function_step(
                        drivers.feature_generation_driver,
                        step,
                        step_info,
                        input_type=".pkl",
                    )

                elif step["type"] == "selectorset":
                    data = self.grid_function_step(
                        drivers.feature_selection_driver,
                        step,
                        step_info,
                        input_type=".csv.gz",
                    )

                elif step["type"] == "tvo":
                    data = self.grid_model_step(drivers.tvo_driver, step, step_info)
                    self._cache_manager.save_result_data(
                        "grid_result", str(self.pipeline_id), data
                    )
                else:
                    raise Exception(
                        "Step type {step_type} not supported.".format(
                            step_type=step["type"]
                        )
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
            }
        )

        self._temp.clean_up_temp()

        return data, None

    def grid_function_step(self, func, step, step_info, input_type):
        """handles a grid step for transforms, segmenters generatorsets
             and selectorsets

        Args:
            func (function): the function to call
            step (dict): a single pipeline step

        Returns:
            TYPE: Description
        """

        grid_param = self.grid_parameters.get(step.get("name", None), None)

        logger.userlog(
            {
                "message": "Grid Params",
                "data": grid_param,
                "sandbox_uuid": self.pipeline_id,
                "log_type": "PID",
                "task_id": self.task_id,
                "project_uuid": self.project_id,
            }
        )

        temp_steps = self.prepare_grid_steps(grid_param, step, input_type=input_type)

        results = self.parallel_pipeline_step(
            func,
            temp_steps,
            self._team_id,
            self.project_id,
            self.pipeline_id,
            self._user.id,
            return_results=False,
            step_info=step_info,
        )

        return results

    def grid_model_step(self, func, step, step_info):
        """Handles a tvo or model_generator step for grid search

        Args:
            func (function): the function to call
            step (dict): a single pipeline step

        Returns:
            Dataframe: mean result matrix for the grid search space
        """

        grid_training_param = self.grid_parameters.get(
            step["optimizers"][0].get("name", None), None
        )
        grid_validation_param = self.grid_parameters.get(
            step["validation_methods"][0].get("name", None), None
        )
        grid_classifier_param = self.grid_parameters.get(
            step["classifiers"][0].get("name", None), None
        )

        grid_param = {}
        if grid_training_param:
            grid_param["training_method"] = grid_training_param
        if grid_validation_param:
            grid_param["validation_method"] = grid_validation_param
        if grid_classifier_param:
            grid_param["classifier_method"] = grid_classifier_param

        if not grid_param:
            grid_param = None

        temp_steps = self.prepare_grid_steps(grid_param, step, input_type=".csv.gz")

        results = self.parallel_pipeline_step(
            func,
            temp_steps,
            self._team_id,
            self.project_id,
            self.pipeline_id,
            self._user.id,
            step_info=step_info,
        )

        # update the result matrix with the grid params
        M = []
        for index, result in enumerate(results):
            if result[0]:
                for row in result[1]["model_stats"]["metrics"]:
                    row.update(flatten_dictionary(self.gridded_pipeline_steps[index]))

                M.append(pd.DataFrame(result[1]["model_stats"]["metrics"]))

        df = (
            pd.concat(M)
            .sort_values(["f1_score"], ascending=False)
            .reset_index(drop=True)
        )

        return clean_results(df.to_dict())

    def prepare_grid_steps(self, grid_param, step, input_type, **kwargs):
        """Prepare a list of pipeline steps for a specific set of grid
        parameters.
        Args:
            grid_param (dict): parameters for this current step to search
            step (dict): a pipeline step

        Returns:
            TYPE: An array of fully modified steps
        """
        parallel_steps = []
        gridded_pipeline_steps = []
        number_of_grids = len(self.gridded_pipeline_steps)

        for index in range(number_of_grids):
            if grid_param is None:
                # there can be multiple output steps, lets modify all of them
                temp_step = create_temp_step(step, index, input_type)
                temp_step["outputs"] = [
                    x + ".grid_{}".format(index) for x in step["outputs"]
                ]
                parallel_steps.append(temp_step)

            else:
                grid_permutation = get_permutated_dictionary_arrays(grid_param, step)
                grid_number = len(grid_permutation)

                for counter, grid_iteration in enumerate(grid_permutation):
                    temp_step = create_temp_step(step, index, input_type)

                    # there can be multiple output steps, lets modify all of
                    # them
                    temp_step["outputs"] = [
                        x + ".grid_{}".format(index * grid_number + counter)
                        for x in step["outputs"]
                    ]

                    if step["type"] == "tvo":
                        temp_step["optimizers"][0]["inputs"].update(
                            grid_iteration.get("training_method", {})
                        )
                        temp_step["validation_methods"][0]["inputs"].update(
                            grid_iteration.get("validation_method", {})
                        )
                        temp_step["classifiers"][0]["inputs"].update(
                            grid_iteration.get("classifier_method", {})
                        )
                    else:
                        temp_step["inputs"].update(
                            filter_update_dictionary(
                                temp_step["inputs"], grid_iteration
                            )
                        )
                        # If there is a set in temp_step we need to treat it differently
                        if temp_step.get("set", None):
                            update_set(temp_step, grid_iteration)

                    parallel_steps.append(temp_step)
                    gridded_pipeline_steps.append(
                        merge_dictionaries(
                            self.gridded_pipeline_steps[index], grid_iteration
                        )
                    )

        if grid_param:
            self.gridded_pipeline_steps = deepcopy(gridded_pipeline_steps)

        return parallel_steps


def filter_update_dictionary(inputs, grid_parameters):
    """Given two dictionaries, take only the paramaters from the second
    dictionary that also have keys in the first"""
    keys = [key for key in grid_parameters.keys() if key in inputs]

    return {param_key: grid_parameters[param_key] for param_key in keys}


def update_set(step, grid_parameters):
    """update the properites of a function in the set"""
    for index, func in enumerate(step.get("set", [])):
        name = func.get("function_name")
        if name in grid_parameters.keys():
            step["set"][index]["inputs"].update(grid_parameters[name])


def get_permutated_dictionary_arrays(grid_parameters, step):
    if step.get("set", None) or step.get("type", None) == "tvo":
        flat_dict = flatten_dictionary(grid_parameters)
        permuated_dict = permutate_dictionary_arrays(flat_dict)
        return reconstruct_dictionary_set(permuated_dict)

    return permutate_dictionary_arrays(grid_parameters)


def permutate_dictionary_arrays(grid_parameters):
    """Given a list of dictionaries containing the grid parameters to search
    over for a single step, return the full list of unique permutations."""

    keys = list(grid_parameters.keys())
    if len(keys) == 1:
        return [{keys[0]: x} for x in grid_parameters[keys[0]]]

    M = []
    for r in itertools.product(grid_parameters[keys[0]], grid_parameters[keys[1]]):
        M.append({keys[0]: r[0], keys[1]: r[1]})

    if len(keys) == 2:
        return M

    # 3 or more
    for key in keys[2:]:
        C = []
        for r in itertools.product(M, grid_parameters[key]):
            C.append(merge_dictionaries(r[0], {key: r[1]}))
        M = C

    return M


def flatten_dictionary(grid_parameters):
    """Takes a grid param with a genset argument
    and flattens the dictonary
    """
    flat_dict = {}
    for key in grid_parameters:
        if isinstance(grid_parameters[key], dict):
            for param, value in grid_parameters[key].items():
                flat_dict[key + "." + param] = value
        else:
            flat_dict[key] = grid_parameters[key]
    return flat_dict


def reconstruct_dictionary_set(permutated_dict):
    for i, flat_dict in enumerate(permutated_dict):
        grid_iteration = {}
        for key in flat_dict.keys():
            if "." in key:
                function_name = key.split(".")[0]
                param = key.split(".")[1]
                if grid_iteration.get(function_name):
                    grid_iteration[function_name].update({param: flat_dict[key]})
                else:
                    grid_iteration[function_name] = {param: flat_dict[key]}
            else:
                grid_iteration[key] = flat_dict[key]
        permutated_dict[i] = grid_iteration

    return permutated_dict


def merge_dictionaries(dict_a, dict_b):
    """Given grid parameter dictionaries, merge them into a new dict as a
    shallow copy."""
    dict_z = dict_a.copy()
    dict_z.update(dict_b)
    return dict_z


def create_temp_step(step, index, input_type):
    """Create a temporary step and replace the input and cost table with a
       reference to the grid index.

    Args:
        step (dict): A pipeline step
        index (int): Index of the current grid step

    Returns:
        dict: A grid point pipeline step.
    """
    temp_step = deepcopy(step)

    if step["type"] == "tvo":
        if temp_step["input_data"] == "temp.raw":
            temp_step["input_data"] = "temp.raw.csv.gz"
        else:
            temp_step["input_data"] = step["input_data"] + ".grid_{}.csv.gz".format(
                index
            )
        if step["validation_methods"][0].get("feature_table", None):
            temp_step["validation_methods"][0]["feature_table"] = step[
                "validation_methods"
            ][0]["feature_table"] + ".grid_{}".format(index)
    else:
        if step["inputs"]["input_data"] == "temp.raw":
            temp_step["inputs"]["input_data"] = "temp.raw.data_0" + input_type
        else:
            temp_step["inputs"]["input_data"] = (
                step["inputs"]["input_data"] + ".grid_{}".format(index) + input_type
            )
        if step["inputs"].get("feature_table", None):
            temp_step["inputs"]["feature_table"] = step["inputs"][
                "feature_table"
            ] + ".grid_{}".format(index)

    if step.get("feature_table", None):
        temp_step["feature_table"] = step["feature_table"] + ".grid_{}".format(index)

    return temp_step
