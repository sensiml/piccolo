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
import pandas as pd
from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.segmenters.sg_general_threshold import (
    general_threshold,
)

from . import segment_index_spotted_to_dict


class TestGeneralThresholdSegmenter:
    """Test windowing segmentation algorithm."""

    def test_general_threshold_segmenter_for_kbclient(self):
        """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""

        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 0.171687,
            "second_vt_threshold": 0,
            "first_comparison": "max",
            "second_comparison": "min",
            "first_threshold_space": "std",
            "second_threshold_space": "std",
            "threshold_space_width": 10,
        }

        spotted_data = general_threshold(
            build_test_data(np.arange(900), tau=100, df=True),
            first_column_of_interest="AccelerometerX",
            second_column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        assert isinstance(spotted_data, list)
        for i in range(4):
            assert i == spotted_data[i]["metadata"]["SegmentID"]

    def test_general_threshold_segmenter_return_segments(self):
        params = {
            "max_segment_length": 100,
            "min_segment_length": 50,
            "first_vt_threshold": 0.171687,
            "second_vt_threshold": 0,
            "first_comparison": "max",
            "second_comparison": "min",
            "first_threshold_space": "std",
            "second_threshold_space": "std",
            "threshold_space_width": 10,
            "return_segment_index": True,
        }

        spotted_data = general_threshold(
            build_test_data(np.arange(900), tau=100, df=True),
            first_column_of_interest="AccelerometerX",
            second_column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        result = segment_index_spotted_to_dict(spotted_data)

        expected = {
            "Seg_Begin": {0: 100, 1: 300, 2: 500, 3: 700},
            "Seg_End": {0: 199, 1: 399, 2: 599, 3: 799},
        }

        assert result == expected

    def test_general_threshold_segmenter_return_segments_partial(self):
        params = {
            "max_segment_length": 100,
            "min_segment_length": 50,
            "first_vt_threshold": 0.171687,
            "second_vt_threshold": 0,
            "first_comparison": "max",
            "second_comparison": "min",
            "first_threshold_space": "std",
            "second_threshold_space": "std",
            "threshold_space_width": 10,
            "return_segment_index": True,
            "keep_partial_segment": True,
        }

        spotted_data = general_threshold(
            build_test_data(np.arange(150), tau=100, df=True),
            first_column_of_interest="AccelerometerX",
            second_column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        result = segment_index_spotted_to_dict(spotted_data)

        expected = {
            "Seg_Begin": {0: 100},
            "Seg_End": {0: 149},
        }

        assert result == expected


def build_test_data(x, tau=100, df=False):
    tau = 100
    y = np.sin(x * (2 * np.pi) / tau)
    y[0:tau] = 0
    for i in range(10):
        if i % 2:
            y[(i + 1) * tau : (i + 1) * tau + tau] = 0

    print(y)

    if df:
        test_data = pd.DataFrame(y, columns=["AccelerometerX"])
        test_data["Subject"] = 0
    else:
        test_data = y

    return dataframe_to_datasegments(
        test_data,
        group_columns=["Subject"],
        data_columns=["AccelerometerX"],
        dtype=np.float32,
    )
