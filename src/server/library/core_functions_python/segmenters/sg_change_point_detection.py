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


change_point_detection_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "no_display": True},
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "no_display": True,
        },
        {
            "name": "threshold",
            "type": "float",
            "default": 500,
            "c_param": 1,
            "display_name": "Threshold",
            "description": "threshold above which a segment will be identified",
        },
        {
            "name": "window_size",
            "type": "int",
            "default": 250,
            "display_name": "Window Size",
            "description": "size of your window",
        },
        {
            "name": "delta_size",
            "type": "int",
            "default": 250,
            "display_name": "Delta Size",
            "description": "size of your window slide",
        },
        {
            "name": "coefficients",
            "type": "list",
            "default": [],
            "display_name": "Coefficients",
        },
        {
            "name": "distance",
            "type": "str",
            "default": "L1",
            "options": [{"name": "L1"}, {"name": "LSUP"}],
        },
        {
            "name": "return_segment_index",
            "type": "boolean",
            "default": False,
            "no_display": True,
        },
        {
            "name": "history",
            "type": "int",
            "default": 2,
            "display_name": "Stored History",
            "description": "Size of history to store.",
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
def change_point_detection(
    input_data,
    group_columns,
    threshold=400,
    window_size=250,
    delta_size=250,
    coefficients=None,
    distance="L1",
    history=2,
    return_segment_index=False,
):
    """ """

    input_data = input_data.sort_values(by="SegmentID").reset_index(drop=True)

    seg_beg_end_list = change_point_segmentation_start_end(
        input_data,
        threshold=threshold,
        coefficients=coefficients,
        distance=distance,
        history=history,
    )

    M = []

    for i in range(len(seg_beg_end_list)):
        if return_segment_index:
            temp_df = (
                input_data[group_columns]
                .iloc[seg_beg_end_list[i][0] : seg_beg_end_list[i][0] + 1]
                .copy()
            )
            temp_df["SegmentID"] = i
            temp_df["Seg_Begin"] = seg_beg_end_list[i][0] * delta_size + window_size
            temp_df["Seg_End"] = seg_beg_end_list[i][1] * delta_size + window_size
        else:
            temp_df = input_data.ix[
                seg_beg_end_list[i][0] : seg_beg_end_list[i][1]
            ].copy()
            temp_df["SegmentID"] = i

        M.append(temp_df)

    if M:
        return pd.concat(M, axis=0)
    else:
        return pd.DataFrame()


def change_point_segmentation_start_end(
    input_data, threshold=1000, coefficients=None, distance="L1", history=2
):
    """Core algorithm of the variance-based segmenter."""
    segment_indexes = []
    index = 1
    stored_index = 0
    segment_indexes = None

    while index < len(input_data):
        if check_threshold(
            input_data,
            index,
            stored_index,
            threshold,
            coefficients=coefficients,
            distance=distance,
        ):
            if segment_indexes is None:
                segment_indexes = [[0, index]]

            elif segment_indexes[-1][1] + 1 < index - 1:
                segment_indexes.append([segment_indexes[-1][1] + 1, index - 1])

            stored_index = index

        elif (index - stored_index) == history:
            stored_index = index

        index += 1

    # add the final one
    if stored_index != len(input_data) - 1:
        segment_indexes.append([stored_index, len(input_data) - 1])

    return segment_indexes


def check_threshold(
    input_data, index, stored_index, threshold, coefficients=None, distance="L1"
):
    total_diff = 0
    gen_cols = [c for c in input_data.columns if c[:4] == "gen_"]

    for i in range(1, int(gen_cols[-1].split("_")[1]) + 1):
        sub_gen_cols = [x for x in gen_cols if int(x.split("_")[1]) == i]

        if len(sub_gen_cols) > 3:
            y1 = moving_average(
                np.hstack(input_data.loc[stored_index][sub_gen_cols].values)
            )
            y2 = moving_average(np.hstack(input_data.loc[index][sub_gen_cols].values))
        else:
            y1 = np.hstack(input_data.loc[stored_index][sub_gen_cols].values)
            y2 = np.hstack(input_data.loc[index][sub_gen_cols].values)

        value = abs(y1 - y2).sum()

        if coefficients and len(coefficients) < i:
            value *= coefficients[i]

        if distance == "L1":
            total_diff += value
        elif distance == "LSUP":
            total_diff = max(total_diff, value)

    if total_diff > threshold:
        return True

    return False


def moving_average(a, n=3, cutoff=40):

    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]

    ret = ret[n - 1 :] / n

    ret[ret > cutoff] = cutoff
    return ret
