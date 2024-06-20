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
import pickle
import queue
import time

from celery import group
from datamanager.pipeline_queue import (
    remove_pipeline_subtask_ids,
    set_pipeline_subtask_ids,
)
from django.conf import settings
from engine.tasks import execute_function, execute_function_return_success
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


def pipeline_step(input_data, func, steps, pipeline_id, task_id):
    """A single pipeline step that returns results from multiple parallel steps that take the same input data"""
    results = []
    for step in steps:
        # logger.userlog(
        #    {
        #        "message": "Running Pipeline Step",
        #        "data": step,
        #        "UUID": pipeline_id,
        #        "log_type": "PID",
        #        "task_id": task_id,
        #    }
        # )

        data = func(input_data, step, pipeline_id)

        results.append(data)

    return results


def parallel_pipeline_step_group(
    func,
    steps,
    team_id,
    project_id,
    pipeline_id,
    user_id,
    return_results=True,
    **kwargs,
):
    """A parallel implementation of the pipeline step"""

    if return_results:
        jobs = group(
            execute_function.s(
                pickle.dumps(func),
                step,
                team_id,
                project_id,
                pipeline_id,
                user_id,
                **kwargs,
            )
            for step in steps
        )
    else:
        jobs = group(
            execute_function_return_success.s(
                pickle.dumps(func),
                step,
                team_id,
                project_id,
                pipeline_id,
                user_id,
                **kwargs,
            )
            for step in steps
        )

    result_set = jobs.apply_async(serializer="pickle")

    set_pipeline_subtask_ids(
        pipeline_id, [subtask.id for subtask in result_set.children]
    )

    while not result_set.ready():
        time.sleep(1)

    results = [x for x in result_set.join_native(disable_sync_subtasks=False)]

    # clean up the celery meta tasks after we have retrieved the results

    result_set.forget()
    remove_pipeline_subtask_ids(pipeline_id)

    return results


def parallel_pipeline_step(
    func,
    steps,
    team_id,
    project_id,
    pipeline_id,
    user_id,
    return_results=True,
    max_batch_size=None,
    **kwargs,
):
    """A parallel implementation of the pipeline step with a batch size"""

    if return_results:
        jobs = [
            execute_function.s(
                pickle.dumps(func),
                step,
                team_id,
                project_id,
                pipeline_id,
                user_id,
                **kwargs,
            )
            for step in steps
        ]
    else:
        jobs = [
            execute_function_return_success.s(
                pickle.dumps(func),
                step,
                team_id,
                project_id,
                pipeline_id,
                user_id,
                **kwargs,
            )
            for step in steps
        ]

    job_queue = queue.Queue()
    for item in range(len(jobs)):
        job_queue.put(item)

    result_set = [None for _ in range(len(jobs))]
    running_jobs = {}

    while not job_queue.empty():
        # print(f"Queue Size: {job_queue.qsize()} Running Jobs: {len(running_jobs)}")
        if (
            len(running_jobs) <= settings.MAX_BATCH_SIZE
            if max_batch_size is None
            else max_batch_size
        ):
            job_id = job_queue.get()
            # print(f"Adding Job : {job_id}")
            running_jobs[job_id] = jobs[job_id].apply_async(serializer="pickle")

            set_pipeline_subtask_ids(
                pipeline_id, [t.task_id for t in running_jobs.values()]
            )
        else:
            time.sleep(1)
            # print(f"Reached Max Queue Size: {settings.MAX_BATCH_SIZE}")
            for job_id in list(running_jobs.keys()):
                if running_jobs[job_id].ready():
                    finished_job = running_jobs.pop(job_id)
                    result_set[job_id] = finished_job.result
                    # print(f"Job {job_id} Result: {result_set[job_id]}")
                    finished_job.forget()

    # print(f"All jobs Queued")

    while len(running_jobs) > 0:
        for job_id in list(running_jobs.keys()):
            if running_jobs[job_id].ready():
                finished_job = running_jobs.pop(job_id)
                result_set[job_id] = finished_job.result
                # print(f"Job {job_id} Result: {result_set[job_id]}")
                finished_job.forget()

        time.sleep(2)

    remove_pipeline_subtask_ids(pipeline_id)

    return result_set


def parallel_pipeline_step_batch(
    func,
    steps,
    team_id,
    project_id,
    pipeline_id,
    user_id,
    return_results=True,
    **kwargs,
):
    """A parallel implementation of the pipeline step with a batch size"""

    batch_size = settings.MAX_BATCH_SIZE

    num_batches = len(steps) // batch_size
    results = []

    for batch in range(num_batches):
        results.extend(
            parallel_pipeline_step_group(
                func,
                steps[batch * batch_size : (batch + 1) * batch_size],
                team_id,
                project_id,
                pipeline_id,
                user_id,
                return_results,
                **kwargs,
            )
        )

    if len(steps) - (num_batches * batch_size) > 0:
        results.extend(
            parallel_pipeline_step_group(
                func,
                steps[num_batches * batch_size :],
                team_id,
                project_id,
                pipeline_id,
                user_id,
                return_results,
                **kwargs,
            )
        )

    return results
