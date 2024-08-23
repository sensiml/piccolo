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
from numpy.testing import assert_array_almost_equal
from pandas import DataFrame

from library.core_functions_python.tr_filter_extreme_values import filter_extreme_values


class TestFilterExtremeValues:
    def assertEqual(self, a, b):
        assert a == b

    def assertFalse(self, a):
        assert not a

    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = DataFrame(
            [
                [-100, -200, -300],
                [3, 7, 8],
                [0, 6, 90],
                [-2, 8, 7],
                [8, 9, 6],
                [8, 9, 6],
                [100, 200, 300],
            ],
            columns=["feature1", "feature2", "feature3"],
        )
        self.data["Subject"] = "s01"
        self.min_max_params = {
            "maximums": {"feature1": 400, "feature2": 90, "feature3": 500},
            "minimums": {"feature1": 0, "feature2": 0, "feature3": -100},
        }

    def test_tr_filter_extreme_values_min_max(self):
        output_data, params = filter_extreme_values(
            self.data,
            ["feature1", "feature2", "feature3"],
            -100,
            100,
        )
        self.assertEqual(type(DataFrame()), type(output_data))
        for x in output_data["feature1"]:
            self.assertFalse(x > 100)
            self.assertFalse(x < -100)
        for x in output_data["feature2"]:
            self.assertFalse(x > 100)
            self.assertFalse(x < -100)
        for x in output_data["feature3"]:
            self.assertFalse(x > 100)
            self.assertFalse(x < -100)

    def test_tr_filter_extreme_values_signal_parameters(self):
        output_data, params = filter_extreme_values(
            self.data,
            ["feature1", "feature2", "feature3"],
            -100,
            100,
            self.min_max_params,
        )
        self.assertEqual(type(DataFrame()), type(output_data))
        for x in output_data["feature1"]:
            self.assertFalse(x > 400)
            self.assertFalse(x < 0)
        for x in output_data["feature2"]:
            self.assertFalse(x > 90)
            self.assertFalse(x < 0)
        for x in output_data["feature3"]:
            self.assertFalse(x > 500)
            self.assertFalse(x < -100)

    def test_tr_filter_extreme_values_passthrough_columns(self):
        output_data, params = filter_extreme_values(
            self.data,
            [],
            -100,
            100,
        )
        self.assertEqual(type(DataFrame()), type(output_data))
        assert_array_almost_equal(output_data["feature1"], self.data["feature1"])
        assert_array_almost_equal(output_data["feature2"], self.data["feature2"])
        assert_array_almost_equal(output_data["feature3"], self.data["feature3"])

    def test_tr_filter_extreme_values_signal_param_output(self):
        output_data, params = filter_extreme_values(
            self.data,
            ["feature1", "feature2", "feature3"],
            -100,
            100,
        )
        for x in params["minimums"].values():
            self.assertEqual(x, -100)
        for x in params["maximums"].values():
            self.assertEqual(x, 100)
