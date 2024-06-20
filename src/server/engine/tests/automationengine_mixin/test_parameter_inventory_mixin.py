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

import pytest
from datamanager.models import KnowledgePack, Project, Query, Sandbox, Segmenter
from engine.automationengine_mixin.parameter_inventory_mixin import (
    ParameterInventoryMixin,
    remove_binary_optimizers_and_dependens,
    update_inventory_to_allow_unknown,
    update_training_algorithm,
    update_training_algorithm_parameters,
)
from library.models import PipelineSeed
from pandas import DataFrame

pytestmark = pytest.mark.django_db


@pytest.fixture
def project():
    project = Project.objects.create(name="test", team_id=1)
    return project


@pytest.fixture
def pipeline_seed():
    pipeline = [
        {
            "inputs": {"group_columns": [], "input_data": "temp.raw"},
            "set": [
                {
                    "inputs": {"smoothing_factor": 4, "sample_rate": 1, "columns": []},
                    "function_name": "Median",
                },
            ],
            "type": "generatorset",
            "name": "generator_set",
            "outputs": ["temp.featuregenerator", "temp.features.featuregenerator"],
        }
    ]
    seed = PipelineSeed.objects.create(name="Test", description="", pipeline=pipeline)

    return seed


@pytest.fixture
def sandbox(project):
    pipeline = [
        {
            "group_columns": ["Subject", "Label"],
            "data_columns": ["AccelX", "AccelY"],
            "label_column": "Label",
            "inputs": {"input_data": "temp.raw"},
            "type": "featurefile",
        }
    ]
    sandbox = Sandbox.objects.create(name="test", project=project, pipeline=pipeline)
    return sandbox


@pytest.fixture
def query(project):
    # create segmetner
    segmenter = Segmenter.objects.create(project=project, name="Manual", custom=True)

    query = Query.objects.create(
        name="test",
        project=project,
        segmenter=segmenter,
        columns=json.dumps(["Column1", "Column2"]),
        metadata_columns=json.dumps(["Gesture"]),
        label_column="Label",
        metadata_filter="",
    )

    return query


@pytest.fixture
def run_pipeline(sandbox, pipeline_seed, query):
    rp = ParameterInventoryMixin()
    rp.random_seed = 0
    rp.segmenter_id = None
    rp.param_validation_method = "Recall"
    rp.param_sample_by_metadatalist = None
    rp.sample_by_metadata_list = None
    rp.label = "Label"
    rp.param_combine_labels = None
    rp.param_outlier_filter = None
    rp.ga_steps = ["selectorset", "tvo"]
    rp.sandbox = sandbox
    rp.pipeline = []
    rp.group_columns = ["Subject", "Label"]
    rp.data_columns = ["AccelX", "AccelY"]
    rp.param_generator_set = None
    rp.param_input_columns = None
    rp.query = query
    rp.param_feature_cascade = None

    return rp


@pytest.fixture
def child_knowledgepack(sandbox):
    child_knowledgepack = KnowledgePack.objects.create(
        sandbox=sandbox,
        project=sandbox.project,
        name="c",
        uuid="11111111-1111-1111-1111-111111111111",
        knowledgepack_description=None,
    )
    return child_knowledgepack


@pytest.fixture
def knowledgepack(sandbox, child_knowledgepack):
    knowledgepack_description = {
        "Parent": {"uuid": "00000000-0000-0000-0000-000000000000"},
        "Model_3": {"uuid": child_knowledgepack.uuid},
    }

    knowledgepack = KnowledgePack.objects.create(
        sandbox=sandbox,
        project=sandbox.project,
        name="p",
        uuid="00000000-0000-0000-0000-000000000000",
        knowledgepack_description=knowledgepack_description,
    )
    knowledgepack.save()
    return knowledgepack


class TestRunPipelinePopulation:
    # in:
    def setup_class(self):

        self.seed = [
            {
                "name": "generator_set",
                "type": "generatorset",
                "set": [
                    {
                        "function_name": "Standard Deviation",
                        "inputs": {"columns": ["GyroscopeZ"]},
                    },
                    {
                        "function_name": "Standard Deviation",
                        "inputs": {"columns": ["GyroscopeY"]},
                    },
                    {
                        "function_name": "Variance",
                        "inputs": {"columns": ["AccelerometerX"]},
                    },
                ],
                "inputs": {"group_columns": [], "input_data": ""},
                "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
            },
            {
                "set": [
                    {
                        "inputs": {"feature_number": 2},
                        "function_name": "Information Gain",
                    }
                ],
                "name": "selectorset",
                "type": "selectorset",
                "inputs": {
                    "input_data": "temp.generator_set0",
                    "label_column": "",
                    "cost_function": "sum",
                    "feature_table": "temp.features.generator_set0",
                    "remove_columns": [],
                    "number_of_features": 30,
                    "passthrough_columns": [],
                },
                "outputs": ["temp.featureselector", "temp.features.featureselector"],
                "refinement": {},
            },
        ]

        self.df_ga_inventory = DataFrame()

        self.df_ga_inventory["function_name"] = [
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
        self.df_ga_inventory["pipeline_key"] = [
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
        self.df_ga_inventory["variable_name"] = [
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
            "None",
            "None",
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
        self.df_ga_inventory["variable_type"] = [
            "int",
            "int",
            "int",
            "float",
            "int",
            "int",
            "int",
            "int",
            "int",
            "Str",
            "Str",
            "None",
            "None",
            "Str",
            "int",
            "int",
            "int",
            "Str",
            "Str",
            "Str",
            "int",
            "int",
            "int",
            "int",
            "int",
            "int",
        ]
        self.df_ga_inventory["variable_values"] = [
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
            ["None"],
            ["None"],
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
        self.df_ga_inventory["classifiers_optimizers_group"] = [
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
        self.df_ga_inventory["binary_classifiers"] = [
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
        self.df_ga_inventory["allow_unknown"] = [
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

    # out:

    def test_update_inventory_to_allow_unknown(self):
        inventory = update_inventory_to_allow_unknown(self.df_ga_inventory)
        assert False not in inventory.allow_unknown.tolist()

    def test_remove_binary_optimizers_and_dependens(self):
        inventory = remove_binary_optimizers_and_dependens(self.df_ga_inventory)
        assert True not in inventory.binary_classifiers.tolist()

    def test_update_training_algorithms(self, run_pipeline, project):
        results = update_training_algorithm(self.df_ga_inventory, ["Random Forest"])
        assert results[
            results.pipeline_key == "optimizers"
        ].function_name.unique().tolist() == ["Random Forest"]

        results = update_training_algorithm(
            self.df_ga_inventory,
            ["Random Forest", "Hierarchical Clustering with Neuron Optimization"],
        )
        assert results[
            results.pipeline_key == "optimizers"
        ].function_name.unique().tolist() == [
            "Hierarchical Clustering with Neuron Optimization",
            "Random Forest",
        ]

        results = update_training_algorithm(
            self.df_ga_inventory, ["Random Forest", "xGBoost"]
        )
        assert results[
            results.pipeline_key == "optimizers"
        ].function_name.unique().tolist() == ["Random Forest", "xGBoost"]

    def test_update_training_algorithm_parameters(self):
        def check_results(set_training_algorithm):
            # this function remove all optimizers from the inventory except "Random Forest" and "xGBoost"
            new_inventory = update_training_algorithm(
                self.df_ga_inventory, list(set_training_algorithm.keys())
            )

            results = update_training_algorithm_parameters(
                new_inventory, set_training_algorithm
            )

            for algorithm in set_training_algorithm.keys():
                for key in set_training_algorithm[algorithm].keys():
                    assert (
                        set_training_algorithm[algorithm][key]
                        == results[
                            (results.function_name == algorithm)
                            & (results.variable_name == key)
                        ].variable_values.values[0]
                    )

        set_training_algorithm = {
            "Random Forest": {"max_depth": [1, 3, 5], "n_estimators": [5, 10, 15]},
            "xGBoost": {"max_depth": [1, 2, 3], "n_estimators": [5, 10, 15]},
        }

        check_results(set_training_algorithm)

        # onyl defined algorithms will be changed
        set_training_algorithm = {
            "Random Forest": {"max_depth": list(range(1, 6, 2))},
            "Hierarchical Clustering with Neuron Optimization": {
                "aif_method": ["max", "robust"],
                "number_of_neurons": ["10", "25", "50", "75"],
                "centroid_calculation": ["robust"],
                "cluster_method": ["kmeans"],
            },
        }

        check_results(set_training_algorithm)
