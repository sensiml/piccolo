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
import os


def find_change_index(y, label):
    for index, i in enumerate(y):
        if i != label:
            return index

    return len(y)


def to_dcli(
    df,
    label_column,
    filename,
    session_name=None,
    outdir="dcli_export",
    sensor_columns=None,
    video_name=None,
    metadata=None,
    exclude_labels=None,
    export_dcli=True,
    export_csv=True,
    dcli_name="export.dcli",
    verbose=True,
):
    """
    This is used to convert a CSV file into a dcli file that can be imported into the DCL

    The expected format of a CSV file for this converter is a CSV containing all of the
    sensor data as well as a column that specifies which label each row corresponds to

    Sensor1,Sensor2,...SensorN,Label
    13,134,...,146,Running
    42,124,...,123,Running
    13,342,...,124,Running
    12,134,...,123,Running
    15,121,...,124,Walking
    19,134,...,134,Walking
    .
    .
    .
    19,134,...,134,Walking


    args:
     df (dataframe)
     label_column: the label column to use for adding segments
     filename: the name of the file
     session_name: The session name to use when creating the session for import
     outdir: the directory to write the exported data to
     sensor_columns (list): the column in the DataFrame that are sensor columns, if None use all columns except the label column
     video_name (str): path to the video associated with this file
     metadata (list): metadata already formatted in the dcli format
     exclude_labels (list): labels to exclude when creating this file
     export_dcli (bool): creates the dcli file in the outdir folder
     export_csv (bool): copies the dataframe of sensor data to the the outdir folder
     dcli_name (str): name of the .dcli file to create

    """
    start = 0
    end = 0
    segments = []
    labels = df[label_column].tolist()
    while end < len(labels):
        current_label = labels[end]
        start = labels[end:].index(current_label) + end
        end = find_change_index(labels[start:], current_label) + start

        if start < 0:
            seg_start = 0
        else:
            seg_start = start

        if end > len(labels):
            seg_end = len(labels) - 1
        else:
            seg_end = end - 1

        if exclude_labels and current_label in exclude_labels:
            continue

        segments.append(
            {
                "name": "Label",
                "value": current_label,
                "start": seg_start,
                "end": seg_end,
            }
        )

    if verbose:
        print("Number of segments found", len(segments))
        print("Type of segments found", df[label_column].unique())

    if dcli_name is None:
        dcli_name = "export.dcli"

    if outdir is not None:
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        file_path = os.path.join(outdir, filename)
        dcli_path = os.path.join(outdir, dcli_name)

    else:
        file_path = filename
        dcli_path = dcli_name

    if session_name is None:
        session_name = "Session1"

    dcli_capture = {
        "file_name": filename,
        "sessions": [{"session_name": session_name, "segments": segments}],
    }

    if video_name:
        dcli_capture.update({"videos": [{"video_path": video_name}]})

    if metadata:
        dcli_capture.update(metadata)

    if export_csv:
        if sensor_columns:
            df[sensor_columns].to_csv(file_path, index=None)
        else:
            df[[col for col in df.columns if col != label_column]].to_csv(
                file_path, index=None
            )
        if verbose:
            print(f"writing csv files to folder '{outdir}'")
    if export_dcli:
        json.dump([dcli_capture], open(dcli_path, "w"))
        if verbose:
            print(f"writing dcli files to folder '{outdir}'")

    return dcli_capture
