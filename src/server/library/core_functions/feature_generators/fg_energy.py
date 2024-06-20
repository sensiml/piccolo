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
from pandas import DataFrame


def fg_energy_average_energy(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Average Energy.

    1) Calculate the element-wise square of the input columns.
    2) Sum the squared components across each column for the total energy per sample.
    3) Take the average of the sum of squares to get the average energy.

    .. math::

        \\frac{1}{N}\\sum_{i=1}^{N}x_{i}^2+y_{i}^2+..n_{i}^2


    Args:
        columns:  List of str; The `columns` represents a list of all
                  column names on which `average_energy` is to be found.

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                               [-2, 8, 7], [2, 9, 6]],
                               columns= ['accelx', 'accely', 'accelz'])
        >>> df['Subject'] = 's01'
        >>> print(df)
            out:
               accelx  accely  accelz Subject
            0      -3       6       5     s01
            1       3       7       8     s01
            2       0       6       3     s01
            3      -2       8       7     s01
            4       2       9       6     s01

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject'])
        >>> client.pipeline.add_feature_generator([{'name':'Average Energy',
                                     'params':{ "columns": ['accelx','accely','accelz'] }}])
        >>> result, stats = client.pipeline.execute()

        >>> print(result)
            out:
              Subject  gen_0000_AvgEng
            0     s01             95.0

    """

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data, columns, "AvgEng", [], fg_algorithms.fg_energy_average_energy_w
    )


fg_energy_average_energy_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def fg_energy_total_energy(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Total Energy.

    1) Calculate the element-wise abs sum of the input columns.
    2) Sum the energy values over all streams to get the total energy.

    Args:
        columns:  List of str; The `columns` represents a list of all column names
                 on which total energy is to be found.

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                               [-2, 8, 7], [2, 9, 6]],
                               columns= ['accelx', 'accely', 'accelz'])
        >>> df['Subject'] = 's01'
        >>> print df
            out:
               accelx  accely  accelz Subject
            0      -3       6       5     s01
            1       3       7       8     s01
            2       0       6       3     s01
            3      -2       8       7     s01
            4       2       9       6     s01

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject'])
        >>> client.pipeline.add_feature_generator([{'name':'Total Energy',
                                     'params':{ "columns": ['accelx','accely','accelz'] }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0000_TotEng
            0     s01            475.0


    """

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data, columns, "TotEng", [], fg_algorithms.fg_energy_total_energy_w
    )


fg_energy_total_energy_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def fg_energy_average_demeaned_energy(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """
    Average Demeaned Energy.

    1) Calculate the element-wise demeaned by its column average of the input columns.
    2) Sum the squared components across each column for the total demeaned energy per sample.
    3) Take the average of the sum of squares to get the average demeaned energy.

    Args:
        columns:  List of str; The `columns` represents a list of all
                  column names on which `average_energy` is to be found.

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                               [-2, 8, 7], [2, 9, 6]],
                               columns= ['accelx', 'accely', 'accelz'])
        >>> df['Subject'] = 's01'
        >>> print df
            out:
               accelx  accely  accelz Subject
            0      -3       6       5     s01
            1       3       7       8     s01
            2       0       6       3     s01
            3      -2       8       7     s01
            4       2       9       6     s01

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject'])
        >>> client.pipeline.add_feature_generator([{'name':'Average Demeaned Energy',
                                     'params':{ "columns": ['accelx','accely','accelz'] }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0000_AvgDemeanedEng
            0     s01                     9.52

    """

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data,
        columns,
        "AvgDemeanedEng",
        [],
        fg_algorithms.fg_energy_average_demeaned_energy_w,
    )


fg_energy_average_demeaned_energy_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}
