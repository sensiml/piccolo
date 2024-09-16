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
import logging
import pickle
from time import time

from celery.result import AsyncResult
from datamanager.models import Query, Sandbox
from django.conf import settings
from engine.base.temp_table import TempVariableTable
from logger.log_handler import LogHandler
from redis import StrictRedis

from server.celery import app

logger = LogHandler(logging.getLogger(__name__))


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


class PipelineException(Exception):
    pass


class EmptyAsyncResult:
    """this is an empty result for when we do not have the pipeline status"""

    def __init__(self):
        self.status = None
        self.task_id = None
        self.worker = None

    def revoke(self, *args, **kwargs):
        return None


def set_value(name, value):
    red = StrictRedis(settings.REDIS_ADDRESS)
    red.set(name, pickle.dumps(value))


def delete_value(name):
    red = StrictRedis(settings.REDIS_ADDRESS)
    red.delete(name)


def get_value(name):
    red = StrictRedis(settings.REDIS_ADDRESS)
    value = red.get(name)
    if value is None:
        return None
    else:
        return pickle.loads(value)


def get_sandbox_status(project_id, sandbox_id):
    name = "sandbox.status.{}.{}".format(project_id, sandbox_id)
    return get_value(name)


def set_sandbox_status(
    project_id, sandbox_id, status="SUCCESS", value=None, worker_pid=None
):
    name = "sandbox.status.{}.{}".format(project_id, sandbox_id)
    set_value(name, [status, time(), value, worker_pid])


def update_sandbox_value(project_id, sandbox_id, value=None):
    name = "sandbox.status.{}.{}".format(project_id, sandbox_id)

    # Note: this could be done in a single call if we switched to redist list datatype
    #      not sure that it matters for now
    stored_data = get_value(name)

    if stored_data is None:
        logger.error(
            {
                "log_type": "pipeline_utils",
                "message": f"update_sandbox_value stored data was null for {project_id}:{sandbox_id} failed to set value.",
            }
        )
        return

    if isinstance(stored_data, list) and len(stored_data) >= 3:
        stored_data[2] = value
        set_value(name, stored_data)


def remove_sandbox_from_queue(project_id, sandbox_id):
    name = "sandbox.status.{}.{}".format(project_id, sandbox_id)
    delete_value(name)


def kill_sandbox(project_id, sandbox_id):
    remove_sandbox_from_queue(project_id, sandbox_id)

    set_pipeline_to_not_active(project_id, sandbox_id)

    return revoke_task(project_id, sandbox_id)


def kill_query(project_id, query_id):
    remove_sandbox_from_queue(project_id, query_id)

    set_query_to_not_active(project_id, query_id)

    return revoke_task(project_id, query_id)


def revoke_task(project_id, task_id):
    result = get_pipeline_task_id_status(project_id, task_id)

    result.revoke(terminate=True)

    subtask_results = get_pipeline_subtask_status(task_id)

    for subtask_result in subtask_results:
        subtask_result.revoke(terminate=True)

    temp = TempVariableTable(task_id)
    temp.clean_up_temp()

    return result


def get_pipeline_task_id_status(project_id, sandbox_id):
    name = "pipeline.task_id.{}.{}".format(project_id, sandbox_id)
    process_id = get_value(name)
    if process_id is None:
        return EmptyAsyncResult()
    return AsyncResult(process_id, app=app)


def set_pipeline_task_id(project_id, sandbox_id, process_id=None):
    name = "pipeline.task_id.{}.{}".format(project_id, sandbox_id)
    set_value(name, process_id)


def remove_pipeline_task_id(project_id, sandbox_id):
    name = "pipeline.task_id.{}.{}".format(project_id, sandbox_id)
    delete_value(name)


def get_pipeline_subtask_status(sandbox_id):
    name = "pipeline.subtasks.{}".format(sandbox_id)
    subtask_ids = get_value(name)
    if subtask_ids is None:
        return [EmptyAsyncResult()]
    return [AsyncResult(subtask_id, app=app) for subtask_id in subtask_ids]


def set_pipeline_subtask_ids(sandbox_id, subtask_ids=None):
    name = "pipeline.subtasks.{}".format(sandbox_id)
    set_value(name, subtask_ids)


def remove_pipeline_subtask_ids(sandbox_id):
    name = "pipeline.subtasks.{}".format(sandbox_id)
    delete_value(name)


def set_start_sandbox(project_id, sandbox_id):
    name = "sandbox.status.{}.{}".format(project_id, sandbox_id)
    value = get_value(name)

    if value in [None, "SUCCESS", "REVOKED", "FAILURE"]:
        set_sandbox_status(project_id, sandbox_id, status="PENDING")
    else:
        raise PipelineException(
            "Pipeline currently executing. Use stop_pipeline() to terminate. status: {status}".format(
                status=value
            )
        )


def render_detail(status, detail):
    message = [f"Status: {status}"]

    if "time" in detail:
        message.append(f"Time: {detail['time']}")

    if "iteration" in detail and "total_iterations" in detail:
        if detail["iteration"] == "RCL":
            return f"Retraining models on best hyperparameters..."

        else:
            message.append(
                f"Iteration {detail['iteration']}/{detail['total_iterations']}"
            )

    if "step_index" in detail and "total_steps" in detail:
        message.append(f"Step: {detail['step_index']}/{detail['total_steps']}")

    if "step_name" in detail:
        if detail["step_name"] == "generator_set":
            message.append(f"Name: Feature Generator")
        elif detail["step_name"] == "tvo":
            message.append(f"Name: Model Training")
        elif detail["step_name"] == "selector_set":
            message.append(f"Name: Feature Selection")
        else:
            message.append(f"Name: {detail['step_name']}")

    if "batch" in detail:
        message.append(f"Batches: {detail['batch']}")

    if "population_size" in detail:
        message.append(f"Population: {detail['population_size']}")

    return ", ".join(message)


def get_pipeline_status(project_id, sandbox_id):
    result = get_pipeline_task_id_status(project_id, sandbox_id)
    pipeline_status = result.status

    detail = None
    # Pending in celery means non existent or still waiting to be
    # Executed. Check Here For this info
    if pipeline_status in ["PENDING", "SENT", "STARTED"]:
        pipeline_info = get_sandbox_status(project_id, sandbox_id)

        if pipeline_info is None:
            pipeline_status = None
            message = None

        elif settings.DEBUG and len(pipeline_info) != 4:
            raise Exception(pipeline_info)

        elif pipeline_info[2]:
            detail = json.loads(pipeline_info[2])
            detail["time"] = convert(time() - float(pipeline_info[1]))
            message = render_detail("Running", detail)

        else:
            message = f"Status: Waiting in the Queue - Time: {convert(time() - float(pipeline_info[1]))}"
            detail = {"time": convert(time() - float(pipeline_info[1]))}

    elif pipeline_status == "FAILURE":
        detail = result.info.args[0]
        if isinstance(detail, str):
            error = detail
            detail = {}
        else:
            error = detail.pop("error", "")
        message = f"Status: Failed - {error}"

    elif pipeline_status == "SUCCESS":
        message = result.get()

    elif pipeline_status == "REVOKED":
        message = "\nStatus: Pipeline was terminated."

    else:
        message = None

    return pipeline_status, message, detail


def get_is_pipeline_active(project_uuid, sandbox_uuid):
    result = get_pipeline_task_id_status(project_uuid, sandbox_uuid)
    pipeline_status = result.status
    return pipeline_status in ["PENDING", "SENT", "STARTED"]


def set_pipeline_to_active(project_uuid, sandbox_uuid, execution_type):
    sandbox = Sandbox.objects.get(uuid=sandbox_uuid)
    sandbox.active = True
    sandbox.save(update_fields=["active"])


def set_pipeline_to_not_active(project_id, sandbox_id):
    sandbox = Sandbox.objects.get(uuid=sandbox_id)
    sandbox.active = False
    sandbox.save(update_fields=["active"])


def set_query_to_active(project_uuid, query_uuid, execution_type):
    query = Query.objects.get(uuid=query_uuid)

    query.active = True
    query.save(update_fields=["active"])


def set_query_to_not_active(project_id, query_id):
    query = Query.objects.get(uuid=query_id)

    query.active = False
    query.save(update_fields=["active"])


def set_task_status(task_name, uuid, status="SUCCESS", value=None, worker_pid=None):
    name = f"{task_name}.status.{uuid}"

    set_value(name, [status, time(), value, worker_pid])


def set_task_id(task_name, uuid, process_id=None):
    name = f"{task_name}.task_id.{uuid}"

    set_value(name, process_id)


def set_start_task(task_name, uuid):
    name = f"{task_name}.status.{uuid}"
    value = get_value(name)

    if value in [None, "SUCCESS", "REVOKED", "FAILURE"]:
        set_task_status(task_name, uuid, status="PENDING")
    else:
        raise PipelineException(
            "Currently executing. status: {status}".format(status=value)
        )


def get_subtask_status(task_name, uuid):
    name = f"{task_name}.subtasks.{uuid}"
    subtask_ids = get_value(name)
    if subtask_ids is None:
        return [EmptyAsyncResult()]
    return [AsyncResult(subtask_id, app=app) for subtask_id in subtask_ids]


def revoke_task_processes(task_name, uuid):
    result = get_task_id_status(task_name, uuid)

    result.revoke(terminate=True)

    subtask_results = get_subtask_status(task_name, uuid)

    for subtask_result in subtask_results:
        subtask_result.revoke(terminate=True)

    return result


def remove_task_from_queue(task_name, uuid):
    name = "{task_name}.status.{uuid}"
    delete_value(name)


def kill_task(task_name, uuid):
    remove_task_from_queue(task_name, uuid)

    return revoke_task_processes(task_name, uuid)


def get_task_id_status(task_name, uuid):
    name = f"{task_name}.task_id.{uuid}"
    process_id = get_value(name)
    if process_id is None:
        return EmptyAsyncResult()
    return AsyncResult(process_id, app=app)


def get_task_status_value(task_name, uuid):
    name = f"{task_name}.status.{uuid}"
    return get_value(name)


def get_task_status(task_name, uuid):
    result = get_task_id_status(task_name, uuid)
    task_status = result.status

    detail = None
    # Pending in celery means non existent or still waiting to be
    # Executed. Check Here For this info
    if task_status in ["PENDING", "SENT", "STARTED"]:
        task_info = get_task_status_value(task_name, uuid)

        if task_info is None:
            task_status = None
            message = []

        elif task_info[2]:
            message = f"Status: Running, Time: {convert(time() - float(task_info[1]))}"

            message += task_info[2]

        else:
            message = f"Status: Waiting in the Queue -- Wait Time: {convert(time() - float(task_info[1]))}"

    elif task_status == "FAILURE":
        message = result.info
        # detail =    result.traceback

    elif task_status == "SUCCESS":
        message = result.get()

    elif task_status == "REVOKED":
        message = "\nStatus: Terminated"

    else:
        message = None

    return task_status, message, detail
