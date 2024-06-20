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
from library.classifiers.linear_regression import (
    LinearRegression,
    get_linear_regression_model,
)
from pandas import DataFrame

pytestmark = pytest.mark.django_db  # All tests use db


@pytest.fixture
def model_parameters():
    return {"num_coefficients": 2, "coefficients": [1, -1], "intercept": 0}


@pytest.fixture
def feature_vectors():
    return DataFrame(
        [
            [254, 253, 1],
            [254, 252, 1],
            [254, 252, 1],
            [254, 251, 1],
        ]
    )


class TestLinearRegression:
    def test_recongize_vector(self, model_parameters, feature_vectors):
        model = LinearRegression()
        model.load_model(model_parameters)

        model.preprocess(3, feature_vectors)

        results = model.recognize_vectors(
            package({"estimator_type": "regression"}, feature_vectors.values)
        )

        expected_results = {
            "y_true": [1.0, 1.0, 1.0, 1.0],
            "y_pred": [1, 2, 2, 3],
            "mean_squared_error": {"average": 1.5},
            "mean_absolute_error": {"average": 1.0},
            "median_absolute_error": {"average": 1.0},
        }

        assert results == expected_results

        print(results)

    def test_get_linear_regression_model(self, model_parameters):
        LinearRegression()

        model = get_linear_regression_model(model_parameters)

        assert model.coefficients[0] == 1.0
        assert model.coefficients[1] == -1.0
        assert model.num_coefficients == 2

    @pytest.mark.django_db
    def test_compute_cost(self, model_parameters):
        model = LinearRegression()
        expected_costs = {"flash": 100, "sram": 64, "stack": 32}

        cost = model.compute_cost(model_parameters)

        assert cost == expected_costs


def package(config, data):
    vector_list = []
    for index, _ in enumerate(data):
        item_ints = [i for i in data[index][:-1]]

        if config.get("estimator_type", "classification") == "regression":
            category = data[index][-1]
        else:
            category = int((data[index][-1]))
        pkg_dict = {
            "Category": category,
            "CategoryVector": [],
            "DistanceVector": [],
            "Vector": list(item_ints),
        }
        vector_list.append(pkg_dict)

    return vector_list
