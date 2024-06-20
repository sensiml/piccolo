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

import copy
import json
import os
import shutil

import pandas as pd
import pytest
from datamanager.datasegments import load_datasegments
from datamanager.models import (
    Capture,
    CaptureConfiguration,
    CaptureLabelValue,
    CaptureMetadataValue,
    Label,
    LabelValue,
    Project,
    Query,
    Segmenter,
    TeamMember,
)
from datamanager.query import partition_query, query_driver_from_csv_to_datasegments
from django.conf import settings
from pandas import DataFrame
from rest_framework import status
from rest_framework.reverse import reverse

"""Tests Legacy Query Endpoint"""


pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("authenticate")]


@pytest.fixture
def query_list():
    try:
        project = Project.objects.get(team_id=1)
        query = Query.objects.get(id=1)
        return project, endpoint, query
    except Exception as e:
        print(e)

    project = Project.objects.create(
        team_id=1,
        name="TestQueryProject",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )

    capture_dir = os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid))
    os.mkdir(capture_dir)

    capture_length = 25
    delta = 5

    # num_captures should be the same len aslabel-values map
    num_captures = 3
    label_values_map = {0: "A", 1: "B", 2: "C"}

    metadata_name = "Subject"
    label_name = "Event"
    segmenter_name = "Manual"

    assert num_captures == len(label_values_map)

    captures = []
    for i in range(0, num_captures):
        captures.append(
            Capture.objects.create(
                project=project,
                name="TestCapture{}".format(i),
                number_samples=capture_length,
                max_sequence=capture_length,
            ),
        )
        captures[-1].file = os.path.join(capture_dir, str(captures[-1].uuid))
        captures[-1].save()

    for capture in captures:
        df = pd.DataFrame(
            {
                "Column1": list(range(capture_length)),
                "Column2": [i * 2 for i in range(capture_length)],
                "sequence": range(capture_length),
            }
        )
        df.to_csv(os.path.join(capture_dir, str(capture.uuid)), index=None)

    # create metadata
    metadata = Label.objects.create(
        project=project, name=metadata_name, metadata=True, type="str"
    )

    label = Label.objects.create(
        project=project, name=label_name, metadata=False, type="str"
    )

    # create label values
    label_values = []

    for i in range(len(label_values_map)):
        label_values.append(
            LabelValue.objects.create(label=label, value=label_values_map[i])
        )

    # create metadata
    metadata_A = LabelValue.objects.create(label=metadata, value="John")
    metadata_B = LabelValue.objects.create(label=metadata, value="Emily")

    # create segmetner
    segmenter = Segmenter.objects.create(
        project=project, name=segmenter_name, custom=True
    )

    # add metadata to captures
    CaptureMetadataValue.objects.create(
        project=project, capture=captures[0], label=metadata, label_value=metadata_A
    )

    CaptureMetadataValue.objects.create(
        project=project, capture=captures[1], label=metadata, label_value=metadata_B
    )

    CaptureMetadataValue.objects.create(
        project=project, capture=captures[2], label=metadata, label_value=metadata_B
    )

    # add labels_values to captures

    for i in range(0, capture_length - delta, delta):
        for index in range(len(label_values)):
            CaptureLabelValue.objects.create(
                project=project,
                capture=captures[index],
                label=label,
                label_value=label_values[index],
                segmenter=segmenter,
                capture_sample_sequence_start=i,
                capture_sample_sequence_end=i + delta,
            )

    query = Query.objects.create(
        name="TestQuery",
        project=project,
        segmenter=segmenter,
        columns=json.dumps(["Column1", "Column2"]),
        metadata_columns=json.dumps([metadata_name]),
        label_column=label_name,
        metadata_filter="",
    )

    query_with_filter = Query.objects.create(
        name="TestQueryFilter",
        project=project,
        segmenter=segmenter,
        columns=json.dumps(["Column1", "Column2"]),
        metadata_columns=json.dumps([metadata_name]),
        label_column=label_name,
        metadata_filter="[Subject] IN [John] AND [Event] IN [A,B,C]",
    )

    query_with_capture_id = Query.objects.create(
        name="QueryFilterCID",
        project=project,
        segmenter=segmenter,
        columns=json.dumps(["Column1", "Column2"]),
        metadata_columns=json.dumps(["Subject", "capture_uuid", "segment_uuid"]),
        label_column=label_name,
        metadata_filter=""
        # metadata_filter="[capture_uuid] IN [{}]".format(captures[0].uuid),
    )

    "Runs once per class"
    yield project, query, query_with_filter, query_with_capture_id, segmenter

    shutil.rmtree(capture_dir)


@pytest.fixture
def query_list_large():
    try:
        project = Project.objects.get(team_id=1)
        query = Query.objects.get(id=1)
        return project, endpoint, query
    except Exception as e:
        print(e)

    project = Project.objects.create(
        team_id=1,
        name="TestQueryProject",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )

    capture_dir = os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid))
    os.mkdir(capture_dir)

    capture_length = 1000
    delta = 5

    # num_captures should be the same len aslabel-values map
    num_captures = 100
    label_values_map = {0: "A", 1: "B", 2: "C"}

    metadata_name = "Subject"
    label_name = "Event"
    segmenter_name = "Manual"

    captures = []
    for i in range(0, num_captures):
        captures.append(
            Capture.objects.create(
                project=project,
                name="TestCapture{}".format(i),
                number_samples=capture_length,
                max_sequence=capture_length,
            ),
        )
        captures[-1].file = os.path.join(capture_dir, str(captures[-1].uuid))
        captures[-1].save()

    for capture in captures:
        df = pd.DataFrame(
            {
                "Column1": list(range(capture_length)),
                "Column2": [i * 2 for i in range(capture_length)],
                "sequence": range(capture_length),
            }
        )

    # create metadata
    metadata = Label.objects.create(
        project=project, name=metadata_name, metadata=True, type="str"
    )

    label = Label.objects.create(
        project=project, name=label_name, metadata=False, type="str"
    )

    # create label values
    label_values = []

    for i in range(len(label_values_map)):
        label_values.append(
            LabelValue.objects.create(label=label, value=label_values_map[i])
        )

    # create metadata
    metadata_A = LabelValue.objects.create(label=metadata, value="John")
    metadata_B = LabelValue.objects.create(label=metadata, value="Emily")

    # create segmetner
    segmenter = Segmenter.objects.create(
        project=project, name=segmenter_name, custom=True
    )

    # add metadata to captures
    CaptureMetadataValue.objects.create(
        project=project, capture=captures[0], label=metadata, label_value=metadata_A
    )

    CaptureMetadataValue.objects.create(
        project=project, capture=captures[1], label=metadata, label_value=metadata_B
    )

    CaptureMetadataValue.objects.create(
        project=project, capture=captures[2], label=metadata, label_value=metadata_B
    )

    # add labels_values to captures

    for i in range(0, capture_length - delta, delta):
        for index in range(len(label_values)):
            CaptureLabelValue.objects.create(
                project=project,
                capture=captures[index],
                label=label,
                label_value=label_values[index % 3],
                segmenter=segmenter,
                capture_sample_sequence_start=i,
                capture_sample_sequence_end=i + delta,
            )

    query = Query.objects.create(
        name="TestQuery",
        project=project,
        segmenter=segmenter,
        columns=json.dumps(["Column1", "Column2"]),
        metadata_columns=json.dumps([metadata_name]),
        label_column=label_name,
        metadata_filter="",
    )

    "Runs once per class"
    yield project, query, segmenter

    shutil.rmtree(capture_dir)


@pytest.fixture
def query_list_large_with_csv():
    try:
        project = Project.objects.get(team_id=1)
        query = Query.objects.get(id=1)
        return project, endpoint, query
    except Exception as e:
        print(e)

    project = Project.objects.create(
        team_id=1,
        name="TestQueryProject",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )

    capture_dir = os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid))
    os.mkdir(capture_dir)

    capture_length = 1000
    delta = 5

    # num_captures should be the same len aslabel-values map
    num_captures = 100
    label_values_map = {0: "A", 1: "B", 2: "C"}

    metadata_name = "Subject"
    label_name = "Event"
    segmenter_name = "Manual"

    captures = []
    for i in range(0, num_captures):
        captures.append(
            Capture.objects.create(
                project=project,
                name="TestCapture{}".format(i),
                number_samples=capture_length,
                max_sequence=capture_length,
            ),
        )
        captures[-1].file = os.path.join(capture_dir, str(captures[-1].uuid))
        captures[-1].save()

    for capture in captures:
        df = pd.DataFrame(
            {
                "Column1": list(range(capture_length)),
                "Column2": [i * 2 for i in range(capture_length)],
                "sequence": range(capture_length),
            }
        )

        df.to_csv(os.path.join(capture_dir, str(capture.uuid)), index=None)

    # create metadata
    metadata = Label.objects.create(
        project=project, name=metadata_name, metadata=True, type="str"
    )

    label = Label.objects.create(
        project=project, name=label_name, metadata=False, type="str"
    )

    # create label values
    label_values = []

    for i in range(len(label_values_map)):
        label_values.append(
            LabelValue.objects.create(label=label, value=label_values_map[i])
        )

    # create metadata
    metadata_A = LabelValue.objects.create(label=metadata, value="John")
    metadata_B = LabelValue.objects.create(label=metadata, value="Emily")

    # create segmetner
    segmenter = Segmenter.objects.create(
        project=project, name=segmenter_name, custom=True
    )

    # add metadata to captures
    CaptureMetadataValue.objects.create(
        project=project, capture=captures[0], label=metadata, label_value=metadata_A
    )

    CaptureMetadataValue.objects.create(
        project=project, capture=captures[1], label=metadata, label_value=metadata_B
    )

    CaptureMetadataValue.objects.create(
        project=project, capture=captures[2], label=metadata, label_value=metadata_B
    )

    # add labels_values to captures

    for i in range(0, capture_length - delta, delta):
        for index in range(len(label_values)):
            CaptureLabelValue.objects.create(
                project=project,
                capture=captures[index],
                label=label,
                label_value=label_values[index % 3],
                segmenter=segmenter,
                capture_sample_sequence_start=i,
                capture_sample_sequence_end=i + delta,
            )

    query = Query.objects.create(
        name="TestQuery",
        project=project,
        segmenter=segmenter,
        columns=json.dumps(["Column1", "Column2"]),
        metadata_columns=json.dumps([metadata_name]),
        label_column=label_name,
        metadata_filter="",
    )

    "Runs once per class"
    yield project, query, segmenter

    shutil.rmtree(capture_dir)


@pytest.fixture
def capture_configuration(query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list
    capture_configuration_1 = CaptureConfiguration.objects.create(
        name="Custom_1",
        project=project,
        configuration={"name": "Custom_1", "capture_sources": [{"sample_rate": 100}]},
    )

    capture_configuration_2 = CaptureConfiguration.objects.create(
        name="Custom_2",
        project=project,
        configuration={"name": "Custom_2", "capture_sources": [{"sample_rate": 100}]},
    )

    capture_configuration_3 = CaptureConfiguration.objects.create(
        name="Custom_3",
        project=project,
        configuration={"name": "Custom_3", "capture_sources": [{"sample_rate": 200}]},
    )

    return [
        str(capture_configuration_1.uuid),
        str(capture_configuration_2.uuid),
        str(capture_configuration_3.uuid),
    ]


test_data_dict = {
    "columns": ["Column1", "Column2"],
    "metadata_columns": ["Subject"],
    "metadata_filter": "",
    "name": "query_gesture",
    "label_column": "Event",
    "segmenter_id": None,
    "capture_configurations": "",
}

test_expected_result = {
    "name": "query_gesture",
    "columns": ["Column1", "Column2"],
    "label_column": "Event",
    "metadata_columns": ["Subject"],
    "metadata_filter": "",
    "segmenter_id": None,
    "combine_labels": None,
    "capture_configurations": "",
}


@pytest.mark.usefixtures("authenticate")
def test_add_query(client, query_list, capture_configuration):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    test_data_dict["segmenter_id"] = segmenter.id
    test_data_dict["capture_configurations"] = json.dumps(capture_configuration[:1])

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}),
        data=test_data_dict,
    )

    test_expected_result["segmenter_id"] = segmenter.id
    test_expected_result["capture_configurations"] = capture_configuration[:1]

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()

    for key in test_expected_result:
        assert result[key] == test_expected_result[key]


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("authenticate")
def test_add_query_without_capture_configurations(
    client, query_list, capture_configuration
):
    # in case capture_configurations is not part of the data
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    test_data_dict["segmenter_id"] = segmenter.id
    del test_data_dict["capture_configurations"]

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}),
        data=test_data_dict,
    )

    test_expected_result["segmenter_id"] = segmenter.id
    del test_expected_result["capture_configurations"]

    result = response.json()

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_201_CREATED

    for key in test_expected_result:
        assert result[key] == test_expected_result[key]


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("authenticate")
def test_add_query_with_empty_capture_configurations(
    client, query_list, capture_configuration
):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    test_data_dict["segmenter_id"] = segmenter.id

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}),
        data=test_data_dict,
    )

    test_expected_result["segmenter_id"] = segmenter.id
    test_expected_result["capture_configurations"] = []

    result = response.json()

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_201_CREATED

    for key in test_expected_result:
        assert result[key] == test_expected_result[key]


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("authenticate")
def test_add_query_with_multi_capture_configurations(
    client, query_list, capture_configuration
):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    test_data_dict["segmenter_id"] = segmenter.id
    test_data_dict["capture_configurations"] = json.dumps(capture_configuration[:2])

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}),
        data=test_data_dict,
    )

    test_expected_result["segmenter_id"] = segmenter.id
    test_expected_result["capture_configurations"] = capture_configuration[:2]

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()

    for key in test_expected_result:
        assert result[key] == test_expected_result[key]


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("authenticate")
def test_add_query_with_multi_capture_configurations_different_sample_rate(
    client, query_list, capture_configuration
):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    test_data_dict["segmenter_id"] = segmenter.id
    test_data_dict["capture_configurations"] = json.dumps(capture_configuration)

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}),
        data=test_data_dict,
    )

    response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
def test_add_query_bad_inputs(client, query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    template = {
        "columns": ["Column1", "Column2"],
        "metadata_columns": ["Subject"],
        "metadata_filter": "",
        "name": "query_gesture",
        "label_column": "Event",
        "segmenter_id": segmenter.id,
    }

    bad_query = copy.deepcopy(template)
    bad_query["label_column"] = "WRONG_LABEL"

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}), data=bad_query
    )

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    bad_query = copy.deepcopy(template)
    bad_query["segmenter_id"] = 5

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}), data=bad_query
    )

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    bad_query = copy.deepcopy(template)
    bad_query["segmenter_id"] = ""

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}), data=bad_query
    )

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    bad_query = copy.deepcopy(template)
    bad_query["metadata_columns"] = ["REDRED"]

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}), data=bad_query
    )

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    bad_query = copy.deepcopy(template)
    bad_query["metadata_columns"] = ""

    response = client.post(
        reverse("query-list", kwargs={"project_uuid": project.uuid}), data=bad_query
    )

    # These endpoints return HTTP 200 OK instead of HTTP 201 Created
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_query_detail_view(client, query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list
    url = reverse(
        "query-detail", kwargs=dict(project_uuid=project.uuid, uuid=query.uuid)
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK

    query.refresh_from_db()
    query.segment_info = {"Test": "Test"}
    query.save()

    response = client.put(
        url,
        data={
            "columns": ["Column1", "Column2"],
            "metadata_columns": ["Subject"],
            "metadata_filter": "[Subect] IN [1]",
            "name": "query_gesture",
            "label_column": "Event",
            "segmenter_id": segmenter.id,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    query.refresh_from_db()

    assert query.segment_info is None

    response = client.delete(url, format="json")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.skip(reason="unreliable fails 50%, needs to be fixed")
@pytest.mark.django_db(transaction=True)
def test_project_statistics(client, query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    url = reverse("project-statistics", kwargs=dict(project_uuid=project.uuid))

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK

    results = response.json()

    print(results)

    # this changes every time its created, remove for now
    [result.pop("capture_uuid") for result in results]

    expected_result = [
        {
            "event_labels": {
                "Event": [
                    {"value": "A", "count": 0},
                    {"value": "B", "count": 0},
                    {"value": "C", "count": 4},
                ]
            },
            "metadata": {"Subject": "Emily"},
            "total_event_count": 4,
            "capture_name": "TestCapture2",
        },
        {
            "event_labels": {
                "Event": [
                    {"value": "A", "count": 0},
                    {"value": "B", "count": 4},
                    {"value": "C", "count": 0},
                ]
            },
            "metadata": {"Subject": "Emily"},
            "total_event_count": 4,
            "capture_name": "TestCapture1",
        },
        {
            "event_labels": {
                "Event": [
                    {"value": "A", "count": 4},
                    {"value": "B", "count": 0},
                    {"value": "C", "count": 0},
                ]
            },
            "metadata": {"Subject": "John"},
            "total_event_count": 4,
            "capture_name": "TestCapture0",
        },
    ]

    assert len(results) == len(expected_result)

    assert results == expected_result


@pytest.mark.skip("TO BE FIXED")
@pytest.mark.django_db(transaction=True)
def test_project_statistics_without_event(client, query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list
    url = reverse("project-statistics", kwargs=dict(project_uuid=project.uuid))

    response = client.get(url, data={"events": False}, format="json")

    assert response.status_code == status.HTTP_200_OK

    results = response.json()

    print(results)

    # this changes every time its created, remove for now
    [result.pop("capture_uuid") for result in results]

    expected_result = [
        {
            "main_label": "C",
            "metadata": {"Subject": "Emily"},
            "total_event_count": 4,
            "capture_name": "TestCapture2",
        },
        {
            "main_label": "B",
            "metadata": {"Subject": "Emily"},
            "total_event_count": 4,
            "capture_name": "TestCapture1",
        },
        {
            "main_label": "A",
            "metadata": {"Subject": "John"},
            "total_event_count": 4,
            "capture_name": "TestCapture0",
        },
    ]

    assert results == expected_result


@pytest.mark.django_db(transaction=True)
def test_query_statistics(client, query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    url = reverse(
        "query-statistics", kwargs=dict(project_uuid=project.uuid, query_id=query.uuid)
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK

    def sort_responses(reponse):
        return (
            DataFrame(reponse)
            .sort_values(
                by=["Capture", "Event", "Subject", "Segment Length", "segstart"]
            )
            .reset_index(drop=True)
            .to_dict(orient="records")
        )

    expected_result = [
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 0,
        },
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 5,
        },
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 10,
        },
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 15,
        },
        {
            "Capture": "TestCapture1",
            "Subject": "Emily",
            "Event": "B",
            "Segment Length": 6,
            "segstart": 0,
        },
        {
            "Capture": "TestCapture1",
            "Subject": "Emily",
            "Event": "B",
            "Segment Length": 6,
            "segstart": 5,
        },
        {
            "Capture": "TestCapture1",
            "Subject": "Emily",
            "Event": "B",
            "Segment Length": 6,
            "segstart": 10,
        },
        {
            "Capture": "TestCapture1",
            "Subject": "Emily",
            "Event": "B",
            "Segment Length": 6,
            "segstart": 15,
        },
        {
            "Capture": "TestCapture2",
            "Subject": "Emily",
            "Event": "C",
            "Segment Length": 6,
            "segstart": 0,
        },
        {
            "Capture": "TestCapture2",
            "Subject": "Emily",
            "Event": "C",
            "Segment Length": 6,
            "segstart": 5,
        },
        {
            "Capture": "TestCapture2",
            "Subject": "Emily",
            "Event": "C",
            "Segment Length": 6,
            "segstart": 10,
        },
        {
            "Capture": "TestCapture2",
            "Subject": "Emily",
            "Event": "C",
            "Segment Length": 6,
            "segstart": 15,
        },
    ]

    assert sort_responses(response.json()) == expected_result

    url = reverse(
        "query-statistics",
        kwargs=dict(project_uuid=project.uuid, query_id=query_with_filter.uuid),
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK

    expected_result = [
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 0,
        },
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 5,
        },
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 10,
        },
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 15,
        },
    ]

    assert sort_responses(response.json()) == expected_result

    url = reverse(
        "query-statistics",
        kwargs=dict(project_uuid=project.uuid, query_id=query_with_capture_id.uuid),
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK

    ########################################################

    url = reverse(
        "query-summary-statistics",
        kwargs=dict(project_uuid=project.uuid, query_id=query_with_filter.uuid),
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "samples": {"A": 24},
        "segments": {"A": 4},
        "total_segments": 4,
    }

    url = reverse(
        "query-summary-statistics",
        kwargs=dict(project_uuid=project.uuid, query_id=query_with_capture_id.uuid),
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "samples": {"A": 24, "B": 24, "C": 24},
        "segments": {"A": 4, "B": 4, "C": 4},
        "total_segments": 12,
    }


@pytest.mark.django_db(transaction=True)
def test_query_statistics_up_to_date(client, query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    url = reverse(
        "query-cache-status",
        kwargs=dict(project_uuid=project.uuid, query_id=query.uuid),
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == None

    url = reverse(
        "query-statistics",
        kwargs=dict(project_uuid=project.uuid, query_id=query_with_capture_id.uuid),
    )

    response = client.get(url, format="json")

    query.segment_info = expected_result = {
        "Capture": [
            "TestCapture0",
            "TestCapture0",
            "TestCapture0",
            "TestCapture0",
            "TestCapture1",
            "TestCapture1",
            "TestCapture1",
            "TestCapture1",
            "TestCapture2",
            "TestCapture2",
            "TestCapture2",
            "TestCapture2",
        ],
        "Subject": [
            "John",
            "John",
            "John",
            "John",
            "Emily",
            "Emily",
            "Emily",
            "Emily",
            "Emily",
            "Emily",
            "Emily",
            "Emily",
        ],
        "Event": ["A", "A", "A", "A", "B", "B", "B", "B", "C", "C", "C", "C"],
        "Segment Length": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        "segstart": [0, 5, 10, 15, 0, 5, 10, 15, 0, 5, 10, 15],
    }
    query.save()

    url = reverse(
        "query-cache-status",
        kwargs=dict(project_uuid=project.uuid, query_id=query.uuid),
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == True

    query.segment_info = response.json()

    query.segment_info = expected_result = [
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 0,
        },
        {
            "Capture": "TestCapture0",
            "Subject": "John",
            "Event": "A",
            "Segment Length": 6,
            "segstart": 5,
        },
    ]
    query.save()

    assert response.status_code == status.HTTP_200_OK

    url = reverse(
        "query-cache-status",
        kwargs=dict(project_uuid=project.uuid, query_id=query.uuid),
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == False

    # delete session
    query.segmenter_id = None
    query.save()

    url = reverse(
        "query-cache-status",
        kwargs=dict(project_uuid=project.uuid, query_id=query.uuid),
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == False
    assert response.json()["build_status"] == "FAILED"


@pytest.mark.skip(reason="Seemingly deprecated endpoint")
def test_query_size(client, query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list
    url = reverse(
        "query-size", kwargs=dict(project_uuid=project.uuid, query_id=query.uuid)
    )

    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK


def sort_responses_by_name(reponse):
    return (
        DataFrame(reponse)
        .sort_values(by=["name"])
        .reset_index(drop=True)
        .to_dict(orient="records")
    )


@pytest.mark.usefixtures("authenticate")
def test_get_captures_statistics(client, query_list):
    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    project2 = Project.objects.create(
        team_id=1,
        name="TestQueryProject2",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )

    Capture.objects.create(project=project, name="TestCapture_no_labels")
    Capture.objects.create(project=project2, name="TestCapture_differnt_project")

    response = client.get(
        reverse("captures-stats", kwargs=dict(project_uuid=project.uuid)),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    # id and uuid changes on every run
    for result in results:
        result.pop("uuid")
        result.pop("capture_uuid")
        result.pop("capture_configuration_uuid")
        result.pop("created")

    expected_result = [
        {
            "name": "TestCapture0",
            "file_size_mb": None,
            "Subject": "John",
            "total_events": 4,
        },
        {
            "name": "TestCapture1",
            "file_size_mb": None,
            "Subject": "Emily",
            "total_events": 4,
        },
        {
            "name": "TestCapture2",
            "file_size_mb": None,
            "Subject": "Emily",
            "total_events": 4,
        },
        {
            "name": "TestCapture_no_labels",
            "file_size_mb": None,
            "Subject": None,
            "total_events": 0,
        },
    ]

    assert sort_responses_by_name(results) == sort_responses_by_name(expected_result)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("query_id", ["query", "query_filter", "query_with_capture_id"])
def test_query_data_task(query_id, client, query_list):
    import os

    from datamanager.tasks import querydata_async
    from django.conf import settings

    project, query, query_with_filter, query_with_capture_id, segmenter = query_list

    if query_id == "query_filter":
        query = query_with_filter
    elif query_id == "query_with_capture_id":
        query = query_with_capture_id

    querydata_async(
        TeamMember.objects.get(pk=1).user.id, query.project.uuid, query.uuid
    )

    result = load_datasegments(
        os.path.join(
            settings.SERVER_QUERY_ROOT, str(query.uuid), str(query.uuid) + ".0.pkl"
        )
    )

    if query_id == "query":
        expected_result = result = load_datasegments(
            os.path.join(
                os.path.dirname(__file__), "data", "query_data_task_results.pkl"
            )
        )

        assert result == expected_result

    url = reverse(
        "query-data",
        kwargs=dict(project_uuid=project.uuid, query_id=query.uuid, partition_id=0),
    )

    response = client.get(url)

    assert response.status_code == 200

    query_uuid = query.uuid
    query.refresh_from_db()
    query.delete()

    assert not os.path.exists(os.path.join(settings.SERVER_QUERY_ROOT, str(query_uuid)))


@pytest.mark.django_db(transaction=True)
def test_partition_query(client, query_list_large):
    project, query, segmenter = query_list_large

    query_parser, filter_list, drop_capture_uuid = partition_query(query)

    M = []
    for i, fl in enumerate(filter_list):
        M.append(set(pd.DataFrame(fl).capture_id))

    for start_index, set_1 in enumerate(M):
        for set_2 in M[start_index:]:
            assert set_1 not in set_2


@pytest.mark.django_db(transaction=True)
def test_query_driver_from_csv_to_datasegment(client, query_list_large_with_csv):
    project, query, segmenter = query_list_large_with_csv

    query_parser, partitions, drop_capture_uuid = partition_query(query)
    task_id = "TestQueryDriver"
    cache = []
    segment_count = 0
    segment_length = 0
    for index, partition in enumerate(partitions):
        partition_name = "{}.{}.gz".format(query.uuid, index)

        tmp_query = {}
        tmp_query["outputs"] = [partition_name]
        tmp_query["query_info"] = partition
        tmp_query["metadata"] = query_parser._metadata
        tmp_query["label"] = query_parser._label
        tmp_query["columns"] = query_parser._columns
        tmp_query["segment_uuid"] = query_parser.return_segment_uuid
        tmp_query["segment_start"] = segment_count

        segment_count += len(partition)

        for p in partition:
            segment_length += p["length"]

        data = query_driver_from_csv_to_datasegments(
            task_id=task_id,
            query_info=tmp_query,
            project_id=project.uuid,
            pipeline_id=query.uuid,
            exclude_metadata_value=None,
        )

        cache.append([sum([x["data"].shape[1] for x in data]), partition_name])

    print(cache)
