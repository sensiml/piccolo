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

from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.sensor_filters import st_moving_average
from numpy import array
from numpy.testing import assert_array_almost_equal
from pandas import DataFrame


def test_tr_ma_filter_symmetric():
    data = DataFrame(
        {"Ax": range(100), "Ay": range(100)},
    )
    data["Subject"] = 0

    data = dataframe_to_datasegments(
        data, data_columns=["Ax", "Ay"], group_columns=["Subject"]
    )
    output_data = st_moving_average(data, ["Subject"], ["Ax"], 10)
    expected = array(
        [
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79,
            80,
            81,
            82,
            83,
            84,
            85,
            86,
            87,
            88,
            89,
            90,
            90,
            90,
            91,
            92,
            92,
            92,
            93,
            94,
            94,
        ]
    )

    assert type(list()) == type(output_data)

    assert_array_almost_equal(expected, output_data[0]["data"][0])


def test_tr_ma_filter_symmetric_group_columns():

    data = DataFrame(
        {"Ax": [2] * 10 + [5] * 10, "Ay": [2] * 20},
    )
    data["Subject"] = [0] * 10 + [1] * 10
    data = dataframe_to_datasegments(
        data, data_columns=["Ax", "Ay"], group_columns=["Subject"]
    )

    output_data = st_moving_average(data, ["Subject"], ["Ax"], 10)
    expected1 = array([2] * 10)
    expected2 = array([5] * 10)

    assert type(list()) == type(output_data)

    assert_array_almost_equal(expected1, output_data[0]["data"][0])
    assert_array_almost_equal(expected2, output_data[1]["data"][0])


def test_tr_ma_filter_symmetric_applied_twices():
    data = DataFrame(
        {"Ax": [2] * 10 + [5] * 10, "Ay": [2] * 20},
    )
    data["Subject"] = [0] * 10 + [1] * 10
    data = dataframe_to_datasegments(
        data, data_columns=["Ax", "Ay"], group_columns=["Subject"]
    )

    expected_Ax_1 = array([2] * 10)
    expected_Ax_2 = array([5] * 10)
    expected_Ay_1 = array([2] * 10)
    expected_Ay_2 = array([2] * 10)

    output_data = st_moving_average(data, ["Subject"], ["Ax"], 10)

    assert_array_almost_equal(expected_Ax_1, output_data[0]["data"][0])
    assert_array_almost_equal(expected_Ax_2, output_data[1]["data"][0])

    output_data = st_moving_average(output_data, ["Subject"], ["Ay"], 10)

    assert type(list()) == type(output_data)

    assert_array_almost_equal(expected_Ay_1, output_data[0]["data"][1])
    assert_array_almost_equal(expected_Ay_2, output_data[1]["data"][1])
    assert_array_almost_equal(expected_Ax_1, output_data[0]["data"][0])
    assert_array_almost_equal(expected_Ax_2, output_data[1]["data"][0])
