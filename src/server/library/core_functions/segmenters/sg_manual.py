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

from typing import List

from datamanager.datasegments import template_datasegment
from pandas import DataFrame


def sg_manual(
    input_data: DataFrame,
    group_columns: List[str],
    window_size: int = 1024,
    return_segment_index: bool = False,
):
    """
    This Segmenter uses the labels directly from your data set for training.

    You should use this if

    * you are testing out models and want to have very accurate labeling
    * have not decided on how you will segment your data
    * you are going to implement your own segmentation algorithm

    Note: This function expects you to implement your own segmentation algorithm in the firmware.
    that matches the types of segments you are creating.

    Model firmware defaults to a sliding window of max window size.

    Args:
        window_size (int) The the total size of the ring buffer in the firmware.
        return_segment_index (bool, optional): Defaults to False.
    """

    new_segments = []
    for index, segment in enumerate(input_data):

        tmp_segment = template_datasegment(segment)

        if return_segment_index:
            tmp_segment["metadata"]["Seg_Begin"] = 0
            tmp_segment["metadata"]["Seg_End"] = segment["data"].shape[0]
        else:
            tmp_segment["data"] = segment["data"]
        tmp_segment["metadata"]["SegmentID"] = index

        new_segments.append(tmp_segment)

    return new_segments


sg_manual_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "window_size",
            "type": "int",
            "default": 1024,
            "c_param": 0,
            "range": [1, 32726],
            "description": "The max data that can be passed into this function. This will determine the size of the buffer on the device",
            "display_name": "Max Window Size",
        },
        {
            "name": "return_segment_index",
            "type": "boolean",
            "default": False,
            "no_display": True,
            "description": "Append columns start and stop of the segment index.",
        },
    ],
    "output_contract": [
        {"name": "output_data", "type": "DataFrame", "metadata_columns": ["SegmentID"]}
    ],
}
