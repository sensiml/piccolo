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

import numpy as np
from library.core_functions import MAX_INT_16, MIN_INT_16
from pandas import DataFrame


def sg_filter_mse(
    input_data: DataFrame,
    input_column: str,
    group_columns: List[str],
    MSE_target: float = 0.0,
    MSE_threshold: float = 10,
) -> DataFrame:
    """
    Filters out groups that do not pass the MSE threshold.

    Args:
        input_column (str): The name of the column to use for filtering.
        MSE_target (float): The filter target value. Default is -1.0.
        MSE_threshold (float): The filter threshold value. Default is 0.01.

    Returns:
        DataFrame: The filtered input data.
    """

    new_segments = []

    def mse(input_data, target):
        value = 1.0 / len(input_data) * sum((input_data - target).astype(int) ** 2)
        return value

    for _, segment in enumerate(input_data):
        column_index = segment["columns"].index(input_column)
        if mse(segment["data"][column_index], MSE_target) > MSE_threshold:
            new_segments.append(segment)

    if len(new_segments) == 0:
        raise Exception(
            f"No groups above the MSE_threshold {MSE_threshold}. Try lowering the threshold"
        )

    return new_segments


sg_filter_mse_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_column", "type": "str"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "MSE_target",
            "type": "int",
            "default": 0,
            "c_param": 0,
            "range": [MIN_INT_16, MAX_INT_16],
        },
        {
            "name": "MSE_threshold",
            "type": "int",
            "default": 10,
            "c_param": 1,
            "range": [MIN_INT_16, MAX_INT_16],
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def sg_filter_threshold(
    input_data: DataFrame,
    input_column: str,
    group_columns: List[str],
    threshold: int = 0,
    comparison: int = 0,
) -> DataFrame:
    """
    Filters out segments that have values greater or less than the specified threshold.

    Args:
        input_column (str): The name of the column to use for filtering.
        threshold (int16): The threshold value to filter against.
        comparison (int): 0 for less than, 1 for greater than.

    Returns:
        DataFrame: Segments that pass the energy threshold.
    """
    if comparison not in [0, 1]:
        raise Exception("Invalid Value for Comparison. Must be 0 or 1.")

    new_segments = []

    column_index = input_data[0]["columns"].index(input_column)
    for segment in input_data:

        if comparison == 0 and segment["data"][column_index].max() < threshold:
            new_segments.append(segment)

        elif comparison == 1 and segment["data"][column_index].min() > threshold:
            new_segments.append(segment)

    return new_segments


sg_filter_threshold_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_column", "type": "str"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "threshold",
            "type": "int",
            "default": 0,
            "range": [MIN_INT_16, MAX_INT_16],
            "c_param": 0,
            "description": "Value which if passed will cause the segment to be filtered.",
        },
        {
            "name": "comparison",
            "type": "int",
            "default": 0,
            "options": [0, 1],
            "c_param": 1,
            "description": "0 for less than, 1 for greater than. If a value is greater/less than the segment will be filtered.",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def sg_filter_energy_threshold(
    input_data: list,
    input_column: str,
    group_columns: List[str],
    threshold: int = 0,
    backoff: int = 0,
    delay: int = 0,
    disable_train: bool = False,
) -> DataFrame:
    """
    Takes the absolute value of each point and compares it with the threshold. If no values are above the threshold, the segment is filtered.

    Args:
        input_data (_type_): _description_
        input_column (_type_): _description_
        group_columns (_type_): _description_
        threshold (int, optional): _description_. Defaults to 0.
        backoff (int, optional): _description_. Defaults to 0.
        delay (int, optional): _description_. Defaults to 0.
        disable_train (bool, optional): _description_. Defaults to False.

    Returns:
        DataFrame: The segments that were not filtered.
    """

    if disable_train:
        return input_data

    new_segments = []
    column_index = input_data[0]["columns"].index(input_column)
    for segment in input_data:
        if np.abs(segment["data"][column_index]).max() > threshold:
            new_segments.append(segment)

    return new_segments


sg_filter_energy_threshold_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_column", "type": "str"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "threshold",
            "type": "int",
            "default": 0,
            "range": [0, MAX_INT_16],
            "c_param": 0,
            "description": "The threshold that must be crossed for the segment to not be filtered.",
        },
        {
            "name": "backoff",
            "type": "int",
            "default": 0,
            "range": [0, 64],
            "c_param": 1,
            "description": "The backoff is used on the device to determine how many segments after a non filtered segment to continue passing if they are below the threshold.",
        },
        {
            "name": "delay",
            "type": "int",
            "default": 0,
            "range": [0, 64],
            "c_param": 2,
            "description": "The delay after the event is triggered before starting classification.",
        },
        {
            "name": "disable_train",
            "type": "boolean",
            "default": False,
            "description": "Disables the segment filter during training. This is typically used in conjunction with the backoff parameter.",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def sg_filter_peak_ratio_energy_threshold(
    input_data: list,
    input_column: str,
    group_columns: List[str],
    lower_threshold: int = 0,
    upper_threshold: int = 0,
    peak_to_average_limit: float = 0,
    backoff: int = 0,
    delay: int = 0,
    disable_train: bool = False,
) -> DataFrame:
    """
    Takes the absolute value of each point and compares it with the threshold. If no values are above the threshold, the segment is filtered.

    Args:
        input_data (_type_): _description_
        input_column (_type_): _description_
        group_columns (_type_): _description_
        lower_threshold (int, optional): Continuous Activation Threshold. The threshold that must be crossed for the segment to not be filtered. Defaults to 0.
        upper_threshold (int, optional): Lowest Activation Threshold. The threshold that must be exceeded to consider the peak-to-average condition. Defaults to 0.
        peak_to_average_limit (float, optional): The minimum acceptable limit of the segment peak-to-average power ratio (PAR). Defaults to 0.
        backoff (int, optional): The backoff is used on the device to determine how many segments after a non filtered segment to continue passing if they are below the threshold. Defaults to 0.
        delay (int, optional): The delay after the event is triggered before starting classification. Defaults to 0.
        disable_train (bool, optional): Disables the segment filter during training. This is typically used in conjunction with the backoff parameter. Defaults to False.

    Returns:
        DataFrame: The segments that were not filtered.

    """

    if disable_train:
        return input_data

    new_segments = []
    column_index = input_data[0]["columns"].index(input_column)
    for segment in input_data:
        peak = np.abs(segment["data"][column_index]).max()
        mean = np.abs(segment["data"][column_index]).mean()
        if (
            peak / (mean + 1.0e-5) > peak_to_average_limit and peak > lower_threshold
        ) or (peak > upper_threshold):
            new_segments.append(segment)

    return new_segments


sg_filter_peak_ratio_energy_threshold_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_column", "type": "str"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "upper_threshold",
            "type": "int",
            "default": 0,
            "range": [0, MAX_INT_16],
            "c_param": 0,
            "description": "Continuous Activation Threshold. The threshold that must be crossed for the segment to not be filtered.",
        },
        {
            "name": "lower_threshold",
            "type": "int",
            "default": 0,
            "range": [0, MAX_INT_16],
            "c_param": 1,
            "description": "Lowest Activation Threshold. The threshold that must be exceeded to consider the peak-to-average condition.",
        },
        {
            "name": "peak_to_average_limit",
            "type": "float",
            "default": 0,
            "range": [0, 10],
            "c_param": 2,
            "description": "The minimum acceptable limit of the segment peak-to-average power ratio (PAR).",
        },
        {
            "name": "backoff",
            "type": "int",
            "default": 0,
            "range": [0, 64],
            "c_param": 3,
            "description": "The backoff is used on the device to determine how many segments after a non filtered segment to continue passing if they are below the threshold.",
        },
        {
            "name": "delay",
            "type": "int",
            "default": 0,
            "range": [0, 64],
            "c_param": 4,
            "description": "The delay after the event is triggered before starting classification.",
        },
        {
            "name": "disable_train",
            "type": "boolean",
            "default": False,
            "description": "Disables the segment filter during training. This is typically used in conjunction with the backoff parameter.",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def sg_filter_vad_silk(
    input_data: list,
    input_column: str,
    group_columns: list,
    threshold: int = 10,
    buffer_size: int = 12,
    disable_train: bool = False,
):
    """TODO: ADD DESCRIPTION

    Args:
        input_data (_type_): _description_
        input_column (_type_): _description_
        group_columns (_type_): _description_
        threshold (int): The number of VAD checks int he buffer that must be positive to pass the segment through the filter. This value must be less that the buffer_size. Defaults to 10.
        buffer_size (int): The number of consecutive VAD checks to store for comparison against the threshold.
        disable_train (bool, optional): _description_. Defaults to False.

    Returns:

    """

    # TODO Implement code to call from python
    # TODO Add validation for buffer_size >= threshold +2

    return input_data


sg_filter_vad_silk_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_column", "type": "str"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "threshold",
            "type": "int",
            "default": 10,
            "range": [1, 29],
            "c_param": 0,
            "description": "The number of VAD checks int he buffer that must be positive to pass the segment through the filter. This value must be less that the buffer_size",
        },
        {
            "name": "buffer_size",
            "type": "int",
            "default": 12,
            "range": [2, 30],
            "c_param": 1,
            "description": "The number of consecutive VAD checks to store for comparison against the threshold.",
        },
        {
            "name": "disable_train",
            "type": "boolean",
            "default": True,
            "description": "Disables the segment filter during training.",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def sg_filter_vad_webrtc(
    input_data: list,
    input_column: str,
    group_columns: list,
    threshold: int = 10,
    buffer_size: int = 12,
    disable_train: bool = True,
):
    """TODO: ADD DESCRIPTION

    Args:
        input_data (_type_): _description_
        input_column (_type_): _description_
        group_columns (_type_): _description_
        threshold (int): The number of VAD checks int he buffer that must be positive to pass the segment through the filter. This value must be less that the buffer_size. Defaults to 10.
        buffer_size (int): The number of consecutive VAD checks to store for comparison against the threshold.
        disable_train (bool, optional): _description_. Defaults to False.

    Returns:

    """

    # TODO Implement code to call from python

    return input_data


sg_filter_vad_webrtc_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_column", "type": "str"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "threshold",
            "type": "int",
            "default": 10,
            "range": [1, 29],
            "c_param": 0,
            "description": "The number of VAD checks int he buffer that must be positive to pass the segment through the filter. This value must be less that the buffer_size",
        },
        {
            "name": "buffer_size",
            "type": "int",
            "default": 12,
            "range": [2, 30],
            "c_param": 1,
            "description": "The number of consecutive VAD checks to store for comparison against the threshold.",
        },
        {
            "name": "disable_train",
            "type": "boolean",
            "default": True,
            "description": "Disables the segment filter during training.",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}
