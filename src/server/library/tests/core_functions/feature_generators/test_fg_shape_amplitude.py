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
from library.core_functions.feature_generators.fg_shape_amplitude import (
    fg_shape_median_difference,
)
from pandas import DataFrame


def test_fg_shape_median_difference():
    data = DataFrame(
        {
            "X": [
                2123,
                2155,
                2232,
                2330,
                2409,
                2428,
                2371,
                2242,
                2054,
                1834,
                1649,
                1561,
                1552,
                1566,
                1561,
                1478,
                1292,
                1043,
                830,
                744,
                794,
                936,
                1113,
                1294,
                1464,
                1616,
                1782,
                1988,
                2237,
                2536,
                2891,
                3282,
                3661,
                3960,
                4203,
                4613,
                5188,
                1511,
                2211,
                2034,
                740,
                2075,
                2462,
                1721,
                3529,
                3611,
                3624,
                3701,
                3366,
                2813,
                2161,
                1394,
                550,
                337,
                1009,
                1536,
                1885,
                2054,
                2053,
                1912,
                1674,
                1394,
                1133,
                948,
                868,
                868,
                913,
                972,
                1028,
                1066,
                1087,
                1100,
                1102,
                1102,
                1096,
                1080,
                1057,
                1038,
                1038,
                1061,
                1093,
            ],
        },
        columns=["X"],
    )

    data["Subject"] = "A"

    data_segment = dataframe_to_datasegments(
        data, data_columns=["X"], group_columns=["Subject"]
    )[0]

    """Call the function and match to ground data."""
    columns = ["X"]

    result = fg_shape_median_difference(data_segment, columns, 0.5)

    expected_result = 909.0

    assert result.values[0][0] == expected_result

    assert type(DataFrame()) == type(result)
