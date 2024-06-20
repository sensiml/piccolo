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



from copy import deepcopy

import pytest
from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.segment_transforms import tr_segment_vertical_scale
from library.core_functions_python.segment_transforms import tr_segment_horizontal_scale
from numpy import arange, pi, sin
from pandas import DataFrame, concat


class TestScaleSegment:
    """Test function for scale_segment functions"""

    def assertEqual(self, a, b):
        assert a == b

    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a dataset"""

        Fs = 50
        f = 3
        sample = 1000
        x = arange(sample)
        y = (sin(2 * pi * f * x / Fs) + 1) * 10 - 10

        df_list = []
        df_sine = DataFrame([], columns=["Word", "SegmentID"])
        df_sine["AccelerometerX"] = y
        df_sine["AccelerometerY"] = y * (-2)
        df_sine["AccelerometerZ"] = y * 4
        df_sine.Word = "Sine"
        df_sine.SegmentID = 1
        df_list.append(df_sine)

        self.passthrough_columns = ["Word", "SegmentID"]
        self.data = concat(df_list)
        self.input_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
        self.data[self.input_columns] = self.data[self.input_columns].astype(int)

        self.data = dataframe_to_datasegments(
            self.data,
            group_columns=["Word", "SegmentID"],
            data_columns=["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        )

    def test_tr_segment_vertical_scale(self):
        # positive and negative values
        input_data = deepcopy(self.data)
        results = tr_segment_vertical_scale(
            input_data, self.input_columns, self.passthrough_columns
        )

        for seg in results:
            max_val = seg["data"].max()

        self.assertEqual(max_val, [32767])

        # all positive values
        input_data = deepcopy(self.data)

        for segment in input_data:
            segment["data"] += 32767

        results = tr_segment_vertical_scale(
            input_data, self.input_columns, self.passthrough_columns
        )

        for seg in results:
            max_val = seg["data"].max()

        self.assertEqual(max_val, [32767])

        # all negative values
        input_data = deepcopy(self.data)
        for segment in input_data:
            segment["data"] -= 32000

        results = tr_segment_vertical_scale(
            input_data, self.input_columns, self.passthrough_columns
        )

        for seg in results:
            max_val = seg["data"].max()

        print(max_val)

        self.assertEqual(max_val, [-32687])

    @pytest.mark.skip("not currently implemented (only dev")
    def test_tr_segment_horizontal_scale_(self):
        input_data = deepcopy(self.data)
        new_length = 103
        results = tr_segment_horizontal_scale(
            input_data,
            self.input_columns,
            new_length,
            "linear",
            self.passthrough_columns,
        )
        self.assertEqual(len(results), new_length)

        input_data = deepcopy(self.data)
        new_length = 2030
        results = tr_segment_horizontal_scale(
            input_data,
            self.input_columns,
            new_length,
            "linear",
            self.passthrough_columns,
        )
        self.assertEqual(len(results), new_length)
