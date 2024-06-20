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


def fg_roc_mean_crossing_rate(
    input_data: DataFrame, columns: List[str], **kwargs
) -> DataFrame:
    """
    Calculates the rate at which the mean value is crossed for each specified column.
    Works with grouped data. The total number of mean value crossings are found
    and then the number is divided by the total number of samples to get
    the `mean_crossing_rate`.

    Args:
        input_data (DataFrame): The input data.
        columns (list of strings): A list of all column names on which `mean_crossing_rate` is to be found.

    Returns:
        DataFrame : Return the number of mean crossings divided by the length of the signal.

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

        >>> client.pipeline.add_feature_generator([{'name':'Mean Crossing Rate',
                                     'params':{"columns": ['accelx','accely', 'accelz']}
                                    }])

        >>> results, stats = client.pipeline.execute()
        >>> print results
            out:
                  Class  Rep Subject  gen_0001_accelxMeanCrossingRate  gen_0002_accelyMeanCrossingRate  gen_0003_accelzMeanCrossingRate
            0  Crawling    1     s01                         0.181818                         0.090909                         0.090909
            1   Running    1     s01                         0.090909                         0.454545                         0.363636

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "MeanCrossingRate",
        [],
        fg_algorithms.fg_roc_mean_crossing_rate_w,
    )


fg_roc_mean_crossing_rate_contracts = {
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
    "output_contract": [
        {
            "name": "output_data",
            "type": "DataFrame",
            "scratch_buffer": {"type": "segment_size"},
        }
    ],
}


def fg_roc_zero_crossing_rate(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Calculates the rate at which zero value is crossed for each specified column.
    The total number of zero crossings are found and then the number is divided
    by total number of samples to get the `zero_crossing_rate`.

    Args:
        columns:  The `columns` represents a list of all column names on which
                 `zero_crossing_rate` is to be found.

    Returns:
        A DataFrame of containing zero crossing rate

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Zero Crossing Rate',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxZeroCrossingRate  gen_0002_accelyZeroCrossingRate  gen_0003_accelzZeroCrossingRate
            0     s01                              0.6                              0.0                              0.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "ZeroCrossingRate",
        [],
        fg_algorithms.fg_roc_zero_crossing_rate_w,
    )


fg_roc_zero_crossing_rate_contracts = {
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
    "output_contract": [
        {
            "name": "output_data",
            "type": "DataFrame",
            "scratch_buffer": {"type": "segment_size"},
        }
    ],
}


def fg_roc_sigma_crossing_rate(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Calculates the rate at which standard deviation value (sigma) is crossed for
    each specified column. The total number of sigma crossings are found and then
    the number is divided by total number of samples to get the `sigma_crossing_rate`.

    Args:
        columns: The `columns` represents a list of all column names on which
                 `sigma_crossing_rate` is to be found.

    Returns:
        DataFrame : Return the sigma crossing rate.

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
        >>> client.pipeline.add_feature_generator([{'name':'Sigma Crossing Rate',
                                     'params':{"columns": ['accelx','accely', 'accelz']}
                                    }])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            out:
                  Class  Rep Subject  gen_0001_accelxSigmaCrossingRate  gen_0002_accelySigmaCrossingRate  gen_0003_accelzSigmaCrossingRate
            0  Crawling    1     s01                          0.090909                               0.0                               0.0
            1   Running    1     s01                          0.000000                               0.0                               0.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "SigmaCrossingRate",
        [],
        fg_algorithms.fg_roc_sigma_crossing_rate_w,
    )


fg_roc_sigma_crossing_rate_contracts = {
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
    "output_contract": [
        {
            "name": "output_data",
            "type": "DataFrame",
            "scratch_buffer": {"type": "segment_size"},
        }
    ],
}


def fg_roc_second_sigma_crossing_rate(
    input_data: DataFrame, columns: List[str], **kwargs
):
    """
    Calculates the rate at which 2nd standard deviation value (second sigma) is
    crossed for each specified column. The total number of second sigma crossings
    are found and then the number is divided by total number of samples  to get
    the `second_sigma_crossing_rate`.


    Args:
        columns:  The `columns` represents a list of all column names on which
                  `second_sigma_crossing_rate` is to be found.

    Returns:
        DataFrame : Return the second sigma crossing rate.

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
        >>> client.pipeline.add_feature_generator([{'name':'Second Sigma Crossing Rate',
                                     'params':{"columns": ['accelx','accely', 'accelz']}
                                    }])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            out:
                  Class  Rep Subject  gen_0001_accelx2ndSigmaCrossingRate  gen_0002_accely2ndSigmaCrossingRate  gen_0003_accelz2ndSigmaCrossingRate
            0  Crawling    1     s01                             0.090909                             0.090909                                  0.0
            1   Running    1     s01                             0.000000                             0.000000                                  0.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "2ndSigmaCrossingRate",
        [],
        fg_algorithms.fg_roc_second_sigma_crossing_rate_w,
    )


fg_roc_second_sigma_crossing_rate_contracts = {
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
    "output_contract": [
        {
            "name": "output_data",
            "type": "DataFrame",
            "scratch_buffer": {"type": "segment_size"},
        }
    ],
}


def fg_roc_mean_difference(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Calculate the mean difference of each specified column. Works with grouped data.
    For a given column, it finds difference of ith element and (i-1)th element and
    finally takes the mean value of the entire column.

    mean(diff(arr)) = mean(arr[i] - arr[i-1]), for all 1 <= i <= n.

    Args:
        columns:  The `columns` represents a list of all column names on which `mean_difference` is to be found.

    Returns:
        DataFrame : Return the number of mean difference divided by the length of the signal.

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Mean Difference',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxMeanDifference  gen_0002_accelyMeanDifference  gen_0003_accelzMeanDifference
            0     s01                           1.25                           0.75                           0.25

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "MeanDifference",
        [],
        fg_algorithms.fg_roc_mean_difference_w,
    )


fg_roc_mean_difference_contracts = {
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


def fg_roc_threshold_crossing_rate(
    input_data: DataFrame, columns: List[str], threshold: int = 0, **kwargs
) -> float:
    """
    Calculates the rate at which each specified column crosses a given threshold.
    The total number of threshold crossings are found,
    and then the number is divided by the total number of samples to get the `threshold_crossing_rate`.

    Args:
        input_data (DataFrame): The input data.
        columns (list of strings): A list of all column names on which `threshold_crossing_rate` is to be found.
        threshold (int, optional): The threshold value. Defaults to 0.

    Returns:
        DataFrame : Return the number of threshold crossings divided by the length of the signal.
    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "ThresholdCrossingRate",
        [threshold],
        fg_algorithms.fg_roc_threshold_crossing_rate_w,
    )


fg_roc_threshold_crossing_rate_contracts = {
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
            "description": "Threshold to check for crossing rate over",
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
    "output_contract": [
        {
            "name": "output_data",
            "type": "DataFrame",
            "scratch_buffer": {"type": "segment_size"},
        }
    ],
}


def fg_roc_threshold_with_offset_crossing_rate(
    input_data: DataFrame,
    columns: List[str],
    threshold: int = 0,
    offset: int = 0,
    **kwargs
) -> DataFrame:
    """
    Calculates the rate at which each specified column crosses a given threshold with a specified offset.
    The total number of threshold crossings are found,
    and then the number is divided by the total number of samples to get the `threshold_crossing_rate`.

    Args:
        input_data (DataFrame): The input data.
        columns (list of strings): A list of all column names on which `threshold_crossing_rate` is to be found.
        threshold (int, optional): The threshold value. Defaults to 0.
        offset (int, optional): The offset value. Defaults to 0.

    Returns:
        DataFrame : Return the number of threshold crossings divided by the length of the signal.
    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "ThresholdCrossingRate",
        [threshold, offset],
        fg_algorithms.fg_roc_threshold_with_offset_crossing_rate_w,
    )


fg_roc_threshold_with_offset_crossing_rate_contracts = {
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
            "description": "Threshold to check for crossing rate over",
            "range": [MIN_INT_16, MAX_INT_16],
            "c_param": 0,
        },
        {
            "name": "offset",
            "type": "int",
            "default": 0,
            "description": "Offset must fall under before new crossing can be detected",
            "range": [MIN_INT_16, MAX_INT_16],
            "c_param": 1,
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
            "scratch_buffer": {"type": "segment_size"},
        }
    ],
}
