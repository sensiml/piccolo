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

from typing import List

from django.conf import settings
from library.core_functions.segmenters.utils import process_segment_results
from library.core_functions.utils.utils import handle_group_columns
from library.exceptions import InputParameterException
from pandas import DataFrame

MAX_INT = 32767
MIN_INT = -32767


@handle_group_columns
def peak_to_peak_segmenter_with_thresholding(
    input_data: DataFrame,
    columns_of_interest: str,
    group_columns: List[str],
    return_segment_index: bool = False,
    max_segment_length: int = 256,
    threshold: int = 1000,
    min_segment_length: int = 50,
    absolute_value: bool = True,
):
    """
    A sliding windowing technique with adaptive sizing. This will find the largest point after
    min_segment_length that is above the threshold. That point will be considered the end of
    the segment. If no points are above the threshold before reaching max segment length, then
    the segment will stop at max_segment_length

    Args:
        input_data (DataFrame): The input data.
        columns_of_interest (str): The stream to use for segmentation.
        group_columns ([str]): A list of column names to use for grouping.
        max_segment_length (int): This is the maximum number of samples a
         segment can contain.
        min_segment_length (int) This is the minimum number of samples a
         segment can contain.
        threshold (int): The threshold must be met to start looking for the
         end of the segment early. If the threshold is not met, the segment
         ends at the max_segment_length
        absolute_value (bool): Takes the absolute value of the sensor data prior
         do doing the comparison
        return_segment_index (False): Set to true to see the segment indexes
         for start and end.
    """

    if max_segment_length > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "The max segment length cannot exceed {}.".format(
                settings.MAX_SEGMENT_LENGTH
            )
        )

    if min_segment_length <= 0:
        raise InputParameterException("The min segment length cannot be less than 0")

    parameters = {
        "max_segment_length": max_segment_length,
        "min_segment_length": min_segment_length,
        "threshold": threshold,
        "absolute_value": absolute_value,
    }

    seg_beg_end_list = detect_segments(input_data[columns_of_interest], parameters)

    return process_segment_results(
        input_data,
        seg_beg_end_list,
        group_columns,
        return_segment_index=return_segment_index,
    )


peak_to_peak_segmenter_with_thresholding_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "no_display": True},
        {
            "name": "columns_of_interest",
            "type": "list",
            "streams": True,
            "display_name": "Columns Of Interest",
            "number_of_elements": -1,
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
            "name": "absolute_value",
            "type": "boolean",
            "display_name": "Absolute Value",
            "default": True,
            "c_param": 4,
            "description": "Take the absolute value of the sensor data before doing the comparison",
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

    while start_index is not None and idx + parameters["max_segment_length"] < len(
        input_data
    ):
        segment_indexes.append([start_index, end_index])
        idx = end_index

        start_index, end_index = peak_peak_detection(input_data, parameters, idx + 1)

    return segment_indexes


def peak_peak_detection(input_data, params, idx):
    cols = input_data.columns
    max_val = MIN_INT

    start_index = idx

    if start_index + params["max_segment_length"] >= len(input_data):
        return None, None

    for col in cols:
        tmp_val = None
        if params["absolute_value"]:
            end_index = (
                input_data[col]
                .iloc[
                    start_index
                    + params["min_segment_length"] : start_index
                    + params["max_segment_length"]
                ]
                .abs()
                .idxmax()
            )
            tmp_val = abs(input_data[col].iloc[end_index])
        else:
            end_index = (
                input_data[col]
                .iloc[
                    start_index
                    + params["min_segment_length"] : start_index
                    + params["max_segment_length"]
                ]
                .idxmax()
            )

            tmp_val = input_data[col].iloc[end_index]

        if max_val < tmp_val:
            max_val = tmp_val

    if max_val < params["threshold"]:
        end_index = start_index + params["min_segment_length"] - 1
    else:
        end_index = end_index

    return start_index, end_index
