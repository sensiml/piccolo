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
from library.core_functions_python.segmenters.sg_windowing_peak_detection import (
    windowing_peak_detection_segmentation_start_end,
    windowing_peak_detection_segmenter,
)
from library.tests.core_functions.segmenters import segment_index_spotted_to_dict


class TestWindowingPeakDetectionegmenter:
    """Test windowing segmentation algorithm."""

    def test_windowing_peak_detection_segmenter_for_kbclient(self):
        """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_comparison": "maximum",
            "second_comparison": "minimum",
            "first_threshold_space": "normal",
            "second_threshold_space": "normal",
        }
        spotted_data = windowing_peak_detection_segmenter(
            build_test_data(np.arange(900), tau=100, df=True),
            first_column_of_interest="AccelerometerX",
            second_column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        assert isinstance(spotted_data, list)
        for i in range(4):
            assert i == spotted_data[i]["metadata"]["SegmentID"]

    def test_windowing_peak_detection_segmenter_return_segment_index(self):
        """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_comparison": "maximum",
            "second_comparison": "minimum",
            "first_threshold_space": "normal",
            "second_threshold_space": "normal",
            "return_segment_index": True,
        }

        spotted_data = windowing_peak_detection_segmenter(
            build_test_data(np.arange(900), tau=100, df=True),
            first_column_of_interest="AccelerometerX",
            second_column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        result = segment_index_spotted_to_dict(spotted_data)
        expected = {
            "Seg_Begin": {0: 125, 1: 325, 2: 525, 3: 725},
            "Seg_End": {0: 175, 1: 375, 2: 575, 3: 775},
        }

        assert result == expected

    def test_windowing_peak_segments_maximum_minimum(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_comparison": "maximum",
            "second_comparison": "minimum",
            "first_threshold_space": "normal",
            "second_threshold_space": "normal",
        }
        test_data = build_test_data(np.arange(900), tau=100, df=True)

        seg_beg_end_list = windowing_peak_detection_segmentation_start_end(
            np.vstack((test_data[0]["data"][0], test_data[0]["data"][0])).T, **params
        )

        ground_data = [[125, 175], [325, 375], [525, 575], [725, 775]]

        assert ground_data == seg_beg_end_list


def build_test_data(x, tau=100, df=False):
    tau = 100
    y = np.sin(x * (2 * np.pi) / tau)
    y[0:tau] = 0
    for i in range(10):
        if i % 2:
            y[(i + 1) * tau : (i + 1) * tau + tau] = 0

    if df:
        test_data = pd.DataFrame(y, columns=["AccelerometerX"])
        test_data["Subject"] = 0
        return dataframe_to_datasegments(
            test_data,
            group_columns=["Subject"],
            data_columns=["AccelerometerX"],
            dtype=np.float32,
        )
    else:
        test_data = y

    return test_data
