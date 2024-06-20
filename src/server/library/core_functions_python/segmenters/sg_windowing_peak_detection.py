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
from django.conf import settings
from library.core_functions.segmenters.utils import process_segment_results
from library.core_functions.utils.utils import handle_group_columns
from library.exceptions import InputParameterException


@handle_group_columns
def windowing_peak_detection_segmenter(
    input_data,
    first_column_of_interest,
    second_column_of_interest,
    group_columns,
    max_segment_length=200,
    min_segment_length=100,
    first_threshold_space="std",
    first_comparison="max",
    second_threshold_space="std",
    second_comparison="min",
    moving_average_width=10,
    return_segment_index=False,
):
    """
    This is a sliding window peak detection algorithm which detects the local maximum or minimum
    within a window and sets the start of a segment to that point. It then detects the local
    maximum or minimum within the max_segment_length distance from that point and sets that
    as the end of the segment.

    Args:
        input_data (DataFrame): input data
        first_column_of_interest (str): name of the stream to use for first threshold segmentation
        second_column_of_interest (str): name of the stream to use for second threshold segmentation
        group_columns (list[str]): list of column names to use for grouping
        max_segment_length (int): number of samples in the window (default is 200)
        min_segment_length (int): The smallest segment allowed. (default 100)
        first_threshold_space (str): threshold space to detect segment against (normal)
        first_comparison (str): detect the maximum or minimum value within the
        window (minimum, minimum)
        second_threshold_space (str): threshold space to detect segment end (normal)
        second_comparison (str): detect the maximum or minimum value within the
        window (minimum, minimum)
        moving_average_width (int): the size of the moving average window.
        return_segment_index (False): set to true to see the segment indexes for start and end.

    Returns:
        DataFrame: The segmented result will have a new column called `SegmentID` that
        contains the segment IDs.
    """
    columns_of_interest = [first_column_of_interest, second_column_of_interest]
    input_stream = input_data[columns_of_interest].values
    seg_beg_end_list = windowing_peak_detection_segmentation_start_end(
        input_stream,
        max_segment_length=max_segment_length,
        min_segment_length=min_segment_length,
        first_threshold_space=first_threshold_space,
        first_comparison=first_comparison,
        second_threshold_space=second_threshold_space,
        second_comparison=second_comparison,
        moving_average_width=moving_average_width,
    )

    return process_segment_results(
        input_data,
        seg_beg_end_list,
        group_columns,
        return_segment_index=return_segment_index,
    )


windowing_peak_detection_segmenter_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "no_display": True},
        {
            "name": "first_column_of_interest",
            "type": "str",
            "streams": True,
            "number_of_elements": 1,
            "display_name": "First Column Of Interest",
            "description": "column used to identify the start of the segment",
        },
        {
            "name": "second_column_of_interest",
            "type": "str",
            "streams": True,
            "number_of_elements": 1,
            "display_name": "Second Column Of Interest",
            "description": "column used to identify the end of the segment",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "no_display": True,
        },
        {
            "name": "max_segment_length",
            "type": "int",
            "default": 200,
            "display_name": "Maximum Segment Length",
            "description": "maximum number of samples a segment can have",
            "c_param": 1,
        },
        {
            "name": "min_segment_length",
            "type": "int",
            "default": 50,
            "display_name": "Minimum Segment Length",
            "description": "minimum number of samples a segment can have",
            "c_param": 2,
        },
        {
            "name": "moving_average_width",
            "type": "int",
            "default": 25,
            "c_param": 3,
            "display_name": "Moving Average Width",
            "description": "the order of the moving average",
        },
        {
            "name": "first_threshold_space",
            "type": "str",
            "default": "normal",
            "display_name": "First Threshold Space",
            "description": "space to transform signal into to compare against the first vertical threshold",
            "options": [{"name": "normal"}],
        },
        {
            "name": "first_comparison",
            "type": "str",
            "default": "maximum",
            "display_name": "First Comparison",
            "description": "the comparison between threshold space and vertical threshold (>=, <=)",
            "options": [{"name": "maximum"}, {"name": "minimum"}],
        },
        {
            "name": "second_threshold_space",
            "type": "str",
            "default": "normal",
            "display_name": "Second Threshold Space",
            "description": "space to transform signal into to compare against the second vertical threshold",
            "options": [{"name": "normal"}],
        },
        {
            "name": "second_comparison",
            "type": "str",
            "default": "minimum",
            "display_name": "Second Comparison",
            "description": "Find the maximum of minimum as of the end segment.",
            "options": [{"name": "maximum"}, {"name": "minimum"}],
        },
        {
            "name": "return_segment_index",
            "type": "boolean",
            "default": False,
            "no_display": True,
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def windowing_peak_detection_segmentation_start_end(
    input_data,
    max_segment_length=200,
    min_segment_length=25,
    first_threshold_space="normal",
    first_comparison="maximum",
    second_threshold_space="normal",
    second_comparison="maximum",
    moving_average_width=10,
):

    threshold_spaces = ["normal"]
    comparisons = ["maximum", "minimum"]
    # Sanity Checks
    assert max_segment_length > min_segment_length
    assert min_segment_length > moving_average_width
    assert first_threshold_space in threshold_spaces
    assert second_threshold_space in threshold_spaces
    assert first_comparison in comparisons
    assert second_comparison in comparisons
    if max_segment_length > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "The max segment length cannot exceed {}.".format(
                settings.MAX_SEGMENT_LENGTH
            )
        )

    segment_indexes = []
    start_index = peak_index_detection(
        input_data[0:max_segment_length, 0],
        threshold_type=first_comparison,
        threshold_space=first_threshold_space,
    )

    while start_index + max_segment_length <= len(input_data):
        local_index = peak_index_detection(
            input_data[
                start_index + min_segment_length : start_index + max_segment_length, 1
            ],
            threshold_type=second_comparison,
            threshold_space=second_threshold_space,
        )

        end_index = local_index + start_index + min_segment_length

        segment_indexes.append([start_index, end_index])

        start_index += max_segment_length

        local_index = peak_index_detection(
            input_data[start_index : start_index + max_segment_length, 0],
            threshold_type=first_comparison,
            threshold_space=first_threshold_space,
        )
        start_index += local_index

    return segment_indexes


def peak_index_detection(
    data_stream, threshold_type="maximum", threshold_space="normal"
):

    local_index = (
        np.argmin(data_stream)
        if threshold_type == "minimum"
        else np.argmax(data_stream)
    )

    return local_index
