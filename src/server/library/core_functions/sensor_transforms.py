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
from datamanager.datasegments import (
    get_datasegment_col_indexes,
    get_datasegments_num_cols,
)
from library.core_functions.utils.utils import transform_column_name


def tr_absolute_average(input_data, input_columns):
    """
    Computes the absolute average of a signal across the input_columns
    streams.

    Args:
        input_data: DataFrame containing the time series data
        input_columns: sensor streams to use in computing the magnitude

    Returns:
        The input DataFrame with an additional column containing the per-sample
        absolute average of the desired input_columns
    """

    column_name = transform_column_name(
        "AbsAverage", input_columns, input_data[0]["columns"]
    )

    col_indexes = get_datasegment_col_indexes(input_data, input_columns)

    for seg in input_data:
        seg["data"] = np.vstack(
            (
                np.abs(seg["data"], seg["data"][col_indexes])
                .mean(axis=0)
                .astype(np.int32)
            )
        )
        seg["columns"] += [column_name]

    return input_data


tr_absolute_average_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
    ],
    "output_contract": [{"name": "AbsAverage", "type": "DataFrame"}],
}


def tr_average(input_data, input_columns):
    """
    Computes the average of a signal across the input_columns streams.

    Args:
        input_data: DataFrame containing the time series data
        input_columns: sensor streams to use in computing the average

    Returns:
        The input DataFrame with an additional column containing the per-sample
        average of the desired input_columns
    """

    column_name = transform_column_name(
        "Average", input_columns, input_data[0]["columns"]
    )

    col_indexes = get_datasegment_col_indexes(input_data, input_columns)

    for seg in input_data:
        seg["data"] = np.vstack(
            (seg["data"], seg["data"][col_indexes].mean(axis=0).astype(np.int32))
        )
        seg["columns"] += [column_name]

    return input_data


tr_average_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
    ],
    "output_contract": [
        {
            "name": "Average",
            "type": "DataFrame",
        }
    ],
}


def tr_magnitude(input_data, input_columns):
    """
    Computes the magnitude (square sum) of a signal across the input_columns
    streams.

    Args:
        input_columns (list[str]): sensor streams to use in computing the magnitude

    Returns:
        The input DataFrame with an additional column containing the per-sample
        magnitude of the desired input_columns
    """

    column_name = transform_column_name(
        "Magnitude", input_columns, input_data[0]["columns"]
    )
    col_indexes = get_datasegment_col_indexes(input_data, input_columns)
    get_datasegments_num_cols(input_data)

    # TODO: This is for backwards compatibility
    dtype = input_data[0]["data"].dtype

    for segment in input_data:
        segment["columns"] += [column_name]

        # additional logic is to fix rounding difference between python and c
        magnitude_column = (
            np.sqrt(np.square(segment["data"][col_indexes]).sum(axis=0))
            / len(input_columns)
            + 0.5
        ).astype(dtype)

        segment["data"] = np.vstack(
            (
                segment["data"],
                magnitude_column,
            )
        )

    return input_data


tr_magnitude_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
    ],
    "output_contract": [{"name": "Magnitude", "type": "DataFrame"}],
}
