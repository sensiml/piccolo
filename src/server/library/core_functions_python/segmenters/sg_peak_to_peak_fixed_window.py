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
from library.core_functions.utils.utils import handle_group_columns

MAX_INT = 32767
MIN_INT = -32767


@handle_group_columns
def peak_to_peak_fixed_window_segmenter(
    input_data,
    columns_of_interest,
    group_columns,
    return_segment_index=False,
    window_size=256,
    start_window=50,
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
    # if window_size > settings.MAX_SEGMENT_LENGTH:
    #    raise InputParameterException(
    #        "The max segment length cannot exceed {}.".format(settings.MAX_SEGMENT_LENGTH))

    parameters = {
        "window_size": window_size,
        "min_segment_length": min_segment_length,
        "start_window": start_window,
    }

    segments = detect_segments(input_data[columns_of_interest], parameters)

    M = []

    segmentid = 0
    if "SegmentID" in input_data.columns:
        segmentid = input_data["SegmentID"].loc[0]

    for i in range(len(segments)):
        if return_segment_index:
            temp_df = (
                input_data[group_columns]
                .iloc[segments[i][0] : segments[i][0] + 1]
                .copy()
            )
            temp_df["SegmentID"] = i + segmentid
            temp_df["Seg_Begin"] = segments[i][0]
            temp_df["Seg_End"] = segments[i][1]
        else:
            temp_df = input_data.ix[segments[i][0] : segments[i][1]].copy()
            temp_df["SegmentID"] = i + segmentid

        M.append(temp_df)

    if M:
        return pd.concat(M, axis=0)
    else:
        return pd.DataFrame()


peak_to_peak_fixed_window_segmenter_contracts = {
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
            "name": "window_size",
            "type": "int16_t",
            "display_name": "Window Size",
            "default": 256,
            "c_param": 1,
            "description": "Size of window to search over",
        },
        {
            "name": "min_segment_length",
            "type": "int16_t",
            "display_name": "Min Segment Length",
            "default": 100,
            "c_param": 1,
            "description": "Size of window to search over",
        },
        {
            "name": "start_window",
            "type": "int16_t",
            "display_name": "Start Window Size",
            "default": 50,
            "c_param": 1,
            "description": "Size of initial window to look for max peak.",
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
}


def detect_segments(input_data, parameters):

    segment_indexes = []
    idx = 0

    start_index, end_index = peak_peak_detection(input_data, parameters, idx)

    if (end_index - start_index) >= parameters["min_segment_length"]:
        segment_indexes.append([start_index, end_index])

    idx += parameters["window_size"]
    while idx + parameters["window_size"] < len(input_data):

        start_index, end_index = peak_peak_detection(input_data, parameters, idx)

        idx += parameters["window_size"]
        if (end_index - start_index) >= parameters["min_segment_length"]:
            segment_indexes.append([start_index, end_index])

    return segment_indexes


def peak_peak_detection(input_data, params, idx):
    cols = input_data.columns
    max_col = cols[0]
    max_val = MIN_INT
    for col in cols:
        tmp_val = np.max(input_data[col].iloc[idx : idx + params["start_window"]])
        if max_val < tmp_val:
            max_col = col
            max_val = tmp_val

    start_index = idx + np.argmax(
        input_data[max_col].iloc[idx : idx + params["start_window"]]
    )
    delta_start = start_index - idx
    end_index = np.argmax(
        input_data[max_col].iloc[
            start_index
            + params["min_segment_length"] : start_index
            + params["window_size"]
            - delta_start
        ]
    )

    return start_index, end_index + start_index
