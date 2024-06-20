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

from sensiml.datamanager.label import Label, LabelSet
from sensiml.datamanager.label_relationship import Segment
from sensiml.datamanager.labelvalue import LabelValue, LabelValueSet
from sensiml.datamanager.metadata import Metadata, MetadataSet
from sensiml.datamanager.metadata_relationship import MetadataRelationship
from sensiml.datamanager.metadata_value import MetadataValue, MetadataValueSet
from sensiml.datamanager.segmenter import SegmenterSet
from sensiml.dclproj import DCLProject

color_list = [
    "#FF1D7DC4",
    "#FF58D963",
    "#FFF49534",
    "#FF7754AB",
    "#FFD14D49",
    "#FFC8CF4E",
    "#FF70A0B5",
    "#FF13631A",
    "#FF319476",
    "#FFB570AC",
    "#FF707070",
    "#FF421609",
    "#FF132AD4",
    "#FFC7AD1C",
    "#FFD47400",
    "#FF330C4A",
    "#FF00A2FF",
]


def upload_project(client, name: str, dclproj_path: str):
    if name in client.list_projects()["Name"].values:
        print("Project with this name already exists.")
        return

    client.project = name
    basedir = os.path.dirname(dclproj_path)
    capture_dir = os.path.join(basedir, "data")
    dclproj = DCLProject(path=dclproj_path)

    # TODO: plugin config
    # plugin_config = dclproj.get("ProjectCapturePluginConfig", None)
    # if plugin_config is not None:
    #    client.project.plugin_config = plugin_config
    #    print("Capture Config Found, Updating...")
    #    client.project.update()

    session_set = {}
    for _, session in dclproj.list_sessions().iterrows():
        if session["parameters"]:
            params = json.loads(session["parameters"])
            call = client.functions.create_function_call(params["name"])
            for k, v in params["inputs"].items():
                setattr(call, k, v)
        else:
            call = None

        new_segmenter = client.project.add_segmenter(
            session["name"],
            call,
            preprocess=session["preprocess"],
            custom=True if session["parameters"] else False,
        )
        session_set[session["id"]] = new_segmenter

    label_set = {}

    for _, item in dclproj._list_table_raw("Label").iterrows():
        if item["metadata"] == 0:
            label = Label(client._connection, client.project)
            label.name = item["name"]
            label.is_dropdown = True if item["is_dropdown"] else False
            label.insert()
            label_set[item.id] = label
        else:
            metadata = Metadata(client._connection, client.project)
            metadata.name = item["name"]
            metadata.is_dropdown = True if item["is_dropdown"] else False
            metadata.insert()
            label_set[item.id] = metadata

    label_value_set = {}

    for _, item in dclproj._list_table_raw("LabelValue").iterrows():
        if label_set[item["label"]].metadata == False:
            label_value = LabelValue(
                client._connection, client.project, label_set[item["label"]]
            )
            label_value.color = item["color"]
            label_value.value = item["value"]
            label_value.insert()
            label_value_set[item.id] = label_value
        else:
            metadata_value = MetadataValue(
                client._connection, client.project, label_set[item["label"]]
            )
            metadata_value.color = None
            metadata_value.value = item["value"]
            metadata_value.insert()
            label_value_set[item.id] = metadata_value

    for _, capture in dclproj.list_captures().iterrows():
        print(f"Uploading Capture data, metadata, and labels for {capture['name']}")

        capture_obj = client.project.captures.create_capture(
            os.path.basename(capture["name"]),
            os.path.join(capture_dir, capture["name"]),
        )

        # TODO: Bulk metadata creation
        for _, metadata_relationship in dclproj.get_capture_metadata(
            capture["name"], include_ids=True
        ).iterrows():
            metadata_value = label_value_set[metadata_relationship["label_value_id"]]
            metadata = label_set[metadata_relationship["label_id"]]
            metadata_relationship_obj = MetadataRelationship(
                client._connection,
                client.project,
                capture_obj,
                metadata,
                metadata_value,
            )
            metadata_relationship_obj.insert()

        # TODO: Bulk label creation
        for _, label_relationship in dclproj.list_capture_segments(
            capture["name"], include_ids=True
        ).iterrows():
            label_value = label_value_set[label_relationship["label_value_id"]]
            label = label_set[label_relationship["label_id"]]

            if not session_set.get(label_relationship["segmenter_id"], None):
                continue

            segmenter = session_set[label_relationship["segmenter_id"]]["id"]
            label_relationship_obj = Segment(
                client._connection,
                client.project,
                capture_obj,
                segmenter,
                label,
                label_value,
            )

            if (
                label_relationship["capture_sample_sequence_start"] < 0
                or label_relationship["capture_sample_sequence_end"]
                <= label_relationship["capture_sample_sequence_start"]
            ):
                print("Invalid Segment: Skipping")
                print(label_relationship)
                continue

            label_relationship_obj.sample_start = label_relationship[
                "capture_sample_sequence_start"
            ]
            label_relationship_obj.sample_end = label_relationship[
                "capture_sample_sequence_end"
            ]
            label_relationship_obj.insert()


def upload_project_dcli(client, name: str, dcli_path: str):
    client.project = name
    basedir = os.path.dirname(dcli_path)
    capture_dir = os.path.join(basedir)

    dcli = json.load(open(dcli_path, "r"))

    session_set = SegmenterSet(client._connection, client.project).to_dict()
    label_set = {}
    label_value_set = {}
    metadata_set = MetadataSet(client._connection, client.project).to_dict()
    metadata_value_set = {}
    for key, metadata in metadata_set.items():
        metadata_value_set[key] = MetadataValueSet(
            client._connection, client.project, metadata
        ).to_dict()

    label_set = LabelSet(client._connection, client.project).to_dict()
    label_value_set = {}
    for key, label in label_set.items():
        label_value_set[key] = LabelValueSet(
            client._connection, client.project, label
        ).to_dict()

    color_index = {}
    for index, capture_info in enumerate(dcli):
        if not os.path.exists(os.path.join(capture_dir, capture_info["file_name"])):
            print(f"Skipping: Capture {capture_info['file_name']} not found.")
            continue

        print(f"Uploading Capture {index}/{len(dcli)}: {capture_info['file_name']}")

        try:
            capture_obj = client.project.captures.get_or_create(
                os.path.basename(capture_info["file_name"]),
                os.path.join(capture_dir, capture_info["file_name"]),
            )
        except Exception as e:
            print(e)
            continue

        if capture_info.get("metadata"):
            for metadata in capture_info["metadata"]:
                if not metadata["value"]:
                    continue

                metadata_obj = metadata_set.get(metadata["name"])

                if metadata_obj is None:
                    metadata_obj = Metadata(client._connection, client.project)
                    metadata_obj.name = metadata["name"]
                    metadata_obj.is_dropdown = True  # TODO check dcli if metadata_obj["is_dropdown"] else False
                    metadata_obj.insert()
                    metadata_set[metadata_obj.name] = metadata_obj
                    metadata_set[metadata_obj.name] = {}
                    metadata_set = MetadataSet(
                        client._connection, client.project
                    ).to_dict()
                    metadata_value_set[metadata_obj.name] = {}

                metadata_value_obj = metadata_value_set[metadata_obj.name].get(
                    metadata["value"]
                )

                if metadata_value_obj is None:
                    metadata_value_obj = MetadataValue(
                        client._connection, client.project, metadata_obj
                    )
                    metadata_value_obj.color = None
                    metadata_value_obj.value = metadata["value"]
                    metadata_value_obj.insert()

                    metadata_value_set[metadata_obj.name][
                        metadata_value_obj.value
                    ] = metadata_value_obj

                metadata_relationship_obj = MetadataRelationship(
                    client._connection,
                    client.project,
                    capture_obj,
                    metadata_obj,
                    metadata_value_obj,
                )
                metadata_relationship_obj.insert()

        if capture_info.get("sessions"):
            for session in capture_info["sessions"]:
                # TODO: Params
                # params = json.loads(session["parameters"])
                # call = client.functions.create_function_call(params["name"])
                # for k, v in params["inputs"].items():
                #    setattr(call, k, v)
                # else:
                # call = None

                if session["session_name"] not in session_set:
                    new_segmenter = client.project.add_segmenter(
                        session["session_name"],
                        segmenter=None,
                        preprocess=None,
                        custom=True,  # True if session["parameters"] else False,
                    )
                    session_set = SegmenterSet(
                        client._connection, client.project
                    ).to_dict()

                session_obj = session_set[session["session_name"]]

                for segment in session["segments"]:
                    label_obj = label_set.get(segment["name"])

                    if label_obj is None:
                        label_obj = Label(client._connection, client.project)
                        label_obj.name = segment["name"]
                        label_obj.is_dropdown = True
                        label_obj.insert()
                        label_set = LabelSet(
                            client._connection, client.project
                        ).to_dict()
                        label_value_set[label_obj.name] = {}
                        color_index[label_obj.name] = 0

                    if color_index.get(label_obj.name) is None:
                        color_index[label_obj.name] = 0

                    label_value_obj = label_value_set[label_obj.name].get(
                        segment["value"]
                    )
                    if label_value_obj is None:
                        label_value_obj = LabelValue(
                            client._connection, client.project, label_obj
                        )
                        # label_value_obj.color = segment["color"]
                        label_value_obj.value = segment["value"]

                        if color_index[label_obj.name] >= len(color_list):
                            color_index[label_obj.name] = 0

                        label_value_obj.color = color_list[color_index[label_obj.name]]
                        color_index[label_obj.name] += 1

                        label_value_obj.insert()

                        label_value_set[label_obj.name][
                            label_value_obj.value
                        ] = label_value_obj

                    label_relationship_obj = Segment(
                        client._connection,
                        client.project,
                        capture_obj,
                        session_obj.uuid,
                        label_obj,
                        label_value_obj,
                    )

                    if segment["end"] > capture_obj.capture_info["max_sequence"]:
                        segment["end"] = capture_obj.capture_info["max_sequence"]

                    if segment["start"] < 0:
                        segment["start"] = 0

                    label_relationship_obj.sample_start = segment["start"]
                    label_relationship_obj.sample_end = segment["end"]
                    try:
                        label_relationship_obj.insert()
                    except Exception as e:
                        print(e)
