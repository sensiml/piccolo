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
import logging
import os

import pytest
from datamanager.models import (
    Capture,
    CaptureLabelValue,
    Label,
    Project,
    Segmenter,
    Team,
)

from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.fixture
def project():
    team = Team.objects.get(name=TEAM_NAME)
    project = Project.objects.create(
        name="APITestProject",
        team=team,
    )

    yield project

    project.delete()


@pytest.fixture
def project_small_resources():
    team = Team.objects.get(name=TEAM_NAME)

    project = Project.objects.create(
        name="APITestProject",
        team=team,
    )

    yield project

    project.delete()


@pytest.fixture()
def segments_capture_label_values(testprojects):
    capture_length = 25
    project = testprojects["dev"]
    project_captures = Capture.objects.filter(project=project)
    labels = Label.objects.filter(project=project)

    segmenter = Segmenter.objects.create(project=project, name="Manual1", custom=True)

    for index, capture in enumerate(project_captures):
        delta = 5 // (index + 1)
        for i in range(0, capture_length - delta, delta):
            for label in labels:
                for label_value in label.label_values.all():
                    CaptureLabelValue.objects.create(
                        project=project,
                        capture=capture,
                        label=label,
                        label_value=label_value,
                        segmenter=segmenter,
                        capture_sample_sequence_start=i,
                        capture_sample_sequence_end=i + delta,
                    )


@pytest.mark.usefixtures("authenticate")
class TestCapture:
    def test_create_wav(self, client, project):
        project.save()
        settings.DEBUG = True

        capture_list_url = reverse(
            "capture-list",
            kwargs={"project_uuid": project.uuid},
        )

        dirname = os.path.dirname(__file__)

        template_path = os.path.join(dirname, "data/on_4c77947d_nohash_0.wav")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "test.wav"},
            )

        assert response.json()["name"] == "test.wav"
        assert response.json()["max_sequence"] == 10922
        assert response.json()["file_size"] == 21890
        assert response.json()["number_samples"] == 10923

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_csv(self, client, project):
        project.save()
        settings.DEBUG = True

        capture_list_url = reverse(
            "capture-list",
            kwargs={"project_uuid": project.uuid},
        )

        dirname = os.path.dirname(__file__)

        template_path = os.path.join(dirname, "data/window_test.csv")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "window_test.wav"},
            )

        assert response.json()["name"] == "window_test.wav"
        assert response.json()["max_sequence"] == 11999
        assert response.json()["file_size"] == 278975
        assert response.json()["number_samples"] == 12000

        assert response.status_code == status.HTTP_201_CREATED

        capture_file_urls = reverse(
            "capture-files",
            kwargs={"project_uuid": project.uuid},
        )

        response = client.post(
            capture_file_urls,
            data={"capture_uuids": [response.json()["uuid"]]},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    def test_create_csv_with_packet_loss(self, client, project):
        project.save()
        settings.DEBUG = True

        capture_list_url = reverse(
            "capture-list",
            kwargs={"project_uuid": project.uuid},
        )

        dirname = os.path.dirname(__file__)

        template_path = os.path.join(dirname, "data/packet_loss.csv")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "test_packet.csv"},
            )

        assert response.status_code == status.HTTP_201_CREATED

        r = response.json()

        assert r["max_sequence"] == 1120
        assert r["number_samples"] == 99
        assert r["name"] == "test_packet.csv"
        assert r["file_size"] == 2943

    def test_create_csv_then_upload_wave(self, client, project):
        project.save()
        settings.DEBUG = True

        capture_list_url = reverse(
            "capture-list",
            kwargs={"project_uuid": project.uuid},
        )

        dirname = os.path.dirname(__file__)

        template_path = os.path.join(dirname, "data/window_test.csv")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "window_test.wav"},
            )
        assert response.status_code == status.HTTP_201_CREATED

        settings.ALLOW_UPDATE_PROJECT_SCHEMA = True

        template_path = os.path.join(dirname, "data/on_4c77947d_nohash_0.wav")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "window_test.wav"},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "status": 400,
            "detail": "Request failed validation",
            "data": {
                "name": [
                    "Project already contains a file with the name window_test.wav"
                ]
            },
        }

        settings.ALLOW_UPDATE_PROJECT_SCHEMA = False

        template_path = os.path.join(dirname, "data/on_4c77947d_nohash_0.wav")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "window_test_2.wav"},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "status": 400,
            "detail": "Request failed validation",
            "data": [
                "Uploaded file does not match project schema ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'GyroscopeX', 'GyroscopeY', 'GyroscopeZ', 'channel_0']. The uploaded file schema is: ['channel_0']"
            ],
        }

        settings.ALLOW_UPDATE_PROJECT_SCHEMA = True

        template_path = os.path.join(dirname, "data/on_4c77947d_nohash_0.wav")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "window_test_2.wav"},
            )

        assert response.status_code == status.HTTP_201_CREATED

        response = client.get(reverse("project-detail", kwargs={"uuid": project.uuid}))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["capture_sample_schema"] == {
            "channel_0": {"type": "int", "index": 0},
            "GyroscopeX": {"type": "int", "index": 3},
            "GyroscopeY": {"type": "int", "index": 4},
            "GyroscopeZ": {"type": "int", "index": 5},
            "AccelerometerX": {"type": "int", "index": 0},
            "AccelerometerY": {"type": "int", "index": 1},
            "AccelerometerZ": {"type": "int", "index": 2},
        }

    def test_capture_stats_api_base(
        self, client, testprojects, segments_capture_label_values
    ):
        url = reverse(
            "captures-stats",
            kwargs={"project_uuid": testprojects["dev"].uuid},
        )
        response = client.get(url)
        response_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        for item in response_json:
            capture = Capture.objects.get(uuid=item["uuid"])
            assert (
                item["total_events"]
                == CaptureLabelValue.objects.filter(capture=capture).count()
            )

    def test_capture_stats_api_with_segment_filter(
        self, client, testprojects, segments_capture_label_values
    ):
        """
        test api with segmenter filter
        """
        url = reverse(
            "captures-stats",
            kwargs={"project_uuid": testprojects["dev"].uuid},
        )
        segmenters = Segmenter.objects.filter(project=testprojects["dev"].id)
        for segmenter in segmenters:
            response = client.get(f"{url}?segmenter={segmenter.id}")
            response_json = response.json()

            assert response.status_code == status.HTTP_200_OK
            for item in response_json:
                capture = Capture.objects.get(uuid=item["uuid"])
                assert (
                    item["total_events"]
                    == CaptureLabelValue.objects.filter(
                        capture=capture, segmenter=segmenter
                    ).count()
                )
