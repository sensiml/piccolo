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

import pandas as pd
from django.conf import settings
from library.exceptions import InputParameterException
from pandas import DataFrame


def tr_cascade_windowing(
    input_data: DataFrame,
    group_columns: List[str],
    delta: int = 250,
    window_size: int = 250,
    return_segment_index: bool = False,
):
    """
    This function transfer the `input_data` and `group_column` from the previous pipeline block.
    It groups 'input_data' by using group_column. It divides each group into windows of size `window_size`.
    The argument `delta` represents the extent of overlap.

    Args:
        window_size: Size of each window
        delta: The number of samples to increment. It is similar to overlap.
          If delta is equal to window size, this means no overlap.
        return_segment_index (False): Set to true to see the segment indexes
          for start and end. Note: This should only be used for visualization not
          pipeline building.
    Returns:
        DataFrame: Returns dataframe with `SegmentID` column added to the original dataframe.

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

        >>> client.pipeline.add_transform('Windowing',
                                        params={'window_size' : 5,
                                                'delta': 5})

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
    if window_size > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "The max window size cannot exceed {}.".format(settings.MAX_SEGMENT_LENGTH)
        )

    # For cascade windowing we want cascade from the initial window of each segment
    input_data["colFromIndex"] = input_data.index
    input_data.sort_values(group_columns + ["colFromIndex"], inplace=True)
    input_data.drop("colFromIndex", axis=1, inplace=True)
    input_data.reset_index(inplace=True, drop=True)
    grouped = input_data.groupby(group_columns, sort=False)

    M = []
    index = 0

    for key, value in grouped.size().items():

        if delta >= window_size:
            num_segments = (value - value % window_size) // delta
        else:
            num_segments = (value - window_size) // delta + 1

        num_rows = num_segments * window_size
        segments = []
        segments_index = []
        segment_begin = []
        segment_end = []

        for j in range(num_segments):
            segments.extend([j] * window_size)
            segments_index.extend(
                range(j * delta + index, j * delta + window_size + index)
            )
            if return_segment_index:
                segment_begin.extend([j * delta + index] * window_size)
                segment_end.extend([j * delta + index + window_size] * window_size)

        tmp_seg = {"CascadeID": segments, "Index": segments_index}

        if return_segment_index:
            tmp_seg["Seg_Begin"] = [x - index for x in segment_begin]
            tmp_seg["Seg_End"] = [x - index for x in segment_end]

        if isinstance(key, tuple):
            for key_index, group_column in enumerate(group_columns):
                tmp_seg[group_column] = [key[key_index]] * num_rows
        else:
            tmp_seg[group_columns[0]] = [key] * num_rows

        index += value

        M.append(pd.DataFrame(tmp_seg))

    windowed_df = pd.merge(
        input_data,
        pd.concat(M),
        left_index=True,
        right_on=["Index"],
        how="right",
        suffixes=["", "_"],
    )
    windowed_df.reset_index(inplace=True, drop=True)
    drop_columns = ["Index", "index"] + [x + "_" for x in group_columns]
    drop_columns = list(set(drop_columns).intersection(windowed_df.columns))
    windowed_df.drop(drop_columns, axis=1, inplace=True)
    windowed_df.CascadeID = windowed_df.CascadeID.astype(int)

    if return_segment_index:
        return (
            windowed_df[group_columns + ["Seg_Begin", "Seg_End", "CascadeID"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

    return windowed_df


tr_cascade_windowing_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "window_size", "type": "int", "default": 250, "c_param": 1},
        {"name": "delta", "type": "int", "default": 250, "c_param": 2},
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
