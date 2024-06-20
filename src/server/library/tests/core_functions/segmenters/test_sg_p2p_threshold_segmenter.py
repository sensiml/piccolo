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
import os
from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.segmenters.sg_p2p_threshold_segmenter import (
    peak_to_peak_segmenter_with_thresholding,
)
from library.exceptions import InputParameterException

from . import segment_index_spotted_to_dict


def build_test_data(x, tau=100, df=False):
    y = (np.sin(x * 2 * np.pi / tau) * 1000).astype(int)

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


def test_peak_to_peak_segmenter_with_thresholding():
    """Applies segmentation wrapper to input DataFrame and checks for 20 unique values in the Rep column."""

    params = {
        "max_segment_length": 150,
        "min_segment_length": 50,
        "threshold": 100,
        "absolute_value": False,
        "return_segment_index": False,
    }

    spotted_data = peak_to_peak_segmenter_with_thresholding(
        build_test_data(np.arange(900), df=True),
        columns_of_interest=["AccelerometerX"],
        group_columns=["Subject"],
        **params
    )

    assert isinstance(spotted_data, list)
    for i in range(8):
        assert i == spotted_data[i]["metadata"]["SegmentID"]


def test_peak_to_peak_segmenter_return_segments():
    params = {
        "max_segment_length": 150,
        "min_segment_length": 50,
        "threshold": 100,
        "absolute_value": False,
        "return_segment_index": True,
    }

    spotted_data = peak_to_peak_segmenter_with_thresholding(
        build_test_data(np.arange(900), df=True),
        columns_of_interest=["AccelerometerX"],
        group_columns=["Subject"],
        **params
    )

    result = segment_index_spotted_to_dict(spotted_data)

    expected = {
        "Seg_Begin": {0: 0, 1: 126, 2: 226, 3: 326, 4: 426, 5: 526, 6: 626, 7: 726},
        "Seg_End": {0: 125, 1: 225, 2: 325, 3: 425, 4: 525, 5: 625, 6: 725, 7: 825},
    }

    assert result == expected


def test_peak_to_peak_segmenter_return_segments_absolute():
    params = {
        "max_segment_length": 150,
        "min_segment_length": 50,
        "threshold": 100,
        "absolute_value": True,
        "return_segment_index": True,
    }

    spotted_data = peak_to_peak_segmenter_with_thresholding(
        build_test_data(np.arange(900), df=True),
        columns_of_interest=["AccelerometerX"],
        group_columns=["Subject"],
        **params
    )

    result = segment_index_spotted_to_dict(spotted_data)

    print(result)

    expected = {
        "Seg_Begin": {0: 0, 1: 76, 2: 176, 3: 276, 4: 376, 5: 476, 6: 576, 7: 676},
        "Seg_End": {0: 75, 1: 175, 2: 275, 3: 375, 4: 475, 5: 575, 6: 675, 7: 775},
    }
    assert result == expected


def test_peak_to_peak_segmenter_return_segments_absolute():
    params = {
        "max_segment_length": 150,
        "min_segment_length": 50,
        "threshold": 100,
        "absolute_value": True,
        "return_segment_index": True,
    }

    spotted_data = peak_to_peak_segmenter_with_thresholding(
        build_test_data(np.arange(900), df=True),
        columns_of_interest=["AccelerometerX"],
        group_columns=["Subject"],
        **params
    )

    result = segment_index_spotted_to_dict(spotted_data)

    print(result)

    expected = {
        "Seg_Begin": {0: 0, 1: 76, 2: 176, 3: 276, 4: 376, 5: 476, 6: 576, 7: 676},
        "Seg_End": {0: 75, 1: 175, 2: 275, 3: 375, 4: 475, 5: 575, 6: 675, 7: 775},
    }
    assert result == expected


def test_peak_to_peak_segmenter_with_thresholding_fail_case():

    params = {
        "max_segment_length": 1,
        "min_segment_length": 0,
        "threshold": 50,
        "absolute_value": False,
        "return_segment_index": False,
    }

    data = pd.read_csv(
        os.path.join(
            os.path.dirname(__file__), "data", "test_p2p_threshold_segmenter_fail.csv"
        ),
        index_col=0,
    )
    data["Subject"] = 0

    raied_exception = False
    try:
        spotted_data = peak_to_peak_segmenter_with_thresholding(
            data,
            columns_of_interest=["A", "B", "C"],
            group_columns=["Subject"],
            **params
        )
    except InputParameterException:
        raied_exception = True

    assert raied_exception


failed_pipeline = [
    {
        "name": ["Book1.csv"],
        "type": "capturefile",
        "outputs": ["temp.raw"],
        "data_columns": ["A", "B", "C"],
    },
    {
        "name": "Adaptive Windowing Segmentation",
        "type": "segmenter",
        "inputs": {
            "threshold": 50,
            "input_data": "temp.raw",
            "group_columns": ["Subject"],
            "absolute_value": True,
            "max_segment_length": 1,
            "min_segment_length": 0,
            "columns_of_interest": ["A", "B", "C"],
            "return_segment_index": True,
        },
        "outputs": ["temp.Adaptive_Windowing_Segmentation"],
        "feature_table": None,
    },
]
