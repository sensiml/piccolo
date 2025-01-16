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

from __future__ import annotations
from __future__ import print_function

import datetime
from copy import deepcopy

import pandas as pd
from pandas import DataFrame


try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import sensiml.base.utility as utility
from sensiml.datamanager.deviceconfig import DeviceConfig
from sensiml.datamanager.knowledgepack import KnowledgePack
from sensiml.datamanager.modelresults import ModelResultSet
from sensiml.datamanager.pipeline import PipelineError, PipelineStep
from sensiml.method_calls.functioncalls import FunctionCalls
from sensiml.method_calls.generatorcallset import GeneratorCallSet
from sensiml.method_calls.selectorcallset import SelectorCallSet
from sensiml.method_calls.trainandvalidationcall import TrainAndValidationCall

from typing import TYPE_CHECKING, Optional
from requests import Response

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project


class SandboxPipeline:
    """Base class for a sandbox pipeline consisting of steps"""

    def __init__(self, steps: Optional[list] = None):
        if steps is None:
            steps = list()

        self._steps = steps

    def add(self, item: PipelineStep):
        """Appends a PipelineStep object to the pipeline while performing integrity checks.

        Args:
            item: a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or TrainAndValidationCall object

        Returns:
            nothing, or raises an exception if integrity check fails
        """
        assert isinstance(item, PipelineStep)
        self._steps.append(item)

        try:
            self._check_integrity()
        except:
            self._steps.pop()
            raise

    def replace(self, item: PipelineStep, index: int):
        """Replace a pipeline step that has the same name.

        Args:
            item: a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or TrainAndValidationCall object
            index (int): index of pipeline step to replace

            Returns:
                nothing, or raises an exception if integrity check fails
        """
        assert isinstance(item, PipelineStep)
        assert item.name == self._get_step_name(index)
        backup_item = deepcopy(self._steps[index])

        self._steps[index] = item

        try:
            self._check_integrity()
        except Exception as e:
            self._steps[index] = backup_item
            raise e

    def linear_pipeline(self, item: PipelineStep) -> PipelineStep:
        """A linear step will automatically set the previous step's output to the currents step's input.

        Args:
            item (pipeline step): a pipeline step to modify

        Returns:
            pipeline step: pipeline step with updated input_data and outputs attributes
        """

        # if this is the first step
        if len(self._steps) == 0:
            if item._step_type == "FeatureFileCall":
                item.outputs = ["temp.raw", "tem.features.raw"]
            else:
                item.outputs = ["temp.raw"]
        else:
            item.input_data = self._steps[-1].outputs[0]
            # Count the number of times the name has been used to get unique
            # input/output names
            index = len(
                [
                    1
                    for s in self._steps
                    if f"temp.{item.name.replace(' ', '_')}" in s.outputs[0]
                ]
            )
            item.outputs = [f"temp.{item.name.replace(' ', '_')}{index}"]

            if item._to_dict()["type"] == "generatorset":
                item.outputs.append(
                    f"temp.features.{item.name.replace(' ', '_')}{index}"
                )
            if len(self._steps[-1].outputs) > 1:
                item.feature_table = self._steps[-1].outputs[-1]
                item.outputs.append(
                    f"temp.features.{item.name.replace(' ', '_')}{index}"
                )

        return item

    def replace_linear_pipeline(self, item: PipelineStep, index: int) -> PipelineStep:
        item.input_data = self._steps[index].input_data
        item.outputs = self._steps[index].outputs
        if len(self._steps[index].outputs) > 1:
            item.feature_table = self._steps[index].feature_table

        return item

    def remove(self, item: PipelineStep):
        """Removes the item from the pipeline.

        Args:
            item (pipeline step)
        """
        if item in self._steps:
            self._steps.remove(item)

    def pop(self, index: int):
        self._steps.pop(index)

    def clear(self):
        """Clears all items from the pipeline."""
        self._steps = []

    def to_list(self) -> list:
        """Returns a list representation of the pipeline."""
        a = []
        if self._steps:
            for step in self._steps:
                if isinstance(step, FunctionCalls):
                    for o in step._to_list():
                        a.append(o)
                else:
                    if isinstance(step, dict):
                        a.append(step)
                    else:
                        a.append(step._to_dict())
        return a

    def describe(self, show_params: bool = True, show_set_params: bool = False):
        """Prints a formatted description of the pipeline"""
        describe_pipeline(
            self.to_list(), show_params=show_params, show_set_params=show_set_params
        )

    def _get_pipeline_step_value(self, step: int, key: str = "type") -> PipelineStep:
        """Returns the value associated with the specified key from the specified step index.

        Args:
            step (int): step index
            key (str): key to get the value for

        Returns:
            if it exists, the contents associated with the key, otherwise None
        """
        if len(self._steps) == 0:
            print("There are no steps associated with this pipeline.")
            return None

        if len(self._steps) < step:
            print("This pipeline step does not exist.")
            return None

        if isinstance(self._steps[step], dict):
            return self._steps[step].get(key, None)

        return self._steps[step]._to_dict().get(key)

    def _get_step_name(self, index: int) -> str:
        if isinstance(self._steps[index], dict):
            return self._steps[index]["name"]
        else:
            return self._steps[index].name

    def _check_duplicate_outputs(self, item: PipelineStep) -> int:
        for i, step in enumerate(self._steps):
            if item.name == self._get_step_name(i):
                return i

        return None

    def _check_integrity(self):
        """Checks the integrity of the pipeline as a whole.

        Returns:
             True if successful, otherwise raises an exception
        """
        _aggregated_errors = []

        def _aggregate_errors(fmt_string, errors=[], *args):
            # Useful aggregation of error strings
            for error in errors:
                err_string = fmt_string.format(error, *args)
                _aggregated_errors.append(err_string)
                # _aggregated_errors.append(fmt_string.format(args, error))
            return

        output_vars = []
        step_num = 1
        for step in self._steps:
            is_last_step = True if step_num == len(self._steps) else False
            if isinstance(step, PipelineStep):
                errors = step._check_inputs(output_vars)
                if errors:
                    _aggregate_errors(
                        '[{1}] Step "{2}" -- Unmatched input: {0}',
                        errors,
                        step_num,
                        step.name,
                    )
                errors = step._check_outputs(output_vars, is_last_step)
                if errors:
                    _aggregate_errors(
                        '[{1}] Step "{2}" -- Duplicate output: {0}',
                        errors,
                        step_num,
                        step.name,
                    )
                output_vars.extend(step.outputs)
            else:
                raise PipelineError("Item is not a valid pipeline step.")
            step_num += 1

            # Ensure that the set objects contain the minimum number of call
            # objects
            missing_call_string = "The {0} set does not contain any {1} calls. Please add one or more {1} calls before adding the step to the sandbox."
            if isinstance(step, GeneratorCallSet) and not len(step.generator_calls):
                raise PipelineError(
                    missing_call_string.format("feature generator", "generator")
                )
            elif isinstance(step, SelectorCallSet) and not len(step.selectors):
                raise PipelineError(
                    missing_call_string.format("feature selector", "selector")
                )
            elif isinstance(step, TrainAndValidationCall):
                if not len(step.classifiers):
                    raise PipelineError(
                        missing_call_string.format("train and validation", "classifier")
                    )
                if not len(step.optimizers):
                    raise PipelineError(
                        missing_call_string.format("train and validation", "optimizer")
                    )
                if not len(step.validation_methods):
                    raise PipelineError(
                        missing_call_string.format(
                            "train and validation", "validation method"
                        )
                    )

        if not _aggregated_errors:
            return True
        else:
            raise PipelineError(
                "Pipeline failed integrity check: " + "\n".join(_aggregated_errors)
            )

    def __str__(self):
        pipeline_string = ""
        pipeline_list = []
        for step in self._steps:
            if isinstance(step, FunctionCalls):
                for o in step._to_list():
                    pipeline_list.append(o)
            else:
                if isinstance(step, dict):
                    pipeline_list.append(step)
                else:
                    pipeline_list.append(step._to_dict())
        for step in pipeline_list:
            if "name" in step:
                pipeline_string += "{name} ({type})\n".format(**step)
            else:
                pipeline_string += "{type}\n".format(**step)
            if "inputs" in step:
                pipeline_string += "    Inputs: \n"
                for input_ in step["inputs"]:
                    pipeline_string += f"        {input_}\n"
            if "outputs" in step:
                pipeline_string += "    Outputs: \n"
                for output_ in step["outputs"]:
                    pipeline_string += f"        {output_}\n"
            pipeline_string += "\n"

        return pipeline_string


class Sandbox(object):
    """Base class for a sandbox."""

    def __init__(self, connection: Connection, project: Project):
        """Initializes a sandbox instance."""
        self._uuid = ""
        self._name = ""
        self._dirty = False
        self._connection = connection
        self._project = project
        self._pipeline = SandboxPipeline()
        self._cache_enabled = True
        self._results = ModelResultSet(project, self)
        self._execution_summary = None
        self._features = None
        self._device_config = DeviceConfig()
        self._created_at = None
        self._last_modified = None
        self._active = False

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._dirty = True
        self._name = value

    @property
    def pipeline(self) -> str:
        return self._pipeline

    @property
    def cache(self) -> bool:
        return self._cache_enabled

    @property
    def active(self) -> bool:
        return self._active

    @property
    def results(self):
        return self._results

    @property
    def device_config(self):
        return self._device_config

    @property
    def created_at(self) -> datetime.datetime:
        """Date of the Pipeline creation"""
        return self._created_at

    @created_at.setter
    def created_at(self, value: str):
        if value:
            self._created_at = datetime.datetime.strptime(
                value[:-6], "%Y-%m-%dT%H:%M:%S.%f"
            )

    @property
    def last_modified(self) -> datetime.datetime:
        return self._last_modified

    @last_modified.setter
    def last_modified(self, value: str):
        self._last_modified = datetime.datetime.strptime(
            value[:19], "%Y-%m-%dT%H:%M:%S"
        )

    @property
    def cost_preview(self):
        print(
            "The cost_preview is no longer available. To view device costs look at a KnowledgePack cost_report.\n"
        )

    def _check_sandbox_inserted(self, insert: bool = False) -> bool:
        """Checks for a uuid and warns the user if none exists"""
        if self.uuid == "":
            if insert:
                print("Sandbox was not on server, attempting to insert now...", end="")
                self.insert()
                print("Success")
            else:
                raise Exception("Sandbox does not exist on the server")
        return True

    def _init_device_config(self, data):
        self._device_config = DeviceConfig(data.get("device_config", None))

    def insert(self) -> Response:
        """Calls the REST API to insert a new object on to the server."""
        url = f"project/{self._project.uuid}/sandbox/"
        sandbox_info = {
            "name": self.name,
            "pipeline": self.pipeline.to_list(),
            "cache_enabled": self.cache,
            "device_config": self.device_config,
        }
        response = self._connection.request("post", url, sandbox_info)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data["uuid"]
            self._init_device_config(response_data)
            self._dirty = False

        return response

    def update(self) -> Response:
        """Calls the REST API to update the object on the server."""

        self._pipeline._check_integrity()
        if self._check_sandbox_inserted():
            url = f"project/{self._project.uuid}/sandbox/{self.uuid}/"
            sandbox_info = {
                "name": self.name,
                "pipeline": self.pipeline.to_list(),
                "cache_enabled": self.cache,
                "device_config": self.device_config,
            }
            response = self._connection.request("put", url, sandbox_info)
            response_data, err = utility.check_server_response(response)
            if err is False:
                self._init_device_config(response_data)
                self._dirty = False

            return response

    def delete(self) -> Response:
        """Calls the REST API to delete the object from the server."""
        url = f"project/{self._project.uuid}/sandbox/{self.uuid}/"
        if self._check_sandbox_inserted(insert=False):
            response = self._connection.request("delete", url)
            response_data, err = utility.check_server_response(response)
            self._dirty = False
            self.uuid = ""

            return response

    def knowledgepack(self, kp_uuid: str) -> KnowledgePack:
        """Gets the KnowledgePack(s) created by the sandbox.

        Returns:
            a KnowledgePack instance, list of instances, or None
        """
        url = f"knowledgepack/{kp_uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            kp = KnowledgePack(self._connection, self._project.uuid, self.uuid)
            kp.initialize_from_dict(response_data)
            return kp

        return response

    def get_knowledgepacks(self) -> DataFrame:
        """Gets the KnowledgePack(s) created by the sandbox.

        Returns:
            a KnowledgePack instance, list of instances, or None
        """
        url = f"project/{self._project.uuid}/sandbox/{self.uuid}/knowledgepack/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return pd.DataFrame(response_data)

        return response

    def _handle_result(self, data: dict, pipeline_step: int = -1):
        """Decides what type of results have been returned and creates a DataFrame or stores model results accordingly."""

        if data.get("status") not in ["SUCCESS"]:
            return data, None

        execution_type = data.get("execution_type")

        if data.get("number_of_pages", 0) > 1:
            print(
                "\nRetrieving page {0} of {1}.".format(
                    data.get("page_index", 1), data["number_of_pages"]
                )
            )
            if data["number_of_pages"] > 1:
                print(
                    "To get more pages, use: \n"
                    + "next_results, next_stats = client.pipeline.get_results(page_index=<desired page number>)."
                )

        summary = {}
        for key in ["execution_summary", "feature_table", "fitness_summary"]:
            if data.get(key):
                summary[key] = pd.DataFrame(data.get(key)).fillna("")

        self._execution_summary = summary.get("execution_summary")
        self._features = summary.get("feature_table")

        results = data.get("results", [])

        if (
            self.pipeline._get_pipeline_step_value(pipeline_step, key="type") == "tvo"
            and execution_type == "pipeline"
        ) or execution_type == "auto":
            if isinstance(results, list):
                data = []
                for result in results:
                    temp_results = ModelResultSet(
                        deepcopy(self._project), deepcopy(self)
                    )
                    temp_results.initialize_from_dict(result)
                    data.append(temp_results)
            else:
                self._results = ModelResultSet(self._project, self)
                self._results.initialize_from_dict(results)
                data = self._results

        else:
            if isinstance(results, list):
                data = map(lambda x: DataFrame(x), results)
            else:
                data = DataFrame(results)

        return data, summary

    def intermediate_data(
        self,
        pipeline_step: int,
        page_index: int = 0,
        convert_datasegments_to_dataframe=True,
    ):
        """Retrieves intermediate pipeline step data from a previously executed pipeline.

        Args:
            pipeline_step (int): The pipeline step to retrieve from and executed pipeline.
            page_index (int): the index to pull form the cache

        Returns:
        Returns:
            1. A datasegments dictionary if the pipeline step is prior to the feature extraction step
            2. A feature vector DataFrame if the result is before the Model train step
            3. A ModelResultSet if the selected pipeline step is TVO step, otherwise the output of the pipeline

        """
        url = f"project/{self._project.uuid}/sandbox/{self.uuid}/data/"
        payload = {
            "pipeline_step": pipeline_step,
            "page_index": page_index,
            "convert_datasegments_to_dataframe": convert_datasegments_to_dataframe,
        }
        response = self._connection.request("get", url, params=payload)

        data, err = utility.check_server_response(response)
        if err is False:
            results = data.pop("results")

            return results, data

        return response

    def get_metrics_set(self, data: dict) -> Response:
        """retrieves metrics set from server

        Args:
            data (dict): dictionary containing
                        - 'y_true' and 'y_pred' keys
                        - y_true and y_pred values must be lists

        Returns:
            (dict): dictionary containing metrics result set from server"""
        url = "get-metrics-set/"
        response = self._connection.request("get", url, data)
        data, err = utility.check_server_response(response)
        if err is False:
            response_data = data
            return response_data

        return response

    def execute(self):
        """Executes the sandbox pipeline and returns results.

        Returns:
            (DataFrame or ModelResultSet): result of executed pipeline, specified by the sandbox
            (dict): execution summary including execution time and whether cache was used for each
            step; also contains a feature cost table if applicable
        """
        self.submit()

        return utility.wait_for_pipeline_result(
            self, lock=True, wait_time=1, silent=True, page_index=1
        )

    def async_submit(self, data: dict):
        """Submits the sandbox for asynchronous execution and returns the task status."""
        if self._dirty:
            self.update()

        url = f"project/{self._project.uuid}/sandbox-async/{self.uuid}/"
        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)

        if err is False:
            print(response_data)
            return response_data

        return response

    def auto(self, auto_params: dict, renderer=None, version: int = 1):
        """Submits the automation job for asynchronous execution and returns the task status"""

        data = {
            "run_parallel": True,
            "execution_type": "automlv2",
            "auto_params": auto_params,
        }

        self.async_submit(data)
        return 1

    def retrieve_auto(self):
        result = self.retrieve(execution_type="auto")
        return result

    def autosegment_search(self, params: dict, run_parallel: bool = True):
        """Submits the grid search for asynchronous execution and returns the task status."""
        data = {
            "run_parallel": run_parallel,
            "execution_type": "autosegment_search",
            "seg_params": params,
        }

        return self.async_submit(data)

    def retrieve_autosegment(self):
        result = self.retrieve()
        return result

    def retrieve(
        self,
        silent: bool = False,
        page_index: int = 0,
        status_only: bool = False,
        **kwargs,
    ):
        """Gets the result of a prior asynchronous execution of the sandbox.

        silent(bool): silence all messages
        page_index(int): The page of data to retrieve
        status_only(bool): Return only the status message, don't retrieve any data

        Returns:
            (DataFrame or ModelResultSet): result of executed pipeline, specified by the sandbox
            (dict): execution summary including execution time and whether cache was used for each
            step; also contains a feature cost table if applicable
        """

        query_params = urlencode({"page_index": page_index, "status_only": status_only})
        url = f"project/{self._project.uuid}/sandbox-async/{self.uuid}/?{query_params}"
        response = self._connection.request("get", url)

        data, err = utility.check_server_response(response)
        if err is False:
            response_data = data or {}
            return utility.check_pipeline_status(
                response_data, self._handle_result, silent=silent
            )

        return response

    def kill_pipeline(self) -> Response:
        url = f"project/{self._project.uuid}/sandbox-async/{self.uuid}/"
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            print(response_data)

        return response

    def submit(self):
        """Submits a pipeline for asynchronous execution."""
        data = {"execution_type": "pipeline"}
        return self.async_submit(data)

    def grid_search(self, grid_params: dict, run_parallel: bool = False):
        """Submits the grid search for asynchronous execution and returns the task status."""
        data = {
            "run_parallel": run_parallel,
            "execution_type": "grid_search",
            "grid_params": grid_params,
        }

        return self.async_submit(data)

    def retrieve_gridsearch(self):
        result = self.retrieve()
        return result

    def refresh(self) -> Response:
        """Calls the REST API and populates the local sandbox from the server."""
        url = f"project/{self._project.uuid}/sandbox/{self.uuid}/"
        response = self._connection.request("get", url)
        data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = data["uuid"]
            self.name = data["name"]
            self.created_at = data.get("created_at", None)
            self.last_modified = data.get("last_modified", None)
            self._active = data.get("active", False)
            if not data.get("cache_enabled", True):
                self.disable_cache()
            self._init_device_config(data)
            self.pipeline._steps = data["pipeline"]
            self._dirty = False

        return response

    def delete_cache(self) -> Response:
        """Calls the REST API and deletes the server cache for the sandbox."""
        if self._check_sandbox_inserted(insert=False):
            url = f"project/{self._project.uuid}/sandbox/{self.uuid}/cache/"
            response = self._connection.request("DELETE", url)
            data, err = utility.check_server_response(response)
            if err is False:
                print(data)
            return response

    def initialize_from_dict(self, init_dict: dict):
        """Populates a single sandbox from a dictionary of properties.

        Args:
            (dict): contains uuid, name, cache_enabled, and pipeline
        """
        self.uuid = init_dict["uuid"]
        self.name = init_dict["name"]
        self.created_at = init_dict.get("created_at", None)
        self.last_modified = init_dict.get("last_modified", None)
        self._active = init_dict.get("active", None)

        if not init_dict.get("cache_enabled", True):
            self.disable_cache()

        if init_dict["pipeline"] and len(init_dict["pipeline"]) != 0:
            self._pipeline._steps = init_dict["pipeline"]
        else:
            self._pipeline._steps = []
            self._init_device_config(init_dict)
        self._dirty = False

    def add_step(self, step: PipelineStep):
        """Adds the step to the sandbox pipeline.

        Args:
            step (pipeline step): a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or
                                  TrainAndValidationCall object
        """
        self._pipeline.add(step)
        self._dirty = True

    def update_step(self, step: PipelineStep, index: int):
        """Update a step with new values

        Args:
            step (pipeline step): a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or
                                  TrainAndValidationCall object
            index (int): index of the pipeline step to update

        """
        step = self._pipeline.replace_linear_pipeline(step, index)
        self._pipeline.replace(step, index)
        self._dirty = True

    def add_linear_step(self, step: PipelineStep, overwrite: bool = True):
        """Adds a linear step to the pipeline (will automatically use the previous step's output as input).

        Args:
            step (pipeline step): a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or
                TrainAndValidationCall object
            overwrite (boolean): when adding multiple instances of the same transform, set
                overwrite to False for the additional steps and the first instance will not
                be overwritten (default is True)

        """
        if not overwrite or self._pipeline._check_duplicate_outputs(step) is None:
            step = self._pipeline.linear_pipeline(step)
            self._pipeline.add(step)
            self._dirty = True
        else:
            self.update_step(step, self._pipeline._check_duplicate_outputs(step))

    def remove_step(self, step: PipelineStep):
        """Removes a step from the pipeline.

        Args:
            step (pipeline step): a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or
                                  TrainAndValidationCall object to remove from the pipeline
        """
        self._pipeline.remove(step)
        self._dirty = True

    def clear(self):
        """Clears the sandbox of all steps."""
        self._pipeline.clear()
        self._dirty = True

    def enable_cache(self):
        """Enables the use of caching for the sandbox on the server."""
        self._cache_enabled = True
        self._dirty = True

    def disable_cache(self):
        """Disables the use of caching for the sandbox on the server."""
        self._cache_enabled = False
        self._dirty = True


def describe_pipeline(
    pipeline: list, show_params: bool = True, show_set_params: bool = False
):
    print("------------------------------------------------------------------------")
    for index, step in enumerate(pipeline):
        if isinstance(step["name"], list):
            name = ", ".join(step["name"])
        else:
            name = step["name"]

        print(f"{index: >2}.     Name: {name: <25} \t\tType: {step['type']: <25}")
        print(
            "------------------------------------------------------------------------"
        )
        if step.get("set", None) and show_params:
            print_set_items(step, params=show_set_params)
        if step.get("inputs", None) and show_params:
            print(filter_params(step["inputs"]))
        if step.get("type") == "tvo":
            print_tvo(step)
        print(
            "------------------------------------------------------------------------"
        )
    print("")


def filter_params(inputs: dict, num_tabs: int = 1):
    not_params = [
        "input_data",
        "feature_table",
    ]
    params = filter(lambda x: x not in not_params, inputs.keys())
    param_values = [
        num_tabs * "\t" + f"{param + ':'} {inputs[param]}" for param in params
    ]
    return "\n".join(param_values)


def print_set_items(step: int, params: Optional[dict] = None):
    for index, set_step in enumerate(step.get("set")):
        print(f"\t{index: >2}. Name: {set_step['function_name']: <25}")
        if params:
            print(filter_params(set_step["inputs"], num_tabs=2))
            print("")


def print_tvo(step: dict):
    map_tvo = {
        "classifiers": "Classifier:",
        "optimizers": "Training Algo:",
        "validation_methods": "Validation Method:",
    }
    for tvo_step in ["classifiers", "optimizers", "validation_methods"]:
        print(f"\t{map_tvo[tvo_step]} {step[tvo_step][0]['name']}")
        print(filter_params(step[tvo_step][0]["inputs"], num_tabs=2))
        print("")
