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

import json
import logging
from collections import deque
from copy import deepcopy

import engine.base.pipeline_utils as pipeline_utils
from datamanager.models import PipelineExecution, Query
from datamanager.query import _get_query_summary_statistics
from django.core.exceptions import ObjectDoesNotExist
from engine.automationengine_mixin.automationengine_exception import ValidationError
from engine.automationengine_mixin.create_cost_table_mixin import CreateCostTableMixin
from engine.automationengine_mixin.genetic_iteration_mixin import GeneticIterationMixin
from engine.automationengine_mixin.parameter_inventory_mixin import (
    ParameterInventoryMixin,
)
from engine.automationengine_mixin.parameter_optimizer_utils import (
    define_auto_params_weight_parm,
)
from engine.automationengine_mixin.run_pipeline_population_mixin import (
    RunPipelinePopulationMixin,
)
from engine.automationengine_mixin.save_knowledgepack_mixin import (
    SaveKnowledgepackMixin,
)
from engine.parallelexecutionengine import ParallelExecutionEngine
from logger.log_handler import LogHandler
from pandas import DataFrame


logger = LogHandler(logging.getLogger(__name__))


class AutomationEngine(
    ParallelExecutionEngine,
    GeneticIterationMixin,
    RunPipelinePopulationMixin,
    SaveKnowledgepackMixin,
    ParameterInventoryMixin,
    CreateCostTableMixin,
):
    def __init__(
        self,
        params,
        task_id,
        user,
        project_id,
        sandbox,
        execution_id=None,
        err_queue=deque(),
    ):

        super(AutomationEngine, self).__init__(
            task_id,
            user,
            project_id,
            sandbox,
            PipelineExecution.ExecutionTypeEnum.AUTOML,
            execution_id,
            err_queue,
        )

        self.version = 2
        self.sandbox = sandbox
        self.project = sandbox.project
        self.execution_summary = []
        self.summary = {}
        self.feature_table = DataFrame()
        self.fitness = 0.0
        self.max_fitness = 0.9
        self.pipeline = []
        self.group_columns = []
        self.data_columns = []
        self.fitness = {}
        self.ga_steps = []  # Names of steps that will run through GA
        self.ga_pipeline = (
            []
        )  # Pipeline beginning with first GA step; can contain non-GA steps
        self.all_libraries = []
        self.static_pipeline = []
        self.population_size = 10
        self.iterations = 1
        self.mutation_rate = 0.1
        self.recreation_rate = 0.1
        self.survivor_rate = 0.5
        self.reset = False
        self.last_iteration = None
        self.param_number_of_models_to_return = 5
        self.segmenter_id = None
        self.random_seed = None
        self.error_log = []
        self.sample_by_metadata_list = []
        self.custom_class_map = None
        self.param_input_columns = None
        self.param_allow_unknown = False
        self.fitted_population_log = None
        self.mapped_inputs_previous_iterations = None
        self.auto_param_weights = None
        self.recognition_split_step = None
        self.disable_automl = False

        self.initialize_genetic_alg_parameters(params)

    def check_for_disable_automl(self, params):
        if params.get("disable_automl", False):
            params["iterations"] = 0
            params["search_steps"] = []
            params["population_size"] = 1
            params["number_of_models_to_return"] = 1
            params["single_model"] = True
            self.disable_automl = True

        return params

    def initialize_genetic_alg_parameters(self, params):

        self.param_for_cache = deepcopy(params)

        params = self.check_for_disable_automl(params)

        self.fitness = params.get(
            "fitness",
            {
                "accuracy": 1.0,
                "f1_score": 0.0,
                "features": 0.3,
                "sensitivity": 0.7,
                "classifiers_sram": 0.5,
                "positive_predictive_rate": 0.0,
            },
        )

        self.ga_steps = sorted(params.get("search_steps", ["selectorset", "tvo"]))
        self.population_size = params.get("population_size", 10)
        self.iterations = params.get("iterations", 1)
        self.mutation_rate = params.get("mutation_rate", 0.1)
        self.recreation_rate = params.get("recreation_rate", 0.2)
        self.survivor_rate = params.get("survivor_rate", 0.5)
        self.param_allow_unknown = params.get("allow_unknown", False)

        validate_genetic_algorithm_parameters(
            self.mutation_rate, self.recreation_rate, self.survivor_rate
        )

        self.reset = params.get("reset", True)

        self.random_seed = params.get("random_seed", None)
        self.param_number_of_models_to_return = params.get(
            "number_of_models_to_return", 5
        )

        self.param_input_columns = params.get("input_columns", None)

        prediction_target_parameters = {
            "accuracy": 0,
            "positive_predictive_rate": 0,
            "sensitivity": 0,
            "f1_score": 0,
        }
        self.param_prediction_target = params.get(
            "prediction_target(%)", prediction_target_parameters
        )

        self.param_prediction_target = update_target_dictionary(
            self.param_prediction_target, prediction_target_parameters
        )

        validate_target_parameters(
            self.param_prediction_target, prediction_target_parameters
        )

        hardware_target_parameters = {"classifiers_sram": 0, "latency": 0}
        self.param_hardware_target = params.get(
            "hardware_target", hardware_target_parameters
        )

        self.param_hardware_target = update_target_dictionary(
            self.param_hardware_target, hardware_target_parameters
        )

        validate_target_parameters(
            self.param_hardware_target, hardware_target_parameters
        )

        self.requirement_satisfaction = False

        validate_population_size(
            self.param_number_of_models_to_return, self.population_size
        )

        self.set_training_algorithm = validate_training_algorithms(
            params.get("set_training_algorithm", None), self.param_allow_unknown
        )

        if sum(self.param_prediction_target.values()):
            self.fitness = update_auto_param_weights_for_prediction_values(
                self.fitness, self.param_prediction_target
            )

        if sum(self.param_hardware_target.values()):
            self.fitness = update_auto_param_weights_for_hardware_values(
                self.fitness, self.param_hardware_target
            )

        self.auto_param_weights = define_auto_params_weight_parm(self.fitness)

        if sum(self.param_hardware_target.values()):
            if self.fitness["classifiers_sram"] == 1:
                self.auto_param_weights.loc[
                    "classifiers_sram", "min"
                ] = self.param_hardware_target["classifiers_sram"]

        if len(self.sandbox.pipeline) and self.sandbox.pipeline[0]["type"] == "query":
            self.sandbox.pipeline[0]["outputs"] = ["temp.raw"]

            try:
                query = Query.objects.get(
                    project=self.project, name=self.sandbox.pipeline[0]["name"]
                )
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist(
                    f"The selected query {self.sandbox.pipeline[0]['name']} does not exist,"
                )

            self.group_columns = json.loads(query.metadata_columns) + [
                query.label_column
            ]

            self.segmenter_id = query.segmenter_id
            self.data_columns = query.columns
            self.data_columns = self.data_columns[1:-1].replace('"', "").split(", ")
            self.label = query.label_column

            validate_number_of_classes(
                _get_query_summary_statistics(
                    None, query.project.uuid, query.id, query=query
                )
            )

            if len(query.capture_configurations.values()) > 0:
                self.sample_rate = query.capture_configurations.values()[0][
                    "configuration"
                ]["capture_sources"][0]["sample_rate"]

        elif len(self.sandbox.pipeline) and self.sandbox.pipeline[0]["type"] in [
            "featurefile",
            "datafile",
        ]:
            self.sandbox.pipeline[0]["outputs"] = ["temp.raw"]
            self.data_columns = self.sandbox.pipeline[0].get("data_columns", None)
            self.label = self.sandbox.pipeline[0].get("label_column", "")
            self.group_columns = self.sandbox.pipeline[0].get("group_columns", [])

        else:
            raise ValidationError(
                "Must define either query or feature file as first step in pipeline."
            )

        self.pipeline = pipeline_utils.make_pipeline_linear(self.sandbox.pipeline)

        if not self.disable_automl:
            self.ga_steps = validate_ga_steps(self.ga_steps, self.pipeline)

        if self.ga_steps:
            recognition_pipeline = [
                step
                for step in self.pipeline
                if step["type"]
                in ["segmenter", "transform", "selectorset", "tvo", "generatorset"]
            ]
            index = [step["type"] for step in recognition_pipeline].index(
                self.ga_steps[0]
            ) - 1
            if recognition_pipeline[index]["type"] == "selectorset":
                index -= 1

            self.recognition_split_step = recognition_pipeline[index]

        self.param_validation_method = get_validation_method_from_pipeline(
            self.pipeline
        )

        self.init_cache_manager(self.pipeline)

        if self._cache_manager._cache_file_exists("fitted_population_log.pkl"):
            self._cache_manager.delete_file("fitted_population_log.pkl")
        if self._cache_manager._cache_file_exists("fitted_population_final.json"):
            self._cache_manager.delete_file("fitted_population_final.json")

    def reset_pipeline(self):
        self.pipeline = deepcopy(
            pipeline_utils.make_pipeline_linear(self.sandbox.pipeline)
        )
        if self.ga_steps:
            self.split = [step["type"] for step in self.pipeline].index(
                self.ga_steps[0]
            )

    def get_static_pipeline_final_data(self):
        return self._cache_manager.get_result_from_cache(
            self.pipeline[self.split - 1]["outputs"][0], cache_key="data"
        )[0]

    def run_automl_search(self, feature_data):

        self.initialize_genetic_algorithm_pipeline(feature_data)

        inventory = self.get_the_parameter_inventory(feature_data)

        fitness_summary, results = self.run_genetic_algorithm(inventory)

        return fitness_summary, results

    def automate(self):

        fitted_population = None
        results = None

        if self.disable_automl:
            results, fitness_summary = self.execute_custom_pipeline()

        else:
            self.execute_the_static_part_of_the_pipeline()

            feature_data = self.get_static_pipeline_final_data()

            (fitted_population, results) = self.run_automl_search(feature_data)

            fitness_summary = self.write_the_internal_cache_variables(
                fitted_population, results
            )

        if len(self.error_log) > 0:
            logger.warn(
                {
                    "message": "AutoML Error reports",
                    "data": self.error_log,
                    "sandbox_uuid": self.sandbox.uuid,
                    "project_uuid": self.project.uuid,
                    "log_type": "PID",
                    "task_id": self.task_id,
                }
            )

        logger.userlog(
            {
                "message": "Automation Summary",
                "data": fitness_summary.to_dict(),
                "sandbox_uuid": self.sandbox.uuid,
                "project_uuid": self.project.uuid,
                "log_type": "PID",
                "task_id": self.task_id,
            }
        )

        self._temp.clean_up_temp()

        return fitness_summary, DataFrame()


def validate_ga_steps(ga_steps, pipeline):
    if not ga_steps:
        raise ValidationError(
            "No search steps are selected. Use custom training to tune for a single pipeline."
        )

    valid_ga_steps = []
    for ga_step in ga_steps:
        for step in pipeline:
            if step["type"] == ga_step:
                valid_ga_steps.append(ga_step)

    return valid_ga_steps


def get_validation_method_from_pipeline(pipeline):
    return pipeline[-1]["validation_methods"][0]


###############################


def update_auto_param_weights_for_prediction_values(fitness, prediction_target):
    fitness["accuracy"] = 0.01
    fitness["f1_score"] = 0.01
    fitness["sensitivity"] = 0.01
    fitness["positive_predictive_rate"] = 0.01

    for key in prediction_target.keys():
        if prediction_target[key]:
            fitness[key] = 1.0
    return fitness


def update_auto_param_weights_for_hardware_values(fitness, hardware_target):
    fitness["features"] = 0.1
    fitness["classifiers_sram"] = 0.01

    for key in hardware_target.keys():
        if hardware_target[key]:
            fitness[key] = 1.0
    return fitness


def update_target_dictionary(new_items, template):
    # if all target parameters (dictionary keys) are not defined,
    # updating template dictionary with new items.
    template.update(new_items)
    return template


def validate_target_parameters(user_input, target_parameters):
    # validating the target input values
    for parameters in user_input.keys():
        if parameters not in target_parameters.keys():
            raise ValidationError(
                "'"
                + parameters
                + "' is not in the target list. "
                + "Please use the items in the list; "
                + str(list(target_parameters.keys()))
            )


def validate_population_size(number_of_models_to_return, population_size):
    # validate the population size
    if number_of_models_to_return > population_size:
        raise ValidationError(
            "Selected 'population_size' should be greater than 'number_of_models_to_return'"
        )


def validate_genetic_algorithm_parameters(
    mutation_rate, recreation_rate, survivor_rate
):
    if sum([mutation_rate, recreation_rate, survivor_rate]) > 0.95:
        raise ValidationError(
            "ERROR: Summation of recreation_rate, mutation_rate and"
            + " survivor_rate cannot be greater than 0.95."
        )


def validate_number_of_classes(query_stat):

    if query_stat is None:
        raise ValidationError(
            "The input query contains no data. Check the query parameters to make sure there is data."
        )

    label_list = list(query_stat["samples"].keys())

    if len(label_list) < 2:
        raise ValidationError(
            "There is only a single class in the data set ["
            + label_list[0]
            + "]. AutoML only supports multi-class models.\n"
            + "Suggestions:\n"
            + "1- Add another class to the query.\n"
            + "2- If your data has only one class, add a negative/idle class. i.e: if the only class you have is 'walking' you would add examples of a 'not walking' class."
            # TODO: uncomment next line when we have PoC documentation page and give a link to PoC page. popcorn demo is ideal for this case
            # + "2- You can use SensiML-python interface to create a single class model.\n"
        )


def validate_training_algorithms(training_algorithms, allow_unknown: bool = False):
    if training_algorithms is None:
        return

    if isinstance(training_algorithms, list):
        training_algorithms = {k: {} for k in training_algorithms}

    for algorithm in training_algorithms.keys():
        if algorithm not in [
            "Hierarchical Clustering with Neuron Optimization",
            "RBF with Neuron Allocation Optimization",
            "Random Forest",
            "xGBoost",
            "Train Fully Connected Neural Network",
        ]:
            raise ValidationError(
                "Training algorithm '{}' is not supported by Auto ML.".format(algorithm)
            )

    if allow_unknown:
        allowed_unknown_training_algorithms = [
            "Train Fully Connected Neural Network",
            "RBF with Neuron Allocation Optimization",
            "Hierarchical Clustering with Neuron Optimization",
        ]
        for key in list(training_algorithms.keys()):
            if key not in allowed_unknown_training_algorithms:
                training_algorithms.pop(key)

    return training_algorithms
