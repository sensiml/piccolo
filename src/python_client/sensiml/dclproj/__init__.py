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

import json

import numpy as np

from sensiml.dclproj.confusion_matrix import ConfusionMatrix
from sensiml.dclproj.csv_to_dcli import to_dcli
from sensiml.dclproj.datasegments import DataSegment, DataSegments
from sensiml.dclproj.dclproj import DCLProject
from sensiml.dclproj.loaders import import_audacity, import_segment_list
from sensiml.dclproj.vizualization import plot_threshold_space

__all__ = [
    "DCLProject",
    "to_dcli",
    "import_segment_list",
    "import_audacity",
    "DataSegment",
    "DataSegments",
    "ConfusionMatrix",
    "plot_threshold_space",
]


def dict_to_datasegments(input_dict: dict, dtype=np.float32):
    columns = list(input_dict.keys())

    data = np.vstack(
        [np.array(input_dict[column], dtype=dtype).T for column in columns]
    )

    return DataSegments(
        [
            DataSegment(
                data=data,
                columns=columns,
                segment_id=0,
                capture_sample_sequence_start=0,
                capture_sample_sequence_end=data.shape[1] - 1,
            )
        ]
    )


def convert_to_datasegments(data: dict, dtype=np.float32) -> DataSegments:

    converted_data = {}
    for k, v in dict(data).items():
        if not k:
            continue
        converted_data[k] = [float(item) for item in v]

    return dict_to_datasegments(converted_data, dtype=dtype)


def to_data_studio_dataseries(name, data, time=None):

    if time is None:
        time = list(range(len(data)))

    if len(time) != len(data):
        raise Exception(
            f"Time and Data are not the same length {len(time)} {len(data)}"
        )

    return {name: (time, data.tolist())}


def validate_params(input_contract, params: dict) -> bool:

    params = json.loads(params)

    for ic_param in input_contract:
        if ic_param["name"] not in params:
            raise Exception(f"param {ic_param['name']} is required")

    return params


def convert_dataseries(data: dict, dtype=np.float32) -> DataSegments:

    converted_data = {}
    for k, v in dict(data).items():
        if not k:
            continue
        converted_data[k] = {
            "X": [float(item) for item in v[0]],
            "Y": [float(item) for item in v[1]],
        }

    return converted_data


def to_data_studio_labels(datasegments: DataSegments):

    result = []
    for datasegment in datasegments:
        tmp = {
            "SegmentStart": datasegment.start,
            "SegmentEnd": datasegment.end,
            "ClassificationName": datasegment.label_value,
        }

        result.append(tmp)

    return result
