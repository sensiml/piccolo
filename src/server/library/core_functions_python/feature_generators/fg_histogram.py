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

import numpy as np
import pandas as pd


def fg_fixed_width_cumulative_distribution_function(
    input_data,
    columns,
    range_left,
    range_right,
    normalize_factor=None,
    number_of_bins=128,
    scaling_factor=255,
    group_columns=None,
):
    """Translates to the data stream(s) from a segment into a feature vector containing the cumulative
         distribution function probabilities.

    Args:
        input_data (DataFrame): input data
        column (list of strings): name of the sensor streams to use
        range_left (int): the left limit (or the min) of the range for a fixed bin histogram
        range_right (int): the right limit (or the max) of the range for a fixed bin histogram
        normalize_factor (None, optional): the number of samples used to calculate the histogram
        number_of_bins (int, optional): the number of bins used for the histogram
        scaling_factor (int, optional): scaling factor used to fit for the device


    Returns:
        DataFrame: feature vector in cdf space.
    """

    input_data = input_data[columns[0]].values

    if normalize_factor is None:
        normalize_factor = len(input_data)

    bins = []

    # calculate bin width
    width = float((range_right - range_left)) / number_of_bins

    # create starting point for each bin
    for ii in range(number_of_bins + 1):
        bins.append(ii * width + range_left)

    # expand two ends
    bins[0] = range_left

    bins[-1] = range_right

    start_point = bins[0]
    cdf_list = []

    total = 0
    for x in bins[1:]:
        temp = _cal_bin_counts(input_data, start_point, x)
        total += temp[2]
        start_point = x
        cdf_list.append(total)

    # added 0.5 for integer operation of roundup
    # normalize_factor = max(hist_cal) #staford implementation
    cdf_scaled = [
        int(x * scaling_factor / float(normalize_factor) + 0.5) for x in cdf_list
    ]

    cdf_dict = {}
    for index, i in enumerate(cdf_scaled):
        cdf_dict["cdf_bin_{0:06}".format(index)] = i

    return pd.DataFrame([cdf_dict])


fg_fixed_width_cumulative_distribution_function_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {"name": "range_left", "type": "int", "default": -1024},
        {"name": "range_right", "type": "int", "default": 1024},
        {"name": "normalize_factor", "type": "int", "default": None},
        {"name": "number_of_bins", "type": "int", "default": 32},
        {"name": "scaling_factor", "type": "int", "default": 255},
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
        }
    ],
}


def fg_pre_specified_bins_histogram(
    input_data,
    columns,
    pre_specified_bins,
    normalize_factor=None,
    scaling_factor=255,
    group_columns=[],
):
    """Translates to the data stream(s) from a segment into a feature vector in histogram
    space based on pre_specified bins.

    Args:
        input_data (DataFrame): input data
        column (list of strings): name of the sensor streams to use
        pre_specified_bins (list of list of two floats: begin and end, in a increasing order):
            pre-specified bins: begin and end pair
        normalize_factor (None, optional): the number of samples used to calculate the histogram
        scaling_factor (int, optional): scaling factor used to fit for the device


    Returns:
        DataFrame: feature vector in histogram space.
    """
    myinput = []
    for column in columns:
        myinput.append(input_data.loc[:, column])
    input_data = pd.concat(myinput).reset_index(drop=True)

    input_data = input_data.values

    if normalize_factor is None:
        normalize_factor = len(input_data)

    bins = pre_specified_bins

    hist_cal = []

    for x in bins:
        temp = _cal_bin_counts(input_data, x[0], x[1])
        hist_cal.append(temp[2])

    # added 0.5 for integer operation of roundup
    hist_scaled = [
        int(x * scaling_factor / float(normalize_factor) + 0.5) for x in hist_cal
    ]

    hist_dict = []
    for index, i in enumerate(hist_scaled):
        hist_dict.append(("hist_bin_{0:06}".format(index), i))
    df = pd.DataFrame(hist_dict, columns=["idx", "count"])
    df = df.set_index("idx", drop=True)
    df.index.name = None

    return df.T


fg_pre_specified_bins_histogram_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "pre_specified_bins", "type": "list", "element_type": "list"},
        {"name": "normalize_factor", "type": "int", "default": None},
        {"name": "scaling_factor", "type": "int", "default": 255},
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


def _cal_bin_counts(array_in, starting_point, end_point):
    """
    Calculates a numpy array's counts in each bin based on the start and end points, with closed
    in the starting point and open on the end point.
    Args:
        array_in: input one dimensional array.
        starting_point: starting point
        end_point: end point

    Returns:
        tuple of triple: start, end point and the count

    """

    # data2 is the index where the logic is true
    data2 = np.where(np.logical_and(array_in >= starting_point, array_in < end_point))
    t_triple = (starting_point, end_point, len(data2[0]))

    return t_triple
