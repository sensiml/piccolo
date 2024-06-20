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

from numpy import divide, float64, mean, std
from pandas import DataFrame, concat


def signal_duration(input_data, sample_rate, columns, **kwargs):
    """
    Duration of the signal. It is calculated by dividing the length of vector
    by the sampling rate.

    Args:
        input_data: DataFrame;

        sample_rate: float; Sampling rate

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                             'Class': ['Crawling'] * 20 ,
                             'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                   Class  Rep Subject  accelx
            0   Crawling    0     s01       1
            1   Crawling    0     s01      -2
            2   Crawling    0     s01      -3
            3   Crawling    0     s01       1
            4   Crawling    0     s01       2
            5   Crawling    0     s01       5
            6   Crawling    0     s01       2
            7   Crawling    0     s01      -2
            8   Crawling    1     s01      -3
            9   Crawling    1     s01      -1
            10  Crawling    1     s01       1
            11  Crawling    1     s01      -3
            12  Crawling    1     s01      -4
            13  Crawling    1     s01       1
            14  Crawling    1     s01       2
            15  Crawling    1     s01       6
            16  Crawling    1     s01       2
            17  Crawling    1     s01      -3
            18  Crawling    1     s01      -2
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Duration of the Signal"],
                    params = {"group_columns": ['Subject', 'Class', 'Rep']},
                    function_defaults={"columns":['accelx'],
                                       'sample_rate' : 5})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxDurSignal
            0  Crawling    0     s01                       1.6
            1  Crawling    1     s01                       2.4
    """
    sample_rate = float64(sample_rate)
    result = DataFrame()
    for col in columns:
        feature = len(input_data[col]) * 1 / sample_rate
        feature_name = col + "DurSignal"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


signal_duration_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "sample_rate",
            "type": "numeric",
            "handle_by_set": True,
            "description": "Sample rate of the sensor data",
        },
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


def pct_time_over_zero(input_data, columns, **kwargs):
    """
    Percentage of samples in the series that are positive.

    Args:
        input_data: DataFrame

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20 ,
                              'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                   Class  Rep Subject  accelx
            0   Crawling    0     s01       1
            1   Crawling    0     s01      -2
            2   Crawling    0     s01      -3
            3   Crawling    0     s01       1
            4   Crawling    0     s01       2
            5   Crawling    0     s01       5
            6   Crawling    0     s01       2
            7   Crawling    0     s01      -2
            8   Crawling    1     s01      -3
            9   Crawling    1     s01      -1
            10  Crawling    1     s01       1
            11  Crawling    1     s01      -3
            12  Crawling    1     s01      -4
            13  Crawling    1     s01       1
            14  Crawling    1     s01       2
            15  Crawling    1     s01       6
            16  Crawling    1     s01       2
            17  Crawling    1     s01      -3
            18  Crawling    1     s01      -2
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Percent Time Over Zero"],
                    params = {"group_columns": ['Subject', 'Class', 'Rep']},
                    function_defaults={"columns":['accelx'], 'sample_rate' : 5})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxPctTimeOverZero
            0  Crawling    0     s01                        0.625000
            1  Crawling    1     s01                        0.416667
    """
    result = DataFrame()
    for col in columns:
        feature = divide(
            sum([int(k > 0) for k in input_data[col]]), float(len(input_data[col]))
        )
        feature_name = col + "PctTimeOverZero"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


pct_time_over_zero_contracts = {
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


def pct_time_over_sigma(input_data, columns, **kwargs):
    """
    Percentage of samples in the series that are above the sample mean + one sigma

    Args:
        input_data: DataFrame

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                    'Class': ['Crawling'] * 20 ,
                    'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                   Class  Rep Subject  accelx
            0   Crawling    0     s01       1
            1   Crawling    0     s01      -2
            2   Crawling    0     s01      -3
            3   Crawling    0     s01       1
            4   Crawling    0     s01       2
            5   Crawling    0     s01       5
            6   Crawling    0     s01       2
            7   Crawling    0     s01      -2
            8   Crawling    1     s01      -3
            9   Crawling    1     s01      -1
            10  Crawling    1     s01       1
            11  Crawling    1     s01      -3
            12  Crawling    1     s01      -4
            13  Crawling    1     s01       1
            14  Crawling    1     s01       2
            15  Crawling    1     s01       6
            16  Crawling    1     s01       2
            17  Crawling    1     s01      -3
            18  Crawling    1     s01      -2
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Percent Time Over Sigma"],
                    params = {"group_columns": ['Subject', 'Class', 'Rep']},
                    function_defaults={"columns":['accelx'], 'sample_rate' : 5})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxPctTimeOverSigma
            0  Crawling    0     s01                         0.125000
            1  Crawling    1     s01                         0.083333
    """
    result = DataFrame()
    for col in columns:
        feature = divide(
            sum(
                [
                    int(k > mean(input_data[col]) + std(input_data[col]))
                    for k in input_data[col]
                ]
            ),
            float(len(input_data[col])),
        )
        feature_name = col + "PctTimeOverSigma"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


pct_time_over_sigma_contracts = {
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


def pct_time_over_second_sigma(input_data, columns, **kwargs):
    """
    Percentage of samples in the series that are above  the sample mean + two sigma

    Args:
        input_data: DataFrame

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20 ,
                              'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                   Class  Rep Subject  accelx
            0   Crawling    0     s01       1
            1   Crawling    0     s01      -2
            2   Crawling    0     s01      -3
            3   Crawling    0     s01       1
            4   Crawling    0     s01       2
            5   Crawling    0     s01       5
            6   Crawling    0     s01       2
            7   Crawling    0     s01      -2
            8   Crawling    1     s01      -3
            9   Crawling    1     s01      -1
            10  Crawling    1     s01       1
            11  Crawling    1     s01      -3
            12  Crawling    1     s01      -4
            13  Crawling    1     s01       1
            14  Crawling    1     s01       2
            15  Crawling    1     s01       6
            16  Crawling    1     s01       2
            17  Crawling    1     s01      -3
            18  Crawling    1     s01      -2
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Percent Time Over Second Sigma"],
                    params = {"group_columns": ['Subject', 'Class', 'Rep']},
                    function_defaults={"columns":['accelx'], 'sample_rate' : 5})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  accelxPctTimeOver2ndSigma
            0  Crawling    0     s01                   0.000000
            1  Crawling    1     s01                   0.083333
    """
    result = DataFrame()
    for col in columns:
        feature = divide(
            sum(
                [
                    int(k > mean(input_data[col]) + 2 * std(input_data[col]))
                    for k in input_data[col]
                ]
            ),
            float(len(input_data[col])),
        )
        feature_name = col + "PctTimeOver2ndSigma"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


pct_time_over_second_sigma_contracts = {
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
