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
from library.core_functions.segmenters.sg_windowing_threshold import (
    windowing_threshold,
    windowing_threshold_segmentation_start_end,
)

from . import segment_index_spotted_to_dict


class TestWindowingThresholdSegmenter:
    """Test windowing segmentation algorithm."""

    def test_windowing_threshold_segments_std_offset(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "offset": 50,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 0.08,
            "threshold_space": "std",
        }

        seg_beg_end_list = windowing_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[50, 150], [250, 350], [450, 550], [650, 750]]

        assert ground_data == seg_beg_end_list

    def test_windowing_threshold_segments_variance(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "offset": 0,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 0.006,
            "threshold_space": "variance",
        }

        seg_beg_end_list = windowing_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 200], [300, 400], [500, 600], [700, 800]]

        assert ground_data == seg_beg_end_list

    def test_windowing_threshold_segments_std(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "offset": 0,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 0.08,
            "threshold_space": "std",
        }

        seg_beg_end_list = windowing_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 200], [300, 400], [500, 600], [700, 800]]

        assert ground_data == seg_beg_end_list

    def test_windowing_threshold_segments_variance(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "offset": 0,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 0.12,
            "threshold_space": "absolute avg",
        }

        seg_beg_end_list = windowing_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 200], [300, 400], [500, 600], [700, 800]]

        assert ground_data == seg_beg_end_list

    def test_windowing_threshold_segments_sum(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "offset": 0,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 0.5,
            "threshold_space": "sum",
        }

        seg_beg_end_list = windowing_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 200], [300, 400], [500, 600], [700, 800]]

        assert ground_data == seg_beg_end_list

    def test_windowing_threshold_segments_absolute_sum(self):
        """Calls the segmentation core algorithm and checks output tuples against ground truth."""
        params = {
            "offset": 0,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 0.5,
            "threshold_space": "absolute sum",
        }

        seg_beg_end_list = windowing_threshold_segmentation_start_end(
            build_test_data(np.arange(900), tau=100), **params
        )

        ground_data = [[100, 200], [300, 400], [500, 600], [700, 800]]

        assert ground_data == seg_beg_end_list

    # def test_windowing_threshold_segments_max(self):
    #    """Calls the segmentation core algorithm and checks output tuples against ground truth."""
    #    params = {"offset":0,
    #              "window_size":101,
    #              "threshold_space_width":5,
    #              "vt_threshold":.2,
    #              "threshold_space":'max',
    #    }

    #    seg_beg_end_list = windowing_threshold_segmentation_start_end(build_test_data(np.arange(900), tau=100),
    #                                                                  **params)

    #    ground_data = [[100, 200], [300,400], [500,600], [700,800]]

    #    self.assertEqual(ground_data, seg_beg_end_list)

    # def test_windowing_threshold_segments_min(self):
    #    params = {"offset":0,
    #              "window_size":101,
    #              "threshold_space_width":5,
    #              "vt_threshold":-.2,
    #              "threshold_space":'min',
    #    }

    #    seg_beg_end_list = windowing_threshold_segmentation_start_end(build_test_data(np.arange(900), tau=100),
    #                                                                  **params)

    #    ground_data = [[150, 250],[350,450], [550,650], [750,850]]

    #    self.assertEqual(ground_data, seg_beg_end_list)

    def test_windowing_threshold_segmenter_for_kbclient(self):
        """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""
        params = {
            "offset": 0,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 0.5,
            "threshold_space": "sum",
        }

        spotted_data = windowing_threshold(
            build_test_data(np.arange(900), tau=100, df=True),
            column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        assert isinstance(spotted_data, list)
        for i in range(4):
            assert i == spotted_data[i]["metadata"]["SegmentID"]

    def test_windowing_threshold_segmenter_return_segment(self):
        """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""
        params = {
            "offset": 0,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 0.5,
            "threshold_space": "sum",
            "return_segment_index": True,
        }

        spotted_data = windowing_threshold(
            build_test_data(np.arange(900), tau=100, df=True),
            column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )
        result = segment_index_spotted_to_dict(spotted_data)

        expected = {
            "Seg_Begin": {0: 100, 1: 300, 2: 500, 3: 700},
            "Seg_End": {0: 200, 1: 400, 2: 600, 3: 800},
        }

        assert result == expected

    def test_windowing_threshold_segmenter_no_frames(self):
        params = {
            "offset": 0,
            "window_size": 101,
            "threshold_space_width": 5,
            "vt_threshold": 100,
            "threshold_space": "sum",
            "return_segment_index": True,
        }

        """Applies DCL segmentation to input DataFrame and checks for correct start and end times."""
        spotted_data = windowing_threshold(
            build_test_data(np.arange(900), tau=100, df=True),
            column_of_interest="AccelerometerX",
            group_columns=["Subject"],
            **params
        )

        assert len(spotted_data) == 0


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
        return y
