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


def fg_stats_mean(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the arithmetic mean of each column in `columns` in the dataframe.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Mean',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxMean  gen_0002_accelyMean  gen_0003_accelzMean
            0     s01                  0.0                  7.2                  5.8

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "Mean", [], fg_algorithms.fg_stats_mean_w
    )


fg_stats_mean_contracts = {
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


def fg_stats_median(input_data: DataFrame, columns: List[str], **kwargs):
    """
    The median of a vector V with N items, is the middle value of a sorted
    copy of V (V_sorted). When N is even, it is the average of the two
    middle values in V_sorted.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Median',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxMedian  gen_0002_accelyMedian  gen_0003_accelzMedian
            0     s01                    0.0                    7.0                    6.0


    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "Median", [], fg_algorithms.fg_stats_median_w
    )


fg_stats_median_contracts = {
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


def fg_stats_stdev(input_data: DataFrame, columns: List[str], **kwargs):
    """
    The standard deviation of a vector V with N items, is the measure of spread
    of the distribution. The standard deviation is the square root of the average \
    of the squared deviations from the mean, i.e., std = sqrt(mean(abs(x - x.mean())**2)).

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Standard Deviation',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxStd  gen_0002_accelyStd  gen_0003_accelzStd
            0     s01            2.280351             1.16619            1.720465

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "Std", [], fg_algorithms.fg_stats_stdev_w
    )


fg_stats_stdev_contracts = {
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


def fg_stats_skewness(input_data: DataFrame, columns: List[str], **kwargs):
    """
    The skewness is the measure of asymmetry of the distribution of a variable
    about its mean. The skewness value can be positive, negative, or even undefined.
    A positive skew indicates that the tail on the right side is fatter than the left.
    A negative value indicates otherwise.

    Args:
        columns:  list of columns on which to apply the feature generator

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:

        >>> from pandas import DataFrame
        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                    [-2, 8, 7], [2, 9, 6]],
                    columns=['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator([{'name':'Skewness',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxSkew  gen_0002_accelySkew  gen_0003_accelzSkew
            0     s01                  0.0             0.363174            -0.395871

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "Skew", [], fg_algorithms.fg_stats_skewness_w
    )


fg_stats_skewness_contracts = {
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


def fg_stats_kurtosis(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Kurtosis is the degree of 'peakedness' or 'tailedness' in the distribution and
    is related to the shape. A high Kurtosis portrays a chart with fat tail and
    peaky distribution, whereas a low Kurtosis corresponds to the skinny tails and
    the distribution is concentrated towards the mean. Kurtosis is calculated using Fisher's method.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Kurtosis',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxKurtosis  gen_0002_accelyKurtosis  gen_0003_accelzKurtosis
            0     s01                -1.565089                -1.371972                -1.005478

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "Kurtosis", [], fg_algorithms.fg_stats_kurtosis_w
    )


fg_stats_kurtosis_contracts = {
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


def fg_stats_iqr(input_data: DataFrame, columns: List[str], **kwargs):
    """
    The IQR (inter quartile range) of a vector V with N items, is the
    difference between  the 75th percentile and 25th percentile value.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Interquartile Range',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxIQR  gen_0002_accelyIQR  gen_0003_accelzIQR
            0     s01                 4.0                 2.0                 2.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "IQR", [], fg_algorithms.fg_stats_iqr_w
    )


fg_stats_iqr_contracts = {
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


def fg_stats_pct025(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the 25th percentile of each column in 'columns' in the dataframe.
    A q-th percentile of a vector V of length N is the q-th ranked value in
    a sorted copy of V. If the normalized ranking doesn't match the q exactly,
    interpolation is done on two nearest values.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'25th Percentile',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()


        >>> print result
            out:
              Subject  gen_0001_accelx25Percentile  gen_0002_accely25Percentile  gen_0003_accelz25Percentile
            0     s01                         -2.0                          6.0                          5.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "25Percentile", [], fg_algorithms.fg_stats_pct025_w
    )


fg_stats_pct025_contracts = {
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


# input_data (DataFrame) : input data as pandas dataframe
# group_columns: List of column names for grouping
def fg_stats_pct075(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the 75th percentile of each column in 'columns' in the dataframe.
    A q-th percentile of a vector V of length N is the q-th ranked value in a
    sorted copy of V. If the normalized ranking doesn't match the q exactly,
    interpolation is done on two nearest values.

    Args:
        columns:  list of columns on which to apply the feature generator

    Returns:
        DataFrame: Returns data frame with 75th percentile of each specified column.

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
        >>> client.pipeline.add_feature_generator([{'name':'75th Percentile',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
              Subject  gen_0001_accelx75Percentile  gen_0002_accely75Percentile  gen_0003_accelz75Percentile
            0     s01                          2.0                          8.0                          7.0
    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "75Percentile", [], fg_algorithms.fg_stats_pct075_w
    )


fg_stats_pct075_contracts = {
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

# input_data (DataFrame) : input data as pandas dataframe


def fg_stats_pct100(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the 100th percentile of each column in 'columns' in the dataframe.
    A 100th percentile of a vector V the maximum value in V.

    Args:
        columns:  list of columns on which to apply the feature generator


    Returns:
        DataFrame: Returns feature vector with 100th percentile (sample maximum) of each specified column.

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
        >>> client.pipeline.add_feature_generator([{'name':'100th Percentile',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
              Subject  gen_0001_accelx100Percentile  gen_0002_accely100Percentile  gen_0003_accelz100Percentile
            0     s01                           3.0                           9.0                           8.0


    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "100Percentile", [], fg_algorithms.fg_stats_pct100_w
    )


fg_stats_pct100_contracts = {
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


def fg_stats_maximum(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the maximum of each column in 'columns' in the dataframe.
    A maximum of a vector V the maximum value in V.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Maximum',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxmaximum  gen_0002_accelymaximum  gen_0003_accelzmaximum
            0     s01                     3.0                     9.0                     8.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "maximum", [], fg_algorithms.fg_stats_maximum_w
    )


fg_stats_maximum_contracts = {
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


def fg_stats_minimum(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the minimum of each column in 'columns' in the dataframe.
    A minimum of a vector V the minimum value in V.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Minimum',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxminimum  gen_0002_accelyminimum  gen_0003_accelzminimum
            0     s01                    -3.0                     6.0                     3.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "minimum", [], fg_algorithms.fg_stats_minimum_w
    )


fg_stats_minimum_contracts = {
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


def fg_stats_sum(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the cumulative sum of each column in 'columns' in the dataframe.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Standard Deviation',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxSum  gen_0002_accelySum  gen_0003_accelzSum
            0     s01                 0.0                36.0                29.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "Sum", [], fg_algorithms.fg_stats_sum_w
    )


fg_stats_sum_contracts = {
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


def fg_stats_abs_sum(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the cumulative sum of absolute values in each column in 'columns' in the dataframe.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Absolute Sum',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()


        >>> print result
            out:
              Subject  gen_0001_accelxAbsSum  gen_0002_accelyAbsSum  gen_0003_accelzAbsSum
            0     s01                   10.0                   36.0                   29.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "AbsSum", [], fg_algorithms.fg_stats_abs_sum_w
    )


fg_stats_abs_sum_contracts = {
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


def fg_stats_abs_mean(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the arithmetic mean of absolute value in each column of `columns` in the dataframe.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Absolute Mean',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()


        >>> print result
            out:
              Subject  gen_0001_accelxAbsMean  gen_0002_accelyAbsMean  gen_0003_accelzAbsMean
            0     s01                     2.0                     7.2                     5.8

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "AbsMean", [], fg_algorithms.fg_stats_abs_mean_w
    )


fg_stats_abs_mean_contracts = {
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


def fg_stats_variance(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Computes the variance of desired column(s) in the dataframe.

    Args:
        columns:  list of columns on which to apply the feature generator

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Variance',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'] }
                                    }])
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
              Subject  gen_0001_accelxVariance  gen_0002_accelyVariance  gen_0003_accelzVariance
            0     s01                      6.5                      1.7                      3.7

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "Variance", [], fg_algorithms.fg_stats_variance_w
    )


fg_stats_variance_contracts = {
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


def fg_stats_zero_crossings(input_data, columns, threshold=100, **kwargs):
    """
    Computes the number of times the selected input crosses the mean+threshold and mean-threshold values. The threshold value is specified by the user.
    crossing the mean value when the threshold is 0 only counts as a single crossing.


    Args:
        columns:  list of columns on which to apply the feature generator
        threshold: value in addition to mean which must be crossed to count as a crossing

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
                            group_columns = ['Subject']
                           )
        >>> client.pipeline.add_feature_generator([{'name':'Zero Crossings',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'],
                                               "threshold: 5}
                                    }])
        >>> result, stats = client.pipeline.execute()

    """
    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "ZeroCrossings",
        [threshold],
        fg_algorithms.fg_stats_zero_crossings_w,
    )


fg_stats_zero_crossings_contracts = {
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
            "type": "numeric",
            "description": "value in addition to mean which must be crossed to count as a crossing",
            "default": 100,
            "c_param": 0,
            "range": [MIN_INT_16 + 1, MAX_INT_16 - 1],
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


def fg_stats_positive_zero_crossings(input_data, columns, threshold=100, **kwargs):
    """
    Computes the number of times the selected input crosses the mean+threshold and mean-threshold values with a positive slope. The threshold value is specified by the user.
    crossing the mean value when the threshold is 0 only counts as a single crossing.


    Args:
        columns:  list of columns on which to apply the feature generator
        threshold: value in addition to mean which must be crossed to count as a crossing

    Returns:
        DataFrame: Returns data frame with specified column(s).

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "PositiveZeroCrossings",
        [threshold],
        fg_algorithms.fg_stats_positive_zero_crossings_w,
    )


fg_stats_positive_zero_crossings_contracts = {
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
            "type": "numeric",
            "description": "value in addition to mean which must be crossed to count as a crossing",
            "default": 100,
            "c_param": 0,
            "range": [MIN_INT_16 + 1, MAX_INT_16 - 1],
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


def fg_stats_negative_zero_crossings(input_data, columns, threshold=100, **kwargs):
    """
    Computes the number of times the selected input crosses the mean+threshold and mean-threshold values with a negative slope. The threshold value is specified by the user.
    crossing the mean value when the threshold is 0 only coutns as a single crossing.


    Args:
        columns:  list of columns on which to apply the feature generator
        threshold: value in addition to mean which must be crossed to count as a crossing

    Returns:
        DataFrame: Returns data frame with specified column(s).

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "NegativeZeroCrossings",
        [threshold],
        fg_algorithms.fg_stats_negative_zero_crossings_w,
    )


fg_stats_negative_zero_crossings_contracts = {
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
            "type": "numeric",
            "description": "value in addition to mean which must be crossed to count as a crossing",
            "default": 100,
            "c_param": 0,
            "range": [MIN_INT_16 + 1, MAX_INT_16 - 1],
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


def fg_stats_linear_regression(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Calculate a linear least-squares regression and returns
    the linear regression stats which are slope, intercept, r value, standard error.

    slope: Slope of the regression line.
    intercept: Intercept of the regression line.
    r value: Correlation coefficient.
    StdErr: Standard error of the estimated gradient.

    Args:
        columns:  list of columns on which to apply the feature generator

    Returns:
        DataFrame: Returns data frame with specified column(s).

    Examples:

        >>> from pandas import DataFrame
        >>> df = pd.DataFrame({'Subject': ['s01'] * 10,'Class': ['Crawling'] * 10 ,'Rep': [1] * 10 })
        >>> df["X"] = [i + 2 for i in range(10)]
        >>> df["Y"] = [i for i in range(10)]
        >>> df["Z"] = [1, 2, 3, 3, 5, 5, 7, 7, 9, 10]
        >>> print(df)
            out:
              Subject     Class  Rep   X  Y   Z
            0     s01  Crawling    1   2  0   1
            1     s01  Crawling    1   3  1   2
            2     s01  Crawling    1   4  2   3
            3     s01  Crawling    1   5  3   3
            4     s01  Crawling    1   6  4   5
            5     s01  Crawling    1   7  5   5
            6     s01  Crawling    1   8  6   7
            7     s01  Crawling    1   9  7   7
            8     s01  Crawling    1  10  8   9
            9     s01  Crawling    1  11  9  10


        >>> client.upload_dataframe('test_data', df, force=True)
        >>> client.pipeline.reset(delete_cache=True)
        >>> client.pipeline.set_input_data('test_data.csv',
                                        group_columns=['Subject','Rep'],
                                        label_column='Class',
                                        data_columns=['X','Y','Z'])
        >>> client.pipeline.add_feature_generator([{'name':'Linear Regression Stats',
                                                 'params':{"columns": ['X','Y','Z'] }}])
        >>> results, stats = client.pipeline.execute()
        >>> print(results.T)
            out:
                                                     0
            Rep                                      1
            Subject                                s01
            gen_0001_XLinearRegressionSlope          1
            gen_0001_XLinearRegressionIntercept      2
            gen_0001_XLinearRegressionR              1
            gen_0001_XLinearRegressionStdErr         0
            gen_0002_YLinearRegressionSlope          1
            gen_0002_YLinearRegressionIntercept      0
            gen_0002_YLinearRegressionR              1
            gen_0002_YLinearRegressionStdErr         0
            gen_0003_ZLinearRegressionSlope      0.982
            gen_0003_ZLinearRegressionIntercept  0.782
            gen_0003_ZLinearRegressionR          0.987
            gen_0003_ZLinearRegressionStdErr     0.056

    """

    params = []
    result_names = [
        "LinearRegressionSlope_0000",
        "LinearRegressionIntercept_0001",
        "LinearRegressionR_0002",
        "LinearRegressionStdErr_0003",
    ]

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        result_names,
        params,
        fg_algorithms.fg_stats_linear_regression_w,
    )


fg_stats_linear_regression_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "num_columns": 1,
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
            "family": True,
            "output_formula": "4",
        }
    ],
}
