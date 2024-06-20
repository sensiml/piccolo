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

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse

from library.models import Transform
from datamanager.models import Team
from library.models import LibraryPack

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


dirname = os.path.dirname(__file__)

template_path = os.path.join(dirname, "data/test.c")

update_template_path = os.path.join(dirname, "data/update.c")


@pytest.fixture
def library_pack():
    team = Team.objects.get(name=TEAM_NAME)
    library_pack = LibraryPack.objects.create(
        team=team,
        name="Custom Transform Test",
        uuid="d95a2811-f506-4712-b570-8829b56362ce",
    )
    library_pack.uuid = str(library_pack.uuid)

    return library_pack


@pytest.mark.usefixtures("authenticate")
def test_create_name_same_as_sensiml_function_fails(client, library_pack):

    Transform.objects.create(name="Sum")

    custom_transform_list = reverse(
        "custom-transform-list",
        kwargs={},
    )

    with open(template_path, "rb") as f:
        response = client.post(
            custom_transform_list,
            format="multipart",
            data={
                "file": f,
                "name": "Sum",
                "input_contract": "{}",
                "output_contract": "{}",
                "description": "Test File",
                "type": "Feature Generator",
                "subtype": "Statistical",
                "library_pack": library_pack.uuid,
            },
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.usefixtures("authenticate")
def test_create_library_pack(client):

    Transform.objects.create(name="Sum", c_file_name="test.c")

    library_pack_list = reverse(
        "library-pack-list",
        kwargs={},
    )

    response = client.post(
        library_pack_list,
        data={
            "name": "Test LibrarY Pack",
            "description": "test",
            "maintainer": "test",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.usefixtures("authenticate")
def test_create_filename_same_as_sensiml_function_fails(client, library_pack):

    Transform.objects.create(name="Sum", c_file_name="test.c")

    custom_transform_list = reverse(
        "custom-transform-list",
        kwargs={},
    )

    with open(template_path, "rb") as f:
        response = client.post(
            custom_transform_list,
            format="multipart",
            data={
                "file": f,
                "name": "FG Sum Test",
                "input_contract": "{}",
                "output_contract": "{}",
                "description": "Test File",
                "type": "Feature Generator",
                "subtype": "Statistical",
                "library_pack": library_pack.uuid,
            },
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.usefixtures("authenticate")
def test_create_update_delete_custom_transform(client, library_pack):
    settings.DEBUG = True

    custom_transform_list = reverse(
        "custom-transform-list",
        kwargs={},
    )

    os.path.dirname(__file__)

    with open(template_path, "rb") as f:
        response = client.post(
            custom_transform_list,
            format="multipart",
            data={
                "file": f,
                "name": "Test Test",
                "c_function_name": "test",
                "input_contract": json.dumps(
                    [
                        {
                            "name": "columns",
                            "num_columns": -1,
                        }
                    ]
                ),
                "output_contract": json.dumps(
                    [{"name": "output_data", "type": "DataFrame"}]
                ),
                "description": "Test File",
                "type": "Feature Generator",
                "subtype": "Statistical",
                "unit_tests": json.dumps(
                    [
                        {
                            "test_data": {"Ax": [1] * 5},
                            "expected_output": [5],
                            "params": {
                                "input_columns": ["Ax"],
                                "param1": 1,
                                "param2": 3,
                            },
                            "tolerance": 0.001,
                        },
                        {
                            "test_data": {"Ax": [1] * 5, "Ay": [2] * 5},
                            "expected_output": [5, 10],
                            "params": {
                                "input_columns": ["Ay", "Ax"],
                                "param1": 1,
                                "param2": 3,
                            },
                            "tolerance": 0.001,
                        },
                    ]
                ),
                "library_pack": library_pack.uuid,
                "c_file_name": "test.c",
            },
        )

    assert response.status_code == status.HTTP_201_CREATED

    response = client.get(custom_transform_list)

    assert response.status_code == status.HTTP_200_OK

    assert response.data[0]["name"] == "Test Test"

    response = client.get(custom_transform_list)

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data) == 1

    for data in response.data:
        custom_transform_detail = reverse(
            "custom-transform-detail",
            kwargs={"uuid": data["uuid"]},
        )

        with open(update_template_path, "rb") as f:
            response = client.put(
                custom_transform_detail,
                format="multipart",
                data={
                    "file": f,
                    "input_contract": json.dumps(
                        [
                            {
                                "name": "columns",
                                "num_columns": -1,
                            }
                        ]
                    ),
                    "output_contract": json.dumps(
                        [{"name": "output_data", "type": "DataFrame"}]
                    ),
                    "description": "Test File",
                    "type": "Feature Generator",
                    "subtype": "Statistical",
                    "unit_tests": json.dumps(
                        [
                            {
                                "test_data": {"Ax": [1] * 5},
                                "expected_output": [5],
                                "params": {
                                    "input_columns": ["Ax"],
                                    "param1": 1,
                                    "param2": 3,
                                },
                                "tolerance": 0.001,
                            },
                            {
                                "test_data": {"Ax": [1] * 5, "Ay": [2] * 5},
                                "expected_output": [5, 10],
                                "params": {
                                    "input_columns": ["Ay", "Ax"],
                                    "param1": 1,
                                    "param2": 3,
                                },
                                "tolerance": 0.001,
                            },
                        ]
                    ),
                },
            )

        assert response.status_code == status.HTTP_200_OK
        response = client.delete(custom_transform_detail)

        assert response.status_code == status.HTTP_204_NO_CONTENT
