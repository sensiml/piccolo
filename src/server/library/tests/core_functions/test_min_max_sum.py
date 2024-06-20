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
from library.core_functions.feature_generators.fg_shape_amplitude import (
    fg_amplitude_min_max_sum,
)
from numpy import array
from pandas import DataFrame


class TestMinMaxSum:
    """Test Min Max Sum function."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        self.data = dataframe_to_datasegments(
            DataFrame(
                [
                    [-3, 6, 5, 1],
                    [3, 7, 8, 1],
                    [0, 6, 3, 1],
                    [-2, 8, 7, 1],
                    [2, 9, 6, 1],
                ],
                columns=["Ax", "Ay", "Az", "Subject"],
            ),
            data_columns=["Ax", "Ay", "Az"],
            group_columns=["Subject"],
        )[0]

    def test_min_max_sum(self):
        mms_data = fg_amplitude_min_max_sum(self.data, ["Ax", "Ay", "Az"])
        expected = array([0, 15, 11])
        print(mms_data)

        assert type(DataFrame()) == type(mms_data)
        assert "AxMinMaxSum" in mms_data.columns
        assert "AyMinMaxSum" in mms_data.columns
        assert "AzMinMaxSum" in mms_data.columns

        assert abs(expected[0] - mms_data["AxMinMaxSum"][0]) < 0.001
        assert expected[1] == mms_data["AyMinMaxSum"][0]
        assert expected[2] == mms_data["AzMinMaxSum"][0]
