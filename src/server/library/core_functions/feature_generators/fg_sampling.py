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
from library.exceptions import InputParameterException
from pandas import DataFrame


def fg_sampling_downsample(
    input_data: DataFrame,
    columns: List[str],
    new_length: int = 12,
    **kwargs,
) -> DataFrame:
    """
    This function takes a dataframe `input_data` as input and performs group by operation on specified `group_columns`.
    For each group, it drops the `passthrough_columns` and performs downsampling on the remaining columns by following steps:

    - Divide the entire column into windows of size total length/`new_length`.
    - Calculate mean for each window.
    - Concatenate all the mean values.
    - The length of the downsampled signal is equal to `new length`.

    Then all such means are concatenated to get `new_length` * # of columns. These constitute features in downstream analyses.
    For instance, if there are three columns and the `new_length` value is 12, then total number of means we get is 12 * 3 = 36.
    Each will represent a feature.

    Args:
        input_data (DataFrame): Input pandas dataframe.
        columns (List[str]): List of column names to perform downsampling.
        new_length (int): Downsampled length. Defaults to 12.

    Returns:
        DataFrame: DataFrame containing Downsampled Feature Vector.

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
        >>> client.pipeline.add_feature_generator([{'name':'Downsample',
                                     'params':{"columns": ['accelx'],
                                               "new_length": 5}}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            out:
                  Class  Rep Subject  gen_0001_accelx_0  gen_0001_accelx_1  gen_0001_accelx_2  gen_0001_accelx_3  gen_0001_accelx_4
            0  Crawling    1     s01              367.0              336.5              391.0              471.0              523.0
            1   Running    1     s01              -45.5              -41.5              -50.0              -64.0              -64.0

    """

    if new_length > input_data["data"].shape[1]:
        raise InputParameterException(
            "new_length ({0}) must not be larger than the amount of input data ({1})".format(
                new_length, input_data["data"].shape[1]
            )
        )

    strLength = str(new_length)

    params = [new_length]
    result_names = [
        "Downsample_{0}".format(str(x).zfill(len(strLength))) for x in range(new_length)
    ]

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        result_names,
        params,
        fg_algorithms.fg_sampling_downsample_w,
    )


fg_sampling_downsample_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 1,
        },
        {
            "name": "new_length",
            "type": "int",
            "default": 12,
            "c_param": 0,
            "range": [5, 32],
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
            "name": "data_out",
            "type": "DataFrame",
            "family": True,
            "output_formula": "params['new_length']*len(params['columns'])",
        }
    ],
}


def fg_sampling_downsample_avg_with_normalization(
    input_data: DataFrame, columns: List[str], new_length: int = 12, **kwargs
):
    """
    This function takes `input_data` dataframe as input and group by `group_columns`.
    Then for each group, it drops the `passthrough_columns` and performs a convolution
    on the remaining columns.

    On each column, perform the following steps:

    - Divide the entire column into windows of size total length/`new_length`.
    - Calculate mean for each window
    - Concatenate all the mean values into a feature vector of length new_length
    - Normalize the signal to be between 0-255

    Then all such means are concatenated to get `new_length` * # of columns. These constitute
    features in downstream analyses. For instance, if there are three columns and the
    `new_length` value is 12, then total number of means we get is 12 * 3 = 36. Each will represent a feature.

    Args:
        input_data (DataFrame): Input data to transform
        columns: List of columns
        group_columns (a list): List of columns on which grouping is to be done.
                                 Each group will go through downsampling one at a time
        new_length (int): Dopwnsample Length length

    Returns:
        DataFrame: Downsampled Features Normalized

    Examples:
        >>> from pandas import DataFrame
        >>> df = DataFrame([[3, 3], [4, 5], [5, 7], [4, 6],
                            [3, 1], [3, 1], [4, 3], [5, 5],
                            [4, 7], [3, 6]], columns=['accelx', 'accely'])
        >>> df
        Out:
           accelx  accely
        0       3       3
        1       4       5
        2       5       7
        3       4       6
        4       3       1
        5       3       1
        6       4       3
        7       5       5
        8       4       7
        9       3       6
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Downsample Average with Normalization"],
                 params = {"group_columns": []},
                           function_defaults={"columns":['accelx', 'accely'],
                                             'new_length' : 5})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            Out:
                   accelx_1  accelx_2  accelx_3  accelx_4  accelx_5  accely_1  accely_2
                0       3.5       4.5         3       4.5       3.5         4       6.5
                   accely_3  accely_4  accely_5
                0         1         4       6.5
    """

    if new_length > input_data["data"].shape[1]:
        raise InputParameterException(
            "new_length ({0}) must not be larger than the amount of input data ({1})".format(
                new_length, input_data["data"].shape[1]
            )
        )

    strLength = str(new_length)

    params = [new_length]
    result_names = [
        "SamplingAvg{0}".format(str(x).zfill(len(strLength))) for x in range(new_length)
    ]

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        result_names,
        params,
        fg_algorithms.fg_sampling_downsample_avg_with_normalization_w,
    )


fg_sampling_downsample_avg_with_normalization_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 1,
        },
        {
            "name": "new_length",
            "type": "int",
            "default": 12,
            "c_param": 0,
            "range": [5, 32],
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
            "name": "data_out",
            "type": "DataFrame",
            "family": True,
            "output_formula": "params['new_length']",
            "scratch_buffer": {"type": "parameter", "name": "new_length"},
        }
    ],
}


def fg_sampling_downsample_max_with_normalization(
    input_data: DataFrame, columns: List[str], new_length: int = 12, **kwargs
):
    """
    This function takes `input_data` dataframe as input and group by `group_columns`.
    Then for each group, it drops the `passthrough_columns` and performs a max downsampling
    on the remaining columns.

    On each column, perform the following steps:

    - Divide the entire column into windows of size total length/`new_length`.
    - Calculate max value for each window
    - Concatenate all the max values into a feature vector of length new_length
    - Nomralize the signal to be between 0-255

    Then all such means are concatenated to get `new_length` * # of columns. These constitute
    features in downstream analyses. For instance, if there are three columns and the
    `new_length` value is 12, then total number of means we get is 12 * 3 = 36. Each will represent a feature.

    Args:
        input_data (DataFrame): Input data to transform
        columns: List of columns
        group_columns (a list): List of columns on which grouping is to be done.
                                 Each group will go through downsampling one at a time
        new_length (int): Dopwnsample Length length

    Returns:
        DataFrame: Downsampled Features Normalized to the Max Value

    Examples:
        >>> from pandas import DataFrame
        >>> df = DataFrame([[3, 3], [4, 5], [5, 7], [4, 6],
                            [3, 1], [3, 1], [4, 3], [5, 5],
                            [4, 7], [3, 6]], columns=['accelx', 'accely'])
        >>> df
        Out:
           accelx  accely
        0       3       3
        1       4       5
        2       5       7
        3       4       6
        4       3       1
        5       3       1
        6       4       3
        7       5       5
        8       4       7
        9       3       6
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Downsample Max with Normalization"],
                 params = {"group_columns": []},
                           function_defaults={"columns":['accelx', 'accely'],
                                             'new_length' : 5})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            Out:
                   accelx_1  accelx_2  accelx_3  accelx_4  accelx_5  accely_1  accely_2
                0       3.5       4.5         3       4.5       3.5         4       6.5
                   accely_3  accely_4  accely_5
                0         1         4       6.5
    """

    if new_length > input_data["data"].shape[1]:
        raise InputParameterException(
            "new_length ({0}) must not be larger than the amount of input data ({1})".format(
                new_length, input_data["data"].shape[1]
            )
        )

    params = [new_length]

    strLength = str(new_length)

    result_names = [
        "SamplingMax{0}".format(str(x).zfill(len(strLength))) for x in range(new_length)
    ]

    return fg_algorithms.run_feature_generator_c(
        input_data,
        columns,
        result_names,
        params,
        fg_algorithms.fg_sampling_downsample_max_with_normalization_w,
    )


fg_sampling_downsample_max_with_normalization_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
            "num_columns": 1,
        },
        {
            "name": "new_length",
            "type": "int",
            "default": 12,
            "c_param": 0,
            "range": [5, 32],
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
            "name": "data_out",
            "type": "DataFrame",
            "family": True,
            "output_formula": "params['new_length']",
            "scratch_buffer": {"type": "parameter", "name": "new_length"},
        }
    ],
}
