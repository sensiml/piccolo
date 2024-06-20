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
import os
import sys
from copy import deepcopy

import pytest
from datamanager.models import Project, Sandbox
from engine.automationengine_mixin.genetic_iteration_mixin import (
    _classifiers_sram_computation,
    add_class_map_to_optimizer,
    add_static_feature_selectors,
    automl_params_validation_for_reset_true,
    check_target_scores_to_end_optimization,
    create_next_generation,
    create_population,
    get_the_results_of_previous_run_from_the_cache,
    save_automl_params,
    save_final_results,
    save_iteration_results,
    save_static_pipeline_for_validation,
    static_pipeline_validation_for_reset_true,
)
from engine.base.cache_manager import CacheManager
from pandas import DataFrame

pytestmark = pytest.mark.django_db

sys.path.append("../../../server")
data_path = os.path.abspath(os.path.dirname(__file__)) + "/"


class TestRunGeneticIteration:
    def setup_class(self):
        pass

    def test_check_target_scores_to_end_optimization(self):
        prediction_target = {
            "accuracy": 70,
            "positive_predictive_rate": 0.0,
            "sensitivity": 0.0,
        }
        hardware_target = {"latency": 0, "classifiers_sram": 500}

        fitted_population = DataFrame(
            columns=[
                "accuracy",
                "positive_predictive_rate",
                "sensitivity",
                "latency",
                "classifiers_sram",
            ]
        )

        fitted_population.loc[0] = [96, 90, 93, 111, 400]
        results = check_target_scores_to_end_optimization(
            fitted_population, prediction_target, hardware_target
        )
        assert results == True

        fitted_population.loc[0] = [65, 90, 93, 111, 400]
        results = check_target_scores_to_end_optimization(
            fitted_population, prediction_target, hardware_target
        )
        assert results == False

        fitted_population.loc[0] = [75, 90, 93, 111, 600]
        results = check_target_scores_to_end_optimization(
            fitted_population, prediction_target, hardware_target
        )
        assert results == False

        fitted_population.loc[0] = [60, 90, 93, 111, 600]
        results = check_target_scores_to_end_optimization(
            fitted_population, prediction_target, hardware_target
        )
        assert results == False

        prediction_target = {
            "accuracy": 75,
            "positive_predictive_rate": 70,
            "sensitivity": 80,
        }
        hardware_target = {"latency": 200, "classifiers_sram": 500}

        fitted_population = DataFrame(
            columns=[
                "accuracy",
                "positive_predictive_rate",
                "sensitivity",
                "latency",
                "classifiers_sram",
            ]
        )

        fitted_population.loc[0] = [96, 90, 93, 111, 400]
        results = check_target_scores_to_end_optimization(
            fitted_population, prediction_target, hardware_target
        )
        assert results == True

        fitted_population.loc[0] = [96, 60, 93, 111, 400]
        results = check_target_scores_to_end_optimization(
            fitted_population, prediction_target, hardware_target
        )
        assert results == False

        fitted_population.loc[0] = [96, 90, 93, 250, 400]
        results = check_target_scores_to_end_optimization(
            fitted_population, prediction_target, hardware_target
        )
        assert results == False

    def test__classifiers_sram_correction(self):
        classifiers_sram = 500
        optimizer_name = "RBF with Neuron Allocation Optimization"
        input_dict = {"number_of_iterations": 50, "number_of_neurons": 50}
        feature_input_dict = {"number_of_features": 4}
        results, sram = _classifiers_sram_computation(
            optimizer_name, input_dict, feature_input_dict, classifiers_sram
        )
        assert (results == False) and (sram == 300)

        input_dict = {"number_of_iterations": 50, "number_of_neurons": 100}
        feature_input_dict = {"number_of_features": 10}
        results, sram = _classifiers_sram_computation(
            optimizer_name, input_dict, feature_input_dict, classifiers_sram
        )
        assert (results == True) and (sram == 1200)

        optimizer_name = "Random Forest"
        input_dict = {"max_depth": 4, "n_estimators": 20}
        feature_input_dict = {"number_of_features": 4}
        results, sram = _classifiers_sram_computation(
            optimizer_name, input_dict, feature_input_dict, classifiers_sram
        )

        assert (results == False) and (sram == 320)

        optimizer_name = "Random Forest"
        input_dict = {"max_depth": 4, "n_estimators": 80}
        feature_input_dict = {"number_of_features": 4}
        results, sram = _classifiers_sram_computation(
            optimizer_name, input_dict, feature_input_dict, classifiers_sram
        )

        assert (results == True) and (sram == 1280)

    def test_add_class_map_to_optimizer(self):
        class_map = {"Rollover": 1, "combined_label_1": 2}
        population = {}
        step_id = "tvo"

        population[step_id] = [
            {
                "name": "tvo",
                "optimizers": [
                    {
                        "inputs": {"number_of_iterations": 50, "number_of_neurons": 10},
                        "name": "RBF with Neuron Allocation Optimization",
                    }
                ],
            }
        ]

        results = add_class_map_to_optimizer(population, class_map, step_id)

        assert results[step_id][0]["optimizers"][0]["inputs"]["class_map"] == class_map

    def test_create_next_generation(self):

        with open(data_path + "/data/data_create_survivors_offspring.txt") as json_file:
            read_data = json.load(json_file)

        top = read_data["top"]
        population_size = read_data["population_size"]
        mutation_rate = read_data["mutation_rate"]
        recreation_rate = read_data["recreation_rate"]
        all_libraries = read_data["all_libraries"]
        ga_pipeline = read_data["ga_pipeline"]
        param_validation_method = read_data["param_validation_method"]
        fitted_population = DataFrame(read_data["fitted_population"])
        auto_param_weights = DataFrame(read_data["auto_param_weights"])
        inventory = DataFrame(read_data["inventory"])
        fitted_population_backlog = DataFrame(read_data["fitted_population_backlog"])

        survivors, offspring = create_next_generation(
            population_size,
            mutation_rate,
            recreation_rate,
            all_libraries,
            ga_pipeline,
            param_validation_method,
            fitted_population,
            top,
            auto_param_weights,
            inventory,
            fitted_population_backlog,
        )

        assert len(survivors) == 3
        assert len(offspring) <= 3

    def test_create_population(self):

        with open(data_path + "/data/data_create_population.txt") as json_file:
            read_data = json.load(json_file)

        generation_data = DataFrame(read_data["generation_data"])
        ga_pipeline = read_data["ga_pipeline"]
        param_hardware_target = read_data["param_hardware_target"]
        inventory = DataFrame(read_data["inventory"])

        population = create_population(
            generation_data,
            ga_pipeline,
            inventory,
            param_hardware_target,
            recall=False,
        )

        assert len(population.keys()) == 6

        for key in population.keys():
            assert key in [
                "selectorset",
                "Min Max Scale",
                "classifiers",
                "optimizers",
                "validation_methods",
                "tvo",
            ]
            assert len(population[key]) == 3

        population = create_population(
            generation_data,
            ga_pipeline,
            inventory,
            param_hardware_target,
            recall=True,
        )

        assert len(population.keys()) == 6

        for key in population.keys():
            assert key in [
                "selectorset",
                "Min Max Scale",
                "classifiers",
                "optimizers",
                "validation_methods",
                "tvo",
            ]
            assert len(population[key]) == 3

    def test_add_static_feature_selectors(self):

        step_id = "selectorset"
        population = {}

        population[step_id] = [
            {
                "set": [
                    {
                        "inputs": {"feature_number": 12},
                        "function_name": "t-Test Feature Selector",
                    },
                ],
                "outputs": [
                    "temp.featureselector.0.0",
                    "temp.features.featureselector.0.0",
                ],
            },
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.65},
                    },
                    {
                        "inputs": {"number_of_features": 8},
                        "function_name": "Tree-based Selection",
                    },
                ],
                "outputs": [
                    "temp.featureselector.0.1",
                    "temp.features.featureselector.0.1",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"number_of_features": 8},
                        "function_name": "Tree-based Selection",
                    },
                ],
                "outputs": [
                    "temp.featureselector.0.2",
                    "temp.features.featureselector.0.2",
                ],
            },
        ]

        static_feature_selectors = []
        results_population = add_static_feature_selectors(
            deepcopy(population), static_feature_selectors
        )
        assert results_population == population

        static_feature_selectors = [
            {"function_name": "Variance Threshold", "inputs": {"threshold": 0.1}},
            {"function_name": "Correlation Threshold", "inputs": {"threshold": 0.65}},
        ]

        results_population = add_static_feature_selectors(
            deepcopy(population), static_feature_selectors
        )

        for i, v in enumerate(results_population[step_id]):
            assert len(v["set"]) == 3
            assert v["set"][0] == static_feature_selectors[0]
            assert v["set"][1] == static_feature_selectors[1]
            assert v["set"][2] == population[step_id][i]["set"][-1]

        step_id = "tvo"
        population = {}

        population[step_id] = []
        results_population = add_static_feature_selectors(deepcopy(population), [])

        assert population == results_population

    def test_save_iteration_results(self):

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

        df_test = DataFrame(columns=col + ["test1", "test2"])

        for c in df_test.columns:
            df_test[c] = 10 * ["A"]

        project = Project.objects.create(name="Test", team_id=1)
        sandbox = Sandbox.objects.create(name="test", project=project)
        cache_obj = CacheManager(sandbox, None)

        save_iteration_results(cache_obj, df_test, sandbox)

        # Read from cache
        results, _ = cache_obj.get_result_from_cache(
            "fitted_population_log.{}".format(sandbox.uuid)
        )

        assert len(results) == 10
        assert sorted(list(results[0].keys())) == sorted(col)

    def test_save_final_results(self):

        df_test = DataFrame(columns=["test1", "test2"])

        for c in df_test.columns:
            df_test[c] = 10 * ["A"]

        project = Project.objects.create(name="Test", team_id=1)
        sandbox = Sandbox.objects.create(name="test", project=project)
        cache_obj = CacheManager(sandbox, None)
        file_name = "test_file"

        save_final_results(cache_obj, df_test, file_name)
        assert cache_obj._cache_file_exists(file_name + ".json")

        fitted_population = cache_obj.get_file(file_name + ".json")
        results = DataFrame(fitted_population).reset_index(drop=True)
        assert len(results) == 10
        assert results.columns.tolist() == df_test.columns.tolist()

    def test_get_the_results_of_previous_run_from_the_cache(self):

        df_test = DataFrame(columns=["test1", "test2"])

        for c in df_test.columns:
            df_test[c] = 10 * ["A"]

        project = Project.objects.create(name="Test", team_id=1)
        sandbox = Sandbox.objects.create(name="test", project=project)
        cache_manager = CacheManager(sandbox, None)

        file_name = "fitted_population_final"
        save_final_results(cache_manager, df_test, file_name)

        population_size = 10

        results = get_the_results_of_previous_run_from_the_cache(
            cache_manager, population_size
        )

        assert len(results) == 10
        assert results.columns.tolist() == df_test.columns.tolist()

        file_name = "fitted_population_final"
        save_final_results(cache_manager, df_test, file_name)

        population_size = 15

        results = get_the_results_of_previous_run_from_the_cache(
            cache_manager, population_size
        )

        assert len(results) == 15
        assert results.columns.tolist() == df_test.columns.tolist() + ["fitness"]

        file_name = "fitted_population_final"
        save_final_results(cache_manager, df_test, file_name)

        population_size = 50

        results = get_the_results_of_previous_run_from_the_cache(
            cache_manager, population_size
        )

        assert len(results) == 50
        assert results.columns.tolist() == df_test.columns.tolist() + ["fitness"]

        file_name = "fitted_population_final"
        save_final_results(cache_manager, df_test, file_name)

        population_size = 5

        results = get_the_results_of_previous_run_from_the_cache(
            cache_manager, population_size
        )

        assert len(results) == 5
        assert results.columns.tolist() == df_test.columns.tolist()

    def test_save_static_pipeline_for_validation(self):

        pipeline = [
            {"name": "Q1"},
            {"name": "Filter Extreme Values", "type": "transform"},
            {
                "name": "Windowing",
                "type": "segmenter",
            },
            {
                "name": "Strip",
                "type": "transform",
            },
            {
                "name": "Vertical AutoScale Segment",
                "type": "transform",
            },
            {
                "name": "generator_set",
                "type": "generatorset",
            },
            {
                "name": "selectorset",
                "type": "selectorset",
            },
            {
                "type": "transform",
                "name": "Min Max Scale",
            },
            {
                "name": "tvo",
                "type": "tvo",
            },
        ]

        project = Project.objects.create(name="Test", team_id=1)
        sandbox = Sandbox.objects.create(name="test", project=project)
        cache_manager = CacheManager(sandbox, None)

        save_static_pipeline_for_validation(cache_manager, pipeline)

        file_name = "static_pipeline_for_validation.json"

        assert cache_manager._cache_file_exists(file_name)
        # read from cache
        cached_pipeline = cache_manager.get_file(file_name)

        assert list(cached_pipeline.keys()) == [
            "Q1",
            "Filter Extreme Values",
            "Windowing",
            "Strip",
            "Vertical AutoScale Segment",
            "generator_set",
        ]

    def test_static_pipeline_validation_for_reset_true(self):
        project = Project.objects.create(name="Test", team_id=1)
        sandbox = Sandbox.objects.create(name="test", project=project)
        cache_manager = CacheManager(sandbox, None)

        pipeline = [
            {"name": "Q1"},
            {"name": "Filter Extreme Values", "type": "transform"},
            {
                "name": "Windowing",
                "type": "segmenter",
            },
            {
                "name": "Strip",
                "type": "transform",
            },
            {
                "name": "Vertical AutoScale Segment",
                "type": "transform",
            },
            {
                "name": "generator_set",
                "type": "generatorset",
            },
            {
                "name": "selectorset",
                "type": "selectorset",
            },
            {
                "type": "transform",
                "name": "Min Max Scale",
            },
            {
                "name": "tvo",
                "type": "tvo",
            },
        ]

        save_static_pipeline_for_validation(cache_manager, pipeline)
        result = static_pipeline_validation_for_reset_true(cache_manager, pipeline)
        assert result is None

    def test_save_automl_params(self):
        project = Project.objects.create(name="Test", team_id=1)
        sandbox = Sandbox.objects.create(name="test", project=project)
        cache_manager = CacheManager(sandbox, None)

        param_for_cache = {
            "search_steps": ["selectorset", "tvo"],
            "population_size": 6,
            "iterations": 1,
            "mutation_rate": 0.1,
            "recreation_rate": 0.1,
            "survivor_rate": 0.5,
            "number_of_models_to_return": 6,
            "run_parallel": True,
            "allow_unknown": False,
            "auto_group": False,
            "balance_data": True,
            "combine_labels": None,
            "input_columns": None,
            "outlier_filter": False,
            "generatorset": False,
            "validation_method": "Recall",
            "feature_cascade": {"num_cascades": 2, "slide": False},
            "reset": False,
            "single_model": True,
            "prediction_target": {
                "accuracy": 1.0,
                "positive_predictive_rate": 0.0,
                "sensitivity": 0.0,
            },
            "hardware_target": {"latency": 0, "classifiers_sram": 5},
        }

        save_automl_params(cache_manager, param_for_cache)
        file_name = "automl_param_for_cache.json"
        assert cache_manager._cache_file_exists(file_name)
        # read from cache
        cached_pipeline = cache_manager.get_file(file_name)
        assert list(cached_pipeline.keys()) == list(param_for_cache.keys())

    def test_automl_params_validation_for_reset_true(self):

        project = Project.objects.create(name="Test", team_id=1)
        sandbox = Sandbox.objects.create(name="test", project=project)
        cache_manager = CacheManager(sandbox, None)

        param_for_cache = {
            "search_steps": ["selectorset", "tvo"],
            "population_size": 6,
            "iterations": 1,
            "mutation_rate": 0.1,
            "recreation_rate": 0.1,
            "survivor_rate": 0.5,
            "number_of_models_to_return": 6,
            "run_parallel": True,
            "allow_unknown": False,
            "auto_group": False,
            "balance_data": True,
            "combine_labels": None,
            "input_columns": None,
            "outlier_filter": False,
            "generatorset": False,
            "validation_method": "Recall",
            "feature_cascade": {"num_cascades": 2, "slide": False},
            "reset": False,
            "single_model": True,
            "prediction_target": {
                "accuracy": 1.0,
                "positive_predictive_rate": 0.0,
                "sensitivity": 0.0,
            },
            "hardware_target": {"latency": 0, "classifiers_sram": 5},
        }

        save_automl_params(cache_manager, param_for_cache)

        results = automl_params_validation_for_reset_true(
            cache_manager, param_for_cache
        )
