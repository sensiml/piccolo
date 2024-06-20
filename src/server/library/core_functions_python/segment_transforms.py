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

from scipy.interpolate import interp1d
import pandas as pd
from pandas import DataFrame, concat
import numpy as np
from library.exceptions import InputParameterException


def interpolation(temp_ts, win_lenght, interp_kind):
    """
    This function is part of scale segment implementation. It is used to
    scale segments in time series domain.
    """
    n = len(temp_ts)
    y = temp_ts[0:n]
    x = np.linspace(0, n - 1, num=n, endpoint=True)
    f2 = interp1d(x, y, kind=interp_kind)
    xnew = np.linspace(0, n - 1, num=win_lenght, endpoint=True)
    return f2(xnew)


def tr_segment_horizontal_scale(
    input_data, input_columns, new_length, interp_kind, group_columns
):
    """
    the horizontal scale_segment function interpolate a function to a specific size

    Args:
        input_data: <Dataframe>; input data
        input_columns: <List>; List of columns to be scaled
        group_columns: <List>; List of columns on which grouping is to be done.
                             Each group will go through scale one at a time


    Returns:
        The interpolated dataframe for each segment for input_columns.
    """

    df_list = []
    results_groups = input_data.groupby(group_columns, sort=False)
    for indx, df in results_groups:
        df_temp = DataFrame([], columns=group_columns)
        for column in input_columns:
            temp = df[column].values
            temp = interpolation(temp, new_length, interp_kind).astype(int)
            df_temp[column] = temp
        for non_column in group_columns:
            unique_item = df[non_column].unique().tolist()
            if len(unique_item) > 1:
                raise InputParameterException("Segmentations are not uniquely grouped.")

            df_temp[non_column] = unique_item[0]
        df_list.append(df_temp)

    df_norm = concat(df_list)
    df_norm.reset_index(inplace=True, drop=True)

    return df_norm


tr_segment_horizontal_scale_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list"},
        {"name": "new_length", "type": "int", "default": None},
        {
            "name": "interp_kind",
            "type": "str",
            "default": "linear",
            "options": [{"name": "linear"}],
        },
        {"name": "group_columns", "type": "list", "element_type": "str"},
    ],
    "output_contract": [
        {
            "name": "df_out",
            "type": "DataFrame",
            "scratch_buffer": {"type": "segment_size"},
        }
    ],
}


def trimseries(input_data, number_of_samples, group_columns):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "number_of_samples", "type": "int"},
    {"name": "group_columns", "type": "list", "element_type": "str"}],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "description": "Truncate all event data streams to the same number of samples."
    }
    """

    if type(input_data) == type(pd.DataFrame()):
        trimmed = input_data.groupby(group_columns, sort=False).head(number_of_samples)
    else:
        trimmed = input_data[0:number_of_samples]
    return trimmed.reindex()
