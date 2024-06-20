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
from library.classifiers.decision_tree_ensemble import DecisionTreeEnsemble

pytestmark = pytest.mark.django_db  # All tests use db


@pytest.fixture
def model_parameters():
    return [
        {
            "children_left": [1, 2, 0, 0, 5, 0, 0],
            "children_right": [4, 3, 0, 0, 6, 0, 0],
            "threshold": [131, 80, 0, 0, 111, 0, 0],
            "feature": [1, 0, 0, 0, 5, 0, 0],
            "classes": [0.0, 1.0, 2.0, 3.0, 4.0],
            "feature_importances": [
                0.41365294219144516,
                0.578845643730371,
                0.0,
                0.0,
                0.0,
                0.007501414078183798,
            ],
        },
        {
            "children_left": [1, 2, 0, 0, 0],
            "children_right": [4, 3, 0, 0, 0],
            "threshold": [145, 72, 0, 0, 0],
            "feature": [1, 5, 0, 0, 0],
            "classes": [0.0, 1.0, 2.0, 3.0, 4.0],
            "feature_importances": [
                0.0,
                0.5139197730730113,
                0.0,
                0.0,
                0.0,
                0.4860802269269888,
            ],
        },
        {
            "children_left": [1, 2, 0, 0, 5, 0, 0],
            "children_right": [4, 3, 0, 0, 6, 0, 0],
            "threshold": [63, 100, 0, 0, 73, 0, 0],
            "feature": [3, 1, 0, 0, 5, 0, 0],
            "classes": [0.0, 1.0, 2.0, 3.0, 4.0],
            "feature_importances": [
                0.0,
                0.23488517742769494,
                0.0,
                0.4196303125251301,
                0.0,
                0.345484510047175,
            ],
        },
    ]


class TestDecisionTreeEnsemble:
    @pytest.mark.django_db
    def test_compute_cost(self, model_parameters, loaddata):
        loaddata("test_classifier_costs")
        classifier = DecisionTreeEnsemble()
        expected_costs = {"flash": 512, "stack": 160}
        for tree in model_parameters:
            expected_costs["flash"] += len(tree["feature"])
            expected_costs["flash"] += len(tree["children_right"]) * 2  # size of int16
            expected_costs["flash"] += len(tree["children_left"]) * 2  # size of int16
            expected_costs["flash"] += len(tree["threshold"])

        cost = classifier.compute_cost(model_parameters)
        assert type(cost) == type(dict())
        for key in expected_costs.keys():
            assert cost[key] == expected_costs[key]
