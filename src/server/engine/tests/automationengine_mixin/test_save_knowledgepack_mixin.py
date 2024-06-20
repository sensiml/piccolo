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

import pytest
from datamanager.models import KnowledgePack, Project, Query, Sandbox, Segmenter
from engine.automationengine_mixin.save_knowledgepack_mixin import (
    SaveKnowledgepackMixin,
)
from library.models import PipelineSeed

pytestmark = pytest.mark.django_db


@pytest.fixture
def project():
    project = Project.objects.create(name="test", team_id=1)
    return project


@pytest.fixture
def pipeline_seed():
    pipeline = [
        {
            "inputs": {"group_columns": [], "input_data": "temp.raw"},
            "set": [
                {
                    "inputs": {"smoothing_factor": 4, "sample_rate": 1, "columns": []},
                    "function_name": "Median",
                },
            ],
            "type": "generatorset",
            "name": "generator_set",
            "outputs": ["temp.featuregenerator", "temp.features.featuregenerator"],
        }
    ]
    seed = PipelineSeed.objects.create(name="Test", description="", pipeline=pipeline)

    return seed


@pytest.fixture
def sandbox(project):
    pipeline = [
        {
            "group_columns": ["Subject", "Label"],
            "data_columns": ["AccelX", "AccelY"],
            "label_column": "Label",
            "inputs": {"input_data": "temp.raw"},
            "type": "featurefile",
        }
    ]
    sandbox = Sandbox.objects.create(name="test", project=project, pipeline=pipeline)
    return sandbox


@pytest.fixture
def query(project):
    # create segmetner
    segmenter = Segmenter.objects.create(project=project, name="Manual", custom=True)

    query = Query.objects.create(
        name="test",
        project=project,
        segmenter=segmenter,
        columns=json.dumps(["Column1", "Column2"]),
        metadata_columns=json.dumps(["Gesture"]),
        label_column="Label",
        metadata_filter="",
    )

    return query


@pytest.fixture
def run_pipeline(sandbox, pipeline_seed, query):
    rp = SaveKnowledgepackMixin()
    rp.random_seed = 0
    rp.segmenter_id = None
    rp.param_validation_method = "Recall"
    rp.param_sample_by_metadatalist = None
    rp.sample_by_metadata_list = None
    rp.label = "Label"
    rp.param_combine_labels = None
    rp.param_outlier_filter = None
    rp.ga_steps = ["selectorset", "tvo"]
    rp.sandbox = sandbox
    rp.pipeline = []
    rp.group_columns = ["Subject", "Label"]
    rp.data_columns = ["AccelX", "AccelY"]
    rp.param_generator_set = None
    rp.param_input_columns = None
    rp.query = query
    rp.param_feature_cascade = None

    return rp


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
        "Parent": {"uuid": "00000000-0000-0000-0000-000000000000"},
        "Model_3": {"uuid": child_knowledgepack.uuid},
    }

    knowledgepack = KnowledgePack.objects.create(
        sandbox=sandbox,
        project=sandbox.project,
        name="p",
        uuid="00000000-0000-0000-0000-000000000000",
        knowledgepack_description=knowledgepack_description,
    )
    knowledgepack.save()
    return knowledgepack
