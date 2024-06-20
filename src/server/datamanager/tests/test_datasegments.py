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
    DataSegments,
    dataframe_to_datasegments,
)
from pandas import DataFrame


def test_dataframe_to_datasegments():
    length = 5
    data = DataFrame(
        {"X": [1] * length, "Y": [-1] * length, "segment_uuid": [1] * length},
        columns=["X", "Y", "segment_uuid"],
    )

    segments = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["segment_uuid"]
    )

    data = DataFrame(
        {
            "X": [1] * length,
            "Y": [-1] * length,
            "segment_uuid": [1] * length,
            "capture_uuid": ["red"] * length,
        },
        columns=["X", "Y", "segment_uuid", "capture_uuid"],
    )

    segments = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["segment_uuid", "capture_uuid"]
    )

    result = DataSegments(segments).summary()

    expected_result = {
        "total_segments": 1,
        "total_samples": 5,
        "distribution_segments": {"Label": 1},
        "distribution_samples": {"Label": 5},
    }
    assert expected_result == result


def test_datasegments_iter_dataframe():
    num_segments = 2
    segment_length = 5
    length = segment_length * num_segments

    data = DataFrame(
        {
            "X": [1] * length,
            "Y": [-1] * length,
            "segment_uuid": [1] * length,
            "capture_uuid": ["red"] * segment_length + ["blue"] * segment_length,
        },
        columns=["X", "Y", "segment_uuid", "capture_uuid"],
    )

    segments = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["segment_uuid", "capture_uuid"]
    )
    datasegments = DataSegments(segments)

    for segment in datasegments.iter_dataframe():
        assert isinstance(segment, DataFrame)

    assert len(datasegments) == 2


def test_datasegment_summary_no_data():
    # fmt: off
    datasegments = DataSegments([{'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 0, 'Seg_End': 250, 'SegmentID': 0}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 250, 'Seg_End': 500, 'SegmentID': 1}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 500, 'Seg_End': 750, 'SegmentID': 2}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 750, 'Seg_End': 1000, 'SegmentID': 3}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 1000, 'Seg_End': 1250, 'SegmentID': 4}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 1250, 'Seg_End': 1500, 'SegmentID': 5}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 1500, 'Seg_End': 1750, 'SegmentID': 6}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 1750, 'Seg_End': 2000, 'SegmentID': 7}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 2000, 'Seg_End': 2250, 'SegmentID': 8}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 2250, 'Seg_End': 2500, 'SegmentID': 9}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 2500, 'Seg_End': 2750, 'SegmentID': 10}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 2750, 'Seg_End': 3000, 'SegmentID': 11}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 3000, 'Seg_End': 3250, 'SegmentID': 12}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 3250, 'Seg_End': 3500, 'SegmentID': 13}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 3500, 'Seg_End': 3750, 'SegmentID': 14}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 3750, 'Seg_End': 4000, 'SegmentID': 15}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 4000, 'Seg_End': 4250, 'SegmentID': 16}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 4250, 'Seg_End': 4500, 'SegmentID': 17}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 4500, 'Seg_End': 4750, 'SegmentID': 18}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 4750, 'Seg_End': 5000, 'SegmentID': 19}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 5000, 'Seg_End': 5250, 'SegmentID': 20}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 5250, 'Seg_End': 5500, 'SegmentID': 21}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 5500, 'Seg_End': 5750, 'SegmentID': 22}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 5750, 'Seg_End': 6000, 'SegmentID': 23}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 6000, 'Seg_End': 6250, 'SegmentID': 24}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 6250, 'Seg_End': 6500, 'SegmentID': 25}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 6500, 'Seg_End': 6750, 'SegmentID': 26}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 6750, 'Seg_End': 7000, 'SegmentID': 27}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 7000, 'Seg_End': 7250, 'SegmentID': 28}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 7250, 'Seg_End': 7500, 'SegmentID': 29}, 'statistics': {}, 'data': None}, {'columns': ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'Magnitude_ST_0000', 'Magnitude_ST_0001'], 'metadata': {'Class': 0, 'Subject': 0, 'Seg_Begin': 7500, 'Seg_End': 7750, 'SegmentID': 30}, 'statistics': {}, 'data': None}])
    # fmt: on
    result = datasegments.summary()

    expected_result = {
        "total_segments": 31,
        "total_samples": 0,
        "distribution_segments": {"Label": 31},
        "distribution_samples": {},
    }
    assert expected_result == result
