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
from library.core_functions.segmenters.sg_general_threshold import (
    general_threshold_segmentation_start_end,
)
from library.core_functions.segmenters.utils import process_segment_results
from library.core_functions.utils.utils import handle_group_columns
from library.exceptions import InputParameterException
from pandas import DataFrame


@handle_group_columns
# developer documentation
# input_data: Pandas dataframe
# group_columns (list[str]): list of column names to use for grouping.
def max_min_threshold(
    input_data: DataFrame,
    column_of_interest: str,
    group_columns: List[str],
    max_segment_length: int = 200,
    min_segment_length: int = 100,
    first_vt_threshold: int = 1000,
    threshold_space: str = "std",
    second_vt_threshold: int = 1000,
    threshold_space_width: int = 10,
    return_segment_index: bool = False,
):
    """
    This is a max min threshold segmentation algorithm which transforms a window
    of the data stream of size threshold_space_width into threshold space. This function
    transfer the `input_data` and `group_column` from the previous pipeline block.


    The threshold space can be computed as standard deviation, sum, absolute sum, absolute
    average and variance. The vt threshold is then compared against the
    calculated value with a comparison type of >= for the start of the segment
    and <= for the end of the segment. This algorithm is a two pass
    detection, the first pass detects the start of the segment, the second pass
    detects the end of the segment.

    Args:
        column_of_interest (str): name of the stream to use for segmentation
        max_segment_length (int): number of samples in the window (default is 100)
        min_segment_length: The smallest segment allowed.
        threshold_space_width (float): number of samples to check for being above the
          vt_threshold before forgetting segment.
        threshold_space (std): Threshold transformation space. (std, sum, absolute sum, variance, absolute avg)
        first_vt_threshold (int):vt_threshold value to begin detecting a segment
        second_vt_threshold (int):vt_threshold value to detect a segments end.
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

        >>> client.pipeline.add_transform("Max Min Threshold Segmentation",
                           params={ "column_of_interest": 'accelx',
                                    "max_segment_length": 5,
                                    "min_segment_length": 5,
                                    "threshold_space_width": 3,
                                    "threshold_space": 'std',
                                    "first_vt_threshold": 0.05,
                                    "second_vt_threshold": 0.05,
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
    if max_segment_length > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "The max segment length cannot exceed {}.".format(
                settings.MAX_SEGMENT_LENGTH
            )
        )

    input_stream = input_data[column_of_interest].values
    if len(input_stream.shape) > 1:
        input_stream = np.concatenate(input_stream)
    seg_beg_end_list = max_min_threshold_segmentation_start_end(
        input_stream,
        max_segment_length=max_segment_length,
        min_segment_length=min_segment_length,
        first_vt_threshold=first_vt_threshold,
        threshold_space=threshold_space,
        second_vt_threshold=second_vt_threshold,
        threshold_space_width=threshold_space_width,
    )

    return process_segment_results(
        input_data,
        seg_beg_end_list,
        group_columns,
        return_segment_index=return_segment_index,
    )


max_min_threshold_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "no_display": True},
        {
            "name": "column_of_interest",
            "type": "str",
            "streams": True,
            "number_of_elements": 1,
            "display_name": "Column Of Interest",
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
            "display_name": "Maximum Segment Length",
            "description": "maximum number of samples a segment can have",
            "default": 200,
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
            "name": "threshold_space",
            "type": "str",
            "default": "std",
            "display_name": "Threshold Space",
            "description": "space to transform signal into to compare against the vertical thresholds",
            "options": [
                {"name": "std"},
                {"name": "absolute sum"},
                {"name": "sum"},
                {"name": "variance"},
                {"name": "absolute avg"},
            ],
        },
        {
            "name": "first_vt_threshold",
            "type": "float",
            "default": 1000,
            "c_param": 4,
            "display_name": "Initial Vertical Threshold",
            "description": "the segment starts when the threshold space is above this value",
        },
        {
            "name": "second_vt_threshold",
            "type": "float",
            "default": 1000,
            "c_param": 5,
            "display_name": "Second Vertical Threshold",
            "description": "the segment ends when the threshold space is below this value",
        },
        {
            "name": "return_segment_index",
            "type": "boolean",
            "default": False,
            "no_display": True,
        },
    ],
    "output_contract": [
        {"name": "output_data", "type": "DataFrame", "metadata_columns": ["SegmentID"]}
    ],
}


def max_min_threshold_segmentation_start_end(
    input_data,
    max_segment_length=100,
    min_segment_length=50,
    first_vt_threshold=1000,
    threshold_space="std",
    second_vt_threshold=1000,
    threshold_space_width=10,
):

    input_streams = np.vstack((input_data, input_data)).T
    return general_threshold_segmentation_start_end(
        input_streams,
        max_segment_length=max_segment_length,
        min_segment_length=min_segment_length,
        first_vt_threshold=first_vt_threshold,
        first_comparison="max",
        first_threshold_space=threshold_space,
        second_vt_threshold=second_vt_threshold,
        second_comparison="min",
        second_threshold_space=threshold_space,
        threshold_space_width=threshold_space_width,
    )
