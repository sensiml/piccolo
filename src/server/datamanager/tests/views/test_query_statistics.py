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

import pytest

from datamanager.models import Project, Query, Sandbox


pytestmark = pytest.mark.django_db


@pytest.fixture
def project():
    project = Project.objects.create(name="test", team_id=1)
    return project


@pytest.fixture
def query(project):
    query = Query.objects.create(
        name="unittest_query",
        project=project,
        uuid="1",
        metadata_columns="[Meta_data_test_1, Meta_data_test_1, Meta_data_test_1]",
        columns="[test_x, test_y, test_z]",
        label_column="unittest_label",
    )
    return query


@pytest.fixture
def sandbox(project):
    pipeline = [
        {
            "inputs": {"group_columns": [], "input_data": "temp.raw"},
            "type": "featurefile",
        }
    ]
    sandbox = Sandbox.objects.create(name="test", project=project, pipeline=pipeline)
    return sandbox
