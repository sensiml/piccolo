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

from numpy import absolute, mean, median, percentile, std, subtract
from pandas import DataFrame, concat
from scipy.stats import kurtosis, skew


def stats_mean(input_data, columns, **kwargs):
    """
    Computes the arithmetic mean of each column in `columns` in the dataframe.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns data frame containing mean values of each specified column.

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
        >>> client.pipeline.add_feature_generator(["Mean"],
                 params = {"group_columns": []},
                 function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                   accelxMean  accelyMean  accelzMean
            0         0.0         7.2         5.8
    """

    result = DataFrame()
    for col in columns:
        feature = mean(input_data[col])
        feature_name = col + "Mean"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_mean_contracts = {
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


def stats_median(input_data, columns, **kwargs):
    """
    The median of a vector V with N items, is the middle value of a sorted
    copy of V (V_sorted). When N is even, it is the average of the two
    middle values in V_sorted.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns data frame with median of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                                [-2, 8, 7], [2, 9, 6]],
                               columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Median"],
                 params = {"group_columns": []},
                 function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
               accelxMedian  accelyMedian  accelzMedian
            0           0.0           7.0           6.0
    """
    result = DataFrame()
    for col in columns:
        feature = median(input_data[col])
        feature_name = col + "Median"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_median_contracts = {
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


def stats_stdev(input_data, columns, **kwargs):
    """
    The standard deviation of a vector V with N items, is the measure of spread
    of the distribution. The standard deviation is the square root of the average \
    of the squared deviations from the mean, i.e., std = sqrt(mean(abs(x - x.mean())**2)).

    Args:
        input_data (DataFrame)
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns data frame with standard deviation of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                                [-2, 8, 7], [2, 9, 6]],
                                columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Standard Deviation"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelxStd  accelyStd  accelzStd
            0   2.280351    1.16619   1.720465

    """
    result = DataFrame()
    for col in columns:
        feature = std(input_data[col])
        feature_name = col + "Std"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_stdev_contracts = {
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


def stats_skewness(input_data, columns, **kwargs):
    """
    The skewness is the measure of asymmetry of the distribution of a variable
    about its mean. The skewness value can be positive, negative, or even undefined.
    A positive skew indicates that the tail on the right side is fatter than the left.
    A negative value indicates otherwise.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns data frame with skewness of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                              [-2, 8, 7], [2, 9, 6]],
                              columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Skewness"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelxSkew  accelySkew  accelzSkew
            0         0.0    0.363173    -0.39587
    """
    result = DataFrame()
    for col in columns:
        feature = skew(input_data[col], axis=0, bias=True)
        feature_name = col + "Skew"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_skewness_contracts = {
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


def stats_kurtosis(input_data, columns, **kwargs):
    """
    Kurtosis is the degree of 'peakedness' or 'tailedness' in the distribution and
    is related to the shape. A high Kurtosis portrays a chart with fat tail and
    peaky distribution, whereas a low Kurtosis corresponds to the skinny tails and
    the distribution is concentrated towards the mean. Kurtosis is calculated using Fisher's method.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:
    Returns:
        DataFrame: Returns data frame with Kurtosis of each specified column.
                    If all values are equal, return -3 for Fishers mrthod.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                                    [-2, 8, 7], [2, 9, 6]],
                                    columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Kurtosis"],
                 params = {"group_columns": []},
                 function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelxKurtosis  accelyKurtosis  accelzKurtosis
            0       -1.565089       -1.371972       -1.005478
    """
    result = DataFrame()
    for col in columns:
        feature = kurtosis(input_data[col], 0, True, True)
        feature_name = col + "Kurtosis"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_kurtosis_contracts = {
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


def stats_iqr(input_data, columns, **kwargs):
    """
    The IQR (inter quartile range) of a vector V with N items, is the
    difference between  the 75th percentile and 25th percentile value.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns dataframe with IQR of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                                 [-2, 8, 7], [2, 9, 6]],
                                 columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Interquartile Range"],
                        params = {"group_columns": []},
                        function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelxIQR  accelyIQR  accelzIQR
            0        4.0        2.0        2.0

    """
    result = DataFrame()
    for col in columns:
        feature = subtract(*percentile(input_data[col], [75, 25]))
        feature_name = col + "IQR"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_iqr_contracts = {
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


def stats_pct025(input_data, columns, **kwargs):
    """
    Computes the 25th percentile of each column in 'columns' in the dataframe.
    A q-th percentile of a vector V of length N is the q-th ranked value in
    a sorted copy of V. If the normalized ranking doesn't match the q exactly,
    interpolation is done on two nearest values.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns 25-th percentile of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],]
                                [-2, 8, 7], [2, 9, 6]],
                                columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["25th Percentile"],
                    params = {"group_columns": []},
                    function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelx25Percentile  accely25Percentile  accelz25Percentile
            0                -2.0                 6.0                 5.0
    """
    result = DataFrame()
    for col in columns:
        feature = percentile(input_data[col], 25)
        feature_name = col + "25Percentile"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_pct025_contracts = {
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


def stats_pct075(input_data, columns, **kwargs):
    """
    Computes the 75th percentile of each column in 'columns' in the dataframe.
    A q-th percentile of a vector V of length N is the q-th ranked value in a
    sorted copy of V. If the normalized ranking doesn't match the q exactly,
    interpolation is done on two nearest values.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns data frame with 75th percentile of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                               [-2, 8, 7], [2, 9, 6]],
                               columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["75th Percentile"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelx75Percentile  accely75Percentile  accelz75Percentile
            0                 2.0                 8.0                 7.0
    """
    result = DataFrame()
    for col in columns:
        feature = percentile(input_data[col], 75)
        feature_name = col + "75Percentile"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_pct075_contracts = {
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


def stats_pct100(input_data, columns, **kwargs):
    """
    Computes the 100th percentile of each column in 'columns' in the dataframe.
    A 100th percentile of a vector V the maximum value in V.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns feature vector with 100th percentile (sample maximum) of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                                [-2, 8, 7], [2, 9, 6]],
                                columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["100th Percentile"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelx100Percentile  accely100Percentile  accelz100Percentile
            0                  3.0                  9.0                  8.0
    """
    result = DataFrame()
    for col in columns:
        feature = percentile(input_data[col], 100)
        feature_name = col + "100Percentile"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_pct100_contracts = {
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


def stats_maximum(input_data, columns, **kwargs):
    """
    Computes the maximum of each column in 'columns' in the dataframe.
    A maximum of a vector V the maximum value in V.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns feature vector with maximum (sample maximum) of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                                [-2, 8, 7], [2, 9, 6]],
                                columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Maximum"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelxmaximum  accelymaximum  accelzmaximum
            0               3.0                 9.0                  8.0
    """
    result = DataFrame()
    for col in columns:
        feature = percentile(input_data[col], 100)
        feature_name = col + "maximum"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_maximum_contracts = {
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


def stats_minimum(input_data, columns, **kwargs):
    """
    Computes the minimum of each column in 'columns' in the dataframe.
    A minimum of a vector V the minimum value in V.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns feature vector with minimum (sample minimum) of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                                [-2, 8, 7], [2, 9, 6]],
                                columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Minimum"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               accelx100Percentile  accely100Percentile  accelz100Percentile
            0                  -3.0                  6.0                  3.0
    """
    result = DataFrame()
    for col in columns:
        feature = percentile(input_data[col], 0)
        feature_name = col + "minimum"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_minimum_contracts = {
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


def stats_sum(input_data, columns, **kwargs):
    """
    Computes the cumulative sum of each column in 'columns' in the dataframe.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping

    Returns:
        DataFrame: Returns data frame containing sum values of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                               [-2, 8, 7], [2, 9, 6]],
                               columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Sum"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                   accelxSum  accelySum  accelzSum
            0         0.0         36.0         29.0
    """

    result = DataFrame()
    for col in columns:
        feature = sum(input_data[col])
        feature_name = col + "Sum"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_sum_contracts = {
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


def stats_abs_sum(input_data, columns, **kwargs):
    """
    Computes the cumulative sum of absolute values in each column in 'columns' in the dataframe.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping

    Returns:
        DataFrame: Returns data frame containing absolute sum values of each specified column.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                               [-2, 8, 7], [2, 9, 6]],
                               columns= ['accelx', 'accely', 'accelz'])
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
        >>> client.pipeline.add_feature_generator(["Absolute Sum"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                   accelxAbsSum  accelyAbsSum  accelzAbsSum
            0         10        36         29
    """

    result = DataFrame()
    for col in columns:
        feature = sum(absolute(input_data[col]))
        feature_name = col + "AbsSum"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_abs_sum_contracts = {
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


def stats_abs_mean(input_data, columns, **kwargs):
    """
    Computes the arithmetic mean of absolute value in each column of `columns` in the dataframe.

    Args:
        input_data (DataFrame) : input data as pandas dataframe
        columns:  list of columns on which to apply the feature generator
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame: Returns data frame containing absolute mean values of each specified column.

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
        >>> client.pipeline.add_feature_generator(["Absolute Mean"],
                 params = {"group_columns": []},
                 function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                   accelxAbsMean  accelyAbsMean  accelzAbsMean
            0         2.0            7.2            5.8
    """

    result = DataFrame()
    for col in columns:
        feature = mean(absolute(input_data[col]))
        feature_name = col + "AbsMean"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


stats_abs_mean_contracts = {
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


def stats_linear_regression(input_data, columns, **kwargs):
    """
    Calculate a linear least-squares regression for two sets of measurements and returns
    the linear regression stats which are slope, intercept, r value, p value, standard error.

    slope: Slope of the regression line.
    intercept: Intercept of the regression line.
    r value: Correlation coefficient.
    p value: Two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero,
             using Wald Test with t-distribution of the test statistic.
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

    # this part will be updated with C function
    from scipy import stats
    from pandas import DataFrame

    df = DataFrame()
    for c in columns:
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            range(len(input_data)), input_data[c].to_list()
        )
        df.loc[0, c + "LinearRegressionSlope_0000"] = slope
        df.loc[0, c + "LinearRegressionIntercept_0001"] = intercept
        df.loc[0, c + "LinearRegressionR_0002"] = r_value
        df.loc[0, c + "LinearRegressionStdErr_0003"] = std_err

    return round(df, 3)


stats_linear_regression_contracts = {
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
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}
