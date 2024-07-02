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


def filter_extreme_values(
    input_data, input_columns, min_bound, max_bound, signal_min_max_parameters={}
):
    """
    Filters sensor streams removing samples that contain values outside bounds.
    User can specify a global min_bound and max_bound to act on all input_columns,
    or use signal_min_max_parameters to customize min and max bounds per column.

    Args:
        input_data (DataFrame): Dataframe to be filtered
        input_columns (list): List of column names to be acted on.
        min_bound (int): global min bound
        max_bound (int): global max bound
        signal_min_max_parameters (dict): Dictionary of per-column maximums
            and per-column minimums. This parameter is optional. If it is not passed,
            the global min_bound and max_bound will be used for all input columns.

    Returns:
        df_out (DataFrame): the new data frame with data rows removed if they contained
            a value outside minimums and maximums.
        signal_min_max_params (dict): If 'signal_min_max_parameters' = {}, it will take
            the same min and max from the global min_bound and max_bound for each selected column.


    Examples:

        Using global min_bound and max_bound

        >>> from pandas import DataFrame
        df = DataFrame([[-100, -200, -300], [3, 7, 8], [0, 6, 90],
                        [-2, 8, 7], [8, 9, 6], [8, 9, 6], [100, 200, 300]],
                        columns=['AccelerometerX', 'AccelerometerY', 'AccelerometerZ'])
        >>> df['Subject'] = 's01'
        >>> client.pipeline.set_input_data('test_data', df, force = True)
        >>> client.pipeline.add_transform('Filter Extreme Values',
                                        params={'input_columns]:['AccelerometerX',
                                                                'AccelerometerY',
                                                                'AccelerometerZ'],
                                        'min_bound' : -100,
                                        'max_bound' : 100})
        >>> result, stats = client.pipeline.execute()
        >>> result
            Out:
                AccelerometerX  AccelerometerY  AccelerometerZ  Subject
            1                3               7              8       s01
            2                0               6             90       s01
            3               -2               8              7       s01
            4                8               9              6       s01
            5                8               9              6       s01


        Using signal_min_max_parameters

        >>> client.pipeline.reset()
        >>> min_max_param = {'maximums': {'AccelerometerX': 400,
                                            'AccelerometerY': 90,
                                            'AccelerometerZ': 500},
                            'minimums': {'AccelerometerX': 0,
                                            'AccelerometerY': 0,
                                            'AccelerometerZ': -100}}
        >>> client.pipeline.set_input_data('test_data', df, force = True)
        >>> client.pipeline.add_transform('Filter Extreme Values',
                                        params={'input_columns':['AccelerometerX',
                                                                'AccelerometerY',
                                                                'AccelerometerZ'],
                                        'min_bound' : -100,
                                        'max_bound' : 100,
                                        'signal_min_max_parameters': min_max_param})
            result, stats = client.pipeline.execute()
            result
            Out:

                AccelerometerX  AccelerometerY  AccelerometerZ  Subject
            1                3               7               8      s01
            2                8               9               6      s01
            3                8               9               6      s01

    """

    # if per-column mins and maxes are not provided, use global min_bound and max_bound
    if not signal_min_max_parameters:
        signal_min_max_parameters = {}
        signal_min_max_parameters["maximums"] = {}
        signal_min_max_parameters["minimums"] = {}
        for col in input_columns:
            signal_min_max_parameters["maximums"][col] = max_bound
            signal_min_max_parameters["minimums"][col] = min_bound

    for col in input_columns:
        input_data = input_data[
            input_data[col] < signal_min_max_parameters["maximums"][col]
        ]
        input_data = input_data[
            input_data[col] > signal_min_max_parameters["minimums"][col]
        ]

    input_data = input_data.reset_index(drop=True)
    return input_data, signal_min_max_parameters


filter_extreme_values_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list"},
        {"name": "min_bound", "type": "int"},
        {"name": "max_bound", "type": "int"},
        {"name": "signal_min_max_parameters", "type": "dict", "default": {}},
    ],
    "output_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "signal_min_max_parameters", "type": "list", "persist": True},
    ],
}
