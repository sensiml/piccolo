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

from typing import Optional
import numpy as np
from sensiml.dclproj import DataSegment, DataSegments
from pandas import DataFrame


def import_model_results(
    results: DataFrame,
    data: Optional[np.array] = None,
    capture_name: Optional[str] = None,
    session: Optional[str] = None,
):
    datasegments = DataSegments()
    for index, result in enumerate(results.to_dict(orient="records")):
        if result["capture_sample_sequence_start"] < 0:
            print("Filtering: capture_sample_sequence_start must be > 0", result)
            continue
        if (
            result["capture_sample_sequence_start"]
            > result["capture_sample_sequence_end"]
        ):
            print(
                "Filtering: capture_sample_sequence_start must be < capture_sample_sequence_end",
                result,
            )

        if data is None:
            datasegments.append(
                DataSegment(
                    segment_id=index,
                    data=None,
                    session=session,
                    capture=capture_name,
                    **result,
                )
            )
        else:
            datasegments.append(
                DataSegment(
                    segment_id=index,
                    columns=data.columns.to_list(),
                    data=data.values[
                        result["capture_sample_sequence_start"] : result[
                            "capture_sample_sequence_end"
                        ]
                    ].T,
                    session=session,
                    capture=capture_name,
                    **result,
                )
            )

    return datasegments


def import_segment_list(
    labels: DataFrame, session: str = "", dcl: Optional[object] = None
):
    """Converts a DataFrame of segments into a DataSegments object

    Args:
        labels (DataFrame): A dataframe containing the segment information
        session (str, optional): The session to set the segments too. Defaults to "".
        dcl (DCLProject): A DCLProject object that is connected to the DCLI file, If this is passed in the data property of the DataSegment objects will be filled with sensor data

    Returns:
        DataSegments
    """

    if isinstance(labels, DataFrame):
        # DCL generates segments with this format ""
        if labels.columns.to_list() == [
            "File",
            "Label",
            "Start",
            "End",
            "Length",
        ]:
            label_dict = (
                labels.rename(
                    columns={
                        "File": "capture",
                        "Label": "label_value",
                        "Start": "capture_sample_sequence_start",
                        "End": "capture_sample_sequence_end",
                    },
                )
                .sort_values(by="capture")
                .to_dict(orient="records")
            )
        elif "Seg_Begin" in labels.columns.to_list():
            if "capture" not in labels.columns:
                labels["capture"] = None
            if "label_value" not in labels.columns:
                labels["label_value"] = None
            label_dict = (
                labels.rename(
                    columns={
                        "Seg_Begin": "capture_sample_sequence_start",
                        "Seg_End": "capture_sample_sequence_end",
                    },
                )
                .sort_values(by="SegmentID")
                .to_dict(orient="records")
            )
        else:
            if "segmenter" in labels.columns.tolist():
                labels.rename({"segmenter": "session"}, axis=1, inplace=True)
            label_dict = labels.sort_values(
                by=["capture", "session", "capture_sample_sequence_start"]
            ).to_dict(orient="records")
    else:
        raise Exception("Expected DataFrame")

    data_segments = DataSegments()
    capture_name = None
    columns = None
    data = None
    capture = None

    for index, label in enumerate(label_dict):

        if capture_name != label["capture"]:
            if dcl:
                capture = dcl.get_capture(label["capture"])
            else:
                capture = None
            capture_name = label["capture"]

        if capture:
            data = capture.iloc[
                label["capture_sample_sequence_start"] : label[
                    "capture_sample_sequence_end"
                ]
            ].values.T
            columns = capture.columns.values.tolist()
        else:
            data = None
            columns = None

        data_segments.append(
            DataSegment(
                segment_id=index,
                capture_sample_sequence_start=label["capture_sample_sequence_start"],
                capture_sample_sequence_end=label["capture_sample_sequence_end"],
                data=data,
                columns=columns,
                session=label.get("session", session),
                label_value=label["label_value"],
                capture=label["capture"],
            )
        )

    return data_segments


def import_audacity(capture_name, file_path: str, session: str = "", rate: int = 16000):
    """Converts labels exported from Audacity into a datasegment object.

    Args:
        capture_name (str): The name of the capture file to import
        file_path (DataFrame): The file path to the Audacity Label
        session (str, optional): The session to set the segments too. Defaults to "".
        rate (int): Audacity uses the actual time and note number of samples. Set the rate to the sample rate for the captured date. Default is 16000.
        data (DataFrame): The data associated with the audacity labels


    Returns:
        Datasegments
    """

    M = []
    with open(file_path, "r") as fid:
        for line in fid.readlines():
            if line[0] == "\\":
                continue
            start, end, label = line[:-1].split("\t")
            M.append([float(start), float(end), label])

    segment_list = DataFrame(
        M,
        columns=[
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "label_value",
        ],
    )

    segment_list["capture_sample_sequence_start"] = (
        segment_list["capture_sample_sequence_start"] * rate
    ).astype(int)
    segment_list["capture_sample_sequence_end"] = (
        segment_list["capture_sample_sequence_end"] * rate
    ).astype(int)

    segment_list["capture"] = capture_name
    segment_list["session"] = session

    return import_segment_list(segment_list)


def import_timeseries(timeseries, y, session="Training Session"):
    data_segments = DataSegments()
    groups = timeseries.groupby("id")
    for index, key in enumerate(groups.groups.keys()):
        data_segments.append(
            DataSegment(
                segment_id=index,
                columns=timeseries.columns.to_list(),
                data=timeseries.values.T,
                session=session,
                capture=f"{index}.csv",
                label_value=y.loc[index],
            )
        )

    return data_segments
