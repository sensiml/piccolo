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
from numpy import divide, int64, mean
from pandas import DataFrame, concat


def downsampler_for_features(input_data, columns, new_length, **kwargs):
    """
    This function takes `input_data` dataframe as input and group by `group_columns`.
    Then for each group, it drops the `passthrough_columns` and perform downsampling
    on the remaining columns.

    On each column, perform the following steps:

    - Divide the entire column into windows of size total length/`new_length`.
    - Calculate mean for each window
    - Concatenate all the mean values.
    - The length of the downsampled signal is equal to 'new length'.

    Then all such means are concatenated to get `new_length` * # of columns. These constitute
    features in downstream analyses. For instance, if there are three columns and the
    `new_length` value is 12, then total number of means we get is 12 * 3 = 36. Each will represent a feature.

    Args:
        input_data: dataframe
        columns: List of columns to be downsampled
        group_columns (a list): List of columns on which grouping is to be done.
                                 Each group will go through downsampling one at a time
        new_length: integer; Downsampled length
        **kwargs:

    Returns:
        DataFrame; downsampled dataframe

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
        >>> client.pipeline.add_feature_generator(["Downsample"],
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
    win_size = divide(
        len(input_data), new_length
    )  # divide the original data length by the downsampled data length to find the downsampling window size
    win_size = int64(win_size)  # convert to whole number
    data_out = DataFrame()
    strLength = str(new_length)

    for col in columns:
        data_ds = {}
        new_sample_num = 0
        # for each downsampling window
        for i in range(0, len(input_data), win_size)[:new_length]:
            # calculate the downsampled data = mean of the original data in the downsampling window
            data_ds[
                "{0}_{1}".format(col, str(new_sample_num).zfill(len(strLength)))
            ] = [mean(input_data[col][i : i + win_size])]
            new_sample_num += 1

        data_out = concat([data_out, DataFrame.from_dict(data_ds)], axis=1)

    return data_out.reset_index(drop=True)  # discard extra samples


downsampler_for_features_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
        },
        {"name": "new_length", "type": "int", "c_param": 0, "default": 12},
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame", "family": True}],
}


def downsample_core(data, new_len):

    # divide the original data length by the downsampled data length to find the downsampling window size
    win_size = np.divide(len(data), new_len)
    # convert to whole number
    win_size = np.int32(win_size)

    data_ds = []

    for i in range(0, len(data), win_size):  # for each downsampling window
        # calculate the downsampled data = mean of the original data in the downsampling window
        data_ds.append(np.mean(data[i : i + win_size]))

    data_ds = np.array(data_ds[:new_len])  # discard extra samples

    return data_ds


def downsampler_for_features_special(
    input_data, columns, passthrough_columns, new_length, **kwargs
):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "columns", "type": "list", "element_type": "str",
        "description": "Set of columns on which to apply the transform"},
    {"name": "new_length", "type":"int"},
    {"name": "group_columns", "type": "list", "element_type": "str", "handle_by_set": true,
        "description": "Set of columns by which to aggregate"}],

    "post": [
    {"name": "data_out", "type": "DataFrame"}],

    "costs": [{"name": "Bytes", "value": "184"},
              {"name": "Microseconds", "value": "median_sample_size*13.5"}],

    "description": "Data downsampler. Turns downsampled columns into features."
    }
    """

    # divide the original data length by the downsampled data length to find the downsampling window size
    win_size = np.divide(len(input_data), new_length)
    # convert to whole number
    win_size = np.int64(win_size)
    data_out = pd.DataFrame()
    strLength = str(new_length)

    for col in columns:
        data_ds = {}
        new_sample_num = 0
        # for each downsampling window
        for i in range(0, len(input_data), win_size)[:new_length]:
            # calculate the downsampled data = mean of the original data in the downsampling window
            data_ds[
                "{0}_{1}".format(col, str(new_sample_num).zfill(len(strLength)))
            ] = [np.mean(input_data[col][i : i + win_size])]
            new_sample_num += 1

        data_out = pd.concat([data_out, pd.DataFrame.from_dict(data_ds)], axis=1)

    otherInfo = pd.DataFrame(input_data[passthrough_columns].iloc[0]).T.reset_index(
        drop=True
    )

    data_out = pd.concat([data_out, otherInfo], axis=1)

    # discard extra samples
    return data_out.reset_index(drop=True)


# Downsampling function

# Input:
#  original data
# Output:
#  downsampled data


def downsampler_for_features_general(
    input_data, group_columns, passthrough_columns, new_length, **kwargs
):
    """
    This function takes `input_data` dataframe as input and group by `group_columns`.
    Then for each group, it drops the `passthrough_columns` and perform downsampling
    on the remaining columns.

    On each column, perform the following steps:

    - Divide the entire column into windows of size total length/`new_length`.
    - Calculate mean for each window
    - Concatenate all the mean values.
    - The length of the downsampled signal is equal to 'new length'.

    Then all such means are concatenated to get `new_length` * # of columns. These constitute
    features in downstream analyses. For instance, if there are three columns and the
    'new_length` value is 12, then total number of means we get is 12 * 3 = 36. Each will represent a feature.

    Args:
        input_data (dataframe): dataframe containing signal.
        group_columns (a list): List of columns on which grouping is to be done. Each group
                                will go through downsampling one at a time
        passthrough_columns: List of columnsto exclude from downsampling.
        new_length (an integer) : Each axis of interest is downsampled to `new_legth` and
                                  concatenated one after another.
        **kwargs:

    Returns:
        Pandas DataFrame with downsampled data as features.

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> df1 = pd.DataFrame({'Subject': ['s01'] * 22,
                               'Class': ['Walking'] * 10 + ['Running'] * 12,
                               'Rep': [1] * 22})
        >>> df2 = pd.DataFrame(np.random.randn(22, 3),
                               columns=['accelx', 'accely', 'accelz'])
        >>> df = pd.concat([df1, df2], axis=1)
        >>> df
                      Class  Rep Subject    accelx    accely    accelz
        0   Walking    1     s01 -0.362810  0.231797  1.224415
        1   Walking    1     s01 -0.339594 -0.859621  2.138825
        2   Walking    1     s01  1.300808 -0.895784  1.087720
        3   Walking    1     s01 -0.465717  1.196583  1.132943
        4   Walking    1     s01  0.939277  0.488416 -0.527926
        5   Walking    1     s01  0.341099  0.565913 -0.104344
        6   Walking    1     s01 -0.759659 -1.648621  0.283909
        7   Walking    1     s01 -0.987915 -0.369262  0.918509
        8   Walking    1     s01  1.038030 -0.236441  0.378719
        9   Walking    1     s01 -0.471219 -2.056975 -0.922634
        10  Running    1     s01 -0.795920  1.211529 -0.290822
        11  Running    1     s01 -0.793176  0.539278  0.567595
        12  Running    1     s01 -0.391819 -0.885754  0.185144
        13  Running    1     s01  0.728319  0.158360  0.035990
        14  Running    1     s01 -0.709504 -0.910481 -1.555860
        15  Running    1     s01  0.110004 -0.280505 -0.549803
        16  Running    1     s01 -0.573010  0.517376 -1.677610
        17  Running    1     s01  0.294129 -0.940639  0.055527
        18  Running    1     s01  0.526299 -0.418930 -1.653188
        19  Running    1     s01  0.003936 -2.125935  0.123558
        20  Running    1     s01 -0.734292  0.353309  0.080194
        21  Running    1     s01  0.912990 -0.731611 -2.565772
        >>> downsampler_for_features_general(df, ['Subject', u'Class', u'Rep'], [], 5)
                  0         1         2         3         4         5         6
        0 -0.794548  0.168250 -0.299750 -0.139440  0.265118  0.875403 -0.363697
        1 -0.351202  0.417545  0.640188 -0.873787  0.283406 -0.313912  0.150400
                  7         8         9        10        11        12        13
        0 -0.595493 -0.211631 -1.272432  0.138386  0.110567 -1.052831 -0.811042
        1  0.527165 -1.008941 -1.146708  1.681620  1.110331 -0.316135  0.601209
                 14 Subject    Class  Rep
        0 -0.764815     s01  Running    1
        1 -0.271958     s01  Walking    1

    """
    cols_to_transform = [
        col
        for col in input_data.columns
        if col not in passthrough_columns + group_columns
    ]

    str(new_length)

    data_out_total = []

    grpd = input_data.groupby(group_columns)
    for name, grp in grpd:
        name, grp

        data_out = []

        for col in cols_to_transform:
            data_ds = downsample_core(grp[col], new_length)
            data_out = data_out + data_ds.tolist()

        data_out = data_out + list(name)

        data_out_total.append(data_out)

    data_out_total = pd.DataFrame(data_out_total)
    data_out_total.columns = list(data_out_total.columns[:-3]) + group_columns

    return data_out_total  # discard extra samples


downsampler_for_features_general_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the transform",
        },
        {"name": "new_length", "type": "int", "c_param": 0, "default": 12},
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "data_out", "type": "DataFrame"}],
}
