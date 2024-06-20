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
import time
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
