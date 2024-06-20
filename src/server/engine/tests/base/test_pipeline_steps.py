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

# coding=utf-8
import logging
import time

import pytest
from datamanager.models import TeamMember
from engine.base import pipeline_steps
from engine.base.temp_cache import TempCache

logger = logging.getLogger(__name__)
import time

pytestmark = pytest.mark.django_db  # All tests use db


def get_template(sleep_time):
    return {
        "name": "Sleep",
        "type": "segmenter",
        "feature_table": None,
        "inputs": {
            "input_data": "temp0.pkl",
            "sleep_time": sleep_time,
        },
        "outputs": ["temp.Windowing0"],
    }


def sleep_func(
    input_data, step, team_id, project_id, pipeline_id, user_id, task_id, **kwargs
):

    sleep_time = step["inputs"]["sleep_time"]
    time.sleep(sleep_time)

    return [sleep_time], None


@pytest.mark.skip("Only run this locally")
def test_pipeline_step(test_project_simple):

    project, pipeline = test_project_simple

    user = TeamMember.objects.filter(team=project.team)[0]

    steps = []
    sleep_times = [1, 1, 1, 10, 1, 5, 1, 5, 1, 1, 1, 1]
    for sleep_time in sleep_times:
        steps.append(get_template(sleep_time))

    temp_cache = TempCache(pipeline_id=pipeline.uuid)

    temp_cache.write_file([1, 2, 3, 4], "temp1")

    result_set = pipeline_steps.parallel_pipeline_step(
        sleep_func,
        steps,
        project.team.uuid,
        project.uuid,
        pipeline.uuid,
        user,
        return_results=True,
    )

    for index, result in enumerate(result_set):
        assert result[1][0] == sleep_times[index]

    print(result_set)

    start = time.time()
    result_set = pipeline_steps.parallel_pipeline_step(
        sleep_func,
        steps,
        project.team.uuid,
        project.uuid,
        pipeline.uuid,
        user,
        return_results=False,
    )
    print("Total Time Step", time.time() - start)

    expected_result = [(1, "temp.Windowing0.pkl") for _ in range(len(sleep_times))]

    assert result_set == expected_result

    start = time.time()
    result_set = pipeline_steps.parallel_pipeline_step_group(
        sleep_func,
        steps,
        project.team.uuid,
        project.uuid,
        pipeline.uuid,
        user,
        return_results=False,
    )
    print("Total Time Group", time.time() - start)

    start = time.time()
    result_set = pipeline_steps.parallel_pipeline_step_batch(
        sleep_func,
        steps,
        project.team.uuid,
        project.uuid,
        pipeline.uuid,
        user,
        return_results=False,
    )
    print("Total Time Batch", time.time() - start)

    steps = []
    sleep_times = [1, "A", 1, 1]
    for sleep_time in sleep_times:
        steps.append(get_template(sleep_time))

    result_set = pipeline_steps.parallel_pipeline_step(
        sleep_func,
        steps,
        project.team.uuid,
        project.uuid,
        pipeline.uuid,
        user,
        return_results=False,
    )

    expected_result = [
        (1, "temp.Windowing0.pkl"),
        (None, "an integer is required (got type str)"),
        (1, "temp.Windowing0.pkl"),
        (1, "temp.Windowing0.pkl"),
    ]

    assert result_set == expected_result

    print(result_set)

    start = time.time()
    result_set = pipeline_steps.parallel_pipeline_step_group(
        sleep_func,
        steps,
        project.team.uuid,
        project.uuid,
        pipeline.uuid,
        user,
        return_results=False,
    )
    print("Total Time", time.time() - start)

    expected_result = [
        (1, "temp.Windowing0.pkl"),
        (None, "an integer is required (got type str)"),
        (1, "temp.Windowing0.pkl"),
        (1, "temp.Windowing0.pkl"),
    ]

    assert result_set == expected_result

    print(result_set)
