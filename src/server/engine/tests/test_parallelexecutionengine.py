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

import os
import uuid

import pytest
from datamanager.datasegments import datasegments_equal, load_datasegments
from datamanager.models import PipelineExecution
from django.conf import settings
from django.contrib.auth.models import User
from engine.parallelexecutionengine import ParallelExecutionEngine
from numpy import array, int32
from pandas import DataFrame


@pytest.mark.django_db(transaction=True)
def test_map_capturefiles(test_project_simple):
    project, sandbox = test_project_simple
    user = User.objects.get(username="unittest@piccolo.com")

    engine = ParallelExecutionEngine(
        task_id=uuid.uuid4(),
        user=user,
        project_id=project.uuid,
        sandbox=sandbox,
        execution_type=PipelineExecution.ExecutionTypeEnum.AUTOML,
    )

    engine.init_cache_manager([])

    data = DataFrame({"Ax": [100] * 10})
    output_name = "temp.raw"
    cache_index = 1
    filename = "test_file.csv"
    capture_uuid = "12345"
    fill_group_columns = ["capture_uuid", "capture_name", "Subject", "random"]
    results, cache_index = engine.map_capturefiles(
        data,
        output_name,
        cache_index,
        filename,
        capture_uuid,
        fill_group_columns=fill_group_columns,
    )

    expected_results = [
        (
            1,
            {
                "filename": "temp.raw.data_1.pkl",
                "total_segments": 1,
                "total_samples": 10,
                "distribution_segments": {"Label": 1},
                "distribution_samples": {"Label": 10},
                "type": "datasegments",
            },
        )
    ]

    assert results == expected_results

    data_segments = load_datasegments(
        os.path.join(
            settings.SERVER_CACHE_ROOT,
            "00000000-0000-0000-0000-000000000000",
            "temp.raw.data_1.pkl",
        )
    )

    expected_results = [
        {
            "data": array(
                [[100, 100, 100, 100, 100, 100, 100, 100, 100, 100]], dtype=int32
            ),
            "columns": ["Ax"],
            "metadata": {
                "capture_uuid": "12345",
                "capture_name": "test_file.csv",
                "Subject": "test_file.csv",
                "random": 1,
            },
        }
    ]

    datasegments_equal(expected_results, data_segments)

    data = DataFrame({"Ax": [100] * 10})
    output_name = "temp.raw"
    cache_index = 2
    filename = "test_file.csv"
    capture_uuid = "12345"
    fill_group_columns = None
    results, cache_index = engine.map_capturefiles(
        data,
        output_name,
        cache_index=cache_index,
        filename=filename,
        capture_uuid=capture_uuid,
        fill_group_columns=fill_group_columns,
    )

    expected_results = [
        (
            1,
            {
                "filename": "temp.raw.data_2.pkl",
                "total_segments": 1,
                "total_samples": 10,
                "distribution_segments": {"Label": 1},
                "distribution_samples": {"Label": 10},
                "type": "datasegments",
            },
        )
    ]
    assert results == expected_results

    data_segments = load_datasegments(
        os.path.join(
            settings.SERVER_CACHE_ROOT,
            "00000000-0000-0000-0000-000000000000",
            "temp.raw.data_2.pkl",
        )
    )

    expected_results = [
        {
            "data": array(
                [[100, 100, 100, 100, 100, 100, 100, 100, 100, 100]], dtype=int32
            ),
            "columns": ["Ax"],
            "metadata": {
                "capture_uuid": "12345",
                "capture_name": "test_file.csv",
                "Subject": "test_file.csv",
                "segment_uuid": data_segments[0]["metadata"]["segment_uuid"],
            },
        }
    ]

    datasegments_equal(expected_results, data_segments)


@pytest.mark.django_db(transaction=True)
def test_map_datafiles(test_project_simple):
    project, sandbox = test_project_simple
    user = User.objects.get(username="unittest@piccolo.com")

    engine = ParallelExecutionEngine(
        task_id=uuid.uuid4(),
        user=user,
        project_id=project.uuid,
        sandbox=sandbox,
        execution_type=PipelineExecution.ExecutionTypeEnum.AUTOML,
    )

    engine.init_cache_manager([])

    data = DataFrame({"Ax": [100] * 10, "Ay": [200] * 10, "Subject": [5] * 5 + [6] * 5})
    output_name = "temp.raw"
    cache_index = 1
    filename = "test_file.csv"
    group_columns = ["Subject"]
    data_columns = ["Ax", "Ay"]

    results, cache_index = engine.map_datafiles(
        data,
        output_name,
        cache_index,
        filename,
        group_columns=group_columns,
        data_columns=data_columns,
    )

    expected_results = [
        (
            1,
            {
                "filename": "temp.raw.data_1.pkl",
                "total_segments": 2,
                "total_samples": 10,
                "distribution_segments": {"Label": 2},
                "distribution_samples": {"Label": 10},
                "type": "datasegments",
            },
        )
    ]

    assert results == expected_results

    data_segments = load_datasegments(
        os.path.join(
            settings.SERVER_CACHE_ROOT,
            "00000000-0000-0000-0000-000000000000",
            "temp.raw.data_1.pkl",
        )
    )

    expected_results = [
        {
            "data": array(
                [[100, 100, 100, 100, 100], [200, 200, 200, 200, 200]], dtype=int32
            ),
            "columns": ["Ax", "Ay"],
            "metadata": {"Subject": 5},
        },
        {
            "data": array(
                [[100, 100, 100, 100, 100], [200, 200, 200, 200, 200]], dtype=int32
            ),
            "columns": ["Ax", "Ay"],
            "metadata": {"Subject": 6},
        },
    ]

    datasegments_equal(expected_results, data_segments)

    data = DataFrame({"Ax": [100] * 10, "Ay": [200] * 10, "Subject": [5] * 5 + [6] * 5})
    output_name = "temp.raw"
    cache_index = 1
    filename = "test_file.csv"
    group_columns = ["Subject"]
    data_columns = ["Ax", "Ay", "Az"]

    map_fails = False
    try:
        results, cache_index = engine.map_datafiles(
            data,
            output_name,
            cache_index,
            filename,
            group_columns=group_columns,
            data_columns=data_columns,
        )
    except:
        map_fails = True

    assert map_fails
