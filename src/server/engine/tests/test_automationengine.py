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

from engine.automationengine import (
    update_auto_param_weights_for_prediction_values,
    update_auto_param_weights_for_hardware_values,
    update_target_dictionary,
    validate_training_algorithms,
)


def test_update_auto_param_weights_for_prediction_values():

    prediction_target = {
        "accuracy": 100,
        "f1_score": 0,
        "sensitivity": 0,
        "positive_predictive_rate": 0,
    }

    fitness = {
        "accuracy": 0,
        "f1_score": 0,
        "sensitivity": 0,
        "positive_predictive_rate": 0,
    }

    results = update_auto_param_weights_for_prediction_values(
        fitness, prediction_target
    )

    assert results == {
        "accuracy": 1.0,
        "f1_score": 0.01,
        "sensitivity": 0.01,
        "positive_predictive_rate": 0.01,
    }


def test_update_auto_param_weights_for_hardware_values():
    hardware_target = {"features": 0, "classifiers_sram": 1000}
    fitness = {"features": 0, "classifiers_sram": 0}
    results = update_auto_param_weights_for_hardware_values(fitness, hardware_target)
    assert results == {"features": 0.1, "classifiers_sram": 1.0}


def test_complete_target_items():
    template = {
        "accuracy": 0,
        "f1_score": 0,
        "sensitivity": 0,
        "positive_predictive_rate": 0,
    }

    new_items = {"accuracy": 95, "f1_score": 90}

    results = update_target_dictionary(new_items, template)
    expected_results = {
        "accuracy": 95,
        "f1_score": 90,
        "sensitivity": 0,
        "positive_predictive_rate": 0,
    }

    assert results == expected_results

    template = {"classifiers_sram": 0, "latency": 0}
    new_items = {"classifiers_sram": 95}

    results = update_target_dictionary(new_items, template)
    expected_results = {"classifiers_sram": 95, "latency": 0}

    assert results == expected_results


def test_validate_training_algorithms():

    training_algorithms = None
    assert validate_training_algorithms(training_algorithms) == None

    training_algorithms = [
        "Hierarchical Clustering with Neuron Optimization",
        "RBF with Neuron Allocation Optimization",
        "Random Forest",
        "xGBoost",
        "Train Fully Connected Neural Network",
    ]

    expected_results = {
        "Hierarchical Clustering with Neuron Optimization": {},
        "RBF with Neuron Allocation Optimization": {},
        "Random Forest": {},
        "xGBoost": {},
        "Train Fully Connected Neural Network": {},
    }

    assert validate_training_algorithms(training_algorithms) == expected_results

    training_algorithms = {
        "Hierarchical Clustering with Neuron Optimization": {},
        "RBF with Neuron Allocation Optimization": {},
        "Random Forest": {},
        "xGBoost": {},
        "Train Fully Connected Neural Network": {},
    }

    assert validate_training_algorithms(training_algorithms) == training_algorithms

    training_algorithms = {
        "Hierarchical Clustering with Neuron Optimization": {},
        "RBF with Neuron Allocation Optimization": {},
        "Random Forest": {},
        "xGBoost": {},
        "2Train Fully Connected Neural Network": {},
    }
    raised_validation = False

    try:
        validate_training_algorithms(training_algorithms) == training_algorithms
    except:
        raised_validation = True

    assert raised_validation
