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
from datamanager.models import KnowledgePack, Project, Sandbox
from engine.recognitionengine import clean_feature_cascade

pytestmark = pytest.mark.django_db


@pytest.fixture
def project():
    project = Project.objects.create(name="test", team_id=1)
    return project


@pytest.fixture
def sandbox(project):
    sandbox = Sandbox.objects.create(name="test", project=project)
    return sandbox


@pytest.fixture
def child_knowledgepack(sandbox):
    child_knowledgepack = KnowledgePack.objects.create(
        sandbox=sandbox,
        project=sandbox.project,
        name="c",
        uuid="11111111-1111-1111-1111-111111111111",
        knowledgepack_description=None,
    )
    return child_knowledgepack


@pytest.fixture
def knowledgepack(sandbox, child_knowledgepack):
    knowledgepack_description = {
        "Parent": {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "results": {"1": "Report", "2": "Model_3"},
        },
        "Model_3": {"uuid": child_knowledgepack.uuid},
    }

    knowledgepack = KnowledgePack.objects.create(
        sandbox=sandbox,
        project=sandbox.project,
        name="p",
        class_map={"1": "D", "2": "combined_label_1"},
        uuid="00000000-0000-0000-0000-000000000000",
        knowledgepack_description=knowledgepack_description,
    )
    return knowledgepack


class TestRunPipelinePopulation:
    def setUp(self):
        pass


def test_clean_feature_cascade():

    feature_summary = [
        {
            "Feature": "gen_c0000_gen_0001_Axis_1LinearRegressionSlope_0000",
            "Sensors": ["Axis_1"],
        },
        {
            "Feature": "gen_c0000_gen_0002_Axis_1Median",
            "Sensors": ["Axis_1"],
        },
        {
            "Feature": "agen_0001_Axis_1LinearRegressionSlope_0000",
            "Sensors": ["Axis_1"],
        },
        {
            "Feature": "agen_0002_Axis_1Median",
            "Sensors": ["Axis_1"],
        },
    ]

    result = clean_feature_cascade(feature_summary)

    expected_result = [
        {
            "Feature": "gen_0001_Axis_1LinearRegressionSlope_0000",
            "Sensors": ["Axis_1"],
        },
        {
            "Feature": "gen_0002_Axis_1Median",
            "Sensors": ["Axis_1"],
        },
        {
            "Feature": "agen_0001_Axis_1LinearRegressionSlope_0000",
            "Sensors": ["Axis_1"],
        },
        {
            "Feature": "agen_0002_Axis_1Median",
            "Sensors": ["Axis_1"],
        },
    ]

    assert result == expected_result


def test_walk_tree():
    pass
