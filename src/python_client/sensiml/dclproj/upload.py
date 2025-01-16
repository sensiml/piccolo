import os
from concurrent.futures import ThreadPoolExecutor
import time
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

import os
from concurrent.futures import ThreadPoolExecutor
import time
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


from more_itertools import chunked


def bulk_upload_label_relationship_set(client, label_relationship_set, batch_size=250):

    def serialize_relationship_set(lrs):
        result = {}
        for lr in lrs:
            tmp = lr._to_representation()
            tmp["capture"] = lr._capture.capture_info["uuid"]
            segmenter = str(tmp.pop("segmenter"))
            if not result.get(segmenter):
                result[segmenter] = []
            result[segmenter].append(tmp)

        return result

    label_relationship_set_json = serialize_relationship_set(label_relationship_set)

    responses = []
    for segmenter in label_relationship_set_json.keys():
        url = f"v2/project/{client.project.uuid}/segmenter/{segmenter}/label-relationship/"
        data = label_relationship_set_json[segmenter]

        for batch in chunked(data, batch_size):
            response = client._connection.request("post", url, json=batch)
            responses.append(response.status_code)

    print("label_relationship", responses)


def bulk_upload_metadata_relationship_set(
    client, metadata_relationship_set, batch_size=50
):

    def serialize_relationship_set(relationship_set):
        result = []
        for relationship in relationship_set:
            tmp = relationship._to_representation()
            tmp["capture"] = relationship._capture.capture_info["uuid"]
            result.append(tmp)

        return result

    relationship_set_json = serialize_relationship_set(metadata_relationship_set)

    url = f"project/{client.project.uuid}/metadata-relationship/"

    responses = []
    for batch in chunked(relationship_set_json, batch_size):
        response = client._connection.request("post", url, json=batch)
        responses.append(response.status_code)

    print("metadata_relationship", responses)


def get_value_dict_from_data(data, label):
    for item in data["label_values"]:
        if item["value"] == label:
            return item


def get_relationship_data(label_dict, relationship):
    label = label_dict[relationship.label]

    label_value = get_value_dict_from_data(label.data, relationship.label_value)

    return {
        "label_value": label_value["uuid"],
        "label": label.uuid,
    }


def bulk_upload_metadata_relationship_set_server(
    client, dclproj, captures, batch_size=1000
):

    metadata = MetadataSet(client._connection, client.project)
    metadata_dict = metadata.to_dict()
    metadata_relationships = dclproj.get_capture_metadata(include_ids=True).groupby(
        ["capture"]
    )
    metadata_relationship_set = []
    for index, capture in captures.iterrows():
        if capture[0] not in metadata_relationships.groups.keys():
            continue
        for id, row in metadata_relationships.get_group(capture[0]).iterrows():
            print(row)
            tmp = get_relationship_data(metadata_dict, row)
            tmp["capture"] = capture.UUID
            metadata_relationship_set.append(tmp)

    url = f"project/{client.project.uuid}/metadata-relationship/"

    responses = []
    for batch in chunked(metadata_relationship_set, batch_size):
        response = client._connection.request("post", url, json=batch)
        responses.append(response.status_code)
        print(len(responses), responses[-1])

    print("metadata_relationship", responses)


def bulk_upload_label_relationship_set_server(
    client, dclproj, captures, batch_size=1000
):
    from collections import defaultdict

    segmenters = SegmenterSet(client._connection, client.project)
    segmenter_dict = segmenters.to_dict()
    label = LabelSet(client._connection, client.project)
    label_dict = label.to_dict()

    label_relationships = dclproj.list_capture_segments(include_ids=True).groupby(
        "capture"
    )

    label_relationship_set = defaultdict(list)
    for index, capture in captures.iterrows():
        if capture[0] not in label_relationships.groups.keys():
            continue

        for id, row in label_relationships.get_group(capture[0]).iterrows():
            tmp = get_relationship_data(label_dict, row)
            tmp["capture"] = capture.UUID

            tmp["capture_sample_sequence_start"] = row["capture_sample_sequence_start"]
            tmp["capture_sample_sequence_end"] = row["capture_sample_sequence_end"]

            if tmp["capture_sample_sequence_start"] < 0:
                tmp["capture_sample_sequence_start"] = 0
            """TODO: Check This
            if (
                tmp["capture_sample_sequence_end"]
                >= capture_obj.capture_info["max_sequence"]
            ):
                tmp["capture_sample_sequence_end"] = (
                    capture_obj.capture_info["max_sequence"] - 1
                )                
            """
            if (
                tmp["capture_sample_sequence_end"]
                <= tmp["capture_sample_sequence_start"]
            ):
                print("Invalid Segment: Skipping", id)
                continue

            label_relationship_set[segmenter_dict[row["segmenter"]].uuid].append(tmp)

    responses = []
    for segmenter in label_relationship_set.keys():
        url = f"v2/project/{client.project.uuid}/segmenter/{segmenter}/label-relationship/"
        data = label_relationship_set[segmenter]

        for batch in chunked(data, batch_size):
            response = client._connection.request("post", url, json=batch)
            responses.append(response.status_code)
            print(len(responses), responses[-1])

    print("label_relationship", responses)


def upload_capture(
    client,
    capture,
    capture_dir,
    index,
):
    start = time.time()
    print(f"Uploading Capture data for {capture['name']}")
    capture_obj = client.project.captures.create_capture(
        os.path.basename(capture["name"]),
        os.path.join(capture_dir, capture["name"]),
    )
    print(
        f"Finished Uploading Capture data for {capture['name']} - {index} in {time.time()-start}"
    )

    return capture_obj


def upload_project(
    client,
    name: str,
    dclproj_path: str,
    max_workers: int = 10,
    batch_size: int = 250,
    force_capture=False,
):

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

        try:
            new_segmenter = client.project.add_segmenter(
                session["name"],
                call,
                preprocess=session["preprocess"],
                custom=True if session["parameters"] else False,
            )

            session_set[session["id"]] = new_segmenter
        except Exception as e:
            print("session failed", e)

    label_set = {}

    print("Creating Project Metadata and Labels")
    for _, item in dclproj._list_table_raw("Label").iterrows():
        if item["metadata"] == 0:
            label = Label(client._connection, client.project)
            label.name = item["name"]
            label.is_dropdown = True if item["is_dropdown"] else False
            try:
                label.insert()
            except Exception as e:
                print("label insert failed", e)

            label_set[item.id] = label
        else:
            metadata = Metadata(client._connection, client.project)
            metadata.name = item["name"]
            metadata.is_dropdown = True if item["is_dropdown"] else False
            try:
                metadata.insert()
            except Exception as e:
                print("Metadata insert failed", e)
            label_set[item.id] = metadata

    label_value_set = {}

    # Resync of Metadata and Labels before adding label values and metadata values
    metadata_set = MetadataSet(client._connection, client._project).to_dict()
    label_set = LabelSet(client._connection, client._project).to_dict()
    dclproj_label_table = dclproj._list_table_raw("Label")

    print(metadata_set)
    print(label_set)

    def get_label_or_metadata_name(item, dclproj_label_table):
        index = item["label"] - 1
        return (
            dclproj_label_table.iloc[index]["metadata"] == 1,
            dclproj_label_table.iloc[index]["name"],
        )

    print("Creating Project Label and Metadata Values")
    # TODO: Bulk upload of labels and metadata
    for _, item in dclproj._list_table_raw("LabelValue").iterrows():

        is_metadata, name = get_label_or_metadata_name(item, dclproj_label_table)

        # print(f"is_metadata {is_metadata}, name {name}, found in metadata set {item['label'] in metadata_set.keys()}")

        if is_metadata and name in metadata_set.keys():
            metadata_value = MetadataValue(
                client._connection, client.project, metadata_set[name]
            )
            metadata_value.color = None
            metadata_value.value = item["value"]
            try:
                metadata_value.insert()
            except Exception as e:
                print("metadata insert failed")

        elif not is_metadata and name in label_set.keys():
            label_value = LabelValue(
                client._connection, client.project, label_set[name]
            )
            label_value.color = item["color"]
            label_value.value = item["value"]
            try:
                label_value.insert()
            except Exception as e:
                print("label insert failed")
        else:
            print(
                f"label value not found on server for label_value {name,  item['value']}"
            )
            print(item)

            print(metadata_set)
            print(label_set)
            raise Exception("Error")

    print("Uploading Captures")
    capture_set = []
    captures = client.list_captures()
    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:  # Using ThreadPoolExecutor
        futures = []
        for index, capture in dclproj.list_captures(include_metadata=False).iterrows():
            if capture[1] in captures.Name.values and not force_capture:
                print("skipping capture: ", capture[1])
                continue
            future = executor.submit(
                upload_capture, client, capture, capture_dir, index
            )
            futures.append(future)

        for future in futures:  # Iterate and retrieve results
            try:
                result = future.result()
                capture_set.append((capture, result))
            except Exception as e:  # Handle potential exceptions
                print(f"Error: {e}")

    captures = client.list_captures()
    print("Uploading Metdata Relationshipos")
    bulk_upload_metadata_relationship_set_server(client, dclproj, captures)
    print("Uploading Label Relationshipos")
    bulk_upload_label_relationship_set_server(client, dclproj, captures)


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
