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


def fg_frequency_dominant_frequency(
    input_data: DataFrame, sample_rate: int, columns: List[str], **kwargs
):
    """
    Calculate the dominant frequency for each specified signal. For each column,
    find the frequency at which the signal has highest power.

    Note: the current FFT length is 512, data larger than this will be truncated.
    Data smaller than this will be zero padded

    Args:
        columns: List of columns on which `dominant_frequency` needs to be calculated

    Returns:
        DataFrame of `dominant_frequency` for each column and the specified group_columns

    Examples:
        >>> import matplotlib.pyplot as plt
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
        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:].tolist()


        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class']
                           )

        >>> client.pipeline.add_feature_generator([{'name':'Dominant Frequency',
                                     'params':{"columns": ['accelx', 'accely', 'accelz' ],
                                              "sample_rate" : sample
                                              }
                                    }])

        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               Class Subject  gen_0001_accelxDomFreq  gen_0002_accelyDomFreq  gen_0003_accelzDomFreq
            0      0     s01                    22.0                    28.0                    34.0
            1      1     s01                    22.0                    26.0                    52.0

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "DomFreq",
        [sample_rate],
        fg_algorithms.fg_frequency_dominant_frequency_w,
    )


fg_frequency_dominant_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "sample_rate",
            "type": "numeric",
            "default": 100,
            "description": "Sample rate of the sensor data",
            "range": [1, 100000],
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
    "output_contract": [
        {
            "name": "output_data",
            "type": "DataFrame",
            "scratch_buffer": {"type": "fixed_value", "value": 512},
        }
    ],
}


def fg_frequency_peak_frequencies(
    input_data: DataFrame,
    columns: List[str],
    sample_rate: int,
    window_type: str,
    num_peaks: int,
    min_frequency: int,
    max_frequency: int,
    threshold: int,
    **kwargs
) -> DataFrame:
    """
    Calculate the peak frequencies for each specified signal. For each column, find the frequencies at which the signal
    has highest power.

    Note: The current FFT length is 512. Data larger than this will be truncated. Data smaller than this will be zero padded.
          The FFT is computed and the cutoff frequency is converted to a bin based on the following formula:
          fft_min_bin_index = (min_freq * FFT_length / sample_rate)
          fft_max_bin_index = (max_freq * FFT_length / sample_rate)

    Args:
        input_data (DataFrame): The input data.
        columns (List[str]): A list of column names on which 'dominant_frequency' needs to be calculated.
        sample_rate (int): The sample rate of the sensor data.
        window_type (str): The type of window to apply to the signal before taking the FFT. Currently only 'hanning'
                           window is supported.
        num_peaks (int): The number of peaks to identify.
        min_frequency (int): The minimum frequency bound to look for peaks.
        max_frequency (int): The maximum frequency bound to look for peaks.
        threshold (int): The threshold value that a peak must be above to be considered a peak.

    Returns:
        DataFrame: DataFrame containing the 'peak frequencies' for each column and the specified group_columns.
    """

    if window_type.lower() not in ["hanning", "boxcar"]:
        raise Exception("window type must be either hanning or boxcar")

    params = [sample_rate, min_frequency, max_frequency, threshold, num_peaks, 0]
    result_columns = ["PeakFreq_{0:06}".format(index) for index in range(num_peaks)]
    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        result_columns,
        params,
        fg_algorithms.fg_frequency_peak_frequencies_w,
    )


fg_frequency_peak_frequencies_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "sample_rate",
            "type": "numeric",
            "description": "Sample rate of the sensor data",
            "default": 100,
            "range": [1, 100000],
            "c_param": 0,
        },
        {
            "name": "min_frequency",
            "type": "numeric",
            "description": "min cutoff frequency",
            "default": 0,
            "range": [0, 512],
            "c_param": 1,
        },
        {
            "name": "max_frequency",
            "type": "numeric",
            "description": "max cutoff frequency",
            "default": 500,
            "range": [0, 512],
            "c_param": 2,
        },
        {
            "name": "threshold",
            "type": "numeric",
            "description": "threshold value a peak must be above",
            "default": 0.2,
            "range": [0.0, 1.0],
            "c_param": 3,
        },
        {
            "name": "num_peaks",
            "type": "numeric",
            "default": 2,
            "description": "number of frequency peaks to find",
            "range": [1, 12],
            "c_param": 4,
        },
        {
            "name": "window_type",
            "type": "str",
            "description": "window function to use before fft",
            "default": "hanning",
            "options": [{"name": "hanning"}],
            "c_param_mapping": {"hanning": 0},
            "c_param": 5,
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
            "scratch_buffer": {"type": "fixed_value", "value": 512},
        }
    ],
}


def fg_frequency_spectral_entropy(input_data: DataFrame, columns: List[str], **kwargs):
    """
    Calculate the spectral entropy for each specified signal. For each column,
    first calculate the power spectrum, and then using the power spectrum, calculate
    the entropy in the spectral domain. Spectral entropy measures the spectral
    complexity of the signal.

    Note: the current FFT length is 512, data larger than this will be truncated.
    Data smaller than this will be zero padded

    Args:
        columns: List of all columns for which `spectral_entropy` is to be calculated

    Returns:
        DataFrame of `spectral_entropy` for each column and the specified group_columns

    Examples:
        >>> import matplotlib.pyplot as plt
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
        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:].tolist()


        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class']
                           )

        >>> client.pipeline.add_feature_generator([{'name':'Spectral Entropy',
                                     'params':{"columns": ['accelx', 'accely', 'accelz' ]}
                                    }])


        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
               Class Subject  gen_0001_accelxSpecEntr  gen_0002_accelySpecEntr  gen_0003_accelzSpecEntr
            0      0     s01                  1.97852                 1.983631                 1.981764
            1      1     s01                  1.97852                 2.111373                 2.090683

    """

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        "SpecEntr",
        [],
        fg_algorithms.fg_frequency_spectral_entropy_w,
    )


fg_frequency_spectral_entropy_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "description": "Input signal data"},
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
            "scratch_buffer": {"type": "fixed_value", "value": 512},
        }
    ],
}


def fg_frequency_power_spectrum(
    input_data: DataFrame,
    columns: List[str],
    window_type: str = "hanning",
    number_of_bins: int = 16,
    **kwargs
) -> DataFrame:
    """
    Calculate the power spectrum for the signal. The resulting power spectrum will be binned into number_of_bins.

    Note: The current FFT length is 512. Data larger than this will be truncated. Data smaller than this will be zero padded.

    Args:
        input_data (DataFrame): The input data.
        columns (List[str]): A list of column names to use for the frequency calculation.
        window_type (str): The type of window to apply to the signal before taking the FFT. Defaults to 'hanning'.
        number_of_bins (int): The number of bins to use to compute the power spectrum.

    Returns:
        DataFrame: DataFrame containing the 'power spectrum' for each column and the specified group_columns.
    """

    params = [
        number_of_bins,
        fg_frequency_power_spectrum_contracts["input_contract"][3]["c_param_mapping"][
            window_type
        ],
    ]

    result_columns = [
        "PowerSpec_{0:06}".format(index) for index in range(number_of_bins)
    ]
    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        result_columns,
        params,
        fg_algorithms.fg_frequency_power_spectrum_w,
    )


fg_frequency_power_spectrum_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
            "num_columns": 1,
        },
        {
            "name": "number_of_bins",
            "type": "numeric",
            "default": 16,
            "description": "number of bins to use to compute the power spectrum",
            "range": [4, 256],
            "c_param": 0,
        },
        {
            "name": "window_type",
            "type": "str",
            "description": "window function to use before fft",
            "default": "hanning",
            "options": [{"name": "hanning"}],
            "c_param_mapping": {"hanning": 0},
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
            "family": True,
            "output_formula": "params['number_of_bins']",
            "scratch_buffer": {"type": "fixed_value", "value": 512},
        }
    ],
}


def fg_frequency_mfcc(
    input_data: DataFrame,
    columns: List[str],
    sample_rate: int,
    cepstra_count: int,
    **kwargs
) -> DataFrame:
    """
    Translates the data stream(s) from a segment into a feature vector of Mel-Frequency Cepstral Coefficients (MFCC).
    The features are derived in the frequency domain that mimic human auditory response.

    Note: The current FFT length is 512. Data larger than this will be truncated. Data smaller than this will be zero padded.

    Args:
        input_data (DataFrame): The input data.
        columns (list of strings): Names of the sensor streams to use.
        sample_rate (int): Sampling rate
        cepstra_count (int): Number of coefficients to generate.

    Returns:
        DataFrame: Feature vector of MFCC coefficients.

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
        >>> client.pipeline.add_feature_generator([{'name':'MFCC', 'params':{"columns": ['accelx'],
                                                              "sample_rate": 10,
                                                              "cepstra_count": 23 }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxmfcc_000000  gen_0001_accelxmfcc_000001 ... gen_0001_accelxmfcc_000021  gen_0001_accelxmfcc_000022
            0     s01                    131357.0                    -46599.0 ...                      944.0                       308.0

    """

    params = [sample_rate, cepstra_count]
    result_names = ["mfcc_{0:06}".format(index) for index in range(cepstra_count)]

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, result_names, params, fg_algorithms.fg_frequency_mfcc_w
    )


fg_frequency_mfcc_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
            "num_columns": 1,
        },
        {
            "name": "sample_rate",
            "type": "int",
            "default": 16000,
            "c_param": 0,
            "range": [1, 16000],
        },
        {
            "name": "cepstra_count",
            "type": "int",
            "default": 23,
            "c_param": 1,
            "range": [1, 23],
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
            "output_formula": "params['cepstra_count']",
            "scratch_buffer": {"type": "fixed_value", "value": 512},
        }
    ],
}


def fg_frequency_mfe(
    input_data: DataFrame, columns: List[str], num_filters: int, **kwargs
) -> DataFrame:
    """
    Translates the data stream(s) from a segment into a feature vector of Mel-Frequency Energy (MFE).
    The power spectrum of each frame of audio is passed through a filterbank of triangular filters
    which are spaced uniformly in the mel-frequency domain.

    Args:
        input_data (DataFrame): The input data.
        columns (list of strings): Names of the sensor streams to use.
        num_filters (int): Number of filters for the mel-scale filterbank.

    Returns:
        DataFrame: Feature vector of MFE coefficients.

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
        >>> client.pipeline.add_feature_generator([{'name':'MFE', 'params':{"columns": ['accelx'],
                                                              "num_filters": 23 }}])
        >>> result, stats = client.pipeline.execute()

        >>> print result
            out:
              Subject  gen_0001_accelxmfe_000000  gen_0001_accelxmfe_000001 ... gen_0001_accelxmfe_000021  gen_0001_accelxmfe_000022
            0     s01                    131357.0                    -46599.0 ...                      944.0                       308.0

    """

    params = [num_filters]
    result_names = ["mfe_{0:06}".format(index) for index in range(num_filters)]

    return fg_algorithms.run_feature_generator_c(
        input_data, columns, result_names, params, fg_algorithms.fg_frequency_mfe_w
    )


fg_frequency_mfe_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
            "num_columns": 1,
        },
        {
            "name": "num_filters",
            "type": "int",
            "default": 23,
            "c_param": 0,
            "range": [1, 23],
            "description": "The number of mel filter bank values to return.",
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
            "output_formula": "params['num_filters']",
            "scratch_buffer": {"type": "fixed_value", "value": 512},
        }
    ],
}


def fg_frequency_harmonic_product_spectrum(
    input_data: DataFrame, columns: List[str], harmonic_coefficients: int, **kwargs
) -> DataFrame:
    """


    Args:
        input_data (DataFrame): The input data.
        columns (list of strings): Names of the sensor streams to use.
        harmonic_coefficients (int): Number of harmonic coefficients to use

    Returns:
        DataFrame: Product Spectrum
    """

    params = [harmonic_coefficients]
    result_names = [
        "hpc_{0:06}".format(index) for index in range(256 // harmonic_coefficients)
    ]

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        result_names,
        params,
        fg_algorithms.fg_frequency_harmonic_product_spectrum_w,
    )


fg_frequency_harmonic_product_spectrum_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
            "num_columns": 1,
        },
        {
            "name": "harmonic_coefficients",
            "type": "int",
            "default": 5,
            "c_param": 0,
            "range": [2, 10],
            "description": "The number of mel filter bank values to return.",
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
            "output_formula": "256//params['harmonic_coefficients']",
            "scratch_buffer": {"type": "fixed_value", "value": 512},
        }
    ],
}


def fg_frequency_peak_harmonic_product_spectrum(
    input_data: DataFrame, columns: List[str], harmonic_coefficients: int, **kwargs
) -> DataFrame:
    """


    Args:
        input_data (DataFrame): The input data.
        columns (list of strings): Names of the sensor streams to use.
        harmonic_coefficients (int): Number of harmonic coefficients to use

    Returns:
        DataFrame: Product Spectrum
    """

    params = [harmonic_coefficients]
    result_names = ["phpc_{0:06}".format(index) for index in range(2)]

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        result_names,
        params,
        fg_algorithms.fg_frequency_peak_harmonic_product_spectrum_w,
    )


fg_frequency_peak_harmonic_product_spectrum_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
            "num_columns": 1,
        },
        {
            "name": "harmonic_coefficients",
            "type": "int",
            "default": 5,
            "c_param": 0,
            "range": [2, 10],
            "description": "The number of mel filter bank values to return.",
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
            "output_formula": "2",
            "scratch_buffer": {"type": "fixed_value", "value": 512},
        }
    ],
}
