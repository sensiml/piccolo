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

from pandas import concat


def tr_threshold_crossing_filter(
    input_data, group_columns, input_column, threshold=0.0
):
    """Filters out groups that do not cross the threshold at least once in the
    desired input column.

    Args:
        input_data (DataFrame): the input DataFrame
        group_columns (list[str]): set of columns that define the unique groups
        input_column (str): the name of the column to use for filtering
        threshold (float): the threshold (default is 0.0)

    Returns:
        DataFrame: The filtered DataFrame.
    """

    output = []

    grouped = input_data.groupby(group_columns, sort=False)
    for index, group in grouped:
        signal_min = group[input_column].min()
        signal_max = group[input_column].max()

        if signal_min < threshold < signal_max:
            output.append(group)

    if len(output) == 0:
        raise Exception("No groups cross the threshold. Try changing the threshold.")

    return concat(output)


tr_threshold_crossing_filter_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "input_column", "type": "str"},
        {"name": "threshold", "type": "float", "default": 0.0},
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}
