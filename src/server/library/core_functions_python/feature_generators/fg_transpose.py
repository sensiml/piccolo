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


def fg_transpose_signal(input_data, columns, cutoff, **kwargs):
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

    assert len(input_data) > cutoff

    transpose_dict = []
    for col in columns:
        feature_name = col + "signal"
        for index in range(cutoff):
            transpose_dict.append(
                (
                    feature_name + "_bin_{0:06}".format(index),
                    input_data[col].iloc[index],
                )
            )

    df = DataFrame(transpose_dict, columns=["idx", "count"])
    df = df.set_index("idx", drop=True)
    df.index.name = None

    return df.T


fg_transpose_signal_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "cutoff", "type": "int", "default": 1},
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}
