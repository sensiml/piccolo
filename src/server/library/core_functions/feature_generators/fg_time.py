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
from library.core_functions import MAX_INT_16, MIN_INT_16
from pandas import DataFrame


def fg_time_signal_duration(
    input_data: DataFrame, columns: List[str], sample_rate: int, **kwargs
):
    """
    Duration of the signal. It is calculated by dividing the length of vector
    by the sampling rate.

    Args:
        sample_rate: float; Sampling rate
        columns: List of str; Set of columns on which to apply the feature generator

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
        >>> client.pipeline.add_feature_generator([{'name':'Duration of the Signal',
                                     'params':{"columns": ['accelx'] ,
                                               "sample_rate": 10
                                              }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
               Subject  gen_0001_accelxDurSignal
             0     s01                       0.5
    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "DurSignal",
        [sample_rate],
        fg_algorithms.fg_time_signal_duration_w,
    )


fg_time_signal_duration_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "sample_rate",
            "type": "numeric",
            "default": 100,
            "description": "Sample rate of the sensor data",
            "range": [1, 100000],
            "c_param": 0,
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


def fg_time_pct_time_over_zero(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Percentage of samples in the series that are positive.

    Args:
        columns: List of str; Set of columns on which to apply the feature generator

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> print df
            out:
               Subject     Class  Rep  accelx  accely  accelz
            0      s01  Crawling    1     377     569    4019
            1      s01  Crawling    1     357     594    4051
            2      s01  Crawling    1     333     638    4049
            3      s01  Crawling    1     340     678    4053
            4      s01  Crawling    1     372     708    4051
            5      s01  Crawling    1     410     733    4028
            6      s01  Crawling    1     450     733    3988
            7      s01  Crawling    1     492     696    3947
            8      s01  Crawling    1     518     677    3943
            9      s01  Crawling    1     528     695    3988
            10     s01  Crawling    1      -1    2558    4609
            11     s01   Running    1     -44   -3971     843
            12     s01   Running    1     -47   -3982     836
            13     s01   Running    1     -43   -3973     832
            14     s01   Running    1     -40   -3973     834
            15     s01   Running    1     -48   -3978     844
            16     s01   Running    1     -52   -3993     842
            17     s01   Running    1     -64   -3984     821
            18     s01   Running    1     -64   -3966     813
            19     s01   Running    1     -66   -3971     826
            20     s01   Running    1     -62   -3988     827
            21     s01   Running    1     -57   -3984     843

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns=['accelx', 'accely', 'accelz'],
                            group_columns=['Subject', 'Class', 'Rep'],
                            label_column='Class')
        >>> client.pipeline.add_feature_generator([{'name':'Percent Time Over Zero',
                                     'params':{"columns": ['accelx','accely','accelz'] }}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            out:
                Class  Rep Subject  gen_0001_accelxPctTimeOverZero  gen_0002_accelyPctTimeOverZero  gen_0003_accelzPctTimeOverZero
          0  Crawling    1     s01                        0.909091                             1.0                             1.0
          1   Running    1     s01                        0.000000                             0.0                             1.0



    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "PctTimeOverZero",
        [],
        fg_algorithms.fg_time_pct_time_over_zero_w,
    )


fg_time_pct_time_over_zero_contracts = {
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


def fg_time_pct_time_over_sigma(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Percentage of samples in the series that are above the sample mean + one sigma

    Args:
        columns: List of str; Set of columns on which to apply the feature generator

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> print df
            out:
               Subject     Class  Rep  accelx  accely  accelz
            0      s01  Crawling    1     377     569    4019
            1      s01  Crawling    1     357     594    4051
            2      s01  Crawling    1     333     638    4049
            3      s01  Crawling    1     340     678    4053
            4      s01  Crawling    1     372     708    4051
            5      s01  Crawling    1     410     733    4028
            6      s01  Crawling    1     450     733    3988
            7      s01  Crawling    1     492     696    3947
            8      s01  Crawling    1     518     677    3943
            9      s01  Crawling    1     528     695    3988
            10     s01  Crawling    1      -1    2558    4609
            11     s01   Running    1     -44   -3971     843
            12     s01   Running    1     -47   -3982     836
            13     s01   Running    1     -43   -3973     832
            14     s01   Running    1     -40   -3973     834
            15     s01   Running    1     -48   -3978     844
            16     s01   Running    1     -52   -3993     842
            17     s01   Running    1     -64   -3984     821
            18     s01   Running    1     -64   -3966     813
            19     s01   Running    1     -66   -3971     826
            20     s01   Running    1     -62   -3988     827
            21     s01   Running    1     -57   -3984     843

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns=['accelx', 'accely', 'accelz'],
                            group_columns=['Subject', 'Class', 'Rep'],
                            label_column='Class')
        >>> client.pipeline.add_feature_generator([{'name':'Percent Time Over Sigma',
                                     'params':{"columns": ['accelx','accely','accelz'] }}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            out:
                Class  Rep Subject  gen_0001_accelxPctTimeOverSigma  gen_0002_accelyPctTimeOverSigma  gen_0003_accelzPctTimeOverSigma
          0  Crawling    1     s01                         0.181818                         0.090909                         0.090909
          1   Running    1     s01                         0.272727                         0.090909                         0.272727

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "PctTimeOverSigma",
        [],
        fg_algorithms.fg_time_pct_time_over_sigma_w,
    )


fg_time_pct_time_over_sigma_contracts = {
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


def fg_time_pct_time_over_second_sigma(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """
    Percentage of samples in the series that are above  the sample mean + two sigma

    Args:
        columns: List of str; Set of columns on which to apply the feature generator

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> print df
            out:
               Subject     Class  Rep  accelx  accely  accelz
            0      s01  Crawling    1     377     569    4019
            1      s01  Crawling    1     357     594    4051
            2      s01  Crawling    1     333     638    4049
            3      s01  Crawling    1     340     678    4053
            4      s01  Crawling    1     372     708    4051
            5      s01  Crawling    1     410     733    4028
            6      s01  Crawling    1     450     733    3988
            7      s01  Crawling    1     492     696    3947
            8      s01  Crawling    1     518     677    3943
            9      s01  Crawling    1     528     695    3988
            10     s01  Crawling    1      -1    2558    4609
            11     s01   Running    1     -44   -3971     843
            12     s01   Running    1     -47   -3982     836
            13     s01   Running    1     -43   -3973     832
            14     s01   Running    1     -40   -3973     834
            15     s01   Running    1     -48   -3978     844
            16     s01   Running    1     -52   -3993     842
            17     s01   Running    1     -64   -3984     821
            18     s01   Running    1     -64   -3966     813
            19     s01   Running    1     -66   -3971     826
            20     s01   Running    1     -62   -3988     827
            21     s01   Running    1     -57   -3984     843

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns=['accelx', 'accely', 'accelz'],
                            group_columns=['Subject', 'Class', 'Rep'],
                            label_column='Class')
        >>> client.pipeline.add_feature_generator([{'name':'Percent Time Over Second Sigma',
                                     'params':{"columns": ['accelx','accely','accelz'] }}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            out:
                  Class  Rep Subject  gen_0001_accelxPctTimeOver2ndSigma  gen_0002_accelyPctTimeOver2ndSigma  gen_0003_accelzPctTimeOver2ndSigma
            0  Crawling    1     s01                                 0.0                            0.090909                            0.090909
            1   Running    1     s01                                 0.0                            0.000000                            0.000000


    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "PctTimeOver2ndSigma",
        [],
        fg_algorithms.fg_time_pct_time_over_second_sigma_w,
    )


fg_time_pct_time_over_second_sigma_contracts = {
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


def fg_time_pct_time_over_threshold(
    input_data: DataFrame, columns: List[str], threshold: int = 0, **kwargs
):
    """
    Percentage of samples in the series that are above threshold

    Args:
        columns: List of str; Set of columns on which to apply the feature generator

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> print df
            out:
               Subject     Class  Rep  accelx  accely  accelz
            0      s01  Crawling    1     377     569    4019
            1      s01  Crawling    1     357     594    4051
            2      s01  Crawling    1     333     638    4049
            3      s01  Crawling    1     340     678    4053
            4      s01  Crawling    1     372     708    4051
            5      s01  Crawling    1     410     733    4028
            6      s01  Crawling    1     450     733    3988
            7      s01  Crawling    1     492     696    3947
            8      s01  Crawling    1     518     677    3943
            9      s01  Crawling    1     528     695    3988
            10     s01  Crawling    1      -1    2558    4609
            11     s01   Running    1     -44   -3971     843
            12     s01   Running    1     -47   -3982     836
            13     s01   Running    1     -43   -3973     832
            14     s01   Running    1     -40   -3973     834
            15     s01   Running    1     -48   -3978     844
            16     s01   Running    1     -52   -3993     842
            17     s01   Running    1     -64   -3984     821
            18     s01   Running    1     -64   -3966     813
            19     s01   Running    1     -66   -3971     826
            20     s01   Running    1     -62   -3988     827
            21     s01   Running    1     -57   -3984     843

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns=['accelx', 'accely', 'accelz'],
                            group_columns=['Subject', 'Class', 'Rep'],
                            label_column='Class')
        >>> client.pipeline.add_feature_generator([{'name':'Percent Time Over Threshold',
                                     'params':{"columns": ['accelx','accely','accelz'] }}])
        >>> results, stats = client.pipeline.execute()


    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "PctTimeOverThreshold",
        [threshold],
        fg_algorithms.fg_time_pct_time_over_threshold_w,
    )


fg_time_pct_time_over_threshold_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "threshold",
            "type": "int",
            "default": 0,
            "description": "Offset to check for percent time over",
            "range": [MIN_INT_16, MAX_INT_16],
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
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def fg_time_avg_time_over_threshold(
    input_data: DataFrame, columns: List[str], threshold: int = 0, **kwargs
):
    """
    Average of the time spent above threshold for all times crossed.

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "PctTimeAvgTimeOverThreshold",
        [threshold],
        fg_algorithms.fg_time_avg_time_over_threshold_w,
    )


fg_time_avg_time_over_threshold_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "threshold",
            "type": "int",
            "default": 0,
            "description": "Offset to check for percent time over",
            "c_param": 0,
            "range": [MIN_INT_16, MAX_INT_16],
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


def fg_time_abs_pct_time_over_threshold(
    input_data: DataFrame, columns: List[str], threshold: int = 0, **kwargs
):
    """
    Percentage of absolute value of samples in the series that are above the offset

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "AbsPctTimeOverThreshold",
        [threshold],
        fg_algorithms.fg_time_abs_pct_time_over_threshold_w,
    )


fg_time_abs_pct_time_over_threshold_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "threshold",
            "type": "int",
            "default": 0,
            "c_param": 0,
            "description": "Threshold to check for percent time over",
            "range": [MIN_INT_16, MAX_INT_16],
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
