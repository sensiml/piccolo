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


@handle_group_columns
# developer documentation
# input_data: Pandas dataframe
# group_columns (list[str]): list of column names to use for grouping.
def general_threshold(
    input_data: DataFrame,
    first_column_of_interest: str,
    second_column_of_interest: str,
    group_columns: List[str],
    max_segment_length: int = 200,
    min_segment_length: int = 100,
    first_vt_threshold: int = 1000,
    first_threshold_space: str = "std",
    first_comparison: str = "max",
    second_vt_threshold: int = 1000,
    second_threshold_space: str = "std",
    second_comparison: str = "min",
    threshold_space_width: int = 10,
    drop_over: bool = False,
    return_segment_index: bool = False,
    keep_partial_segment: bool = False,
):
    """
    This is a general threshold segmentation algorithm which transforms a window
    of the data stream of size threshold_space_width into threshold space. This function
    transfer the `input_data` and `group_column` from the previous pipeline block.

    The threshold space can be computed as standard deviation, sum, absolute sum, absolute
    average and variance. The vt threshold is then compared against the calculated value
    with a comparison type of <= or >= based on the use of "min" or "max" in the comparison
    type. This algorithm is a two pass detection, the first pass detects the start of the
    segment, the second pass detects the end of the segment. In this generalized algorithm,
    the two can be set independently.

    Args:
        first_column_of_interest (str): name of the stream to use for first threshold segmentation
        second_column_of_interest (str): name of the stream to use for second threshold segmentation
        max_segment_length (int): number of samples in the window (default is 200)
        min_segment_length (int): The smallest segment allowed. (default 100)
        first_vt_threshold (int):vt_threshold value to begin detecting a segment
        first_threshold_space (str): threshold space to detect segment against (std, variance, absolute avg, absolute sum, sum)
        first_comparison (str): detect threshold above(max) or below(min) the vt_threshold (max, min)
        second_vt_threshold (int):vt_threshold value to detect a segments
           end.
        second_threshold_space (str): threshold space to detect segment end (std, variance, absolute avg, absolute sum, sum)
        second_comparison (str): detect threshold above(max) or below(min) the vt_threshold (max, min)
           threshold_space_width (int): the size of the buffer that the threshold value is calculated from.
        return_segment_index (False): set to true to see the segment indexes for start and end.

    Returns:
        DataFrame: The segmented result will have a new column called `SegmentID` that
        contains the segment IDs.


    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df
            out:
                   Subject     Class  Rep  accelx  accely  accelz
                0      s01  Crawling    1     377     569    4019
                1      s01  Crawling    1     357     594    4051
                2      s01  Crawling    1     333     638    4049
                3      s01  Crawling    1     340     678    4053
                4      s01  Crawling    1     372     708    4051
                5      s01  Crawling    1     410     733    4028
                6      s01  Crawling    1     450     733    3988
                7      s01  Crawling    1     492     696    3947
                8      s01  Crawling    1     518     677    3943
                9      s01  Crawling    1     528     695    3988
                10     s01  Crawling    1      -1    2558    4609
                11     s01   Running    1     -44   -3971     843
                12     s01   Running    1     -47   -3982     836
                13     s01   Running    1     -43   -3973     832
                14     s01   Running    1     -40   -3973     834
                15     s01   Running    1     -48   -3978     844
                16     s01   Running    1     -52   -3993     842
                17     s01   Running    1     -64   -3984     821
                18     s01   Running    1     -64   -3966     813
                19     s01   Running    1     -66   -3971     826
                20     s01   Running    1     -62   -3988     827
                21     s01   Running    1     -57   -3984     843

        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns=['accelx', 'accely', 'accelz'],
                            group_columns=['Subject', 'Class', 'Rep'],
                            label_column='Class')

        >>> client.pipeline.add_transform("General Threshold Segmentation",
                           params={"first_column_of_interest": 'accelx',
                                "second_column_of_interest": 'accely',
                                "max_segment_length": 5,
                                "min_segment_length": 5,
                                "threshold_space_width": 2,
                                "first_vt_threshold": 0.05,
                                "first_threshold_space": 'std',
                                "first_comparison": 'max',
                                "second_vt_threshold": 0.05,
                                "second_threshold_space": 'std',
                                "second_comparison": 'min',
                                "return_segment_index": False})

        >>> results, stats = client.pipeline.execute()
        >>> print results
            out:
                      Class  Rep  SegmentID Subject  accelx  accely  accelz
                0  Crawling    1          0     s01     377     569    4019
                1  Crawling    1          0     s01     357     594    4051
                2  Crawling    1          0     s01     333     638    4049
                3  Crawling    1          0     s01     340     678    4053
                4  Crawling    1          0     s01     372     708    4051
                5   Running    1          0     s01     -44   -3971     843
                6   Running    1          0     s01     -47   -3982     836
                7   Running    1          0     s01     -43   -3973     832
                8   Running    1          0     s01     -40   -3973     834
                9   Running    1          0     s01     -48   -3978     844


    """

    columns_of_interest = [first_column_of_interest, second_column_of_interest]
    input_stream = input_data[columns_of_interest].values
    seg_beg_end_list = general_threshold_segmentation_start_end(
        input_stream,
        max_segment_length=max_segment_length,
        min_segment_length=min_segment_length,
        first_vt_threshold=first_vt_threshold,
        first_threshold_space=first_threshold_space,
        first_comparison=first_comparison,
        second_vt_threshold=second_vt_threshold,
        second_threshold_space=second_threshold_space,
        second_comparison=second_comparison,
        threshold_space_width=threshold_space_width,
        drop_over=drop_over,
        keep_partial_segment=keep_partial_segment,
    )

    return process_segment_results(
        input_data,
        seg_beg_end_list,
        group_columns,
        return_segment_index=return_segment_index,
    )


general_threshold_contracts = {
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
            "name": "threshold_space_width",
            "type": "int",
            "default": 25,
            "c_param": 3,
            "display_name": "Threshold Space Width",
            "description": "the size of the window to transform into threshold space",
        },
        {
            "name": "first_vt_threshold",
            "type": "float",
            "default": 1000,
            "c_param": 4,
            "display_name": "Initial Vertical Threshold",
            "description": "the threshold value to identify the start of a segment",
        },
        {
            "name": "first_threshold_space",
            "type": "str",
            "default": "std",
            "display_name": "First Threshold Space",
            "description": "space to transform signal into to compare against the first vertical threshold",
            "options": [
                {"name": "std"},
                {"name": "absolute sum"},
                {"name": "sum"},
                {"name": "variance"},
                {"name": "absolute avg"},
            ],
        },
        {
            "name": "first_comparison",
            "type": "str",
            "default": "max",
            "display_name": "First Comparison",
            "description": "the comparison between threshold space and vertical threshold (>=, <=)",
            "options": [{"name": "max"}, {"name": "min"}],
        },
        {
            "name": "second_vt_threshold",
            "type": "float",
            "default": 1000,
            "c_param": 5,
            "display_name": "Second Vertical Threshold",
            "description": "the threshold value to identify the end of a segment",
        },
        {
            "name": "second_threshold_space",
            "type": "str",
            "default": "std",
            "display_name": "Second Threshold Space",
            "description": "space to transform signal into to compare against the second vertical threshold",
            "options": [
                {"name": "std"},
                {"name": "absolute sum"},
                {"name": "sum"},
                {"name": "variance"},
                {"name": "absolute avg"},
            ],
        },
        {
            "name": "second_comparison",
            "type": "str",
            "default": "min",
            "display_name": "Second Comparison",
            "description": "the comparison between threshold space and vertical threshold (>=, <=)",
            "options": [{"name": "max"}, {"name": "min"}],
        },
        {
            "name": "drop_over",
            "type": "boolean",
            "default": False,
            "display_name": "Drop over max length",
            "description": "If the second threshold has not been triggered by max length, drop the segment.",
            "options": [{"name": True}, {"name": False}],
        },
        {
            "name": "return_segment_index",
            "type": "boolean",
            "default": False,
            "no_display": True,
        },
        {
            "name": "keep_partial_segment",
            "type": "boolean",
            "display_name": "Keep Partial Segment",
            "default": False,
            "description": "When training if True, when the algorithm gets to the end of file and has only found part of a segment, it will keep the segment. If False it will discard any unfinished segments.",
            "no_display": False,
        },
    ],
    "output_contract": [
        {"name": "output_data", "type": "DataFrame", "metadata_columns": ["SegmentID"]}
    ],
}


def general_threshold_segmentation_start_end(
    input_data,
    max_segment_length=100,
    min_segment_length=50,
    first_vt_threshold=1000,
    first_threshold_space="std",
    first_comparison="max",
    second_vt_threshold=1000,
    second_threshold_space="std",
    second_comparison="min",
    drop_over=False,
    threshold_space_width=10,
    keep_partial_segment=False,
):

    threshold_spaces = ["std", "variance", "sum", "absolute sum", "absolute avg"]
    comparisons = ["max", "min"]

    if min_segment_length <= 0:
        raise InputParameterException("Segment Length cannot be negative.")

    # Sanity Checks
    if max_segment_length < min_segment_length:
        raise InputParameterException(
            "Max segment length must be greater than the min segment length"
        )

    if min_segment_length <= threshold_space_width:
        raise InputParameterException(
            "Min segment length must be greater than the threshold space width"
        )

    if first_threshold_space not in threshold_spaces:
        raise InputParameterException(
            "First Threshold Space '{0}' is not a valid threshold space".format(
                first_threshold_space
            )
        )

    if second_threshold_space not in threshold_spaces:
        raise InputParameterException(
            "Second Threshold Space '{0}' is not a valid threshold space".format(
                second_threshold_space
            )
        )

    if first_comparison not in comparisons:
        raise InputParameterException(
            "First comparison '{0}' is not a valid comparison type".format(
                first_comparison
            )
        )

    if second_comparison not in comparisons:
        raise InputParameterException(
            "second comparison '{0}' is not a valid comparison type".format(
                second_comparison
            )
        )

    if max_segment_length > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "The max segment length cannot exceed {}.".format(
                settings.MAX_SEGMENT_LENGTH
            )
        )

    segment_indexes = []
    start_index = windowed_threshold_segmenter(
        input_data[:, 0]
        if keep_partial_segment
        else input_data[:-max_segment_length, 0],
        index=0,
        threshold_type=first_comparison,
        vt_threshold=first_vt_threshold,
        threshold_space_width=threshold_space_width,
        threshold_space=first_threshold_space,
    )

    while start_index is not None:
        start_looking = start_index + min_segment_length - threshold_space_width
        stop_looking = start_index + max_segment_length
        end_index = windowed_threshold_segmenter(
            input_data[start_looking:stop_looking, 1],
            index=0,
            threshold_type=second_comparison,
            vt_threshold=second_vt_threshold,
            threshold_space_width=threshold_space_width,
            threshold_space=second_threshold_space,
        )

        if end_index is not None:
            end_index += start_looking + threshold_space_width
            segment_indexes.append([start_index, end_index])
        else:
            end_index = start_index + max_segment_length - 1
            if end_index > input_data.shape[0] - 1:
                end_index = input_data.shape[0] - 1
            if drop_over == False:
                segment_indexes.append([start_index, end_index])

        start_index = windowed_threshold_segmenter(
            input_data[:, 0]
            if keep_partial_segment
            else input_data[:-max_segment_length, 0],
            index=end_index + 1,
            threshold_type=first_comparison,
            vt_threshold=first_vt_threshold,
            threshold_space_width=threshold_space_width,
            threshold_space=first_threshold_space,
        )

    return segment_indexes


def thresholding(value, threshold, threshold_type):
    if threshold_type == "max":
        return value >= threshold
    if threshold_type == "min":
        return value <= threshold


def windowed_threshold_segmenter(
    data_stream,
    index=0,
    threshold_type="max",
    vt_threshold=1000,
    threshold_space_width=10,
    threshold_space="std",
):

    for i in range(index, len(data_stream) - threshold_space_width):

        if threshold_space == "variance":
            segment_value = np.var(data_stream[i : i + threshold_space_width])

        elif threshold_space == "std":
            segment_value = np.std(data_stream[i : i + threshold_space_width])

        elif threshold_space == "sum":
            segment_value = data_stream[i : i + threshold_space_width].sum()

        elif threshold_space == "absolute sum":
            segment_value = np.abs(data_stream[i : i + threshold_space_width]).sum()

        elif threshold_space == "absolute avg":
            segment_value = np.abs(data_stream[i : i + threshold_space_width]).mean()

        if thresholding(segment_value, vt_threshold, threshold_type):
            return i

    return None
