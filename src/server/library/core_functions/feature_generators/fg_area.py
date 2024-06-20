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


def fg_area_total_area(
    input_data: DataFrame, sample_rate: int, columns: List[str], **kwargs
):
    """
    Total area under the signal. Total area = sum(signal(t)*dt), where
    signal(t) is signal value at time t, and dt is sampling time (dt = 1/sample_rate).

    Args:
        sample_rate: Sampling rate of the signal
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

        >>> client.pipeline.add_feature_generator([{'name':'Total Area',
                                     'params':{"sample_rate": 10,
                                               "columns": ['accelx','accely','accelz']
                                              }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen0001_accelxTotArea  gen_0002_accelyTotArea  gen_0003_accelzTotArea
            0     s01                    0.0                     3.6                     2.9

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "TotArea",
        [sample_rate],
        fg_algorithms.fg_area_total_area_w,
    )


fg_area_total_area_contracts = {
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


def fg_area_absolute_area(
    input_data: DataFrame, sample_rate: int, columns: List[str], **kwargs
):
    """
    Absolute area of the signal. Absolute area = sum(abs(signal(t)) dt), where
    `abs(signal(t))` is absolute signal value at time t, and dt is sampling time (dt = 1/sample_rate).

    Args:
        sample_rate: Sampling rate of the signal
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
        >>> client.pipeline.add_feature_generator([{'name':'Absolute Area',
                                     'params':{"columns": ['accelx', 'accely', 'accelz'],
                                               "sample_rate": 10 }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxAbsArea  gen_0002_accelyAbsArea  gen_0003_accelzAbsArea
            0     s01                     1.0                     3.6                     2.9

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "AbsArea",
        [sample_rate],
        fg_algorithms.fg_area_absolute_area_w,
    )


fg_area_absolute_area_contracts = {
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


def fg_area_total_area_low_frequency(
    input_data: DataFrame,
    sample_rate: int,
    smoothing_factor: int,
    columns: List[str],
    **kwargs
):
    """
    Total area of low frequency components of the signal. It calculates total area
    by first applying a moving average filter on the signal with a smoothing factor.

    Args:
        sample_rate: float; Sampling rate of the signal
        smoothing_factor (int); Determines the amount of attenuation for
                          frequencies over the cutoff frequency.
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
        >>> client.pipeline.add_feature_generator([{'name':'Total Area of Low Frequency',
                                     'params':{"sample_rate": 10,
                                               "smoothing_factor": 5,
                                               "columns": ['accelx','accely','accelz']
                                              }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxTotAreaDc  gen_0002_accelyTotAreaDc  gen_0003_accelzTotAreaDc
            0     s01                       0.0                      0.72                      0.58


    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "TotAreaDc",
        [sample_rate, smoothing_factor],
        fg_algorithms.fg_area_total_area_low_frequency_w,
    )


fg_area_total_area_low_frequency_contracts = {
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
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 50],
            "c_param": 1,
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


def fg_area_absolute_area_low_frequency(
    input_data: DataFrame,
    sample_rate: int,
    smoothing_factor: int,
    columns: List[str],
    **kwargs
):
    """
    Absolute area of low frequency components of the signal. It calculates absolute area
    by first applying a moving average filter on the signal with a smoothing factor.

    Args:
        sample_rate: float; Sampling rate of the signal
        smoothing_factor (int); Determines the amount of attenuation for frequencies
                         over the cutoff frequency.
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
        >>> client.pipeline.add_feature_generator([{'name':'Absolute Area of Spectrum',
                                     'params':{"sample_rate": 10,
                                               "columns": ['accelx','accely','accelz']
                                              }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxAbsAreaSpec  gen_0002_accelyAbsAreaSpec  gen_0003_accelzAbsAreaSpec
            0     s01                       260.0                      2660.0                      1830.0


    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "AbsAreaDc",
        [sample_rate, smoothing_factor],
        fg_algorithms.fg_area_absolute_area_low_frequency_w,
    )


fg_area_absolute_area_low_frequency_contracts = {
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
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 50],
            "c_param": 1,
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


def fg_area_total_area_high_frequency(
    input_data: DataFrame,
    sample_rate: int,
    smoothing_factor: int,
    columns: List[str],
    **kwargs
):
    """
    Total area of high frequency components of the signal. It calculates total
    area by applying a moving average filter on the signal with a smoothing factor
    and subtracting the filtered signal from the original.

    Args:
        sample_rate: float; Sampling rate of the signal
        smoothing_factor (int): Determines the amount of attenuation for frequencies
                         over the cutoff frequency.
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
        >>> client.pipeline.add_feature_generator([{'name':'Total Area of High Frequency',
                                     'params':{"sample_rate": 10,
                                               "smoothing_factor": 5,
                                               "columns": ['accelx','accely','accelz']
                                              }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxTotAreaAc  gen_0002_accelyTotAreaAc  gen_0003_accelzTotAreaAc
            0     s01                       0.0                      0.12                      0.28

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "TotAreaAc",
        [sample_rate, smoothing_factor],
        fg_algorithms.fg_area_total_area_high_frequency_w,
    )


fg_area_total_area_high_frequency_contracts = {
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
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 50],
            "c_param": 1,
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


def fg_area_absolute_area_high_frequency(
    input_data: DataFrame,
    sample_rate: int,
    smoothing_factor: int,
    columns: List[str],
    **kwargs
):
    """
    Absolute area of high frequency components of the signal. It calculates absolute
    area by applying a moving average filter on the signal with a smoothing factor
    and subtracting the filtered signal from the original.


    Args:
        sample_rate: float; Sampling rate of the signal
        smoothing_factor (int): Determines the amount of attenuation for frequencies
                         over the cutoff frequency.
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
        >>> client.pipeline.add_feature_generator([{'name':'Absolute Area of High Frequency',
                                     'params':{"sample_rate": 10,
                                               "smoothing_factor": 5,
                                               "columns": ['accelx','accely','accelz']
                                              }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxAbsAreaAc  gen_0002_accelyAbsAreaAc  gen_0003_accelzAbsAreaAc
            0     s01                 76.879997                800.099976                470.160004

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "AbsAreaAc",
        [sample_rate, smoothing_factor],
        fg_algorithms.fg_area_absolute_area_high_frequency_w,
    )


fg_area_absolute_area_high_frequency_contracts = {
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
            "name": "smoothing_factor",
            "type": "int",
            "default": 5,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
            "range": [1, 50],
            "c_param": 1,
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


def fg_area_power_spectrum_density(
    input_data: DataFrame, sample_rate: int, columns: List[str], **kwargs
):
    """
    Absolute area of spectrum.

    Args:
        sample_rate: Sampling rate of the signal
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

        >>> client.pipeline.add_feature_generator([{'name':'Absolute Area of Spectrum',
                                     'params':{"sample_rate": 10,
                                               "columns": ['accelx','accely','accelz']
                                              }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxAbsAreaSpec  gen_0002_accelyAbsAreaSpec  gen_0003_accelzAbsAreaSpec
            0     s01                       260.0                      2660.0                      1830.0


    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "AbsAreaSpec",
        [sample_rate],
        fg_algorithms.fg_area_power_spectrum_density_w,
    )


fg_area_power_spectrum_density_contracts = {
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
