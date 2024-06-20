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

import pandas as pd
from numpy import ceil, diff, divide, fft, float64, hstack, int64, linspace, log2
from pandas import DataFrame, concat

from library.core_functions.utils import ma_filter
from library.exceptions import InputParameterException

# def filter_selection():
#     # Wp = np.divide(cutoff, np.divide(Fs,2.0)) # passband cutoff
#     # Rp = 1.0 # maximum allowable ripple in the passband in dB
#     # Rs = 60.0# minimum stopband attenuation in dB
#     # Ws = np.divide(np.multiply(cutoff, stopFactor), np.divide(Fs,2.0)) # stopband cutoff
#     # Niir, Wn = signal.buttord(Wp, Ws, Rp, Rs) # select the order and -3 dB cutoff of the butterworth filter
#     # The buttord implementation of scipy has some issues and is not matching matlab.
#     # I had to hardcode matlab output of buttord since the scipy outputs were different
#     Niir = 5
#     Wn = 0.0890974634052728
#     bIIR, aIIR = butter(Niir, Wn) # calculate the butterworth filter coeffcients
#     return (bIIR, aIIR)
#
# # The IIR filter is not generic enough. It is parameterized by the sample rate, but the butterworth coefficients
# # were calculated by hand for a specific application, so we are using the moving average filter instead.
# def iir_filter(data, fs, fc):
#     # Select a lowpass filter based on the sampling rate Fs
#     bIIR, aIIR = filter_selection()
#     # Filter the data using the selected filter
#     filtered_data = filtfilt(bIIR, aIIR, data)
#     return filtered_data


def calculate_total_area(data, fs):
    total_area = sum(data * (1.0 / fs))
    return total_area


def calculate_abs_area(data, fs):
    abs_area = sum(abs(data) * (1.0 / fs))
    return abs_area


def calculate_conv_area(data, fs):
    t = divide(range(0, len(data)), fs)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    area = abs(sum(data * dt))
    return area


def calculate_abs_conv_area(data, fs):
    t = divide(range(0, len(data)), fs)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    abs_area = sum(abs(data) * dt)
    return abs_area


"""
def calculate_conv_area_dc(data, fs, smoothing_factor):
    t = divide(range(0, len(data)), fs)
    data_dc = ma_filter(data, smoothing_factor)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    area = abs(sum(data_dc * dt))
    return area

def calculate_abs_area_dc(data, fs, smoothing_factor):
    t = divide(range(0, len(data)), fs)
    data_dc = ma_filter(data, smoothing_factor)
    data_dc = pd.Series(data_dc)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    abs_area = sum(abs(data_dc) * dt)
    return abs_area

def calculate_conv_area_ac(data, fs, smoothing_factor):
    t = divide(range(0, len(data)), fs)
    data_ac = data - ma_filter(data, smoothing_factor)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    area = abs(sum(data_ac * dt))
    return area

def calculate_abs_area_ac(data, fs, smoothing_factor):
    t = divide(range(0, len(data)), fs)
    data_ac = data - ma_filter(data, smoothing_factor)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    abs_area = sum(abs(data_ac) * dt)
    return abs_area
"""


def calculate_conv_area_dc(data, fs, smoothing_factor):
    t = divide(range(0, len(data) - smoothing_factor + 1), fs)
    data_dc = ma_filter(data, smoothing_factor)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    area = abs(sum(data_dc * dt))
    return area


def calculate_abs_area_dc(data, fs, smoothing_factor):
    t = divide(range(0, len(data) - smoothing_factor + 1), fs)
    data_dc = ma_filter(data, smoothing_factor)
    data_dc = pd.Series(data_dc)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    abs_area = sum(abs(data_dc) * dt)
    return abs_area


def calculate_conv_area_ac(data, fs, smoothing_factor):
    t = divide(range(0, len(data) - smoothing_factor + 1), fs)
    midpoint = smoothing_factor / 2
    data_ac = data[midpoint : len(data) - midpoint] - ma_filter(data, smoothing_factor)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    area = abs(sum(data_ac * dt))
    return area


def calculate_abs_area_ac(data, fs, smoothing_factor):
    t = divide(range(0, len(data) - smoothing_factor + 1), fs)
    midpoint = smoothing_factor / 2
    data_ac = data[midpoint : len(data) - midpoint] - ma_filter(data, smoothing_factor)
    dt = diff(t, 1)
    dt = hstack((dt, dt[-1]))
    abs_area = sum(abs(data_ac) * dt)
    return abs_area


def calculate_abs_area_spec(data, fs):
    Y, f = spectrum(data, fs)
    dt = diff(f, 1)
    dt = hstack((dt, dt[-1]))
    psd_area = sum(Y * dt)
    return psd_area


def nextpow2(n):
    m_f = log2(n)
    m_i = ceil(m_f)
    return 2 ** m_i


def spectrum(data, fs):
    L = len(data)
    NFFT = nextpow2(L)
    NFFT = NFFT.astype(int64)
    ft = fft.fft(data, NFFT)
    PSD = (ft * ft.conjugate()).real
    f = linspace(0, 1, (NFFT)) * (fs)
    return PSD, f


def total_area(input_data, sample_rate, columns, **kwargs):
    """
    Total area under the signal. Total area = sum(signal(t)*dt), where
    signal(t) is signal value at time t, and dt is sampling time (dt = 1/sample_rate).

    Args:
        input_data: input dataframe

        sample_rate: Sampling rate of the signal

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                             'Class': ['Crawling'] * 20,
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
                19  Crawling    1     s01      -1

        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Total Area"],
                        params = {"group_columns": ['Subject', 'Class', 'Rep']},
                                  function_defaults={"columns":['accelx'],
                                                     'sample_rate' : 10.0})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                      Class   Rep Subject  gen_0001_accelxTotArea
                0  Crawling    0     s01                     0.4
                1  Crawling    1     s01                    -0.5

    """
    result = DataFrame()
    for col in columns:
        feature = calculate_total_area(input_data[col], sample_rate)
        feature_name = col + "TotArea"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


total_area_contracts = {
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


def absolute_area(input_data, sample_rate, columns, **kwargs):
    """
    Absolute area of the signal. Absolute area = sum(abs(signal(t)) dt), where
    `abs(signal(t))` is absolute signal value at time t, and dt is sampling time (dt = 1/sample_rate).

    Args:
        input_data: Input dataframe

        sample_rate: Sampling rate of the signal

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20,
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
                19  Crawling    1     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Absolute Area"],
                        params = {"group_columns": ['Subject', 'Class', 'Rep']},
                        function_defaults={"columns":['accelx'], 'sample_rate' : 10.})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxAbsArea
            0  Crawling    0     s01                     1.8
            1  Crawling    1     s01                     2.9
    """
    sample_rate = float64(sample_rate)
    result = DataFrame()
    for col in columns:
        feature = calculate_abs_area(input_data[col], sample_rate)
        feature_name = col + "AbsArea"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


absolute_area_contracts = {
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


def total_area_low_frequency(
    input_data, sample_rate, smoothing_factor, columns, **kwargs
):
    """
    Total area of low frequency components of the signal. It calculates total area
    by first applying a moving average filter on the signal with a smoothing factor.

    Args:
        input_data: Input dataframe

        sample_rate: float; Sampling rate of the signal

        smoothing_factor: int(odd); Determines the amount of attenuation for
                          frequencies over the cutoff frequency. An 'odd' number is expected.

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20,
                              'Rep' : [0] * 8 + [1] * 12})
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
                19  Crawling    1     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Total Area of Low Frequency"],
                         params = {"group_columns": ['Subject', 'Class', 'Rep']},
                                    function_defaults={"columns":['accelx'],
                                                       'sample_rate' : 10.,
                                                       'smoothing_factor' :3})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxTotAreaDc
            0  Crawling    0     s01                  0.466667
            1  Crawling    1     s01                  0.133333


    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    sample_rate = float64(sample_rate)
    result = DataFrame()
    for col in columns:
        feature = calculate_conv_area_dc(input_data[col], sample_rate, smoothing_factor)
        feature_name = col + "TotAreaDc"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


total_area_low_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "sample_rate",
            "type": "numeric",
            "handle_by_set": True,
            "description": "Sample rate of the sensor data",
        },
        {
            "name": "smoothing_factor",
            "type": "int",
            "handle_by_set": True,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
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


def absolute_area_low_frequency(
    input_data, sample_rate, smoothing_factor, columns, **kwargs
):
    """
    Absolute area of low frequency components of the signal. It calculates absolute area
    by first applying a moving average filter on the signal with a smoothing factor.

    Args:
        input_data: Input dataframe

        sample_rate: float; Sampling rate of the signal

        smoothing_factor: int (odd); Determines the amount of attenuation
                         for frequencies over the cutoff frequency. An 'odd' number is expected.

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20,
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
                19  Crawling    1     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Absolute Area of Low Frequency"],
                        params = {"group_columns": ['Subject', 'Class', 'Rep']},
                                 function_defaults={"columns":['accelx'],
                                 'sample_rate' : 10.,
                                 'smoothing_factor' :2})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxTotAreaDc
            0  Crawling    0     s01                      0.25
            1  Crawling    1     s01                      0.40
    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    sample_rate = float64(sample_rate)
    result = DataFrame()
    for col in columns:
        feature = calculate_abs_area_dc(input_data[col], sample_rate, smoothing_factor)
        feature_name = col + "AbsAreaDc"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


absolute_area_low_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "sample_rate",
            "type": "numeric",
            "handle_by_set": True,
            "description": "Sample rate of the sensor data",
        },
        {
            "name": "smoothing_factor",
            "type": "int",
            "handle_by_set": True,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
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


def total_area_high_frequency(
    input_data, sample_rate, smoothing_factor, columns, **kwargs
):
    """
    Total area of high frequency components of the signal. It calculates total
     area by applying a moving average filter on the signal with a smoothing factor
      and subtracting the filtered signal from the original.

    Args:
        input_data: Input dataframe

        sample_rate: float; Sampling rate of the signal

        smoothing_factor: int(odd); Determines the amount of attenuation for
                             frequencies over the cutoff frequency. An 'odd' number is expected.

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20,
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
                19  Crawling    1     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Total Area of High Frequency"],
                        params = {"group_columns": ['Subject', 'Class', 'Rep']},
                         function_defaults={"columns":['accelx'],
                                                     'sample_rate' : 10.,
                                                     'smoothing_factor' :2})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxTotAreaAc
            0  Crawling    0     s01                      0.15
            1  Crawling    1     s01                      0.10
    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    sample_rate = float64(sample_rate)
    result = DataFrame()
    for col in columns:
        feature = calculate_conv_area_ac(input_data[col], sample_rate, smoothing_factor)
        feature_name = col + "TotAreaAc"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


total_area_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "sample_rate",
            "type": "numeric",
            "handle_by_set": True,
            "description": "Sample rate of the sensor data",
        },
        {
            "name": "smoothing_factor",
            "type": "int",
            "handle_by_set": True,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
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


def absolute_area_high_frequency(
    input_data, sample_rate, smoothing_factor, columns, **kwargs
):
    """
    Absolute area of high frequency components of the signal. It calculates absolute
    area by applying a moving average filter on the signal with a smoothing factor
    and subtracting the filtered signal from the original.


    Args:
        input_data: Input dataframe

        sample_rate: float; Sampling rate of the signal

        smoothing_factor: int (odd); Determines the amount of attenuation for frequencies
                         over the cutoff frequency. An 'odd' number is expected.

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20,
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
                19  Crawling    1     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Absolute Area of High Frequency"],
                    params = {"group_columns": ['Subject', 'Class', 'Rep']},
                              function_defaults={"columns":['accelx'],
                                                'sample_rate' : 10.,
                                                'smoothing_factor' :2})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxTotAreaAc
            0  Crawling    0     s01                      0.15
            1  Crawling    1     s01                      0.10
    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    sample_rate = float64(sample_rate)
    result = DataFrame()
    for col in columns:
        feature = calculate_abs_area_ac(input_data[col], sample_rate, smoothing_factor)
        feature_name = col + "AbsAreaAc"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


absolute_area_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "sample_rate",
            "type": "numeric",
            "handle_by_set": True,
            "description": "Sample rate of the sensor data",
        },
        {
            "name": "smoothing_factor",
            "type": "int",
            "handle_by_set": True,
            "description": "Determines the amount of attenuation for frequencies over the cutoff frequency",
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


def absolute_area_spectrum(input_data, sample_rate, columns, **kwargs):
    """
    Absolute area of spectrum.

    Args:
        input_data: DataFrame

        sample_rate: Sampling rate of the signal

        columns: List of str; Set of columns on which to apply the feature generator

        group_columns: List of str; Set of columns by which to aggregate

        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20,
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
                19  Crawling    1     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Absolute Area of Spectrum"],
                params = {"group_columns": ['Subject', 'Class', 'Rep']},
                 function_defaults={"columns":['accelx'],
                                    'sample_rate' : 10.,
                                    'smoothing_factor' :2})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxAbsAreaSpec
            0  Crawling    0     s01                    8.546426
            1  Crawling    1     s01                    7.643549
    """
    sample_rate = float64(sample_rate)
    result = DataFrame()
    for col in columns:
        feature = calculate_abs_area_spec(input_data[col], sample_rate)
        feature_name = col + "AbsAreaSpec"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


absolute_area_spectrum_contracts = {
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
