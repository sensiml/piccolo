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

import numpy as np
from pandas import DataFrame, concat


def min_max_scale(
    input_data: DataFrame,
    passthrough_columns: List[str],
    min_bound: int = 0,
    max_bound: int = 255,
    feature_min_max_parameters: Optional[dict] = None,
    pad: Optional[float] = None,
    feature_min_max_defaults: Optional[dict] = None,
):
    """
    Normalize and scale data to integer values between min_bound and max_bound,
    while leaving specified passthrough columns unscaled. This operates on each
    feature column separately and  saves min/max data transforming the features
    prior to classification

    Args:
        min_bound: min value in the output (0~255)
        max_bound: max value in the output (0~255)
        feature_min_max_parameters: Dictionary of 'maximums' and 'minimums'.
            If a non-empty dictionary is passed as parameter, the minimum and maximum value will
            be calculated based on the 'maximums' and 'minimums' in the dictionary. If the value
            of this parameter is {}, then a new min-max value for each feature is
            calculated.
        pad: pad the min and max value by +-col.std()/pad. Can be used to make min max more robust to
             unseen data.
        feature_min_max_defaults: allows you to set the min max value for all values at once. example {'minimum':-1000, maximum:1000}

    Returns:
        The scaled dataframe and minimums and maximums for each feature.
        If 'feature_min_max_parameters' values is {} then the minimums
        and maximums for each feature are calculated based on the data passed.

    Examples:
        >>> from pandas import DataFrame
        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                            [-2, 8, 7], [2, 9, 6]],
                            columns=['feature1', 'feature2', 'feature3'])
        >>> df['Subject'] = 's01'
        >>> df
            Out:
               feature1  feature2  feature3 Subject
            0        -3         6         5     s01
            1         3         7         8     s01
            2         0         6         3     s01
            3        -2         8         7     s01
            4         2         9         6     s01
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force = True)
        >>> client.pipeline.add_transform('Min Max Scale',
                params={'passthrough_columns':['Subject'],
                        'min_bound' : 0, 'max_bound' : 255})
            Out:
                  Subject  feature1  feature2  feature3
                0     s01         0         0       101
                1     s01       254        84       254
                2     s01       127         0         0
                3     s01        42       169       203
                4     s01       212       254       152

        Passing min-max parameter as arguments

        >>> my_min_max_param = {'maximums': {'feature1': 30,
                                            'feature2': 100,
                                            'feature3': 500},
                                'minimums': {'feature1': 0,
                                            'feature2': 0,
                                            'feature3': -100}}
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force = True)
        >>> client.pipeline.add_transform('Min Max Scale',
                            params={'passthrough_columns':['Subject'],
                                    'min_bound' : 0,
                                    'max_bound' : 255,
                                    'feature_min_max_parameters': my_min_max_param})
        >>> results, stats = client.pipeline.execute()
        >>> print results, stats
            Out:
                    feature1  feature2  feature3 Subject
                 0         0        15        44     s01
                 1        25        17        45     s01
                 2         0        15        43     s01
                 3         0        20        45     s01
                 4        16        22        45     s01
    """

    cols_to_scale = sorted(
        [col for col in input_data.columns if col not in passthrough_columns]
    )
    df_out = DataFrame()
    new_scale = input_data[cols_to_scale].values.astype(np.float32).T

    if not feature_min_max_parameters:
        feature_min_max_parameters = {"maximums": {}, "minimums": {}}

    # If the sample mins and maxes are not provided, calculate them from the input data
    for index, col in enumerate(cols_to_scale):
        if col not in feature_min_max_parameters["maximums"].keys():
            if feature_min_max_defaults:
                feature_min_max_parameters["minimums"][col] = float(
                    feature_min_max_defaults["minimum"]
                )
                feature_min_max_parameters["maximums"][col] = float(
                    feature_min_max_defaults["maximum"]
                )
            elif pad:
                feature_min_max_parameters["minimums"][col] = float(
                    (new_scale[index].min() - new_scale[index].std() / pad)
                )
                feature_min_max_parameters["maximums"][col] = float(
                    (new_scale[index].max() + new_scale[index].std() / pad)
                )
            else:
                feature_min_max_parameters["minimums"][col] = float(
                    new_scale[index].min()
                )
                feature_min_max_parameters["maximums"][col] = float(
                    new_scale[index].max()
                )

    for index, col in enumerate(cols_to_scale):
        new_scale[index, :] = np.floor(
            255
            * (
                (new_scale[index] - feature_min_max_parameters["minimums"][col])
                / (
                    feature_min_max_parameters["maximums"][col]
                    - feature_min_max_parameters["minimums"][col]
                    + 1e-10
                )
            )
        ).astype(int)

        new_scale[index][np.where(new_scale[index] >= max_bound)] = max_bound
        new_scale[index][np.where(new_scale[index] <= min_bound)] = min_bound

    df_out = DataFrame(new_scale.T.astype(np.int32), columns=cols_to_scale)

    df_out[passthrough_columns] = input_data[passthrough_columns]

    return df_out, feature_min_max_parameters


min_max_scale_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "passthrough_columns", "type": "list"},
        {"name": "min_bound", "type": "numeric", "default": 0, "range": [0, 255]},
        {"name": "max_bound", "type": "numeric", "default": 255, "range": [0, 255]},
        {"name": "pad", "type": "float", "default": None, "range": [0, 10]},
        {"name": "feature_min_max_parameters", "type": "dict", "default": None},
        {"name": "feature_min_max_defaults", "type": "dict", "default": None},
    ],
    "output_contract": [
        {"name": "df_out", "type": "DataFrame"},
        {"name": "feature_min_max_parameters", "type": "list", "persist": True},
    ],
}


def normalize(input_data: DataFrame, passthrough_columns: List[str]):
    """
    Scale each feature vector to between -1 and 1 by dividing each feature
    in a feature vector by the absolute maximum value in that feature vector.

    This function transfer the `input_data` and `passthrough_columns` from the previous pipeline block.

    Returns:
        dataframe: Normalized dataframe

    Examples:
        >>> from pandas import DataFrame
        >>> df = DataFrame([[3, 3], [4, 5], [5, 7], [4, 6], [3, 1],
                    [3, 1], [4, 3], [5, 5], [4, 7], [3, 6]],
                    columns=['accelx', 'accely'])
        >>> df['Subject'] = 's01'
        >>> df['Rep'] = [0] * 5 + [1] * 5
        >>> df
            Out:
               accelx  accely Subject  Rep
            0       3       3     s01    0
            1       4       5     s01    0
            2       5       7     s01    0
            3       4       6     s01    0
            4       3       1     s01    0
            5       3       1     s01    1
            6       4       3     s01    1
            7       5       5     s01    1
            8       4       7     s01    1
            9       3       6     s01    1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('testn', df, data_columns=['accelx', 'accely'], group_columns=['Subject','Rep'])
        >>> client.pipeline.add_transform('Normalize')
        >>> r, s = client.pipeline.execute()
        >>> r
            Out:
                  Rep Subject  accelx    accely
                    0   0   s01 1.000000    1.000000
                    1   0   s01 0.800000    1.000000
                    2   0   s01 0.714286    1.000000
                    3   0   s01 0.666667    1.000000
                    4   0   s01 1.000000    0.333333
                    5   1   s01 1.000000    0.333333
                    6   1   s01 1.000000    0.750000
                    7   1   s01 1.000000    1.000000
                    8   1   s01 0.571429    1.000000
                    9   1   s01 0.500000    1.000000


    """

    cols_to_transform = [
        col for col in input_data.columns if col not in passthrough_columns
    ]
    input_data[cols_to_transform] = input_data[cols_to_transform].astype(float)
    data = input_data
    df_out = data[cols_to_transform].apply(lambda x: x / x.abs().max(), axis=1)
    df_out[passthrough_columns] = input_data[passthrough_columns]

    return df_out


normalize_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "passthrough_columns", "type": "list", "element_type": "str"},
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}


def quantize_254(input_data: DataFrame, passthrough_columns: List[str]):
    """
    Scalar quantization of a normalized dataframe to integers between 0 and 254.
    This step should only be applied after features have been normalized to the
    range [-1, 1]. This function transfer the `input_data` and `passthrough_columns`
    from the previous pipeline block. It does not require any feature-specific
    statistics to be saved to the knowledgepack.

    Returns:
        dataframe: quantized dataframe
    """
    cols_to_scale = [
        col for col in input_data.columns if col not in passthrough_columns
    ]
    data_st = input_data[cols_to_scale].applymap(q254).astype(int)

    return concat([data_st, input_data[passthrough_columns]], axis=1)


quantize_254_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "passthrough_columns", "type": "list", "element_type": "str"},
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def q254(x):
    x = x + 1.0  # Add 1.0 to the input value to ensure values between 0 and 2
    qx = x * 127.0
    qx = np.int64(qx)

    return qx
