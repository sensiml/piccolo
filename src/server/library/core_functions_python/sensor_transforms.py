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
from numpy import diff, hstack

from library.core_functions.utils.utils import transform_column_name


def differentiate(data):
    return hstack((0, diff(data)))


def tr_first_derivative(input_data, input_columns):
    """
    Computes the first derivative of a single sensor input column.

    Args:
        input_data: DataFrame
        input_columns: list of the columns of which to calculate the first derivative

    Returns:
        The input DataFrame with an additional column containing the integer
        derivative of the desired input_column
    """

    for input_column in input_columns:
        column_name = transform_column_name(
            "DerivFst", input_column, input_data.columns
        )
        input_data[column_name] = np.round(
            differentiate(input_data[input_column])
        ).astype(int)

    return input_data


tr_first_derivative_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list"},
    ],
    "output_contract": [{"name": "input_data", "type": "DataFrame"}],
}


def tr_second_derivative(input_data, input_columns):
    """
    Computes the second derivative of a single sensor input column.

    Args:
        input_data: DataFrame
        input_column: list of the columns of which to calculate the second derivative

    Returns:
        The input DataFrame with an additional column containing the integer
        second derivative of the desired input_column.
    """

    for input_column in input_columns:
        column_name = transform_column_name(
            "DerivSec", input_column, input_data.columns
        )
        input_data[column_name] = np.round(
            differentiate(differentiate(input_data[input_column]))
        ).astype(int)

    return input_data


tr_second_derivative_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list"},
    ],
    "output_contract": [{"name": "input_data", "type": "DataFrame"}],
}
