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
from library.core_functions.segmenters.utils import process_segment_results

z_score_threshold_peak_detection_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "no_display": True},
        {
            "name": "column_of_interest",
            "type": "str",
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
            "name": "segment_length",
            "type": "int16_t",
            "display_name": "Max Segment Size",
            "default": 256,
            "c_param": 1,
            "description": "Segment Length to Search Over",
        },
        {
            "name": "threshold",
            "type": "float",
            "display_name": "Threshold",
            "default": 50,
            "c_param": 2,
            "description": "Threshold above which value must be to consider it a maxx value",
        },
        {
            "name": "lag",
            "type": "int16_t",
            "display_name": "Lag",
            "default": 50,
            "c_param": 3,
            "description": "Threshold above which value must be to consider it a maxx value",
        },
        {
            "name": "influence",
            "type": "float",
            "display_name": "Influence",
            "default": 1,
            "c_param": 4,
            "description": "Threshold above which value must be to consider it a maxx value",
        },
        {
            "name": "offset",
            "type": "int16_t",
            "display_name": "Offset",
            "default": 0,
            "c_param": 5,
            "description": "Threshold above which value must be to consider it a maxx value",
        },
        {
            "name": "return_segment_index",
            "type": "boolean",
            "default": False,
            "no_display": True,
            "description": "Append columns start and stop of the segment index.",
        },
        {
            "name": "peak_type",
            "type": "str",
            "default": "peaks_and_valleys",
            "options": [
                {"name": "peaks_and_valleys"},
                {"name": "peaks"},
                {"name": "valleys"},
            ],
            "description": "Append columns start and stop of the segment index.",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
    "c_contract": [
        {"name": "seg_state", "type": "uint8_t", "value": 0},
        {"name": "max_value", "type": "int16_t", "value": 0},
        {"name": "max_col", "type": "uint8_t", "value": 0},
        {"name": "max_index", "type": "uint16_t", "value": 0},
    ],
}


def z_score_threshold_peak_detection(
    input_data,
    column_of_interest,
    group_columns,
    return_segment_index=False,
    segment_length=10,
    threshold=5,
    lag=10,
    influence=1,
    offset=0,
    peak_type="peak_and_valley",
):
    """
    A sliding windowing technique with adaptive sizing. This will find the largest point after
    min_segment_length that is above the threshold. That point will be considered the end of
    the segment. If no points are above the threshold before reaching max segment length, then
    the segment will stop at max_segment_length

    Args:
        input_data (DataFrame): The input data.
        column_of_interest (str): The stream to use for segmentation.
        group_columns ([str]): A list of column names to use for grouping.
        segment_length (int): This is the maximum number of samples a
         segment can contain.
        lag (float):
        influence (float):
        threshold (float):
        return_segment_index (False): Set to true to see the segment indexes
         for start and end.
    """

    parameters = {
        "segment_length": segment_length,
        "threshold": threshold,
        "offset": offset,
        "lag": lag,
        "influence": influence,
        "peak_type": peak_type,
    }

    seg_beg_end_list = detect_segments(input_data[column_of_interest], parameters)

    return process_segment_results(
        input_data,
        seg_beg_end_list,
        group_columns,
        return_segment_index=return_segment_index,
    )


def detect_segments(input_data, parameters):

    signals = thresholding_algo(
        input_data.values,
        parameters["lag"],
        parameters["threshold"],
        parameters["influence"],
    )

    if parameters["peak_type"] == "peaks":
        peaks = np.where(signals > 0)[0]
    if parameters["peak_type"] == "valleys":
        peaks = np.where(signals < 0)[0]
    if parameters["peak_type"] == "peaks_and_valleys":
        peaks = np.where(signals != 0)[0]

    seg_offset = parameters["segment_length"] - parameters["offset"]

    segment_indexes = [
        [int(x) - seg_offset, int(x) + parameters["offset"]] for x in peaks
    ]

    return segment_indexes


def thresholding_algo(y, lag, threshold, influence):
    signals = np.zeros(len(y))
    filteredY = np.array(y)
    avgFilter = [0] * len(y)
    stdFilter = [0] * len(y)
    avgFilter[lag - 1] = np.mean(y[0:lag])
    stdFilter[lag - 1] = np.std(y[0:lag])
    for i in range(lag, len(y)):
        if abs(y[i] - avgFilter[i - 1]) > threshold * stdFilter[i - 1]:
            if y[i] > avgFilter[i - 1]:
                signals[i] = 1
            else:
                signals[i] = -1

            filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i - 1]
            avgFilter[i] = np.mean(filteredY[(i - lag + 1) : i + 1])
            stdFilter[i] = np.std(filteredY[(i - lag + 1) : i + 1])
        else:
            signals[i] = 0
            filteredY[i] = y[i]
            avgFilter[i] = np.mean(filteredY[(i - lag + 1) : i + 1])
            stdFilter[i] = np.std(filteredY[(i - lag + 1) : i + 1])

    return signals
