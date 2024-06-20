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

import pandas as pd
import pytest

import codegen.knowledgepack_codegen_mixin as codegen_mixin

pytestmark = pytest.mark.django_db  # All tests use db


@pytest.fixture
def capture_config():
    from datamanager.models import Project, CaptureConfiguration

    project_dev = Project.objects.create(
        team_id=1,
        name="DevProject22",
        capture_sample_schema={
            "Column1": {"type": "float"},
            "Column2": {"type": "float"},
        },
    )
    ranged_conf = CaptureConfiguration.objects.create(
        project=project_dev,
        name="ConfigWithRange",
        configuration={
            "version": 3,
            "name": "SAMD21 ML Evaluation Kit",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "plugin_uuid": "4a915608-c5ca-4813-890c-7d20f6e7c283",
            "capture_sources": [
                {
                    "name": "Motion (BMI160)",
                    "part": "BMI160",
                    "sample_rate": 100,
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804865,
                            "can_live_stream": True,
                        },
                        {
                            "type": "Gyroscope",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 125,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804871,
                            "can_live_stream": True,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
    )

    unranged_conf = CaptureConfiguration.objects.create(
        project=project_dev,
        name="ConfigWithoutRange",
        configuration={
            "version": 3,
            "name": "SAMD21 ML Evaluation Kit",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "plugin_uuid": "5d53948a-720f-446f-b2c8-4604a963ad45",
            "capture_sources": [
                {
                    "name": "Motion (BMI160)",
                    "part": "BMI160",
                    "sample_rate": 100,
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "parameters": [],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1,
                            "can_live_stream": False,
                        },
                        {
                            "type": "Gyroscope",
                            "parameters": [],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 2,
                            "can_live_stream": False,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
    )

    configs = {"ranged": ranged_conf, "norange": unranged_conf}

    return configs


def test_create_test_data_debugger():

    df = pd.DataFrame(
        [
            [3, 3],
            [4, 5],
            [5, 7],
            [4, 6],
            [3, 1],
            [3, 1],
            [4, 3],
            [5, 5],
            [4, 7],
            [3, 6],
        ],
        columns=["accelx", "accely"],
    )

    cgm = codegen_mixin.CodeGenMixin()

    result = cgm.create_test_data_debugger(df, ["accelx", "accely"])
    print(result)

    expected_result = {
        "test_data_h": [
            "#define USE_TEST_RAW_SAMPLES",
            "#define TD_NUMROWS 10",
            "#define TD_NUMCOLS 2",
            "const short testdata[TD_NUMROWS][TD_NUMCOLS] = ",
            "{",
            "{3,3,},",
            "{4,5,},",
            "{5,7,},",
            "{4,6,},",
            "{3,1,},",
            "{3,1,},",
            "{4,3,},",
            "{5,5,},",
            "{4,7,},",
            "{3,6,},",
            "};",
        ]
    }

    assert result == expected_result


def test_create_model_ranges(capture_config):

    cgm = codegen_mixin.CodeGenMixin()
    model = {"capture_configuration": capture_config["ranged"]}

    result = cgm.get_model_ranges(model)
    print(result)
    expected_result = {"accelerometer_sensor_range": 2, "gyroscope_sensor_range": 125}

    assert result == expected_result

    model = {"capture_configuration": capture_config["norange"]}

    result = cgm.get_model_ranges(model)
    print(result)
    expected_result = dict()

    assert result == expected_result
