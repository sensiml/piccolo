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

from numpy import array, diff, divide, mean, multiply, nonzero, std
from pandas import DataFrame, concat


def _calculate_crossing_rate(input_array, threshold_value=0):
    """Calculates the rate at which a threshold value is crossed."""
    # Subtract the threshold value and remove zeros
    data = input_array - threshold_value
    # Zeros can cause miscounting for the multiply method
    data = data[nonzero(data)]

    # Return the number of zero crossings divided by the length of the signal
    return divide((multiply(data[:-1], data[1:]) < 0).sum(), float(len(input_array)))


def mean_crossing_rate(input_data, columns, **kwargs):
    """
    Calculates the rate at which mean value is crossed for each specified column.
    Works with grouped data. The total number of mean value crossings are found
    and then the number is divided by total number of samples  to get
    the `mean_crossing_rate`.

    Args:
        input_data: is dataframe.
        columns:  The `columns` represents a list of all column names on
                  which `mean_crossing_rate` is to be found.
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame : Return the number of zero crossings divided by the length of the signal.

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20 ,
                               'Rep': [1] * 20 })
        >>> df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df
            Out:
                  Class    Rep   Subject  accelx
            0   Crawling    1     s01       0
            1   Crawling    1     s01       9
            2   Crawling    1     s01       5
            3   Crawling    1     s01      -5
            4   Crawling    1     s01      -9
            5   Crawling    1     s01       0
            6   Crawling    1     s01       9
            7   Crawling    1     s01       5
            8   Crawling    1     s01      -5
            9   Crawling    1     s01      -9
            10  Crawling    1     s01       0
            11  Crawling    1     s01       9
            12  Crawling    1     s01       5
            13  Crawling    1     s01      -5
            14  Crawling    1     s01      -9
            15  Crawling    1     s01       0
            16  Crawling    1     s01       9
            17  Crawling    1     s01       5
            18  Crawling    1     s01      -5
            19  Crawling    1     s01      -9
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df)
        >>> client.pipeline.add_feature_generator(["Mean Crossing Rate"],
                 params = {"group_columns": []},
                           function_defaults={"columns":['accelx']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            Out:
               gen_0001_accelxMeanCrossingRate
            0                             0.35
    """
    result = DataFrame()
    for col in columns:
        feature = _calculate_crossing_rate(
            array(input_data[col]), mean(input_data[col])
        )
        feature_name = col + "MeanCrossingRate"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


mean_crossing_rate_contracts = {
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


def zero_crossing_rate(input_data, columns, **kwargs):
    """
    Calculates the rate at which zero value is crossed for each specified column.
    The total number of zero crossings are found and then the number is divided
    by total number of samples to get the `zero_crossing_rate`.

    Args:
        input_data: is dataframe.
        columns:  The `columns` represents a list of all column names on which
                 `zero_crossing_rate` is to be found.
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        A dataframe of containing ZCR

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                             'Class': ['Crawling'] * 20 ,
                             'Rep': [1] * 20 })
        >>> df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df
            Out:
               Class  Rep Subject  accelx
            0   Crawling    1     s01       0
            1   Crawling    1     s01       9
            2   Crawling    1     s01       5
            3   Crawling    1     s01      -5
            4   Crawling    1     s01      -9
            5   Crawling    1     s01       0
            6   Crawling    1     s01       9
            7   Crawling    1     s01       5
            8   Crawling    1     s01      -5
            9   Crawling    1     s01      -9
            10  Crawling    1     s01       0
            11  Crawling    1     s01       9
            12  Crawling    1     s01       5
            13  Crawling    1     s01      -5
            14  Crawling    1     s01      -9
            15  Crawling    1     s01       0
            16  Crawling    1     s01       9
            17  Crawling    1     s01       5
            18  Crawling    1     s01      -5
            19  Crawling    1     s01      -9
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df)
        >>> client.pipeline.add_feature_generator(["Zero Crossing Rate"],
                    params = {"group_columns": []},
                    function_defaults={"columns":['accelx']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            Out:
               gen_0001_accelxZeroCrossingRate
            0                             0.35
    """
    result = DataFrame()
    for col in columns:
        feature = _calculate_crossing_rate(array(input_data[col]))
        feature_name = col + "ZeroCrossingRate"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


zero_crossing_rate_contracts = {
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


def sigma_crossing_rate(input_data, columns, **kwargs):
    """
    Calculates the rate at which standard deviation value (sigma) is crossed for
    each specified column. The total number of sigma crossings are found and then
    the number is divided by total number of samples to get the `sigma_crossing_rate`.

    Args:
        input_data: is dataframe.
        columns:  The `columns` represents a list of all column names on which
                 `sigma_crossing_rate` is to be found.
        group_columns: List of column names for grouping
        **kwargs:

    Returns:
        DataFrame:

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20 ,
                               'Rep': [1] * 20 })
        >>> df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df
            Out:
               Class  Rep Subject  accelx
            0   Crawling    1     s01       0
            1   Crawling    1     s01       9
            2   Crawling    1     s01       5
            3   Crawling    1     s01      -5
            4   Crawling    1     s01      -9
            5   Crawling    1     s01       0
            6   Crawling    1     s01       9
            7   Crawling    1     s01       5
            8   Crawling    1     s01      -5
            9   Crawling    1     s01      -9
            10  Crawling    1     s01       0
            11  Crawling    1     s01       9
            12  Crawling    1     s01       5
            13  Crawling    1     s01      -5
            14  Crawling    1     s01      -9
            15  Crawling    1     s01       0
            16  Crawling    1     s01       9
            17  Crawling    1     s01       5
            18  Crawling    1     s01      -5
            19  Crawling    1     s01      -9
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df)
        >>> client.pipeline.add_feature_generator(["Sigma Crossing Rate"],
                params = {"group_columns": []},
                          function_defaults={"columns":['accelx']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            Out:
               gen_0001_accelxSigmaCrossingRate
            0                               0.2
    """
    result = DataFrame()
    for col in columns:
        feature = _calculate_crossing_rate(array(input_data[col]), std(input_data[col]))
        feature_name = col + "SigmaCrossingRate"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


sigma_crossing_rate_contracts = {
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


def second_sigma_crossing_rate(input_data, columns, **kwargs):
    """
    Calculates the rate at which 2nd standard deviation value (second sigma) is
    crossed for each specified column. The total number of second sigma crossings
    are found and then the number is divided by total number of samples  to get
    the `second_sigma_crossing_rate`.


    Args:
        input_data: is dataframe.
        columns:  The `columns` represents a list of all column names on which
                  `second_sigma_crossing_rate` is to be found.
        group_columns: List of column names for grouping
        **kwargs:

    Returns:

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20 ,
                               'Rep': [1] * 20 })
        >>> df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df
            Out:
               Class  Rep Subject  accelx
            0   Crawling    1     s01       0
            1   Crawling    1     s01       9
            2   Crawling    1     s01       5
            3   Crawling    1     s01      -5
            4   Crawling    1     s01      -9
            5   Crawling    1     s01       0
            6   Crawling    1     s01       9
            7   Crawling    1     s01       5
            8   Crawling    1     s01      -5
            9   Crawling    1     s01      -9
            10  Crawling    1     s01       0
            11  Crawling    1     s01       9
            12  Crawling    1     s01       5
            13  Crawling    1     s01      -5
            14  Crawling    1     s01      -9
            15  Crawling    1     s01       0
            16  Crawling    1     s01       9
            17  Crawling    1     s01       5
            18  Crawling    1     s01      -5
            19  Crawling    1     s01      -9
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df)
        >>> client.pipeline.add_feature_generator(["Second Sigma Crossing Rate"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            Out:
               accelx2ndSigmaCrossingRate
            0                           0
    """
    result = DataFrame()
    for col in columns:
        feature = _calculate_crossing_rate(
            array(input_data[col]), 2 * std(input_data[col])
        )
        feature_name = col + "2ndSigmaCrossingRate"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


second_sigma_crossing_rate_contracts = {
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


def mean_difference(input_data, columns, **kwargs):
    """
    Calculate the mean difference of each specified column. Works with grouped data.
    For a given column, it finds difference of ith element and (i-1)th element and
    finally takes the mean value of the entire column.

    mean(diff(arr)) = mean(arr[i] - arr[i-1]), for all 1 <= i <= n.

    Args:
        input_data: is dataframe.
        columns:  The `columns` represents a list of all column names
        on which `mean_difference` is to be found.
        group_columns: List of column names for grouping
        **kwargs:


    Returns:
    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,'Class': ['Crawling'] * 20 ,'Rep': [1] * 20 })
        >>> df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df
            Out:
                 Class     Rep   Subject  accelx
            0   Crawling    1     s01       0
            1   Crawling    1     s01       9
            2   Crawling    1     s01       5
            3   Crawling    1     s01      -5
            4   Crawling    1     s01      -9
            5   Crawling    1     s01       0
            6   Crawling    1     s01       9
            7   Crawling    1     s01       5
            8   Crawling    1     s01      -5
            9   Crawling    1     s01      -9
            10  Crawling    1     s01       0
            11  Crawling    1     s01       9
            12  Crawling    1     s01       5
            13  Crawling    1     s01      -5
            14  Crawling    1     s01      -9
            15  Crawling    1     s01       0
            16  Crawling    1     s01       9
            17  Crawling    1     s01       5
            18  Crawling    1     s01      -5
            19  Crawling    1     s01      -9
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df)
        >>> client.pipeline.add_feature_generator(["Mean Difference"],
                params = {"group_columns": []},
                function_defaults={"columns":['accelx']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            Out:
               gen_0001_accelxMeanDifference
            0                      -0.105263
    """
    result = DataFrame()
    for col in columns:
        feature = mean(diff(input_data[col]))
        feature_name = col + "MeanDifference"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


mean_difference_contracts = {
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
