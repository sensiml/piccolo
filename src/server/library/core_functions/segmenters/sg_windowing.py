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
from library.exceptions import InputParameterException
from pandas import DataFrame


def sg_windowing(
    input_data: DataFrame,
    group_columns: List[str],
    window_size: int,
    delta: int,
    enable_train_delta: bool = False,
    train_delta: int = 0,
    return_segment_index: bool = False,
):
    """

    Args:
        window_size (int): The size of the window
        delta (int): The slide of the window
        enable_train_delta (bool): Enable or disable the train delta parameter
        train_delta (int, optional): Use this delta for sliding during training.
        return_segment_index (bool, optional): _description_. Defaults to False.
    """

    def validate_delta(delta, window_size):
        if delta > window_size:
            raise InputParameterException("Delta cannot be larger than the window size")

        if delta <= 0:
            raise InputParameterException("Delta cannot be less than or equal to 0")

        if delta <= window_size * 0.25:
            raise InputParameterException(
                "Delta cannot be less than 25% of window_size"
            )

    validate_delta(delta, window_size)

    if enable_train_delta:
        validate_delta(train_delta, window_size)
        delta = int(train_delta)

    new_segments = []
    for segment in input_data:
        for SegmentID, start_index in enumerate(
            range(0, segment["data"].shape[1] - (window_size - 1), delta)
        ):
            tmp_segment = template_datasegment(segment)

            if return_segment_index:
                tmp_segment["metadata"]["Seg_Begin"] = start_index
                tmp_segment["metadata"]["Seg_End"] = start_index + window_size
            else:
                tmp_segment["data"] = segment["data"][
                    :, start_index : start_index + window_size
                ]
            tmp_segment["metadata"]["SegmentID"] = SegmentID

            new_segments.append(tmp_segment)

    return new_segments


sg_windowing_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list", "element_type": "str"},
        {
            "name": "window_size",
            "type": "int",
            "default": 250,
            "c_param": 1,
            "range": [1, 16384],
            "description": "The amount of data that will be used to classify the current signal.",
            "display_name": "Window Size",
        },
        {
            "name": "delta",
            "type": "int",
            "default": 250,
            "c_param": 2,
            "range": [1, 16384],
            "description": "The amount of overlap between this signal and the next. For example if the Window Size is 250 and the slide is 50, the next classification will add 50 new samples to the last 200 samples from the previous window. If Slide is equal to Window Size there will be no overlap.",
            "display_name": "Slide",
        },
        {
            "name": "enable_train_delta",
            "type": "bool",
            "default": False,
            "description": "Enable or disable the training slide",
            "display_name": "Use Training Slide",
        },
        {
            "name": "train_delta",
            "type": "int",
            "default": 125,
            "range": [1, 16384],
            "description": "The Training Slide will replace the Slide setting during training, but the Slide will be used when generating the Knowledge Pack. Train slide is useful for data augmentation.",
            "display_name": "Training Slide",
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
