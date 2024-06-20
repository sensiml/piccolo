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
import json
import logging

import pytest
from datamanager.models import (
    Capture,
    CaptureMetadataValue,
    Label,
    LabelValue,
    Project,
    Team,
)
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.mark.usefixtures("authenticate")
class TestMetadataRelationship:
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

        self.capture2 = capture = Capture.objects.create(
            project=project, name="TestCapture2", number_samples=4, max_sequence=4
        )

    def make_metadata_labelvalue(
        self, client, label_name="MyLabel", label_value_names=["Red"]
    ):
        self.labelvalue_uuids = []
        label_url = reverse(
            "label-list",
            kwargs={"project_uuid": self.project.uuid, "label_or_metadata": "metadata"},
        )

        response = client.post(label_url, data={"name": label_name, "type": "string"})

        self.label_uuid = response.data["uuid"]

        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": self.label_uuid,
                "label_or_metadata": "metadata",
            },
        )

        for label_value_name in label_value_names:
            response = client.post(labelvalue_url, data={"value": label_value_name})

            self.labelvalue_uuids.append(response.data["uuid"])

        return self.label_uuid, self.labelvalue_uuids

    def make_single_metadata_labelvalue(
        self, client, label_uuid, label_value_name="Red"
    ):
        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": label_uuid,
                "label_or_metadata": "metadata",
            },
        )

        response = client.post(labelvalue_url, data={"value": label_value_name})

        labelvalue_uuid = response.data["uuid"]

        return labelvalue_uuid

    def test_single_capture_multi_metadata_create_update(self, client):
        label_uuid_1, labelvalue_uuid_1 = self.make_metadata_labelvalue(
            client, label_name="meta1", label_value_names=["1", "2"]
        )
        label_uuid_2, labelvalue_uuid_2 = self.make_metadata_labelvalue(
            client, label_name="meta2", label_value_names=["A", "B"]
        )

        relationship_url = reverse(
            "metadata-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        response = client.post(
            relationship_url,
            format="json",
            data=[
                {"label": label_uuid_1, "label_value": labelvalue_uuid_1[0]},
                {"label": label_uuid_2, "label_value": labelvalue_uuid_2[0]},
            ],
        )

        assert len(CaptureMetadataValue.objects.all()) == 2

        response = client.put(
            relationship_url,
            format="json",
            data=[
                {
                    "uuid": response.data[0]["uuid"],
                    "label": label_uuid_1,
                    "label_value": labelvalue_uuid_1[1],
                },
                {
                    "uuid": response.data[1]["uuid"],
                    "label": label_uuid_2,
                    "label_value": labelvalue_uuid_2[1],
                },
            ],
        )

        assert len(CaptureMetadataValue.objects.all()) == 2

        assert response.status_code == status.HTTP_200_OK

        response = client.put(
            relationship_url,
            format="json",
            data=[
                {
                    "uuid": response.data[0]["uuid"],
                    "label": label_uuid_1,
                    "label_value": labelvalue_uuid_2[1],
                },
                {
                    "uuid": response.data[1]["uuid"],
                    "label": label_uuid_2,
                    "label_value": labelvalue_uuid_1[1],
                },
            ],
        )

        assert len(CaptureMetadataValue.objects.all()) == 2

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_multi_capture_multi_metadata_create_update(self, client):
        label_uuid_1, labelvalue_uuid_1 = self.make_metadata_labelvalue(
            client, label_name="meta1", label_value_names=["1", "2"]
        )
        label_uuid_2, labelvalue_uuid_2 = self.make_metadata_labelvalue(
            client, label_name="meta2", label_value_names=["A", "B"]
        )

        labelvalue_uuid_2_C = self.make_single_metadata_labelvalue(
            client, label_uuid_2, "C"
        )
        labelvalue_uuid_1_3 = self.make_single_metadata_labelvalue(
            client, label_uuid_1, 3
        )

        relationship_url = reverse(
            "project-metadata-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
            },
        )

        response = client.post(
            relationship_url,
            format="json",
            data=[
                {
                    "label": label_uuid_1,
                    "label_value": labelvalue_uuid_1[0],
                    "capture": self.capture.uuid,
                },
                {
                    "label": label_uuid_2,
                    "label_value": labelvalue_uuid_2[0],
                    "capture": self.capture2.uuid,
                },
            ],
        )
        assert len(CaptureMetadataValue.objects.all()) == 2

        response = client.put(
            relationship_url,
            format="json",
            data=[
                {
                    "uuid": response.data[0]["uuid"],
                    "label": label_uuid_1,
                    "label_value": labelvalue_uuid_1_3,
                    "capture": self.capture.uuid,
                },
                {
                    "uuid": response.data[1]["uuid"],
                    "label": label_uuid_2,
                    "label_value": labelvalue_uuid_2_C,
                    "capture": self.capture2.uuid,
                },
            ],
        )

        assert len(CaptureMetadataValue.objects.all()) == 2

        relationship_url = reverse(
            "project-capture-metadata-relationship-list",
            kwargs={"project_uuid": self.project.uuid},
        )

        response = client.post(
            relationship_url,
            content_type="application/json",
            data=json.dumps(
                {"capture_uuid_list": [str(self.capture.uuid), str(self.capture2.uuid)]}
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_create_delete_metadata(self, client):
        label_url = reverse(
            "label-list",
            kwargs={"label_or_metadata": "metadata", "project_uuid": self.project.uuid},
        )
        response = client.post(
            label_url, data={"name": "TestLabel", "type": "string", "values": ["abc"]}
        )
        assert response.status_code == status.HTTP_201_CREATED
        label_detail_url = reverse(
            "label-detail",
            kwargs={
                "label_or_metadata": "metadata",
                "project_uuid": self.project.uuid,
                "uuid": response.data["uuid"],
            },
        )
        response = client.get(label_detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["label_values"][0]["value"] == "abc"
        response = client.delete(label_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_make_metadata_relationship_v2_updates_capture_last_modified(self, client):
        self.make_metadata_value(client)

        relationship_url = reverse(
            "metadata-relationship-list",
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
            data={"label": self.label_uuid, "label_value": self.labelvalue_uuid},
        )

        assert response.status_code == status.HTTP_201_CREATED

        self.capture.refresh_from_db()

        assert last_modified < self.capture.last_modified
        assert version < self.capture.version

    def test_make_update_capture_metadata_relationships(self, client):
        self.make_metadata_value(client)

        relationship_url = reverse(
            "metadata-relationship-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
            },
        )

        response = client.post(
            relationship_url,
            data={"label": self.label_uuid, "label_value": self.labelvalue_uuid},
        )
        assert response.status_code == status.HTTP_201_CREATED

        md_relation_uuid = response.data[0]["uuid"]

        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": self.label_uuid,
                "label_or_metadata": "metadata",
            },
        )

        response = client.post(labelvalue_url, data={"value": "Blue"})
        new_value_uuid = response.data["uuid"]

        metadata_relation_detail_url = reverse(
            "metadata-relationship-detail",
            kwargs={
                "project_uuid": self.project.uuid,
                "capture_uuid": self.capture.uuid,
                "uuid": md_relation_uuid,
            },
        )

        self.capture.refresh_from_db()
        version = self.capture.version
        response = client.patch(
            metadata_relation_detail_url,
            data={
                "label": self.label_uuid,
                "label_value": new_value_uuid,
                "uuid": md_relation_uuid,
            },
        )

        self.capture.refresh_from_db()
        assert self.capture.version == version + 1
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data[0]["label_value"]) == new_value_uuid

        response = client.get(relationship_url)
        clv_list = response.data
        assert len(clv_list) == 1

        response = client.delete(metadata_relation_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = client.get(relationship_url)
        clv_list = response.data
        assert len(clv_list) == 0

    def make_metadata_value(self, client):
        label_url = reverse(
            "label-list",
            kwargs={"project_uuid": self.project.uuid, "label_or_metadata": "metadata"},
        )

        response = client.post(
            label_url, data={"name": "MyLabel", "type": "string", "is_dropdown": True}
        )

        self.label_uuid = response.data["uuid"]

        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": self.label_uuid,
                "label_or_metadata": "metadata",
            },
        )
        response = client.post(labelvalue_url, data={"value": "Red"})

        self.labelvalue_uuid = response.data["uuid"]

    def test_project_metadata_relationship(self, client):
        for i in range(0, 4):
            label_uuid, labe_value_uuid = self.make_metadata_labelvalue(
                client, "label_{}".format(i)
            )

            CaptureMetadataValue.objects.create(
                project=self.project,
                capture=self.capture,
                label=Label.objects.get(uuid=label_uuid),
                label_value=LabelValue.objects.get(uuid=labe_value_uuid[0]),
            )

        label_url = reverse(
            "project-metadata-relationship-list",
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
                "created_at",
                "last_modified",
            ]
        )

    def test_project_metadata_relationship_delete_multi(self, client):
        cmv = []
        for i in range(0, 4):
            self.label_uuid, self.labelvalue_uuid = self.make_metadata_labelvalue(
                client, label_name="metadata_{}".format(i)
            )
            cmv.append(
                CaptureMetadataValue.objects.create(
                    project=self.project,
                    capture=self.capture,
                    label=Label.objects.get(uuid=self.label_uuid),
                    label_value=LabelValue.objects.get(uuid=self.labelvalue_uuid[0]),
                )
            )

        label_url = reverse(
            "relationship-delete",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_or_metadata": "metadata",
            },
        )

        response = client.post(
            label_url,
            data=json.dumps([str(x.uuid) for x in cmv]),
            content_type="application/json",
        )

        assert response.data == 4
