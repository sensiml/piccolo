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
from datamanager.models import Project, Sandbox
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.fixture
def projects():
    project_dev = Project.objects.create(
        team_id=1,
        name="DevProject",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )

    project_dev_test = Project.objects.create(
        team_id=1,
        name="DevProjectTest",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )

    project_free = Project.objects.create(
        team_id=5,
        name="FreeProject",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )

    yield {"free": project_free, "dev": project_dev}

    project_free.delete()
    project_dev.delete()
    project_dev_test.delete()


@pytest.mark.usefixtures("authenticate")
def test_create_sandbox(client, projects):
    project = projects["dev"]

    data = {
        "name": "TestSadnbox",
        "pipeline": [{"name": "test"}],
        "steps": [],
        "cache_enabled": True,
        "hyper_params": {
            "seed": "Custom",
            "disable_automl": False,
            "params": {
                "reset": True,
                "set_training_algorithm": {"Random Forest": {}, "xGBoost": {}},
            },
        },
        "device_config": {"target_platform": 0},
    }

    response = client.post(
        reverse("sandbox-list", kwargs={"project_uuid": project.uuid}),
        data=data,
        format="json",
    )

    assert response.data.get("hyper_params") == data.get("hyper_params")
    assert response.status_code == status.HTTP_200_OK

    assert "uuid" in response.data

    sandbox = response.data

    response = client.get(
        reverse("sandbox-list", kwargs={"project_uuid": project.uuid})
    )

    assert response.status_code == status.HTTP_200_OK

    response = client.get(
        reverse(
            "sandbox-detail",
            kwargs={"project_uuid": project.uuid, "uuid": sandbox.get("uuid")},
        )
    )

    assert response.status_code == status.HTTP_200_OK

    url = reverse("sandbox-list", kwargs={"project_uuid": project.uuid})
    response = client.get(f"{url}?fields[]=uuid&fields[]=name")

    assert response.json() == [{"uuid": sandbox.get("uuid"), "name": "TestSadnbox"}]

    assert response.status_code == status.HTTP_200_OK

    url = reverse(
        "sandbox-detail",
        kwargs={"project_uuid": project.uuid, "uuid": sandbox.get("uuid")},
    )
    response = client.get(f"{url}?fields[]=uuid&fields[]=name&fields[]=cache")

    assert response.json() == {
        "uuid": sandbox.get("uuid"),
        "name": "TestSadnbox",
        "cache": None,
    }

    assert response.status_code == status.HTTP_200_OK

    data = {
        "name": "TestSandbox2",
        "pipeline": [{"name": "test"}],
        "steps": [],
        "cache_enabled": True,
        "device_config": {"target_platform": 0},
        "hyper_params": {
            "seed": "Custom",
            "disable_automl": True,
            "params": {
                "reset": True,
                "set_training_algorithm": {
                    "Univariate Selection": {},
                    "Tree-based Selection": {},
                },
            },
        },
    }

    response = client.patch(
        reverse(
            "sandbox-detail",
            kwargs={"project_uuid": project.uuid, "uuid": sandbox.get("uuid")},
        ),
        data=data,
        format="json",
    )
    assert response.data.get("name") == "TestSandbox2"
    assert response.data.get("hyper_params") == data.get("hyper_params")

    sandbox_obj = Sandbox.objects.get(uuid=sandbox.get("uuid"))
    sandbox_obj.active = True
    sandbox_obj.save()

    response = client.patch(
        reverse(
            "sandbox-detail",
            kwargs={"project_uuid": project.uuid, "uuid": sandbox.get("uuid")},
        ),
        data=data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.delete(
        reverse(
            "sandbox-detail",
            kwargs={"project_uuid": project.uuid, "uuid": sandbox.get("uuid")},
        )
    )

    sandbox_obj.active = False
    sandbox_obj.save()

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.delete(
        reverse(
            "sandbox-detail",
            kwargs={"project_uuid": project.uuid, "uuid": sandbox.get("uuid")},
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.usefixtures("authenticate")
def test_create_sandbox_same_name(client, projects):
    project = projects["dev"]

    data = {
        "name": "TestSadnbox",
        "pipeline": [{"name": "test"}],
        "steps": [],
        "cache_enabled": True,
        "device_config": {"target_platform": 0},
    }

    response = client.post(
        reverse("sandbox-list", kwargs={"project_uuid": project.uuid}),
        data=data,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    response = client.post(
        reverse("sandbox-list", kwargs={"project_uuid": project.uuid}),
        data=data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("authenticate")
def test_create_sandbox_too_many_features(client, projects):
    project = projects["dev"]

    data = {
        "name": "TestSadnbox",
        "pipeline": [{"name": "generator_set", "set": list(range(300))}],
        "steps": [],
        "cache_enabled": True,
        "device_config": {"target_platform": 0},
    }

    response = client.post(
        reverse("sandbox-list", kwargs={"project_uuid": project.uuid}),
        data=data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("authenticate")
def test_generate_python_code(client, test_projects_with_pipelines):
    from django.core.management import call_command

    call_command("load_functions")

    project = test_projects_with_pipelines

    feature_cascade_pipeline = Sandbox.objects.get(
        project=project,
        name="feature_file_pipeline_cascasde",
    )

    response = client.get(
        reverse(
            "sandbox-to-python",
            kwargs={
                "project_uuid": project.uuid,
                "sandbox_uuid": feature_cascade_pipeline.uuid,
            },
        ),
    )

    assert response.status_code == 200

    # Check if the response content type is set correctly to 'application/octet-stream'
    assert response.get("Content-Type") == "application/octet-stream"

    # Check if the Content-Disposition header is set with the correct filename
    assert (
        response.get("Content-Disposition")
        == f'attachment; filename="{feature_cascade_pipeline.name}.py"'
    )


@pytest.mark.usefixtures("authenticate")
def test_generate_ipynb_code(client, test_projects_with_pipelines):
    from django.core.management import call_command

    call_command("load_functions")

    project = test_projects_with_pipelines

    feature_cascade_pipeline = Sandbox.objects.get(
        project=project,
        name="feature_file_pipeline_cascasde",
    )

    response = client.get(
        reverse(
            "sandbox-to-ipynb",
            kwargs={
                "project_uuid": project.uuid,
                "sandbox_uuid": feature_cascade_pipeline.uuid,
            },
        ),
    )

    assert response.status_code == 200

    # Check if the response content type is set correctly to 'application/octet-stream'
    assert response.get("Content-Type") == "application/octet-stream"

    # Check if the Content-Disposition header is set with the correct filename
    assert (
        response.get("Content-Disposition")
        == f'attachment; filename="{feature_cascade_pipeline.name}.ipynb"'
    )


def test_sandbox_async_cpu_validation(projects):
    client = APIClient()
    client.login(username="unittest@starter.com", password="TinyML4Life")
    project = Project.objects.create(
        team_id=2,
        name="DevProject",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )
    sandbox = Sandbox.objects.create(
        project=project,
        name="TestPipeline",
        uuid="00000000-0000-0000-0000-000000000000",
        cpu_clock_time=100,
        active=True,
    )

    response = client.post(
        reverse(
            "sandbox-async", kwargs={"project_uuid": project.uuid, "uuid": sandbox.uuid}
        ),
        data={"execution_type": "pipeline"},
        format="json",
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = client.post(
        reverse(
            "sandbox-async", kwargs={"project_uuid": project.uuid, "uuid": sandbox.uuid}
        ),
        data={"execution_type": "pipeline"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
