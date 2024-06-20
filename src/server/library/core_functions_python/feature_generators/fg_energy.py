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

from numpy import square
from pandas import DataFrame


def average_energy(input_data, columns, **kwargs):
    """
    Average Energy.

    1) Calculate the element-wise square of the input columns.
    2) Sum the squared components across each column for the total energy per sample.
    3) Take the average of the sum of squares to get the average energy.

    Args:
        input_data: input DataFrame.

        columns:  List of str; The `columns` represents a list of all
                  column names on which `average_energy` is to be found.

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        Dataframe

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                             'Class': ['Crawling'] * 20,
                             'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                       Class  Rep Subject  accelx  accely  accelz
                0   Crawling    0     s01       1       0       1
                1   Crawling    0     s01      -2       9      -2
                2   Crawling    0     s01      -3       5       3
                3   Crawling    0     s01       1      -5      -1
                4   Crawling    0     s01       2      -9       2
                5   Crawling    0     s01       5       0       5
                6   Crawling    0     s01       2       9       2
                7   Crawling    0     s01      -2       5      -2
                8   Crawling    1     s01      -3      -5      -3
                9   Crawling    1     s01      -1      -9       1
                10  Crawling    1     s01       1       0       1
                11  Crawling    1     s01      -3       9       3
                12  Crawling    1     s01      -4       5       4
                13  Crawling    1     s01       1      -5       1
                14  Crawling    1     s01       2      -9       2
                15  Crawling    1     s01       6       0       6
                16  Crawling    1     s01       2       9       2
                17  Crawling    1     s01      -3       5      -3
                18  Crawling    1     s01      -2      -5      -2
                19  Crawling    1     s01      -1      -9      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Average Energy"],
             params = {"group_columns": ['Subject', 'Class', 'Rep']},
             function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0000_AvgEng
            0  Crawling    0     s01            52.75
            1  Crawling    1     s01            60.00
    """
    results = {}
    results["AvgEng"] = []

    energy = square(input_data[columns]).sum().sum()
    average = energy / float(len(input_data))
    results["AvgEng"].append(average)

    return DataFrame.from_dict(results)


average_energy_contracts = {
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


def total_energy(input_data, columns, **kwargs):
    """
    Total Energy.

    1) Calculate the element-wise square of the input columns.
    2) Sum the energy values over all streams to get the total energy.

    Args:
        input_data: input DataFrame.

        columns:  List of str; The `columns` represents a list of all column names
                 on which total energy is to be found.

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        Dataframe

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20,
                               'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                       Class  Rep Subject  accelx  accely  accelz
                0   Crawling    0     s01       1       0       1
                1   Crawling    0     s01      -2       9      -2
                2   Crawling    0     s01      -3       5       3
                3   Crawling    0     s01       1      -5      -1
                4   Crawling    0     s01       2      -9       2
                5   Crawling    0     s01       5       0       5
                6   Crawling    0     s01       2       9       2
                7   Crawling    0     s01      -2       5      -2
                8   Crawling    1     s01      -3      -5      -3
                9   Crawling    1     s01      -1      -9       1
                10  Crawling    1     s01       1       0       1
                11  Crawling    1     s01      -3       9       3
                12  Crawling    1     s01      -4       5       4
                13  Crawling    1     s01       1      -5       1
                14  Crawling    1     s01       2      -9       2
                15  Crawling    1     s01       6       0       6
                16  Crawling    1     s01       2       9       2
                17  Crawling    1     s01      -3       5      -3
                18  Crawling    1     s01      -2      -5      -2
                19  Crawling    1     s01      -1      -9      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Total Energy"],
             params = {"group_columns": ['Subject', 'Class', 'Rep']},
             function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0000_TotEng
            0  Crawling    0     s01              422
            1  Crawling    1     s01              720
    """
    results = {}
    results["TotEng"] = []

    # Feature: energy of input columns
    energy = square(input_data[columns]).sum().sum()
    results["TotEng"].append(energy)

    return DataFrame.from_dict(results)


total_energy_contracts = {
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
