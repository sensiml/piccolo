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
import json

from time import sleep

import pytest
from datamanager.models import (
    Capture,
    CaptureVideo,
)

from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.fixture
def project_with_capture_videos(test_project_with_capture):
    test_project, test_capture1 = test_project_with_capture

    test_capture2 = Capture.objects.create(
        project=test_project,
        name="TestCaptureB.csv",
        format=".csv",
        file_size=1048576,
        max_sequence=10,
        number_samples=10,
        file="testtest",
    )

    capture_video1 = CaptureVideo.objects.create(
        capture=test_capture1, name="video_test1.mp4", file_size=1570024
    )
    capture_video2 = CaptureVideo.objects.create(
        capture=test_capture2, name="video_test2.mp4", file_size=1570024
    )

    yield test_project, test_capture1, test_capture2, capture_video1, capture_video2

    test_capture1.delete()
    test_capture2.delete()


@pytest.mark.usefixtures("authenticate")
class TestCaptureVideo:
    def test_list_capture_videos(self, client, project_with_capture_videos):
        (
            test_project,
            test_capture1,
            test_capture2,
            capture_video1,
            capture_video2,
        ) = project_with_capture_videos
        settings.DEBUG = True

        capture_video_list_url = reverse(
            "capture-video-list",
            kwargs={
                "project_uuid": test_project.uuid,
                "capture_uuid": test_capture1.uuid,
            },
        )
        response = client.get(capture_video_list_url)
        assert len(response.json()) == 1
        assert response.json()[0]["uuid"] == str(capture_video1.uuid)

        base_url = reverse(
            "capture-video-bulk-list",
            kwargs={
                "project_uuid": test_project.uuid,
            },
        )
        response_bulk_list_one = client.get(
            f"{base_url}?capture_uuids[]={test_capture1.uuid}"
        )
        assert len(response_bulk_list_one.json()) == 1
        assert response.json()[0]["uuid"] == str(capture_video1.uuid)

        response_bulk_list_two = client.get(
            f"{base_url}?capture_uuids[]={test_capture1.uuid}&capture_uuids[]={test_capture2.uuid}"
        )
        assert len(response_bulk_list_two.json()) == 2

    def test_upload_success(self, client, test_project_with_capture):
        test_project, test_capture = test_project_with_capture
        settings.DEBUG = True

        capture_video_list_url = reverse(
            "capture-video-list",
            kwargs={
                "project_uuid": test_project.uuid,
                "capture_uuid": test_capture.uuid,
            },
        )

        video_path = os.path.join(os.path.dirname(__file__), "data/video_test.mp4")
        keypoints = json.dumps({"test": "test"})
        with open(video_path, "rb") as f:
            response = client.post(
                capture_video_list_url,
                format="multipart",
                data={"file": f, "name": "video_test.mp4", "keypoints": keypoints},
            )

        assert response.json()["name"] == "video_test.mp4"
        assert response.json()["file_size"] == 1570024
        assert response.json()["keypoints"] == json.loads(keypoints)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db(transaction=True)
    def test_changing_capture_fields(self, client, test_project_with_capture):
        _test_project, test_capture = test_project_with_capture

        capture_last_modified_video_before = test_capture.last_modified_video
        capture_video = CaptureVideo.objects.create(
            capture=test_capture, name="video_test.mp4", file_size=1570024
        )
        assert test_capture.last_modified_video is not None
        assert capture_last_modified_video_before != test_capture.last_modified_video
        assert capture_video.last_modified == test_capture.last_modified_video

        sleep(1)
        capture_last_modified_video_before_snd = test_capture.last_modified_video
        capture_video_snd = CaptureVideo.objects.create(
            capture=test_capture, name="video_test1.mp4", file_size=1570024
        )
        assert test_capture.last_modified_video > capture_last_modified_video_before_snd

        sleep(1)
        capture_last_modified_video_after_snd = test_capture.last_modified_video
        # first video delete should not change
        capture_video.delete()
        assert test_capture.last_modified_video == capture_last_modified_video_after_snd

        sleep(1)
        # second video delete should not change
        capture_video_snd.delete()
        assert test_capture.last_modified_video is None
