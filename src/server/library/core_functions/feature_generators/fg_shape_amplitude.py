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


def fg_shape_ratio_high_frequency(
    input_data: DataFrame,
    columns: List[str],
    smoothing_factor: int = 5,
    **kwargs,
) -> DataFrame:
    """
    Calculates the ratio of peak to peak of high frequency between two halves. The high frequency
    signal is calculated by subtracting the moving average filter output from the original signal.

    Args:
        input_data (DataFrame): Input pandas dataframe.
        smoothing_factor (int): Determines the amount of attenuation for frequencies over the cutoff frequency.
            Number of elements in individual columns should be at least three times the smoothing factor.
        columns (List[str]): List of column names on which to apply the feature generator.

    Returns:
        DataFrame: `ratio high frequency` for each column and the specified group_columns.

    Examples:
        >>> import numpy as np
        >>> sample = 100
        >>> df = pd.DataFrame()
        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,
                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })
        >>> x = np.arange(sample)
        >>> fx = 2; fy = 3; fz = 5
        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )
        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )
        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )
        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()


        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class']
                           )

        >>> client.pipeline.add_feature_generator([{'name':'Ratio of Peak to Peak of High Frequency between two halves',
                                     'params':{"smoothing_factor": 5,
                                               "columns": ['accelz'] }}])

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               Class Subject  gen_0001_accelzACRatio
            0      0     s01                3.888882
            1      1     s01                0.350000

    """

    if input_data["data"].shape[1] < 2 * 3 * smoothing_factor:
        raise Exception(
            "This feature generator requires all groups to have at least 2*3*smoothing_factor = {0} samples."
            "You can lower the smoothing_factor, change your query, or omit this feature.".format(
                2 * 3 * smoothing_factor
            )
        )

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "ACRatio",
        [smoothing_factor],
        fg_algorithms.fg_shape_ratio_high_frequency_w,
    )


fg_shape_ratio_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 32],
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


def fg_shape_difference_high_frequency(
    input_data: DataFrame,
    columns: List[str],
    smoothing_factor: int = 5,
    **kwargs,
) -> DataFrame:
    """
    Calculates the difference of peak to peak of high frequency between two halves.
    The high frequency signal is calculated by subtracting the moving average filter output from the original signal.

    Args:
        input_data (DataFrame): Input pandas dataframe.
        smoothing_factor (int): Determines the amount of attenuation for frequencies over the cutoff frequency.
            Number of elements in individual columns should be at least three times the smoothing factor.
        columns (List[str]): List of column names on which to apply the feature generator.


    Returns:
        DataFrame: `difference high frequency` for each column and the specified group_columns.


    Examples:
        >>> import numpy as np
        >>> sample = 100
        >>> df = pd.DataFrame()
        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,
                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })
        >>> x = np.arange(sample)
        >>> fx = 2; fy = 3; fz = 5
        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )
        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )
        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )
        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()


        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class']
                           )

        >>> client.pipeline.add_feature_generator([{'name':'Difference of Peak to Peak of High Frequency between two halves',
                                     'params':{"smoothing_factor": 5,
                                               "columns": ['accelz'] }}])

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               Class Subject  gen_0001_accelzACDiff
            0      0     s01              -5.199997
            1      1     s01              13.000000


    """

    if input_data["data"].shape[1] < 2 * 3 * smoothing_factor:
        raise Exception(
            f"This feature generator requires all groups to have at least 2*3*smoothing_factor = { 2 * 3 * smoothing_factor} samples."
        )

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "ACDiff",
        [smoothing_factor],
        fg_algorithms.fg_shape_difference_high_frequency_w,
    )


fg_shape_difference_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 32],
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


def fg_amplitude_global_p2p_high_frequency(
    input_data: DataFrame, columns: List[str], smoothing_factor: int = 5, **kwargs
):
    """
    Global peak to peak of high frequency. The high frequency signal is calculated by
    subtracting the moving average filter output from the original signal.

    Args:
        smoothing_factor (int); Determines the amount of attenuation for frequencies
          over the cutoff frequency. The number of elements in individual
          columns should be al least three times the smoothing factor.
        columns: List of str; Set of columns on which to apply the feature generator

    Returns:
        DataFrame of `global p2p high frequency` for each column and the specified group_columns

    Examples:
        >>> import numpy as np
        >>> sample = 100
        >>> df = pd.DataFrame()
        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,
                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })
        >>> x = np.arange(sample)
        >>> fx = 2; fy = 3; fz = 5
        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )
        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )
        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )
        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()


        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class']
                           )

        >>> client.pipeline.add_feature_generator([{'name':'Global Peak to Peak of High Frequency',
                                     'params':{"smoothing_factor": 5,
                                               "columns": ['accelx','accely','accelz'] }}])

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               Class Subject  gen_0001_accelxMaxP2PGlobalAC  gen_0002_accelyMaxP2PGlobalAC  gen_0003_accelzMaxP2PGlobalAC
            0      0     s01                            3.6                            7.8                      86.400002
            1      1     s01                            3.6                            7.8                     165.000000

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "MaxP2PGlobalAC",
        [smoothing_factor],
        fg_algorithms.fg_amplitude_global_p2p_high_frequency_w,
    )


fg_amplitude_global_p2p_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 32],
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


def fg_amplitude_global_p2p_low_frequency(
    input_data: DataFrame, columns: List[str], smoothing_factor: int = 5, **kwargs
):
    """
    Global peak to peak of low frequency. The low frequency signal is calculated by
    applying a moving average filter with a smoothing factor.

    Args:
        smoothing_factor (int); Determines the amount of attenuation for
          frequencies over the cutoff frequency.
        columns: List of str; Set of columns on which to apply the feature generator

    Returns:
        DataFrame of `global p2p low frequency` for each column and the specified group_columns

    Examples:
        >>> import numpy as np
        >>> sample = 100
        >>> df = pd.DataFrame()
        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,
                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })
        >>> x = np.arange(sample)
        >>> fx = 2; fy = 3; fz = 5
        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )
        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )
        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )
        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()


        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class']
                           )

        >>> client.pipeline.add_feature_generator([{'name':'Global Peak to Peak of Low Frequency',
                                     'params':{"smoothing_factor": 5,
                                               "columns": ['accelx','accely','accelz'] }}])

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               Class Subject  gen_0001_accelxMaxP2PGlobalDC  gen_0002_accelyMaxP2PGlobalDC  gen_0003_accelzMaxP2PGlobalDC
            0      0     s01                     195.600006                     191.800003                     187.000000
            1      1     s01                     195.600006                     191.800003                     185.800003

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "MaxP2PGlobalDC",
        [smoothing_factor],
        fg_algorithms.fg_amplitude_global_p2p_low_frequency_w,
    )


fg_amplitude_global_p2p_low_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 32],
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


def fg_amplitude_max_p2p_half_high_frequency(
    input_data: DataFrame, columns: List[str], smoothing_factor: int = 5, **kwargs
):
    """
    Max Peak to Peak of first half of High Frequency. The high frequency signal
    is calculated by subtracting the moving average filter output from the original signal.

    Args:
        smoothing_factor (int); Determines the amount of attenuation for
          frequencies over the cutoff frequency.
        columns: List of str; Set of columns on which to apply the feature generator

    Returns:
        DataFrame of `max p2p half high frequency` for each column and the specified group_columns

    Examples:
        >>> import numpy as np
        >>> sample = 100
        >>> df = pd.DataFrame()
        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,
                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })
        >>> x = np.arange(sample)
        >>> fx = 2; fy = 3; fz = 5
        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )
        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )
        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )
        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()


        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class']
                           )

        >>> client.pipeline.add_feature_generator([{'name':'Max Peak to Peak of first half of High Frequency',
                                     'params':{"smoothing_factor": 5,
                                               "columns": ['accelx','accely','accelz'] }}])

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               Class Subject  gen_0001_accelxMaxP2P1stHalfAC  gen_0002_accelyMaxP2P1stHalfAC  gen_0003_accelzMaxP2P1stHalfAC
            0      0     s01                             1.8                             7.0                             1.8
            1      1     s01                             1.8                             7.0                            20.0


    """

    if input_data["data"].shape[1] < 2 * 3 * smoothing_factor:
        raise Exception(
            "This feature generator requires all groups to have at least 2*3*smoothing_factor = {0} samples."
            "You can lower the smoothing_factor, change your query, or omit this feature.".format(
                2 * 3 * smoothing_factor
            )
        )

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "MaxP2P1stHalfAC",
        [smoothing_factor],
        fg_algorithms.fg_amplitude_max_p2p_half_high_frequency_w,
    )


fg_amplitude_max_p2p_half_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 32],
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


def fg_amplitude_peak_to_peak(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Global Peak to Peak of signal.

    Args:
        columns: (list of str): Set of columns on which to apply the feature generator

    Returns:
        DataFrame of `peak to peak` for each column and the specified group_columns


    Examples:
        >>> from pandas import DataFrame
        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
                            columns=['accelx', 'accely', 'accelz'])
        >>> df['Subject'] = 's01'
        >>> print df
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

        >>> client.pipeline.add_feature_generator([{'name':'Global Peak to Peak',
                                     'params':{"columns": ['accelx','accely','accelz'] }}])

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
              Subject  gen_0001_accelxP2P  gen_0002_accelyP2P  gen_0003_accelzP2P
            0     s01                 6.0                 3.0                 5.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "P2P", [], fg_algorithms.fg_amplitude_peak_to_peak_w
    )


fg_amplitude_peak_to_peak_contracts = {
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


def fg_amplitude_min_max_sum(input_data: DataFrame, columns: List[str], **kwargs):
    """
    This function is the sum of the maximum and minimum values. It is also
    used as the 'min max amplitude difference'.

    Args:
        columns: (list of str): Set of columns on which to apply the feature generator

    Returns:
        DataFrame of `min max sum` for each column and the specified group_columns


    Examples:
        >>> from pandas import DataFrame
        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
                            columns=['accelx', 'accely', 'accelz'])
        >>> df['Subject'] = 's01'
        >>> print df
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

        >>> client.pipeline.add_feature_generator([{'name':'Global Min Max Sum',
                                     'params':{"columns": ['accelx','accely','accelz'] }}])

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               Subject  gen_0001_accelxMinMaxSum  gen_0002_accelyMinMaxSum  gen_0003_accelzMinMaxSum
            0     s01                       0.0                      15.0                      11.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "MinMaxSum", [], fg_algorithms.fg_amplitude_min_max_sum_w
    )


fg_amplitude_min_max_sum_contracts = {
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


def fg_shape_median_difference(
    input_data: DataFrame, columns: List[str], center_ratio: int = 0.5, **kwargs
):
    """
    Computes the difference in median between the first and second half of a signal


    Args:
        columns:  list of columns on which to apply the feature generator
        center_ratio: ratio of the signal to be on the first half to second half

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
        >>> client.pipeline.add_feature_generator([{'name':'Shape Median Difference',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'],
                                               "center_ratio: 0.5}
                                    }])
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
              Subject  gen_0001_accelxShapeMedianDifference  gen_0002_accelyShapeMedianDifference  gen_0003_accelzShapeMedianDifference
            0     s01
    """

    if center_ratio <= 0 or center_ratio >= 1.0:
        raise Exception("center ratio must be between 0 and 1.0")

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "ShapeMedianDifference",
        [center_ratio],
        fg_algorithms.fg_shape_median_difference_w,
    )


fg_shape_median_difference_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "center_ratio",
            "type": "numeric",
            "description": "ratio of the signal to be on the first half to second half",
            "default": 0.5,
            "c_param": 0,
            "range": [0.1, 0.9],
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


def fg_shape_absolute_median_difference(
    input_data: DataFrame, columns: List[str], center_ratio: int = 0.5, **kwargs
):
    """
    Computes the absolute value of the difference in median between the first and second half of a signal


    Args:
        columns:  list of columns on which to apply the feature generator
        center_ratio: ratio of the signal to be on the first half to second half

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
        >>> client.pipeline.add_feature_generator([{'name':'Shape Absolute Median Difference',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'],
                                            "center_ratio": 0.5}
                                    }])
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
              Subject  gen_0001_accelxShapeAbsoluteMedianDifference  gen_0002_accelyShapeAbsoluteMedianDifference  gen_0003_accelzShapeAbsoluteMedianDifference
            0     s01
    """

    if center_ratio <= 0 or center_ratio >= 1.0:
        raise Exception("center ratio must be between 0 and 1.0")

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "ShapeAbsoluteMedianDifference",
        [center_ratio],
        fg_algorithms.fg_shape_absolute_median_difference_w,
    )


fg_shape_absolute_median_difference_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "center_ratio",
            "type": "numeric",
            "description": "ratio of the signal to be on the first half to second half",
            "default": 0.5,
            "c_param": 0,
            "range": [0.1, 0.9],
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
