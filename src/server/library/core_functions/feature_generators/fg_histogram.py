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

from typing import List, Optional

import library.core_functions.fg_algorithms as fg_algorithms
from library.core_functions import MAX_INT_16, MIN_INT_16
from library.exceptions import InputParameterException
from pandas import DataFrame


# input_data (DataFrame): input data
#
def fg_fixed_width_histogram(
    input_data: DataFrame,
    columns: List[str],
    range_left: int,
    range_right: int,
    number_of_bins: int = 128,
    scaling_factor: int = 255,
    group_columns: Optional[List[str]] = None,
    **kwargs
):
    """
    Translates to the data stream(s) from a segment into a feature vector in histogram space.

    Args:
        column (list of strings): name of the sensor streams to use
        range_left (int): the left limit (or the min) of the range for a fixed bin histogram
        range_right (int): the right limit (or the max) of the range for a fixed bin histogram
        number_of_bins (int, optional): the number of bins used for the histogram
        scaling_factor (int, optional): scaling factor used to fit for the device

    Returns:
        DataFrame: feature vector in histogram space.

    Examples:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> print df
            out:
               Subject     Class  Rep  accelx  accely  accelz
            0      s01  Crawling    1     377     569    4019
            1      s01  Crawling    1     357     594    4051
            2      s01  Crawling    1     333     638    4049
            3      s01  Crawling    1     340     678    4053
            4      s01  Crawling    1     372     708    4051
            5      s01  Crawling    1     410     733    4028
            6      s01  Crawling    1     450     733    3988
            7      s01  Crawling    1     492     696    3947
            8      s01  Crawling    1     518     677    3943
            9      s01  Crawling    1     528     695    3988
            10     s01  Crawling    1      -1    2558    4609
            11     s01   Running    1     -44   -3971     843
            12     s01   Running    1     -47   -3982     836
            13     s01   Running    1     -43   -3973     832
            14     s01   Running    1     -40   -3973     834
            15     s01   Running    1     -48   -3978     844
            16     s01   Running    1     -52   -3993     842
            17     s01   Running    1     -64   -3984     821
            18     s01   Running    1     -64   -3966     813
            19     s01   Running    1     -66   -3971     826
            20     s01   Running    1     -62   -3988     827
            21     s01   Running    1     -57   -3984     843

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns=['accelx', 'accely', 'accelz'],
                            group_columns=['Subject', 'Class', 'Rep'],
                            label_column='Class')
        >>> client.pipeline.add_feature_generator([{'name':'Histogram',
                                     'params':{"columns": ['accelx','accely','accelz'],
                                               "range_left": 10,
                                               "range_right": 1000,
                                               "number_of_bins": 5,
                                               "scaling_factor": 254 }}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            out:
                  Class  Rep Subject  gen_0000_hist_bin_000000  gen_0000_hist_bin_000001  gen_0000_hist_bin_000002  gen_0000_hist_bin_000003  gen_0000_hist_bin_000004
            0  Crawling    1     s01                       8.0                      38.0                      46.0                      69.0                       0.0
            1   Running    1     s01                      85.0                       0.0                       0.0                       0.0                      85.0

    """
    if number_of_bins > 128 or number_of_bins < 1:
        raise InputParameterException(
            "Number of bins must be positive and less than 128"
        )

    params = [number_of_bins, range_left, range_right, scaling_factor]
    result_names = ["hist_bin_{0:06}".format(index) for index in range(number_of_bins)]

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data,
        columns,
        result_names,
        params,
        fg_algorithms.fg_fixed_width_histogram_w,
    )


fg_fixed_width_histogram_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {
            "name": "range_left",
            "type": "int",
            "default": -32000,
            "c_param": 0,
            "range": [MIN_INT_16, MAX_INT_16],
        },
        {
            "name": "range_right",
            "type": "int",
            "default": 32000,
            "c_param": 1,
            "range": [MIN_INT_16, MAX_INT_16],
        },
        {
            "name": "number_of_bins",
            "type": "int",
            "default": 32,
            "c_param": 2,
            "range": [1, 255],
        },
        {
            "name": "scaling_factor",
            "type": "int",
            "default": 255,
            "c_param": 3,
            "range": [1, 255],
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
            "scratch_buffer": {"type": "parameter", "name": "number_of_bins"},
        }
    ],
}


# input_data (DataFrame): input data
#
def fg_min_max_scaled_histogram(
    input_data: DataFrame,
    columns: List[str],
    number_of_bins: int = 5,
    scaling_factor: int = 255,
    group_columns: Optional[List[str]] = None,
    **kwargs
):
    """
    Translates to the data stream(s) from a segment into a feature vector in histogram space where the range
    is set by the min and max values and the number of bins by the user.

    Args:
        column (list of strings): name of the sensor streams to use
        number_of_bins (int, optional): the number of bins used for the histogram
        scaling_factor (int, optional): scaling factor used to fit for the device

    Returns:
        DataFrame: feature vector in histogram space.

    Examples:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> print df
            out:
               Subject     Class  Rep  accelx  accely  accelz
            0      s01  Crawling    1     377     569    4019
            1      s01  Crawling    1     357     594    4051
            2      s01  Crawling    1     333     638    4049
            3      s01  Crawling    1     340     678    4053
            4      s01  Crawling    1     372     708    4051
            5      s01  Crawling    1     410     733    4028
            6      s01  Crawling    1     450     733    3988
            7      s01  Crawling    1     492     696    3947
            8      s01  Crawling    1     518     677    3943
            9      s01  Crawling    1     528     695    3988
            10     s01  Crawling    1      -1    2558    4609
            11     s01   Running    1     -44   -3971     843
            12     s01   Running    1     -47   -3982     836
            13     s01   Running    1     -43   -3973     832
            14     s01   Running    1     -40   -3973     834
            15     s01   Running    1     -48   -3978     844
            16     s01   Running    1     -52   -3993     842
            17     s01   Running    1     -64   -3984     821
            18     s01   Running    1     -64   -3966     813
            19     s01   Running    1     -66   -3971     826
            20     s01   Running    1     -62   -3988     827
            21     s01   Running    1     -57   -3984     843

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns=['accelx', 'accely', 'accelz'],
                            group_columns=['Subject', 'Class', 'Rep'],
                            label_column='Class')
        >>> client.pipeline.add_feature_generator([{'name':'Histogram',
                                     'params':{"columns": ['accelx','accely','accelz'],
                                               "range_left": 10,
                                               "range_right": 1000,
                                               "number_of_bins": 5,
                                               "scaling_factor": 254 }}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            out:
                  Class  Rep Subject  gen_0000_hist_bin_000000  gen_0000_hist_bin_000001  gen_0000_hist_bin_000002  gen_0000_hist_bin_000003  gen_0000_hist_bin_000004
            0  Crawling    1     s01                       8.0                      38.0                      46.0                      69.0                       0.0
            1   Running    1     s01                      85.0                       0.0                       0.0                       0.0                      85.0

    """
    if number_of_bins > 128 or number_of_bins < 1:
        raise InputParameterException(
            "Number of bins must be positive and less than 128"
        )

    params = [number_of_bins, scaling_factor]
    result_names = [
        "mm_hist_bin_{0:06}".format(index) for index in range(number_of_bins)
    ]

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data,
        columns,
        result_names,
        params,
        fg_algorithms.fg_min_max_scaled_histogram_w,
    )


fg_min_max_scaled_histogram_contracts = {
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
            "name": "number_of_bins",
            "type": "int",
            "default": 32,
            "c_param": 0,
            "range": [1, 255],
        },
        {
            "name": "scaling_factor",
            "type": "int",
            "default": 255,
            "c_param": 1,
            "range": [1, 255],
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
            "scratch_buffer": {"type": "parameter", "name": "number_of_bins"},
        }
    ],
}
