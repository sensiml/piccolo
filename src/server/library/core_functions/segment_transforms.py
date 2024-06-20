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
from library.core_functions import MAX_INT_16, MIN_INT_16, fix_overflow, fix_rounding
from pandas import DataFrame


def int16_check(value):

    if value > 32767:
        return 32767
    if value < -32767:
        return -32767

    return value


def get_scale_factor(max, min):
    sf = 1.0
    # get abs of min,max:
    if max < 0:
        max *= -1
    if min < 0:
        min *= -1

    # calc scale factor based on larger abs value:
    if max >= min:
        if max > 0:
            sf = 32767 / max
    else:
        if min > 0:
            sf = 32767 / min

    return sf


def autoscale(x, mean, max_value, min_value):

    max_value = int16_check(max_value - mean)
    min_value = int16_check(min_value - mean)
    sf = get_scale_factor(max_value, min_value)

    x -= mean
    x *= sf

    x[x > MAX_INT_16] = MAX_INT_16
    x[x < MIN_INT_16] = MIN_INT_16

    return x


def tr_segment_offset_factor(
    input_data: DataFrame, input_columns: list, offset_factor: float = 0.0
):
    """
    Adds an offset to each column in the input data. This can be used in conjunction with a scale factor to split
    multiple channels into distinct bands of data.

    Args:
        input_data (DataFrame): The input data to transform.
        input_columns (list): A list of column names to transform.
        offset_factor (float, optional): The number by which input_columns are offset by. Defaults to 0.0.

    Returns:
        DataFrame: The updated input data with the transformation applied.
    """

    col_indexes = [input_data[0]["columns"].index(column) for column in input_columns]
    for segment in input_data:
        segment["data"][col_indexes] = fix_overflow(
            segment["data"][col_indexes] + int(offset_factor), col_indexes
        )

    return input_data


tr_segment_offset_factor_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
        {
            "name": "offset_factor",
            "type": "int",
            "default": 0,
            "c_param": 0,
            "range": [MIN_INT_16, MAX_INT_16],
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def tr_segment_strip(
    input_data: DataFrame, group_columns: list, input_columns: list, type: str
) -> DataFrame:
    """
    Remove each signal's mean or min from its values, while leaving specified passthrough columns unmodified.
    This function transforms a DataFrame in such a way that the entire signal is shifted towards 'mean', 'median', 'min', or 'zero'.

    Args:
        input_data: The input DataFrame.
        group_columns: The list of columns to group by.
        input_columns: The list of column names to use.
        type: Possible values are 'mean' or 'min', 'median' and 'zero'.
         zero - zeros out the segment by subtracting the starting value of data
         from the rest of the segment

    Returns:
        A DataFrame containing the transformed signal.

    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df
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

        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns=['accelx', 'accely', 'accelz'],
                            group_columns=['Subject', 'Class', 'Rep'],
                            label_column='Class')

        >>> client.pipeline.add_transform("Strip",
                           params={"input_columns": ['accelx'],
                                   "type": 'min' })

        >>> results, stats = client.pipeline.execute()
        >>> print results
            out:
                       Class  Rep Subject  accelx  accely  accelz
                0   Crawling    1     s01   378.0     569    4019
                1   Crawling    1     s01   358.0     594    4051
                2   Crawling    1     s01   334.0     638    4049
                3   Crawling    1     s01   341.0     678    4053
                4   Crawling    1     s01   373.0     708    4051
                5   Crawling    1     s01   411.0     733    4028
                6   Crawling    1     s01   451.0     733    3988
                7   Crawling    1     s01   493.0     696    3947
                8   Crawling    1     s01   519.0     677    3943
                9   Crawling    1     s01   529.0     695    3988
                10  Crawling    1     s01     0.0    2558    4609
                11   Running    1     s01    22.0   -3971     843
                12   Running    1     s01    19.0   -3982     836
                13   Running    1     s01    23.0   -3973     832
                14   Running    1     s01    26.0   -3973     834
                15   Running    1     s01    18.0   -3978     844
                16   Running    1     s01    14.0   -3993     842
                17   Running    1     s01     2.0   -3984     821
                18   Running    1     s01     2.0   -3966     813
                19   Running    1     s01     0.0   -3971     826
                20   Running    1     s01     4.0   -3988     827
                21   Running    1     s01     9.0   -3984     843
    """

    col_indexes = [input_data[0]["columns"].index(column) for column in input_columns]
    for segment in input_data:
        if type == "mean":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: x - x.mean(), 1, segment["data"][col_indexes]
            )
        elif type == "min":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: x - x.min(), 1, segment["data"][col_indexes]
            )
        elif type == "median":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: x - np.median(x), 1, segment["data"][col_indexes]
            )
        elif type == "zero":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: x - x[0], 1, segment["data"][col_indexes]
            )
        else:
            raise Exception("Invalid Parameter!")

        fix_overflow(segment["data"], col_indexes)

    return input_data


tr_segment_strip_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
        {
            "name": "type",
            "type": "str",
            "options": [
                {"name": "mean"},
                {"name": "median"},
                {"name": "min"},
                {"name": "zero"},
            ],
            "c_param": 0,
            "default": "mean",
            "c_param_mapping": {"mean": 0, "median": 1, "min": 2, "zero": 3},
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}


def tr_segment_scale_factor(
    input_data: DataFrame,
    group_columns: list,
    input_columns: list,
    mode: str,
    scale_factor: float = 1,
) -> DataFrame:
    """
    Performs a pre-emphasis filter on the input columns and modifies the sensor streams in place.
    This is a first-order FIR filter that performs a weighted average of each sample with the previous sample.

    Args:
        input_data (DataFrame): Input data containing the sensor streams to be filtered.
        input_column (str): Name of the sensor stream to apply the pre-emphasis filter to.
        group_columns (list): List of column names to group by.
        alpha (float, optional): Pre-emphasis factor (weight given to the previous sample). Defaults to 0.97.
        prior (int, optional): The value of the previous sample. Defaults to 0.

    Returns:
        DataFrame: Input data after having been passed through a pre-emphasis filter.

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
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_transform('Scale Factor',
                            params={'scale_factor':4096.,
                            'input_columns':['accely']})
        >>> results, stats = client.pipeline.execute()

    """
    col_indexes = [input_data[0]["columns"].index(col) for col in input_columns]

    for seg in input_data:

        # TODO: reimplement scale factor for std and median
        if mode == "std":
            raise Exception("Not Currently Implemented")
            # std = seg['data'][col_indexes].std(ddof=0)
            # seg['data'][col_indexes] /= int(x.std(ddof=0)) if int(x.std(ddof=0)) != 0 else x)

        elif mode == "median":
            raise Exception("Not Currently Implemented")
            # df_out = (
            #    grouped[input_columns]
            #    .transform(lambda x: x / int(x.median()) if int(x.median()) != 0 else x)
            #    .astype(int)
            # )
        elif mode == "scalar":
            seg["data"][col_indexes] = seg["data"][col_indexes] / scale_factor

        else:
            raise Exception("Invalid Parameter! {}".format(mode))

    for seg in input_data:
        fix_rounding(seg["data"], col_indexes)
        fix_overflow(seg["data"], col_indexes)

    return input_data


tr_segment_scale_factor_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
        {
            "name": "mode",
            "type": "str",
            "options": [{"name": "scalar"}],
            "c_param": 0,
            "c_param_mapping": {"std": 0, "median": 1, "scalar": 2},
            "default": "scalar",
        },
        {
            "name": "scale_factor",
            "type": "float",
            "c_param": 1,
            "default": 1.0,
            "range": [0.1, 10.0],
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def pre_emphasis_filter(data_stream, alpha=0.97, prior=0):
    # assuming data_stream in int16 range
    y = np.zeros(data_stream.shape[0], dtype="int16")

    # what is the range of alpha? for now assuming it to be less than or equal to 1
    Q = 15
    alpha_Q = round(alpha / 1 * (2 ** Q - 1))

    for i in range(0, data_stream.shape[0]):
        y[i] = np.floor(
            (data_stream[i] * (2 ** Q) - (alpha_Q * prior)) / (2 ** (Q + 1))
        )
        prior = data_stream[i]

    return y


def tr_segment_pre_emphasis_filter(
    input_data: DataFrame,
    input_column: str,
    group_columns: list,
    alpha: float = 0.97,
    prior: int = 0,
) -> DataFrame:
    """Performs a pre-emphasis filter on the input columns and modifies the sensor
    streams in place. This is a first-order Fir filter that performs a weighted
    average of each sample with the previous sample.

    Args:
        input_column (str): sensor stream to apply pre_emphasis filter against
        alpha (float): pre-emphasis factor (weight given to the previous sample)
        prior (int): the value of the previous sample, default is 0

    Returns:
        input data after having been passed through a pre-emphasis filter

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
        >>> client.pipeline.set_input_data('test_data', df, force=True)

        >>> client.pipeline.add_transform("Pre-emphasis Filter",
                           params={"input_column": 'accelx',
                                "alpha": 0.97,
                                "prior": 2})

        >>> results, stats = client.pipeline.execute()
        >>> print results
            out:
                       Class  Rep Subject  accelx  accely  accelz
                0   Crawling    1     s01     187     569    4019
                1   Crawling    1     s01      -5     594    4051
                2   Crawling    1     s01      -7     638    4049
                3   Crawling    1     s01       8     678    4053
                4   Crawling    1     s01      21     708    4051
                5   Crawling    1     s01      24     733    4028
                6   Crawling    1     s01      26     733    3988
                7   Crawling    1     s01      27     696    3947
                8   Crawling    1     s01      20     677    3943
                9   Crawling    1     s01      12     695    3988
                10  Crawling    1     s01    -257    2558    4609
                11   Running    1     s01     -23   -3971     843
                12   Running    1     s01      -3   -3982     836
                13   Running    1     s01       1   -3973     832
                14   Running    1     s01       0   -3973     834
                15   Running    1     s01      -5   -3978     844
                16   Running    1     s01      -3   -3993     842
                17   Running    1     s01      -7   -3984     821
                18   Running    1     s01      -1   -3966     813
                19   Running    1     s01      -2   -3971     826
                20   Running    1     s01       1   -3988     827
                21   Running    1     s01       1   -3984     843


    """
    col_index = input_data[0]["columns"].index(input_column)
    for segment in input_data:
        segment["data"][col_index] = pre_emphasis_filter(
            segment["data"][col_index],
            alpha=alpha,
            prior=prior,
        )

    return input_data


tr_segment_pre_emphasis_filter_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_column", "type": "str"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "alpha",
            "type": "float",
            "default": 0.97,
            "c_param": 0,
            "range": [0.1, 1.0],
        },
        {
            "name": "prior",
            "type": "int",
            "default": 0,
            "c_param": 1,
            "range": [MIN_INT_16, MAX_INT_16],
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}


def tr_segment_normalize(
    input_data: DataFrame, group_columns: list, input_columns: list, mode: str
) -> DataFrame:
    """
    Subtract a value from the data defined by the mode selected, then expand the data to fill MAX_INT_16.

    Args:
        input_data (DataFrame): Input data to be normalized.
        group_columns (list): List of column names to group by.
        input_columns (list): List of column names to be normalized.
        mode (str): Normalization mode, which can be 'mean', 'median', "zero" or 'none'.
         zero - zeros out the segment by subtracting the starting value of data
         from the rest of the segment
         none - skips the subtraction steps and only expands the data

    Returns:
        DataFrame: Normalized data as a new DataFrame.
    """

    col_indexes = [input_data[0]["columns"].index(column) for column in input_columns]

    for segment in input_data:
        if mode == "mean":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: autoscale(x.astype(np.float), x.mean(), x.max(), x.min()),
                1,
                segment["data"][col_indexes],
            )

        elif mode == "median":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: autoscale(x.astype(np.float), np.median(x), x.max(), x.min()),
                1,
                segment["data"][col_indexes],
            )

        elif mode == "none":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: autoscale(x.astype(np.float), 0, x.max(), x.min()),
                1,
                segment["data"][col_indexes],
            )
        elif mode == "zero":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: autoscale(x.astype(np.float), x[0], x.max(), x.min()),
                1,
                segment["data"][col_indexes],
            )

        else:
            raise Exception("Invalid Type Parameter!")

    return input_data


tr_segment_normalize_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
        {
            "name": "mode",
            "type": "str",
            "options": [
                {"name": "mean"},
                {"name": "median"},
                {"name": "none"},
                {"name": "zero"},
            ],
            "c_param": 0,
            "c_param_mapping": {"mean": 0, "median": 1, "none": 2, "zero": 3},
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}


def tr_segment_vertical_scale(
    input_data: DataFrame, input_columns: list, group_columns: list
) -> DataFrame:
    """
    Scale the amplitude of the input columns to MAX_INT_16 or as close as possible without overflowing.
    Scaling is only applied to the input columns; other sensor columns will be ignored.

    Args:
        input_data (DataFrame): Input data to be vertically scaled.
        input_columns (list): List of column names to be vertically scaled.
        group_columns (list): List of column names on which grouping is to be done. Each group will be scaled one at a time.

    Returns:
        DataFrame: The vertically scaled DataFrame for each segment for input_columns.
    """

    col_indexes = [input_data[0]["columns"].index(column) for column in input_columns]

    for segment in input_data:
        segment["data"][col_indexes] = np.apply_along_axis(
            lambda x: autoscale(x.astype(np.float), 0, x.max(), x.min()),
            1,
            segment["data"][col_indexes],
        )

    return input_data


tr_segment_vertical_scale_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "input_columns", "type": "list"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}


def tr_segment_rotate(
    input_data: DataFrame, group_columns: list, input_columns: list, mode: str
) -> DataFrame:
    """
    Applies a rotation matrix to the entire segment so that the origin point of the rotation is always zero

    Args:
        input_data (DataFrame): Input data to be rotated.
        group_columns (list): List of column names to group by.
        input_columns (list): List of column names to be normalized.

    Returns:
        DataFrame: Rotated Sensor Data
    """

    col_indexes = [input_data[0]["columns"].index(column) for column in input_columns]

    for segment in input_data:
        if mode == "mean":
            segment["data"][col_indexes] = np.apply_along_axis(
                lambda x: autoscale(x.astype(np.float), x.mean(), x.max(), x.min()),
                1,
                segment["data"][col_indexes],
            )

        else:
            raise Exception("Invalid Type Parameter!")

    return input_data


tr_segment_normalize_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {"name": "input_columns", "type": "list", "element_type": "str"},
        {
            "name": "mode",
            "type": "str",
            "options": [
                {"name": "mean"},
                {"name": "median"},
                {"name": "none"},
                {"name": "zero"},
            ],
            "c_param": 0,
            "c_param_mapping": {"mean": 0, "median": 1, "None": 2, "zero": 3},
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}
