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

import pandas as pd
from datamanager.datasegments import datasegments_equal
from library.core_functions.segmenters.utils import process_segment_results
from numpy import array


def combine(lists):
    return [item for sublist in lists for item in sublist]


def test_process_segment_results():
    num_segments = 3
    seg_length = 5

    input_data = pd.DataFrame(
        {
            "ax": combine([[x] * seg_length for x in range(num_segments)]) + ["0"],
            "ay": combine([[x**2] * seg_length for x in range(num_segments)]) + ["0"],
            "label": ["A"] * seg_length * num_segments + ["0"],
            "metadata_1": ["B"] * seg_length * num_segments + ["0"],
        }
    )

    seg_beg_end_list = [
        [seg_length * i, seg_length + seg_length * i - 1] for i in range(num_segments)
    ]
    group_columns = ["label", "metadata_1"]

    result = process_segment_results(
        input_data, seg_beg_end_list, group_columns, return_segment_index=False
    )

    # fmt: off
    expected_result = [{'columns': ['ax', 'ay'], 'metadata': {'label': 'A', 'metadata_1': 'B', 'SegmentID': 0}, 'statistics': {}, 'data': array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])},
                       {'columns': ['ax', 'ay'], 'metadata': {'label': 'A', 'metadata_1': 'B', 'SegmentID': 1}, 'statistics': {}, 'data': array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]])},
                       {'columns': ['ax', 'ay'], 'metadata': {'label': 'A', 'metadata_1': 'B', 'SegmentID': 2}, 'statistics': {}, 'data': array([[2, 2, 2, 2, 2], [4, 4, 4, 4, 4]])}
                      ]
    # fmt: on

    datasegments_equal(result, expected_result)


def test_process_segment_results_return_segment_index():
    num_segments = 3
    seg_length = 5

    input_data = pd.DataFrame(
        {
            "ax": combine([[x] * seg_length for x in range(num_segments)]) + ["0"],
            "ay": combine([[x**2] * seg_length for x in range(num_segments)]) + ["0"],
            "label": ["A"] * seg_length * num_segments + ["0"],
            "metadata_1": ["B"] * seg_length * num_segments + ["0"],
        }
    )

    seg_beg_end_list = [
        [seg_length * i, seg_length + seg_length * i - 1] for i in range(num_segments)
    ]
    group_columns = ["label", "metadata_1"]

    result = process_segment_results(
        input_data, seg_beg_end_list, group_columns, return_segment_index=True
    )

    # fmt: off
    expected_result = [{'columns': ['ax', 'ay'], 'metadata': {'label': 'A', 'metadata_1': 'B', 'SegmentID': 0, 'Seg_Begin': 0, 'Seg_End': 4}, 'statistics': {}, 'data': None},
                       {'columns': ['ax', 'ay'], 'metadata': {'label': 'A', 'metadata_1': 'B', 'SegmentID': 1, 'Seg_Begin': 5, 'Seg_End': 9}, 'statistics': {}, 'data': None},
                       {'columns': ['ax', 'ay'], 'metadata': {'label': 'A', 'metadata_1': 'B', 'SegmentID': 2, 'Seg_Begin': 10, 'Seg_End': 14}, 'statistics': {}, 'data': None}
                      ]
    # fmt: on

    datasegments_equal(result, expected_result)
