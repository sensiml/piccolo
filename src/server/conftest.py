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

# pylint: disable=W0613,W0621
import json
import os
import random
import shutil

import pandas as pd
import pytest
from django.conf import settings


@pytest.fixture(autouse=True)
def use_dummy_cache_dir(settings):
    FILE_DIR = os.path.join(f"/tmp/test_cache_{str(random.randint(0,100000))}")
    print(f"SETTING FILE DIR TO {FILE_DIR}")
    SERVER_BASE_DIRECTORY = FILE_DIR

    settings.MAX_BATCH_SIZE = 2
    settings.FILE_DIR = FILE_DIR
    settings.SERVER_BASE_DIRECTORY = SERVER_BASE_DIRECTORY
    settings.SERVER_CAPTURE_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "capture")
    settings.SERVER_CUSTOM_TRANSFORM_ROOT = os.path.join(
        SERVER_BASE_DIRECTORY, "custom_transforms"
    )
    settings.SERVER_DATA_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "datafiles")
    settings.SERVER_MODEL_STORE_ROOT = os.path.join(
        SERVER_BASE_DIRECTORY, "model_store"
    )
    settings.SERVER_CACHE_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "pipelinecache")
    settings.SERVER_QUERY_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "querydata")
    settings.SERVER_FEATURE_FILE_ROOT = os.path.join(
        SERVER_BASE_DIRECTORY, "featurefile"
    )
    settings.SERVER_CODEGEN_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "codegen")

    for folder in [
        settings.FILE_DIR,
        settings.SERVER_BASE_DIRECTORY,
        settings.SERVER_CAPTURE_ROOT,
        settings.SERVER_CUSTOM_TRANSFORM_ROOT,
        settings.SERVER_DATA_ROOT,
        settings.SERVER_MODEL_STORE_ROOT,
        settings.SERVER_CACHE_ROOT,
        settings.SERVER_QUERY_ROOT,
        settings.SERVER_FEATURE_FILE_ROOT,
        settings.SERVER_CODEGEN_ROOT,
    ]:
        if not os.path.isdir(folder):
            try:
                os.mkdir(folder)
            except FileExistsError:
                continue

    yield FILE_DIR

    shutil.rmtree(FILE_DIR)


@pytest.fixture
def client(request):
    """Django Rest Framework APIClient"""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticate(request, client):
    """Authenticates client fixture with unittest user"""
    client.login(username="unittest@piccolo.com", password="TinyML4Life")
    request.addfinalizer(client.logout)
    return client


@pytest.fixture
def authenticated_client(request, client):
    """Authenticates client fixture with unittest user"""
    r = client.login(username="unittest@piccolo.com", password="TinyML4Life")

    yield client

    client.logout()


@pytest.fixture
def loaddata(db):
    """Allows easy loading of django db fixtures for tests"""
    from django.core.management import call_command

    def _(*args):
        call_command("loaddata", *args)

    return _


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    """Automatically loads initial data for testing session

    See http://pytest-django.readthedocs.io/en/latest/database.html#std:fixture-django_db_setup
    for explanation.
    """
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command(
            "loaddata",
            "tests_users",
            "tests_teams",
            "test_client",
            "tag",
            "loglevel",
        )

    print("loaded stuff")
    print("loaded stuff1")


@pytest.fixture
def test_project_simple():
    from datamanager.models import Project, Sandbox

    project = Project.objects.create(
        team_id=1,
        name="SimpleProject" + str(random.randint(0, 1000)),
        uuid="00000000-0000-0000-0000-000000000000",
        capture_sample_schema={
            "Column1": {"type": "float", "index": 0},
            "Column2": {"type": "float", "index": 1},
        },
    )

    sandbox = Sandbox.objects.create(
        project=project,
        name="TestPipeline",
        uuid="00000000-0000-0000-0000-000000000000",
        cpu_clock_time=100,
    )

    yield (project, sandbox)

    if os.path.exists(os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid))):
        shutil.rmtree(os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid)))
    project.delete()


@pytest.fixture
def testprojects():

    from datamanager.models import (
        Capture,
        CaptureLabelValue,
        CaptureMetadataValue,
        KnowledgePack,
        Label,
        LabelValue,
        Project,
        Query,
        Sandbox,
        Segmenter,
        TeamMember,
    )

    project_dev = Project.objects.create(
        team_id=1,
        name="DevProject",
        capture_sample_schema={
            "Column1": {"type": "float", "index": 0},
            "Column2": {"type": "float", "index": 1},
        },
    )

    project_dev_test = Project.objects.create(
        team_id=1,
        name="DevProjectTest",
        capture_sample_schema={
            "Column1": {"type": "float", "index": 0},
            "Column2": {"type": "float", "index": 1},
        },
    )

    projects = {
        "dev": project_dev,
    }

    for name, project in projects.items():

        # adding pipeline
        num_pipelines = 2

        # adding knowledgepacks per pipeline
        num_knowledgepacks = 2

        for i in range(0, num_pipelines):
            sandbox = Sandbox.objects.create(
                project=project, name="TestPipeline{}".format(i)
            )
            for j in range(0, num_knowledgepacks):
                KnowledgePack.objects.create(
                    sandbox=sandbox,
                    project=sandbox.project,
                    name="TestModel{}".format(j),
                )

            if i == 0:
                team_members = TeamMember.objects.filter(team=project.team)
                for team_member in team_members:
                    sandbox.users.add(team_member)
                sandbox.save()

            sandbox = Sandbox.objects.create(
                project=project, name="TestPipeline{}_private".format(i), private=True
            )

            if i == 0:
                team_members = TeamMember.objects.filter(team=project.team)
                for team_member in team_members:
                    sandbox.users.add(team_member)
                sandbox.save()

        # adding queries
        num_queries = 6
        for i in range(0, num_queries):
            Query.objects.create(project=project, name="TestQuery{}".format(i))

        capture_length = 25
        delta = 5

        # num_captures should be the same len aslabel-values map
        num_captures = 3
        label_values_map = {0: "A", 1: "B", 2: "C"}

        metadata_name = "Subject"
        label_name = "Event"
        segmenter_name = "Manual"

        assert num_captures == len(label_values_map)

        captures = []
        for i in range(0, num_captures):
            captures.append(
                Capture.objects.create(
                    project=project,
                    name="TestCapture{}".format(i),
                    file_size=1048576,
                    max_sequence=capture_length,
                    number_samples=capture_length,
                    file="testtest",
                )
            )

        capture_dir = os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid))
        if not os.path.isdir(capture_dir):
            os.mkdir(capture_dir)

        for capture in captures:
            df = pd.DataFrame(
                {
                    "Column1": list(range(capture_length)),
                    "Column2": [i * 2 for i in range(capture_length)],
                    "sequence": range(capture_length),
                }
            )
            df.to_csv(os.path.join(capture_dir, str(capture.uuid)), index=None)

        # create metadata
        metadata = Label.objects.create(
            project=project, name=metadata_name, metadata=True, type="str"
        )

        label = Label.objects.create(
            project=project, name=label_name, metadata=False, type="str"
        )

        # create label values
        label_values = []

        for i in range(len(label_values_map)):
            label_values.append(
                LabelValue.objects.create(label=label, value=label_values_map[i])
            )

        # create metadata
        metadata_A = LabelValue.objects.create(label=metadata, value="John")
        metadata_B = LabelValue.objects.create(label=metadata, value="Emily")

        # create segmetner
        segmenter = Segmenter.objects.create(
            project=project, name=segmenter_name, custom=True
        )

        # add metadata to captures
        CaptureMetadataValue.objects.create(
            project=project, capture=captures[0], label=metadata, label_value=metadata_A
        )

        CaptureMetadataValue.objects.create(
            project=project, capture=captures[1], label=metadata, label_value=metadata_B
        )

        CaptureMetadataValue.objects.create(
            project=project, capture=captures[2], label=metadata, label_value=metadata_B
        )

        # add labels_values to captures

        for i in range(0, capture_length - delta, delta):
            for index in range(len(label_values)):
                CaptureLabelValue.objects.create(
                    project=project,
                    capture=captures[index],
                    label=label,
                    label_value=label_values[index],
                    segmenter=segmenter,
                    capture_sample_sequence_start=i,
                    capture_sample_sequence_end=i + delta,
                )

    yield projects

    for key, project in projects.items():
        shutil.rmtree(os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid)))


@pytest.fixture
def test_projects_with_pipelines():

    import random

    from datamanager.models import (
        Capture,
        CaptureLabelValue,
        CaptureMetadataValue,
        Label,
        LabelValue,
        Project,
        Query,
        Sandbox,
        Segmenter,
    )

    project = Project.objects.create(
        team_id=1,
        name="RealProject_{rand}".format(rand=random.randint(0, 100)),
        capture_sample_schema={
            "AccelerometerX": {"type": "float"},
            "AccelerometerY": {"type": "float"},
            "AccelerometerZ": {"type": "float"},
        },
    )

    feature_file_pipeline_cascade = [
        {
            "name": [
                "window_test_0.csv",
                "window_test_1.csv",
                "window_test_2.csv",
                "window_test_3.csv",
                "window_test_4.csv",
            ],
            "type": "featurefile",
            "data_columns": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
            "group_columns": ["Label", "Subject"],
            "label_column": "Label",
            "outputs": ["temp.raw"],
        },
        {
            "name": "Windowing",
            "type": "segmenter",
            "feature_table": None,
            "inputs": {
                "input_data": "temp.raw",
                "group_columns": ["Label", "Subject"],
                "window_size": 50,
                "delta": 50,
                "train_delta": 0,
                "return_segment_index": False,
            },
            "outputs": ["temp.Windowing0"],
        },
        {
            "name": "generator_set",
            "type": "generatorset",
            "set": [
                {
                    "function_name": "Sum",
                    "inputs": {
                        "columns": [
                            "AccelerometerX",
                            "AccelerometerY",
                            "AccelerometerZ",
                        ]
                    },
                },
                {
                    "function_name": "Absolute Sum",
                    "inputs": {
                        "columns": [
                            "AccelerometerX",
                            "AccelerometerY",
                            "AccelerometerZ",
                        ]
                    },
                },
            ],
            "inputs": {
                "group_columns": ["Label", "SegmentID", "Subject"],
                "input_data": "temp.Windowing0",
            },
            "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
        },
        {
            "name": "Feature Cascade",
            "type": "transform",
            "feature_table": "temp.features.generator_set0",
            "inputs": {
                "input_data": "temp.generator_set0",
                "group_columns": ["Label", "SegmentID", "Subject"],
                "num_cascades": 2,
                "slide": True,
            },
            "outputs": ["temp.Feature_Cascade0", "temp.features.Feature_Cascade0"],
        },
        {
            "name": "Min Max Scale",
            "type": "transform",
            "feature_table": "temp.features.Feature_Cascade0",
            "inputs": {
                "input_data": "temp.Feature_Cascade0",
                "passthrough_columns": ["CascadeID", "Label", "SegmentID", "Subject"],
                "min_bound": 0,
                "max_bound": 255,
                "pad": 0,
                "feature_min_max_parameters": {},
                "feature_min_max_defaults": None,
            },
            "outputs": ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
        },
        {
            "name": "Sample By Metadata",
            "type": "sampler",
            "feature_table": "temp.features.Min_Max_Scale0",
            "inputs": {
                "input_data": "temp.Min_Max_Scale0",
                "metadata_name": "Label",
                "metadata_values": ["A", "B"],
            },
            "outputs": [
                "temp.Sample_By_Metadata0",
                "temp.features.Sample_By_Metadata0",
            ],
        },
        {
            "name": "tvo",
            "type": "tvo",
            "input_data": "temp.Sample_By_Metadata0",
            "feature_table": "temp.features.Sample_By_Metadata0",
            "label_column": "Label",
            "ignore_columns": ["Subject", "CascadeID", "SegmentID"],
            "outputs": ["temp.tvo0", "temp.features.tvo0"],
            "validation_seed": 0,
            "optimizers": [
                {
                    "inputs": {
                        "aggressive_neuron_creation": True,
                        "number_of_iterations": 50,
                        "number_of_neurons": 10,
                        "ranking_metric": "f1_score",
                        "turbo": True,
                    },
                    "name": "RBF with Neuron Allocation Optimization",
                }
            ],
            "classifiers": [
                {
                    "inputs": {
                        "classification_mode": "KNN",
                        "distance_mode": "Lsup",
                        "max_aif": 250,
                        "min_aif": 20,
                        "num_channels": 1,
                        "reinforcement_learning": False,
                        "reserved_patterns": 0,
                    },
                    "name": "PME",
                }
            ],
            "validation_methods": [{"inputs": {}, "name": "Recall"}],
        },
    ]

    feature_file_pipeline = [
        {
            "name": [
                "window_test_0.csv",
                "window_test_1.csv",
                "window_test_2.csv",
                "window_test_3.csv",
                "window_test_4.csv",
            ],
            "type": "featurefile",
            "data_columns": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
            "group_columns": ["Label", "Subject"],
            "label_column": "Label",
            "outputs": ["temp.raw"],
        },
        {
            "name": "Windowing",
            "type": "segmenter",
            "feature_table": None,
            "inputs": {
                "input_data": "temp.raw",
                "group_columns": ["Label", "Subject"],
                "window_size": 50,
                "delta": 50,
                "train_delta": 0,
                "return_segment_index": False,
            },
            "outputs": ["temp.Windowing0"],
        },
        {
            "name": "generator_set",
            "type": "generatorset",
            "set": [
                {
                    "function_name": "Sum",
                    "inputs": {
                        "columns": [
                            "AccelerometerX",
                            "AccelerometerY",
                            "AccelerometerZ",
                        ]
                    },
                },
                {
                    "function_name": "Absolute Sum",
                    "inputs": {
                        "columns": [
                            "AccelerometerX",
                            "AccelerometerY",
                            "AccelerometerZ",
                        ]
                    },
                },
            ],
            "inputs": {
                "group_columns": ["Label", "SegmentID", "Subject"],
                "input_data": "temp.Windowing0",
            },
            "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
        },
        {
            "name": "Min Max Scale",
            "type": "transform",
            "feature_table": "temp.features.generator_set0",
            "inputs": {
                "input_data": "temp.generator_set0",
                "passthrough_columns": ["Label", "SegmentID", "Subject"],
                "min_bound": 0,
                "max_bound": 255,
                "pad": 0,
                "feature_min_max_parameters": {},
                "feature_min_max_defaults": None,
            },
            "outputs": ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
        },
        {
            "name": "tvo",
            "type": "tvo",
            "input_data": "temp.Min_Max_Scale0",
            "feature_table": "temp.features.Min_Max_Scale0",
            "label_column": "Label",
            "ignore_columns": ["Subject", "SegmentID"],
            "outputs": ["temp.tvo0", "temp.features.tvo0"],
            "validation_seed": 0,
            "optimizers": [
                {
                    "inputs": {
                        "aggressive_neuron_creation": True,
                        "number_of_iterations": 50,
                        "number_of_neurons": 10,
                        "ranking_metric": "f1_score",
                        "turbo": True,
                    },
                    "name": "RBF with Neuron Allocation Optimization",
                }
            ],
            "classifiers": [
                {
                    "inputs": {
                        "classification_mode": "KNN",
                        "distance_mode": "Lsup",
                        "max_aif": 250,
                        "min_aif": 20,
                        "num_channels": 1,
                        "reinforcement_learning": False,
                        "reserved_patterns": 0,
                    },
                    "name": "PME",
                }
            ],
            "validation_methods": [{"inputs": {}, "name": "Recall"}],
        },
    ]

    query_pipeline = [
        {
            "name": "TestQuery",
            "type": "query",
            "outputs": ["temp.raw"],
        },
        {
            "name": "Windowing",
            "type": "segmenter",
            "feature_table": None,
            "inputs": {
                "input_data": "temp.raw",
                "group_columns": ["Label", "Subject"],
                "window_size": 50,
                "delta": 50,
                "train_delta": 0,
                "return_segment_index": False,
            },
            "outputs": ["temp.Windowing0"],
        },
        {
            "name": "generator_set",
            "type": "generatorset",
            "set": [
                {
                    "function_name": "Sum",
                    "inputs": {
                        "columns": [
                            "AccelerometerX",
                            "AccelerometerY",
                            "AccelerometerZ",
                        ]
                    },
                },
                {
                    "function_name": "Absolute Sum",
                    "inputs": {
                        "columns": [
                            "AccelerometerX",
                            "AccelerometerY",
                            "AccelerometerZ",
                        ]
                    },
                },
            ],
            "inputs": {
                "group_columns": ["Label", "SegmentID", "Subject"],
                "input_data": "temp.Windowing0",
            },
            "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
        },
        {
            "type": "selectorset",
            "name": "selector_set",
            "set": [
                {
                    "inputs": {"method": "Log R", "number_of_features": 10},
                    "function_name": "Recursive Feature Elimination",
                }
            ],
            "inputs": {
                "remove_columns": [],
                "passthrough_columns": ["Label", "SegmentID", "Subject"],
                "input_data": "temp.generator_set0",
                "label_column": "Label",
                "number_of_features": 10,
                "feature_table": "temp.features.generator_set0",
                "cost_function": "sum",
            },
            "outputs": ["temp.selector_set0", "temp.features.selector_set0"],
            "refinement": {},
        },
        {
            "name": "Min Max Scale",
            "type": "transform",
            "feature_table": "temp.features.selector_set0",
            "inputs": {
                "input_data": "temp.selector_set0",
                "passthrough_columns": ["Label", "SegmentID", "Subject"],
                "min_bound": 0,
                "max_bound": 255,
                "pad": 0,
                "feature_min_max_parameters": {},
                "feature_min_max_defaults": None,
            },
            "outputs": ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
        },
        {
            "name": "tvo",
            "type": "tvo",
            "input_data": "temp.Min_Max_Scale0",
            "feature_table": "temp.features.Min_Max_Scale0",
            "label_column": "Label",
            "ignore_columns": ["Subject", "SegmentID"],
            "outputs": ["temp.tvo0", "temp.features.tvo0"],
            "validation_seed": 0,
            "optimizers": [
                {
                    "inputs": {
                        "aggressive_neuron_creation": True,
                        "number_of_iterations": 50,
                        "number_of_neurons": 10,
                        "ranking_metric": "f1_score",
                        "turbo": True,
                    },
                    "name": "RBF with Neuron Allocation Optimization",
                }
            ],
            "classifiers": [
                {
                    "inputs": {
                        "classification_mode": "KNN",
                        "distance_mode": "Lsup",
                        "max_aif": 250,
                        "min_aif": 20,
                        "num_channels": 1,
                        "reinforcement_learning": False,
                        "reserved_patterns": 0,
                    },
                    "name": "PME",
                }
            ],
            "validation_methods": [{"inputs": {}, "name": "Recall"}],
        },
    ]

    Sandbox.objects.create(
        project=project,
        name="feature_file_pipeline_cascasde",
        pipeline=feature_file_pipeline_cascade,
    )

    Sandbox.objects.create(
        project=project, name="feature_file_pipeline", pipeline=feature_file_pipeline
    )

    Sandbox.objects.create(
        project=project, name="query_pipeline", pipeline=query_pipeline
    )

    metadata_name = "Subject"
    label_name = "Label"
    segmenter_name = "Manual"

    samples = samples = []

    # create metadata
    metadata = Label.objects.create(
        project=project, name=metadata_name, metadata=True, type="str"
    )

    label = Label.objects.create(
        project=project, name=label_name, metadata=False, type="str"
    )

    # create label values
    label_values = []

    label_values_map = {
        0: "A",
        1: "B",
        2: "C",
    }

    for i in range(len(label_values_map)):
        label_values.append(
            LabelValue.objects.create(label=label, value=label_values_map[i])
        )

    # create metadata
    metadata_A = LabelValue.objects.create(label=metadata, value="John")
    metadata_B = LabelValue.objects.create(label=metadata, value="Emily")

    # create segmetner
    segmenter = Segmenter.objects.create(
        project=project, name=segmenter_name, custom=True
    )

    Query.objects.create(
        project=project,
        name="TestQuery",
        segmenter=segmenter,
        columns=json.dumps(["AccelerometerX", "AccelerometerY", "AccelerometerZ"]),
        metadata_columns=json.dumps(["Subject"]),
        label_column="Label",
        metadata_filter="",
    )

    capture_length = 200
    delta = 5

    # num_captures should be the same len aslabel-values map
    num_captures = 3

    assert num_captures == len(label_values_map)

    captures = []
    for i in range(0, num_captures):
        captures.append(
            Capture.objects.create(
                project=project,
                name="TestCapture{}".format(i),
                file_size=1048576,
                max_sequence=capture_length,
                number_samples=capture_length,
                file="testtest",
            )
        )

    capture_dir = os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid))
    if not os.path.isdir(capture_dir):
        os.mkdir(capture_dir)

    for capture in captures:
        df = pd.DataFrame(
            {
                "AccelerometerX": list(range(capture_length)),
                "AccelerometerY": [i * 2 for i in range(capture_length)],
                "AccelerometerZ": [i * 3 for i in range(capture_length)],
                "sequence": range(capture_length),
            }
        )
        df.to_csv(os.path.join(capture_dir, str(capture.uuid)), index=None)

    # add metadata to captures
    CaptureMetadataValue.objects.create(
        project=project, capture=captures[0], label=metadata, label_value=metadata_A
    )

    CaptureMetadataValue.objects.create(
        project=project, capture=captures[1], label=metadata, label_value=metadata_B
    )

    CaptureMetadataValue.objects.create(
        project=project, capture=captures[2], label=metadata, label_value=metadata_B
    )

    # add labels_values to captures
    for i in range(0, capture_length - delta, delta):
        for index in range(len(label_values)):
            CaptureLabelValue.objects.create(
                project=project,
                capture=captures[index],
                label=label,
                label_value=label_values[index],
                segmenter=segmenter,
                capture_sample_sequence_start=i,
                capture_sample_sequence_end=i + delta,
            )

    yield project

    shutil.rmtree(os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid)))


@pytest.fixture
def testprojects_profile():

    from datamanager.models import (
        Capture,
        CaptureLabelValue,
        CaptureMetadataValue,
        KnowledgePack,
        Label,
        LabelValue,
        Project,
        Query,
        Sandbox,
        Segmenter,
        TeamMember,
    )

    projects = []
    for i in range(2000):

        projects.append(
            Project.objects.create(
                team_id=1,
                name="ExampleProject" + str(i),
                capture_sample_schema={
                    "Column1": {"type": "float"},
                    "Column2": {"type": "float"},
                },
            )
        )

    for _, project in enumerate(projects):

        # adding pipeline
        num_pipelines = 10

        # adding knowledgepacks per pipeline
        num_knowledgepacks = 10

        for i in range(0, num_pipelines):
            sandbox = Sandbox.objects.create(
                project=project, name="TestPipeline{}".format(i)
            )
            for j in range(0, num_knowledgepacks):
                KnowledgePack.objects.create(
                    sandbox=sandbox,
                    project=sandbox.project,
                    name="TestModel{}".format(j),
                )

            if i == 0:
                team_members = TeamMember.objects.filter(team=project.team)
                for team_member in team_members:
                    sandbox.users.add(team_member)
                sandbox.save()

            sandbox = Sandbox.objects.create(
                project=project, name="TestPipeline{}_private".format(i), private=True
            )

            if i == 0:
                team_members = TeamMember.objects.filter(team=project.team)
                for team_member in team_members:
                    sandbox.users.add(team_member)
                sandbox.save()

        # adding queries
        num_queries = 6
        for i in range(0, num_queries):
            Query.objects.create(project=project, name="TestQuery{}".format(i))

        capture_length = 25
        delta = 5

        # num_captures should be the same len aslabel-values map
        num_captures = 3
        label_values_map = {0: "A", 1: "B", 2: "C"}

        metadata_name = "Subject"
        label_name = "Event"
        segmenter_name = "Manual"

        assert num_captures == len(label_values_map)

        captures = []
        for i in range(0, num_captures):
            captures.append(
                Capture.objects.create(
                    project=project,
                    name="TestCapture{}".format(i),
                    file_size=1048576,
                    max_sequence=capture_length,
                    number_samples=capture_length,
                    file="testtest",
                )
            )

            # create metadata
        metadata = Label.objects.create(
            project=project, name=metadata_name, metadata=True, type="str"
        )

        label = Label.objects.create(
            project=project, name=label_name, metadata=False, type="str"
        )

        # create label values
        label_values = []

        for i in range(len(label_values_map)):
            label_values.append(
                LabelValue.objects.create(label=label, value=label_values_map[i])
            )

        # create metadata
        metadata_A = LabelValue.objects.create(label=metadata, value="John")
        metadata_B = LabelValue.objects.create(label=metadata, value="Emily")

        # create segmetner
        segmenter = Segmenter.objects.create(
            project=project, name=segmenter_name, custom=True
        )

        # add metadata to captures
        CaptureMetadataValue.objects.create(
            project=project, capture=captures[0], label=metadata, label_value=metadata_A
        )

        CaptureMetadataValue.objects.create(
            project=project, capture=captures[1], label=metadata, label_value=metadata_B
        )

        CaptureMetadataValue.objects.create(
            project=project, capture=captures[2], label=metadata, label_value=metadata_B
        )

        # add labels_values to captures

        for i in range(0, capture_length - delta, delta):
            for index in range(len(label_values)):
                CaptureLabelValue.objects.create(
                    project=project,
                    capture=captures[index],
                    label=label,
                    label_value=label_values[index],
                    segmenter=segmenter,
                    capture_sample_sequence_start=i,
                    capture_sample_sequence_end=i + delta,
                )

    yield projects

    for project in projects:
        project.delete()


@pytest.fixture
def test_project_with_capture():
    from datamanager.models import Capture, Project

    project = Project.objects.create(
        team_id=1,
        name="SimpleProject" + str(random.randint(0, 1000)),
        uuid="00000000-0000-0000-0000-000000000000",
        capture_sample_schema={
            "Column1": {"type": "float", "index": 0},
            "Column2": {"type": "float", "index": 1},
        },
    )

    capture_length = 10

    capture = Capture.objects.create(
        project=project,
        name="TestCaptureA.csv",
        format=".csv",
        file_size=1048576,
        max_sequence=capture_length,
        number_samples=capture_length,
    )

    capture_dir = os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid))
    if not os.path.isdir(capture_dir):
        os.mkdir(capture_dir)

    df = pd.DataFrame(
        {
            "Column 1": list(range(capture_length)),
            "Column2": [i * 2 for i in range(capture_length)],
            "sequence": range(capture_length),
        }
    )
    df.to_csv(os.path.join(capture_dir, str(capture.uuid)), index=None)

    capture.file = os.path.join(
        settings.SERVER_CAPTURE_ROOT, os.path.join(capture_dir, str(capture.uuid))
    )
    capture.save()

    yield (project, capture)

    if os.path.exists(os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid))):
        shutil.rmtree(os.path.join(settings.SERVER_CAPTURE_ROOT, str(project.uuid)))
    project.delete()
