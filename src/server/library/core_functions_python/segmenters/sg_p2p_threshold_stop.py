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
from django.conf import settings

from library.core_functions.utils.utils import handle_group_columns
from library.exceptions import InputParameterException

MAX_INT = 32767
MIN_INT = -32767


@handle_group_columns
def peak_to_peak_segmenter_with_thresholding_stop(
    input_data,
    columns_of_interest,
    group_columns,
    return_segment_index=False,
    max_segment_length=256,
    start_window=50,
    threshold=1000,
    min_segment_length=50,
):
    """
    Considers a double peak as the key to begin segmentation segmentation and a single peak as the end.

    Args:
        input_data (DataFrame): The input data.
        axis_of_interest (str): The stream to use for segmentation.
        group_columns ([str]): A list of column names to use for grouping.
        max_segment_length (int): This is the maximum number of samples a
            segment can contain. A segment length too large will not fit on the
            device.
        return_segment_index (False): Set to true to see the segment indexes for start and end.
            Note: This should only be used for visualization not pipeline building.


    """

    if max_segment_length > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "The max segment length cannot exceed {}.".format(
                settings.MAX_SEGMENT_LENGTH
            )
        )

    parameters = {
        "max_segment_length": max_segment_length,
        "min_segment_length": min_segment_length,
        "start_window": start_window,
        "threshold": threshold,
    }

    segments = detect_segments(input_data[columns_of_interest], parameters)

    M = []

    for i in range(len(segments)):
        if return_segment_index:
            temp_df = (
                input_data[group_columns]
                .iloc[segments[i][0] : segments[i][0] + 1]
                .copy()
            )
            temp_df["SegmentID"] = i
            temp_df["Seg_Begin"] = segments[i][0]
            temp_df["Seg_End"] = segments[i][1]
        else:
            temp_df = input_data.ix[segments[i][0] : segments[i][1]].copy()
            temp_df["SegmentID"] = i

        M.append(temp_df)

    if M:
        return pd.concat(M, axis=0)
    else:
        return pd.DataFrame()


peak_to_peak_segmenter_with_thresholding_stop_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "no_display": True},
        {
            "name": "columns_of_interest",
            "type": "list",
            "streams": True,
            "display_name": "Columns Of Interest",
            "number_of_elements": 1,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "no_display": True,
        },
        {
            "name": "max_segment_length",
            "type": "int16_t",
            "display_name": "Max Segment Size",
            "default": 256,
            "c_param": 1,
            "description": "Max segment to search over",
        },
        {
            "name": "min_segment_length",
            "type": "int16_t",
            "display_name": "Min Segment Length",
            "default": 100,
            "c_param": 2,
            "description": "Size of window to search over",
        },
        {
            "name": "threshold",
            "type": "int16_t",
            "display_name": "Threshold",
            "default": 50,
            "c_param": 3,
            "description": "Threshold above which value must be to consider it a maxx value",
        },
        {
            "name": "return_segment_index",
            "type": "boolean",
            "default": False,
            "no_display": True,
            "description": "Append columns start and stop of the segment index.",
        },
    ],
    "output_contract": [
        {"name": "output_data", "type": "DataFrame", "metadata_columns": ["SegmentID"]}
    ],
    "c_contract": [
        {"name": "seg_state", "type": "uint8_t", "value": 0},
        {"name": "max_value", "type": "int16_t", "value": 0},
        {"name": "max_col", "type": "uint8_t", "value": 0},
        {"name": "max_index", "type": "uint16_t", "value": 0},
    ],
}


def detect_segments(input_data, parameters):

    segment_indexes = []
    idx = 0

    start_index, end_index = peak_peak_detection(input_data, parameters, idx)

    while start_index is not None and idx + parameters["start_window"] < len(
        input_data
    ):
        segment_indexes.append([start_index, end_index])
        idx = end_index

        start_index, end_index = peak_peak_detection(input_data, parameters, idx + 1)

    return segment_indexes


def peak_peak_detection(input_data, params, idx):
    cols = input_data.columns
    max_val = MIN_INT
    max_col = None

    start_index = idx
    min_stop = False

    if start_index + params["max_segment_length"] >= len(input_data):
        return None, None

    for col in cols:
        tmp_val = np.max(
            np.abs(
                input_data[col].loc[
                    start_index : start_index + params["min_segment_length"]
                ]
            )
        )

        if tmp_val > params["threshold"] and tmp_val > max_val:
            min_stop = True
            max_val = tmp_val
            max_col = col

    max_val = MIN_INT

    for col in cols:
        if min_stop:
            if col != max_col:
                continue

        tmp_val = np.max(
            np.abs(
                input_data[col].loc[
                    start_index
                    + params["min_segment_length"] : start_index
                    + params["max_segment_length"]
                ]
            )
        )

        if max_val < tmp_val:
            max_val = tmp_val
            end_index = np.argmax(
                np.abs(
                    input_data[col].loc[
                        start_index
                        + params["min_segment_length"] : start_index
                        + params["max_segment_length"]
                    ]
                )
            )

    if max_val < params["threshold"] and min_stop is False:
        end_index = start_index + params["max_segment_length"] - 1

    if max_val < params["threshold"] and min_stop:
        end_index = start_index + params["min_segment_length"]

    return start_index, end_index + start_index
