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

from library.core_functions.utils import ma_filter
from library.exceptions import InputParameterException
from pandas import DataFrame, concat

"""
def filter_selection():
    # Wp = np.divide(cutoff, np.divide(Fs,2.0)) # passband cutoff
    # Rp = 1.0 # maximum allowable ripple in the passband in dB
    # Rs = 60.0# minimum stopband attenuation in dB
    # Ws = np.divide(np.multiply(cutoff, stopFactor), np.divide(Fs,2.0)) # stopband cutoff
    # Niir, Wn = signal.buttord(Wp, Ws, Rp, Rs) # select the order and -3 dB cutoff of the butterworth filter
    # The buttord implementation of scipy has some issues and is not matching matlab.
    # I had to hardcode matlab output of buttord since the scipy outputs were different
    Niir = 5
    Wn = 0.0890974634052728
    bIIR, aIIR = butter(Niir, Wn) # calculate the butterworth filter coeffcients
    return (bIIR, aIIR)

# The IIR filter is not generic enough. It is parameterized by the sample rate, but the butterworth coefficients
# were calculated by hand for a specific application, so we are using the moving average filter instead.
def iir_filter(data, sample_rate, fc):
    # Select a lowpass filter based on the sampling rate Fs
    bIIR, aIIR = filter_selection()
    # Filter the data using the selected filter
    filtered_data = filtfilt(bIIR, aIIR, data)
    return filtered_data
"""

"""
def max_p2p_ac(data, smoothing_factor):
    data_ac = data - ma_filter(data, smoothing_factor)
    return max(data_ac) - min(data_ac)

def max_p2p_dc(data, smoothing_factor):
    data_dc = ma_filter(data, smoothing_factor)
    return max(data_dc) - min(data_dc)
"""


def max_p2p_ac(data, smoothing_factor):
    midpoint = smoothing_factor / 2
    data_ac = data[midpoint : len(data) - midpoint] - ma_filter(data, smoothing_factor)
    return max(data_ac) - min(data_ac)


def max_p2p_dc(data, smoothing_factor):
    data_dc = ma_filter(data, smoothing_factor)
    return max(data_dc) - min(data_dc)


def ratio_high_frequency(input_data, smoothing_factor, columns, **kwargs):
    """
    Ratio of peak to peak of high frequency between two halves. The high frequency
    signal is calculated by subtracting the moving average filter output from the original signal.

    Args:
        input_data:
        smoothing_factor: int (odd); Determines the amount of attenuation for
          frequencies over the cutoff frequency. An 'odd' number is expected.
          of elements in individual columns should be al least
          three times the smoothing factor. An 'odd' number is expected.
        columns: List of str; Set of columns on which to apply the feature generator
        group_columns: List of str; Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,'Class': ['Crawling'] * 20 ,'Rep': [0] * 20})
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
            8   Crawling    0     s01      -3
            9   Crawling    0     s01      -1
            10  Crawling    0     s01       1
            11  Crawling    0     s01      -3
            12  Crawling    0     s01      -4
            13  Crawling    0     s01       1
            14  Crawling    0     s01       2
            15  Crawling    0     s01       6
            16  Crawling    0     s01       2
            17  Crawling    0     s01      -3
            18  Crawling    0     s01      -2
            19  Crawling    0     s01      -1

        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Ratio of Peak to Peak of High Frequency between two halves"],
                params = {"group_columns": ['Subject', 'Class', 'Rep']},
                function_defaults={"columns":['accelx'],
                                  'smoothing_factor' : 3})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxACRatio
            0  Crawling    0     s01                1.263158
    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    if input_data["data"].shape[1] < 2 * 3 * smoothing_factor:
        raise Exception(
            "This feature generator requires all groups to have at least 2*3*smoothing_factor = {0} samples."
            "You can lower the smoothing_factor, change your query, or omit this feature.".format(
                2 * 3 * smoothing_factor
            )
        )

    result = DataFrame()
    for col in columns:
        feature = max_p2p_ac(
            input_data[col][int(len(input_data[col]) / 2) :], smoothing_factor
        ) / max_p2p_ac(
            input_data[col][: int(len(input_data[col]) / 2)], smoothing_factor
        )
        feature_name = col + "ACRatio"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


ratio_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
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


def difference_high_frequency(input_data, smoothing_factor, columns, **kwargs):
    """
    Difference of peak to peak of high frequency between two halves.
    The high frequency signal is calculated by subtracting the moving
    average filter output from the original signal.

    Args:
        input_data:
        smoothing_factor: int(odd); Determines the amount of attenuation for
            frequencies over the cutoff frequency. The number of elements in
            individual columns should be at lest three times the smoothing factor.
            An 'odd' number is expected.
        columns: List of str; Set of columns on which to apply the feature generator
        group_columns: List of str; Set of columns by which to aggregate

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20 ,
                              'Rep': [0] * 20})
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
            8   Crawling    0     s01      -3
            9   Crawling    0     s01      -1
            10  Crawling    0     s01       1
            11  Crawling    0     s01      -3
            12  Crawling    0     s01      -4
            13  Crawling    0     s01       1
            14  Crawling    0     s01       2
            15  Crawling    0     s01       6
            16  Crawling    0     s01       2
            17  Crawling    0     s01      -3
            18  Crawling    0     s01      -2
            19  Crawling    0     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Difference of Peak to Peak of High Frequency between two halves"],
                params = {"group_columns": ['Subject', 'Class', 'Rep']},
                function_defaults={"columns":['accelx'], 'smoothing_factor' : 3})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxACDiff
            0  Crawling    0     s01              -1.666667
    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    if input_data["data"].shape[1] < 2 * 3 * smoothing_factor:
        raise Exception(
            "This feature generator requires all groups to have at least 2*3*smoothing_factor = {0} samples."
            "You can lower the smoothing_factor, change your query, or omit this feature.".format(
                2 * 3 * smoothing_factor
            )
        )
    result = DataFrame()
    for col in columns:
        feature = max_p2p_ac(
            input_data[col][: int(len(input_data[col]) / 2)], smoothing_factor
        ) - max_p2p_ac(
            input_data[col][int(len(input_data[col]) / 2) :], smoothing_factor
        )
        feature_name = col + "ACDiff"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


difference_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
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


def global_p2p_high_frequency(input_data, smoothing_factor, columns, **kwargs):
    """
    Global peak to peak of high frequency. The high frequency signal is calculated by
    subtracting the moving average filter output from the original signal.

    Args:
        input_data:
        smoothing_factor: int (odd); Determines the amount of attenuation for frequencies
          over the cutoff frequency. The number of elements in individual
          columns should be al least three times the smoothing factor. An 'odd' number is expected.
        columns: List of str; Set of columns on which to apply the feature generator
        group_columns: List of str; Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20 ,
                              'Rep': [0] * 20})
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
            8   Crawling    0     s01      -3
            9   Crawling    0     s01      -1
            10  Crawling    0     s01       1
            11  Crawling    0     s01      -3
            12  Crawling    0     s01      -4
            13  Crawling    0     s01       1
            14  Crawling    0     s01       2
            15  Crawling    0     s01       6
            16  Crawling    0     s01       2
            17  Crawling    0     s01      -3
            18  Crawling    0     s01      -2
            19  Crawling    0     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Global Peak to Peak of High Frequency"],
                params = {"group_columns": ['Subject', 'Class', 'Rep']},
                function_defaults={"columns":['accelx'],
                                   'smoothing_factor' : 3})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxMaxP2PGlobalAC
            0  Crawling    0     s01                            8.0
    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    result = DataFrame()
    for col in columns:
        feature = max_p2p_ac(input_data[col], smoothing_factor)
        feature_name = col + "MaxP2PGlobalAC"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


global_p2p_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
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


def global_p2p_low_frequency(input_data, smoothing_factor, columns, **kwargs):
    """
    Global peak to peak of low frequency. The low frequency signal is calculated by
    applying a moving average filter with a smoothing factor.

    Args:
        input_data:
        smoothing_factor: int (odd); Determines the amount of attenuation for
          frequencies over the cutoff frequency. An 'odd' number is expected. An 'odd' number is expected.
        columns: List of str; Set of columns on which to apply the feature generator
        group_columns: List of str; Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                                'Class': ['Crawling'] * 20 ,
                                'Rep': [0] * 20})
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
            8   Crawling    0     s01      -3
            9   Crawling    0     s01      -1
            10  Crawling    0     s01       1
            11  Crawling    0     s01      -3
            12  Crawling    0     s01      -4
            13  Crawling    0     s01       1
            14  Crawling    0     s01       2
            15  Crawling    0     s01       6
            16  Crawling    0     s01       2
            17  Crawling    0     s01      -3
            18  Crawling    0     s01      -2
            19  Crawling    0     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Global Peak to Peak of Low Frequency"],
                        params = {"group_columns": ['Subject', 'Class', 'Rep']},
                        function_defaults={"columns":['accelx'],
                                            'smoothing_factor' : 3})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxMaxP2PGlobalDC
            0  Crawling    0     s01                       5.333333
    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    result = DataFrame()
    for col in columns:
        feature = max_p2p_dc(input_data[col], smoothing_factor)
        feature_name = col + "MaxP2PGlobalDC"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


global_p2p_low_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
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


def max_p2p_half_high_frequency(input_data, smoothing_factor, columns, **kwargs):
    """
    Max Peak to Peak of first half of High Frequency. The high frequency signal
    is calculated by subtracting the moving average filter output from the original signal.

    Args:
        input_data:
        smoothing_factor: int (odd); Determines the amount of attenuation for frequencies
          over the cutoff frequency. An 'odd' number is expected.
        columns: List of str; Set of columns on which to apply the feature generator
        group_columns: List of str; Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20 ,
                               'Rep': [0] * 20})
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
            8   Crawling    0     s01      -3
            9   Crawling    0     s01      -1
            10  Crawling    0     s01       1
            11  Crawling    0     s01      -3
            12  Crawling    0     s01      -4
            13  Crawling    0     s01       1
            14  Crawling    0     s01       2
            15  Crawling    0     s01       6
            16  Crawling    0     s01       2
            17  Crawling    0     s01      -3
            18  Crawling    0     s01      -2
            19  Crawling    0     s01      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Max Peak to Peak of first half of High Frequency"],
                 params = {"group_columns": ['Subject', 'Class', 'Rep']},
                 function_defaults={"columns":['accelx'],
                                    'smoothing_factor' : 3})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxMaxP2P1stHalfAC
            0  Crawling    0     s01                        6.333333


    """
    if smoothing_factor % 2 == 0:
        raise InputParameterException(
            "The value of smoothing factor can be 'odd' only."
        )

    if input_data["data"].shape[1] < 2 * 3 * smoothing_factor:
        raise Exception(
            "This feature generator requires all groups to have at least 2*3*smoothing_factor = {0} samples."
            "You can lower the smoothing_factor, change your query, or omit this feature.".format(
                2 * 3 * smoothing_factor
            )
        )

    result = DataFrame()
    for col in columns:
        feature = max_p2p_ac(
            input_data[col][: int(len(input_data[col]) / 2)], smoothing_factor
        )
        feature_name = col + "MaxP2P1stHalfAC"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


max_p2p_half_high_frequency_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
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


def peak_to_peak(input_data, columns, **kwargs):
    """
    Global Peak to Peak of signal.

    Args:
        input_data: DataFrame
        columns: (list of str): Set of columns on which to apply the feature generator
        group_columns:(list of str): Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20 ,
                               'Rep': [0] * 10 + [1] *10 })
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
            8   Crawling    0     s01      -3
            9   Crawling    0     s01      -1
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
        >>> client.pipeline.add_feature_generator(["Global Peak to Peak"],
                    params = {"group_columns": ['Subject', 'Class', 'Rep']},
                    function_defaults={"columns":['accelx']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0001_accelxP2P
            0  Crawling    0     s01                   8
            1  Crawling    1     s01                  10
    """
    result = DataFrame()
    for col in columns:
        feature = max(input_data[col]) - min(input_data[col])
        feature_name = col + "P2P"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


peak_to_peak_contracts = {
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


def min_max_sum(input_data, columns, **kwargs):
    """
    This function is the sum of the maximum and minimum values. It is also
    used as the 'min max amplitude difference'.

    Args:
        input_data: DataFrame
        columns: (list of str): Set of columns on which to apply the feature generator
        group_columns:(list of str): Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20 ,
                               'Rep': [0] * 10 + [1] *10 })
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
            8   Crawling    0     s01      -3
            9   Crawling    0     s01      -1
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
        >>> client.pipeline.add_feature_generator(["Global Min Max Sum"],
                    params = {"group_columns": ['Subject', 'Class', 'Rep']},
                    function_defaults={"columns":['accelx']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject   accelxMinMaxSum
            0  Crawling    0     s01                 2
            1  Crawling    1     s01                 2
    """
    result = DataFrame()

    for col in columns:
        feature = max(input_data[col]) + min(input_data[col])
        feature_name = col + "MinMaxSum"
        result = concat([result, DataFrame([feature], columns=[feature_name])], axis=1)
    return result


min_max_sum_contracts = {
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
