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

from pandas import DataFrame


def fg_cross_column_min_max_ratio_two_columns(
    input_data, columns, saturate=10, **kwargs
):
    """Compute the ratio between two columns. Computes the location of the
    max value for each of the two columns, whichever one larger, it computes the ratio
    between the two at that index.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use

    Returns:
        DataFrame: feature vector ratio of two columns
    """
    feature_name = "".join([c[0] + c[-1] for c in columns]) + "_cross_min_max_ratio"

    column1 = columns[0]
    column2 = columns[1]
    index_col1 = input_data[column1].values.argmin()
    index_col2 = input_data[column2].values.argmin()

    val_col1 = input_data[column1].values[index_col1]
    val_col2 = input_data[column2].values[index_col2]

    if val_col1 > val_col2:
        index = index_col1
    else:
        index = index_col2

    y = input_data[column1].values[index] / input_data[column2].values[index]

    if y > saturate:
        y = saturate
    if y < -saturate:
        y = -saturate

    return DataFrame([y], columns=[feature_name])


fg_cross_column_min_max_ratio_two_columns_contracts = {
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
            "name": "saturate",
            "type": "int",
            "default": 10,
            "description": "Above this value result is set to saturation level",
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


def cross_column_correlation_phase_shift(
    input_data, columns, phase=0, sample_frequency=5, **kwargs
):
    """Compute the correlation of the slopes between two columns with a phase shift between the
    correlation computation.

    Args:
        input_data (DataFrame): input data
        columns (list of strings): name of the sensor streams to use
        phase (int): number of samples to shift by
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

    y = float(sum((slope_col1[1 + phase : -1] * slope_col2[1 : -1 - phase]) > 0)) / (
        len(slope_col1) - (2 + phase)
    )

    return DataFrame([y], columns=[feature_name])


cross_column_correlation_phase_shift_columns_contracts = {
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
            "name": "normalized",
            "type": "bool",
            "default": False,
            "description": "Normalize by the largest of the two means",
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
