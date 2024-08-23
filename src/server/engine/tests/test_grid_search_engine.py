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

import unittest

import pytest

from engine.gridsearchengine import (
    filter_update_dictionary,
    flatten_dictionary,
    get_permutated_dictionary_arrays,
    permutate_dictionary_arrays,
    update_set,
)


class TestGridSearchEngine:
    """Unit tests for EventFile and EventFiles."""

    fixtures = ["datamanager.yml", "develop.yml"]

    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    def test_filter_update_dictionary(self):
        inputs = {"a": 1, "b": 2, "c": 3}
        grid_parameters = {"a": 4, "b": 5, "d": 6}

        result = filter_update_dictionary(inputs, grid_parameters)

        expected_result = {"a": 4, "b": 5}

        assert result == expected_result

    def test_update_set(self):
        grid_parameters = {
            "Mean": {"columns": ["AccelerometerZ"]},
            "Kurtosis": {"columns": ["AccelerometerZ"]},
        }

        step = {
            "inputs": {
                "group_columns": ["Class", "SegmentID", "Subject"],
                "input_data": "temp.Windowing0",
            },
            "name": "generator_set",
            "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
            "set": [
                {"function_name": "Mean", "inputs": {"columns": ["AccelerometerY"]}},
                {
                    "function_name": "Skewness",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "Kurtosis",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "Zero Crossing Rate",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
            ],
            "type": "generatorset",
        }

        update_set(step, grid_parameters)

        expected_result = {
            "inputs": {
                "group_columns": ["Class", "SegmentID", "Subject"],
                "input_data": "temp.Windowing0",
            },
            "name": "generator_set",
            "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
            "set": [
                {"function_name": "Mean", "inputs": {"columns": ["AccelerometerZ"]}},
                {
                    "function_name": "Skewness",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "Kurtosis",
                    "inputs": {"columns": ["AccelerometerZ"]},
                },
                {
                    "function_name": "Zero Crossing Rate",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
            ],
            "type": "generatorset",
        }

        assert step == expected_result

    def test_permutate_dictionary_arrays_single_param(self):
        grid_parameters = {"delta": [150, 200, 250]}

        result = permutate_dictionary_arrays(grid_parameters)

        expected_result = [{"delta": 150}, {"delta": 200}, {"delta": 250}]

        assert result == expected_result

    def test_permutate_dictionary_arrays_two_param(self):
        grid_parameters = {"delta": [150, 200, 250], "size": [100, 200]}

        result = permutate_dictionary_arrays(grid_parameters)

        expected_result = [
            {"delta": 150, "size": 100},
            {"delta": 200, "size": 100},
            {"delta": 250, "size": 100},
            {"delta": 150, "size": 200},
            {"delta": 200, "size": 200},
            {"delta": 250, "size": 200},
        ]

        for row in expected_result:
            assert row in result

    def test_permutate_dictionary_arrays_three_param(self):
        grid_parameters = {
            "delta": [150, 200, 250],
            "size": [100, 200],
            "color": ["red", "blue"],
        }

        result = permutate_dictionary_arrays(grid_parameters)

        expected_result = [
            {"delta": 150, "size": 100, "color": "red"},
            {"delta": 200, "size": 100, "color": "red"},
            {"delta": 250, "size": 100, "color": "red"},
            {"delta": 150, "size": 200, "color": "red"},
            {"delta": 200, "size": 200, "color": "red"},
            {"delta": 250, "size": 200, "color": "red"},
            {"delta": 150, "size": 100, "color": "blue"},
            {"delta": 200, "size": 100, "color": "blue"},
            {"delta": 250, "size": 100, "color": "blue"},
            {"delta": 150, "size": 200, "color": "blue"},
            {"delta": 200, "size": 200, "color": "blue"},
            {"delta": 250, "size": 200, "color": "blue"},
        ]

        for row in expected_result:
            assert row in result

    def test_flatten_dictionary(self):

        grid_parameters = {
            "validation_method": {"test": [1, 2, 3]},
            "training_method": {"red": [4, 5, 6]},
            "classifier_method": {"blue": [7, 8, 9], "green": [10, 11, 12]},
        }

        result = flatten_dictionary(grid_parameters)

        print(result)

        expected_result = {
            "training_method.red": [4, 5, 6],
            "validation_method.test": [1, 2, 3],
            "classifier_method.green": [10, 11, 12],
            "classifier_method.blue": [7, 8, 9],
        }

        assert result == expected_result

    def test_get_permuated_dictionary_arrays(self):

        grid_parameters = {
            "validation_method": {"test": [1, 2]},
            "training_method": {"red": [4, 5]},
            "classifier_method": {"blue": [7, 8], "green": [10, 11]},
        }
        step = {"type": "tvo"}

        result = get_permutated_dictionary_arrays(grid_parameters, step)

        expected_result = [
            {
                "classifier_method": {"blue": 7, "green": 10},
                "training_method": {"red": 4},
                "validation_method": {"test": 1},
            },
            {
                "classifier_method": {"blue": 8, "green": 10},
                "training_method": {"red": 4},
                "validation_method": {"test": 1},
            },
            {
                "classifier_method": {"blue": 7, "green": 11},
                "training_method": {"red": 4},
                "validation_method": {"test": 1},
            },
            {
                "classifier_method": {"blue": 8, "green": 11},
                "training_method": {"red": 4},
                "validation_method": {"test": 1},
            },
            {
                "classifier_method": {"blue": 7, "green": 10},
                "training_method": {"red": 4},
                "validation_method": {"test": 2},
            },
            {
                "classifier_method": {"blue": 8, "green": 10},
                "training_method": {"red": 4},
                "validation_method": {"test": 2},
            },
            {
                "classifier_method": {"blue": 7, "green": 11},
                "training_method": {"red": 4},
                "validation_method": {"test": 2},
            },
            {
                "classifier_method": {"blue": 8, "green": 11},
                "training_method": {"red": 4},
                "validation_method": {"test": 2},
            },
            {
                "classifier_method": {"blue": 7, "green": 10},
                "training_method": {"red": 5},
                "validation_method": {"test": 1},
            },
            {
                "classifier_method": {"blue": 8, "green": 10},
                "training_method": {"red": 5},
                "validation_method": {"test": 1},
            },
            {
                "classifier_method": {"blue": 7, "green": 11},
                "training_method": {"red": 5},
                "validation_method": {"test": 1},
            },
            {
                "classifier_method": {"blue": 8, "green": 11},
                "training_method": {"red": 5},
                "validation_method": {"test": 1},
            },
            {
                "classifier_method": {"blue": 7, "green": 10},
                "training_method": {"red": 5},
                "validation_method": {"test": 2},
            },
            {
                "classifier_method": {"blue": 8, "green": 10},
                "training_method": {"red": 5},
                "validation_method": {"test": 2},
            },
            {
                "classifier_method": {"blue": 7, "green": 11},
                "training_method": {"red": 5},
                "validation_method": {"test": 2},
            },
            {
                "classifier_method": {"blue": 8, "green": 11},
                "training_method": {"red": 5},
                "validation_method": {"test": 2},
            },
        ]

        for row in expected_result:
            assert row in result


if __name__ == "__main__":
    unittest.main()
