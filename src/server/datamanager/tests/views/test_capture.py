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

    def test_create_csv_with_timestamp(self, client, project):
        project.save()
        settings.DEBUG = True

        capture_list_url = reverse(
            "capture-list",
            kwargs={"project_uuid": project.uuid},
        )

        dirname = os.path.dirname(__file__)

        template_path = os.path.join(dirname, "data/packet_loss_with_timestamp.csv")
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
        assert r["file_size"] == 3151

        from datamanager.query import get_capture_file

        capture = Capture.objects.get(name="test_packet.csv")
        capture_df = get_capture_file(project.uuid, capture.file, ".csv")
        assert "timestamp" not in capture_df.columns

        from engine.base import pipeline_utils
        from datamanager.models import TeamMember

        user = TeamMember.objects.get(email="unittest@sensiml.com").user
        capture_df_pipeline_utils, _, _ = pipeline_utils.get_capturefile(
            user, project.uuid, capture.name
        )

        assert "timestamp" not in capture_df_pipeline_utils.columns

        capture_list_url = reverse(
            "capture-file",
            kwargs={"project_uuid": project.uuid, "uuid": capture.uuid},
        )

        response = client.get(capture_list_url)

        assert (
            response.data
            == b"timestamp,sequence,AccelerometerX,AccelerometerY,AccelerometerZ,GyroscopeX,GyroscopeY,GyroscopeZ\r\nr,1000,-158,313,4173,0,-2,-226\r\nr,1001,-146,368,4192,15,-5,-332\r\nr,1002,-282,278,4120,-93,56,-408\r\nr,1003,-332,179,4159,-19,14,-333\r\nr,1004,-181,170,4166,29,-13,-153\r\nr,1005,-148,154,4175,12,0,-51\r\nr,1006,-197,234,4166,9,-1,-8\r\nr,1007,-225,263,4160,10,-3,1\r\nr,1008,-218,252,4154,10,-2,-1\r\nr,1009,-215,254,4159,10,-3,-1\r\nr,1010,-221,248,4180,9,-2,-1\r\nr,1011,-217,250,4166,10,-4,-4\r\nr,1012,-215,255,4165,9,-3,-3\r\nr,1013,-217,256,4169,9,-2,-2\r\nr,1014,-215,262,4163,10,-3,-2\r\nr,1015,-213,264,4177,11,-2,-2\r\nr,1016,-214,255,4161,10,-2,-2\r\nr,1017,-213,248,4163,10,-2,-1\r\nr,1018,-218,250,4172,10,-3,-1\r\nr,1019,-211,254,4169,11,-4,-1\r\nr,1020,-213,256,4169,10,-2,-3\r\nr,1021,-220,250,4158,10,-3,-2\r\nr,1022,-212,258,4168,10,-3,-2\r\nr,1023,-202,257,4169,9,-2,-2\r\nr,1024,-210,258,4161,9,-3,-2\r\nr,1025,-215,256,4165,10,-4,-3\r\nr,1026,-213,256,4163,11,-1,-2\r\nr,1027,-210,256,4169,10,-2,-1\r\nr,1028,-216,257,4164,9,-2,-1\r\nr,1029,-217,253,4167,10,-1,-3\r\nr,1030,-215,260,4171,11,-1,-2\r\nr,1031,-213,255,4174,11,-3,0\r\nr,1032,-214,256,4164,9,-3,-1\r\nr,1033,-211,253,4169,8,-3,-2\r\nr,1034,-209,253,4163,9,-2,-2\r\nr,1035,-215,253,4159,9,-2,-2\r\nr,1036,-215,253,4166,10,-4,-2\r\nr,1037,-214,258,4161,11,-4,-2\r\nr,1038,-213,256,4163,10,-3,-1\r\nr,1039,-211,256,4163,10,-3,-2\r\nr,1040,-212,255,4164,9,-2,-1\r\nr,1041,-218,256,4172,9,-3,0\r\nr,1042,-215,253,4171,10,-4,0\r\nr,1043,-211,253,4164,10,-1,-1\r\nr,1044,-215,260,4158,11,-2,-2\r\nr,1045,-212,248,4169,10,-3,-3\r\nr,1046,-213,256,4162,11,-2,-1\r\nr,1047,-214,259,4160,10,-3,-1\r\nr,1048,-217,256,4161,10,-4,-1\r\nr,1049,-217,254,4175,11,-4,-2\r\nr,1050,-210,256,4172,11,-4,-3\r\nr,1051,-211,264,4162,10,-4,-3\r\nr,1052,-210,259,4163,10,-3,-1\r\nr,1053,-205,253,4168,9,-3,0\r\nr,1054,-221,250,4164,10,-2,-2\r\nr,1055,-221,255,4156,10,-3,-3\r\nr,1056,-213,259,4162,10,-2,-1\r\nr,1057,-218,254,4176,10,-2,-1\r\nr,1058,-216,250,4167,9,-2,-1\r\nr,1059,-206,257,4165,9,-2,-3\r\nr,1060,-212,255,4161,10,-1,-1\r\nr,1061,-214,252,4173,10,-2,-2\r\nr,1062,-217,255,4188,10,-2,-2\r\nr,1063,-224,255,4191,10,-2,-1\r\nr,1064,-218,258,4180,9,-2,-3\r\nr,1065,-221,256,4157,9,-3,-1\r\nr,1066,-208,258,4147,10,-4,-1\r\nr,1067,-211,257,4157,10,-2,-1\r\nr,1068,-214,257,4166,10,-2,-2\r\nr,1069,-209,253,4181,10,-2,-2\r\nr,1070,-213,256,4179,12,-1,-2\r\nr,1071,-212,257,4168,11,-3,-2\r\nr,1072,-205,255,4155,9,-3,-1\r\nr,1073,-215,261,4162,11,-2,-1\r\nr,1074,-223,261,4168,10,-2,-2\r\nr,1075,-212,264,4175,10,-2,-1\r\nr,1076,-217,257,4187,9,-2,-2\r\nr,1077,-214,258,4184,10,-4,-2\r\nr,1078,-220,264,4171,9,-3,-2\r\nr,1079,-211,284,4164,10,-2,-11\r\nr,1080,-206,268,4163,11,-2,-58\r\nr,1081,-222,233,4155,10,-4,-66\r\nr,1082,-217,252,4164,11,-3,-17\r\nr,1083,-214,261,4173,10,-3,3\r\nr,1084,-217,258,4181,10,-3,-2\r\nr,1086,-210,258,4171,10,-3,-2\r\nr,1087,-203,253,4158,9,-2,-2\r\nr,1088,-209,249,4167,10,-3,-2\r\nr,1089,-215,252,4173,10,-2,-1\r\nr,1090,-219,263,4172,10,-3,-1\r\nr,1092,-205,258,4184,11,-4,0\r\nr,1093,-211,261,4163,10,-3,-1\r\nr,1094,-219,258,4166,10,-4,-2\r\nr,1095,-217,251,4162,10,-3,-3\r\nr,1096,-213,257,4164,10,-3,-2\r\nr,1097,-210,254,4168,9,-4,-3\r\nr,1098,-224,252,4169,10,-2,-2\r\nr,1099,-219,261,4173,11,-3,-2\r\nr,1120,-212,263,4167,10,-3,-3"
        )

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

        template_path = os.path.join(dirname, "data/on_4c77947d_nohash_0.wav")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "window_test2.wav"},
            )

        assert response.status_code == status.HTTP_201_CREATED

        project.lock_schema = True
        project.save(update_fields=["lock_schema"])

        template_path = os.path.join(dirname, "data/on_4c77947d_nohash_0.wav")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "window_test_3.wav"},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "status": 400,
            "detail": "Request failed validation",
            "data": [
                "Uploaded file does not match project schema ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'GyroscopeX', 'GyroscopeY', 'GyroscopeZ', 'channel_0']. The uploaded file schema is: ['channel_0']"
            ],
        }

        project.lock_schema = False
        project.save(update_fields=["lock_schema"])

        template_path = os.path.join(dirname, "data/on_4c77947d_nohash_0.wav")
        with open(template_path, "rb") as f:
            response = client.post(
                capture_list_url,
                format="multipart",
                data={"file": f, "name": "window_test_4.wav"},
            )

        assert response.status_code == status.HTTP_201_CREATED

        response = client.get(reverse("project-detail", kwargs={"uuid": project.uuid}))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["capture_sample_schema"] == {
            "channel_0": {"type": "int"},
            "GyroscopeX": {"type": "int"},
            "GyroscopeY": {"type": "int"},
            "GyroscopeZ": {"type": "int"},
            "AccelerometerX": {"type": "int"},
            "AccelerometerY": {"type": "int"},
            "AccelerometerZ": {"type": "int"},
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
