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
import itertools
import json
from typing import Optional, Union, Callable, Tuple
import logging
import time
from requests import Response
import numpy as np
from pandas import DataFrame
from requests.exceptions import HTTPError

from six import string_types

import sensiml.base.utility as utility
from sensiml.base.exceptions import DuplicateValueError, PipelineOrderException
from sensiml.base.snippets import generate_pipeline
from sensiml.datamanager.knowledgepack import KnowledgePack
from sensiml.datamanager.modelresults import ModelResultSet

try:
    from sensiml.visualize import Visualize
except:
    print("skipping visualization library")


logger = logging.getLogger(__name__)


class InvalidParameterException(Exception):
    pass


class InvalidModelException(Exception):
    pass


class PlatformNotSpecifiedException(Exception):
    pass


class Pipeline(object):
    """Base class of a pipeline object"""

    def __init__(self, client, name=None):
        self._client = client
        self._project = client.project
        self._results = None
        self._stats = None
        self._dataset = None
        self._async = None
        self._save = False
        self._tvo_call = None
        self._generator_index = 0
        self._selector_index = 0
        self._classifier_call = None
        self._training_algorithm_call = None
        self._validation_call = None
        self._group_columns = None
        self._label_column = None
        self._data_columns = None
        self._use_query_session = False

        if name:
            self._id = f"{name}"
        else:
            self._id = f"{time.time()}_sandbox"

        self._sandbox = self._project.sandboxes.get_or_create_sandbox(self._id)

        logger.debug("pipeline_instance:" + self._id)

    @property
    def name(self) -> str:
        return self._id

    @property
    def data_columns(self) -> list[str]:
        if self._data_columns:
            return sorted(list(self._data_columns))
        return self._data_columns

    @data_columns.setter
    def data_columns(self, value: list[str]):
        if isinstance(value, list):
            if len(set(value)) != len(value):
                raise DuplicateValueError()
            self._data_columns = set(map(lambda x: str(x), value))
        else:
            print("Error: data_columns must be a list.")

    @property
    def label_column(self) -> str:
        return self._label_column

    @label_column.setter
    def label_column(self, value: str):
        if isinstance(value, str) or isinstance(value, string_types):
            self._label_column = str(value)
        else:
            print("Error: label_column must be a string.")

    @property
    def group_columns(self):
        if self._group_columns:
            return sorted(list(self._group_columns))
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value: list[str]):
        if isinstance(value, list):
            if len(set(value)) is not len(value):
                raise DuplicateValueError()
            self._group_columns = set(map(lambda x: str(x), value))
        else:
            print("Error: group_columns must be a list.")

    def to_list(self) -> list[dict]:
        """Converts the current pipeline into its List form

        Returns:
            List:
        """
        return self._sandbox._pipeline.to_list()

    def get_automl_iteration_metrics(self) -> DataFrame:
        """
        Results of automl stats for each iteration

        Returns:
            DataFrame: AutoML results stats
        """

        url = f"project/{self._project.uuid}/sandbox/{self._sandbox.uuid}/automl-iteration-metrics/"

        response = self._project._connection.request("get", url)

        response_data, err = utility.check_server_response(response)

        response_data = DataFrame(response_data)

        return response_data.sort_values(
            by=["original_iteration", "fitness"], ascending=[True, False]
        )

    def get_knowledgepack(self, uuid: str) -> KnowledgePack:
        """retrieve knowledgepack by uuid from the server

        Args:
            uuid (str): unique identifier for knowledgepack

        Returns:
            TYPE: a knowledgepack object
        """
        return self._sandbox.knowledgepack(uuid)

    def list_knowledgepacks(self) -> DataFrame:
        """Lists all of the projects on kb cloud associated with current pipeline

        Returns:
            DataFrame: projects on kb cloud
        """

        knowledgepacks = self._sandbox.get_knowledgepacks().rename(
            columns={
                "name": "Name",
                "project_name": "Project",
                "sandbox_name": "Pipeline",
                "uuid": "kp_uuid",
                "created_at": "Created",
                "knowledgepack_description": "kp_description",
            }
        )
        if len(knowledgepacks) < 1:
            print("No Knowledgepacks stored for this pipeline on the cloud.")
            return None

        return knowledgepacks[
            ["Name", "Created", "Project", "Pipeline", "kp_uuid", "kp_description"]
        ]

    def set_columns(
        self,
        data_columns: Optional[list[str]] = None,
        group_columns: Optional[list[str]] = None,
        label_column: Optional[str] = None,
    ):
        """Sets the columns for group_columns, data_columns and the label column
         to be used in the pipeline. This will automatically handle label column, ignore columns, group columns
         and passthrough columns for the majority of pipelines. For pipelines that need individually specified
         column attributes, set them in the step command.

        Args:
            data_columns (None, list): List of sensor data streams to use.
            group_columns (None, list): List of columns to use when applying aggregate functions
                and defining unique subsets on which to operate.
            label_column (None, str): The column name containing the ground truth label.

        """
        if data_columns:
            self.data_columns = data_columns

        if label_column:
            self.label_column = label_column

        if group_columns:
            self.group_columns = group_columns

    def get_pipeline_length(self) -> int:
        """
        Returns:
            int: The current length of the pipeline.
        """
        return len(self._sandbox._pipeline._steps)

    def get_function_type(self, name: str) -> str:
        """
        Returns:
            str: The type of a function.
        """
        return self._client.functions.get_function_by_name(name).type

    def describe(self, show_params: bool = True, show_set_params: bool = False):
        """Prints out a description of the pipeline steps and parameters

        Args:
            show_params (bool, True): Include the parameters in the pipeline description

        """
        self._sandbox.pipeline.describe(
            show_params=show_params, show_set_params=show_set_params
        )

    def rehydrate_knowledgepack(
        self,
        model: Optional[KnowledgePack] = None,
        uuid: Optional[str] = None,
        replace: bool = True,
    ):
        """Replace the executing cell with pipeline code for a knowledge Pack

        Args:
            model (model, knowledgepack, None): pass in a model to build a pipeline from that
        """

        return self.rehydrate(model=model, replace=replace, kp_summary=True, uuid=uuid)

    def rehydrate_pipeline(
        self,
        model: Optional[KnowledgePack] = None,
        uuid: Optional[str] = None,
        replace: bool = True,
    ):
        """Replace the executing cell with pipeline code for the current pipeline or
        pipeline that generated the model

        Args:
            model (model, knowledgepack, None): pass in a model to build a pipeline from that
        """

        return self.rehydrate(model=model, replace=replace, kp_summary=False, uuid=uuid)

    def rehydrate(
        self,
        model: Optional[KnowledgePack] = None,
        replace: Optional[bool] = True,
        kp_summary: Optional[list] = False,
        uuid: Optional[str] = None,
    ):
        """Replace the executing cell with pipeline code for either a model or
        pipeline.

        Args:
            model (model, knowledgepack, None): pass in a model to build a pipeline from that
            replace (boolean, True): replace the executing cell with pipeline code
        """
        if isinstance(uuid, str):
            knowledgepack = self._client.get_knowledgepack(uuid)

        if hasattr(model, "knowledgepack"):
            knowledgepack = model.knowledgepack
        else:
            knowledgepack = model

        steps = None

        if knowledgepack:
            try:
                if kp_summary:
                    if not knowledgepack.knowledgepack_summary:
                        print("Knowledge Pack doesn't have a summary.")
                        return
                    steps = (
                        [knowledgepack.pipeline_summary[0]]
                        + knowledgepack.knowledgepack_summary["recognition_pipeline"]
                        + [knowledgepack.pipeline_summary[-1]]
                    )
                else:
                    steps = knowledgepack.pipeline_summary
            except:
                raise InvalidModelException(
                    "Model Pipeline was not able to be generated."
                )

        else:
            steps = self._sandbox.pipeline.to_list()

        # reindex min max scale
        if knowledgepack and kp_summary:
            min_max_step = None
            for index in range(len(steps) - 1, 0, -1):
                if steps[index]["name"] == "Min Max Scale":
                    min_max_step = index

            # Set the Min Max Scale features correctly

            feature_min_max = steps[min_max_step]["inputs"][
                "feature_min_max_parameters"
            ]
            rescaled_features_min_max = {"maximums": {}, "minimums": {}}

            for factor in ["maximums", "minimums"]:
                generator_index = 0
                last_index = None
                for _, key in enumerate(sorted(feature_min_max["maximums"].keys())):
                    if last_index != key.split("_")[1]:
                        last_index = key.split("_")[1]
                        generator_index += 1

                    rescaled_features_min_max[factor][
                        "gen_"
                        + f"{generator_index:04}"
                        + f"_{'_'.join(key.split('_')[2:])}"
                    ] = feature_min_max[factor][key]

            steps[min_max_step]["inputs"][
                "feature_min_max_parameters"
            ] = rescaled_features_min_max

            # Add a custom feature selector to handle family generators such as histogram

            fs_dict = generate_custom_feature_selector(knowledgepack.feature_summary)

            fs_step = {
                "type": "selectorset",
                "name": "selector_set",
                "set": [
                    {
                        "inputs": {"custom_feature_selection": fs_dict},
                        "function_name": "Custom Feature Selection By Index",
                    }
                ],
                "inputs": {
                    "remove_columns": [],
                    "passthrough_columns": steps[min_max_step]["inputs"][
                        "passthrough_columns"
                    ],
                    "input_data": steps[min_max_step]["inputs"]["input_data"],
                    "label_column": steps[-1]["label_column"],
                    "number_of_features": len(knowledgepack.feature_summary),
                    "feature_table": steps[min_max_step]["outputs"][1],
                    "cost_function": "sum",
                },
                "outputs": ["temp.selector_set0", "temp.features.selector_set0"],
                "refinement": {},
            }

            steps.insert(min_max_step, fs_step)

        return generate_pipeline(
            self._client.functions.function_list, steps, replace=replace
        )

    def submit(self) -> bool:
        """Submit a pipeline asynchronously to SensiML Cloud for execution."""
        try:
            self._sandbox.submit()

        except HTTPError:
            return False

        return True

    def execute(self, wait_time: int = 15, silent: bool = True, describe: bool = True, **kwargs) -> Tuple[Union[DataFrame, ModelResultSet], dict]:  # type: ignore
        """Execute pipeline asynchronously and check for results.

        Args:
            wait_time (int, 10): Time to wait in between status checks.
            silent (bool, True): Silence status updates.
        """
        if describe:
            print("Executing Pipeline with Steps:\n")
            self.describe(show_params=False)

        self.submit()

        time.sleep(5)
        return self.get_results(lock=True, wait_time=wait_time, silent=silent, **kwargs)

    def auto(
        self,
        auto_params: dict,
        run_parallel: bool = True,
        lock: bool = True,
        silent: bool = True,
        renderer: Optional[Callable] = None,
        version: int = 2,
    ) -> Tuple[DataFrame, dict]:  # type: ignore
        """
        Execute automated pipeline asynchronously.

        The automated pipeline is used to find optimal parameters with a genetic algorithm. The genetic algorithm starts with a user-defined
        randomized population (pipelines) and generates models from them and tests them, keeps a subset of high-performing combinations, and
        then recombines those "survivors" and repeats the process over again. The offspring of good parameter combinations are usually also
        good and sometimes are significantly better than their parents. As the algorithm iterates each successive generation, it often finds a
        near-optimal model without trying as many configurations. The algorithm terminates when the desired number of iteration is completed.

        The created pipelines are run in parallel in SensiML servers and results are ranked by the fitness score which takes into account the
        model's F1 score, precision, sensitivity, and other metrics. The automation options and definition of the performance metrics are
        given below.

        Args:

            params (dict) : Parameters of the genetic algorithm to optimize the pipelines. Definition and options of the parameters are given below.
                - search_steps, (list, ['selectorset', 'tvo']): it is used to define which libraries in the pipelines will be optimized.

                - population_size, (int, 10): Initial number of randomly created pipelines.

                - iterations, (int, 1): Repetition number of optimization process

                - mutation_rate, (float, 0.1): Random changes from the previous population.

                - recreation_rate, (float, 0.1): Rate of randomly created pipelines for next generation.

                - survivor_rate, (float, 0.5): Ratio of the population that will be transferred to next generation.

                - number_of_models_to_return, (int, 5): Number of pipelines that will return to user.

                - allow_unknown, (bool, False): Allows creating unknown prediction results for the vectors. A vector is classified as an unknown if it

                    cannot be recognized by any neurons.

                - fitness (dict): Fitness parameters are combination of statistical and cost variables. It is used to evaluate the performance of
                  the models found by the algorithm. The user will define the coefficient scores for the parameters to define the priority of
                  the parameters in the fitness score. Definition and options of the parameters are given below.

                    - statistical variables:
                        - accuracy: The degree of correctness of all vectors

                        - f1_score: Measures of the test's accuracy

                        - precision: Proportion of positive identifications that is actually correct

                        - sensitivity: Measures of the proportion of actual positives that are correctly identified

                        - specificity: Measures of the proportion of actual negatives that are correctly identified

                        - positive_predictive_rate: Ratio of "true positive" is the event that the test makes a positive prediction


                    - cost variables:
                        - neurons: Number of neurons that used in the model

                        - features: Number of features that used in the model,

            lock (bool, False): Ping for results every 30 seconds until the process finishes.
            silent (bool, True): Silence status updates.

        Example:
            .. code-block:: python

                activity_data = client.datasets.load_activity_raw()
                client.upload_dataframe('activity_data.csv', activity_data, force=True)

                client.pipeline.reset()
                client.pipeline.set_input_data('activity_data.csv',
                                            data_columns = ['accelx', 'accely', 'accelz', 'gyrox', 'gyroy', 'gyroz'],
                                            group_columns = ['Subject','Class', 'Rep'],
                                            label_column = 'Class')

                client.pipeline.add_transform("Windowing", params={"window_size": 100, "delta": 100 })

                results, summary = client.pipeline.auto({ 'params':{"search_steps": ['selectorset', 'tvo'],
                                                                "population_size": 10,
                                                                "iterations": 1,
                                                                "mutation_rate": 0.1,
                                                                "recreation_rate": 0.1,
                                                                "survivor_rate": 0.5,
                                                                "number_of_models_to_return": 5,
                                                                "run_parallel": True,
                                                                "allow_unknown": False,
                                                                "fitness": {'accuracy': 1.0,
                                                                            'f1_score': 0.0,
                                                                            'features': 0.3,
                                                                            'precision': 0.0,
                                                                            'sensitivity': 0.7,
                                                                            'specificity': 0.0,
                                                                            'positive_predictive_rate': 0.0},

                                                                }})

                results.summarize()



        """
        if self._group_columns:
            auto_params["group_columns"] = list(self._group_columns)
        if self._data_columns:
            auto_params["data_columns"] = list(self._data_columns)
        if self._label_column:
            auto_params["label_column"] = self._label_column

        success = self._sandbox.auto(
            auto_params=auto_params, renderer=renderer, version=version
        )
        if success:
            return self.get_results(lock=lock, silent=silent, renderer=renderer)
        return (None, None)

    def grid_search(self, grid_params: dict, run_parallel: bool = True, lock: bool = True, silent: bool = True) -> Tuple[DataFrame, dict]:  # type: ignore
        """
        Grid search is a parameter optimization method that exhaustively searches over a gridded parameter space.
        Grid search returns will return the score each parameter combination for f1, precision and sensitivity so that
        you can choose the best performing combination to build a knowledge pack with.

        Args:
            grid_params (dict): Grid search parameters.
            run_parallel (bool, True): Run grid search in parallel in KB cloud.
            lock (bool, False): Ping for results every 30 seconds until the process finishes.


        grid_params is a nested python dictionary object.

            grid_params = {"Name Of Function":{"Name of Parameter":[ A, B, C]}}

        Where A, B and C are the parameters to search over. Additionally, for each step you may want to search over more than
        one of a functions configurable parameters. To do this simply add another element to the functions dictionary.

            grid_params = {"Name Of Function":{"Name of Parameter 1":[ A, B, C], "Name of Parameter 2":[ D, E]}}

        This will tell grid search to search over 6 different parameter spaces.

        You can also specify more than one step to search over in grid params. This is done by adding another element to
        the function level of the grid_params dictionary.

            grid_params = {"Name Of Function":{"Name of Parameter 1":[ A, B, C], "Name of Parameter 2":[ D, E]}, "Name of Function 2":{"Name of Parameter":[1, 2, 3, 4, 5, 6]}}

        Example:

            grid_params = {'Windowing':{"window_size": [100,200],'delta':[100]}, 'selector_set': {"Recursive Feature Elimination":{'number_of_features':[10, 20]}}, 'Hierarchical Clustering with Neuron Optimization': {'number_of_neurons':[10,20]}}

            results, stats = client.pipeline.grid_search(grid_params)

        """

        print("Executing Pipeline with Steps:\n")
        self.describe(show_params=False)

        self._sandbox.grid_search(grid_params=grid_params, run_parallel=run_parallel)

        time.sleep(5)
        return self.get_results(lock=lock, silent=silent)

    def autosegment_search(self, params: dict, run_parallel: bool = True, lock: bool = True, silent: bool = True) -> Tuple[DataFrame, dict]:  # type: ignore
        """Execute auto segment search pipeline asynchronously.

        Args:
            params (dict): Automation parameters for segment search.
            run_parallel (bool, True): Run in parallel in KB cloud.
            lock (bool, False): Ping for results every 30 seconds until the process finishes.
            silent (bool, True): Silence status updates.
        """
        print("Running AutoSegment Pipeline\n")

        # check that the pipeline is correct for autosegmentation.
        for step_index, step in enumerate(self._sandbox.pipeline.to_list()):
            if step_index == 0:
                if step["type"] not in ["featurefile", "datafile", "capturefile"]:
                    print("First step in pipeline must be a featurefile")
                    return None, None
            else:
                if step["type"] != "transform":
                    print("Pipeline can only contain sensor transforms.")
                    return None, None

        self._sandbox.autosegment_search(params, run_parallel=run_parallel)

        return self.get_results(lock=lock, silent=silent)

    def get_results(
        self,
        lock: bool = False,
        wait_time: int = 15,
        silent: bool = False,
        page_index: int = 0,
        renderer=None,
        **kwargs,
    ) -> Tuple[DataFrame, dict]:  # type: ignore:
        """Retrieve status, results from the kb cloud for the current pipeline.

        Args:
            results to retrieve. The default is the last type that was run.
            lock (bool, False): This will lock the process and continuously ping the KB cloud
            for the status of the pipeline process.
            wait_time (int, 30): The time to wait between individual status checks.
            silent (bool,  False): This will silence updates to every 4th update check.
            page_index (int, 0): The page desired if the result is multi-paged (1-based)

        Returns:
            results (DataFrame or model result): This is the result of the last executed pipeline step.
            stats (dictionary): A dictionary containing the execution summary, features and other
            summary statistics
        """

        self._results = utility.wait_for_pipeline_result(
            self._sandbox,
            lock=lock,
            wait_time=wait_time,
            silent=silent,
            page_index=page_index,
            renderer=renderer,
            **kwargs,
        )

        return self._results[0], self._results[1]

    def data(
        self,
        pipeline_step: int,
        page_index: int = 0,
        convert_datasegments_to_dataframe=True,
    ) -> DataFrame:
        """Retrieves results from a specific pipeline step in the pipeline from stored values in the pipeline cache
        after execution has been performed.

        Args:
            pipeline_step (int): Pipeline step to retrieve results from.
            page_index (int): Index of data to get.
            datasegments (bool): Keep results in datasegments format instead flattening to DataFrame format

        Returns:
            A ModelResultSet if the selected pipeline step is TVO step, otherwise the output of the pipeline
            step is returned as a DataFrame.
        """
        try:
            return self._sandbox.intermediate_data(
                pipeline_step=pipeline_step,
                page_index=page_index,
                convert_datasegments_to_dataframe=convert_datasegments_to_dataframe,
            )
        except HTTPError:
            return None, None

    def get_cached_data(self, pipeline_step: int, page_index: int = 0) -> DataFrame:
        """Retrieves results from a specific pipeline step in the pipeline from stored values in the pipeline cache
        after execution has been performed.

        Args:
            pipeline_step (int): Pipeline step to retrieve results from.
            page_index (int): Index of data to get.
            datasegments (bool): Keep results in datasegments format instead flattening to DataFrame format

        Returns:
            1. A datasegments dictionary if the pipeline step is prior to the feature extraction step
            2. A feature vector DataFrame if the result is before the Model train step
            3. A ModelResultSet if the selected pipeline step is TVO step, otherwise the output of the pipeline
        """
        try:
            return self._sandbox.intermediate_data(
                pipeline_step=pipeline_step,
                page_index=page_index,
                convert_datasegments_to_dataframe=False,
            )
        except HTTPError:
            return None, None

    def clear_cache(self) -> Response:
        """Deletes the cache on KB cloud for this pipeline."""
        if self._sandbox is not None:
            return self._sandbox.delete_cache()

    def reset(self, delete_cache: bool = False, update: bool = False):
        """Reset the current pipeline steps.

        Args:
            delete_cache (bool, False): Delete the cache from KB cloud.
            update (bool, False): Push cleared pipeline to the server
        """
        self._sandbox.clear()
        if update:
            self._sandbox.update()
        self._generator_index = 0
        self._selector_index = 0
        self._data_columns = ""
        self._tvo_call = None
        self._classifier_call = None
        self._training_algorithm_call = None
        self._validation_call = None
        self._group_columns = None
        self._label_column = None
        self._use_query_session = False

        if delete_cache:
            print(
                "\n\nWarning:: You have cache set to delete, this will cause your pipelines to run slower!\n\n"
            )
            self.clear_cache()

    def stop_pipeline(self) -> Response:
        """Kills a pipeline that is running on KB cloud."""
        return self._sandbox.kill_pipeline()

    def delete_sandbox(self) -> Response:
        """Clears the local pipeline steps, and delete the sandbox from the KB cloud."""
        self.reset(delete_cache=True)

        if self._sandbox is not None:
            return self._sandbox.delete()

    def set_input_query(self, name: str, use_session_preprocessor: bool = True):
        """Set the input data to be a stored query.

        Args:
            name (str): The name of the saved query.
            use_session_preprocessor (bool): Use the autosegmentation algorithms for this pipeline
             (if there is one). When this is true, the segmentation algorithm will not show up in
             the pipeline but will be included in the firmware generation.
        """

        query_call = self._client.functions.create_query_call(name)
        query_call.query = self._project.queries.get_query_by_name(
            name, raise_exception=True
        )
        query_call.use_session_preprocessor = use_session_preprocessor

        self._dataset = query_call

        label_column = query_call.query.label_column

        self.set_columns(
            query_call.query.columns._columns,
            query_call.query.metadata_columns._columns + [label_column, "SegmentID"],
            label_column,
        )

        self._add_initial_data()

        if use_session_preprocessor:
            self._preprocess(query_call.query.segmenter)

    def set_input_data(
        self,
        name: str,
        data_columns: Optional[list[str]] = None,
        group_columns: Optional[list[str]] = None,
        label_column: str = None,
    ):
        """Use a data file that has been uploaded as your data source.

        Args:
            name (str, list): The name of the data file or list of datafiles in SensiML cloud.
            data_columns (list, required): Array of data streams to use in model building.
            group_columns (list, required): The List of columns to use when applying aggregate functions
                and defining unique subsets on which to operate.
            label_column (str, required): The column with the true classification.

        """

        if data_columns is None:
            raise Exception("data_columns can not be None")

        if not isinstance(data_columns, list):
            raise Exception("data_columns must be a list")

        if label_column and label_column not in group_columns:
            raise Exception("Label column must be a group column!")

        self.set_columns(data_columns, group_columns, label_column)

        if isinstance(name, list):
            for index, csv_name in enumerate(name):
                if csv_name[-4:] != ".csv":
                    name[index] = f"{csv_name}.csv"
        else:
            if name[-4:] != ".csv":
                name = f"{name}.csv"

        call = self._client.functions.create_datafile_call(name)
        self._dataset = call
        self._dataset.data_columns = self.data_columns
        self._dataset.group_columns = self.group_columns
        self._dataset.label_column = self.label_column

        self._add_initial_data()

    def set_input_features(
        self,
        name: str,
        feature_columns: Optional[list[str]] = None,
        group_columns: Optional[list[str]] = None,
        label_column: Optional[str] = None,
    ):
        """Use a feature file as input to the pipeline (features have already been generated in this case)

        Args:
            name (str, list): The name of the data file or list of feature files in SensiML cloud.
            feature_columns (list, required): Array of data streams to use in model building.
            group_columns (list, required): The List of columns to use when applying aggregate functions
                and defining unique subsets on which to operate.
            label_column (str, required): The column with the true classification.

        """

        self.set_columns(feature_columns, group_columns, label_column)

        if isinstance(name, list):
            for index, csv_name in enumerate(name):
                if csv_name[-4:] != ".csv":
                    name[index] = f"{csv_name}.csv"
        else:
            if name[-4:] != ".csv":
                name = f"{name}.csv"

        call = self._client.functions.create_featurefile_call(name)
        self._dataset = call
        self._dataset.feature_columns = self.data_columns
        self._dataset.group_columns = self.group_columns
        self._dataset.label_column = self.label_column

        self._add_initial_data()

    def set_input_capture(
        self, names: list[str], group_columns: Optional[list[str]] = None
    ):
        """Use a data file that has been uploaded as your data source.

        Args:
            name (str,list): single capture or list of captures file names to use in SensiML cloud.

        """

        if group_columns is None:
            group_columns = ["segment_uuid", "capture_uuid"]

        self.set_columns(list(self._project.columns()), group_columns, None)

        call = self._client.functions.create_capturefile_call(names)
        self._dataset = call
        self._dataset.data_columns = self.data_columns
        self._dataset.group_columns = self.group_columns

        self._add_initial_data()

    def add_linear_step(self, func):
        """Add a step to the pipeline. Automatically tie the previous step and current step.

        Args:
            func (function): A sensiml function method call
        """
        self._sandbox.add_linear_step(func)

    def add_segmenter(self, name: str, params: Optional[dict] = None):
        """Add a Segmenter to the pipeline.

        Args:
            name (str): Name of the segmenter method to add.
            params (dict, optional): Dictionary containing the parameters of the transform.

        """

        if params is None:
            params = {}

        self._add_transform({"name": name, "params": params})

    def add_transform(
        self, name: str, params: Optional[dict] = None, overwrite: bool = True
    ):
        """Add a Transform to the pipeline.

        Args:
            name (str): Name of the transform method to add.
            params (dict, optional): Dictionary containing the parameters of the transform.
            overwrite (boolean): when adding multiple instances of the same transform, set
                overwrite to False for the additional steps and the first instance will not
                be overwritten (default is True)

        """

        if params is None:
            params = {}

        self._add_transform({"name": name, "params": params}, overwrite)

    def add_feature_generator(
        self,
        feature_generators,
        params: Optional[dict] = None,
        function_defaults: Optional[dict] = None,
        return_generator_set: bool = False,
    ):
        """Add a feature generator set to the pipeline.

        Args:
            feature_generators (list): List of feature generators. As names or dictionaries.
            params (dict, {}}): Parameters to apply to the feature generator set.
            function_defaults (dict,{}}): Parameters to apply to all individual feature generators.

        Examples:
            >>> # Add a single feature generator
            >>> client.pipeline.add_feature_generator([{'name': 'Downsample', 'params': {'new_length': 5}}, {'name': 'Mean'}],
                                                   function_defaults = {'columns': sensor_columns})

            >>> # Call multiple functions by name when they use the same same function defaults
            >>> client.pipeline.add_feature_generator(['Mean', 'Standard Deviation', 'Skewness', 'Kurtosis', '25th Percentile',
                                                   '75th Percentile', '100th Percentile', 'Zero Crossing Rate'],
                                                   function_defaults = {'columns': sensor_columns})

            >>> # Call multiple functions using function defaults
            >>> client.pipeline.add_feature_generator([{'name': 'Downsample', 'params': {'new_length': 5}}, {'name': 'Mean'}],
                                                    function_defaults = {'columns': sensor_columns})

            >>> # Call multiple functions by subtype which use different parameters; note all subtypes will take the same inputs
            >>> client.pipeline.add_feature_generator([{'subtype_call': 'Area', 'params': {'sample_rate': 100, 'smoothing_factor': 9}},
                                                    {'subtype_call': 'Time', 'params': {'sample_rate': 100}},
                                                    {'subtype_call': 'Rate of Change'},
                                                    {'subtype_call': 'Statistical'},
                                                    {'subtype_call': 'Energy'},
                                                    {'subtype_call': 'Amplitude', 'params': {'smoothing_factor': 9}},
                                                    {'subtype_call': 'Physical', 'params': {'sample_rate': 100}}
                                                    ],
                                                    function_defaults={'columns': sensor_columns},
                                                   )

            >>> # Mix subtype and specify additional feature generators
            >>> client.pipeline.add_feature_generator([{'subtype_call': 'Statistical'},
                                                    {'name': 'Downsample', 'params': {'new_length': 5}},
                                                    ],
                                                    function_defaults={'columns': sensor_columns},
                                                    )

            >>> # Call the same feature generators multiple times with different parameters
            >>> client.pipeline.add_feature_generator([{'name': 'Downsample', 'params': {'new_length': 5, 'columns': sensor_columns[0]}},
                                                    {'name': 'Downsample', 'params': {'new_length': 12}},
                                                    ],
                                                    function_defaults={'columns': sensor_columns},
                                                    )

        """

        if params is None:
            params = {}

        if function_defaults is None:
            function_defaults = {}

        # if we get a list of strings
        feature_generators = copy.deepcopy(feature_generators)
        if isinstance(feature_generators[0], str):
            feature_generators = list(
                map(lambda x: {"name": x, "params": {}}, feature_generators)
            )
            for fg in feature_generators:
                for default_param in list(function_defaults.keys()):
                    if default_param not in list(fg["params"].keys()):
                        fg["params"].update(
                            {default_param: function_defaults.get(default_param)}
                        )

        # if we get a list of dicts
        elif isinstance(feature_generators[0], dict):
            for fg in feature_generators:
                if fg.get("params", None) is None:
                    fg["params"] = {}
                for default_param in list(function_defaults.keys()):
                    if default_param not in list(fg["params"].keys()):
                        fg["params"].update(
                            {default_param: function_defaults.get(default_param)}
                        )

        else:
            print(
                "Feature Generator was improperly specified. See Documentation (client.pipeline.add_feature_generator?) for examples."
            )
            raise InvalidParameterException(
                "Feature Generator was improperly specified. See Documentation (client.pipeline.add_feature_generator?) for examples."
            )

        return self._add_feature_generator(
            feature_generators, params, return_generator_set=return_generator_set
        )

    def add_feature_selector(
        self, feature_selectors: list[dict], params: Optional[dict] = None
    ):
        """Add a feature selection set to the pipeline.

        Args:
            feature_selectors (List): List of dictionaries containing feature selectors
            params (dict, {}): Parameters of the feature selector set.

        Examples:
            >>> client.pipeline.add_feature_selector([{"name":"Recursive Feature Elimination", "params":{"method":"Log R"}}],
            >>>                                    params = {"number_of_features":20})
        """

        if params is None:
            params = {}

        self._add_feature_selector(feature_selectors, params)

    def add_augmentation(
        self,
        augmentation: list[dict],
        params: Optional[dict] = None,
        overwrite: bool = True,
    ):
        """
        Add augmentation set to the pipeline.

        Args:
            augmentation (List): List of dictionaries containing time series augmentations
            params (dict, {}): Parameters of the augmentation set.

        Examples:
            >>> client.pipeline.add_augmentation([{"name": "Add Noise", "params": {
            >>>                                                                 "background_scale_range": [100, 1000],
            >>>                                                                 "target_labels": ['idle','walking'],
            >>>                                                                 "target_sensors": ['AccelerometerX', 'GyroscopeZ'],
            >>>                                                                 "fraction": 1.2,
            >>>                                                                 "noise_types": ["pink", "white"],
            >>>                                                                 "filter": {"Set": ["Train"]}
            >>>                                                                 }
            >>>                                   }])

        """
        if params is None:
            params = {}

        self._add_augmentation(augmentation, params, overwrite)

    def set_validation_method(self, name: str, params: Optional[dict] = None):
        """Set the validation method for the tvo step.

        Args:
            name (str): Name of the validation method to use.
            params (dict, optional): Parameters for the validation method.

        """

        if params is None:
            params = {}

        self._validation_call = call = (
            self._client.functions.create_validation_method_call(name)
        )
        for k, v in params.items():
            setattr(call, k, v)

    def set_classifier(self, name: str, params: Optional[dict] = None):
        """Classification method for the TVO step to use.

        Args:
            name (str): Name of the classification method.
            params (dict, optional): Parameters of the classification method.
        """

        if params is None:
            params = {}

        self._classifier_call = call = self._client.functions.create_classifier_call(
            name
        )
        for k, v in params.items():
            setattr(call, k, v)

    def set_regression(self, name: str, params: Optional[dict] = None):
        """Regression method for the TVO step to use.

        Args:
            name (str): Name of the classification method.
            params (dict, optional): Parameters of the classification method.
        """

        if params is None:
            params = {}

        self._classifier_call = call = self._client.functions.create_classifier_call(
            name
        )
        for k, v in params.items():
            setattr(call, k, v)

    def set_training_algorithm(self, name: str, params: Optional[dict] = None):
        """Training algorithm for the TVO step to use.

        Args:
            name (str): Name of the training algorithm.
            params (dict, optional): Parameters of the training algorithm.
        """
        if params is None:
            params = {}

        self._training_algorithm_call = call = (
            self._client.functions.create_training_algorithm_call(name)
        )
        for k, v in params.items():
            setattr(call, k, v)

    def set_tvo(self, params: Optional[dict] = None):
        """Description of the train, validate optimize step, which consists of a training algorithm,
        validation method and classifier.

        Args:
            params (dict, optional): Parameters of the TVO step.

        Example:
            >>> client.pipeline.set_validation_method('Stratified K-Fold Cross-Validation', params={'number_of_folds':3})
            >>> client.pipeline.set_classifier('PME', params={"classification_mode":'RBF','distance_mode':'L1'})
            >>> client.pipeline.set_training_algorithm('Hierarchical Clustering with Neuron Optimization', params = {'number_of_neurons':10})
            >>> client.pipeline.set_tvo({'label_column':'Label', 'ignore_columns': ['Subject', 'Rep']})
        """

        if params is None:
            params = {}

        self._tvo_call = call = self._client.functions.create_train_and_validation_call(
            "tvo"
        )
        for k, v in params.items():
            setattr(call, k, v)
        if (
            self._classifier_call
            and self._training_algorithm_call
            and self._validation_call
        ):
            call.add_classifier(self._classifier_call)
            call.add_validation_method(self._validation_call)
            call.add_optimizer(self._training_algorithm_call)
        else:
            raise PipelineOrderException(
                "Set classifier, validation, and training_algorithm methods before calling."
            )

        self._add_tvo(self._tvo_call)

    def iterate_columns(self, fg, n_columns=None, columns=None):
        """
        Builds Multiple Feature generators by iterating over the input columns

        Args:
            fg (dict): Single input feature generator folowing the standard format
            n_columns (int): The number of columns to return as a combination.
            columns (list): if None, will use the columns in the input feature generator, otherwise will use this list provided

        Example
            >>> fg =  {'name':'Downsample with Min Max Scaling', 'params':{"columns": ['gyrZ','gyrX'] , "new_length": 15}}
            >>> fg_new = client.pipeline.iterate_columns(fg, n_columns=1)

            >>> print(fg_new)

            Output:
            [{'name': 'Downsample with Min Max Scaling', 'params': {'columns': ['gyrX'], 'new_length': 15}}, {'name': 'Downsample with Min Max Scaling', 'params': {'columns': ['gyrX'], 'new_length': 15}}]
        """

        if n_columns is None:
            function = self._client.functions.get_function_by_name(fg["name"])
            n_columns = get_contract_column_type(function.input_contract)

            if n_columns is None or n_columns < 0:
                return [fg]

        if columns is None:
            columns = fg["params"]["columns"]

        column_list = itertools.combinations(columns, n_columns)

        fg_list = []
        tmp_fg = copy.deepcopy(fg)

        for column_combo in column_list:
            tmp_fg["params"]["columns"] = list(column_combo)
            fg_list.append(copy.deepcopy(tmp_fg))

        return fg_list

    def _preprocess(self, segmenterid):
        """adds the segmenter preprocess steps to the pipeline"""

        try:
            segmenter = self._project.get_segmenters().loc[segmenterid]
        except TypeError:
            print("Error. Segmenter associated with this query does not exist.")
            return

        if segmenter.preprocess is None:
            return

        preprocess = json.loads(segmenter.preprocess)

        for i in range(len(preprocess.keys())):
            transform = preprocess[str(i)]
            self._add_transform(
                {
                    "name": transform["params"]["name"],
                    "params": transform["params"]["inputs"],
                },
                False,
            )
            self._data_columns.add(transform["actual_name"])
            print(f"Adding Preprocess Transform {transform['params']['name']}")

        self._use_query_session = True

    def _check_for_input_data(self):
        if len(self._sandbox._pipeline.to_list()) == 0:
            raise PipelineOrderException(
                "You must specify the input data before specifying additional steps"
            )

    def _add_tvo(self, call):
        self._add_label_column(call)
        self._add_ignore_columns(call)

        self.tvo_index = self.get_pipeline_length()
        self._sandbox.add_linear_step(call)

    def _add_transform(self, transform, overwrite=True):
        if (
            self.get_function_type(transform["name"]) == "Segmenter"
            and self._use_query_session
        ):
            raise Exception(
                "You have set use query session True, can't add a segmentation step."
            )

        self._check_for_input_data()

        logger.debug("transform:" + str(transform["name"]))

        if (
            self.get_function_type(transform["name"]) == "Segmenter"
            and self.group_columns
        ):
            if "Cascade" not in transform["name"]:
                self._group_columns.discard("SegmentID")
            self._group_columns.discard("CascadeID")

        call = self._client.functions.create_function_call(transform["name"])
        # Add params to function call object
        for k, v in transform["params"].items():
            setattr(call, k, v)

        self._set_call_columns(call)
        self._sandbox.add_linear_step(call, overwrite)

        if (
            self.get_function_type(transform["name"]) == "Segmenter"
            and self.group_columns
        ):
            self._group_columns.add("SegmentID")
            if "Cascade" in transform["name"]:
                self._group_columns.add("CascadeID")

        if transform["name"] == "Feature Cascade" and self.group_columns:
            self._group_columns.add("CascadeID")

    def _add_feature_generator(
        self,
        feature_generators,
        feature_generator_params={},
        return_generator_set=False,
    ):
        self._check_for_input_data()

        generator_set = self._client.functions.create_generator_call_set(
            "generator_set"
        )

        logger.debug("feature_generator_set")

        # set any generator set params given
        for k, v in feature_generator_params.items():
            setattr(generator_set, k, v)

        subtype_functions = []
        for fg in feature_generators:
            if fg.get("subtype_call", None):
                logger.debug("generator_subtype_call:" + str(fg["subtype_call"]))
                for name in self._client.list_functions(
                    "Feature Generator",
                    str(fg["subtype_call"]),
                    kp_functions=True,
                    qgrid=False,
                ).NAME:
                    subtype_functions.append({"name": name, "params": fg["params"]})

        feature_generators.extend(subtype_functions)

        feature_generator_list = []
        for fg in feature_generators:
            if fg.get("name", None):
                feature_generator_list.extend(self.iterate_columns(fg))

        for fg in feature_generator_list:
            logger.debug("generator_name:" + str(fg["name"]))
            call = self._client.functions.create_function_call(fg["name"])

            for k, v in fg["params"].items():
                setattr(call, k, v)

            generator_set.add_generator_call(call)

        if return_generator_set:
            return generator_set

        self._add_group_columns(generator_set)

        self._generator_index = self.get_pipeline_length()

        self._sandbox.add_linear_step(generator_set)

    def _add_augmentation(self, augmentations, augmentation_set_params, overwrite=True):
        self._check_for_input_data()

        augmentation_set = self._client.functions.create_augmentation_call_set(
            "augmentation_set"
        )

        logger.debug("augmentation_set")

        for k, v in augmentation_set_params.items():
            setattr(augmentation_set, k, v)

        for augmentation in augmentations:
            logger.debug("augmentations:" + augmentation["name"])

            call = self._client.functions.create_augmentation_call(augmentation["name"])

            for k, v in augmentation["params"].items():
                setattr(call, k, v)

            augmentation_set.add_augmentation_call(call)

        self._add_group_columns(augmentation_set)

        self._add_passthrough_columns(augmentation_set)

        self._add_label_column(augmentation_set)

        self._augmentation_index = self.get_pipeline_length()

        self._sandbox.add_linear_step(augmentation_set, overwrite)

    def _add_feature_selector(self, feature_selectors, selector_set_params={}):
        self._check_for_input_data()
        selector_set = self._client.functions.create_selector_call_set("selector_set")
        logger.debug("feature_selector_set")

        for k, v in selector_set_params.items():
            setattr(selector_set, k, v)

        for fs in feature_selectors:
            logger.debug("feature_selector:" + fs["name"])
            call = self._client.functions.create_function_call(fs["name"])
            for k, v in fs["params"].items():
                setattr(call, k, v)
            selector_set.add_selector_call(call)

        self._add_passthrough_columns(selector_set)
        self._add_label_column(selector_set)

        self._selector_index = self.get_pipeline_length()
        self._sandbox.add_linear_step(selector_set)

    def _add_initial_data(self):
        """Add the raw data call to the pipeline"""
        if self.get_pipeline_length() != 0:
            raise PipelineOrderException(
                "Input data must be the first step in the pipeline"
            )

        self._sandbox.add_linear_step(self._dataset)

    def _add_label_column(self, call):
        if self.label_column and hasattr(call, "label_column"):
            if call.label_column is None:
                call.label_column = self.label_column

    def _add_group_columns(self, call):
        if self.group_columns and hasattr(call, "group_columns"):
            if call.group_columns is None:
                call.group_columns = self.group_columns

    def _add_passthrough_columns(self, call):
        if self.group_columns and hasattr(call, "passthrough_columns"):
            if call.passthrough_columns is None:
                call.passthrough_columns = self.group_columns

    def _add_ignore_columns(self, call):
        if (self.label_column and self.group_columns) and hasattr(
            call, "ignore_columns"
        ):
            if call.ignore_columns is None:
                call.ignore_columns = list(
                    set(self.group_columns) - set([self.label_column])
                )
        elif hasattr(call, "ignore_columns") and call.ignore_columns is None:
            call.ignore_columns = []

    def _set_call_columns(self, call):
        self._add_label_column(call)
        self._add_group_columns(call)
        self._add_passthrough_columns(call)
        self._add_ignore_columns(call)

    def features_to_tensor(
        self,
        feature_vectors,
        validate=0.1,
        test=0.1,
        label=None,
        feature_columns=None,
        class_map=None,
        dtype=np.int32,
        int8_input_type=True,
        shape=None,
        verbose=True,
    ):
        """Converts a SensiML feature vector Dataframe into a train, test, validate set of Numpy arrays to use in training a tensorflow model

        Args:
            feature_vectors (DataFrame): DataFrame of feature vectors returned from SensiML Pipeline
            validate (float, optional): percentage of data to use in validation set. Defaults to 0.1.
            test (float, optional): percentage of data to use in test set. Defaults to 0.1.
            label (str, optional): the label column for the feature vectors. Defaults to None.
            feature_columns (list, optional): the coluns of the feature vector DataFrame containing features. Defaults to None.
            class_map (dict, optional): a class map describing the mapping of labels to int values. Defaults to None.
            dtype (_type_, optional): the dtype of the tensorflow object to create. Defaults to np.int32.
            int8_input_type (bool, optional): Scales the SensiML Features to int8 from uint8. Defaults to True.
            shape (tuple, optional): Reshape the dataframe before loading it into the numpy array. Defaults to None.

        Returns:
            A tuple containing numpy arrays for traning a TensorFlow model along with the class map x_train, x_test, x_validate, y_train, y_test, y_validate, class_map
        """
        if label is None:
            label = self._label_column

        if class_map is None:
            class_map = {k: v for v, k in enumerate(feature_vectors[label].unique())}

        num_classes = len(class_map)

        feature_vectors["__CAT_LABEL__"] = feature_vectors[label].apply(
            lambda x: class_map[x]
        )

        if feature_columns is None:
            feature_columns = [
                col for col in feature_vectors.columns if col[:4] == "gen_"
            ]

        resample = feature_vectors.sample(frac=1, axis=0).reset_index(drop=True)

        if int8_input_type:
            resample_features = resample[feature_columns] - 127
        else:
            resample_features = resample[feature_columns]

        y_values_encoded = get_one_hot(resample["__CAT_LABEL__"].values, num_classes)

        y_values_encoded = y_values_encoded.reshape(resample.shape[0], num_classes)

        if shape is None:
            shape = resample_features.shape

        x_values = resample_features.values[:, :].reshape(shape)

        SAMPLES = x_values.shape[0]
        # Calculate the indices of each section.
        train = 1.0 - (test + validate)
        TRAIN_SPLIT = int(train * SAMPLES)
        TEST_SPLIT = int(test * SAMPLES + TRAIN_SPLIT)

        # Use np.split to chop our data into three parts.
        # The second argument to np.split is an array of indices where the data will be
        # split. We provide two indices, so the data will be divided into three chunks.
        x_train, x_test, x_validate = np.split(x_values, [TRAIN_SPLIT, TEST_SPLIT])
        y_train, y_test, y_validate = np.split(
            y_values_encoded, [TRAIN_SPLIT, TEST_SPLIT]
        )

        if verbose:
            print("-----  Summary  -----")
            print("Class Map:" + str(class_map))
            print("Train:\n total: ", x_train.shape[0])
            print(" by class:", y_train.sum(axis=0))

            print("Validate:\n total: ", x_validate.shape[0])
            print(" by class:", y_validate.sum(axis=0))

            print("Test:\n total: ", x_test.shape[0])
            print(" by class:", y_test.sum(axis=0))

        return (
            x_train.astype(dtype),
            x_test.astype(dtype),
            x_validate.astype(dtype),
            y_train.astype(dtype),
            y_test.astype(dtype),
            y_validate.astype(dtype),
            class_map,
        )

    def visualize_features(
        self, feature_vector: DataFrame, label_column: Optional[str] = None
    ):
        """Makes a plot of feature vectors by class to aid in understanding your model

        Args:
            feature_vector (DataFrame): Dataframe containing feature vectors and label column
        """
        if label_column is None:
            label_column = self.label_column

        return Visualize(
            feature_vector=feature_vector, label=label_column
        ).plot_features()

    def visualize_neuron_array(
        self, model, feature_vector, featureX=None, featureY=None, neuron_alpha=0.2
    ):
        """Makes a plot of feature vectors by class to aid in understanding your model

        Args:
            model (model/knowledgepack): The model or knowledgepack to use for plotting the neurons
            feature_vector (DataFrame): Dataframe containing feature vectors and label column
            featureX (str): The name of the feature for the x axis
            featureY (str): The name of the feature for the y axis

        """

        if hasattr(model, "knowledgepack"):
            if (
                model.knowledgepack.device_configuration.get("classifier", None)
                != "PME"
            ):
                print(
                    "Visualize neuron array is only supported for models using the PME classifier."
                )
                return

        feature_columns = [col for col in feature_vector.columns if col[:4] == "gen_"]
        if featureX is None:
            featureX = feature_columns[0]
        if featureY is None:
            featureY = feature_columns

        Visualize(
            model=model, feature_vector=feature_vector, label=self.label_column
        ).neuron_feature_map(featureX, featureY, neuron_alpha=neuron_alpha)


def get_contract_column_type(input_contract):
    column_contract = None

    for elem in input_contract:
        if elem.get("name", None) == "columns":
            column_contract = elem
            break

    if isinstance(column_contract, dict):
        return column_contract.get("num_columns", None)

    return None


def generate_custom_feature_selector(feature_summary):
    """
    takes a feature summary and resturns the Custom Feature Selection by Index feature selection dictionary
    """
    current_gen_index = 1
    last_gen_index = feature_summary[0]["Feature"].split("_")[1]
    feature_selection = {1: []}
    for feature in feature_summary:
        if last_gen_index != feature["Feature"].split("_")[1]:
            current_gen_index += 1
            last_gen_index = feature["Feature"].split("_")[1]
            feature_selection[current_gen_index] = []
        feature_selection[current_gen_index].append(feature["GeneratorFamilyIndex"])

    return feature_selection


def get_one_hot(targets, nb_classes):
    res = np.eye(nb_classes)[np.array(targets).reshape(-1)]
    return res.reshape(list(targets.shape) + [nb_classes])
