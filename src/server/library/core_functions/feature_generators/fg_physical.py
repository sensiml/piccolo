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
from numpy import sqrt, square
from pandas import DataFrame


def magnitude(input_data, input_columns):
    """Computes the magnitude of each column in a dataframe"""
    return sqrt(square(input_data[input_columns]).sum(axis=1))


def fg_physical_average_movement_intensity(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """
    Calculates the average movement intensity defined by:

    .. math::

        \\frac{1}{N}\\sum_{i=1}^{N} \\sqrt{x_{i}^2 + y_{i}^2 + .. n_{i}^2}

    Args:
        columns (list):  list of columns to calculate average movement intensity.

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
        >>> client.pipeline.add_feature_generator([{'name':'Average of Movement Intensity',
                                     'params':{ "columns": ['accelx','accely','accelz'] }}])
        >>> result, stats = client.pipeline.execute()

        >>> print(result)
            out:
              Subject  gen_0000_AvgInt
            0     s01         9.0


    """

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data,
        columns,
        "AvgInt",
        [],
        fg_algorithms.fg_physical_average_movement_intensity_w,
    )


fg_physical_average_movement_intensity_contracts = {
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


def fg_physical_variance_movement_intensity(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """
    Variance of movement intensity

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
        >>> client.pipeline.add_feature_generator([{'name':'Variance of Movement Intensity',
                                     'params':{ "columns": ['accelx','accely','accelz'] }}])
        >>> result, stats = client.pipeline.execute()

        >>> print(result)
            out:
              Subject  gen_0000_VarInt
            0     s01         3.082455
    """

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data,
        columns,
        "VarInt",
        [],
        fg_algorithms.fg_physical_variance_movement_intensity_w,
    )


fg_physical_variance_movement_intensity_contracts = {
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


def fg_physical_average_signal_magnitude_area(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """
    Average signal magnitude area.

    .. math::

        \\frac{1}{N}\\sum_{i=1}^{N} {x_{i} + y_{i} + .. n_{i}}

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
        >>> client.pipeline.add_feature_generator([{'name':"Average Signal Magnitude Area",
                                     'params':{ "columns": ['accelx','accely','accelz'] }}])
        >>> result, stats = client.pipeline.execute()

        >>> print(result)
            out:
              Subject  gen_0000_AvgSigMag
                s01          13.0

    """

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data,
        columns,
        "AvgSigMag",
        [],
        fg_algorithms.fg_physical_average_signal_magnitude_area_w,
    )


fg_physical_average_signal_magnitude_area_contracts = {
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
