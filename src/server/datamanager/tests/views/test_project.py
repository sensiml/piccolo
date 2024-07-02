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

import logging

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.fixture
def project_with_capture_video(testprojects):
    from datamanager.models import Capture, CaptureVideo

    dev_test_project = testprojects["dev"]

    test_capture = Capture.objects.filter(project=dev_test_project).first()
    test_capture_video = CaptureVideo.objects.create(
        capture=test_capture, name="video_test1.mp4", file_size=3123456
    )

    yield dev_test_project, test_capture_video

    test_capture_video.delete()


@pytest.mark.usefixtures("authenticate")
class TestProject:
    def test_project(self, client):
        response = client.post(
            reverse("project-list"), data=dict(name="APITestProject")
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "uuid" in response.data
        assert "settings" in response.data
        project = response.data

        response = client.get(reverse("project-list"))
        assert response.status_code == status.HTTP_200_OK

        response = client.get(
            reverse("project-detail", kwargs={"uuid": project.get("uuid")})
        )
        assert response.status_code == status.HTTP_200_OK
        assert project["uuid"] == response.data["uuid"]
        project_last_modified = response.data["last_modified"]

        response = client.patch(
            reverse("project-detail", kwargs={"uuid": project.get("uuid")}),
            data={"name": "APITestProject2"},
        )
        assert response.data.get("name") == "APITestProject2"
        assert response.data.get("last_modified") > project_last_modified

        response = client.delete(
            reverse("project-detail", kwargs={"uuid": project.get("uuid")})
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_project_validate_names(self, client):
        response = client.post(
            reverse("project-list"), data=dict(name="APITestProject")
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "uuid" in response.data
        assert "settings" in response.data

        response = client.post(
            reverse("project-list"), data=dict(name="abc_DEF123- RED")
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "uuid" in response.data
        assert "settings" in response.data

        response = client.post(
            reverse("project-list"), data=dict(name="abc_DEF123- RED!")
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(
            reverse("project-list"), data=dict(name="abc_DEF123- RED?")
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(
            reverse("project-list"), data=dict(name="abc_DEF123- RED:")
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(
            reverse("project-list"), data=dict(name="abc_DEF123- RED/")
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(
            reverse("project-list"), data=dict(name="abc_DEF123- RED\\")
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(
            reverse("project-list"), data=dict(name="abc_DEF123- RED*")
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(
            reverse("project-list"), data=dict(name="abc_DEF123- RED|")
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db(transaction=True)
    def test_project_post_capture_schema(self, client, testprojects):
        response = client.get(reverse("project-list"))

        result = response.json()

        assert response.status_code == status.HTTP_200_OK

        response = client.patch(
            reverse("project-detail", kwargs={"uuid": result[0]["uuid"]}),
            data={"name": "APITestProject2", "capture_sample_schema": {"red": 1}},
            format="json",
        )

        assert response.json()["capture_sample_schema"] == {
            "Column1": {"type": "float", "index": 0},
            "Column2": {"type": "float", "index": 1},
        }

        assert response.json()["name"] == "APITestProject2"

    def test_get_project_summary(
        self, client, testprojects, project_with_capture_video
    ):
        response = client.get(reverse("project-summary"))
        assert response.status_code == status.HTTP_200_OK

        assert len(response.data) == 2
        result = response.data[0]
        assert result["name"] == "DevProject"
        assert result["files"] == 3
        assert result["size_mb"] == 3.0
        assert result["pipelines"] == 2
        assert result["queries"] == 6
        assert result["models"] == 4
        assert result["videos"] == 1
        assert result["video_size_mb"] == 2.98
        assert result["segments"] == 12

        result = response.data[1]
        assert result["name"] == "DevProjectTest"
        assert result["files"] == 0
        assert result["size_mb"] == 0.00
        assert result["pipelines"] == 0
        assert result["queries"] == 0
        assert result["models"] == 0
        assert result["videos"] == 0
        assert result["video_size_mb"] == 0.00
        assert result["segments"] == 0

    def test_get_project_summary_by_uuid(self, client, project_with_capture_video):
        test_project, test_capture_video = project_with_capture_video

        response = client.get(
            reverse("project-summary-detail", kwargs={"uuid": test_project.uuid})
        )

        assert response.status_code == status.HTTP_200_OK

        result = response.data
        assert result["name"] == "DevProject"
        assert result["files"] == 3
        assert result["size_mb"] == 3.0
        assert result["pipelines"] == 2
        assert result["queries"] == 6
        assert result["models"] == 4
        assert result["videos"] == 1
        assert result["video_size_mb"] == round(
            test_capture_video.file_size / (1024**2), 2
        )

        assert result["segments"] == 12

    def test_get_project_dcli(self, client, testprojects):
        project_uuid = testprojects["dev"].uuid

        response = client.get(reverse("dcli", kwargs={"project_uuid": project_uuid}))

        assert response.status_code == status.HTTP_200_OK

        result = response.json()

        expected_result = [
            {
                "file_name": "TestCapture0",
                "metadata": [{"name": "Subject", "value": "John"}],
                "sessions": [
                    {
                        "session_name": "Manual",
                        "segments": [
                            {"name": "Event", "value": "A", "start": 0, "end": 5},
                            {"name": "Event", "value": "A", "start": 5, "end": 10},
                            {"name": "Event", "value": "A", "start": 10, "end": 15},
                            {"name": "Event", "value": "A", "start": 15, "end": 20},
                        ],
                    }
                ],
            },
            {
                "file_name": "TestCapture1",
                "metadata": [{"name": "Subject", "value": "Emily"}],
                "sessions": [
                    {
                        "session_name": "Manual",
                        "segments": [
                            {"name": "Event", "value": "B", "start": 0, "end": 5},
                            {"name": "Event", "value": "B", "start": 5, "end": 10},
                            {"name": "Event", "value": "B", "start": 10, "end": 15},
                            {"name": "Event", "value": "B", "start": 15, "end": 20},
                        ],
                    }
                ],
            },
            {
                "file_name": "TestCapture2",
                "metadata": [{"name": "Subject", "value": "Emily"}],
                "sessions": [
                    {
                        "session_name": "Manual",
                        "segments": [
                            {"name": "Event", "value": "C", "start": 0, "end": 5},
                            {"name": "Event", "value": "C", "start": 5, "end": 10},
                            {"name": "Event", "value": "C", "start": 10, "end": 15},
                            {"name": "Event", "value": "C", "start": 15, "end": 20},
                        ],
                    }
                ],
            },
        ]

        assert len(result) == len(expected_result)


@pytest.mark.usefixtures("authenticate")
@pytest.mark.django_db(transaction=True)
def test_get_project_summary(client, testprojects):
    # still have the api make sure it still behaves the same, even though its deprecated

    project = testprojects["dev"]

    assert project.optimized == False

    response = client.post(reverse("project-profile", kwargs={"uuid": project.uuid}))

    project.refresh_from_db()

    assert project.optimized
    response = client.delete(reverse("project-profile", kwargs={"uuid": project.uuid}))

    project.refresh_from_db()
    assert project.optimized == False


@pytest.mark.usefixtures("authenticate")
@pytest.mark.django_db(transaction=True)
class TestProjectImageView:
    def test_get_default_project_image(self, client, testprojects):
        project = testprojects["dev"]
        assert project.image_file_name == None
        response = client.get(reverse("project-image", kwargs={"uuid": project.uuid}))

        # Look for the existence of an index
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == "/static/images/noimage_icon.png"

    def test_get_actual_project_image(self, client, testprojects):
        project = testprojects["dev"]
        project.image_file_name = "test_image.png"
        project.save()

        response = client.get(reverse("project-image", kwargs={"uuid": project.uuid}))

        # Look for the existence of an index
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == "/static/projectimages/test_image.png"


@pytest.mark.skip("used for profiling only")
@pytest.mark.usefixtures("authenticate")
def test_get_project_summary_profile(client, testprojects_profile):
    response = client.get(reverse("project-summary"))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse("project-summary"))
    assert len(response.data) == 2000
