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

import os

import pandas as pd
import pytest
from numpy import array
from pandas import DataFrame

from library.classifiers.bonsai import Bonsai

pytestmark = pytest.mark.django_db  # All tests use db


@pytest.fixture
def model_parameters():
    return {
        "T": [1.0, 1.0, 1.0, 1.0, 1.0],
        "V": [
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            -1.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
        ],
        "W": [
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
            3.0,
        ],
        "Z": [
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            -100.0,
        ],
        "Mean": [0.0, 0.0, 0.0, 0.0],
        "sigma": 1.0,
        "Variance": [1.0, 1.0, 1.0, 1.0],
        "num_nodes": 3,
        "tree_depth": 1,
        "num_classes": 4,
        "num_features": 4,
        "projection_dimension": 5,
    }


@pytest.fixture
def model_parameters_iris():
    return {
        "V": [
            0.190486,
            0.000000,
            1.329567,
            -1.927121,
            1.253055,
            -0.161887,
            0.000000,
            1.920066,
            0.079787,
            0.535121,
            -0.146567,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -0.440725,
            0.000000,
            0.000000,
            -1.321985,
            0.000000,
            0.000000,
            0.000000,
            -2.618819,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -0.152481,
            0.000000,
            0.000000,
            0.000000,
            -1.045787,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -0.261976,
            0.000000,
            0.707860,
            0.156855,
            0.000000,
            0.000000,
            0.179092,
            0.417326,
            0.014047,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -1.443624,
            1.688396,
            0.000000,
            0.320981,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -0.192983,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -0.136105,
            -1.667041,
            0.000000,
            0.000000,
            0.000000,
            -2.198193,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
        ],
        "W": [
            -0.309815,
            -2.806459,
            0.000000,
            -0.871105,
            0.000000,
            0.000000,
            -0.072441,
            0.000000,
            0.000000,
            1.383573,
            0.000000,
            -1.021098,
            0.000000,
            0.000000,
            1.341398,
            0.146119,
            0.000000,
            -0.496814,
            0.295442,
            0.000000,
            0.000000,
            2.677322,
            0.000000,
            0.000000,
            0.000000,
            0.159704,
            0.000000,
            0.000000,
            0.089932,
            -0.633272,
            0.000000,
            0.000000,
            0.000000,
            -1.157816,
            0.000000,
            0.000001,
            0.000000,
            -0.451730,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            1.645497,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.587277,
            0.000000,
            0.284226,
            3.098047,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -0.150802,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -0.899149,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            1.751028,
            0.000000,
            1.972134,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -0.822448,
            0.000000,
            1.040152,
        ],
        "Z": [
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            4.321795,
            -1.661260,
            0.000000,
            0.000000,
            0.000000,
            -3.816179,
            0.000000,
            0.000000,
            2.960832,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -1.234765,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            2.361992,
            0.000000,
            0.000000,
        ],
        "T": [
            -0.3752323091030121,
            -1.0119010210037231,
            -0.8354557752609253,
            -1.876120686531067,
            0.0,
            0.0,
            0.0,
            -0.16529729962348938,
            0.0,
            -0.9702313542366028,
        ],
        "Mean": array([58.93333333, 38.03333333, 0.0]),
        "Variance": array([8.44432748, 17.85774031, 1.0]),
        "projection_dimension": 10,
        "tree_depth": 1,
        "sigma": 1.0,
        "num_nodes": 3,
        "num_classes": 3,
        "num_features": 3,
    }


@pytest.fixture
def feature_vectors():
    return DataFrame([[1, 1, 1, 0, 2], [2, 2, 2, 2, 3]])


@pytest.fixture
def feature_vectors_iris():
    train_set = pd.read_csv(os.path.join("engine", "tests", "data", "Iris_train.csv"))

    train_set["label"] += 1

    test_set = pd.read_csv(os.path.join("engine", "tests", "data", "Iris_test.csv"))
    test_set["label"] += 1

    return pd.concat([train_set, test_set], ignore_index=True)


class TestBonsai:
    @pytest.mark.skip()
    def test_recongize_vector(self, model_parameters, feature_vectors):

        classifier = Bonsai()

        classifier.load_model(model_parameters)

        classifier.preprocess(3, feature_vectors)

        results = classifier.recognize_vectors(package(feature_vectors.values))

        assert results["accuracy"] == 100.0

    def test_recongize_vector_iris(self, model_parameters_iris, feature_vectors_iris):

        classifier = Bonsai()

        classifier.load_model(model_parameters_iris)

        classifier.preprocess(3, feature_vectors_iris)

        results = classifier.recognize_vectors(package(feature_vectors_iris.values))

        assert results["accuracy"] >= 94.4

    @pytest.mark.django_db
    def test_compute_cost(self, model_parameters_iris, loaddata):
        loaddata("test_classifier_costs")
        classifier = Bonsai()

        classifier.load_model(model_parameters_iris)
        num_nodes = model_parameters_iris["num_nodes"]
        num_classes = model_parameters_iris["num_classes"]
        projection_dimension = model_parameters_iris["projection_dimension"]
        total_flash_size = 100 + (5 * 4 * num_classes) + (4 * num_nodes)
        int(model_parameters_iris["Mean"].shape[0])
        int(model_parameters_iris["Variance"].shape[0])

        total_flash_size += 4 * len(model_parameters_iris["V"])
        total_flash_size += 4 * len(model_parameters_iris["W"])
        total_flash_size += 4 * len(model_parameters_iris["Z"])
        total_flash_size += 4 * len(model_parameters_iris["T"])
        total_flash_size += 4 * int(model_parameters_iris["Mean"].shape[0])
        total_flash_size += 4 * int(model_parameters_iris["Variance"].shape[0])

        expected_costs = {
            "flash": total_flash_size,
            "sram": (3 * 4 * num_classes)
            + (4 * projection_dimension)
            + (4 * num_nodes),
            "stack": 384,
        }

        computed_costs = classifier.compute_cost(model_parameters_iris)

        for key in expected_costs.keys():

            assert computed_costs[key] == expected_costs[key]


def package(data):
    vector_list = []
    for index, _ in enumerate(data):
        item_ints = [i for i in data[index][:-1]]
        pkg_dict = {
            "Category": int((data[index][-1])),
            "CategoryVector": [],
            "DistanceVector": [],
            "Vector": list(item_ints),
        }
        vector_list.append(pkg_dict)

    return vector_list


"""
conversion scripts for model parameters to formatted text
V = np.array(s['V']).reshape(3,3,10)
W = np.array(s['W']).reshape(3,3,10)
Z = np.array(s['Z']).reshape(10,3)
def convert_matrix(Z):
    for i in Z:
        if len(i.shape) > 1:
            for j in i:
                print(', '.join(['{:1.6f}'.format(x) for x in j]),end=',\n')
        else:
            print(', '.join(['{:1.6f}'.format(x) for x in i]),end=',\n')
"""
