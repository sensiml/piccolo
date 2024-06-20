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
from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.sensor_transforms import tr_magnitude
from numpy import array
from numpy.testing import assert_array_almost_equal
from pandas import DataFrame


class TestMagnitude:
    """Test Magnitude function."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        self.data = DataFrame(
            [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
            columns=["Ax", "Ay", "Az"],
        )
        self.data["Subject"] = "A"

        self.data = dataframe_to_datasegments(
            self.data, group_columns=["Subject"], data_columns=["Ax", "Ay", "Az"]
        )

    def test_magnitude_transform(self):
        """Computes magnitude and tests that the result is a DataFrame with a new columns."""
        magnitude_data = tr_magnitude(self.data, ["Ax", "Ay", "Az"])
        expected = array([3, 4, 2, 4, 4])

        assert isinstance(magnitude_data, list)
        assert "Magnitude_ST_0000" in magnitude_data[0]["columns"]
        assert_array_almost_equal(
            expected,
            magnitude_data[0]["data"][
                magnitude_data[0]["columns"].index("Magnitude_ST_0000")
            ],
        )

    def test_two_magnitude_transform(self):
        """Computes magnitude and tests that the result is a DataFrame with a new columns."""
        magnitude_data = tr_magnitude(self.data, ["Ax", "Ay", "Az"])
        magnitude_data = tr_magnitude(magnitude_data, ["Ax", "Az"])
        assert isinstance(magnitude_data, list)

        expected = array([3, 4, 2, 4, 4])
        assert "Magnitude_ST_0000" in magnitude_data[0]["columns"]
        index = magnitude_data[0]["columns"].index("Magnitude_ST_0000")
        assert index == 3
        assert_array_almost_equal(expected, magnitude_data[0]["data"][index])

        expected = array([3, 4, 2, 4, 3])
        assert "Magnitude_ST_0001" in magnitude_data[0]["columns"]
        index = magnitude_data[0]["columns"].index("Magnitude_ST_0001")
        assert index == 4

        assert_array_almost_equal(expected, magnitude_data[0]["data"][index])

    def test_multiple_segments(self):
        data = DataFrame(
            [
                [-3, 6, 5],
                [3, 7, 8],
                [0, 6, 3],
                [-2, 8, 7],
                [2, 9, 6],
                [-3, 6, 5],
                [3, 7, 8],
                [0, 6, 3],
                [-2, 8, 7],
                [2, 9, 6],
            ],
            columns=["Ax", "Ay", "Az"],
        )
        data["Subject"] = ["A"] * 5 + ["B"] * 5

        data = dataframe_to_datasegments(
            data, group_columns=["Subject"], data_columns=["Ax", "Ay", "Az"]
        )

        magnitude_data = tr_magnitude(data, ["Ax", "Ay", "Az"])
        expected = array([3, 4, 2, 4, 4])

        assert isinstance(magnitude_data, list)
        assert len(magnitude_data) == 2
        assert "Magnitude_ST_0000" in magnitude_data[0]["columns"]
        index = magnitude_data[0]["columns"].index("Magnitude_ST_0000")
        for segment in magnitude_data:
            assert_array_almost_equal(expected, segment["data"][index])
