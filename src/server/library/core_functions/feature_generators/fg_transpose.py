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
import pandas as pd
from django.conf import settings
from pandas import DataFrame


def fg_transpose_signal(
    input_data: DataFrame, columns: List[str], cutoff: int = 1, **kwargs
):
    """
    Turns raw signal into a feature over a range.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns data frame containing transpose range values of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8],
                               [0, 6, 3], [-2, 8, 7],
                               [2, 9, 6]], columns= ['accelx', 'accely', 'accelz'])
        >>> df
            out:
               accelx  accely  accelz
            0      -3       6       5
            1       3       7       8
            2       0       6       3
            3      -2       8       7
            4       2       9       6
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Transpose Range"],
                params = {"group_columns": [], 'range':2},
                 function_defaults={"columns":['accelx']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                   accelx_range0  accelx_range1
            0         -3             3
    """

    if cutoff > input_data["data"].shape[1]:
        extend_array = np.zeros(
            (input_data["data"].shape[0], cutoff - input_data["data"].shape[1])
        )
        for index in range(input_data["data"].shape[0]):
            extend_array[index] += input_data["data"][index, -1]
        input_data["data"] = np.concatenate((input_data["data"], extend_array), axis=1)

    results = []
    feature_names = []
    for col in columns:
        feature_names.extend(
            [str(col) + "_signal_bin_{0:06}".format(x) for x in range(cutoff)]
        )
        col_index = input_data["columns"].index(col)
        results.extend(input_data["data"][col_index, :cutoff])

    return pd.DataFrame([results], columns=feature_names)


fg_transpose_signal_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
            "num_columns": -1,
        },
        {
            "name": "cutoff",
            "type": "int",
            "default": 1,
            "range": [1, settings.MAX_SEGMENT_LENGTH],
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
    "output_contract": [
        {
            "name": "output_data",
            "type": "DataFrame",
            "family": True,
            "output_formula": "params['cutoff']*len(params['columns'])",
        }
    ],
}


def fg_interleave_signal(
    input_data: DataFrame, columns: List[str], cutoff: int = 1, delta: int = 1, **kwargs
):
    """
    Turns raw signal into a feature over a range. Interleaves the signal while doing the transform
    so the feature is stacked. Useful for feeding raw data into a CNN without additional reshaping.


    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns data frame containing transpose range values of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8],
                               [0, 6, 3], [-2, 8, 7],
                               [2, 9, 6]], columns= ['accelx', 'accely', 'accelz'])
        >>> df
            out:
               accelx  accely  accelz
            0      -3       6       5
            1       3       7       8
            2       0       6       3
            3      -2       8       7
            4       2       9       6
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Interleave"],
                params = {"group_columns": [], 'range':2},\
                 function_defaults={"columns":['accelx','accely]})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                   accelx_range0  accely_range0 accelx_range1 accely_range1
            0         -3             6                3             7
    """
    if cutoff > input_data["data"].shape[1]:
        extend_array = np.zeros(
            (input_data["data"].shape[0], cutoff - input_data["data"].shape[1])
        )
        for index in range(input_data["data"].shape[0]):
            extend_array[index] += input_data["data"][index, -1]
        input_data["data"] = np.concatenate((input_data["data"], extend_array), axis=1)

    feature_names = []
    for i in range(0, cutoff, delta):
        feature_names.extend(
            [
                "bin_{0:06}_{1}_interleave".format(i * len(columns) + index, col)
                for index, col in enumerate(columns)
            ]
        )

    column_indexes = [input_data["columns"].index(c) for c in columns]
    interleave_array = np.empty((cutoff * len(column_indexes) // delta), dtype=np.int16)
    for index, col_index in enumerate(column_indexes):
        interleave_array[index :: len(column_indexes)] = input_data["data"][col_index][
            :cutoff:delta
        ]

    interleave_df = pd.DataFrame(interleave_array.reshape(1, -1), columns=feature_names)

    return interleave_df


fg_interleave_signal_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Columns on which to apply the feature generator",
            "num_columns": -1,
        },
        {
            "name": "cutoff",
            "type": "int",
            "default": 1,
            "c_param": 0,
            "description": "The total length of the signal to use as part of the feature extractor.",
            "range": [1, settings.MAX_SEGMENT_LENGTH],
        },
        {
            "name": "delta",
            "type": "int",
            "default": 1,
            "c_param": 1,
            "description": "Dowsample signal by selecting every delta data point.",
            "range": [1, 32],
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
            "name": "output_data",
            "type": "DataFrame",
            "family": True,
            "output_formula": "math.ceil(params['cutoff']/params['delta'])*len(params['columns'])",
        }
    ],
}
