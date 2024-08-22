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
import random
from copy import deepcopy

from engine.automationengine_mixin import parameter_optimizer_utils as param_optimizer
from engine.automationengine_mixin.automationengine_exception import ValidationError
from engine.base.cache_manager import load_persisitent_variables
from engine.base.temp_cache import TempCache
from engine import drivers
from library.models import Transform
from logger.log_handler import LogHandler
from numpy import inf, unique
from pandas import DataFrame, concat
from sklearn.utils import resample

logger = LogHandler(logging.getLogger(__name__))


MAX_NUMBER_FEATURES = 20000
import logging
from copy import deepcopy

logger = LogHandler(logging.getLogger(__name__))


MAX_NUMBER_FEATURES = 20000


class GeneticIterationMixin:
    def __init__(self):
        pass

    def run_genetic_algorithm(self, inventory):
        self.last_iteration = 0

        fitted_population = None

        if self.reset:
            self._cache_manager.evict_key("auto_results")
        else:
            fitted_population = self.load_cached_automl_data()

        fitted_population = self.genetic_iterations(fitted_population, inventory)

        # TODO: move this to the intialize step (currently cache_manager is not initialized until static pipeline is run)
        save_automl_params(self._cache_manager, self.param_for_cache)

        # TODO: this may not be implemented correctly for custom pipelines
        save_static_pipeline_for_validation(self._cache_manager, self.sandbox.pipeline)

        # train on all the training data using recall for the final model
        fitness_summay, results = self.final_run_with_recall(fitted_population)

        return fitness_summay, results

    def run_population_for_each_library(
        self,
        ga_pipeline,
        custom_class_map,
        population,
        generation,
        recall=False,
    ):
        mapped_inputs = None
        clean_cache = False

        for i, step in enumerate(ga_pipeline):
            map_inputs = False if i == 0 else True
            func = get_driver(step)

            if recall:
                clean_cache = True
                if step["type"] == "tvo":
                    clean_cache = False

            else:
                if (step["type"] == "tvo") and (custom_class_map is not None):
                    population = add_class_map_to_optimizer(
                        population, custom_class_map, "tvo"
                    )

            (
                population,
                results_tvo,
                mapped_inputs,
                failed_pipeline_indexes,
            ) = self.run_population(
                step_index=i,
                step=step,
                func=func,
                population=population,
                iteration=generation,
                mapped_inputs=mapped_inputs,
                map_inputs=map_inputs,
                clean_cache=clean_cache,
                return_results=True,
            )

        return population, results_tvo, mapped_inputs, failed_pipeline_indexes

    def get_population_fitness_score(
        self,
        offspring_population,
        results_tvo,
        generation,
        survivors,
        population_size,
    ):
        offspring_population = separate_tvo_libraries(offspring_population)
        cost_table, _ = self.create_cost_table(
            offspring_population, results_tvo, generation
        )

        results_tvo, cost_table = model_check(
            results_tvo, cost_table, param_optimizer.model_stat_list_tuple
        )

        fitted_offspring = param_optimizer.assign_fitness_values(
            results_tvo, cost_table, self.auto_param_weights
        )

        if survivors is not None:
            fitted_population = (
                concat([survivors, fitted_offspring], sort=False)
                .sort_values(by="fitness", ascending=False)
                .reset_index(drop=True)
            )
        else:
            fitted_population = fitted_offspring

        fitted_population = complete_missing_population(
            fitted_offspring, population_size - len(fitted_offspring)
        )

        return fitted_population

    def initialize_population(self, inventory):
        """
        creates a population of the form

        population[step_id][population_index][]

        step_id: name of the step
        population_index: index of the pipeline for this population

        """

        # Generate the Initial Populations
        population = {}
        for i, step in enumerate(self.ga_pipeline):
            libraries = []
            step_id = param_optimizer.get_step_id(step)

            if step["type"] in self.ga_steps:
                if step["type"] == "selectorset":
                    libraries = ["selectorset"]
                elif step["type"] == "tvo":
                    libraries = ["optimizers", "classifiers"]
                else:
                    raise Exception(
                        "GA step type {} not supported by AutoML".format(step["type"])
                    )

            self.all_libraries += libraries

            population[step_id] = [deepcopy(step) for _ in range(self.population_size)]

            for library in libraries:
                for pop_index, _ in enumerate(population[step_id]):
                    if library == "selectorset":
                        population[step_id][pop_index]["set"] = (
                            param_optimizer.define_parameters(
                                inventory,
                                sandbox_variable=library,
                                add_unsupervised_selectors=True,
                            )
                        )
                    else:
                        if population[step_id][pop_index].get("optimizers", None):
                            optimizer = population[step_id][pop_index]["optimizers"][0][
                                "name"
                            ]
                        else:
                            optimizer = None

                        population[step_id][pop_index][library] = (
                            param_optimizer.define_parameters(
                                sandbox_variable=library,
                                optimizer=optimizer,
                                inventory=inventory,
                            )
                        )

        if self.param_hardware_target["classifiers_sram"] and "tvo" in self.ga_steps:
            population = classifiers_sram_correction(
                population,
                self.param_hardware_target["classifiers_sram"],
                inventory,
                add_unsupervised_selectors=True,
            )

        return population

    def process_population(
        self,
        ga_pipeline,
        custom_class_map,
        population,
        generation,
        survivors,
        recall=False,
    ):
        (population, results, _, _) = self.run_population_for_each_library(
            ga_pipeline=ga_pipeline,
            custom_class_map=custom_class_map,
            population=population,
            generation=generation,
            recall=recall,
        )

        if not [r for r in results if r]:
            error_list = list(unique([i["error_message"] for i in self.error_log]))
            logger.errorlog(
                {
                    "message": "No populations successfully",
                    "data": generation,
                    "UUID": self.sandbox.uuid,
                    "data": self.error_log,
                    "log_type": "PID",
                    "task_id": self.task_id,
                }
            )

            raise Exception(
                "ERROR detected. No populations successfully created!. \n"
                + "=== List of Error Messages === \n"
                + " \n".join([str(i + 1) + " -" + e for i, e in enumerate(error_list)])
            )

        fitted_population = self.get_population_fitness_score(
            offspring_population=population,
            results_tvo=results,
            generation=generation,
            survivors=survivors,
            population_size=self.population_size,
        )

        # this will be used to performance monitoring in client
        fitted_population["original_iteration"] = generation

        self.fitted_population_log = concat(
            [self.fitted_population_log, deepcopy(fitted_population)]
        ).reset_index(drop=True)

        save_iteration_results(
            self._cache_manager, self.fitted_population_log, self.sandbox
        )

        return fitted_population

    def genetic_iterations(self, fitted_population, inventory):
        if fitted_population is None:
            population = self.initialize_population(inventory)

            fitted_population = self.process_population(
                ga_pipeline=self.ga_pipeline,
                custom_class_map=self.custom_class_map,
                population=population,
                generation=self.last_iteration,
                survivors=None,
                recall=False,
            )
            self.last_iteration += 1

        top = int(len(fitted_population) * self.survivor_rate)

        start_iteration = self.last_iteration

        for generation in range(start_iteration, self.iterations):
            survivors, offspring = create_next_generation(
                population_size=self.population_size,
                mutation_rate=self.mutation_rate,
                recreation_rate=self.recreation_rate,
                all_libraries=self.all_libraries,
                ga_pipeline=self.ga_pipeline,
                validation_method=self.param_validation_method,
                fitted_population=fitted_population,
                top=top,
                auto_param_weights=self.auto_param_weights,
                inventory=inventory,
                fitted_population_log=self.fitted_population_log,
                add_unsupervised_selectors=True,
            )

            offspring_population = create_population(
                offspring,
                self.ga_pipeline,
                inventory,
                hardware_target=self.param_hardware_target,
                recall=False,
            )

            fitted_population = self.process_population(
                ga_pipeline=self.ga_pipeline,
                custom_class_map=self.custom_class_map,
                population=offspring_population,
                generation=generation,
                survivors=survivors,
                recall=False,
            )

            if check_target_scores_to_end_optimization(
                fitted_population,
                self.param_prediction_target,
                self.param_hardware_target,
            ):
                self.requirement_satisfaction = True
                break

            self.last_iteration += 1

        save_final_results(
            self._cache_manager,
            fitted_population,
            "fitted_population_final",
        )

        return fitted_population

    def final_run_with_recall(self, fitted_population):
        backup_last_iteration = self.last_iteration
        self.last_iteration = "RCL"

        recall_pipelines = deepcopy(fitted_population).iloc[
            : self.param_number_of_models_to_return
        ]

        for _, index in enumerate(recall_pipelines.index):
            logger.debug(
                {
                    "message": "Training Final Model: {} with Validation Method Recall".format(
                        index
                    ),
                    "UUID": self.sandbox.uuid,
                    "log_type": "PID",
                    "data": recall_pipelines.loc[index].to_dict(),
                    "task_id": self.task_id,
                }
            )

        population = create_population(
            recall_pipelines,
            self.ga_pipeline,
            inventory=None,
            hardware_target=None,
            recall=True,
        )

        (
            recall_population,
            results_tvo,
            mapped_inputs,
            failed_pipeline_indexes,
        ) = self.run_population_for_each_library(
            self.ga_pipeline,
            self.custom_class_map,
            population,
            generation="RCL",
            recall=True,
        )

        population = separate_tvo_libraries(recall_population)
        cost_table, _ = self.create_cost_table(population, results_tvo, "RCL")

        fitted_population = postprocess_of_genetic_iterations_for_recall(
            fitted_population,
            self.param_number_of_models_to_return,
            cost_table,
            failed_pipeline_indexes,
        )

        # this may not be sorted that is fine
        fitness_summary, results = self.save_results_tvo_knowledgepacks(
            fitted_population, results_tvo
        )

        fitness_summary["original_iteration"] = "99999"

        self.last_iteration = backup_last_iteration

        return fitness_summary, results

    def initialize_genetic_algorithm_pipeline(self, feature_data):
        self.ga_pipeline = [
            step for i, step in enumerate(self.pipeline) if i >= self.split
        ]

        if self.ga_pipeline[0].get("inputs", None):
            self.ga_pipeline[0]["inputs"]["input_data"] = (
                self.ga_pipeline[0]["inputs"]["input_data"] + ".data_0.csv.gz"
            )
        elif self.ga_pipeline[0].get("input_data", None):
            self.ga_pipeline[0]["input_data"] = (
                self.ga_pipeline[0]["input_data"] + ".data_0.csv.gz"
            )
        else:
            raise Exception("Invalid Pipeline, No input data specified!")

        self._validate_feature_data_size(
            self.pipeline[self.split - 1]["outputs"][0], feature_data
        )

        load_persisitent_variables(self._cache_manager, self._temp)

    def _validate_feature_data_size(self, name, feature_data):
        # TODO: reenable this check
        check_validation_of_validation_method(
            feature_data, self.param_validation_method, self.label
        )

        if feature_data.shape[0] > MAX_NUMBER_FEATURES:
            dowsnampled_fv = get_downsampled_classes(
                feature_data, self.pipeline[-1]["label_column"], MAX_NUMBER_FEATURES
            )

            temp_cache = TempCache(pipeline_id=self.pipeline_id)

            temp_cache.write_file(dowsnampled_fv, name + ".data_0")

    def load_cached_automl_data(self):
        # if static part of the pipeline is different than previous run return error
        static_pipeline_validation_for_reset_true(self._cache_manager, self.pipeline)
        automl_params_validation_for_reset_true(
            self._cache_manager, self.param_for_cache
        )

        fitted_population = get_the_results_of_previous_run_from_the_cache(
            self._cache_manager, self.population_size
        )

        self.fitted_population_log = DataFrame(columns=fitted_population.columns)

        self.all_libraries = []
        for step in self.ga_pipeline:
            if step["type"] in self.ga_steps:
                self.all_libraries += param_optimizer.get_libraries(step)

        return fitted_population


def create_population(
    generation_data,
    ga_pipeline,
    inventory,
    hardware_target,
    recall=False,
):
    # group libraries to form offspring for parallel computation
    population = {}

    # set up pipelines that need to be run
    for i, step in enumerate(ga_pipeline):
        if step["type"] == "selectorset":
            population["selectorset"] = [o for o in generation_data["selectorset"]]
        elif step["type"] == "tvo":
            population["classifiers"] = [o for o in generation_data["classifiers"]]
            population["optimizers"] = [o for o in generation_data["optimizers"]]

            if recall:
                population["validation_methods"] = [
                    {"inputs": {}, "name": "Recall"}
                    for _ in generation_data["validation_methods"]
                ]

            else:
                population["validation_methods"] = [
                    o for o in generation_data["validation_methods"]
                ]
            population = combine_tvo_libraries(step, population)
        else:
            population[step["name"]] = [o for o in generation_data[step["name"]]]

    if not recall:
        if hardware_target["classifiers_sram"]:
            population = classifiers_sram_correction(
                population,
                hardware_target["classifiers_sram"],
                inventory,
                add_unsupervised_selectors=True,
            )

    return population


def get_the_results_of_previous_run_from_the_cache(cache_manager, population_size):
    file_name = "fitted_population_final.json"

    if cache_manager._cache_file_exists(file_name):
        # read from cache
        fitted_population = cache_manager.get_file(file_name)
    else:
        raise Exception("ERROR: Results form the previous run don't exist.")

    fitted_population = DataFrame(fitted_population).reset_index(drop=True)

    # in case user increase the population size
    if population_size - len(fitted_population) > 0:
        orj_df_size = len(fitted_population)
        while len(fitted_population) <= population_size:
            fitted_population = concat([fitted_population, fitted_population])

        fitted_population = fitted_population.reset_index(drop=True)
        fitted_population.loc[orj_df_size:, "fitness"] = 0.0

    fitted_population = fitted_population.loc[: population_size - 1]

    return fitted_population


def add_class_map_to_optimizer(population, class_map, step_id):
    for i in range(len(population[step_id])):
        population[step_id][i]["optimizers"][0]["inputs"]["class_map"] = class_map

    return population


def _classifiers_sram_computation(
    optimizer_name, input_dict, feature_input_dict, classifiers_sram
):
    pme_optimizer = [
        "Hierarchical Clustering with Neuron Optimization",
        "RBF with Neuron Allocation Optimization",
        "RBF with Neuron Allocation Limit",
    ]

    if optimizer_name == "Bonsai Tree Optimizer":
        classifiers_sram_cost = 10000

    elif optimizer_name == "Random Forest":
        classifiers_sram_cost = input_dict["max_depth"] * input_dict["n_estimators"] * 4

    elif optimizer_name == "xGBoost":
        # TODO: needs to be defined for xGBoost
        classifiers_sram_cost = input_dict["max_depth"] * input_dict["n_estimators"] * 4

    elif optimizer_name in pme_optimizer:
        features_cost = feature_input_dict.get(
            "feature_number", feature_input_dict.get("number_of_features", inf)
        )
        classifiers_sram_cost = (features_cost + 2) * input_dict["number_of_neurons"]

    elif optimizer_name in ["Neuron Optimization"]:
        features_cost = feature_input_dict.get(
            "feature_number", feature_input_dict.get("number_of_features", inf)
        )
        classifiers_sram_cost = (features_cost + 2) * input_dict["neuron_range"][1]

    else:
        classifiers_sram_cost = 10000

    return classifiers_sram_cost > (classifiers_sram * 2), classifiers_sram_cost


def classifiers_sram_correction(
    population, classifiers_sram, inventory, add_unsupervised_selectors=False
):
    """
    if classifiers_sram is assigned as a hardware target,
    initial population of the classifiers_sram can be limitted
    with 2*self.param_hardware_target['classifiers_sram'] to eliminate extremes
    """

    # TODO: enable this to limit computation to classifier size when selectorset is
    # not selected
    if population.get("selectorset", None) is None:
        return population

    for pop_index in range(len(population["tvo"])):
        optimizer_name = population["tvo"][pop_index]["optimizers"][0]["name"]
        input_dict = population["tvo"][pop_index]["optimizers"][0]["inputs"]

        temp_selector = population["selectorset"][pop_index]["set"]
        feature_input_dict = temp_selector[0]["inputs"]

        update_requirement, _ = _classifiers_sram_computation(
            optimizer_name, input_dict, feature_input_dict, classifiers_sram
        )
        iteration = 0
        min_classifiers_sram_cost = inf

        while update_requirement:
            # update selectorset
            if optimizer_name == "Random Forest":
                temp_selector_feature_input_dict = feature_input_dict
            else:
                temp_selector = param_optimizer.define_parameters(
                    inventory,
                    sandbox_variable="selectorset",
                    add_unsupervised_selectors=add_unsupervised_selectors,
                )
                temp_selector_feature_input_dict = temp_selector[0]["inputs"]

            # update optimizer
            temp_iteration = 0
            while True:
                temp_iteration = temp_iteration + 1
                temp_optimizer = param_optimizer.define_parameters(
                    inventory,
                    sandbox_variable="optimizers",
                    optimizer=optimizer_name,
                )

                # if the same optimizers is not selected in max iteration number, change the optimizer
                if temp_iteration > 25:
                    optimizer_name = temp_optimizer[0]["name"]

                if optimizer_name == temp_optimizer[0]["name"]:
                    break

            temp_optimizer_input_dict = temp_optimizer[0]["inputs"]
            update_requirement, classifiers_sram_cost = _classifiers_sram_computation(
                optimizer_name,
                temp_optimizer_input_dict,
                temp_selector_feature_input_dict,
                classifiers_sram,
            )

            # keep min cost item if it reach max iteration and cannot scaled
            if min_classifiers_sram_cost > classifiers_sram_cost:
                pass

            if update_requirement:
                population["selectorset"][pop_index]["set"] = temp_selector
                population["tvo"][pop_index]["optimizers"] = temp_optimizer

            iteration = iteration + 1
            # max iteration number
            if iteration > 25:
                # use min cost items if target cannot be achived
                population["selectorset"][pop_index]["set"] = temp_selector
                population["tvo"][pop_index]["optimizers"] = temp_optimizer
                break

    return population


def get_driver(step):
    if step["type"] == "selectorset":
        return drivers.feature_selection_driver
    elif step["type"] == "tvo":
        return drivers.tvo_driver
    elif step["type"] in ["transform", "segmenter", "sampler"]:
        transform = Transform.objects.get(name=step["name"])
        if transform.subtype == "Feature Vector":
            return drivers.feature_transform_caller
        return drivers.function_caller
    else:
        raise Exception(
            "Transform type {} not supported by AutoML".format(step["type"])
        )


def separate_tvo_libraries(population):
    if "tvo" in population.keys():
        for sub_library in ["optimizers", "classifiers", "validation_methods"]:
            population[sub_library] = [
                individual[sub_library][0] for individual in population["tvo"]
            ]

    return population


def model_check(results, cost_table, model_stat_list_tuple):
    # drop the populations with 0 neurons, if it exist
    drop_list = []
    for population_index in cost_table.index:
        model = results[population_index]["model_stats"]["models"]
        for key in model.keys():
            if model[key]["metrics"]["validation"].get("NeuronsUsed", None) == 0:
                drop_list.append(population_index)

    if drop_list:
        cost_table = cost_table.drop(drop_list).reset_index(drop=True)
        results = [results[i] for i in range(len(results)) if i not in drop_list]

    return results, cost_table


def complete_missing_population(fitted_population_initial, missing_population_count):
    """
    if there is a pipeline in initial population that failed, complete fitted_population size to desired population size
    as a place holder.
    """
    for i in range(missing_population_count):
        fitted_population_initial.loc[len(fitted_population_initial)] = (
            fitted_population_initial.loc[i]
        )
        fitted_population_initial.loc[len(fitted_population_initial) - 1, "fitness"] = 0
    return fitted_population_initial


def combine_tvo_libraries(step, population):
    population_size = len(population["optimizers"])
    population["tvo"] = [deepcopy(step) for p in range(population_size)]
    for sub_library in ["optimizers", "classifiers", "validation_methods"]:
        for i in range(population_size):
            population["tvo"][i][sub_library] = [deepcopy(population[sub_library][i])]

    return population


def check_target_scores_to_end_optimization(
    fitted_population, prediction_target, hardware_target
):
    for indx in fitted_population.index:
        bool_list = []
        key_temp = []

        for key in prediction_target.keys():
            if prediction_target[key] > 0:
                key_temp.append(key)
                bool_list.append(
                    fitted_population.loc[indx, key] >= prediction_target[key]
                )

        for key in hardware_target.keys():
            if hardware_target[key] > 0:
                key_temp.append(key)
                bool_list.append(
                    fitted_population.loc[indx, key] <= hardware_target[key]
                )

        if (len(bool_list) > 0) and (all(bool_list)):
            return True

    return False


def create_survivors_and_offsprings(
    fitted_population,
    all_libraries,
    mutation_list_orj,
    mutation_list,
    recreation_list,
    top,
    auto_param_weights,
    inventory,
    ga_pipeline,
    param_validation_method,
    temp_fitted_population_log,
    add_unsupervised_selectors=False,
):
    iteration = 0
    offspring = []
    # To make sure, there is at least one item in the offspring
    while not offspring:
        new_generation = param_optimizer.run_ga_functions(
            fitted_population,
            all_libraries,
            mutation_list_orj,
            mutation_list,
            recreation_list,
            top,
            auto_param_weights,
            inventory,
            ga_pipeline,
            param_validation_method,
            add_unsupervised_selectors=add_unsupervised_selectors,
        )

        # just run offspring, NOT survivors
        survivors = deepcopy(
            new_generation.loc[: top - 1, all_libraries].to_dict(orient="records")
        )

        offspring = deepcopy(
            new_generation.loc[top:, all_libraries].to_dict(orient="records")
        )

        # eliminated the offspring which are already in survivors
        offspring = [
            temp for temp in offspring if temp not in temp_fitted_population_log
        ]

        if iteration > 100:
            offspring = [survivors[0]]

        iteration = iteration + 1

    return new_generation, survivors, offspring


def create_mutation_list(population_size, mutation_rate):
    mutation_list_orj = random.sample(
        range(population_size // 2),
        int(mutation_rate * population_size),
    )

    mutation_list = random.sample(
        range(population_size // 2, population_size),
        int(mutation_rate * population_size),
    )

    return mutation_list_orj, mutation_list


def create_recreation_list(population_size, mutation_list, recreation_rate):
    recreation_list = random.sample(
        list(set(range(population_size // 2, population_size)) - set(mutation_list)),
        int(recreation_rate * population_size),
    )

    return recreation_list


def create_next_generation(
    population_size,
    mutation_rate,
    recreation_rate,
    all_libraries,
    ga_pipeline,
    validation_method,
    fitted_population,
    top,
    auto_param_weights,
    inventory,
    fitted_population_log,
    add_unsupervised_selectors=False,
):
    temp_fitted_population_log = fitted_population_log[all_libraries].to_dict(
        orient="records"
    )

    # create mutation list
    mutation_list_orj, mutation_list = create_mutation_list(
        population_size, mutation_rate
    )

    # create recreation list
    recreation_list = create_recreation_list(
        population_size, mutation_list, recreation_rate
    )

    # create survivors and offsprings
    new_generation, survivors, offspring = create_survivors_and_offsprings(
        fitted_population,
        all_libraries,
        mutation_list_orj,
        mutation_list,
        recreation_list,
        top,
        auto_param_weights,
        inventory,
        ga_pipeline,
        validation_method,
        temp_fitted_population_log,
        add_unsupervised_selectors=add_unsupervised_selectors,
    )

    # eliminate duplicated offspring
    temp = []
    [temp.append(indx) for indx in offspring if not (indx in temp)]

    # recreate steps for offspring
    for indx, _ in enumerate(temp):
        for lib in all_libraries:
            new_generation.at[indx + top, lib] = deepcopy(temp[indx][lib])

    # keep survivors in df form with all fitness parameters
    survivors = new_generation.loc[: top - 1]
    offspring = new_generation.loc[top : top + len(temp) - 1]

    return survivors, offspring


def postprocess_of_genetic_iterations_for_recall(
    fitted_population, number_of_models_to_return, cost_table, failed_pipeline_indexes
):
    keep_indexes = [
        x for x in range(number_of_models_to_return) if x not in failed_pipeline_indexes
    ]

    recall_fitted_populations = fitted_population.iloc[keep_indexes].reset_index(
        drop=True
    )

    recall_fitted_populations.loc[:, "summary"] = cost_table["summary"]

    return recall_fitted_populations


def check_validation_of_validation_method(features, validation_method, label_column):
    """
    Checking the possible error of validation algorithm before it run.
    """
    if features is None:
        raise Exception("Error: No feature data was generated!")

    number_of_folds = validation_method["inputs"].get("number_of_folds", 1)
    metadata_name = validation_method["inputs"].get("metadata_name", None)

    if metadata_name:
        if len(features[metadata_name].unique()) < number_of_folds:
            raise Exception(
                "ERROR detected in "
                + validation_method["name"]
                + ". \n"
                + "Number of unique metadata("
                + str(len(features[metadata_name].unique()))
                + ") names is less then desired k-fold ("
                + str(number_of_folds)
                + ").\n"
                + "============================== \n"
                + "=== Possible Solutions  ====== \n"
                + " 1- Add more data with different metadata. \n"
                + " 2- Reduce the number of fold. \n"
                + "============================== \n"
            )

    for label in unique(features[label_column]):
        if sum(features[label_column] == label) < number_of_folds:
            raise Exception(
                "\n ERROR detected in " + validation_method["name"] + "!!! \n"
                " Number of examples(segments) in class - [ "
                + label
                + " ] cannot be less than"
                + " the number of splits(k-fold:"
                + str(number_of_folds)
                + "). \n"
                + "============================== \n"
                + "=== Possible Solutions  ====== \n"
                + " 1- Add more data. \n"
                + " 2- Reduce the segment length. \n"
                + " 3- Reduce the number of fold. \n"
                + "============================== \n"
            )


def get_downsampled_classes(df, label_column, target_size):
    df_g = df.groupby(label_column)
    max_samples_per_class = int(target_size / len(df_g))

    M = []
    for key in df_g.groups.keys():
        samples = (
            max_samples_per_class
            if max_samples_per_class < df_g.get_group(key).shape[0]
            else df_g.get_group(key).shape[0]
        )
        M.append(resample(df_g.get_group(key), replace=False, n_samples=samples))

    return concat(M)


def add_static_feature_selectors(population, static_feature_selectors):
    if "selectorset" in population.keys():
        for pop_index, _ in enumerate(population["selectorset"]):
            if len(population["selectorset"][pop_index]["set"]) <= 1:
                population["selectorset"][pop_index]["set"] = (
                    static_feature_selectors
                    + population["selectorset"][pop_index]["set"]
                )

    return population


def save_iteration_results(cache_manager, fitted_population, sandbox):
    file_name = "fitted_population_log"

    col = [
        "optimizers",
        "classifiers",
        "pipeline",
        "original_iteration",
        "iteration",
        "fitness",
        "flash",
        "sram",
        "latency",
        "accuracy",
        "accuracy_std",
        "f1_score",
        "f1_score_std",
        "positive_predictive_rate",
        "positive_predictive_rate_std",
        "precision",
        "precision_std",
        "sensitivity",
        "sensitivity_std",
        "specificity",
        "specificity_std",
        "TrainingMetrics",
        "classifiers_sram",
        "classifiers_sram_std",
        "features",
        "features_std",
    ]

    # save to cache
    cache_manager.save_result_data(
        file_name,
        str(sandbox.uuid),
        data=fitted_population[col]
        .sort_values(by="fitness", ascending=False)
        .to_dict(orient="records"),
    )


def save_final_results(cache_manager, fitted_population, file_name):
    # save to cache
    cache_manager.write_file(fitted_population.to_dict(), file_name)


def save_static_pipeline_for_validation(cache_manager, pipeline):
    temp = {}
    for i in pipeline:
        if isinstance(i["name"], list):
            temp[",".join(i["name"])] = i
        else:
            temp[i["name"]] = i

        if i["name"] == "generator_set":
            break

    # save to cache
    cache_manager.write_file(temp, "static_pipeline_for_validation")


def static_pipeline_validation_for_reset_true(cache_manager, pipeline):
    file_name = "static_pipeline_for_validation.json"

    if cache_manager._cache_file_exists(file_name):
        # read from cache
        cached_pipeline = cache_manager.get_file(file_name)

        current_pipeline = {}
        for i in pipeline:
            current_pipeline[i["name"]] = i
            if i["name"] == "generator_set":
                break

        if cached_pipeline != current_pipeline:
            if len(cached_pipeline.keys()) == len(current_pipeline.keys()):
                for k in cached_pipeline.keys():
                    if cached_pipeline[k] != current_pipeline[k]:
                        raise ValidationError(
                            "ERROR: in 'reset:False'. \n"
                            + "Cached pipeline setting for '"
                            + cached_pipeline[k]["name"]
                            + "' is different than the current setting. \n"
                            + "Suggestions: \n"
                            + "1 - Set the same parameters for current and cached "
                            + cached_pipeline[k]["name"]
                            + " algorithm \n"
                            + "2 - Set 'reset' option to True \n"
                        )
                        break

            elif len(cached_pipeline.keys()) > len(current_pipeline.keys()):
                missing_algorithms = str(
                    list(cached_pipeline.keys() - current_pipeline.keys())
                )
                raise ValidationError(
                    "ERROR: in 'reset:False'. \n"
                    + "Current pipeline does not have '"
                    + missing_algorithms
                    + "' algorithms. \n"
                    + "Suggestions: \n"
                    + "1 - Add "
                    + missing_algorithms
                    + " algorithms to your pipeline. \n"
                    + "2 - Set 'reset' option to True \n"
                )

            else:
                missing_algorithms = str(
                    list(current_pipeline.keys() - cached_pipeline.keys())
                )

                raise ValidationError(
                    "ERROR: in 'reset:False'. \n"
                    + "Cached pipeline does not have '"
                    + missing_algorithms
                    + "' algorithms. \n"
                    + "Suggestions: \n"
                    + "1 - Remove "
                    + missing_algorithms
                    + " algorithms from your current pipeline. \n"
                    + "2 - Set 'reset' option to True \n"
                )

    else:
        raise ValidationError("ERROR: Results form the previous run does not exist.")


def save_automl_params(cache_manager, param_for_cache):
    # save to cache
    cache_manager.write_file(param_for_cache, "automl_param_for_cache")


def automl_params_validation_for_reset_true(cache_manager, param_for_cache):
    keys = [
        "search_steps",
        "allow_unknown",
        "auto_group",
        "balance_data",
        "combine_labels",
        "input_columns",
        "outlier_filter",
        "generatorset",
        "validation_method",
        "feature_cascade",
        "fitness",
        "prediction_target",
        "hardware_target",
    ]

    file_name = "automl_param_for_cache.json"

    if cache_manager._cache_file_exists(file_name):
        # read from cache
        cached_automl_params = cache_manager.get_file(file_name)

        for k in keys:
            if k in param_for_cache.keys() and k in cached_automl_params.keys():
                if param_for_cache[k] != cached_automl_params[k]:
                    raise ValidationError(
                        "ERROR: in 'reset:False'. \n"
                        + "Current '"
                        + k
                        + "' parameter in AutoML is different than cached one. \n"
                        + "Current '"
                        + k
                        + "' parameter:  "
                        + str(param_for_cache[k])
                        + " \n"
                        + "Cached '"
                        + k
                        + "' parameter:  "
                        + str(cached_automl_params[k])
                        + " \n"
                        + "Suggestions: \n"
                        + "1 - Set the same parameters for current and cached Automl pipeline \n"
                        + "2 - Set 'reset' option to True \n"
                    )

            elif (k in param_for_cache.keys()) and (
                k not in cached_automl_params.keys()
            ):
                raise ValidationError(
                    "ERROR: in 'reset:False'. \n"
                    + "The cached AutoML setting does not have '"
                    + k
                    + "' parameter. \n"
                    + "Suggestions: \n"
                    + "1 - Remove '"
                    + k
                    + "' parameter from current AutoML pipeline. \n"
                    + "2 - Set 'reset' option to True \n"
                )

            elif (k not in param_for_cache.keys()) and (
                k in cached_automl_params.keys()
            ):
                raise ValidationError(
                    "ERROR: in 'reset:False'. \n"
                    + "The current AutoML setting does not have '"
                    + k
                    + "' parameter. \n"
                    + "Suggestions: \n"
                    + "1 - Add '"
                    + k
                    + "' parameter to current AutoML pipeline. \n"
                    + "2 - Set 'reset' option to True \n"
                )

    else:
        raise ValidationError(
            "ERROR: Automl parameters form the previous run does not exist.\n"
            + "Suggestions: Set 'reset' option to True \n"
        )
