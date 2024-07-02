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

import pytest
from pandas import DataFrame

from library.core_functions.selectors import tree_select


class TestTreeSelect:
    """Test function."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a dataset"""
        columns = [
            "Class",
            "Subject",
            0,
            1,
            2,
            3,
            4,
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
        ]

        data_list = [
            [
                "Crawling",
                "s01",
                347,
                372,
                208,
                153,
                111,
                1016,
                862,
                884,
                827,
                861,
                3977,
                3881,
                3899,
                3943,
                3900,
            ],
            [
                "Crawling",
                "s02",
                347,
                224,
                91,
                83,
                323,
                628,
                557,
                554,
                646,
                668,
                3889,
                3821,
                3858,
                3913,
                3896,
            ],
            [
                "Crawling",
                "s03",
                545,
                503,
                200,
                494,
                542,
                -332,
                199,
                455,
                458,
                469,
                3972,
                3896,
                3851,
                3810,
                3889,
            ],
            [
                "Running",
                "s01",
                -21,
                -23,
                -16,
                -40,
                16,
                -4029,
                -3971,
                -4051,
                -3949,
                -4065,
                696,
                641,
                650,
                720,
                605,
            ],
            [
                "Running",
                "s02",
                422,
                453,
                431,
                469,
                432,
                -3940,
                -4037,
                -3989,
                -3979,
                -4037,
                825,
                870,
                830,
                858,
                846,
            ],
            [
                "Running",
                "s03",
                350,
                366,
                360,
                339,
                398,
                -4054,
                -4045,
                -4125,
                -4067,
                -4109,
                260,
                263,
                185,
                241,
                234,
            ],
            [
                "Walking",
                "s01",
                -10,
                -46,
                0,
                -16,
                18,
                -4030,
                -4049,
                -4020,
                -4040,
                -4028,
                564,
                559,
                555,
                564,
                558,
            ],
            [
                "Walking",
                "s02",
                375,
                413,
                374,
                385,
                391,
                -4024,
                -3995,
                -4029,
                -4009,
                -3996,
                730,
                658,
                670,
                722,
                669,
            ],
            [
                "Walking",
                "s03",
                353,
                317,
                283,
                325,
                353,
                -4068,
                -4073,
                -4085,
                -4064,
                -4063,
                -138,
                -87,
                -114,
                -116,
                -98,
            ],
        ]

        self.data = DataFrame(data_list, columns=columns)

    def test_ttest_select(self):
        """Calling ttest feature selector function"""
        results, eliminated_featues = tree_select(
            self.data, "Class", 2, ["Subject", "Class"]
        )

        assert results.columns.tolist() == ["Subject", "Class", 9, 8]
        assert eliminated_featues == [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14]
