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
from library.core_functions.feature_generators.fg_histogram import (
    fg_fixed_width_histogram,
)
from pandas import DataFrame


def test_fixed_width():
    data = DataFrame(
        {
            "X": [1] * 5 + [2] * 10 + [3] * 15 + [4] * 20,
            "Y": [1] * 20 + [2] * 15 + [3] * 10 + [4] * 5,
        },
        columns=["X", "Y"],
    )

    data["Subject"] = "A"

    data_segment = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["Subject"]
    )[0]

    """Call the function and match to ground data."""
    columns = ["X"]

    result = fg_fixed_width_histogram(data_segment, columns, -5, 5, 10)
    expected = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 26.0, 51.0, 77.0, 102.0]

    assert type(DataFrame()) == type(result)

    assert expected == result.values.tolist()[0]

    columns = ["X", "Y"]
    result = fg_fixed_width_histogram(data_segment, columns, -5, 5, 10)
    expected = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 64.0, 64.0, 64.0, 64.0]

    assert type(DataFrame()) == type(result)
    assert expected == result.values.tolist()[0]
