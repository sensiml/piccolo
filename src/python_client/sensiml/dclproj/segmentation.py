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

from sensiml.dclproj import DataSegment, DataSegments


def sliding_window(
    input_data: DataSegments, window_size: int, delta: int, label: str = "Unknown"
) -> DataSegments:
    """Returns the sliding window of datasegments across all datasegments in the input_data

    Args:
        input_data (DataSegments): Datasegments to apply the sliding window too
        window_size (int): size of the sliding window
        delta (int): slide of the sliding window
        label (str, optional): Default label to use when creating new segments if None exists. Defaults to "Unknown".

    Returns:
        DataSegments
    """
    new_segments = []
    for segment in input_data:
        for segment_id, start_index in enumerate(
            range(0, segment.data.shape[1] - window_size, delta)
        ):
            tmp_segment = DataSegment(
                segment_id=segment_id,
                columns=segment.columns,
                capture_sample_sequence_start=start_index,
                capture_sample_sequence_end=start_index + window_size,
                label_value=segment.label_value if segment.label_value else label,
            )

            tmp_segment._data = segment.data[:, start_index : start_index + window_size]

            new_segments.append(tmp_segment)

    return DataSegments(new_segments)
