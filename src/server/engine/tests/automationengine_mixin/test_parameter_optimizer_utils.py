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

import pytest
from numpy import sort
from pandas import DataFrame

import engine.automationengine_mixin.parameter_optimizer_utils as po
from library.models import Transform

pytestmark = pytest.mark.django_db  # All tests use db


@pytest.fixture
def validation_method():
    from library.core_functions.mg_contracts import k_fold_strat_contracts

    validation_method = Transform.objects.create(
        name="Stratified K-Fold Cross-Validation",
        input_contract=k_fold_strat_contracts["input_contract"],
        output_contract=k_fold_strat_contracts["output_contract"],
    )

    return validation_method


@pytest.fixture
def df_ga_inventory():

    df_ga_inventory = DataFrame()

    df_ga_inventory["function_name"] = [
        "Min Max Scale",
        "Min Max Scale",
        "Information Gain",
        "Information Gain",
        "t-Test Feature Selector",
        "Univariate Selection",
        "Tree-based Selection",
        "PME",
        "PME",
        "PME",
        "PME",
        "Decision Tree Ensemble",
        "Boosted Tree Ensemble",
        "Hierarchical Clustering with Neuron Optimization",
        "Hierarchical Clustering with Neuron Optimization",
        "Hierarchical Clustering with Neuron Optimization",
        "Hierarchical Clustering with Neuron Optimization",
        "Hierarchical Clustering with Neuron Optimization",
        "Hierarchical Clustering with Neuron Optimization",
        "Hierarchical Clustering with Neuron Optimization",
        "RBF with Neuron Allocation Optimization",
        "RBF with Neuron Allocation Optimization",
        "Random Forest",
        "Random Forest",
        "xGBoost",
        "xGBoost",
    ]
    df_ga_inventory["pipeline_key"] = [
        "transform",
        "transform",
        "selectorset",
        "selectorset",
        "selectorset",
        "selectorset",
        "selectorset",
        "classifiers",
        "classifiers",
        "classifiers",
        "classifiers",
        "classifiers",
        "classifiers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
        "optimizers",
    ]
    df_ga_inventory["variable_name"] = [
        "min_bound",
        "max_bound",
        "feature_number",
        "target_sensor_weight",
        "feature_number",
        "number_of_features",
        "number_of_features",
        "max_aif",
        "min_aif",
        "distance_mode",
        "classification_mode",
        None,
        None,
        "aif_method",
        "min_number_of_dominant_vector",
        "max_number_of_weak_vector",
        "number_of_neurons",
        "linkage_method",
        "centroid_calculation",
        "cluster_method",
        "number_of_iterations",
        "number_of_neurons",
        "max_depth",
        "n_estimators",
        "max_depth",
        "n_estimators",
    ]
    df_ga_inventory["variable_type"] = [
        "int",
        "int",
        "int",
        "float",
        "int",
        "int",
        "int",
        "int",
        "int",
        "str",
        "str",
        None,
        None,
        "str",
        "int",
        "int",
        "int",
        "str",
        "str",
        "str",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
    ]
    df_ga_inventory["variable_values"] = [
        ["0"],
        ["255"],
        ["1", "2", "4", "8", "12", "16"],
        ["0.9"],
        ["1", "2", "4", "8", "12", "16"],
        ["2", "4", "8", "16", "32"],
        ["2", "4", "8", "16", "32"],
        ["100", "150", "200", "250"],
        ["20", "40", "80"],
        ["L1", "Lsup"],
        ["KNN"],
        None,
        None,
        ["max", "robust", "median"],
        ["3", "5", "7", "10", "15", "20"],
        ["2", "4", "8"],
        ["10", "25", "50", "75"],
        ["average", "complete"],
        ["robust", "median"],
        ["kmeans"],
        ["50"],
        ["10", "25", "50", "75"],
        ["3", "4", "5", "6", "7"],
        ["10", "20", "30", "50", "60", "70"],
        ["3", "4", "5", "6", "7"],
        ["10", "20", "30", "50", "60", "70"],
    ]
    df_ga_inventory["classifiers_optimizers_group"] = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        2,
        3,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        2,
        3,
        3,
    ]
    df_ga_inventory["binary_classifiers"] = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
        False,
        False,
        False,
        False,
    ]
    df_ga_inventory["allow_unknown"] = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
        False,
        False,
        False,
        False,
    ]

    return df_ga_inventory


def test_define_auto_params_weight_parm():
    pass


def test_define_prm():
    pass


def test_run_ga_functions():
    """Tests cross-over, mutation, and recreation"""


def test_assign_fitness_values():
    pass


def test_get_inventory():

    pass

    # TODO: The databse needs to be set up to run this

    # inventory = po.get_inventory()
    # assert inventory is not None


def test_get_libraries():
    tvo_step = {"name": "tvo", "type": "tvo", "extra": {1, 2, 3}}
    tvo_libraries = po.get_libraries(tvo_step)
    assert set(tvo_libraries) == set(
        ["classifiers", "optimizers", "validation_methods"]
    )

    selector_step = {"name": "selector", "type": "selectorset", "extra": {1, 2, 3}}
    selector_libraries = po.get_libraries(selector_step)
    assert set(selector_libraries) == set(["selectorset"])


def test_create_genetic_step():
    step = {
        "name": "tvo",
        "type": "tvo",
        "extra": {1, 2, 3},
        "input_data": "temp.input",
        "feature_table": "temp.selectorfeatures",
        "outputs": ["temp.tvodata", "temp.tvofeatures"],
    }

    # Without modified inputs
    modified_step = po.create_genetic_step(step, 0, False, None, None)
    expected = {
        "name": "tvo",
        "extra": set([1, 2, 3]),
        "type": "tvo",
        "outputs": ["temp.tvodata.0.False", "temp.tvofeatures.0.False"],
        "input_data": "temp.input",
        "feature_table": "temp.selectorfeatures",
    }

    assert expected == modified_step

    # With modified inputs
    modified_step = po.create_genetic_step(step, 0, True, None, None)
    expected = {
        "name": "tvo",
        "extra": set([1, 2, 3]),
        "type": "tvo",
        "outputs": ["temp.tvodata.0.True", "temp.tvofeatures.0.True"],
        "input_data": "temp.input",
        "feature_table": "temp.selectorfeatures",
    }

    assert expected == modified_step

    # With different index
    modified_step = po.create_genetic_step(step, 5, True, None, None)
    expected = {
        "name": "tvo",
        "extra": set([1, 2, 3]),
        "type": "tvo",
        "outputs": ["temp.tvodata.5.True", "temp.tvofeatures.5.True"],
        "input_data": "temp.input",
        "feature_table": "temp.selectorfeatures",
    }

    assert expected == modified_step

    # With different placement
    step = {
        "name": "tvo",
        "type": "tvo",
        "extra": {1, 2, 3},
        "inputs": {
            "input_data": "temp.input",
            "feature_table": "temp.selectorfeatures",
        },
        "outputs": ["temp.tvodata", "temp.tvofeatures"],
    }
    modified_step = po.create_genetic_step(step, 5, True, None, None)
    expected = {
        "name": "tvo",
        "extra": set([1, 2, 3]),
        "type": "tvo",
        "outputs": ["temp.tvodata.5.True", "temp.tvofeatures.5.True"],
        "inputs": {
            "input_data": "temp.input",
            "feature_table": "temp.selectorfeatures",
        },
    }

    assert expected == modified_step

    map_inputs = True
    previous_outputs = [
        [136, "temp.scale.0.0.csv.gz"],
        [136, "temp.scale.0.1.csv.gz"],
        [136, "temp.scale.0.2.csv.gz"],
    ]

    step = {
        "name": "tvo",
        "type": "tvo",
        "extra": {1, 2, 3},
        "input_data": "temp.input",
        "feature_table": "temp.selectorfeatures",
        "outputs": ["temp.tvodata", "temp.tvofeatures"],
    }

    # Without modified inputs
    modified_step = po.create_genetic_step(step, 0, False, map_inputs, previous_outputs)

    expected = {
        "name": "tvo",
        "type": "tvo",
        "extra": {1, 2, 3},
        "input_data": "temp.scale.0.0.csv.gz",
        "feature_table": "temp.selectorfeatures.0.0",
        "outputs": ["temp.tvodata.0.False", "temp.tvofeatures.0.False"],
    }

    assert expected == modified_step

    modified_step = po.create_genetic_step(step, 0, True, map_inputs, previous_outputs)

    expected = {
        "name": "tvo",
        "type": "tvo",
        "extra": {1, 2, 3},
        "input_data": "temp.scale.0.1.csv.gz",
        "feature_table": "temp.selectorfeatures.0.1",
        "outputs": ["temp.tvodata.0.True", "temp.tvofeatures.0.True"],
    }

    assert expected == modified_step

    modified_step = po.create_genetic_step(step, 5, True, map_inputs, previous_outputs)

    expected = {
        "name": "tvo",
        "type": "tvo",
        "extra": {1, 2, 3},
        "input_data": "temp.scale.0.1.csv.gz",
        "feature_table": "temp.selectorfeatures.0.1",
        "outputs": ["temp.tvodata.5.True", "temp.tvofeatures.5.True"],
    }

    assert expected == modified_step

    # With different placement
    step = {
        "name": "tvo",
        "type": "tvo",
        "extra": {1, 2, 3},
        "inputs": {
            "input_data": "temp.input",
            "feature_table": "temp.selectorfeatures",
        },
        "outputs": ["temp.tvodata", "temp.tvofeatures"],
    }

    modified_step = po.create_genetic_step(step, 5, True, map_inputs, previous_outputs)

    expected = {
        "name": "tvo",
        "type": "tvo",
        "extra": {1, 2, 3},
        "inputs": {
            "input_data": "temp.scale.0.1.csv.gz",
            "feature_table": "temp.selectorfeatures.0.1",
        },
        "outputs": ["temp.tvodata.5.True", "temp.tvofeatures.5.True"],
    }

    assert expected == modified_step


def test_create_classifiers_index_list():
    temp_list = [
        {"name": "Decision Tree Ensemble"},
        {"name": "Decision Tree Ensemble"},
        {"name": "Decision Tree Ensemble"},
        {"name": "PME"},
        {"name": "PME"},
        {"name": "PME"},
    ]

    test_df = DataFrame(columns=["classifiers"])
    test_df["classifiers"] = temp_list
    result = po.create_classifiers_index_list(test_df, test_df.index)

    assert ([0, 1, 2] == result[0]) & ([3, 4, 5] == result[1])


def test_create_cross_over_list():
    result = list(sort(po.create_cross_over_list([[0, 1], [2, 3]], [0])))
    assert result == [0, 1]

    result = list(sort(po.create_cross_over_list([[0, 1], [2, 3]], [1])))
    assert result == [0, 1]

    result = list(sort(po.create_cross_over_list([[0, 1], [2, 3]], [2])))
    assert result == [2, 3]

    result = list(sort(po.create_cross_over_list([[0, 1], [2, 3]], [3])))
    assert result == [2, 3]

    result = list(sort(po.create_cross_over_list([[1], [2, 3]], [1])))
    assert result == [1, 1]

    result = list(sort(po.create_cross_over_list([[0], [2, 3]], [0])))
    assert result == [0, 0]

    result = list(sort(po.create_cross_over_list([[0, 1], [2]], [2])))
    assert result == [2, 2]

    result = list(sort(po.create_cross_over_list([[0, 1], [3]], [3])))
    assert result == [3, 3]


def test_cross_over():
    # Creating a synthetic data set
    fitness_values = DataFrame(
        [], columns=["fitness", "lib1", "lib2", "classifiers"]
    )  # 'lib1',
    fitness_values.loc[1] = [10, 1, "a", {"name": "Decision Tree Ensemble"}]
    fitness_values.loc[2] = [11, 11, "b", {"name": "Decision Tree Ensemble"}]
    fitness_values.loc[3] = [20, 2, "c", {"name": "PME"}]
    fitness_values.loc[4] = [22, 22, "d", {"name": "PME"}]
    fitness_values.loc[5] = [0, 0, "e", {"name": "xxxxx"}]

    # Define the parameter of cross over
    mutation_list = []
    recreation_list = []
    top_trh = 4
    lib_list = ["lib1", "lib2", "classifiers"]  # ['lib1', 'lib2']
    auto_params_weight_parm = DataFrame([])
    # One of these results can be returned with given parameters above
    expected_results = [
        [0, 1, "a", {"name": "Decision Tree Ensemble"}],
        [0, 1, "b", {"name": "Decision Tree Ensemble"}],
        [0, 11, "a", {"name": "Decision Tree Ensemble"}],
        [0, 11, "b", {"name": "Decision Tree Ensemble"}],
        [0, 2, "c", {"name": "PME"}],
        [0, 2, "d", {"name": "PME"}],
        [0, 22, "c", {"name": "PME"}],
        [0, 22, "d", {"name": "PME"}],
    ]

    fitness_values = po.cross_over(
        fitness_values,
        auto_params_weight_parm,
        lib_list,
        mutation_list,
        recreation_list,
        top_trh,
    )

    # Cross over results will be placed in 5th row
    return_result = fitness_values.loc[5].tolist()

    assert (
        return_result in expected_results
    ), "Result of cross_over function is not in the expected results list."


def test_tvo_recreation(df_ga_inventory):
    # this unit test checks the dictionary keys for tvo, classification and optimizers
    recreation_list = [5]
    dict_temp = {
        "tvo": {
            recreation_list[0]: {
                "classifiers": [],
                "optimizers": [],
                "type": "tvo",
                "validation_methods": [],
            }
        }
    }
    new_generation = DataFrame(dict_temp)
    lib_list = ["optimizers", "classifiers", "validation_methods"]
    search_pipeline = [{"type": "tvo"}]
    validation_method = "Stratified Shuffle Split"

    return_result = po.recreation(
        new_generation,
        df_ga_inventory,
        recreation_list,
        lib_list,
        search_pipeline,
        validation_method,
    )

    return_result = return_result.to_dict()

    # tvo keys
    tvo_keys_expected = sort(
        ["type", "validation_methods", "classifiers", "optimizers"]
    )

    tvo_keys_return = sort(list(return_result["tvo"][recreation_list[0]].keys()))

    assert all(tvo_keys_return == tvo_keys_expected)

    # classification list
    return_classifiers = return_result["tvo"][recreation_list[0]]["classifiers"][0][
        "name"
    ]
    assert return_classifiers in [
        "PME",
        "Decision Tree Ensemble",
        "Boosted Tree Ensemble",
    ]

    # optimizers keys
    return_optimizers_keys = sort(
        list(return_result["tvo"][recreation_list[0]]["optimizers"][0]["inputs"].keys())
    )
    if (
        return_result["tvo"][recreation_list[0]]["optimizers"][0]["name"]
        == "Hierarchical Clustering with Neuron Optimization"
    ):
        expected_optimizers_keys = sort(
            [
                "min_number_of_dominant_vector",
                "centroid_calculation",
                "max_number_of_weak_vector",
                "cluster_method",
                "number_of_neurons",
                "linkage_method",
                "aif_method",
            ]
        )

    elif return_result["tvo"][recreation_list[0]]["optimizers"][0]["name"] in [
        "xGBoost",
        "Random Forest",
    ]:
        expected_optimizers_keys = ["max_depth", "n_estimators"]

    else:
        expected_optimizers_keys = sort(["number_of_neurons", "number_of_iterations"])

    assert all(return_optimizers_keys == expected_optimizers_keys)


def test_mutation(df_ga_inventory):
    # Apply mutation to Row#1 based on Row#0
    mutation_list_orj = [0]
    mutation_list = [1]
    nan = None

    dict_temp = {
        "feature_min_max_parameters": {0: nan, 1: nan},
        "input_data": {0: nan, 1: nan},
        "passthrough_columns": {0: nan, 1: nan},
        "classifiers": {
            0: {
                "inputs": {
                    "classification_mode": "RBF",
                    "distance_mode": "L1",
                    u"max_aif": 50,
                    "min_aif": 10,
                },
                "name": "PME",
            },
            1: {
                "inputs": {
                    "classification_mode": "xxx",
                    "distance_mode": "xxx",
                    u"max_aif": 0,
                    "min_aif": 0,
                },
                "name": "PME",
            },
        },
        "optimizers": {
            0: {
                "inputs": {"number_of_iterations": 60, "number_of_neurons": 20},
                "name": "RBF with Neuron Allocation Optimization",
            },
            1: {
                "inputs": {
                    "aif_method": "min",
                    "centroid_calculation": "mean",
                    "cluster_method": "DHC",
                    "linkage_method": "average",
                    "max_number_of_weak_vector": 1,
                    "min_number_of_dominant_vector": 3,
                    "number_of_neurons": 109,
                },
                "name": "Hierarchical Clustering with Neuron Optimization",
            },
        },
    }

    new_generation = DataFrame(dict_temp)

    (
        return_variables_name_list,
        return_algorithm,
    ) = po.variables_name_list_for_mutation("classifiers", new_generation, 0)
    assert all(
        [
            i in ["distance_mode", "max_aif", "min_aif", "classification_mode"]
            for i in return_variables_name_list
        ]
    )
    assert return_algorithm == "PME"

    (
        return_variables_name_list,
        return_algorithm,
    ) = po.variables_name_list_for_mutation("optimizers", new_generation, 0)
    assert all(
        [
            i in ["number_of_iterations", "number_of_neurons"]
            for i in return_variables_name_list
        ]
    )
    assert return_algorithm == "RBF with Neuron Allocation Optimization"

    lib_list = ["classifiers", "optimizers"]
    return_result = po.mutation(
        new_generation,
        df_ga_inventory,
        mutation_list_orj,
        mutation_list,
        lib_list,
    )
    return_result = return_result.to_dict()

    # check classifiers
    assert return_result["classifiers"][1]["inputs"]["classification_mode"] in [
        "RBF",
        "KNN",
    ]
    assert return_result["classifiers"][1]["inputs"]["distance_mode"] in [
        "L1",
        "Lsup",
    ]
    assert return_result["classifiers"][1]["inputs"]["max_aif"] in range(25, 101)
    assert return_result["classifiers"][1]["inputs"]["min_aif"] in range(5, 21)

    # check optimizers
    assert return_result["optimizers"][1]["inputs"]["number_of_iterations"] in range(
        30, 121
    )
    assert return_result["optimizers"][1]["inputs"]["number_of_neurons"] in range(
        10, 41
    )


def test_read_classifiers_algorithms(df_ga_inventory):
    optimizer = "RBF with Neuron Allocation Optimization"
    classifier = po.read_classifiers_algorithms(optimizer, df_ga_inventory)
    expected_result = ["PME"]
    assert classifier == expected_result

    optimizer = "Random Forest"
    classifier = po.read_classifiers_algorithms(optimizer, df_ga_inventory)
    expected_result = ["Decision Tree Ensemble"]
    assert classifier == expected_result

    optimizer = "Boosted Tree Ensemble"
    classifier = po.read_classifiers_algorithms(optimizer, df_ga_inventory)
    expected_result = ["Boosted Tree Ensemble"]
    assert classifier == expected_result


def test_read_validation_algorithms(validation_method):

    validation_method = "Recall"

    result = po.read_validation_algorithms(validation_method)

    expected_result = [{"inputs": {}, "name": u"Recall"}]

    assert result == expected_result

    validation_method = {
        "name": "Stratified K-Fold Cross-Validation",
        "inputs": {
            "number_of_folds": 5,
            "test_size": 0.0,
            "shuffle": False,
            "red": "blue",
        },
    }

    result = po.read_validation_algorithms(validation_method)

    expected_result = [
        {
            "name": "Stratified K-Fold Cross-Validation",
            "inputs": {
                "number_of_folds": 5,
                "test_size": 0.0,
                "shuffle": False,
            },
        }
    ]

    assert result == expected_result
