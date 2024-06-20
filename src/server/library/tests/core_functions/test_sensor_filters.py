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
from datamanager.datasegments import dataframe_to_datasegments, datasegments_equal
from library.core_functions.sensor_filters import (
    streaming_downsample_by_averaging,
    streaming_downsample_by_decimation,
)
from numpy import array, int32
from pandas import DataFrame


class TestDownsampleAveraging:
    """Test Magnitude function."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        self.data = DataFrame(
            [
                [-3, 6, 5],
                [3, 7, 8],
                [0, 6, 3],
                [-2, 8, 7],
                [2, 9, 6],
                [-3, 6, 5],
                [-3, 6, 5],
                [-3, 6, 5],
                [-11, 11, 11],
            ],
            columns=["Ax", "Ay", "Az"],
        )
        self.data["Subject"] = "A"

        self.data = dataframe_to_datasegments(
            self.data, group_columns=["Subject"], data_columns=["Ax", "Ay", "Az"]
        )

    def test_downsample_averaging(self):
        """Computes magnitude and tests that the result is a DataFrame with a new columns."""
        downsample_data = streaming_downsample_by_averaging(
            self.data, ["Subject"], ["Ax", "Ay", "Az"], filter_length=2
        )

        expected = [
            {
                "data": array(
                    [[0, -1, 0, -3], [6, 7, 7, 6], [6, 5, 5, 5]], dtype=int32
                ),
                "columns": ["Ax", "Ay", "Az"],
                "metadata": {"Subject": "A"},
            }
        ]

        datasegments_equal(downsample_data, expected)

    def test_downsample_by_decimation(self):

        downsample_data = streaming_downsample_by_decimation(
            self.data, ["Subject"], ["Ax", "Ay", "Az"], filter_length=2
        )

        expected = [
            {
                "data": array(
                    [[-3, 0, 2, -3, -11], [6, 6, 9, 6, 11], [5, 3, 6, 5, 11]],
                    dtype=int32,
                ),
                "columns": ["Ax", "Ay", "Az"],
                "metadata": {"Subject": "A"},
            }
        ]

        datasegments_equal(downsample_data, expected)
