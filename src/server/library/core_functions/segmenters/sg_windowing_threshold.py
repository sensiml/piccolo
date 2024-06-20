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

windowing_threshold_contracts = {
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
            "name": "window_size",
            "type": "int",
            "display_name": "Window Size",
            "description": "number of samples in the segment",
            "default": 200,
            "c_param": 1,
        },
        {
            "name": "offset",
            "type": "int",
            "default": 0,
            "display_name": "Offset",
            "description": "Offset from anchor point to start of segment.",
            "c_param": 2,
        },
        {
            "name": "vt_threshold",
            "type": "float",
            "default": 1000,
            "c_param": 3,
            "display_name": "Vertical Threshold",
            "description": "threshold above which a segment will be identified",
        },
        {
            "name": "threshold_space_width",
            "type": "int",
            "default": 25,
            "c_param": 4,
            "display_name": "Threshold Space Width",
            "description": "the size of the window to transform into threshold space",
        },
        {
            "name": "comparison",
            "type": "str",
            "default": "maximum",
            "display_name": "Comparison",
            "description": "the comparison between threshold space and vertical threshold (>=, <=)",
            "options": [{"name": "maximum"}, {"name": "minimum"}],
        },
        {
            "name": "threshold_space",
            "type": "str",
            "options": [
                {"name": "std"},
                {"name": "absolute sum"},
                {"name": "sum"},
                {"name": "variance"},
                {"name": "absolute avg"},
            ],
            "default": "std",
            "display_name": "Threshold Space",
            "description": "space to transform signal into",
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


@handle_group_columns
# developer documentation
# input_data: Pandas dataframe
# group_columns (list[str]): list of column names to use for grouping.
def windowing_threshold(
    input_data: DataFrame,
    column_of_interest: str,
    group_columns: List[str],
    window_size: int = 100,
    offset: int = 0,
    vt_threshold: int = 1000,
    comparison: str = "maximum",
    threshold_space_width: int = 10,
    threshold_space: str = "std",
    return_segment_index: bool = False,
):
    """
    This function transfer the `input_data` and `group_column` from the previous pipeline block. This
    is a single pass threshold segmentation algorithm which transforms a window of the data stream
    that defined with 'threshold_space_width' into threshold space. The threshold space can be
    computed as 'standard deviation'(std), 'sum', 'absolute sum', 'absolute average' and 'variance'.
    The vt threshold is then compared against the calculated value with a comparison type of >=.
    Once the threshold space is detected above the vt_threshold that becomes the anchor point.
    The segment starts at the index of the detected point minus a user specified offset. The end
    of the segment is immediately set to the window size.

    Args:
        column_of_interest (str): name of the stream to use for segmentation
        window_size (int): number of samples in the window (default is 100)
        offset (int): The offset from the anchor point and the start of the segment. for a offset of 0, the start of the window will start at the anchor point. ( default is 0)
        vt_threshold (int): vt_threshold value which determines the segment.
        threshold_space_width (int): Size of the threshold buffer.
        threshold_space (str): Threshold transformation space. (std, sum, absolute sum, variance, absolute avg)
        comparison (str): the comparison between threshold space and vertical threshold (>=, <=)
        return_segment_index (False): Set to true to see the segment indexes for start and end.

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

        >>> client.pipeline.add_transform("Windowing Threshold Segmentation",
                               params={"column_of_interest": 'accelx',
                                       "window_size": 5,
                                       "offset": 0,
                                       "vt_threshold": 0.05,
                                       "threshold_space_width": 4,
                                       "threshold_space": 'std',
                                       "return_segment_index": False
                                      })

        >>> results, stats = client.pipeline.execute()
        >>> print results
            out:
                      Class  Rep  SegmentID Subject  accelx  accely  accelz
               0   Crawling    1          0     s01     377     569    4019
               1   Crawling    1          0     s01     357     594    4051
               2   Crawling    1          0     s01     333     638    4049
               3   Crawling    1          0     s01     340     678    4053
               4   Crawling    1          0     s01     372     708    4051
               5   Crawling    1          1     s01     410     733    4028
               6   Crawling    1          1     s01     450     733    3988
               7   Crawling    1          1     s01     492     696    3947
               8   Crawling    1          1     s01     518     677    3943
               9   Crawling    1          1     s01     528     695    3988
               10   Running    1          0     s01     -44   -3971     843
               11   Running    1          0     s01     -47   -3982     836
               12   Running    1          0     s01     -43   -3973     832
               13   Running    1          0     s01     -40   -3973     834
               14   Running    1          0     s01     -48   -3978     844
               15   Running    1          1     s01     -52   -3993     842
               16   Running    1          1     s01     -64   -3984     821
               17   Running    1          1     s01     -64   -3966     813
               18   Running    1          1     s01     -66   -3971     826
               19   Running    1          1     s01     -62   -3988     827

    """

    input_stream = input_data[column_of_interest].values
    seg_beg_end_list = windowing_threshold_segmentation_start_end(
        input_stream,
        window_size=window_size,
        offset=offset,
        vt_threshold=vt_threshold,
        threshold_space_width=threshold_space_width,
        threshold_space=threshold_space,
        comparison=comparison,
    )

    return process_segment_results(
        input_data,
        seg_beg_end_list,
        group_columns,
        return_segment_index=return_segment_index,
    )


def windowing_threshold_segmentation_start_end(
    input_data,
    window_size=100,
    offset=0,
    vt_threshold=1000,
    threshold_space_width=10,
    comparison="maximum",
    threshold_space="std",
):

    threshold_spaces = ["std", "variance", "sum", "absolute sum", "absolute avg"]
    valid_comparison = ["maximum", "minimum"]

    if window_size < offset + threshold_space_width:
        raise InputParameterException(
            "The window size must be greater than the offset + threshold space width"
        )

    if threshold_space not in threshold_spaces:
        raise InputParameterException(
            "Threshold Space '{0}' is not a valid threshold space".format(
                threshold_space
            )
        )

    if comparison not in valid_comparison:
        raise InputParameterException(
            "Comparison '{0}' is not a valid".format(comparison)
        )

    if window_size > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "The window size cannot exceed {}.".format(settings.MAX_SEGMENT_LENGTH)
        )

    """Core algorithm of the variance-based segmenter."""
    segment_indexes = []
    start_index = windowed_threshold_segmenter(
        input_data,
        offset,
        window_size=window_size,
        vt_threshold=vt_threshold,
        threshold_space_width=threshold_space_width,
        threshold_space=threshold_space,
        comparison=comparison,
        offset=offset,
    )

    while start_index is not None:
        start_index = start_index - offset
        segment_indexes.append([start_index, start_index + window_size - 1])

        start_index = windowed_threshold_segmenter(
            input_data,
            start_index + window_size + offset,
            window_size=window_size,
            vt_threshold=vt_threshold,
            threshold_space_width=threshold_space_width,
            threshold_space=threshold_space,
            comparison=comparison,
            offset=offset,
        )

    return segment_indexes


def windowed_threshold_segmenter(
    data_stream,
    index,
    window_size=100,
    vt_threshold=1000,
    threshold_space_width=10,
    threshold_space="std",
    comparison="maximum",
    offset=0,
):
    pass

    N = len(data_stream)
    for i in range(index, np.min([N, N - window_size + offset])):

        if threshold_space == "variance":
            value = np.var(data_stream[i : i + threshold_space_width])

        elif threshold_space == "std":
            value = np.std(data_stream[i : i + threshold_space_width])

        elif threshold_space == "sum":
            value = data_stream[i : i + threshold_space_width].sum()

        elif threshold_space == "absolute sum":
            value = np.abs(data_stream[i : i + threshold_space_width]).sum()

        elif threshold_space == "absolute avg":
            value = np.abs(data_stream[i : i + threshold_space_width]).mean()
        else:
            raise Exception("Threshold space not supported!")

        if comparison == "maximum":
            if value >= vt_threshold:
                return i
        else:
            if value <= vt_threshold:
                return i

    return None
