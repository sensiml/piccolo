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
import tempfile

import pytest
from datamanager.models import (
    Project,
    Sandbox,
    Team,
)
from django.conf import settings
from engine.base.cache_manager import CacheManager
from pandas import DataFrame
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


def test_health_check(client):
    response = client.get(reverse("health"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("authenticate")
def test_api_version(client):
    response = client.get(reverse("version"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("authenticate")
class TestCapture:
    """Test Capture CRUD API"""

    @pytest.fixture(autouse=True)
    def project(self, client, request):
        team = Team.objects.get(name=TEAM_NAME)

        return Project.objects.create(name="APITestProject", team=team)

    @pytest.mark.django_db(transaction=True)
    def test_capture(self, client, project):
        settings.DEBUG = True
        with tempfile.NamedTemporaryFile(mode="w+b", suffix=".csv") as f:
            f.write(b"AccelerometerX,AccelerometerY,GyroscopeZ\n1,2,3\n4,5,6\n7,8,9")
            f.seek(0)
            response = client.post(
                reverse("capture-list", kwargs={"project_uuid": project.uuid}),
                data={"name": "TestCapture", "file": f},
            )
        assert response.status_code == status.HTTP_201_CREATED
        capture_json = response.data

        capture_url = reverse(
            "capture-detail",
            kwargs={"project_uuid": project.uuid, "uuid": response.data.get("uuid")},
        )

        response = client.get(capture_url)
        assert response.status_code == status.HTTP_200_OK
        version = response.data.get("version")

        capture_json["capture_configuration_uuid"] = None
        for key in response.data.keys():
            # if key == 'last_modified':
            #    continue
            assert capture_json[key] == response.data[key]

        response = client.patch(capture_url, data={"name": "TestCapture2"})

        response = client.get(capture_url)
        assert response.data.get("name") == "TestCapture2"
        assert response.data.get("version") > version

        response = client.delete(capture_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_capture_delete_multiple(self, client, project):
        settings.DEBUG = True
        captures = []
        for i in range(0, 3):
            with tempfile.NamedTemporaryFile(mode="w+b", suffix=".csv") as f:
                f.write(
                    b"AccelerometerX,AccelerometerY,GyroscopeZ\n1,2,3\n4,5,6\n7,8,9"
                )
                f.seek(0)
                response = client.post(
                    reverse("capture-list", kwargs={"project_uuid": project.uuid}),
                    data={"name": "TestCapture{}".format(i), "file": f},
                )
                assert response.status_code == status.HTTP_201_CREATED
                captures.append(response.data["uuid"])

        for uuid in captures:
            url = reverse(
                "capture-detail",
                kwargs={"project_uuid": project.uuid, "uuid": uuid},
            )
            response = client.delete(url)
            assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.usefixtures("authenticate")
class TestLabel:
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

    def test_label_create_update_label(self, client):
        label_url = reverse(
            "label-list",
            kwargs={"project_uuid": self.project.uuid, "label_or_metadata": "metadata"},
        )

        response = client.post(
            label_url, data={"name": "MyLabel", "type": "string", "is_dropdown": True}
        )

        label_uuid = response.data["uuid"]

        assert response.status_code == status.HTTP_201_CREATED

        label_detail_url = reverse(
            "label-detail",
            kwargs={
                "project_uuid": self.project.uuid,
                "uuid": label_uuid,
                "label_or_metadata": "metadata",
            },
        )

        response = client.put(
            label_detail_url,
            data={"name": "Red", "type": "string", "is_dropdown": True},
        )

        assert response.status_code == status.HTTP_200_OK

        response = client.get(label_detail_url)

        assert response.data["name"] == "Red"
        assert response.data["type"] == "string"
        assert response.data["is_dropdown"] == True


@pytest.mark.usefixtures("authenticate")
class TestLabelValue:
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

    def test_labelvalue_create_update(self, client):
        label_url = reverse(
            "label-list",
            kwargs={"project_uuid": self.project.uuid, "label_or_metadata": "label"},
        )

        response = client.post(
            label_url,
            data={
                "name": "MyLabel",
                "type": "string",
                "is_dropdown": True,
                "color": "#FF0000",
            },
        )

        label_uuid = response.data["uuid"]

        assert response.status_code == status.HTTP_201_CREATED

        labelvalue_url = reverse(
            "labelvalue-list",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": label_uuid,
                "label_or_metadata": "metadata",
            },
        )

        response = client.post(
            labelvalue_url, data={"value": "Red", "color": "#FF0000"}
        )

        assert response.status_code == status.HTTP_201_CREATED

        labelvalue_uuid = response.data["uuid"]

        labelvalue_detail_url = reverse(
            "labelvalue-detail",
            kwargs={
                "project_uuid": self.project.uuid,
                "label_uuid": label_uuid,
                "label_or_metadata": "metadata",
                "uuid": labelvalue_uuid,
            },
        )

        response = client.get(labelvalue_detail_url)

        assert response.status_code == status.HTTP_200_OK

        assert response.data["value"] == "Red"
        assert response.data["color"] == "#FF0000"

        response = client.put(
            labelvalue_detail_url, data={"value": "Blue", "color": "#89CFF0"}
        )

        assert response.status_code == status.HTTP_200_OK

        assert response.data["value"] == "Blue"
        assert response.data["color"] == "#89CFF0"

        response = client.put(
            labelvalue_detail_url, data={"value": "Blue", "color": "---AA"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("authenticate")
class TestUser:
    @pytest.fixture(autouse=True)
    def setup(self, client, request):
        self.user = user = TeamMember.objects.get(email="sys_sensiml@sensiml.com").user
        client.force_authenticate(user=user)

    def test_get_team_subscription(self, client):
        response = client.get(reverse("team-subscription"))

        assert response.status_code == status.HTTP_200_OK

        assert len(response.json()) == 6

        data = response.json()

        assert data["team"] == "SensimlDevTeam"
        assert data["subscription"] == "ENTERPRISE"
        assert data["active"] == True
        assert data["expires"] == "2084-12-24T17:21:28Z"

        testuser = TeamMember.objects.get(email="unittest@starter.com").user
        client.force_authenticate(user=testuser)

        response = client.get(reverse("team-subscription"))

        assert response.status_code == status.HTTP_200_OK

        assert len(response.json()) == 6

        data = response.json()

        assert data["team"] == "StarterTeam"
        assert data["subscription"] == "STARTER"
        assert data["active"] == True
        assert data["expires"] == "2014-12-24T17:21:28Z"

        client.force_authenticate(user=self.user)

    def test_get_team_subscriptionv2(self, client):
        response = client.get(reverse("team-subscription-v2"))

        assert response.status_code == status.HTTP_200_OK

        assert len(response.json()) == 6

        data = response.json()

        assert data["team"] == "SensimlDevTeam"
        assert data["subscription"]["name"] == "ENTERPRISE"
        assert data["active"] == True
        assert data["subscription"]["is_read_only"] == False
        assert data["subscription"]["can_edit_offline"] == True
        assert data["subscription"]["max_project_segments"] == None
        assert data["expires"] == "2084-12-24T17:21:28Z"

        testuser = TeamMember.objects.get(email="unittest@starter.com").user
        client.force_authenticate(user=testuser)

        response = client.get(reverse("team-subscription-v2"))

        assert response.status_code == status.HTTP_200_OK

        assert len(response.json()) == 6

        data = response.json()

        assert data["team"] == "StarterTeam"
        assert data["subscription"]["name"] == "STARTER"
        assert data["subscription"]["uuid"] == "56eada75-e049-47bc-bf73-535b8666c91d"
        assert data["subscription"]["display_name"] == "Community Edition"
        assert data["subscription"]["is_read_only"] == False
        assert data["subscription"]["can_edit_offline"] == False
        assert data["subscription"]["max_project_segments"] == 2500
        assert data["active"] == True
        assert data["expires"] == "2014-12-24T17:21:28Z"

        client.force_authenticate(user=self.user)

    def test_get_options(self, client):
        response = client.options(reverse("user-list"))
        assert response.data["actions"]["POST"]["email"]["required"] == True
        assert response.data["actions"]["POST"]["password"]["required"] == True

    def test_create_user(self, client):
        data = {"email": "test@email.com", "password": "testpassword"}
        response = client.post(reverse("user-list"), data=data)
        assert response.status_code == status.HTTP_201_CREATED
        response = client.get(response.data["url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.data["team"] == TEAM_NAME
        TeamMember.objects.get(email="test@email.com")

    def test_create_user_with_new_team(self, client):
        data = {
            "email": "test@email.com",
            "password": "testpassword",
            "team": "new_team",
        }
        response = client.post(reverse("user-list"), data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["team"] == "new_team"
        # check team manager
        response.data["email"]
        response = client.get(reverse("team-list"))
        assert response.status_code == status.HTTP_200_OK
        team = next(
            (team for team in response.data if team["name"] == "new_team"), None
        )
        assert team is not None

    def test_modify_user_password(self, client):
        data = {"email": "test@email.com", "password": "testpassword"}
        response = client.post(reverse("user-list"), data=data)
        assert response.status_code == status.HTTP_201_CREATED
        response = client.patch(response.data["url"], data={"password": "newpassword"})
        assert response.status_code == status.HTTP_200_OK
        user = User.objects.get(email="test@email.com")
        assert user.check_password("newpassword")


class TestActivationCode:
    def test_activation_code_creation(self, client):
        response = client.post(
            reverse("activation-code"),
            data={
                "authentication": settings.ACTIVATION_CODE_AUTH,
                "code": "11111" * 5,
                "duration": "90 day",
                "subscription": "STARTER",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        act = ActivationCode.objects.get(code="11111" * 5)
        assert act.subscription.id == 1

    def test_activation_code_creation_no_duration(self, client):
        response = client.post(
            reverse("activation-code"),
            data={
                "authentication": settings.ACTIVATION_CODE_AUTH,
                "code": "11111" * 5,
                "subscription": "STARTER",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        act = ActivationCode.objects.get(code="11111" * 5)
        assert act.subscription.id == 1

    def test_activation_code_invalid(self, client):
        response = client.post(
            reverse("activation-code"),
            data={
                "authentication": settings.ACTIVATION_CODE_AUTH,
                "code": "11111",
                "duration": "90 day",
                "subscription": "STARTER",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_subsciption_invalid(self, client):
        response = client.post(
            reverse("activation-code"),
            data={
                "authentication": settings.ACTIVATION_CODE_AUTH,
                "code": "11111" * 5,
                "duration": "90 day",
                "subscription": "BLAH",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_authentication_invalid(self, client):
        response = client.post(
            reverse("activation-code"),
            data={
                "authentication": "555",
                "code": "11111" * 5,
                "duration": "90 day",
                "subscription": "BLAH",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSegmenterViews:
    @pytest.fixture(autouse=True)
    def setup(self, client, authenticate):
        from datamanager.models import Project, Segmenter

        self.project = Project.objects.create(name="Test", team_id=1)
        kwargs = {"project_uuid": self.project.uuid}
        self.list_url = reverse("segmenter-list", kwargs=kwargs)

        segmenter = Segmenter.objects.create(name="Test", project=self.project)
        kwargs.update({"pk": segmenter.id})
        self.detail_url = reverse("segmenter-detail", kwargs=kwargs)

    def test_get_segmenters(self, client):
        response = client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_segmenter_detail(self, client):
        response = client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

    def test_add_segmenter(self, client):
        response = client.post(self.list_url, data={"name": "Test Added Segmenter"})

        assert response.status_code == status.HTTP_201_CREATED

    def test_add_segmenter_with_params(self, client):
        response = client.post(
            self.list_url,
            data={
                "name": "Test Added Segmenter",
                "params": json.dumps({"input": {"test": 1}}),
                "preprocess": json.dumps(
                    {
                        1: {
                            "user_name": "MagnitudeGyroXYZ",
                            "actual_name": "Magnitude_ST_0001",
                            "params": "jsonblob",
                        }
                    }
                ),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.usefixtures("authenticate")
class TestAutomationEngine:
    """Test AutoML paramenter inventory request"""

    def test_get_iteration_results(self, client):
        project = Project.objects.create(name="Test", team_id=1)
        sandbox = Sandbox.objects.create(name="test", project=project)
        kwargs = {"project_uuid": project.uuid, "sandbox_uuid": sandbox.uuid}

        # save to cache
        df_test = DataFrame(columns=["test1", "test2"])
        df_test["test1"] = 10 * ["A"]
        df_test["test2"] = 10 * ["B"]

        cache_obj = CacheManager(sandbox, None)
        cache_obj.save_result_data(
            "test_data",
            str(sandbox.uuid),
            data=df_test.to_dict(),
        )

        parameter_url = reverse("iteration_results", kwargs=kwargs)
        response = client.get(parameter_url)

        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data == {}

        cache_obj.save_result_data(
            "fitted_population_log",
            str(sandbox.uuid),
            data=df_test.to_dict(),
        )

        parameter_url = reverse("iteration_results", kwargs=kwargs)
        response = client.get(parameter_url)

        data = DataFrame(response.json())

        assert response.status_code == status.HTTP_200_OK
        assert all(data.test1 == ["A"] * 10)
        assert all(data.test2 == ["B"] * 10)

    def test_get_pipeline_schema_rules(self, client):
        parameter_url = reverse("pipeline_schema_rules")
        response = client.get(parameter_url)
        assert response.status_code == status.HTTP_200_OK

        expected_keys = [
            "Name",
            "Next Step",
            "Mandatory",
            "TransformFilter",
            "TransformList",
            "Exclude",
            "Limit",
            "Set",
        ]
        for data in response.json():
            print(data)
            assert all([i in expected_keys for i in list(data.keys())])

            assert (data["TransformFilter"] is not None) or (
                data["TransformList"] is not None
            )
