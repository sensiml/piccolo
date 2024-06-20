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

import logging
import os
from copy import deepcopy

from datamanager import utils
from datamanager.datasegments import DataSegments, is_datasegments
from datamanager.models import Query
from datamanager.datastore import get_datastore, get_datastore_basedir
from django.conf import settings
from django.core import serializers
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class VariableNotFoundException(Exception):
    pass


class CacheManager(object):
    def __init__(self, sandbox, pipeline, pipeline_id=None):
        self._sandbox = sandbox
        self._current_pipeline = pipeline
        if pipeline_id is None:
            self._pipeline_id = str(sandbox.uuid)
        else:
            self._pipeline_id = str(pipeline_id)

        self._bucket = get_datastore_basedir(settings.SERVER_CACHE_ROOT)

        self._datastore = get_datastore(folder=self._bucket)

        utils.ensure_path_exists(self._bucket)

        if sandbox.cache is None:
            self._cache = {"pipeline": [], "data": {}, "detail": {}, "results": {}}
        else:
            # This can be remove once we know customer data has been migrated safely
            self._cache = sandbox.cache

    def set_variable_path_id(self, name):
        if self._datastore.is_remote:
            return f"{self._pipeline_id}/{name}"

        return f"{self._bucket}/{ self._pipeline_id}/{name}"

    def get_folder_path(self):
        if self._datastore.is_remote:
            return self._pipeline_id

        folder_path = "{}/{}".format(self._bucket, self._pipeline_id)

        utils.ensure_path_exists(folder_path)

        return folder_path

    def _evict_extra_cache_steps(self):
        if len(self._cache["pipeline"]) > len(self._current_pipeline):
            self._cache["pipeline"] = self._current_pipeline
            self.evict(len(self._current_pipeline))

    def _cache_is_present(self):
        return self._cache is not None

    def _cache_file_exists(self, file_name):
        if isinstance(file_name, list):
            for f in file_name:
                if not self._cache_file_exists(f):
                    return False
            return True
        else:
            return self._datastore.key_exists(self.set_variable_path_id(file_name))

    def get_last_iteration(self, cache_key="auto_results"):
        """Returns the last numbered iteration that was generated. Currently
        only implemented for the auto_results cache_key."""
        if cache_key in self._cache and len(self._cache[cache_key].keys()):
            last_iteration = 0
            for key in self._cache[cache_key].keys():
                iteration = key.split("_")[1]
                last_iteration = max(int(iteration), last_iteration)
            return last_iteration
        else:
            return None

    def validate_steps(self, temp):
        """Returns an updated pipeline that contains only the steps that need to be freshly executed.

        Also returns the variables to be written to temp for the current execution and the variables to be
        returned from the last cached step and evicts from the cache any steps that follow the changed step.
        """
        # Determine the steps that need fresh computation; if a step does not need to be run, collect its outputs
        difference_detected = False
        outputs = []
        cached_inputs = []
        new_pipeline = list(self._current_pipeline)

        for i, step in enumerate(self._current_pipeline):
            detail = None

            if step["type"] == "query":
                query = Query.objects.get(
                    name=step["name"], project=self._sandbox.project
                )
                detail = {
                    "name": "query",
                    "value": serializers.serialize("json", [query]),
                }
            if not difference_detected and self.step_has_valid_cache(i, step, detail):
                # logger.userlog(
                #    {
                #        "message": "Using cached value for step {}: {}".format(
                #            i, step["type"]
                #        ),
                #        "UUID": self._pipeline_id,
                #        "log_type": "PID",
                #    }
                # )
                outputs = step["outputs"]
                new_pipeline.remove(step)

                # the pipeline results are not copied from the cache, they only
                # point to the same place. If we add new steps, they will be evicted.
                # so we want to remove the reference to the pipeline results here
                # when it is the same as the last step of the pipeline.
                pipeline_result_key = "{}.{}".format(
                    "pipeline_result", self._pipeline_id
                )

                if self._cache["results"].get(pipeline_result_key, None) == self._cache[
                    "data"
                ].get(outputs[0], [False]):
                    self._cache["results"].pop(pipeline_result_key)

                if len(outputs) > 1:
                    feature_table_key = "{}.{}".format(
                        "feature_table", self._pipeline_id
                    )
                    if self._cache["results"].get(
                        feature_table_key, None
                    ) == self._cache["data"].get(outputs[1], False):
                        self._cache["results"].pop(feature_table_key)

            elif not difference_detected:
                difference_detected = True
                self.evict(i)

        # Collect the variables that need to be written to temp
        # (Any inputs required by pipeline steps that are outputs of cache steps including shards of those outputs)
        if outputs:
            if len(outputs) > 1:
                feature_table = self.get_file(self._cache["data"][outputs[-1]])
                temp.add_variable_temp(outputs[-1], feature_table, overwrite=True)

            cached_inputs = [x for x in self._cache["data"][outputs[0]]]

        return new_pipeline, cached_inputs

    def step_has_valid_cache(self, index, step, detail=None):
        """Returns true if the argument step is present in the cache with the same configuration and index.

        The cached file must also be present on either the local cache root or S3.
        """
        if self._cache_is_present():
            if len(self._cache["pipeline"]) > index:
                if self._cache["pipeline"][index] == step:
                    if self._cache["pipeline"][index]["name"] == "tvo":
                        return False
                    if not detail:
                        for output in self._cache["pipeline"][index]["outputs"]:
                            if not self._cache_file_exists(self._cache["data"][output]):
                                return False
                        return True
                    elif (
                        detail["name"] in self._cache["detail"]
                        and detail["value"] == self._cache["detail"][detail["name"]]
                    ):
                        if not self._cache_file_exists(
                            self._cache["data"][
                                self._cache["pipeline"][index]["outputs"][0]
                            ]
                        ):
                            return False
                        return True
        return False

    def get_result_pages(self, variable_name, cache_key="results"):
        variable_value = self._cache[cache_key].get(variable_name, None)

        if variable_value is None:
            return 0, None

        if isinstance(variable_value, list) and not variable_value:
            return 0, None

        if isinstance(variable_value, list):
            keys = variable_value
        else:
            keys = [variable_value]

        return len(keys), keys

    def get_result_from_cache(self, variable_name, page_index=0, cache_key="results"):
        num_pages, keys = self.get_result_pages(variable_name, cache_key=cache_key)

        if keys is None:
            return None, 0

        if num_pages == 1:
            page_index = 0

        if page_index > num_pages:
            raise VariableNotFoundException(
                "Page index {} not found for variable {}".format(
                    page_index, variable_name
                )
            )

        data = self.get_file(keys[page_index])

        if isinstance(data, list) and is_datasegments(data):
            data = DataSegments(data).to_dataframe()

        return data, num_pages

    def get_file(self, summary):
        """Gets data from the cache corresponding to a particular named variable."""
        if not summary:
            return None

        if isinstance(summary, dict):
            filename = summary.get("filename")
        else:
            filename = summary

        if not filename:
            return None

        return self._datastore.get_data(self.set_variable_path_id(filename))

    def write_file(self, data, filename):
        if isinstance(data, DataFrame):
            fmt = ".csv.gz"
            filename += fmt

        elif isinstance(data, dict):
            fmt = ".json"
            filename += fmt

        elif isinstance(data, list):
            fmt = ".pkl"
            filename += fmt

        else:
            raise Exception(
                "Data type {} cannot be written to the cache".format(type(data))
            )

        self._datastore.save_data(data, self.set_variable_path_id(filename), fmt)

        return filename

    def delete_file(self, filename):
        if self._datastore.is_remote:
            self._datastore.delete(self.set_variable_path_id(filename))

        else:
            try:
                os.remove(self.set_variable_path_id(filename))
            except:
                logger.error(
                    {
                        "message": "FILE {} NOT FOUND".format(filename),
                        "UUID": self._pipeline_id,
                        "log_type": "PID",
                    }
                )

    def get_persistent_variables_from_cache(self):
        """Returns all persistent variables in the cache as key-value pairs"""
        return {
            key: value
            for key, value in self._cache["data"].items()
            if key.split(".")[0] == "persist"
        }

    def save_pipeline_result(self, steps, task_id):
        """Saves the passed variable names as a single S3 or local cache variable without disturbing
        the sandbox pipeline and associated cached steps. Either a copy is made from an existing
        pipeline cache file (in the 'data' cache key) or a DataFrame can be passed in as the data to
        write. The resulting cache entry will be a list to support sharded results.

        Args:
            task_index (uuid): the unique pipeline id
            data_names (list): list of intermediate step variable(s) to copy as result
                variable(s) - can be an empty list if using the data argument
            name (string, optional): name of the result prefix to use, default is 'result'
            cache_key (string, optional): cache key to write to (default is the 'data' cache)
            overwrite (Boolean, optional): if set to False, an existing cached variable
                by the same name will not be overwritten
            data (DataFrame, dictionary, or empty list, optional): explicitly passed DataFrame to
                store; using data_names is preferred for better performance, but for feature tables
                and dictionary results, passing the actual data is convenient.
        """

        pipeline_result_key = "{}.{}".format("pipeline_result", task_id)
        feature_table_key = "{}.{}".format("feature_table", task_id)

        self._cache["results"] = self._cache.get("results", {})

        # Copy the output created by the task
        self._cache["results"][pipeline_result_key] = self._cache["data"][
            steps[-1]["outputs"][0]
        ]

        if len(steps[-1]["outputs"]) > 1:
            self._cache["results"][feature_table_key] = self._cache["data"][
                steps[-1]["outputs"][-1]
            ]
        else:
            self._cache["results"][feature_table_key] = None

        self._sandbox.cache = self._cache
        self._sandbox.save(update_fields=["cache"])

        return True

    def save_result_data(self, key, task_id, data, cache_key="results"):
        """Saves the passed variable names as a single S3 or local cache variable without disturbing
        the sandbox pipeline and associated cached steps. Either a copy is made from an existing
        pipeline cache file (in the 'data' cache key) or a DataFrame can be passed in as the data to
        write. The resulting cache entry will be a list to support sharded results.

        Args:
            task_index (uuid): the unique pipeline id
            data_names (list): list of intermediate step variable(s) to copy as result
                variable(s) - can be an empty list if using the data argument
            name (string, optional): name of the result prefix to use, default is 'result'
            cache_key (string, optional): cache key to write to (default is the 'data' cache)
            overwrite (Boolean, optional): if set to False, an existing cached variable
                by the same name will not be overwritten
            data (DataFrame, dictionary, or empty list, optional): explicitly passed DataFrame to
                store; using data_names is preferred for better performance, but for feature tables
                and dictionary results, passing the actual data is convenient.
        """

        pipeline_result_key = "{}.{}".format(key, task_id)

        filename = self.write_file(data, key)

        # Copy the output created by the task
        self._cache[cache_key][pipeline_result_key] = filename

        self._sandbox.cache = self._cache
        self._sandbox.save(update_fields=["cache"])

        return True

    def save_variable_to_cache(self, key, data, cache_key="results"):
        """Saves the passed variable names as a single S3 or local cache variable without disturbing
        the sandbox pipeline and associated cached steps. Either a copy is made from an existing
        pipeline cache file (in the 'data' cache key) or a DataFrame can be passed in as the data to
        write. The resulting cache entry will be a list to support sharded results.

        Args:
            task_index (uuid): the unique pipeline id
            data_names (list): list of intermediate step variable(s) to copy as result
                variable(s) - can be an empty list if using the data argument
            name (string, optional): name of the result prefix to use, default is 'result'
            cache_key (string, optional): cache key to write to (default is the 'data' cache)
            overwrite (Boolean, optional): if set to False, an existing cached variable
                by the same name will not be overwritten
            data (DataFrame, dictionary, or empty list, optional): explicitly passed DataFrame to
                store; using data_names is preferred for better performance, but for feature tables
                and dictionary results, passing the actual data is convenient.
        """
        if self._cache.get(cache_key) is None:
            self._cache[cache_key] = {}

        # Copy the output created by the task
        self._cache[cache_key][key] = data

        self._sandbox.cache = self._cache
        self._sandbox.save(update_fields=["cache"])

        return True

    def get_variable_from_cache(self, key, cache_key="results"):
        """
        Args:
            name (string, optional): name of the result prefix to use, default is 'result'
            cache_key (string, optional): cache key to write to (default is the 'data' cache)
        """

        # Copy the output created by the task
        return self._cache[cache_key][key]

    def write_step(self, index, step, temp, result_names, detail=None):
        """Saves the intermediate (temp) sandbox data objects to the persistent cache (S3 or local)
        and associates them with the step that created them and any other details, such as a query.
        Result_names should be a list containing the main data output names for the step, which can
        be multiple because of sharding. It shouldn't contain the feature table output or persistent
        variables - those will be added internally by the method.

        Args:
            index (int): the index of the step of the pipeline
            step (dict): describes the current step to place into the cache
            temp (class): and instance of the temp_table class
            result_names (list): temp names to be stored for the step
            detail (None, optional): additional information to store
        """

        if len(self._cache["pipeline"]) <= index:
            self._cache["pipeline"].append(step)
        else:
            self._cache["pipeline"][index] = step

        self._cache["data"][step["outputs"][0]] = result_names

        if len(step["outputs"]) > 1:
            self._cache["data"][step["outputs"][1]] = step["outputs"][1] + ".csv.gz"

        # Write all persistent variables from temp to the cache. These are never evicted, but will be overwritten
        # every time there is a recalculation of the step that produced them, so they should refresh correctly.
        persistent_vars = temp.get_persistent_variables()
        for v in persistent_vars:
            self._cache["data"][v["name"]] = v["value"]

        # Save additional detail
        if detail:
            self._cache["detail"][detail["name"]] = detail["value"]

        self._sandbox.cache = self._cache
        self._sandbox.save(update_fields=["cache"])

        return True

    def evict(self, index):
        """Deletes all items from the sandbox's cache starting with the provided step index."""
        new_cache = deepcopy(self._cache)
        for i in range(index, len(self._cache["pipeline"])):
            # logger.userlog(
            #    {
            #        "message": "Evicting step {} from the cache".format(
            #            self._cache["pipeline"][i]["type"],
            #        ),
            #        "UUID": self._pipeline_id,
            #        "log_type": "PID",
            #    }
            # )
            for cache_key in self._cache["pipeline"][i]["outputs"]:
                if isinstance(self._cache["data"][cache_key], list):
                    for cache_data in self._cache["data"][cache_key]:
                        self.delete_file(cache_data)
                else:
                    self.delete_file(self._cache["data"][cache_key])

                new_cache["data"].pop(cache_key, None)

            new_cache["pipeline"].remove(self._cache["pipeline"][i])

        # delete all the results in the cache['results']
        for cache_key, cache_data in self._cache["results"].items():
            if isinstance(cache_data, list):
                for file_name in cache_data:
                    self.delete_file(file_name)
            else:
                self.delete_file(cache_data)

        # Update the cache and save it to the sandbox
        new_cache["results"] = {}
        self._sandbox.cache = new_cache
        self._sandbox.save(update_fields=["cache"])

        self._cache = new_cache

        return 0

    def evict_key(self, cache_key):
        if cache_key in self._cache:
            self._cache.pop(cache_key)
        else:
            return

        self._sandbox.cache = self._cache
        self._sandbox.save(update_fields=["cache"])

    def evict_all_from_key(self, cache_key):
        if cache_key in self._cache:
            if isinstance(self._cache[cache_key], dict):
                for key in self._cache[cache_key].keys():
                    self.evict_data(key, cache_key)

    def evict_data(self, name, cache_key="data"):
        """Deletes the named item from the sandbox's cache_key cache (default is the 'data' cache)."""
        new_cache = deepcopy(self._cache)

        for cache_data in self._cache[cache_key][name]:
            if isinstance(cache_data, list):
                for cached_file in cache_data:
                    self.delete_file(cached_file)
            else:
                self.delete_file(cache_data)

        new_cache[cache_key].pop(name, None)

        # Update the cache and save it to the sandbox
        self._sandbox.cache = new_cache
        self._sandbox.save(update_fields=["cache"])
        self._cache = new_cache

        return 0

    def write_cache_list(self, list_of_dicts, cache_key):
        """Flattens a list of dictionaries, each with key 'value' which is a list, into one flattened list of values."""
        flattened = []
        for item in list_of_dicts:
            flattened += item["value"]
        self._sandbox.cache[cache_key] = flattened
        self._sandbox.save(update_fields=["cache"])

    def get_cache_list(self, cache_key):
        if self._sandbox.cache:
            return self._sandbox.cache.get(cache_key, [])
        else:
            return []


def get_cached_pipeline(cache_manager, temp):
    """Retrieve Cached data"""

    steps_to_execute, outputs = cache_manager.validate_steps(temp)

    # Persistent variables
    for name, value in cache_manager.get_persistent_variables_from_cache().items():
        temp.add_variable_temp(name, value, overwrite=True)

    return steps_to_execute, outputs


def load_persisitent_variables(cache_manager, temp):
    for name, value in cache_manager.get_persistent_variables_from_cache().items():
        temp.add_variable_temp(name, value, overwrite=True)
