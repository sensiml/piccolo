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

import library.core_functions.fg_algorithms as fg_algorithms
from library.core_functions import MAX_INT_16, MIN_INT_16
from library.exceptions import InputParameterException
from numpy import median
from pandas import DataFrame


def fg_cross_column_max_column(input_data: DataFrame, columns: List[str], **kwargs):
    """Returns the index of the column with the max value for each segment.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector with index of max column.
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_max_col"
    max_column = 1
    max_value = input_data["data"][input_data["columns"].index(columns[0])].max()
    for index, col in enumerate(columns[1:]):
        col_index = input_data["columns"].index(col)
        tmp_value = input_data["data"][col_index].max()
        if tmp_value > max_value:
            max_value = tmp_value
            max_column = index + 2

    return DataFrame([max_column], columns=[feature_name])


fg_cross_column_max_column_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": -1,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_abs_max_column(input_data: DataFrame, columns: List[str], **kwargs):
    """Returns the index of the column with the max abs value for each segment.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector with index of max abs value column.
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_max_col"
    max_column = 1
    max_value = input_data["data"][input_data["columns"].index(columns[0])].abs().max()
    for index, col in enumerate(columns[1:]):
        col_index = input_data["columns"].index(col)
        tmp_value = max(
            abs(input_data["data"][col_index].max()),
            abs(input_data["data"][col_index].min()),
        )
        if tmp_value > max_value:
            max_value = tmp_value
            max_column = index + 2

    return DataFrame([max_column], columns=[feature_name])


fg_cross_column_abs_max_column_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": -1,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_min_column(input_data: DataFrame, columns: List[str], **kwargs):
    """Returns the index of the column with the min value for each segment.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector with index of max abs value column.
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_min_col"
    min_column = 1
    min_value = input_data["data"][input_data["columns"].index(columns[0])].min()

    for index, col in enumerate(columns[1:]):
        col_index = input_data["columns"].index(col)
        tmp_value = input_data["data"][col_index].min()
        if tmp_value < min_value:
            min_value = tmp_value
            min_column = index + 2

    return DataFrame([min_column], columns=[feature_name])


fg_cross_column_min_column_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": -1,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_min_max_difference_two_columns(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """Compute the min max difference between two columns. Computes the location of the
    min value for each of the two columns, whichever one larger, it computes the difference
    between the two at that index.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector difference of two columns
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_min_max_diff"

    col_1 = input_data["columns"].index(columns[0])
    col_2 = input_data["columns"].index(columns[1])

    index_col1 = input_data["data"][col_1].argmin()
    index_col2 = input_data["data"][col_2].argmin()

    val_col1 = input_data["data"][col_1][index_col1]
    val_col2 = input_data["data"][col_2][index_col2]

    if val_col1 > val_col2:
        index = index_col1
    else:
        index = index_col2

    y = input_data["data"][col_1][index] - input_data["data"][col_2][index]
    return DataFrame([y], columns=[feature_name])


fg_cross_column_min_max_difference_two_columns_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 2,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_mean_difference(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """Compute the mean difference between two columns.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector mean difference
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_mean_diff"

    col_1 = input_data["columns"].index(columns[0])
    col_2 = input_data["columns"].index(columns[1])

    mean_col1 = input_data["data"][col_1].mean()
    mean_col2 = input_data["data"][col_2].mean()

    y = mean_col1 - mean_col2

    return DataFrame([y], columns=[feature_name])


fg_cross_column_mean_difference_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 2,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_median_difference(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """Compute the median difference between two columns.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector median difference
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_median_diff"

    col_1 = input_data["columns"].index(columns[0])
    col_2 = input_data["columns"].index(columns[1])

    median_col1 = median(input_data["data"][col_1])
    median_col2 = median(input_data["data"][col_2])

    y = median_col1 - median_col2

    return DataFrame([y], columns=[feature_name])


fg_cross_column_median_difference_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 2,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [
        {
            "name": "data_out",
            "type": "DataFrame",
            "family": False,
            "scratch_buffer": {"type": "segment_size"},
        }
    ],
}


def fg_cross_column_peak_location_difference(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """Computes the location of the maximum value for each column and then finds the difference
       between those two points.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector mean difference
    """
    feature_name = (
        "".join([c[0] + c[-1] for c in columns]) + "_cross_peak_location_difference"
    )

    col_1 = input_data["columns"].index(columns[0])
    col_2 = input_data["columns"].index(columns[1])

    loc_col1 = input_data["data"][col_1].argmax()
    loc_col2 = input_data["data"][col_2].argmax()

    y = loc_col1 - loc_col2

    return DataFrame([y], columns=[feature_name])


fg_cross_column_peak_location_difference_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 2,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_p2p_difference(input_data: DataFrame, columns: List[str], **kwargs):
    """Compute the max value for each column, then subtract the first column for the second.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector mean difference
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_p2p_diff"

    col_1 = input_data["columns"].index(columns[0])
    col_2 = input_data["columns"].index(columns[1])

    val_col1 = input_data["data"][col_1].max()
    val_col2 = input_data["data"][col_2].max()

    y = val_col1 - val_col2

    return DataFrame([y], columns=[feature_name])


fg_cross_column_p2p_difference_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 2,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_correlation(
    input_data: DataFrame, columns: List[str], sample_frequency: int = 1, **kwargs
):
    """Compute the correlation of the slopes between two columns.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use
        sample_frequency (int): frequency to sample correlation at. Default 1 which is every sample

    Returns:
        DataFrame: feature vector mean difference
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_corr"

    slope_col1 = (
        input_data[columns[0]].values[sample_frequency:]
        - input_data[columns[0]].values[:-sample_frequency]
    )
    slope_col2 = (
        input_data[columns[1]].values[sample_frequency:]
        - input_data[columns[1]].values[:-sample_frequency]
    )

    y = float(sum((slope_col1 * slope_col2) > 0)) / len(slope_col1)

    return DataFrame([y], columns=[feature_name])


fg_cross_column_correlation_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 2,
        },
        {
            "name": "sample_frequency",
            "type": "int",
            "default": 1,
            "description": "Sampling frequency for correlation comparison",
            "range": [1, 10],
            "c_param": 0,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_mean_crossing_rate(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """Compute the crossing rate of column 2 of over the mean of column 1

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use (requires 2 inputs)

    Returns:
        DataFrame: feature vector mean crossing rate
    """

    if len(columns) != 2:
        raise InputParameterException(
            "Cross column mean crossing rate requires two columns"
        )

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data,
        columns,
        "CCMeanCrossing",
        [],
        fg_algorithms.fg_cross_column_mean_crossing_rate_w,
    )


fg_cross_column_mean_crossing_rate_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 2,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}


def fg_cross_column_mean_crossing_rate_with_offset(
    input_data: DataFrame, columns: List[str], offset: int = 0, **kwargs
):
    """Compute the crossing rate of column 2 of over the mean of column 1

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use (requires 2 inputs)

    Returns:
        DataFrame: feature vector mean crossing rate
    """

    if len(columns) != 2:
        raise InputParameterException(
            "Cross column mean crossing rate requires two columns"
        )

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data,
        columns,
        "CCMeanCrossingOffset",
        [offset],
        fg_algorithms.fg_cross_column_mean_crossing_rate_with_offset_w,
    )


fg_cross_column_mean_crossing_rate_with_offset_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 2,
        },
        {
            "name": "offset",
            "type": "int",
            "default": 0,
            "description": "Offset from the mean to use",
            "range": [MIN_INT_16, MAX_INT_16],
            "c_param": 0,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": False}],
}
