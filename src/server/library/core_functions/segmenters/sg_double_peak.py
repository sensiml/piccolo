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

import numpy as np
from django.conf import settings
from library.core_functions.segmenters.utils import process_segment_results
from library.core_functions.utils.utils import handle_group_columns
from library.exceptions import InputParameterException
from pandas import DataFrame

MAX_INT = 32767
MIN_INT = -32767


@handle_group_columns
def double_peak_key_segmenter(
    input_data: DataFrame,
    column_of_interest: str,
    group_columns: List[str],
    return_segment_index: bool = False,
    min_peak_to_peak: int = 10,
    max_peak_to_peak: int = 80,
    twist_threshold: int = -20000,
    end_twist_threshold: int = -1000,
    last_twist_threshold: int = 15000,
    max_segment_length: int = 256,
) -> DataFrame:
    """
    Considers a double peak as the key to begin segmentation and a single peak as the end.

    Args:
        input_data (DataFrame): The input data.
        column_of_interest (str): The name of the stream to use for segmentation.
        group_columns (List[str]): A list of column names to use for grouping.
        return_segment_index (bool): If True, returns the segment indexes for start and end. This should only be used for
                                     visualization purposes and not for pipeline building.
        min_peak_to_peak (int): Minimum peak-to-peak distance for a potential double peak.
        max_peak_to_peak (int): Maximum peak-to-peak distance for a potential double peak.
        twist_threshold (int): Threshold to detect a first downward slope in a double peak.
        end_twist_threshold (int): Threshold to detect an upward slope preceding the last peak in a double peak.
        last_twist_threshold (int): Minimum threshold difference between the last peak and the following minimums.
        max_segment_length (int): The maximum number of samples a segment can contain. A segment length too large will
                                  not fit on the device.

    Returns:
        DataFrame: If return_segment_index is True, returns a dictionary containing the start and
                                        end indexes of each segment for visualization purposes. Otherwise, returns a DataFrame.
    """
    if max_segment_length > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "The max segment length cannot exceed {}.".format(
                settings.MAX_SEGMENT_LENGTH
            )
        )

    parameters = {
        "min_peak_to_peak": min_peak_to_peak,
        "max_peak_to_peak": max_peak_to_peak,
        "twist_threshold": twist_threshold,
        "end_twist_threshold": end_twist_threshold,
        "last_twist_threshold": last_twist_threshold,
        "max_segment_length": max_segment_length,
    }

    if not (MIN_INT < parameters["last_twist_threshold"] < MAX_INT):
        raise InputParameterException("last peak threshold must be of size int16_t")

    if not (MIN_INT < parameters["end_twist_threshold"] < MAX_INT):
        raise InputParameterException("end peak threshold must be of size int16_t")

    if not (MIN_INT < parameters["twist_threshold"] < MAX_INT):
        raise InputParameterException("peak threshold must be of size int16_t")

    seg_beg_end_list = detect_segments(
        input_data[column_of_interest].values, parameters, max_segment_length
    )

    return process_segment_results(
        input_data,
        seg_beg_end_list,
        group_columns,
        return_segment_index=return_segment_index,
    )


double_peak_key_segmenter_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "no_display": True},
        {
            "name": "column_of_interest",
            "type": "str",
            "streams": True,
            "display_name": "Column Of Interest",
            "number_of_elements": 1,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "no_display": True,
        },
        {
            "name": "last_twist_threshold",
            "type": "int16_t",
            "display_name": "last peak threshold",
            "default": 15000,
            "c_param": 1,
            "description": "This will be the threshold for detecting the end of the segment",
        },
        {
            "name": "twist_threshold",
            "type": "int16_t",
            "display_name": "peak threshold",
            "default": -20000,
            "c_param": 2,
            "description": "This will be the threshold for detecting the start of the first and second peaks",
        },
        {
            "name": "end_twist_threshold",
            "type": "int16_t",
            "display_name": "end peak threshold",
            "default": -1000,
            "c_param": 3,
            "description": "This will be the threshold for detecting the  end of the first and second peaks",
        },
        {
            "name": "max_segment_length",
            "type": "int",
            "default": 256,
            "c_param": 4,
            "display_name": "Max Segment Length",
            "description": "Maximum length of a segment that can be identified",
        },
        {
            "name": "min_peak_to_peak",
            "type": "int",
            "default": 10,
            "c_param": 5,
            "display_name": "Min Peak to Peak Distance",
            "description": "Min number of samples between peak 1 and 2",
        },
        {
            "name": "max_peak_to_peak",
            "type": "int",
            "default": 80,
            "c_param": 6,
            "display_name": "Max Peak to Peak Distance",
            "description": "Max number of samples between peak 1 and 2",
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


def detect_segments(input_data, parameters, max_segment_length):
    segment_indexes = []
    idx = 0

    start_index, end_index = peak_peak_detection(
        input_data[:], parameters, idx, wait_for_silent=False
    )

    while start_index is not None and end_index is not None:
        if end_index - start_index <= max_segment_length:
            segment_indexes.append([start_index, end_index])
        idx = end_index

        start_index, end_index = peak_peak_detection(
            input_data[end_index:], parameters, idx
        )

    return segment_indexes


def peak_peak_detection(input_data, params, idx, wait_for_silent=True):
    searching = True

    if wait_for_silent:
        index = np.argmax(input_data > params["twist_threshold"])
    else:
        index = 0

    num_sample = len(input_data)

    while searching:
        t1 = True

        while t1:
            if index >= num_sample:
                return None, None

            if np.sum(input_data[index:] < params["twist_threshold"]) == 0:
                return None, None

            first_twist_index = (
                np.argmax(input_data[index:] < params["twist_threshold"]) + index
            )

            # print('twist argmax, ', np.argmax(input_data[index:] <
            #                                  params['twist_threshold']))
            # print('first_twist_index', first_twist_index+idx)

            if first_twist_index >= num_sample:
                return None, None

            end_first_twist = (
                np.argmax(
                    input_data[first_twist_index:] > params["end_twist_threshold"]
                )
                + first_twist_index
            )

            t2 = True

            while t2:
                if end_first_twist >= num_sample:
                    return None, None

                start_second_twist = (
                    np.argmax(input_data[end_first_twist:] < params["twist_threshold"])
                    + end_first_twist
                )
                # print('end_twist_1 ', end_first_twist+idx)
                # print('start_twist_2', start_second_twist+idx)

                time_delta = start_second_twist - first_twist_index
                # print('time between first and second twist', time_delta)

                # End of the twist occured too quickly
                if (
                    params["min_peak_to_peak"]
                    <= time_delta
                    <= params["max_peak_to_peak"]
                ):
                    index = start_second_twist
                    t1 = False
                    t2 = False

                # end of the twist took too long
                elif time_delta > params["max_peak_to_peak"]:
                    t2 = False
                    index += params["max_peak_to_peak"]
                    continue

                # end of the twist took too long
                elif time_delta < params["min_peak_to_peak"]:
                    t2 = False
                    index += params["min_peak_to_peak"]
                    continue

                if start_second_twist >= num_sample:
                    return None, None

            if t1 is False:
                end_second_twist = (
                    np.argmax(
                        input_data[start_second_twist:] > params["end_twist_threshold"]
                    )
                    + start_second_twist
                )

                # print("end second twist", end_second_twist+idx)

                if end_second_twist > num_sample:
                    # print('Reached End of File')
                    return None, None

                time_delta = end_second_twist - start_second_twist

                if time_delta == 0:
                    t1 = True
                    index = end_second_twist
                    # print("Second Peak to Long, searching again from ", index)
                    continue

                # end of the twist took too long
                if time_delta > params["min_peak_to_peak"] * 4:
                    t1 = True
                    index += params["min_peak_to_peak"] * 4
                    # print("Second Peak to Long, searching again from ", index)
                    continue

        final_twist = (
            np.argmax(input_data[end_second_twist:] < params["last_twist_threshold"])
            + end_second_twist
        )

        # print('Final twist', final_twist + idx)
        time_delta = final_twist - end_second_twist

        # print('Segment Length', time_delta)

        # End of the twist occured too quickly
        if time_delta > params["max_segment_length"]:
            index += params["max_segment_length"]
            continue

        if final_twist == end_second_twist:
            # print('No Final Twist')
            return None, None

        return end_second_twist + idx, final_twist + idx
