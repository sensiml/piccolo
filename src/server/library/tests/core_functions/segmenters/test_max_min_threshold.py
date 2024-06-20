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
from library.core_functions.segmenters.sg_max_min_threshold import (
    max_min_threshold,
    max_min_threshold_segmentation_start_end,
)
from library.tests.core_functions.segmenters import segment_index_spotted_to_dict


class TestMaxMinThresholdSegmenter:
    """Test windowing segmentation algorithm."""

    def test_max_min_threshold_segments_variance(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 0.029476,
            "threshold_space": "variance",
            "second_vt_threshold": 0,
            "threshold_space_width": 10,
        }

        seg_beg_end_list = max_min_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 210], [300, 410], [500, 610], [700, 810]]

        assert ground_data == seg_beg_end_list

    def test_max_min_threshold_segments_std(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 0.1716874,
            "threshold_space": "std",
            "second_vt_threshold": 0,
            "threshold_space_width": 10,
        }

        seg_beg_end_list = max_min_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 210], [300, 410], [500, 610], [700, 810]]

        assert ground_data == seg_beg_end_list

    def test_max_min_threshold_segments_absolute_avg(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 0.27,
            "threshold_space": "absolute avg",
            "second_vt_threshold": 0.0,
            "threshold_space_width": 10,
        }

        seg_beg_end_list = max_min_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 210], [300, 410], [500, 610], [700, 810]]

        assert ground_data == seg_beg_end_list

    def test_max_min_threshold_segments_sum(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 2.7,
            "threshold_space": "sum",
            "second_vt_threshold": -2.7,
            "threshold_space_width": 10,
        }

        seg_beg_end_list = max_min_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 160], [300, 360], [500, 560], [700, 760]]

        assert ground_data == seg_beg_end_list

    def test_max_min_threshold_segments_absolute_sum(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 2.7,
            "threshold_space": "absolute sum",
            "second_vt_threshold": 0.06,
            "threshold_space_width": 10,
        }

        seg_beg_end_list = max_min_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 210], [300, 410], [500, 610], [700, 810]]

        assert ground_data == seg_beg_end_list

    def test_max_min_threshold_segments_stop_at_max(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 2.7,
            "threshold_space": "absolute sum",
            "second_vt_threshold": -1,
            "threshold_space_width": 10,
        }

        seg_beg_end_list = max_min_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 249], [300, 449], [500, 649], [700, 849]]

        assert ground_data == seg_beg_end_list

    def test_max_min_threshold_segmenter_for_kbclient(self):
        """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 0.1716874,
            "threshold_space": "std",
            "second_vt_threshold": 0,
            "threshold_space_width": 10,
        }

        spotted_data = max_min_threshold(
            build_test_data(np.arange(900), tau=100, df=True),
            column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        assert isinstance(spotted_data, list)
        for i in range(4):
            assert i == spotted_data[i]["metadata"]["SegmentID"]

    def test_max_min_threshold_segmenter_return_segments(self):
        params = {
            "max_segment_length": 150,
            "min_segment_length": 50,
            "first_vt_threshold": 0.1716874,
            "threshold_space": "std",
            "second_vt_threshold": 0,
            "threshold_space_width": 10,
            "return_segment_index": True,
        }

        spotted_data = max_min_threshold(
            build_test_data(np.arange(900), tau=100, df=True),
            column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        result = segment_index_spotted_to_dict(spotted_data)

        expected = {
            "Seg_Begin": {0: 100, 1: 300, 2: 500, 3: 700},
            "Seg_End": {0: 210, 1: 410, 2: 610, 3: 810},
        }

        assert result == expected


def build_test_data(x, tau=100, df=False):
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
