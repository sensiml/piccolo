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

import os

import pandas as pd
from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.segmenters.sg_double_peak import (
    double_peak_key_segmenter,
)


class TestWindowingPeakDetectionegmenter:
    """Test windowing segmentation algorithm."""

    def test_windowing_peak_detection_segmenter(self):
        """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""
        params = {
            "min_peak_to_peak": 10,
            "max_peak_to_peak": 150,
            "twist_threshold": -10000,
            "end_twist_threshold": 0,
            "last_twist_threshold": -5000,
            "max_segment_length": 300,
            "return_segment_index": False,
        }

        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "data", "double_peak_data.csv")

        datasegments = dataframe_to_datasegments(
            pd.read_csv(filepath),
            group_columns=["Subject"],
            data_columns=[
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
            ],
        )

        segments = double_peak_key_segmenter(
            datasegments,
            column_of_interest="GyroscopeY",
            group_columns=["Subject"],
            **params
        )

        assert len(segments) == 19

    def test_windowing_peak_detection_segmenter_return_segment_index(self):
        """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""
        params = {
            "min_peak_to_peak": 10,
            "max_peak_to_peak": 150,
            "twist_threshold": -10000,
            "end_twist_threshold": 0,
            "last_twist_threshold": -5000,
            "max_segment_length": 300,
            "return_segment_index": True,
        }

        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "data", "double_peak_data.csv")

        datasegments = dataframe_to_datasegments(
            pd.read_csv(filepath),
            group_columns=["Subject"],
            data_columns=[
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
            ],
        )

        segments = double_peak_key_segmenter(
            datasegments,
            column_of_interest="GyroscopeY",
            group_columns=["Subject"],
            **params
        )

        assert len(segments) == 19
