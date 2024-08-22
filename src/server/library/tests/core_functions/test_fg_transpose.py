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

from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.feature_generators.fg_transpose import (
    fg_interleave_signal,
    fg_transpose_signal,
)
from pandas import DataFrame


def test_fg_interleave_signal():
    # fmt: off
    data = DataFrame(
        {"X": [1] * 5 + [2] * 5 + [3] * 5,
         "Y": [-1] * 5 + [-2] * 5 + [-3] * 5,
         "segment_uuid":[1]*15
        },
        
        columns=["X", "Y",'segment_uuid'],
    )
    # fmt: on
    data_segments = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["segment_uuid"]
    )[0]

    columns = ["X"]
    result = fg_interleave_signal(copy.deepcopy(data_segments), columns, 10, 1)
    expected = [1] * 5 + [2] * 5

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    columns = ["X"]
    result = fg_interleave_signal(copy.deepcopy(data_segments), columns, 10, 2)
    expected = [1] * 3 + [2] * 2

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    columns = ["X"]
    result = fg_interleave_signal(copy.deepcopy(data_segments), columns, 20, 2)
    expected = [1] * 3 + [2] * 2 + [3] * 5

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    columns = ["X", "Y"]
    result = fg_interleave_signal(copy.deepcopy(data_segments), columns, 10, 1)
    expected = [1, -1] * 5 + [2, -2] * 5

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    result = fg_interleave_signal(copy.deepcopy(data_segments), columns, 10, 2)
    expected = [1, -1] * 3 + [2, -2] * 2

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    result = fg_interleave_signal(copy.deepcopy(data_segments), columns, 20, 2)
    expected = [1, -1] * 3 + [2, -2] * 2 + [3, -3] * 5

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)


def test_fg_transpose_signal():
    # fmt: off
    data = DataFrame(
        {"X": [1] * 5 + [2] * 5 + [3] * 5,
         "Y": [-1] * 5 + [-2] * 5 + [-3] * 5,
         "segment_uuid":[1]*15
        },
        
        columns=["X", "Y",'segment_uuid'],
    )
    # fmt: on
    data_segment = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["segment_uuid"]
    )[0]

    columns = ["X"]
    result = fg_transpose_signal(copy.deepcopy(data_segment), columns, 10)
    expected = [1] * 5 + [2] * 5

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    columns = ["X"]
    result = fg_transpose_signal(copy.deepcopy(data_segment), columns, 20)
    expected = [1] * 5 + [2] * 5 + [3] * 5 + [3] * 5

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    columns = ["X", "Y"]
    result = fg_transpose_signal(copy.deepcopy(data_segment), columns, 10)
    expected = [1] * 5 + [2] * 5 + [-1] * 5 + [-2] * 5

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    result = fg_transpose_signal(copy.deepcopy(data_segment), columns, 20)
    expected = [1] * 5 + [2] * 5 + [3] * 10 + [-1] * 5 + [-2] * 5 + [-3] * 10

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)


def test_fg_transpose_signal_single_frame():
    # fmt: off
    data = DataFrame(
        {"X": [1] * 5 + [2] * 5 + [3] * 5,
         "Y": [-1] * 5 + [-2] * 5 + [-3] * 5,
         "segment_uuid":list(range(15))
        },
        
        columns=["X", "Y",'segment_uuid'],
    )
    # fmt: on
    data_segment = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["segment_uuid"]
    )

    columns = ["X"]
    result = fg_transpose_signal(copy.deepcopy(data_segment[0]), columns, 1)
    expected = [1]

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)

    columns = ["X", "Y"]
    result = fg_transpose_signal(copy.deepcopy(data_segment[0]), columns, 1)
    expected = [1, -1]

    assert type(DataFrame()) == type(result)
    assert expected == list(result.loc[0].values)
