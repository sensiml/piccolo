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

from datamanager.datasegments import (
    dataframe_to_datasegments,
    datasegments_equal,
)
from library.core_functions.segment_transforms import tr_segment_pre_emphasis_filter
from pandas import DataFrame, concat

a = DataFrame(
    [
        1123.0,
        1168.0,
        1253.0,
        1336.0,
        1388.0,
        1417.0,
        1458.0,
        1529.0,
        1606.0,
        1646.0,
    ],
    columns=["Audio_Stream"],
)

a["Subject"] = "1112"
a["Label"] = "howling"
b = DataFrame(
    [
        689.0,
        855.0,
        2097.0,
        1928.0,
        11.0,
        548.0,
        1035.0,
        1039.0,
        1665.0,
        1820.0,
    ],
    columns=["Audio_Stream"],
)

b["Subject"] = "61025"
b["Label"] = "eating"
data = dataframe_to_datasegments(
    concat([a, b]).reset_index(drop=True),
    data_columns=["Audio_Stream"],
    group_columns=["Subject", "Label"],
)


def test_tr_segment_pre_emphasis_filter():
    """Calls tr_segment_pre_emphasis_filter and check output dataframe with ground truth data frame"""

    results = tr_segment_pre_emphasis_filter(
        data,
        input_column="Audio_Stream",
        group_columns=["Subject", "Label"],
        alpha=0.97,
        prior=0,
    )

    a_gt = DataFrame(
        [
            561.0,
            39.0,
            60.0,
            60.0,
            46.0,
            35.0,
            41.0,
            57.0,
            61.0,
            44.0,
        ],
        dtype="int16",
        columns=["Audio_Stream"],
    )
    a_gt["Subject"] = "1112"
    a_gt["Label"] = "howling"
    b_gt = DataFrame(
        [
            344.0,
            93.0,
            633.0,
            -54.0,
            -930.0,
            268.0,
            251.0,
            17.0,
            328.0,
            102.0,
        ],
        dtype="int16",
        columns=["Audio_Stream"],
    )
    b_gt["Subject"] = "61025"
    b_gt["Label"] = "eating"

    expected_result = dataframe_to_datasegments(
        concat([a_gt, b_gt]).reset_index(drop=True),
        data_columns=["Audio_Stream"],
        group_columns=["Subject", "Label"],
    )

    datasegments_equal(results, expected_result)
