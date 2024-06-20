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

import copy
import os
from ctypes import c_int
from functools import wraps

import billiard as multiprocessing
import numpy as np
import numpy.ctypeslib as npct
from datamanager.datasegments import get_datasegment_col_indexes
from django.conf import settings
from library.exceptions import InputParameterException
from pandas import DataFrame, concat


def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


@parametrized
def run_function_with_timer(func, allowed_time):
    @wraps(func)
    def wrapper(input_data, columns, result_names, in_params, function):
        recv_end, send_end = multiprocessing.Pipe(False)
        p = multiprocessing.Process(
            target=func,
            args=(input_data, columns, result_names, in_params, function, send_end),
        )
        p.start()
        p.join(allowed_time)
        if p.is_alive():
            p.terminate()
            p.join()
            raise Exception("Function Exceeded Alloted Exceution Time")
        result = recv_end.recv()

        if isinstance(result, Exception):
            raise result

        result = DataFrame(result)

        return result

    return wrapper


@run_function_with_timer(settings.CUSTOM_TRANSFORM_CPU_TIME)
def run_feature_generator_c_sandboxed(
    input_data, columns, result_names, in_params, function, send_end
):
    try:

        if isinstance(result_names, str):
            result_names = [result_names]

        num_outputs = len(result_names)

        result = DataFrame()
        if len(input_data["data"]) > settings.MAX_SEGMENT_LENGTH:
            raise InputParameterException(
                "Segment size exceeded length {}.".format(settings.MAX_SEGMENT_LENGTH)
            )

        for col in columns:
            feature_names = [col + x for x in result_names]
            col_index = input_data["columns"].index(col)
            data = np.ascontiguousarray(input_data["data"][col_index], dtype=np.int16)

            y = np.zeros(num_outputs, dtype=np.float32)
            params = np.array(in_params, dtype=np.float32)
            function(data, y, params, len(params), 1, data.shape[0], y.shape[0])

            result = concat(
                [
                    result,
                    DataFrame(copy.deepcopy(y).reshape(1, -1), columns=feature_names),
                ],
                axis=1,
            )
    except Exception as e:
        send_end.send(e)
        return

    send_end.send(result.to_dict())


@run_function_with_timer(settings.CUSTOM_TRANSFORM_CPU_TIME)
def run_feature_generator_c_multiple_columns_sandboxed(
    input_data, columns, result_names, in_params, function, send_end
):
    try:
        if isinstance(result_names, str):
            result_names = [result_names]
        if len(columns) > settings.MAX_COLS:
            raise Exception("Too Many Input Columns")
        if len(input_data["data"]) > settings.MAX_SEGMENT_LENGTH:
            raise InputParameterException(
                "Segment size exceeded length {}.".format(settings.MAX_SEGMENT_LENGTH)
            )

        num_outputs = len(result_names)

        result = DataFrame()
        data = np.array([], dtype=np.int16)
        col_indexes = get_datasegment_col_indexes(input_data, columns)
        data = input_data["data"][col_indexes].flatten()

        data = np.ascontiguousarray(data, dtype=np.int16)
        y = np.zeros(num_outputs, dtype=np.float32)
        params = np.array(in_params, dtype=np.float32)
        function(data, y, params, len(params), len(columns), data.shape[0], y.shape[0])

        result = DataFrame(copy.deepcopy(y.reshape(1, -1)), columns=result_names)

    except Exception as e:
        send_end.send(e)
        return

    send_end.send(result.to_dict())


def run_feature_generator_c(input_data, columns, result_names, in_params, function):
    if isinstance(result_names, str):
        result_names = [result_names]

    num_outputs = len(result_names)

    result = DataFrame()
    if len(input_data) > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "Segment size exceeded length {}.".format(settings.MAX_SEGMENT_LENGTH)
        )

    for col in columns:
        feature_names = [col + x for x in result_names]
        col_index = input_data["columns"].index(col)
        data = np.ascontiguousarray(input_data["data"][col_index], dtype=np.int16)

        y = np.zeros(num_outputs, dtype=np.float32)
        params = np.array(in_params, dtype=np.float32)
        function(data, y, params, 1, data.shape[0])

        result = concat(
            [result, DataFrame(copy.deepcopy(y).reshape(1, -1), columns=feature_names)],
            axis=1,
        )

    return result


def run_feature_generator_c_multiple_columns(
    input_data, columns, result_names, in_params, function
):
    if isinstance(result_names, str):
        result_names = [result_names]
    if len(columns) > settings.MAX_COLS:
        raise Exception("Too Many Input Columns")
    if input_data["data"].shape[1] > settings.MAX_SEGMENT_LENGTH:
        raise InputParameterException(
            "Segment size exceeded length {}.".format(settings.MAX_SEGMENT_LENGTH)
        )

    num_outputs = len(result_names)

    data = np.array([], dtype=np.int16)
    col_indexes = get_datasegment_col_indexes(input_data, columns)
    data = input_data["data"][col_indexes].flatten()

    data = np.ascontiguousarray(data, dtype=np.int16)
    y = np.zeros(num_outputs, dtype=np.float32)
    params = np.array(in_params, dtype=np.float32)

    function(data, y, params, len(columns), input_data["data"].shape[1])

    # result = {result_names[index]:y[index] for index in range(y.shape[0])}

    result = DataFrame(y.reshape(1, -1), columns=result_names)

    return result


# input type for the feature generator functions
# must be a double array, with single dimension that is contiguous
array_1d_int = npct.ndpointer(dtype=np.int16, ndim=1, flags="CONTIGUOUS")

array_1d_float = npct.ndpointer(dtype=np.float32, ndim=1, flags="CONTIGUOUS")

# Our windows build agent doesn't build this library file.
# This allows it to still load our library (we can look into other solutions)


class EmptyLibrary:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


if os.path.exists(
    os.path.join(settings.CODEGEN_C_FUNCTION_LOCATION, "pywrapper/libfg_algorithms.so")
):
    libcd = npct.load_library(
        os.path.join(
            settings.CODEGEN_C_FUNCTION_LOCATION, "pywrapper/libfg_algorithms.so"
        ),
        ".",
    )
else:
    libcd = EmptyLibrary()
# Transpose Signal
libcd.fg_transpose_signal_w.restype = None
libcd.fg_transpose_signal_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_transpose_signal_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_transpose_signal_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Interleave Signal
libcd.fg_interleave_signal_w.restype = None
libcd.fg_interleave_signal_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_interleave_signal_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_interleave_signal_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Duration of the Signal
libcd.fg_time_signal_duration_w.restype = None
libcd.fg_time_signal_duration_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_time_signal_duration_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_time_signal_duration_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Percent Time Over Zero
libcd.fg_time_pct_time_over_zero_w.restype = None
libcd.fg_time_pct_time_over_zero_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_time_pct_time_over_zero_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_time_pct_time_over_zero_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Percent Time Over Sigma
libcd.fg_time_pct_time_over_sigma_w.restype = None
libcd.fg_time_pct_time_over_sigma_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_time_pct_time_over_sigma_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_time_pct_time_over_sigma_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Percent Time Over Second Sigma
libcd.fg_time_pct_time_over_second_sigma_w.restype = None
libcd.fg_time_pct_time_over_second_sigma_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_time_pct_time_over_second_sigma_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_time_pct_time_over_second_sigma_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Percent Time Over Threshold
libcd.fg_time_pct_time_over_threshold_w.restype = None
libcd.fg_time_pct_time_over_threshold_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_time_pct_time_over_threshold_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_time_pct_time_over_threshold_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Abs Percent Time Over Threshold
libcd.fg_time_abs_pct_time_over_threshold_w.restype = None
libcd.fg_time_abs_pct_time_over_threshold_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_time_abs_pct_time_over_threshold_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_time_abs_pct_time_over_threshold_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Average Time Over Threshold
libcd.fg_time_avg_time_over_threshold_w.restype = None
libcd.fg_time_avg_time_over_threshold_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_time_avg_time_over_threshold_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_time_avg_time_over_threshold_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Mean
libcd.fg_stats_mean_w.restype = None
libcd.fg_stats_mean_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_mean_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_mean_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Zero Crossings
libcd.fg_stats_zero_crossings_w.restype = None
libcd.fg_stats_zero_crossings_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_zero_crossings_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_zero_crossings_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Positive Zero Crossings
libcd.fg_stats_positive_zero_crossings_w.restype = None
libcd.fg_stats_positive_zero_crossings_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_positive_zero_crossings_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_positive_zero_crossings_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Negative Zero Crossings
libcd.fg_stats_negative_zero_crossings_w.restype = None
libcd.fg_stats_negative_zero_crossings_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_negative_zero_crossings_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_negative_zero_crossings_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Median
libcd.fg_stats_median_w.restype = None
libcd.fg_stats_median_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_median_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_median_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Linear Regression Stats
libcd.fg_stats_linear_regression_w.restype = None
libcd.fg_stats_linear_regression_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_linear_regression_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_linear_regression_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Standard Deviation
libcd.fg_stats_stdev_w.restype = None
libcd.fg_stats_stdev_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_stdev_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_stdev_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Skewness
libcd.fg_stats_skewness_w.restype = None
libcd.fg_stats_skewness_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_skewness_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_skewness_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Kurtosis
libcd.fg_stats_kurtosis_w.restype = None
libcd.fg_stats_kurtosis_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_kurtosis_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_kurtosis_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Interquartile Range
libcd.fg_stats_iqr_w.restype = None
libcd.fg_stats_iqr_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_iqr_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_iqr_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# 25th Percentile
libcd.fg_stats_pct025_w.restype = None
libcd.fg_stats_pct025_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_pct025_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_pct025_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# 75th Percentile
libcd.fg_stats_pct075_w.restype = None
libcd.fg_stats_pct075_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_pct075_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_pct075_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# 100th Percentile
libcd.fg_stats_pct100_w.restype = None
libcd.fg_stats_pct100_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_pct100_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_pct100_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Minimum
libcd.fg_stats_minimum_w.restype = None
libcd.fg_stats_minimum_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_minimum_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_minimum_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Maximum
libcd.fg_stats_maximum_w.restype = None
libcd.fg_stats_maximum_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_maximum_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_maximum_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Sum
libcd.fg_stats_sum_w.restype = None
libcd.fg_stats_sum_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_sum_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_sum_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Absolute Sum
libcd.fg_stats_abs_sum_w.restype = None
libcd.fg_stats_abs_sum_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_abs_sum_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_abs_sum_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Absolute Mean
libcd.fg_stats_abs_mean_w.restype = None
libcd.fg_stats_abs_mean_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_abs_mean_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_abs_mean_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Variance
libcd.fg_stats_variance_w.restype = None
libcd.fg_stats_variance_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_stats_variance_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_stats_variance_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Global Peak to Peak of Low Frequency
libcd.fg_amplitude_global_p2p_low_frequency_w.restype = None
libcd.fg_amplitude_global_p2p_low_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_amplitude_global_p2p_low_frequency_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_amplitude_global_p2p_low_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Global Peak to Peak of High Frequency
libcd.fg_amplitude_global_p2p_high_frequency_w.restype = None
libcd.fg_amplitude_global_p2p_high_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_amplitude_global_p2p_high_frequency_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_amplitude_global_p2p_high_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Max Peak to Peak of first half of High Frequency
libcd.fg_amplitude_max_p2p_half_high_frequency_w.restype = None
libcd.fg_amplitude_max_p2p_half_high_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_amplitude_max_p2p_half_high_frequency_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_amplitude_max_p2p_half_high_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Global Peak to Peak
libcd.fg_amplitude_peak_to_peak_w.restype = None
libcd.fg_amplitude_peak_to_peak_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_amplitude_peak_to_peak_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_amplitude_peak_to_peak_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Global Min Max Sum
libcd.fg_amplitude_min_max_sum_w.restype = None
libcd.fg_amplitude_min_max_sum_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_amplitude_min_max_sum_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_amplitude_min_max_sum_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Ratio of Peak to Peak of High Frequency between two halves
libcd.fg_shape_ratio_high_frequency_w.restype = None
libcd.fg_shape_ratio_high_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_shape_ratio_high_frequency_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_shape_ratio_high_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Difference of Peak to Peak of High Frequency between two halves
libcd.fg_shape_difference_high_frequency_w.restype = None
libcd.fg_shape_difference_high_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_shape_difference_high_frequency_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_shape_difference_high_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Shape Median Difference
libcd.fg_shape_median_difference_w.restype = None
libcd.fg_shape_median_difference_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_shape_median_difference_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_shape_median_difference_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Shape Absolute Median Difference
libcd.fg_shape_absolute_median_difference_w.restype = None
libcd.fg_shape_absolute_median_difference_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_shape_absolute_median_difference_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_shape_absolute_median_difference_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Mean Difference
libcd.fg_roc_mean_difference_w.restype = None
libcd.fg_roc_mean_difference_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_roc_mean_difference_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_roc_mean_difference_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Mean Crossing Rate
libcd.fg_roc_mean_crossing_rate_w.restype = None
libcd.fg_roc_mean_crossing_rate_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_roc_mean_crossing_rate_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_roc_mean_crossing_rate_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Zero Crossing Rate
libcd.fg_roc_zero_crossing_rate_w.restype = None
libcd.fg_roc_zero_crossing_rate_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_roc_zero_crossing_rate_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_roc_zero_crossing_rate_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Sigma Crossing Rate
libcd.fg_roc_sigma_crossing_rate_w.restype = None
libcd.fg_roc_sigma_crossing_rate_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_roc_sigma_crossing_rate_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_roc_sigma_crossing_rate_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Second Sigma Crossing Rate
libcd.fg_roc_second_sigma_crossing_rate_w.restype = None
libcd.fg_roc_second_sigma_crossing_rate_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_roc_second_sigma_crossing_rate_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_roc_second_sigma_crossing_rate_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Threshold Crossing Rate
libcd.fg_roc_threshold_crossing_rate_w.restype = None
libcd.fg_roc_threshold_crossing_rate_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_roc_threshold_crossing_rate_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_roc_threshold_crossing_rate_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Threshold With Offset Crossing Rate
libcd.fg_roc_threshold_with_offset_crossing_rate_w.restype = None
libcd.fg_roc_threshold_with_offset_crossing_rate_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_roc_threshold_with_offset_crossing_rate_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_roc_threshold_with_offset_crossing_rate_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Average of Movement Intensity
libcd.fg_physical_average_movement_intensity_w.restype = None
libcd.fg_physical_average_movement_intensity_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_physical_average_movement_intensity_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_physical_average_movement_intensity_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Variance of Movement Intensity
libcd.fg_physical_variance_movement_intensity_w.restype = None
libcd.fg_physical_variance_movement_intensity_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_physical_variance_movement_intensity_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_physical_variance_movement_intensity_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Average Signal Magnitude Area
libcd.fg_physical_average_signal_magnitude_area_w.restype = None
libcd.fg_physical_average_signal_magnitude_area_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_physical_average_signal_magnitude_area_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_physical_average_signal_magnitude_area_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# MFCC
libcd.fg_frequency_mfcc_w.restype = None
libcd.fg_frequency_mfcc_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_frequency_mfcc_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_frequency_mfcc_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# MFE
libcd.fg_frequency_mfe_w.restype = None
libcd.fg_frequency_mfe_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_frequency_mfe_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_frequency_mfe_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Histogram
libcd.fg_fixed_width_histogram_w.restype = None
libcd.fg_fixed_width_histogram_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_fixed_width_histogram_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_fixed_width_histogram_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Histogram Auto Scale Range
libcd.fg_min_max_scaled_histogram_w.restype = None
libcd.fg_min_max_scaled_histogram_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_min_max_scaled_histogram_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_min_max_scaled_histogram_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Dominant Frequency
libcd.fg_frequency_dominant_frequency_w.restype = None
libcd.fg_frequency_dominant_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_frequency_dominant_frequency_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_frequency_dominant_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Spectral Entropy
libcd.fg_frequency_spectral_entropy_w.restype = None
libcd.fg_frequency_spectral_entropy_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_frequency_spectral_entropy_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_frequency_spectral_entropy_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Power Spectrum
libcd.fg_frequency_power_spectrum_w.restype = None
libcd.fg_frequency_power_spectrum_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_frequency_power_spectrum_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_frequency_power_spectrum_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Average Energy
libcd.fg_energy_average_energy_w.restype = None
libcd.fg_energy_average_energy_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_energy_average_energy_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_energy_average_energy_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Total Energy
libcd.fg_energy_total_energy_w.restype = None
libcd.fg_energy_total_energy_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_energy_total_energy_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_energy_total_energy_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Average Demeaned Energy
libcd.fg_energy_average_demeaned_energy_w.restype = None
libcd.fg_energy_average_demeaned_energy_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_energy_average_demeaned_energy_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_energy_average_demeaned_energy_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Downsample
libcd.fg_sampling_downsample_w.restype = None
libcd.fg_sampling_downsample_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_sampling_downsample_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_sampling_downsample_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Max Column
libcd.fg_cross_column_max_column_w.restype = None
libcd.fg_cross_column_max_column_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_max_column_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_cross_column_max_column_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Min Column
libcd.fg_cross_column_min_column_w.restype = None
libcd.fg_cross_column_min_column_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_min_column_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_cross_column_min_column_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Two Column Min Max Difference
libcd.fg_cross_column_min_max_difference_w.restype = None
libcd.fg_cross_column_min_max_difference_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_min_max_difference_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_cross_column_min_max_difference_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Two Column Mean Difference
libcd.fg_cross_column_mean_difference_w.restype = None
libcd.fg_cross_column_mean_difference_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_mean_difference_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_cross_column_mean_difference_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Two Column Peak To Peak Difference
libcd.fg_cross_column_p2p_difference_w.restype = None
libcd.fg_cross_column_p2p_difference_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_p2p_difference_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_cross_column_p2p_difference_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Abs Max Column
libcd.fg_cross_column_abs_max_column_w.restype = None
libcd.fg_cross_column_abs_max_column_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_abs_max_column_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_cross_column_abs_max_column_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Cross Column Correlation
libcd.fg_cross_column_correlation_w.restype = None
libcd.fg_cross_column_correlation_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_correlation_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_cross_column_correlation_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Cross Column Mean Crossing Rate
libcd.fg_cross_column_mean_crossing_rate_w.restype = None
libcd.fg_cross_column_mean_crossing_rate_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_mean_crossing_rate_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_cross_column_mean_crossing_rate_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Cross Column Mean Crossing with Offset
libcd.fg_cross_column_mean_crossing_rate_with_offset_w.restype = None
libcd.fg_cross_column_mean_crossing_rate_with_offset_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_mean_crossing_rate_with_offset_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_cross_column_mean_crossing_rate_with_offset_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Two Column Median Difference
libcd.fg_cross_column_median_difference_w.restype = None
libcd.fg_cross_column_median_difference_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_median_difference_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_cross_column_median_difference_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Two Column Peak Location Difference
libcd.fg_cross_column_peak_location_difference_w.restype = None
libcd.fg_cross_column_peak_location_difference_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_cross_column_peak_location_difference_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_cross_column_peak_location_difference_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Downsample Average with Normalization
libcd.fg_sampling_downsample_avg_with_normalization_w.restype = None
libcd.fg_sampling_downsample_avg_with_normalization_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_sampling_downsample_avg_with_normalization_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_sampling_downsample_avg_with_normalization_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Downsample Max With Normaliztion
libcd.fg_sampling_downsample_max_with_normalization_w.restype = None
libcd.fg_sampling_downsample_max_with_normalization_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_sampling_downsample_max_with_normalization_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_sampling_downsample_max_with_normalization_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Total Area
libcd.fg_area_total_area_w.restype = None
libcd.fg_area_total_area_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_area_total_area_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_area_total_area_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Absolute Area
libcd.fg_area_absolute_area_w.restype = None
libcd.fg_area_absolute_area_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_area_absolute_area_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_area_absolute_area_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Total Area of Low Frequency
libcd.fg_area_total_area_low_frequency_w.restype = None
libcd.fg_area_total_area_low_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_area_total_area_low_frequency_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_area_total_area_low_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Absolute Area of Low Frequency
libcd.fg_area_absolute_area_low_frequency_w.restype = None
libcd.fg_area_absolute_area_low_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_area_absolute_area_low_frequency_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_area_absolute_area_low_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Total Area of High Frequency
libcd.fg_area_total_area_high_frequency_w.restype = None
libcd.fg_area_total_area_high_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_area_total_area_high_frequency_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_area_total_area_high_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Absolute Area of High Frequency
libcd.fg_area_absolute_area_high_frequency_w.restype = None
libcd.fg_area_absolute_area_high_frequency_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_area_absolute_area_high_frequency_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_area_absolute_area_high_frequency_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Absolute Area of Spectrum
libcd.fg_area_power_spectrum_density_w.restype = None
libcd.fg_area_power_spectrum_density_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_area_power_spectrum_density_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_area_power_spectrum_density_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Peak Frequencies
libcd.fg_frequency_peak_frequencies_w.restype = None
libcd.fg_frequency_peak_frequencies_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_frequency_peak_frequencies_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.fg_frequency_peak_frequencies_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Harmonic Product Spectrum
libcd.fg_frequency_harmonic_product_spectrum_w.restype = None
libcd.fg_frequency_harmonic_product_spectrum_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_frequency_harmonic_product_spectrum_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_frequency_harmonic_product_spectrum_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )


# Peak Harmonic Product Spectrum
libcd.fg_frequency_peak_harmonic_product_spectrum_w.restype = None
libcd.fg_frequency_peak_harmonic_product_spectrum_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def fg_frequency_peak_harmonic_product_spectrum_w(
    in_array, out_array, params, num_cols, num_rows
):
    return libcd.fg_frequency_peak_harmonic_product_spectrum_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )
