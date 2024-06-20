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
from datamanager.datasegments import (
    get_datasegment_col_indexes,
    get_datasegments_columns,
)
from pandas import DataFrame


class InputDataException(Exception):
    pass


def high_pass_filter(data_stream, alpha):
    y = np.zeros(data_stream.shape[0])

    y[0] = data_stream[0]

    for i in range(1, data_stream.shape[0]):
        y[i] = int(y[i - 1] + alpha * (data_stream[i] - y[i - 1]))

    y[0] = 0

    return y


def tr_high_pass_filter(
    input_data: DataFrame, input_columns: List[str], alpha: float
) -> DataFrame:
    """
    This is a simple IIR Filter that is useful for removing drift from sensors by subtracting the attentuated running average.

    .. math::
        y_{i}= y_{i-1} + \\alpha (x_{i} - y_{i-1})

    Args:
        input_data: DataFrame containing the time series data
        input_columns: sensor streams to apply  the filter to
        alpha: attenuation coefficient

    Returns:
        input data after having been passed through the IIR filter
    """

    for segment in input_data:
        for column in input_columns:
            col_index = segment["columns"].index(column)
            input_data["data"][col_index] = high_pass_filter(
                input_data["data"][col_index], alpha
            )

    return input_data


tr_high_pass_filter_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
        {
            "name": "alpha",
            "type": "float",
            "c_param": 0,
            "range": [0, 1],
            "default": 0.9,
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "c_contract": {"buffer": 2, "params": ["alpha"], "params_type": ["float"]},
}


def symmetric_ma_filter(data, filter_order=3):

    ma_filtered = np.zeros(len(data))

    for i in range(len(data)):
        if i < filter_order:
            ma_filtered[i] = data[i : i + filter_order + 1].mean()
        elif i > (len(data) - filter_order):
            ma_filtered[i] = data[i - filter_order :].mean()
        else:
            ma_filtered[i] = data[i - filter_order : i + filter_order + 1].mean()

    return np.round(ma_filtered).astype(np.int32)


def st_moving_average(
    input_data: DataFrame,
    group_columns: List[str],
    input_columns: List[str],
    filter_order: int = 1,
) -> DataFrame:
    """
    Performs a symmetric moving average filter on the input column,
    creates a new column with the filtered data.

    Args:
        input_data: DataFrame containing the time series data.
        group_columns: columns to group data by before processing.
        input_column: sensor stream to apply moving average filter on.
        filter order: the number of samples to average to the left and right.

    Returns:
        input data after having been passed through symmetric moving average filter
    """

    for column in input_columns:
        if column not in get_datasegments_columns(input_data):
            raise InputDataException("Column {} not in input data!".format(column))

    col_indexes = get_datasegment_col_indexes(input_data, input_columns)

    for segment in input_data:
        for col_index in col_indexes:
            segment["data"][col_index] = symmetric_ma_filter(
                segment["data"][col_index], filter_order=filter_order
            )

    return input_data


st_moving_average_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "input_columns", "type": "list"},
        {
            "name": "filter_order",
            "type": "int",
            "default": 1,
            "c_param": 0,
            "range": [1, 32],
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "c_contract": {"buffer": None, "params": ["filter_order"], "params_type": ["int"]},
}


def downsample_filter_by_average(data, filter_length=3):

    downsampled = np.zeros(
        (data.shape[0], data.shape[1] // filter_length), dtype=np.int32
    )

    for i, index in enumerate(np.arange(0, data.shape[1], filter_length)):
        if i >= downsampled.shape[1]:
            break
        else:
            downsampled[:, i] = (
                data[:, index : index + filter_length].mean(axis=1).astype(np.int32)
            )

    return downsampled


def downsample_filter_by_decimation(data, filter_length=3):

    indexes = np.arange(0, data.shape[1], filter_length)

    return data[:, indexes]


def streaming_downsample_by_averaging(
    input_data: DataFrame,
    group_columns: List[str],
    input_columns: List[str],
    filter_length: int = 1,
) -> DataFrame:
    """
    Downsample the entire dataframe into a dataframe of size `filter_length` by taking the average over the samples within the filter length.

    Args:
        input_data: dataframe
        group_columns (a list): List of columns on which grouping is to be done.
                             Each group will go through downsampling one at a time
        input_columns: List of columns to be downsampled
        filter_length: Number of samples in each new filter length

    Returns:
        DataFrame: The downsampled dataframe.

    """

    for column in input_columns:
        if column not in get_datasegments_columns(input_data):
            raise InputDataException("Column {} not in input data!".format(column))

    for seg in input_data:
        seg["data"] = downsample_filter_by_average(
            seg["data"], filter_length=filter_length
        )

    return input_data


streaming_downsample_by_averaging_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "input_columns", "type": "list"},
        {
            "name": "filter_length",
            "type": "int",
            "default": 1,
            "c_param": 0,
            "range": [1, 32],
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "c_contract": {
        "buffer": None,
        "params": ["filter_length"],
        "params_type": ["int"],
        "streaming_filter_length": "filter_length",
    },
}


def streaming_downsample_by_decimation(
    input_data: DataFrame,
    group_columns: List[str],
    input_columns: List[str],
    filter_length: int = 1,
) -> DataFrame:
    """
    Decrease the sample rate by a factor of filter_length, this will only keep one samples for every length of the filter.

    Args:
        input_data: dataframe
        columns: List of columns to be downsampled
        group_columns (a list): List of columns on which grouping is to be done.
                             Each group will go through downsampling one at a time
        filter_length: integer; Number of samples in each new filter length

    Returns:
        DataFrame: The downsampled dataframe.

    Examples:
        >>> from pandas import DataFrame
        >>> df = DataFrame([[3, 3], [4, 5], [5, 7], [4, 6], [3, 1],
                            [3, 1], [4, 3], [5, 5], [4, 7], [3, 6]],
                            columns=['accelx', 'accely'])
        >>> df
        Out:
               accelx  accely
            0       3       3
            1       4       5
            2       5       7
            3       4       6
            4       3       1
            5       3       1
            6       4       3
            7       5       5
            8       4       7
            9       3       6
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force = True)
        >>> client.pipeline.add_transform('Streaming Downsample by Decimation', params={'group_columns':[],\
                                                            'columns' : ['accelx', 'accely'],\
                                                            'filter_length' : 5 })
        >>> results, stats = client.pipeline.execute()
        >>> print results
            Out:
                    accelx  accely
                0     3       3
                1     3       1
                2     3       6
    """

    for column in input_columns:
        if column not in get_datasegments_columns(input_data):
            raise InputDataException("Column {} not in input data!".format(column))

    for seg in input_data:
        seg["data"] = downsample_filter_by_decimation(
            seg["data"], filter_length=filter_length
        )

    return input_data


streaming_downsample_by_decimation_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "input_columns", "type": "list"},
        {
            "name": "filter_length",
            "type": "int",
            "default": 1,
            "c_param": 0,
            "range": [1, 32],
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "c_contract": {
        "buffer": None,
        "params": ["filter_length"],
        "params_type": ["int"],
        "streaming_filter_length": "filter_length",
    },
}
