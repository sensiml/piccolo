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

import gzip
import pickle
from collections import defaultdict
from copy import deepcopy
from typing import Optional

import numpy as np
from pandas import DataFrame, concat


class DataSegment(object):
    def __init__(
        self,
        data: np.array,
        columns: list,
        segment_id: int,
        session: Optional[str] = None,
        label_value: Optional[str] = None,
        uuid: Optional[str] = None,
        capture: Optional[str] = None,
        extra_metadata: Optional[dict] = None,
    ):
        self._metadata = [
            "label_value",
            "capture",
            "segment_id",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "columns",
            "session",
            "uuid",
        ]
        self._label_value = str(label_value)
        self._session = session
        self._segment_id = segment_id
        self._uuid = uuid
        self._capture = capture
        self._data = data
        self._columns = columns
        self._extra_metadata = extra_metadata

    @property
    def size(self):
        return self._data.shape[0]


class DataSegments(object):
    def __init__(self, data):
        self._data = data

    def __len__(self):
        return len(self._data)

    @property
    def only_metadata(self):
        if self._data[0].get("data") is None:
            return True

        return False

    def to_dataframe(self):
        M = []

        if not self._data:
            return None

        if self.only_metadata:
            for segment in self._data:
                M.append(segment["metadata"])

            return DataFrame(M)

        for segment in self._data:
            tmp_df = DataFrame(segment["data"].T, columns=segment["columns"])
            M.append(tmp_df.assign(**segment["metadata"]))

        return concat(M).reset_index(drop=True)

    def apply(self, func, **kwargs):
        feature_vectors = []
        for segment in self._data:
            if sum([x == 0 for x in segment["data"].shape]) == 0:
                tmp_df = func(segment, **kwargs)
                feature_vectors.append(tmp_df.assign(**segment["metadata"]))

        return concat(feature_vectors).reset_index(drop=True)

    def iter_dataframe(self):
        if self.only_metadata:
            for segment in self._data:
                yield DataFrame([segment["metadata"]])
        else:
            for segment in self._data:
                tmp_df = DataFrame(segment["data"].T, columns=segment["columns"])

                yield tmp_df.assign(**segment["metadata"])

    def summary(self):
        distribution_segments = defaultdict(int)
        total_samples = 0
        distribution_samples = defaultdict(int)
        for data_segment in self._data:
            distribution_segments[
                str(data_segment.get("metadata", dict()).get("Label", "Label"))
            ] += 1
            if data_segment["data"] is not None:
                distribution_samples[
                    str(data_segment.get("metadata", dict()).get("Label", "Label"))
                ] += data_segment["data"].shape[1]
                total_samples += data_segment["data"].shape[1]

        return {
            "total_segments": len(self._data),
            "total_samples": total_samples,
            "distribution_segments": dict(distribution_segments),
            "distribution_samples": dict(distribution_samples),
        }


def dataframe_to_datasegments(input_data, data_columns, group_columns, dtype=np.int32):
    groups = input_data.groupby(group_columns)

    M = []
    if sorted(data_columns) != sorted(
        [x for x in input_data.columns if x not in group_columns]
    ):
        raise Exception(
            "data columns [{data_columns}] and group columns [{group_columns}] do not match the input_data columns [{input_columns}]".format(
                data_columns=data_columns,
                group_columns=group_columns,
                input_columns=input_data.columns,
            )
        )

    for key, tmp_df in groups:
        tmp_seg = {}
        tmp_seg["data"] = tmp_df[data_columns].values.astype(dtype).T
        tmp_seg["columns"] = data_columns
        tmp_seg["metadata"] = {
            k: v
            for k, v in zip(group_columns, key if isinstance(key, tuple) else [key])
        }

        M.append(tmp_seg)

    return M


def dict_to_datasegments(input_dict: dict, dtype=np.int32):
    columns = list(input_dict.keys())

    data = np.concatenate(
        [np.array(input_dict[column], dtype=dtype).T for column in columns]
    )

    return DataSegments(DataSegment(data=data, columns=columns, segment_id=0))


def template_datasegment(segment):
    return {
        "columns": deepcopy(segment["columns"]),
        "metadata": deepcopy(segment["metadata"]),
        "statistics": {},
        "data": None,
    }


def generate_segment_template():
    return {"columns": None, "metadata": {}, "statistics": {}, "data": None}


def load_datasegments(path):
    with gzip.open(path, "rb") as fid:
        data = pickle.load(fid)

    return data


def datasegments_equal(a1, a2):
    for index, seg in enumerate(a1):
        assert np.array_equal(seg["data"], a2[index]["data"])
        assert seg["metadata"] == a2[index]["metadata"]
        assert seg["columns"] == a2[index]["columns"]

    return True


def get_datasegments_num_cols(datasegments):
    return len(datasegments[0]["columns"])


def get_datasegments_columns(datasegments):
    return datasegments[0]["columns"]


def get_datasegment_col_indexes(datasegments, column_names):
    if isinstance(datasegments, list):
        return [datasegments[0]["columns"].index(col) for col in column_names]

    if isinstance(datasegments, dict):
        return [datasegments["columns"].index(col) for col in column_names]


def get_dataframe_datatype(data):
    for column in data.columns:
        if data[column].dtype == "float64":
            return np.float32

    return np.int32


def is_datasegments(data):
    if (
        data
        and isinstance(data, list)
        and (
            isinstance(data[0], DataSegment)
            or (
                isinstance(data[0], dict)
                and "metadata" in data[0]
                and "data" in data[0]
            )
        )
    ):
        return True

    return False
