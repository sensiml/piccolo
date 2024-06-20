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
from unittest.mock import patch

import pandas as pd
import pytest
from datamanager.models import FeatureFile, Project, Team
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.fixture
def project():
    project = Project.objects.create(
        name="APITestProject",
        team=Team.objects.get(name=TEAM_NAME),
    )

    return project


@pytest.fixture
def featurefile(project):
    featurefile = FeatureFile.objects.create(
        name="TestFile",
        project=project,
        format=".data_0.csv.gz",
        path="",
        is_features=True,
    )
    return featurefile


def mock_s3_data():
    return pd.Series({"Label": ["Test1", "Test2", "Test3", "Test4", "Test5", "Test6"]})


@pytest.mark.usefixtures("authenticate")
@patch("datamanager.datastore.LocalDataStoreService.get_data")
class TestFeatureFileWithS3Mock:
    def test_feature_file_json(self, mocks_s3, client, project, featurefile):
        mocks_s3.return_value = mock_s3_data()
        feature_file_json_url = reverse(
            "feature-file-json",
            kwargs={
                "project_uuid": project.uuid,
                "uuid": featurefile.uuid,
            },
        )
        response = client.get(feature_file_json_url)

        assert len(mocks_s3.call_args_list) == 1
        assert len(mocks_s3.call_args_list[0][0]) == 1
        assert mocks_s3.call_args_list[0][0][0] == "{}.data_0.csv.gz".format(
            str(featurefile.uuid)
        )

        expected_result = b'{"Label":["Test1","Test2","Test3","Test4","Test5","Test6"]}'

        assert response.status_code == status.HTTP_200_OK
        assert response.content == expected_result


@pytest.mark.usefixtures("authenticate")
class TestFeatureFile:
    def test_create_featurefile(self, client, project):
        settings.DEBUG = True

        featurefile_list_url = reverse(
            "feature-file",
            kwargs={"project_uuid": project.uuid},
        )

        dirname = os.path.dirname(__file__)

        template_path = os.path.join(dirname, "data/window_test.csv")
        with open(template_path, "rb") as f:
            response = client.post(
                featurefile_list_url,
                format="multipart",
                data={"file": f, "name": "test.csv", "is_features": True},
            )

        assert response.status_code == status.HTTP_200_OK

        assert response.json()["is_features"] == True

        featurefile_detail_url = reverse(
            "feature-file-detail",
            kwargs={"project_uuid": project.uuid, "uuid": response.json()["uuid"]},
        )

        with open(template_path, "rb") as f:
            response = client.put(
                featurefile_detail_url,
                format="multipart",
                data={"file": f, "name": "test.csv", "is_features": True},
            )

        assert response.status_code == status.HTTP_200_OK

        assert response.json()["is_features"] == True

        assert os.path.exists(
            os.path.join(
                settings.SERVER_FEATURE_FILE_ROOT,
                str(project.uuid),
                response.json()["uuid"] + ".csv",
            )
        )

        with open(template_path, "rb") as f:
            response = client.put(
                featurefile_detail_url,
                format="multipart",
                data={"file": f, "name": "test.csv", "is_features": False},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_datafile(self, client, project):
        settings.DEBUG = True

        featurefile_list_url = reverse(
            "feature-file",
            kwargs={"project_uuid": project.uuid},
        )

        dirname = os.path.dirname(__file__)

        template_path = os.path.join(dirname, "data/window_test.csv")
        with open(template_path, "rb") as f:
            response = client.post(
                featurefile_list_url,
                format="multipart",
                data={"file": f, "name": "test.csv", "is_features": False},
            )

        assert response.status_code == status.HTTP_200_OK

        assert response.json()["is_features"] == False

        featurefile_detail_url = reverse(
            "feature-file-detail",
            kwargs={"project_uuid": project.uuid, "uuid": response.json()["uuid"]},
        )

        with open(template_path, "rb") as f:
            response = client.put(
                featurefile_detail_url,
                format="multipart",
                data={"file": f, "name": "test.csv", "is_features": False},
            )

        assert response.status_code == status.HTTP_200_OK

        assert response.json()["is_features"] == False
        assert os.path.exists(
            os.path.join(
                settings.SERVER_DATA_ROOT,
                str(project.uuid),
                response.json()["uuid"] + ".csv",
            )
        )

        with open(template_path, "rb") as f:
            response = client.put(
                featurefile_detail_url,
                format="multipart",
                data={"file": f, "name": "test.csv", "is_features": True},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
