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

import numpy as np
import pytest
from pandas import DataFrame

from library.classifiers.boosted_tree_ensemble import (
    BoostedTreeEnsemble,
    compute_cost,
    get_tree_ensemble,
)

pytestmark = pytest.mark.django_db  # All tests use db


@pytest.fixture
def model_parameters():
    return [
        {
            "Tree": 0,
            "Node": 0,
            "ID": "0-0",
            "Feature": "f0",
            "Split": 129.0,
            "Yes": "0-1",
            "No": "0-2",
            "Missing": "0-1",
            "Gain": 60.8421059,
            "Cover": 17.0,
        },
        {
            "Tree": 0,
            "Node": 1,
            "ID": "0-1",
            "Feature": "Leaf",
            "Split": None,
            "Yes": None,
            "No": None,
            "Missing": None,
            "Gain": 0.178947374,
            "Cover": 8.5,
        },
        {
            "Tree": 0,
            "Node": 2,
            "ID": "0-2",
            "Feature": "Leaf",
            "Split": None,
            "Yes": None,
            "No": None,
            "Missing": None,
            "Gain": -0.178947374,
            "Cover": 8.5,
        },
        {
            "Tree": 1,
            "Node": 0,
            "ID": "1-0",
            "Feature": "f0",
            "Split": 129.0,
            "Yes": "1-1",
            "No": "1-2",
            "Missing": "1-1",
            "Gain": 50.8301773,
            "Cover": 16.8646278,
        },
        {
            "Tree": 1,
            "Node": 1,
            "ID": "1-1",
            "Feature": "Leaf",
            "Split": None,
            "Yes": None,
            "No": None,
            "Missing": None,
            "Gain": 0.164148405,
            "Cover": 8.43231487,
        },
        {
            "Tree": 1,
            "Node": 2,
            "ID": "1-2",
            "Feature": "Leaf",
            "Split": None,
            "Yes": None,
            "No": None,
            "Missing": None,
            "Gain": -0.164148435,
            "Cover": 8.43231392,
        },
        {
            "Tree": 2,
            "Node": 0,
            "ID": "2-0",
            "Feature": "f0",
            "Split": 129.0,
            "Yes": "2-1",
            "No": "2-2",
            "Missing": "2-1",
            "Gain": 43.037117,
            "Cover": 16.509367,
        },
        {
            "Tree": 2,
            "Node": 1,
            "ID": "2-1",
            "Feature": "Leaf",
            "Split": None,
            "Yes": None,
            "No": None,
            "Missing": None,
            "Gain": 0.152484536,
            "Cover": 8.25468349,
        },
        {
            "Tree": 2,
            "Node": 2,
            "ID": "2-2",
            "Feature": "Leaf",
            "Split": None,
            "Yes": None,
            "No": None,
            "Missing": None,
            "Gain": -0.152484536,
            "Cover": 8.25468349,
        },
    ]


@pytest.fixture
def feature_vectors():
    return DataFrame(
        [
            [254, 253, 252, 1],
            [254, 252, 253, 1],
            [254, 252, 252, 1],
            [254, 251, 253, 1],
            [254, 251, 254, 1],
            [253, 250, 253, 1],
            [253, 252, 254, 1],
            [252, 252, 253, 1],
            [254, 252, 253, 1],
            [253, 252, 254, 1],
            [252, 250, 254, 1],
            [254, 250, 254, 1],
            [252, 250, 253, 1],
            [250, 252, 254, 1],
            [249, 253, 253, 1],
            [248, 254, 253, 1],
            [250, 254, 254, 1],
            [8, 2, 0, 2],
            [10, 1, 0, 2],
            [8, 0, 1, 2],
            [7, 1, 1, 2],
            [5, 0, 2, 2],
            [5, 0, 2, 2],
            [6, 2, 3, 2],
            [5, 2, 2, 2],
            [5, 2, 2, 2],
            [3, 2, 2, 2],
            [3, 2, 1, 2],
            [2, 1, 1, 2],
            [3, 2, 1, 2],
            [2, 4, 1, 2],
            [2, 3, 0, 2],
            [0, 2, 0, 2],
            [0, 1, 1, 2],
            [254, 253, 252, 1],
            [254, 252, 253, 1],
            [254, 252, 252, 1],
            [254, 251, 253, 1],
            [254, 251, 254, 1],
            [253, 250, 253, 1],
            [253, 252, 254, 1],
            [252, 252, 253, 1],
            [254, 252, 253, 1],
            [253, 252, 254, 1],
            [252, 250, 254, 1],
            [254, 250, 254, 1],
            [252, 250, 253, 1],
            [250, 252, 254, 1],
            [249, 253, 253, 1],
            [248, 254, 253, 1],
            [250, 254, 254, 1],
            [8, 2, 0, 2],
            [10, 1, 0, 2],
            [8, 0, 1, 2],
            [7, 1, 1, 2],
            [5, 0, 2, 2],
            [5, 0, 2, 2],
            [6, 2, 3, 2],
            [5, 2, 2, 2],
            [5, 2, 2, 2],
            [3, 2, 2, 2],
            [3, 2, 1, 2],
            [2, 1, 1, 2],
            [3, 2, 1, 2],
            [2, 4, 1, 2],
            [2, 3, 0, 2],
            [0, 2, 0, 2],
            [0, 1, 1, 2],
        ]
    )


class TestBoostedTreeEnseble:
    def test_recongize_vector(self, model_parameters, feature_vectors):

        classifier = BoostedTreeEnsemble()
        classifier.load_model(model_parameters)

        classifier.preprocess(3, feature_vectors)

        results = classifier.recognize_vectors(package(feature_vectors.values))

        assert results["accuracy"] == 100.0

    def test_get_tree_ensemble(self, model_parameters):

        BoostedTreeEnsemble()

        models = get_tree_ensemble(model_parameters)

        assert len(models) == 3

        expected_node_list = np.array([1, 0, 0])
        expected_leafs = np.array([0.17894737, -0.17894737])
        expect_features = np.array([0, 0, 1])
        expecthed_thresholds = np.array([129, 0, 0])

        assert np.array_equal(models[0].node_list, expected_node_list)
        assert round(models[0].leafs[0], 4) == round(expected_leafs[0], 4)
        assert round(models[0].leafs[1], 4) == round(expected_leafs[1], 4)
        assert np.array_equal(models[0].features, expect_features)
        assert np.array_equal(models[0].threshold, expecthed_thresholds)

    @pytest.mark.django_db
    def test_compute_cost(self, model_parameters, loaddata):
        loaddata("test_classifier_costs")
        expected_flash_size = 499
        cost = compute_cost(model_parameters)
        assert type(cost) == type(dict())
        assert cost["flash"] == expected_flash_size


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
