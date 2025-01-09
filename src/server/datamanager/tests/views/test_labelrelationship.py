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

# pylint: disable=W0201
import copy
import json
import logging

import pytest
from datamanager.models import (
    Capture,
    CaptureLabelValue,
    Label,
    LabelValue,
    Project,
    Segmenter,
    Team,
)
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.mark.usefixtures("authenticate")
class TestLabelRelationship:
    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.project = project = Project.objects.create(
            name="APITestProject",
            team=Team.objects.get(name=TEAM_NAME),
            capture_sample_schema={
                "Column1": {"type": "float"},
                "Column2": {"type": "string"},
            },
        )

        self.capture = capture = Capture.objects.create(
            project=project, name="TestCapture", number_samples=4, max_sequence=4
        )

    def test_make_capture_labelvalue_relationships(self, client):
        self.make_label_labelvalue(client)

        relationship_url = reverse(
            "label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        response = client.post(
            relationship_url,
            data={
                "label": self.label_uuid,
                "label_value": self.labelvalue_uuid,
                "segmenter": self.segmenter_id,
                "capture_sample_sequence_start": 1,
                "capture_sample_sequence_end": 2,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        # print response.data
        assert response.data[0]["capture_sample_sequence_start"] == 1
        assert response.data[0]["capture_sample_sequence_end"] == 2

        relationship_uuid = response.data[0]["uuid"]

        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": self.label_uuid,
                "label_or_metadata": "label",
            },
        )

        response = client.post(labelvalue_url, data={"value": "Blue"})
        assert response.status_code == status.HTTP_201_CREATED
        new_lv_uuid = response.data["uuid"]

        label_relation_detail_url = reverse(
            "label-relationship-detail",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
                "uuid": relationship_uuid,
            },
        )
        response = client.patch(
            label_relation_detail_url,
            data={
                "label": self.label_uuid,
                "label_value": new_lv_uuid,
                "uuid": relationship_uuid,
                "segmenter": self.segmenter_id,
                "capture_sample_sequence_start": 1,
                "capture_sample_sequence_end": 2,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert str(response.data[0]["label_value"]) == new_lv_uuid

        response = client.get(relationship_url)
        clv_list = response.data
        assert len(clv_list) == 1

        response = client.delete(label_relation_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = client.get(relationship_url)
        clv_list = response.data
        assert len(clv_list) == 0

    def make_label_labelvalue(
        self,
        client,
    ):
        label_url = reverse(
            "label-list",
            kwargs={"project_uuid": self.project.uuid, "label_or_metadata": "label"},
        )

        response = client.post(label_url, data={"name": "MyLabel", "type": "string"})
        segmenter = Segmenter.objects.create(
            name="Test Segmenter", project=self.project
        )
        self.segmenter_id = segmenter.id
        self.label_uuid = response.data["uuid"]

        self.labelvalue_uuid = self.make_labelvalue(
            client, self.label_uuid, "Red", "#FF0000"
        )

        return self.labelvalue_uuid

    def make_labelvalue(self, client, label_uuid, value, color):
        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": label_uuid,
                "label_or_metadata": "label",
            },
        )

        response = client.post(labelvalue_url, data={"value": value, "color": color})

        return response.data["uuid"]

    def test_create_post_patch_capture_labelvalue_relationships_many(self, client):
        self.make_label_labelvalue(client)

        relationship_url = reverse(
            "label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        response = client.post(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 1,
                        "capture_sample_sequence_end": 2,
                    },
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 2,
                        "capture_sample_sequence_end": 3,
                    },
                ]
            ),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data[0]["capture_sample_sequence_start"] == 1
        assert response.data[0]["capture_sample_sequence_end"] == 2

        assert response.data[1]["capture_sample_sequence_start"] == 2
        assert response.data[1]["capture_sample_sequence_end"] == 3

        relationship_uuid = response.data[0]["uuid"]

        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": self.label_uuid,
                "label_or_metadata": "label",
            },
        )

        response = client.post(labelvalue_url, data={"value": "Blue"})

        assert response.status_code == status.HTTP_201_CREATED
        new_lv_uuid = response.data["uuid"]

        label_relation_detail_url = reverse(
            "label-relationship-detail",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
                "uuid": relationship_uuid,
            },
        )

        response = client.patch(
            label_relation_detail_url,
            data={
                "label": self.label_uuid,
                "label_value": new_lv_uuid,
                "uuid": relationship_uuid,
                "segmenter": self.segmenter_id,
                "capture_sample_sequence_start": 1,
                "capture_sample_sequence_end": 2,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data[0]["label_value"]) == new_lv_uuid

        response = client.get(relationship_url)

        clv_list = response.data
        print(clv_list)
        assert len(clv_list) == 2

        response = client.delete(label_relation_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = client.get(relationship_url)
        clv_list = response.data
        assert len(clv_list) == 1

        from datamanager.models import CaptureLabelValue

        assert len(CaptureLabelValue.objects.all()) == 1

        response = client.post(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 0,
                        "capture_sample_sequence_end": 1,
                    },
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 2,
                        "capture_sample_sequence_end": 3,
                    },
                ]
            ),
            content_type="application/json",
        )

        assert len(CaptureLabelValue.objects.all()) == 1
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 0,
                        "capture_sample_sequence_end": 1,
                    },
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 2,
                        "capture_sample_sequence_end": 4,
                    },
                ]
            ),
            content_type="application/json",
        )

        assert len(CaptureLabelValue.objects.all()) == 3
        assert response.status_code == status.HTTP_201_CREATED

        clv = CaptureLabelValue.objects.all()

        response = client.put(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "uuid": str(clv[1].uuid),
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 0,
                        "capture_sample_sequence_end": 2,
                    },
                    {
                        "uuid": str(clv[0].uuid),
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 0,
                        "capture_sample_sequence_end": 3,
                    },
                ]
            ),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(CaptureLabelValue.objects.all()) == 3

        relationship_url = reverse(
            "project-capture-label-relationship-list",
            kwargs={"project_uuid": self.project.uuid},
        )

        response = client.post(
            relationship_url,
            data=json.dumps({"capture_uuid_list": [str(self.capture.uuid)]}),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    @pytest.mark.django_db(transaction=True)
    def test_create_post_patch_project_segment_labelvalue_relationships_large(
        self, client
    ):
        import time

        start = time.time()

        capture = Capture.objects.create(
            project=self.project,
            name="TestCaptureLarge",
            number_samples=1000,
            max_sequence=1000,
        )

        num_samples = 1000

        self.make_label_labelvalue(client)

        relationship_url = reverse(
            "v2-segmenter-label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "segmenter_pk": self.segmenter_id,
            },
        )

        template = {
            "label": self.label_uuid,
            "label_value": self.labelvalue_uuid,
            "capture": str(capture.uuid),
            "capture_sample_sequence_start": 1,
            "capture_sample_sequence_end": 2,
        }

        test_data = []
        for i in range(2, num_samples):
            tmp_data = copy.deepcopy(template)
            tmp_data["capture_sample_sequence_end"] = i
            test_data.append(tmp_data)

        response = client.post(
            relationship_url,
            data=json.dumps(test_data),
            content_type="application/json",
        )
        print(
            "POST: Create Capture Label Relationsip - ",
            time.time() - start,
            len(response.json()),
        )
        start = time.time()

        relationship_url = reverse(
            "project-capture-label-relationship-list",
            kwargs={"project_uuid": self.project.uuid},
        )

        response = client.post(
            relationship_url,
            data=json.dumps({"capture_uuid_list": [str(capture.uuid)]}),
            content_type="application/json",
        )
        print(
            "POST: Get Capture Label Relationsip for Capture List - time: ",
            time.time() - start,
            "len: ",
            len(response.json()),
        )
        start = time.time()

        data = response.json()

        relationship_url = reverse(
            "v2-segmenter-label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "segmenter_pk": self.segmenter_id,
            },
        )

        label_value_blue = self.make_labelvalue(
            client, self.label_uuid, "Blue", "#FF0000FF"
        )
        for clv in data:
            clv["label_value"] = label_value_blue

        response = client.put(
            relationship_url,
            data=json.dumps(data),
            content_type="application/json",
        )

        print(
            "PUT: Update Capture Label Relationsip - time: ",
            time.time() - start,
            "len: ",
            len(response.json()),
        )
        start = time.time()

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db(transaction=True)
    def test_create_post_patch_project_segment_labelvalue_relationships_many(
        self, client
    ):
        self.make_label_labelvalue(client)

        relationship_url = reverse(
            "v2-segmenter-label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "segmenter_pk": self.segmenter_id,
            },
        )

        response = client.post(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "capture": str(self.capture.uuid),
                        "capture_sample_sequence_start": 1,
                        "capture_sample_sequence_end": 2,
                    },
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "capture": str(self.capture.uuid),
                        "capture_sample_sequence_start": 2,
                        "capture_sample_sequence_end": 3,
                    },
                ]
            ),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data[0]["capture_sample_sequence_start"] == 1
        assert response.data[0]["capture_sample_sequence_end"] == 2

        assert response.data[1]["capture_sample_sequence_start"] == 2
        assert response.data[1]["capture_sample_sequence_end"] == 3

        relationship_uuid = response.data[0]["uuid"]

        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": self.label_uuid,
                "label_or_metadata": "label",
            },
        )

        response = client.post(labelvalue_url, data={"value": "Blue"})
        assert response.status_code == status.HTTP_201_CREATED
        new_lv_uuid = response.data["uuid"]

        label_relation_detail_url = reverse(
            "label-relationship-detail",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
                "uuid": relationship_uuid,
            },
        )

        response = client.patch(
            label_relation_detail_url,
            data={
                "label": self.label_uuid,
                "label_value": new_lv_uuid,
                "uuid": relationship_uuid,
                "segmenter": self.segmenter_id,
                "capture_sample_sequence_start": 1,
                "capture_sample_sequence_end": 2,
                "capture": str(self.capture.uuid),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert str(response.data[0]["label_value"]) == new_lv_uuid

        response = client.get(relationship_url)
        clv_list = response.data
        assert len(clv_list) == 2

        response = client.delete(label_relation_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = client.get(relationship_url)
        clv_list = response.data
        assert len(clv_list) == 1

        from datamanager.models import CaptureLabelValue

        assert len(CaptureLabelValue.objects.all()) == 1

        response = client.post(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "capture_sample_sequence_start": 0,
                        "capture_sample_sequence_end": 1,
                        "capture": str(self.capture.uuid),
                    },
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "capture_sample_sequence_start": 2,
                        "capture_sample_sequence_end": 3,
                        "capture": str(self.capture.uuid),
                    },
                ]
            ),
            content_type="application/json",
        )

        assert len(CaptureLabelValue.objects.all()) == 1
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "capture_sample_sequence_start": 0,
                        "capture_sample_sequence_end": 1,
                        "capture": str(self.capture.uuid),
                    },
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "capture_sample_sequence_start": 2,
                        "capture_sample_sequence_end": 4,
                        "capture": str(self.capture.uuid),
                    },
                ]
            ),
            content_type="application/json",
        )

        assert len(CaptureLabelValue.objects.all()) == 3
        assert response.status_code == status.HTTP_201_CREATED

        clv = CaptureLabelValue.objects.all()

        uuid0 = clv[1].uuid
        uuid1 = clv[0].uuid

        last_modified_uuid0 = CaptureLabelValue.objects.get(uuid=uuid0).last_modified

        response = client.put(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "uuid": str(uuid0),
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "capture": str(self.capture.uuid),
                        "capture_sample_sequence_start": 0,
                        "capture_sample_sequence_end": 2,
                    },
                    {
                        "uuid": str(uuid1),
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "capture": str(self.capture.uuid),
                        "capture_sample_sequence_start": 0,
                        "capture_sample_sequence_end": 3,
                    },
                ]
            ),
            content_type="application/json",
        )

        assert (
            last_modified_uuid0
            < CaptureLabelValue.objects.get(uuid=uuid0).last_modified
        )

        assert len(CaptureLabelValue.objects.all()) == 3
        assert response.status_code == status.HTTP_200_OK

        print(response.json())

        clv_updated = CaptureLabelValue.objects.get(uuid=uuid0)

        assert clv_updated.capture_sample_sequence_start == 0
        assert clv_updated.capture_sample_sequence_end == 2

        clv_updated = CaptureLabelValue.objects.get(uuid=uuid1)
        assert clv_updated.capture_sample_sequence_start == 0
        assert clv_updated.capture_sample_sequence_end == 3

        relationship_url = reverse(
            "project-capture-label-relationship-list",
            kwargs={"project_uuid": self.project.uuid},
        )

        response = client.post(
            relationship_url,
            data=json.dumps({"capture_uuid_list": [str(self.capture.uuid)]}),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    def test_make_capture_label_value_v2_updates_capture_last_modified(self, client):
        self.make_label_labelvalue(client)

        relationship_url = reverse(
            "label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        last_modified = self.capture.last_modified
        version = self.capture.version

        response = client.post(
            relationship_url,
            format="json",
            data={
                "label": self.label_uuid,
                "label_value": self.labelvalue_uuid,
                "segmenter": self.segmenter_id,
                "capture_sample_sequence_start": 1,
                "capture_sample_sequence_end": 2,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        self.capture.refresh_from_db()

        assert last_modified < self.capture.last_modified

        assert self.capture.version == version + 1

    def test_bulk_make_capture_label_value_v2_updates_capture_last_modified(
        self, client
    ):
        self.make_label_labelvalue(client)

        relationship_url = reverse(
            "label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        last_modified = self.capture.last_modified
        version = self.capture.version

        response = client.post(
            relationship_url,
            data=json.dumps(
                [
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 1,
                        "capture_sample_sequence_end": 2,
                    },
                    {
                        "label": self.label_uuid,
                        "label_value": self.labelvalue_uuid,
                        "segmenter": self.segmenter_id,
                        "capture_sample_sequence_start": 2,
                        "capture_sample_sequence_end": 3,
                    },
                ]
            ),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        self.capture.refresh_from_db()

        assert last_modified < self.capture.last_modified

        assert self.capture.version == version + 1

    def test_v2_project_lookup_fails(self, client):
        self.make_label_labelvalue(client)

        project2 = Project.objects.create(
            name="APITestProject2",
            team=Team.objects.get(name=TEAM_NAME),
            capture_sample_schema={
                "Column1": {"type": "float"},
                "Column2": {"type": "string"},
            },
        )

        relationship_url = reverse(
            "label-relationship-list",
            kwargs={"project_uuid": project2.uuid, "capture_uuid": self.capture.uuid},
        )
        response = client.post(
            relationship_url,
            format="json",
            data={
                "label": self.label_uuid,
                "label_value": self.labelvalue_uuid,
                "segmenter": self.segmenter_id,
                "capture_sample_sequence_start": 1,
                "capture_sample_sequence_end": 2,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_make_label_relationships_fail_without_start_end(self, client):
        self.make_label_labelvalue(client)
        relationship_url = reverse(
            "label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )
        # test auto setting sequence
        response = client.post(
            relationship_url,
            data={
                "label": self.label_uuid,
                "label_value": self.labelvalue_uuid,
                "segmenter": self.segmenter_id,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_make_label_relationships_v2_work_without_segmenter(self, client):
        self.make_label_labelvalue(client)
        relationship_url = reverse(
            "label-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )
        # test auto setting sequence
        response = client.post(
            relationship_url,
            data={
                "label": self.label_uuid,
                "label_value": self.labelvalue_uuid,
                "capture_sample_sequence_start": 1,
                "capture_sample_sequence_end": 2,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_delete_labels(self, client):
        label_url = reverse(
            "label-list",
            kwargs={"label_or_metadata": "label", "project_uuid": self.project.uuid},
        )
        response = client.post(
            label_url,
            data={
                "name": "TestLabel",
                "type": "string",
                "values": ["abc"],
                "capture_sample_sequence_start": 1,
                "capture_sample_sequence_end": 2,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        label_detail_url = reverse(
            "label-detail",
            kwargs={
                "label_or_metadata": "label",
                "project_uuid": self.project.uuid,
                "uuid": response.data["uuid"],
            },
        )
        response = client.get(label_detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["label_values"][0]["value"] == "abc"
        response = client.delete(label_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.skip("V1 depricated")
    def test_make_metadata_relationship_with_label_fails(self, client):
        label_url = reverse(
            "label-list",
            kwargs={"label_or_metadata": "label", "project_uuid": self.project.uuid},
        )

        response = client.post(
            label_url, data={"name": "TestLabel", "type": "string", "values": ["abc"]}
        )

        assert response.status_code == status.HTTP_201_CREATED

        response["Location"]

        relationship_url = reverse(
            "metadata-relationship-list-v1",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        # test auto setting sequence
        response = client.post(relationship_url, data={"name": "TestLabel"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.skip("V1 depricated")
    def test_invalid_names(self, client):
        relationship_url = reverse(
            "metadata-relationship-list-v1",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        # test auto setting sequence
        response = client.post(
            relationship_url, data={"name": "_Capture_", "value": 1, "type": "string"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        relationship_url = reverse(
            "metadata-relationship-list-v1",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        # test auto setting sequence
        response = client.post(
            relationship_url, data={"name": "_Capture_", "value": 1, "type": "string"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        relationship_url = reverse(
            "metadata-relationship-list-v1",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )
        # test auto setting sequence
        response = client.post(
            relationship_url, data={"name": "SegmentID", "value": 1, "type": "string"}
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_project_label_relationship(self, client):
        self.make_label_labelvalue(client)

        for i in range(0, 4):
            CaptureLabelValue.objects.create(
                project=self.project,
                capture=self.capture,
                label=Label.objects.get(uuid=self.label_uuid),
                label_value=LabelValue.objects.get(uuid=self.labelvalue_uuid),
                segmenter=Segmenter.objects.get(id=self.segmenter_id),
                capture_sample_sequence_start=i,
                capture_sample_sequence_end=i + 1,
            )

        label_url = reverse(
            "project-label-relationship-list",
            kwargs={"project_uuid": self.project.uuid},
        )

        response = client.get(
            label_url,
        )

        assert len(response.data) == 4
        assert sorted(list(response.data[0].keys())) == sorted(
            [
                "uuid",
                "capture",
                "label",
                "label_value",
                "capture_sample_sequence_start",
                "capture_sample_sequence_end",
                "segmenter",
                "created_at",
                "last_modified",
            ]
        )

        label_url = reverse(
            "project-label-relationship-list",
            kwargs={"project_uuid": self.project.uuid},
        )

        response = client.get(
            f"{label_url}?page_size=1",
        )

        assert len(response.data["results"]) == 1
        assert sorted(list(response.data["results"][0].keys())) == sorted(
            [
                "uuid",
                "capture",
                "label",
                "label_value",
                "capture_sample_sequence_start",
                "capture_sample_sequence_end",
                "label_info",
                "segmenter",
                "created_at",
                "last_modified",
            ]
        )

        response = client.get(response.data["next"].replace("http://testserver", ""))

        assert len(response.data["results"]) == 1
        assert sorted(list(response.data["results"][0].keys())) == sorted(
            [
                "uuid",
                "capture",
                "label",
                "label_value",
                "capture_sample_sequence_start",
                "capture_sample_sequence_end",
                "label_info",
                "segmenter",
                "created_at",
                "last_modified",
            ]
        )

    def test_project_label_relationship_delete_multi(self, client):
        self.make_label_labelvalue(client)
        clv = []
        for i in range(0, 4):
            clv.append(
                CaptureLabelValue.objects.create(
                    project=self.project,
                    capture=self.capture,
                    label=Label.objects.get(uuid=self.label_uuid),
                    label_value=LabelValue.objects.get(uuid=self.labelvalue_uuid),
                    segmenter=Segmenter.objects.get(id=self.segmenter_id),
                    capture_sample_sequence_start=i,
                    capture_sample_sequence_end=i + 1,
                )
            )

        label_url = reverse(
            "relationship-delete",
            kwargs={"project_uuid": self.project.uuid, "label_or_metadata": "label"},
        )

        response = client.post(
            label_url,
            data=json.dumps([str(x.uuid) for x in clv]),
            content_type="application/json",
        )

        assert response.data == 4
