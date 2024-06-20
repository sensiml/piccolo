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

import pytest
from datamanager.datasegments import dataframe_to_datasegments, datasegments_equal
from library.core_functions.segment_transforms import (
    tr_segment_normalize,
    tr_segment_scale_factor,
    tr_segment_strip,
)
from numpy import array, int32
from pandas import DataFrame


@pytest.fixture
def accx_accy_2_group_data():
    df = DataFrame(
        [
            [
                5393,
                -6310,
            ],
            [13675, -7920],
            [18572, -10815],
            [5039, -18178],
            [4882, -3419],
            [5842, -11819],
            [9514, -19908],
            [14003, -10131],
            [5951, -4927],
            [17153, -8763],
            [
                5393,
                -6310,
            ],
            [13675, -7920],
            [18572, -10815],
            [5039, -18178],
            [4882, -3419],
            [5842, -11819],
            [9514, -19908],
            [14003, -10131],
            [5951, -4927],
            [17153, -8763],
            [-2000, 0],
            [-1500, 0],
            [-1000, 0],
            [-500, 0],
            [0, 0],
            [500, 0],
            [1000, 0],
            [1500, 0],
            [2000, 0],
            [2500, 0],
            [32767, -32768],
            [32767, -32768],
            [32767, -32768],
            [32767, -32768],
            [32767, -32768],
            [32767, -32768],
            [32767, -32768],
            [32767, -32768],
            [32767, -32768],
            [-32768, 32767],
        ],
        columns=["accelx", "accely"],
    )
    df["Subject"] = "s01"
    df["Rep"] = [0] * 10 + [1] * 10 + [2] * 10 + [3] * 10

    return dataframe_to_datasegments(
        df, group_columns=["Subject", "Rep"], data_columns=["accelx", "accely"]
    )


def test_tr_segment_scale_factor(accx_accy_2_group_data):

    pass

    group_columns = ["Subject", "Rep"]
    input_columns = ["accelx", "accely"]

    result = tr_segment_scale_factor(
        copy.deepcopy(accx_accy_2_group_data),
        group_columns,
        input_columns,
        "scalar",
        scale_factor=2.0,
    )

    # fmt: off
    expected = [
        {'data': array([[ 2696,  6837,  9286,  2519,  2441,  2921,  4757,  7001,  2975, 8576], [-3155, -3960, -5407, -9089, -1709, -5909, -9954, -5065, -2463, -4381]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 0}}, 
        {'data': array([[ 2696,  6837,  9286,  2519,  2441,  2921,  4757,  7001,  2975, 8576], [-3155, -3960, -5407, -9089, -1709, -5909, -9954, -5065, -2463, -4381]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 1}},
        {'data': array([[-1000,  -750,  -500,  -250,     0,   250,   500,   750,  1000, 1250], [    0,     0,     0,     0,     0,     0,     0,     0,     0, 0]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 2}},
        {'data': array([[ 16383,  16383,  16383,  16383,  16383,  16383,  16383,  16383, 16383, -16384], [-16384, -16384, -16384, -16384, -16384, -16384, -16384, -16384, -16384,  16383]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 3}}]
    # fmt: on

    datasegments_equal(result, expected)

    result = tr_segment_scale_factor(
        copy.deepcopy(accx_accy_2_group_data),
        group_columns,
        input_columns,
        "scalar",
        scale_factor=0.1,
    )

    # fmt: off
    expected = [{'data': array([[ 32767,  32767,  32767,  32767,  32767,  32767,  32767,  32767,  32767,  32767],[-32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 0}},
         {'data': array([[ 32767,  32767,  32767,  32767,  32767,  32767,  32767,  32767,  32767,  32767],[-32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 1}},
         {'data': array([[-20000, -15000, -10000,  -5000,      0,   5000,  10000,  15000,   20000,  25000], [     0,      0,      0,      0,      0,      0,      0,      0,       0,      0]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 2}},        
         {'data': array([[ 32767,  32767,  32767,  32767,  32767,  32767,  32767,  32767,   32767, -32768], [-32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768,  -32768,  32767]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 3}}]
    # fmt: on

    datasegments_equal(result, expected)


class TestTRSegmentNormalize:
    def test_tr_segment_normalize_mean(self, accx_accy_2_group_data):

        group_columns = ["Subject", "Rep"]
        input_columns = ["accelx", "accely"]
        mode = "mean"
        result = tr_segment_normalize(
            copy.deepcopy(accx_accy_2_group_data), group_columns, input_columns, mode
        )

        # fmt: off
        expected = [{'data': array([[-17624,  14042,  32767, -18978, -19578, -15907,  -1867,  15296, -15491,  27341], [ 13219,   7774,  -2015, -26916,  22996,  -5411, -32767,    297, 17896,   4924]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 0}},
                    {'data': array([[-17624,  14042,  32767, -18978, -19578, -15907,  -1867,  15296, -15491,  27341], [ 13219,   7774,  -2015, -26916,  22996,  -5411, -32767,    297, 17896,   4924]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 1}},
                    {'data': array([[-32767, -25485, -18203, -10922,  -3640,   3640,  10922,  18203, 25485,  32767], [     0,      0,      0,      0,      0,      0,      0,      0, 0,      0]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 2}},
                    {'data': array([[  6553,   6553,   6553,   6553,   6553,   6553,   6553,   6553, 6553, -32768], [ -6553,  -6553,  -6553,  -6553,  -6553,  -6553,  -6553,  -6553, -6553,  32767]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 3}}
                    ]
        # fmt: on

        datasegments_equal(result, expected)

    def test_tr_segment_normalize_median(self, accx_accy_2_group_data):

        mode = "median"

        group_columns = ["Subject", "Rep"]
        input_columns = ["accelx", "accely"]

        result = tr_segment_normalize(
            copy.deepcopy(accx_accy_2_group_data), group_columns, input_columns, mode
        )

        # fmt: off
        expected = [{'data': array([[ -7072,  17963,  32767,  -8142,  -8616,  -5714,   5385,  18955, -5385,  28477], [  9826,   4783,  -4284, -27348,  18881,  -7429, -32766,  -2142, 14158,   2142]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 0}},
                    {'data': array([[ -7072,  17963,  32767,  -8142,  -8616,  -5714,   5385,  18955, -5385,  28477], [  9826,   4783,  -4284, -27348,  18881,  -7429, -32766,  -2142, 14158,   2142]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 1}},
                    {'data': array([[-32767, -25485, -18203, -10922,  -3640,   3640,  10922,  18203, 25485,  32767], [     0,      0,      0,      0,      0,      0,      0,      0, 0,      0]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 2}},
                    {'data': array([[     0,      0,      0,      0,      0,      0,      0,      0, 0, -32768], [     0,      0,      0,      0,      0,      0,      0,      0, 0,  32767]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 3}}
                    ]
        # fmt: on

        datasegments_equal(result, expected)

    def test_tr_segment_normalize_none(self, accx_accy_2_group_data):

        mode = "none"

        group_columns = ["Subject", "Rep"]
        input_columns = ["accelx", "accely"]

        result = tr_segment_normalize(
            copy.deepcopy(accx_accy_2_group_data), group_columns, input_columns, mode
        )

        # fmt: off
        expected = [{'data': array([[  9514,  24127,  32767,   8890,   8613,  10307,  16785,  24705, 10499,  30263], [-10385, -13035, -17800, -29919,  -5627, -19453, -32767, -16674,-8109, -14423]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 0}}, 
                    {'data': array([[  9514,  24127,  32767,   8890,   8613,  10307,  16785,  24705, 10499,  30263], [-10385, -13035, -17800, -29919,  -5627, -19453, -32767, -16674, -8109, -14423]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 1}},
                    {'data': array([[-26213, -19660, -13106,  -6553,      0,   6553,  13106,  19660, 26213,  32767], [     0,      0,      0,      0,      0,      0,      0,      0, 0,      0]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 2}},
                    {'data': array([[ 32767,  32767,  32767,  32767,  32767,  32767,  32767,  32767, 32767, -32768], [-32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768,  32767]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 3}}
                    ]
        # fmt: on

        datasegments_equal(result, expected)

    def test_tr_segment_normalize_zero(self, accx_accy_2_group_data):

        mode = "zero"

        group_columns = ["Subject", "Rep"]
        input_columns = ["accelx", "accely"]

        result = tr_segment_normalize(
            copy.deepcopy(accx_accy_2_group_data), group_columns, input_columns, mode
        )

        # fmt: off
        expected = [{'data': array([[     0,  20591,  32766,   -880,  -1270,   1116,  10246,  21407, 1387,  29238], [ 0,  -3879, -10855, -28598,   6966, -13274, -32767,  -9207, 3332,  -5910]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 0}}, 
                    {'data': array([[     0,  20591,  32766,   -880,  -1270,   1116,  10246,  21407, 1387,  29238], [ 0,  -3879, -10855, -28598,   6966, -13274, -32767,  -9207, 3332,  -5910]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 1}},
                    {'data': array([[    0,  3640,  7281, 10922, 14563, 18203, 21844, 25485, 29126, 32767],[    0,     0,     0,     0,     0,     0,     0,     0,     0, 0]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 2}}, 
                    {'data': array([[     0,      0,      0,      0,      0,      0,      0,      0,0, -32768], [     0,      0,      0,      0,      0,      0,      0,      0, 0,  32767]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 3}}]
        # fmt: on

        datasegments_equal(result, expected)


class TestTRSegmentStrip:
    def test_tr_segment_strip_zero(self, accx_accy_2_group_data):

        mode = "zero"

        group_columns = ["Subject", "Rep"]
        input_columns = ["accelx", "accely"]

        result = tr_segment_strip(
            copy.deepcopy(accx_accy_2_group_data), group_columns, input_columns, mode
        )

        # fmt: off
        expected = [{'data': array([[     0,   8282,  13179,   -354,   -511,    449,   4121,   8610, 558,  11760], [     0,  -1610,  -4505, -11868,   2891,  -5509, -13598,  -3821, 1383,  -2453]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 0}}, 
                    {'data': array([[     0,   8282,  13179,   -354,   -511,    449,   4121,   8610, 558,  11760],[     0,  -1610,  -4505, -11868,   2891,  -5509, -13598,  -3821,1383,  -2453]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 1}}, 
                    {'data': array([[   0,  500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500], [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 2}}, 
                    {'data': array([[     0,      0,      0,      0,      0,      0,      0,      0, 0, -32768], [     0,      0,      0,      0,      0,      0,      0,      0, 0,  32767]], dtype=int32), 'columns': ['accelx', 'accely'], 'metadata': {'Subject': 's01', 'Rep': 3}}]
        # fmt: on

        datasegments_equal(result, expected)
