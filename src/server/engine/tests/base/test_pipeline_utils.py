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
import uuid
from unittest.mock import patch

import engine.base.pipeline_utils as pipeline_utils
import pytest
from datamanager.datasegments import datasegments_equal
from datamanager.models import (
    Capture,
    KnowledgePack,
    Project,
    Sandbox,
    Team,
    TeamMember,
)
from library.core_functions import MAX_INT_16, MIN_INT_16
from django.conf import settings
from engine.base.pipeline_utils import (
    PipelineMergeException,
    check_and_convert_datasegments,
    compute_confusion_matrix,
    convert_int16,
    flatten_pipeline_json,
    get_capturefile_labels,
    get_capturefile_sizes,
    get_modified_class_map,
    get_num_feature_banks,
    get_recognize_confusion_matrix,
    merge_data_streaming,
    merge_sensor_columns,
    normalize_signal,
    parse_capture_configuration,
    parse_recognition_pipeline,
    reindex_recognize_file,
    save_cache_as_featurefile,
    save_featurefile,
)
from numpy import array, int32
import numpy as np
from pandas import DataFrame

pytestmark = pytest.mark.django_db  # All tests use db
logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.fixture
def pipeline_json():
    return {
        "Feature Transforms": [
            {
                "name": "Min Max Scale",
                "type": "transform",
                "inputs": {
                    "pad": 0,
                    "max_bound": 255,
                    "min_bound": 0,
                    "input_data": "temp.selector_set0",
                    "passthrough_columns": [
                        "CascadeID",
                        "Label",
                        "SegmentID",
                        "Subject",
                    ],
                    "feature_min_max_defaults": None,
                    "feature_min_max_parameters": {},
                },
                "outputs": ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
                "feature_table": "temp.features.selector_set0",
            },
        ]
    }


@pytest.fixture
def pipeline_json_cascade_slide():
    return {
        "Feature Transforms": [
            {
                "name": "Feature Cascade",
                "type": "transform",
                "inputs": {
                    "slide": True,
                    "input_data": "temp.selector_set0",
                    "num_cascades": 2,
                    "group_columns": ["Label", "SegmentID", "Subject"],
                },
                "outputs": ["temp.Feature_Cascade0", "temp.features.Feature_Cascade0"],
                "feature_table": "temp.features.selector_set0",
            },
            {
                "name": "Min Max Scale",
                "type": "transform",
                "inputs": {
                    "pad": 0,
                    "max_bound": 255,
                    "min_bound": 0,
                    "input_data": "temp.Feature_Cascade0",
                    "passthrough_columns": [
                        "CascadeID",
                        "Label",
                        "SegmentID",
                        "Subject",
                    ],
                    "feature_min_max_defaults": None,
                    "feature_min_max_parameters": {},
                },
                "outputs": ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
                "feature_table": "temp.features.Feature_Cascade0",
            },
        ]
    }


@pytest.fixture
def pipeline_json_cascade_only_training():
    return {
        "Feature Transforms": [
            {
                "name": "Feature Cascade",
                "type": "transform",
                "inputs": {
                    "slide": False,
                    "training_slide": True,
                    "input_data": "temp.selector_set0",
                    "num_cascades": 2,
                    "group_columns": ["Label", "SegmentID", "Subject"],
                },
                "outputs": ["temp.Feature_Cascade0", "temp.features.Feature_Cascade0"],
                "feature_table": "temp.features.selector_set0",
            },
            {
                "name": "Min Max Scale",
                "type": "transform",
                "inputs": {
                    "pad": 0,
                    "max_bound": 255,
                    "min_bound": 0,
                    "input_data": "temp.Feature_Cascade0",
                    "passthrough_columns": [
                        "CascadeID",
                        "Label",
                        "SegmentID",
                        "Subject",
                    ],
                    "feature_min_max_defaults": None,
                    "feature_min_max_parameters": {},
                },
                "outputs": ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
                "feature_table": "temp.features.Feature_Cascade0",
            },
        ]
    }


@pytest.fixture
def pipeline_json_cascade_reset():
    return {
        "Feature Transforms": [
            {
                "name": "Feature Cascade",
                "type": "transform",
                "inputs": {
                    "slide": False,
                    "input_data": "temp.selector_set0",
                    "num_cascades": 2,
                    "group_columns": ["Label", "SegmentID", "Subject"],
                },
                "outputs": ["temp.Feature_Cascade0", "temp.features.Feature_Cascade0"],
                "feature_table": "temp.features.selector_set0",
            },
            {
                "name": "Min Max Scale",
                "type": "transform",
                "inputs": {
                    "pad": 0,
                    "max_bound": 255,
                    "min_bound": 0,
                    "input_data": "temp.Feature_Cascade0",
                    "passthrough_columns": [
                        "CascadeID",
                        "Label",
                        "SegmentID",
                        "Subject",
                    ],
                    "feature_min_max_defaults": None,
                    "feature_min_max_parameters": {},
                },
                "outputs": ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
                "feature_table": "temp.features.Feature_Cascade0",
            },
        ]
    }


class TestPipelineUtils:
    def test_make_pipeline_linear(self):
        expected_result = [
            {"name": "step1", "outputs": ["temp.raw"]},
            {
                "name": "step 2",
                "feature_table": None,
                "inputs": {"input_data": "temp.raw"},
                "outputs": ["temp.step2_out"],
            },
            {
                "name": "step3",
                "feature_table": None,
                "inputs": {"input_data": "temp.step2_out"},
                "outputs": ["temp.step3_out"],
            },
            {
                "name": "generator_set",
                "type": "generatorset",
                "set": [],
                "inputs": {"input_data": "temp.step3_out"},
                "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
            },
            {
                "name": "step5",
                "feature_table": "temp.features.generator_set0",
                "inputs": {"input_data": "temp.generator_set0"},
                "outputs": ["temp.step5_out", "temp.features.step5_out"],
            },
            {
                "type": "selectorset",
                "name": "selector_set",
                "set": [],
                "inputs": {
                    "input_data": "temp.step5_out",
                    "feature_table": "temp.features.step5_out",
                },
                "outputs": ["temp.selector_set0", "temp.features.selector_set0"],
            },
            {
                "name": "step6",
                "feature_table": "temp.features.selector_set0",
                "inputs": {
                    "input_data": "temp.selector_set0",
                },
                "outputs": ["temp.step6_out", "temp.features.step6_out"],
            },
            {
                "name": "tvo",
                "input_data": "temp.step6_out",
                "feature_table": "temp.features.step6_out",
                "outputs": ["temp.tvo0", "temp.features.tvo0"],
            },
        ]

        pipeline = [
            {"name": "step1", "outputs": ["temp.raw"]},
            {
                "name": "step 2",
                "feature_table": None,
                "inputs": {"input_data": "temp.raw"},
                "outputs": ["temp.step2_out"],
            },
            {
                "name": "step3",
                "feature_table": None,
                "inputs": {"input_data": ""},
                "outputs": ["temp.step3_out"],
            },
            {
                "name": "generator_set",
                "type": "generatorset",
                "set": [],
                "inputs": {"input_data": ""},
                "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
            },
            {
                "name": "step5",
                "feature_table": "temp.features.generator_set0",
                "inputs": {"input_data": ""},
                "outputs": ["temp.step5_out", "temp.features.step5_out"],
            },
            {
                "type": "selectorset",
                "name": "selector_set",
                "set": [],
                "inputs": {"input_data": "", "feature_table": ""},
                "outputs": ["temp.selector_set0", "temp.features.selector_set0"],
            },
            {
                "name": "step6",
                "feature_table": "",
                "inputs": {
                    "input_data": "",
                },
                "outputs": ["temp.step6_out", "temp.features.step6_out"],
            },
            {
                "name": "tvo",
                "input_data": "temp.step6_out",
                "feature_table": "temp.features.step6_out",
                "outputs": ["temp.tvo0", "temp.features.tvo0"],
            },
        ]

        result = pipeline_utils.make_pipeline_linear(pipeline)

        assert result == expected_result


class TestPipelineUtilityFunctions:
    """Unit tests for EventFile and EventFiles."""

    @pytest.mark.skip(reason="not working for some reason")
    def test_parse_recognition_pipeline(self):
        inputs = [
            {
                u"feature_table": None,
                u"inputs": {
                    u"input_columns": [
                        u"AccelerometerX",
                        u"AccelerometerY",
                        u"AccelerometerZ",
                    ],
                    u"input_data": "temp.raw",
                },
                u"name": u"Magnitude",
                u"outputs": [u"temp.Magnitude0"],
                u"type": u"transform",
            },
            {
                u"feature_table": None,
                u"inputs": {
                    u"delta": 100,
                    u"group_columns": [u"Label"],
                    u"input_data": u"temp.Magnitude0",
                    u"return_segment_index": False,
                    u"window_size": 100,
                },
                u"name": u"Windowing",
                u"outputs": [u"temp.Windowing0"],
                u"type": u"segmenter",
            },
            {
                u"inputs": {
                    u"group_columns": [u"Label", u"SegmentID"],
                    u"input_data": u"temp.Windowing0",
                },
                u"name": u"generator_set",
                u"outputs": [u"temp.generator_set0", u"temp.features.generator_set0"],
                u"set": [
                    {
                        "family": None,
                        "function_name": u"Sum",
                        "inputs": {"columns": [u"AccelerometerY"]},
                        "outputs": [0],
                    },
                    {
                        "family": None,
                        "function_name": u"Sum",
                        "inputs": {"columns": [u"AccelerometerZ"]},
                        "outputs": [0],
                    },
                    {
                        "family": None,
                        "function_name": u"Sum",
                        "inputs": {"columns": [u"Magnitude_ST_0000"]},
                        "outputs": [0],
                    },
                ],
                u"type": u"generatorset",
            },
            {
                u"feature_table": u"temp.features.generator_set0",
                u"inputs": {
                    u"feature_min_max_parameters": {
                        u"maximums": {
                            u"gen_0001_AccelerometerYSum": 79952.0,
                            u"gen_0002_AccelerometerZSum": 119928.0,
                            u"gen_0003_Magnitude_ST_0000Sum": 149580.0,
                        },
                        u"minimums": {
                            u"gen_0001_AccelerometerYSum": -86.0,
                            u"gen_0002_AccelerometerZSum": -129.0,
                            u"gen_0003_Magnitude_ST_0000Sum": 872.0,
                        },
                    },
                    u"input_data": u"temp.generator_set0",
                    u"max_bound": 255,
                    u"min_bound": 0,
                    u"passthrough_columns": [u"Label", u"SegmentID"],
                },
                u"name": u"Min Max Scale",
                u"outputs": [u"temp.Min_Max_Scale0", u"temp.features.Min_Max_Scale0"],
                u"type": u"transform",
            },
        ]

        result = parse_recognition_pipeline(inputs)

        expected_result = {
            "Feature Generators": {
                u"inputs": {
                    u"group_columns": [u"Label", u"SegmentID"],
                    u"input_data": u"temp.Windowing0",
                },
                u"name": u"generator_set",
                u"outputs": [u"temp.generator_set0", u"temp.features.generator_set0"],
                u"set": [
                    {
                        "family": None,
                        "function_name": u"Sum",
                        "inputs": {"columns": [u"AccelerometerY"]},
                        "outputs": [0],
                    },
                    {
                        "family": None,
                        "function_name": u"Sum",
                        "inputs": {"columns": [u"AccelerometerZ"]},
                        "outputs": [0],
                    },
                    {
                        "family": None,
                        "function_name": u"Sum",
                        "inputs": {"columns": [u"Magnitude_ST_0000"]},
                        "outputs": [0],
                    },
                ],
                u"type": u"generatorset",
            },
            "Feature Transforms": [
                {
                    u"feature_table": u"temp.features.generator_set0",
                    u"inputs": {
                        u"feature_min_max_parameters": {
                            u"maximums": {
                                u"gen_0001_AccelerometerYSum": 79952.0,
                                u"gen_0002_AccelerometerZSum": 119928.0,
                                u"gen_0003_Magnitude_ST_0000Sum": 149580.0,
                            },
                            u"minimums": {
                                u"gen_0001_AccelerometerYSum": -86.0,
                                u"gen_0002_AccelerometerZSum": -129.0,
                                u"gen_0003_Magnitude_ST_0000Sum": 872.0,
                            },
                        },
                        u"input_data": u"temp.generator_set0",
                        u"max_bound": 255,
                        u"min_bound": 0,
                        u"passthrough_columns": [u"Label", u"SegmentID"],
                    },
                    u"name": u"Min Max Scale",
                    u"outputs": [
                        u"temp.Min_Max_Scale0",
                        u"temp.features.Min_Max_Scale0",
                    ],
                    u"type": u"transform",
                }
            ],
            "Segment Transforms": [],
            "Segmenter": {
                u"feature_table": None,
                u"inputs": {
                    u"delta": 100,
                    u"group_columns": [u"Label"],
                    u"input_data": u"temp.Magnitude0",
                    u"return_segment_index": False,
                    u"window_size": 100,
                },
                u"name": u"Windowing",
                u"outputs": [u"temp.Windowing0"],
                u"type": u"segmenter",
            },
            "Sensor Transforms": [
                {
                    u"feature_table": None,
                    u"inputs": {
                        u"input_columns": [
                            u"AccelerometerX",
                            u"AccelerometerY",
                            u"AccelerometerZ",
                        ],
                        u"input_data": "temp.raw",
                    },
                    u"name": u"Magnitude",
                    u"outputs": [u"temp.Magnitude0"],
                    u"type": u"transform",
                }
            ],
        }

        assert result == expected_result

    def test_merge_sensor_columns(self):
        inputs = {
            0: {"sensor_columns": ["A", "B"]},
            1: {"sensor_columns": ["A", "B"]},
            2: {"sensor_columns": ["C", "B"]},
        }

        # check that columns are merged correctly
        result = merge_sensor_columns([0, 1], inputs)
        expected_result = ["A", "B"]
        assert result == expected_result

        # check that an assertion is raised when sensor columns don't match
        with pytest.raises(PipelineMergeException):
            merge_sensor_columns([0, 1, 2], inputs)

    def test_flatten_pipeline_json(self):

        inputs = {
            "Sensor Transforms": [1, 2],
            "Segmenter": "Test Segmenter",
            "Segment Transforms": [3, 4],
            "Feature Generators": "test Feature Generators",
            "Feature Transforms": [5, 6],
            "Sensor Filters": [],
        }
        result = flatten_pipeline_json(inputs)
        expected_result = [
            1,
            2,
            "Test Segmenter",
            3,
            4,
            "test Feature Generators",
            5,
            6,
        ]

        assert result == expected_result

    def test_merge_data_streaming(self):

        inputs = {
            0: {
                "pipeline_json": {
                    "Sensor Transforms": [
                        {
                            u"inputs": {
                                u"input_columns": [
                                    u"AccelerometerX",
                                    u"AccelerometerY",
                                    u"AccelerometerZ",
                                ]
                            },
                            u"name": u"Magnitude",
                            u"type": u"transform",
                        }
                    ],
                },
                "sensor_columns": [
                    "AccelerometerX",
                    "AccelerometerY",
                    "AccelerometerZ",
                ],
                "data_columns": [
                    "ACCELEROMETERX",
                    "ACCELEROMETERY",
                    "ACCELEROMETERZ",
                    "MAGNINTUDE_0000",
                ],
            },
            1: {
                "pipeline_json": {
                    "Sensor Transforms": [
                        {
                            u"inputs": {
                                u"input_columns": [
                                    u"AccelerometerX",
                                    u"AccelerometerY",
                                    u"AccelerometerZ",
                                ]
                            },
                            u"name": u"Magnitude",
                            u"type": u"transform",
                        }
                    ],
                },
                "sensor_columns": [
                    "AccelerometerX",
                    "AccelerometerY",
                    "AccelerometerZ",
                ],
                "data_columns": ["ACCELEROMETERX", "ACCELEROMETERZ", "MAGNINTUDE_0000"],
            },
        }
        result_1, result_2, result_3 = merge_data_streaming([0, 1], inputs)

        expected_result_1 = [
            {
                u"inputs": {
                    u"input_columns": [
                        u"AccelerometerX",
                        u"AccelerometerY",
                        u"AccelerometerZ",
                    ]
                },
                u"name": u"Magnitude",
                u"type": u"transform",
            }
        ]

        expected_result_2 = {
            "ACCELEROMETERX": 0,
            "ACCELEROMETERY": 1,
            "ACCELEROMETERZ": 2,
            "MAGNINTUDE_0000": 3,
        }

        expected_result_3 = {
            0: {
                "ACCELEROMETERX": 0,
                "ACCELEROMETERY": 1,
                "ACCELEROMETERZ": 2,
                "MAGNINTUDE_0000": 3,
            },
            1: {"ACCELEROMETERX": 0, "ACCELEROMETERZ": 2, "MAGNINTUDE_0000": 3},
        }

        assert result_1 == expected_result_1
        assert result_2 == expected_result_2
        assert result_3 == expected_result_3

    def test_merge_data_streaming_two(self):

        inputs = {
            0: {
                "pipeline_json": {
                    "Sensor Transforms": [
                        {
                            u"inputs": {
                                u"input_columns": [u"AccelerometerY", u"AccelerometerZ"]
                            },
                            u"name": u"Magnitude",
                            u"type": u"transform",
                        }
                    ],
                },
                "sensor_columns": [
                    "AccelerometerX",
                    "AccelerometerY",
                    "AccelerometerZ",
                ],
                "data_columns": ["ACCELEROMETERY", "ACCELEROMETERZ", "MAGNINTUDE_0000"],
            },
            1: {
                "pipeline_json": {
                    "Sensor Transforms": [],
                },
                "sensor_columns": ["AccelerometerX", "AccelerometerY", "AcceleromterZ"],
                "data_columns": ["ACCELEROMETERX", "ACCELEROMETERZ"],
            },
        }
        result_1, result_2, result_3 = merge_data_streaming([0, 1], inputs)

        expected_result_1 = [
            {
                u"inputs": {u"input_columns": [u"AccelerometerY", u"AccelerometerZ"]},
                u"name": u"Magnitude",
                u"type": u"transform",
            }
        ]

        expected_result_2 = {
            "ACCELEROMETERX": 0,
            "ACCELEROMETERY": 1,
            "ACCELEROMETERZ": 2,
            "MAGNINTUDE_0000": 3,
        }

        expected_result_3 = {
            0: {"ACCELEROMETERY": 1, "ACCELEROMETERZ": 2, "MAGNINTUDE_0000": 3},
            1: {"ACCELEROMETERX": 0, "ACCELEROMETERZ": 2},
        }

        assert result_1 == expected_result_1
        assert result_2 == expected_result_2
        assert result_3 == expected_result_3

    @patch("datamanager.utils")
    @patch("os.path.join")
    @patch("datamanager.datastore.LocalDataStoreService.save_data")
    def test_save_featurefile(self, mock_datastore, mock_os, mock_utils):
        expectedPath = "Test1"
        expectedData = "Test Data"
        expectedExtension = ".test_extension"
        mock_os.return_value = expectedPath
        mock_datastore.return_value = ""
        mock_utils().ensure_path_exists.return_value = True
        project = Project.objects.create(
            name="APITestProject",
            team=Team.objects.get(name=TEAM_NAME),
        )
        ret_feature_file = save_featurefile(project, expectedData, expectedExtension)
        mock_os.assert_called_with(settings.SERVER_FEATURE_FILE_ROOT, project.uuid)
        mock_datastore.assert_called_with(
            expectedData, "{}{}".format(ret_feature_file.uuid, expectedExtension)
        )
        assert ret_feature_file.name == str(ret_feature_file.uuid)
        assert ret_feature_file.project.uuid == project.uuid
        assert ret_feature_file.path == expectedPath

    @patch("datamanager.utils")
    @patch("os.path.join")
    @patch("datamanager.datastore.LocalDataStoreService.save_data")
    def test_save_featurefile(self, mock_datastore, mock_os, mock_utils):
        expectedPath = "Test1"
        expectedData = "Test Data"
        expectedExtension = ".test_extension"
        expectedFmt = ".test_extension"
        mock_os.return_value = expectedPath
        mock_datastore.return_value = ""
        mock_utils().ensure_path_exists.return_value = True
        project = Project.objects.create(
            name="APITestProject",
            team=Team.objects.get(name=TEAM_NAME),
        )
        ret_feature_file = save_featurefile(project, expectedData, expectedExtension)
        mock_os.assert_called_with(settings.SERVER_FEATURE_FILE_ROOT, project.uuid)
        mock_datastore.assert_called_with(
            expectedData,
            "{}{}".format(ret_feature_file.uuid, expectedExtension),
            fmt=expectedFmt,
        )
        assert ret_feature_file.name == str(ret_feature_file.uuid)
        assert ret_feature_file.project.uuid == project.uuid
        assert ret_feature_file.path == expectedPath

    @patch("datamanager.utils")
    @patch("os.path.join")
    @patch("datamanager.datastore.LocalDataStoreService.copy_to_folder")
    def test_save_cache_as_featurefile(self, mock_datastore, mock_os, mock_utils):
        expectedPath = "Test1"
        expectedPipelineId = "4537d71a-7479-4715-b1cd-d7748b140001"
        expectedSourceFileName = "test_source_file"
        expectedExtension = ".test_extension"
        mock_os.return_value = expectedPath
        mock_datastore.return_value = ""
        mock_utils().ensure_path_exists.return_value = True
        label_column = "Test"
        project = Project.objects.create(
            name="APITestProject",
            team=Team.objects.get(name=TEAM_NAME),
        )
        ret_feature_file = save_cache_as_featurefile(
            project,
            expectedPipelineId,
            expectedSourceFileName,
            expectedExtension,
            label_column,
        )
        mock_os.assert_called_with(settings.SERVER_CACHE_ROOT, expectedPipelineId)
        mock_datastore.assert_called_with(
            "{}{}".format(expectedSourceFileName, expectedExtension),
            "{}{}".format(ret_feature_file.uuid, expectedExtension),
            expectedPath,
        )
        assert ret_feature_file.name == str(ret_feature_file.uuid)
        assert ret_feature_file.project.uuid == project.uuid
        assert ret_feature_file.path == expectedPath
        assert ret_feature_file.label_column == label_column


def test_get_capturefile_labels(testprojects):

    project = testprojects["dev"]

    data = get_capturefile_labels(project.uuid, filenames="TestCapture0", label="Event")

    expected_result = [
        {
            "Capture": "TestCapture0",
            "Label_Value": "A",
            "SegmentStart": 0,
            "SegmentEnd": 5,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture0",
            "Label_Value": "A",
            "SegmentStart": 5,
            "SegmentEnd": 10,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture0",
            "Label_Value": "A",
            "SegmentStart": 10,
            "SegmentEnd": 15,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture0",
            "Label_Value": "A",
            "SegmentStart": 15,
            "SegmentEnd": 20,
            "Session": "Manual",
        },
    ]

    assert data == expected_result


def test_get_capturefile_labels_list(testprojects):

    project = testprojects["dev"]

    data = get_capturefile_labels(
        project.uuid, filenames=["TestCapture0", "TestCapture1"], label="Event"
    )

    expected_result = [
        {
            "Capture": "TestCapture0",
            "Label_Value": "A",
            "SegmentStart": 0,
            "SegmentEnd": 5,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture1",
            "Label_Value": "B",
            "SegmentStart": 0,
            "SegmentEnd": 5,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture0",
            "Label_Value": "A",
            "SegmentStart": 5,
            "SegmentEnd": 10,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture1",
            "Label_Value": "B",
            "SegmentStart": 5,
            "SegmentEnd": 10,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture0",
            "Label_Value": "A",
            "SegmentStart": 10,
            "SegmentEnd": 15,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture1",
            "Label_Value": "B",
            "SegmentStart": 10,
            "SegmentEnd": 15,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture0",
            "Label_Value": "A",
            "SegmentStart": 15,
            "SegmentEnd": 20,
            "Session": "Manual",
        },
        {
            "Capture": "TestCapture1",
            "Label_Value": "B",
            "SegmentStart": 15,
            "SegmentEnd": 20,
            "Session": "Manual",
        },
    ]
    print(data)
    assert data == expected_result


def test_get_capturefile_sizes(testprojects):

    project = testprojects["dev"]

    results = get_capturefile_sizes(
        project.uuid, filenames=["TestCapture0", "TestCapture1"]
    )

    expected_results = [
        {"capture": "TestCapture0", "number_samples": 25},
        {"capture": "TestCapture1", "number_samples": 25},
    ]

    assert results == expected_results


def test_reindex_recognize_file(testprojects):

    capture_sizes = [
        {"capture": "TestCapture0", "number_samples": 25},
        {"capture": "TestCapture1", "number_samples": 25},
    ]

    recognize = [
        {"SegmentStart": 0, "SegmentEnd": 4},
        {"SegmentStart": 5, "SegmentEnd": 19},
        {"SegmentStart": 20, "SegmentEnd": 24},
        {"SegmentStart": 22, "SegmentEnd": 29},
        {"SegmentStart": 25, "SegmentEnd": 29},
        {"SegmentStart": 30, "SegmentEnd": 39},
        {"SegmentStart": 40, "SegmentEnd": 49},
    ]

    result = reindex_recognize_file(capture_sizes, recognize)

    expected_result = [
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture0"},
        {"SegmentEnd": 19, "SegmentStart": 5, "Capture": "TestCapture0"},
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture1"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1"},
        {"SegmentEnd": 24, "SegmentStart": 15, "Capture": "TestCapture1"},
    ]

    assert result == expected_result


def test_compute_confusion_matrix():

    # fmt: off
    ground_truth = [
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture0", "Label_Value":"A"},
        {"SegmentEnd": 19, "SegmentStart": 5, "Capture": "TestCapture0", "Label_Value":"A"},
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0", "Label_Value":"A"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture1", "Label_Value":"A"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1","Label_Value":"B"},
        {"SegmentEnd": 24, "SegmentStart": 15, "Capture": "TestCapture1","Label_Value":"B"},
    ]

    predicted = [
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture0", "ClassificationName":"B"},
        {"SegmentEnd": 19, "SegmentStart": 5, "Capture": "TestCapture0", "ClassificationName":"A"},
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0", "ClassificationName":"A"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture1", "ClassificationName":"A"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1","ClassificationName":"A"},
        {"SegmentEnd": 24, "SegmentStart": 15, "Capture": "TestCapture1","ClassificationName":"B"},
    ]
    # fmt: on
    # class_map = {'unknown':0,'A':1,'B':2}

    ytick_labels = ["unknown", "A", "B"]

    results = compute_confusion_matrix(predicted, ground_truth, ytick_labels)

    expected_results = {
        "unknown": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
        "A": {"unknown": 0, "A": 1, "B": 1, "GroundTruth_Total": 4},
        "B": {"unknown": 0, "A": 3, "B": 1, "GroundTruth_Total": 2},
    }

    print(results)
    assert results == expected_results

    results = compute_confusion_matrix(predicted, [], ytick_labels)

    expected_results = {
        "unknown": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
        "A": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
        "B": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
    }

    print(results)
    assert results == expected_results

    results = compute_confusion_matrix([], ground_truth, ytick_labels)

    expected_results = {
        "unknown": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
        "A": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 4},
        "B": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 2},
    }

    ground_truth[0]["Label_Value"] = "NO_LABEL"

    results = compute_confusion_matrix([], ground_truth, ytick_labels)

    expected_results = {
        "unknown": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
        "A": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
        "B": {"unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
    }

    print(results)
    assert results == expected_results


def test_get_recognize_confusion_matrix():

    # fmt: off
    ground_truth = [
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture0", "Label_Value":"A", "Session":"A"},
        {"SegmentEnd": 19, "SegmentStart": 5, "Capture": "TestCapture0", "Label_Value":"A","Session":"A"},
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0", "Label_Value":"A","Session":"A"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture1", "Label_Value":"A","Session":"A"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1", "Label_Value":"B","Session":"A"},
        {"SegmentEnd": 24, "SegmentStart": 15, "Capture": "TestCapture1", "Label_Value":"B","Session":"A"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture0", "Label_Value":"A", "Session":"B"},
        {"SegmentEnd": 19, "SegmentStart": 5, "Capture": "TestCapture0", "Label_Value":"A","Session":"B"},
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0", "Label_Value":"A","Session":"B"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture1", "Label_Value":"A","Session":"A"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1", "Label_Value":"B","Session":"A"},
        {"SegmentEnd": 24, "SegmentStart": 15, "Capture": "TestCapture1", "Label_Value":"B","Session":"A"},
    ]

    predicted = [
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture0", "ClassificationName":"B"},
        {"SegmentEnd": 19, "SegmentStart": 5, "Capture": "TestCapture0", "ClassificationName":"A"},
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0", "ClassificationName":"A"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture1", "ClassificationName":"A"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1","ClassificationName":"A"},
        {"SegmentEnd": 24, "SegmentStart": 15, "Capture": "TestCapture1","ClassificationName":"B"},
    ]
    # fmt: on
    class_map = {"1": "A", "2": "B"}

    results = get_recognize_confusion_matrix(
        DataFrame(predicted),
        DataFrame(ground_truth),
        ["TestCapture0", "TestCapture1"],
        class_map,
    )

    expected_results = {
        "A": {
            "TestCapture0": {
                "Unknown": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
                "A": {"Unknown": 0, "A": 2, "B": 1, "GroundTruth_Total": 3},
                "B": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
            },
            "TestCapture1": {
                "Unknown": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
                "A": {"Unknown": 0, "A": 1, "B": 0, "GroundTruth_Total": 2},
                "B": {"Unknown": 0, "A": 1, "B": 1, "GroundTruth_Total": 4},
            },
        },
        "B": {
            "TestCapture0": {
                "Unknown": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
                "A": {"Unknown": 0, "A": 2, "B": 1, "GroundTruth_Total": 3},
                "B": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
            },
            "TestCapture1": {
                "Unknown": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
                "A": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
                "B": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
            },
        },
    }
    print(results)

    assert results == expected_results


def test_missing_ground_truth_and_missing_prediction():

    # fmt: off
    ground_truth = [
        {"SegmentEnd": 19, "SegmentStart": 5, "Capture": "TestCapture0", "Label_Value":"A","Session":"A"},
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0", "Label_Value":"A","Session":"A"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1", "Label_Value":"B","Session":"A"},
        {"SegmentEnd": 24, "SegmentStart": 15, "Capture": "TestCapture1", "Label_Value":"B","Session":"A"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture0", "Label_Value":"A", "Session":"B"},
        {"SegmentEnd": 19, "SegmentStart": 5, "Capture": "TestCapture0", "Label_Value":"A","Session":"B"},
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0", "Label_Value":"A","Session":"B"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture1", "Label_Value":"A","Session":"A"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1", "Label_Value":"B","Session":"A"},
        {"SegmentEnd": 24, "SegmentStart": 15, "Capture": "TestCapture1", "Label_Value":"B","Session":"A"},
    ]

    predicted = [
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture0", "ClassificationName":"B"},    
        {"SegmentEnd": 24, "SegmentStart": 20, "Capture": "TestCapture0", "ClassificationName":"A"},
        {"SegmentEnd": 4, "SegmentStart": 0, "Capture": "TestCapture1", "ClassificationName":"A"},
        {"SegmentEnd": 14, "SegmentStart": 5, "Capture": "TestCapture1","ClassificationName":"A"},
    ]
    # fmt: on
    class_map = {"1": "A", "2": "B"}

    results = get_recognize_confusion_matrix(
        DataFrame(predicted),
        DataFrame(ground_truth),
        ["TestCapture0", "TestCapture1"],
        class_map,
    )

    expected_results = {
        "A": {
            "TestCapture0": {
                "A": {"A": 1, "Unknown": 0, "B": 0, "GroundTruth_Total": 2},
                "Unknown": {"A": 0, "Unknown": 0, "B": 0, "GroundTruth_Total": 0},
                "B": {"A": 0, "Unknown": 0, "B": 0, "GroundTruth_Total": 0},
            },
            "TestCapture1": {
                "Unknown": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
                "A": {"Unknown": 0, "A": 1, "B": 0, "GroundTruth_Total": 1},
                "B": {"Unknown": 0, "A": 1, "B": 0, "GroundTruth_Total": 4},
            },
        },
        "B": {
            "TestCapture0": {
                "A": {"A": 1, "Unknown": 0, "B": 1, "GroundTruth_Total": 3},
                "Unknown": {"A": 0, "Unknown": 0, "B": 0, "GroundTruth_Total": 0},
                "B": {"A": 0, "Unknown": 0, "B": 0, "GroundTruth_Total": 0},
            },
            "TestCapture1": {
                "Unknown": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
                "A": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
                "B": {"Unknown": 0, "A": 0, "B": 0, "GroundTruth_Total": 0},
            },
        },
    }
    print(results)

    assert results == expected_results


def test_compute_confusion_matrix_missing_ytick_label():

    ground_truth = [
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 756,
            "SegmentStart": 607,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 1041,
            "SegmentStart": 892,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 1269,
            "SegmentStart": 1120,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 1497,
            "SegmentStart": 1348,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 1744,
            "SegmentStart": 1595,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 2015,
            "SegmentStart": 1866,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 2237,
            "SegmentStart": 2088,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 2462,
            "SegmentStart": 2313,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 2771,
            "SegmentStart": 2622,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 3000,
            "SegmentStart": 2851,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 3273,
            "SegmentStart": 3124,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 3670,
            "SegmentStart": 3521,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 3980,
            "SegmentStart": 3831,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 4270,
            "SegmentStart": 4121,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 4467,
            "SegmentStart": 4318,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 4792,
            "SegmentStart": 4643,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 4953,
            "SegmentStart": 4804,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 5117,
            "SegmentStart": 4968,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 5437,
            "SegmentStart": 5288,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 5967,
            "SegmentStart": 5818,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 6241,
            "SegmentStart": 6092,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 6416,
            "SegmentStart": 6267,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 6767,
            "SegmentStart": 6618,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 7061,
            "SegmentStart": 6912,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 7271,
            "SegmentStart": 7122,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 7425,
            "SegmentStart": 7276,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 7931,
            "SegmentStart": 7782,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 8352,
            "SegmentStart": 8203,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 8564,
            "SegmentStart": 8415,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 8769,
            "SegmentStart": 8620,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "Cross",
            "SegmentEnd": 8978,
            "SegmentStart": 8829,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "No_Punch",
            "SegmentEnd": 291,
            "SegmentStart": 142,
            "Session": "GyroscopeTrigger",
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Label_Value": "No_Punch",
            "SegmentEnd": 9466,
            "SegmentStart": 9317,
            "Session": "GyroscopeTrigger",
        },
    ]
    predicted = [
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 4,
            "ClassificationName": "No_Punch",
            "ModelName": "0",
            "SegmentEnd": 291,
            "SegmentID": 0,
            "SegmentLength": 150,
            "SegmentStart": 142,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 3,
            "ClassificationName": "Jab",
            "ModelName": "0",
            "SegmentEnd": 756,
            "SegmentID": 1,
            "SegmentLength": 150,
            "SegmentStart": 607,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 1041,
            "SegmentID": 2,
            "SegmentLength": 150,
            "SegmentStart": 892,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 1269,
            "SegmentID": 3,
            "SegmentLength": 150,
            "SegmentStart": 1120,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 1497,
            "SegmentID": 4,
            "SegmentLength": 150,
            "SegmentStart": 1348,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 1744,
            "SegmentID": 5,
            "SegmentLength": 150,
            "SegmentStart": 1595,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 2015,
            "SegmentID": 6,
            "SegmentLength": 150,
            "SegmentStart": 1866,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 2237,
            "SegmentID": 7,
            "SegmentLength": 150,
            "SegmentStart": 2088,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 2462,
            "SegmentID": 8,
            "SegmentLength": 150,
            "SegmentStart": 2313,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 2771,
            "SegmentID": 9,
            "SegmentLength": 150,
            "SegmentStart": 2622,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 3000,
            "SegmentID": 10,
            "SegmentLength": 150,
            "SegmentStart": 2851,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 3273,
            "SegmentID": 11,
            "SegmentLength": 150,
            "SegmentStart": 3124,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 3670,
            "SegmentID": 12,
            "SegmentLength": 150,
            "SegmentStart": 3521,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 3980,
            "SegmentID": 13,
            "SegmentLength": 150,
            "SegmentStart": 3831,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 4270,
            "SegmentID": 14,
            "SegmentLength": 150,
            "SegmentStart": 4121,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 3,
            "ClassificationName": "Jab",
            "ModelName": "0",
            "SegmentEnd": 4467,
            "SegmentID": 15,
            "SegmentLength": 150,
            "SegmentStart": 4318,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 4792,
            "SegmentID": 16,
            "SegmentLength": 150,
            "SegmentStart": 4643,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 4953,
            "SegmentID": 17,
            "SegmentLength": 150,
            "SegmentStart": 4804,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 3,
            "ClassificationName": "Jab",
            "ModelName": "0",
            "SegmentEnd": 5117,
            "SegmentID": 18,
            "SegmentLength": 150,
            "SegmentStart": 4968,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 5437,
            "SegmentID": 19,
            "SegmentLength": 150,
            "SegmentStart": 5288,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 3,
            "ClassificationName": "Jab",
            "ModelName": "0",
            "SegmentEnd": 5967,
            "SegmentID": 20,
            "SegmentLength": 150,
            "SegmentStart": 5818,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 6241,
            "SegmentID": 21,
            "SegmentLength": 150,
            "SegmentStart": 6092,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 4,
            "ClassificationName": "No_Punch",
            "ModelName": "0",
            "SegmentEnd": 6416,
            "SegmentID": 22,
            "SegmentLength": 150,
            "SegmentStart": 6267,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 6767,
            "SegmentID": 23,
            "SegmentLength": 150,
            "SegmentStart": 6618,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 3,
            "ClassificationName": "Jab",
            "ModelName": "0",
            "SegmentEnd": 7061,
            "SegmentID": 24,
            "SegmentLength": 150,
            "SegmentStart": 6912,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 7271,
            "SegmentID": 25,
            "SegmentLength": 150,
            "SegmentStart": 7122,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 3,
            "ClassificationName": "Jab",
            "ModelName": "0",
            "SegmentEnd": 7425,
            "SegmentID": 26,
            "SegmentLength": 150,
            "SegmentStart": 7276,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 7931,
            "SegmentID": 27,
            "SegmentLength": 150,
            "SegmentStart": 7782,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 8352,
            "SegmentID": 28,
            "SegmentLength": 150,
            "SegmentStart": 8203,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 8564,
            "SegmentID": 29,
            "SegmentLength": 150,
            "SegmentStart": 8415,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 0,
            "ClassificationName": "Unknown",
            "ModelName": "0",
            "SegmentEnd": 8769,
            "SegmentID": 30,
            "SegmentLength": 150,
            "SegmentStart": 8620,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 3,
            "ClassificationName": "Jab",
            "ModelName": "0",
            "SegmentEnd": 8978,
            "SegmentID": 31,
            "SegmentLength": 150,
            "SegmentStart": 8829,
        },
        {
            "Capture": "Punching_Cross 2020-07-12 08_54_25.csv",
            "Classification": 4,
            "ClassificationName": "No_Punch",
            "ModelName": "0",
            "SegmentEnd": 9466,
            "SegmentID": 32,
            "SegmentLength": 150,
            "SegmentStart": 9317,
        },
    ]

    ytick_labels = [
        "Unknown",
        "Cross",
        "Hook",
        "Jab",
        "No_Punch",
        "Overhand",
        "Uppercut",
    ]

    expected_result = {
        "Unknown": {
            "Unknown": 0,
            "Cross": 0,
            "Uppercut": 0,
            "No_Punch": 0,
            "Jab": 0,
            "Overhand": 0,
            "Hook": 0,
            "GroundTruth_Total": 0,
        },
        "Cross": {
            "Unknown": 23,
            "Cross": 0,
            "Uppercut": 0,
            "No_Punch": 1,
            "Jab": 7,
            "Overhand": 0,
            "Hook": 0,
            "GroundTruth_Total": 31,
        },
        "Uppercut": {
            "Unknown": 0,
            "Cross": 0,
            "Uppercut": 0,
            "No_Punch": 0,
            "Jab": 0,
            "Overhand": 0,
            "Hook": 0,
            "GroundTruth_Total": 0,
        },
        "No_Punch": {
            "Unknown": 0,
            "Cross": 0,
            "Uppercut": 0,
            "No_Punch": 2,
            "Jab": 0,
            "Overhand": 0,
            "Hook": 0,
            "GroundTruth_Total": 2,
        },
        "Jab": {
            "Unknown": 0,
            "Cross": 0,
            "Uppercut": 0,
            "No_Punch": 0,
            "Jab": 0,
            "Overhand": 0,
            "Hook": 0,
            "GroundTruth_Total": 0,
        },
        "Overhand": {
            "Unknown": 0,
            "Cross": 0,
            "Uppercut": 0,
            "No_Punch": 0,
            "Jab": 0,
            "Overhand": 0,
            "Hook": 0,
            "GroundTruth_Total": 0,
        },
        "Hook": {
            "Unknown": 0,
            "Cross": 0,
            "Uppercut": 0,
            "No_Punch": 0,
            "Jab": 0,
            "Overhand": 0,
            "Hook": 0,
            "GroundTruth_Total": 0,
        },
    }

    results = compute_confusion_matrix(predicted, ground_truth, ytick_labels)
    assert results == expected_result


class MockKnowledgepack(object):
    def __init__(self):
        self._class_map = {}
        self._pipeline_summary = []

    @property
    def pipeline_summary(self):
        return self._pipeline_summary

    @property
    def class_map(self):
        return self._class_map


def test_get_modified_class_map():

    mock_kp = MockKnowledgepack()
    mock_kp._class_map = {0: "A", 1: "B", 2: "C"}
    mock_kp.knowledgepack_description = None
    mock_kp._pipeline_summary = [
        {
            "name": "Combine Labels",
            "type": "sampler",
            "inputs": {
                "input_data": "temp.generator_set0",
                "label_column": "Lable",
                "combine_labels": {"A": ["red", "blue", "green"]},
            },
        }
    ]

    result = get_modified_class_map(mock_kp)

    expected_result = {
        "A": "A",
        "red": "A",
        "blue": "A",
        "green": "A",
        "B": "B",
        "C": "C",
    }

    assert result == expected_result

    mock_kp = MockKnowledgepack()
    mock_kp._class_map = {0: "A", 1: "B", 2: "C"}
    mock_kp.knowledgepack_description = None
    mock_kp._pipeline_summary = []

    result = get_modified_class_map(mock_kp)

    expected_result = {"A": "A", "B": "B", "C": "C"}

    assert result == expected_result

    result = get_modified_class_map(mock_kp, {"0": None})
    expected_result = {"A": "A", "B": "B", "C": "C"}

    assert result == expected_result

    # =======  kp with hierarchical model ==================
    project = Project.objects.create(name="Test", team_id=1)
    sandbox = Sandbox.objects.create(name="test", project=project)

    parent_uuid = str(uuid.uuid4())
    model_2_2_uuid = str(uuid.uuid4())
    model_3_2_uuid = str(uuid.uuid4())

    kp_description = {
        "Parent": {"uuid": parent_uuid},
        "Model_2_2": {"uuid": model_2_2_uuid},
        "Model_3_2": {"uuid": model_3_2_uuid},
    }

    KnowledgePack.objects.create(
        uuid=parent_uuid,
        project=sandbox.project,
        sandbox=sandbox,
        class_map={0: "A", 1: "combined_label_1"},
        knowledgepack_description=kp_description,
    )
    KnowledgePack.objects.create(
        uuid=model_2_2_uuid,
        project=sandbox.project,
        sandbox=sandbox,
        class_map={0: "B", 1: "combined_label_1"},
    )
    KnowledgePack.objects.create(
        uuid=model_3_2_uuid,
        sandbox=sandbox,
        project=sandbox.project,
        class_map={0: "C", 1: "D"},
    )

    mock_kp = MockKnowledgepack()
    mock_kp.knowledgepack_description = kp_description
    mock_kp._class_map = {0: "A", 1: "B", 2: "C"}

    result = get_modified_class_map(mock_kp, kb_description=kp_description)
    expected_result = {"A": "A", "B": "B", "C": "C", "D": "D"}

    assert result == expected_result

    # =========== kp with custom hierarchical model ===========
    parent_uuid = str(uuid.uuid4())
    model_2_1_uuid = str(uuid.uuid4())
    model_2_2_uuid = str(uuid.uuid4())
    model_2_3_uuid = str(uuid.uuid4())
    model_3_2_uuid = str(uuid.uuid4())

    kp_description = {
        "Parent": {"uuid": parent_uuid},
        "Model_2_1": {"uuid": model_2_1_uuid},
        "Model_2_2": {"uuid": model_2_2_uuid},
        "Model_2_3": {"uuid": model_2_3_uuid},
        "Model_3_2": {"uuid": model_3_2_uuid},
    }

    KnowledgePack.objects.create(
        uuid=parent_uuid,
        sandbox=sandbox,
        project=sandbox.project,
        class_map={
            1: "combined_label_0",
            2: "combined_label_1",
            3: "combined_label_2",
            4: "A",
            5: "F",
        },
        knowledgepack_description=kp_description,
    )

    KnowledgePack.objects.create(
        uuid=model_2_1_uuid, sandbox=sandbox, class_map={0: "A", 1: "B"}
    )

    KnowledgePack.objects.create(
        uuid=model_2_2_uuid,
        project=sandbox.project,
        sandbox=sandbox,
        class_map={0: "B", 1: "combined_label_1"},
    )

    KnowledgePack.objects.create(
        uuid=model_2_3_uuid,
        project=sandbox.project,
        sandbox=sandbox,
        class_map={0: "C", 1: "D"},
    )

    KnowledgePack.objects.create(
        uuid=model_3_2_uuid,
        sandbox=sandbox,
        project=sandbox.project,
        class_map={0: "E", 1: "F"},
    )

    mock_kp = MockKnowledgepack()
    mock_kp.knowledgepack_description = kp_description
    mock_kp._class_map = {
        1: "combined_label_0",
        2: "combined_label_1",
        3: "combined_label_2",
        4: "A",
        5: "F",
    }
    result = get_modified_class_map(mock_kp, kp_description)
    expected_result = {"A": "A", "F": "F", "B": "B", "C": "C", "D": "D", "E": "E"}

    assert result == expected_result


def test_get_num_feature_banks(
    pipeline_json,
    pipeline_json_cascade_slide,
    pipeline_json_cascade_reset,
    pipeline_json_cascade_only_training,
):
    cleaned_pipeline_json, num_feature_banks, cascade_reset = get_num_feature_banks(
        pipeline_json
    )

    assert len(cleaned_pipeline_json["Feature Transforms"]) == 1
    assert num_feature_banks == 1
    assert cascade_reset == None

    cleaned_pipeline_json, num_feature_banks, cascade_reset = get_num_feature_banks(
        pipeline_json_cascade_slide
    )

    assert len(cleaned_pipeline_json["Feature Transforms"]) == 1
    assert num_feature_banks == 2
    assert cascade_reset == False

    cleaned_pipeline_json, num_feature_banks, cascade_reset = get_num_feature_banks(
        pipeline_json_cascade_reset
    )

    assert len(cleaned_pipeline_json["Feature Transforms"]) == 1
    assert num_feature_banks == 2
    assert cascade_reset == True

    cleaned_pipeline_json, num_feature_banks, cascade_reset = get_num_feature_banks(
        pipeline_json_cascade_only_training
    )

    assert len(cleaned_pipeline_json["Feature Transforms"]) == 1
    assert num_feature_banks == 2
    assert cascade_reset == True


def test_get_capture_file_does_not_exist(testprojects):
    project = Project.objects.create(
        name="APITestProject",
        team=Team.objects.get(name=TEAM_NAME),
    )

    user = TeamMember.objects.get(username="unittest@piccolo.com").user

    try:
        pipeline_utils.get_capturefiles(
            user=user, project_uuid=project.uuid, filenames=["testA", "testB"]
        )
        assert False
    except Capture.DoesNotExist as e:
        assert str(e) == "Capture testA does not exist."


def test_check_and_convert_datasegments():

    input_data = DataFrame({"A": [1, 2, 3, 4], "B": [1, 1, 1, 1]})
    step = {"name": "generator_set", "inputs": {"group_columns": ["A", "C"]}}

    result = check_and_convert_datasegments(input_data, step)

    expected = [
        {"data": array([[1]], dtype=int32), "columns": ["B"], "metadata": {"A": 1}},
        {"data": array([[1]], dtype=int32), "columns": ["B"], "metadata": {"A": 2}},
        {"data": array([[1]], dtype=int32), "columns": ["B"], "metadata": {"A": 3}},
        {"data": array([[1]], dtype=int32), "columns": ["B"], "metadata": {"A": 4}},
    ]

    assert datasegments_equal(result, expected)


def test_get_capture_file(test_project_with_capture):
    project, capture = test_project_with_capture

    user = TeamMember.objects.get(username="unittest@piccolo.com").user

    data, sample_rate = pipeline_utils.get_capturefiles(
        user=user, project_uuid=project.uuid, filenames=[capture.name]
    )

    assert list(data.columns) == ["Column_1", "Column2"]


def test_parse_capture_configuration():
    class MockCapture(object):
        def __init__(self, configuration):
            self.configuration = configuration

    capture_configuration = MockCapture(
        {
            "name": "m5Stick C Plus - Wizard Wand",
            "version": 3,
            "plugin_uuid": "1de28820-dfbc-4841-8699-eb354724c2b9",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 0,
                            "parameters": [],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": False,
                        },
                        {
                            "type": "Gyroscope",
                            "sensor_id": 0,
                            "parameters": [],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": False,
                        },
                        {
                            "type": "Gesture",
                            "sensor_id": 0,
                            "parameters": [],
                            "column_count": 1,
                            "column_names": [],
                            "can_live_stream": False,
                        },
                    ],
                    "sample_rate": 250,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        }
    )
    result = parse_capture_configuration(capture_configuration)

    expected_result = [
        "AccelerometerX",
        "AccelerometerY",
        "AccelerometerZ",
        "GyroscopeX",
        "GyroscopeY",
        "GyroscopeZ",
        "Gesture",
    ]

    assert result == expected_result


#################################################################


def test_normalize_signal():

    signal = np.zeros(1000000) + 20
    signal = normalize_signal(signal)

    assert np.mean(signal) == 1.0
    assert np.min(signal) == 1.0
    assert np.max(signal) == 1.0


def test_decimate_signal():

    signal = np.zeros(1000)

    try:
        pipeline_utils.decimate_signal(signal, 8000, 16000)
        assert False
    except ValueError as e:
        assert str(e) == "Input sample rate must be larger than output sample rate !"

    try:
        pipeline_utils.decimate_signal(signal, 16000, 7000)
        assert False
    except ValueError as e:
        assert (
            str(e)
            == "Input sampling rat (16000) must be divisible by the output sampling (7000) rate !"
        )

    out_signal = pipeline_utils.decimate_signal(signal, 16000, 8000)

    assert len(out_signal) == 500


def test_rand_sample():

    signal = np.zeros(1200) + 100
    signal[:100] = 50
    signal[-100:] = 50

    try:
        pipeline_utils.rand_sample(signal, 1000, 700)
        assert False
    except ValueError as e:
        assert str(e) == "Signal size (1200) is smaller than 2*margin (1400) !"

    try:
        pipeline_utils.rand_sample(signal, 1200, 100)
        assert False
    except ValueError as e:
        assert (
            str(e)
            == "Signal size (1200) can not be smaller than 2*margin+length (1400) !"
        )

    out_signal = pipeline_utils.rand_sample(signal, 100, 100)
    assert len(out_signal) == 100
    assert np.sum(out_signal) == 100 * 100

    out_signal = pipeline_utils.rand_sample(signal, 1100, 50)
    assert len(out_signal) == 1100
    assert np.sum(out_signal[:50]) == 50 * 50


def test_convert_int16():

    signal = np.zeros(12) + 100
    signal[:1] = MAX_INT_16 + 100
    signal[-1:] = MIN_INT_16 - 100

    signal = convert_int16(signal)

    assert signal.dtype == np.int16
    assert np.min(signal) >= MIN_INT_16
    assert np.max(signal) <= MAX_INT_16

    assert signal[0] == MAX_INT_16
    assert signal[11] == MIN_INT_16

    for i in range(1, 11):
        assert signal[i] == 100
