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

import json
import os

import pytest
from datamanager.models import (
    Capture,
    KnowledgePack,
    Project,
    Sandbox,
    Team,
    TeamMember,
)
from logger.data_logger import usage_log

pytestmark = pytest.mark.django_db  # All tests use db


@pytest.fixture
def project():
    project = Project.objects.create(
        team_id=1,
        name="Test",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )

    return project


@pytest.fixture
def capture(project):
    capture = Capture.objects.create(project=project, name="Test")

    return capture


@pytest.fixture
def sandbox(project):
    sandbox = Sandbox.objects.create(project=project, name="Test")

    return sandbox


@pytest.fixture
def knowledgepack(sandbox):
    knowledgepack = KnowledgePack.objects.create(
        sandbox=sandbox, project=sandbox.project, name="Test"
    )

    return knowledgepack


def test_usage_log(project, capture, sandbox, knowledgepack):

    usage_log(
        operation="test",
        team=Team.objects.get(pk=1),
        team_member=TeamMember.objects.get(pk=1),
        detail=None,
        PJID=None,
        PID=None,
        CID=None,
        PROC=None,
    )

    with open(
        os.path.join(os.path.dirname(__file__), "../../usage_logs.log"), "r"
    ) as fid:
        lines = fid.readlines()
        header_size = len("[07/Jul/2021 21:45:44] INFO [logger.data_logger:57]")
        result = json.loads(lines[-1][header_size:])

    assert result["team"] == "SensimlDevTeam"
    assert result["operation"] == "test"
