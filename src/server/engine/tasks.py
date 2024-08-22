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
import os
import pickle
import sys
import time
import traceback
from functools import wraps

from celery import Task, shared_task
from celery.signals import task_revoked
from datamanager.models import Sandbox
from django.conf import settings
from django.db.models import F
from engine.base.pipeline_utils import check_and_convert_datasegments, make_summary
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class NoDataException(Exception):
    pass


class BaseTask(Task):
    abstract = True

    @staticmethod
    def get_ecs_agent_arn():
        if os.environ.get("ECS_AGENT_URI"):
            return os.environ.get("ECS_AGENT_URI").split("/")[-1].split("-")[0]

        return None


def active_task_counter(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        from engine.base.temp_counter import TempSet

        hostname = self.request.hostname
        TempSet(hostname).set_add(self.request.id)
        try:
            result = func(self, *args, **kwargs)
        except Exception as e:
            TempSet(hostname).set_remove(self.request.id)
            raise e
        TempSet(hostname).set_remove(self.request.id)

        return result

    return wrapper


def get_feature_table_key(step):
    if "set" in step:
        feature_table_key = step["inputs"].get("feature_table", None)
    else:
        feature_table_key = step.get("feature_table", None)

    if feature_table_key:
        feature_table_key += ".csv.gz"

    return feature_table_key


def has_feature_table(step):
    if len(step["outputs"]) > 1:
        return True

    return False


def pop_input_data_key(step):
    if step.get("inputs", None):
        return step["inputs"].pop("input_data")
    elif step.get("input_data", None):
        return step["input_data"]

    return None


@task_revoked.connect
def task_revoked_handler(sender=None, request=None, **kwargs):
    from engine.base.temp_counter import TempSet

    if "steps" in request.hostname:
        TempSet(request.hostname).set_remove(request.id)


@shared_task(bind=True, acks_late=True, base=BaseTask, track_started=True)
@active_task_counter
def execute_function_return_success(
    self, pickled_function, step, team_id, project_id, pipeline_id, user_id, **kwargs
):
    from engine.base.temp_cache import TempCache

    start_time = time.time()

    logger.userlog(
        {
            "message": "Executing Step: {name}".format(name=step["name"]),
            "data": step,
            "log_type": "PID",
            "UUID": pipeline_id,
            "team_id": team_id,
            "user_id": user_id,
            "task_id": self.request.parent_id,
            "child_task_id": self.request.id,
        }
    )

    try:
        func = pickle.loads(pickled_function)

        temp_cache = TempCache(pipeline_id=pipeline_id)

        input_data_key = pop_input_data_key(step)

        input_data = temp_cache.get_file(input_data_key)

        input_data = check_and_convert_datasegments(input_data, step)

        step["feature_table_value"] = temp_cache.get_file(get_feature_table_key(step))

        data, feature_table = func(
            input_data,
            step,
            team_id,
            project_id,
            pipeline_id,
            user_id,
            self.request.parent_id,
            **kwargs,
        )

        if isinstance(data, DataFrame) and data.shape[0] == 0:
            raise NoDataException(
                f"No data was generated from this step {step['name']}"
            )

        filename = temp_cache.write_file(data, step["outputs"][0])

        if has_feature_table(step):
            if not isinstance(feature_table, DataFrame):
                feature_table = DataFrame(feature_table)
            feature_table_name = temp_cache.write_file(
                feature_table, step["outputs"][1]
            )

    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        step.pop("feature_table_value", None)
        logger.warn(
            {
                "message": "Error Executing Step: {name}".format(name=step["name"]),
                "data": {"error": e, "traceback": s_traceback, "step": step},
                "log_type": "PID",
                "UUID": pipeline_id,
                "task_id": self.request.parent_id,
                "child_task_id": self.request.id,
                "team_id": team_id,
                "user_id": user_id,
                "project_id": project_id,
            }
        )
        if settings.DEBUG_FUNCTIONS:
            raise e

        return (None, e.__str__())

    cpu_clock_time = time.time() - start_time

    try:
        pipeline = Sandbox.objects.get(uuid=pipeline_id)
        pipeline.cpu_clock_time = F("cpu_clock_time") + cpu_clock_time
        pipeline.save(update_fields=["cpu_clock_time"])
    except Sandbox.DoesNotExist:
        pass

    logger.userlog(
        {
            "message": "Finished Executing Step: {name}".format(name=step["name"]),
            "data": {
                "name": step["name"],
                "cpu_clock_time": cpu_clock_time,
                "data_size": (
                    len(data) if not isinstance(data, DataFrame) else data.shape[0]
                ),
                "input": input_data_key,
                "output": filename,
            },
            "UUID": pipeline_id,
            "task_id": self.request.parent_id,
            "child_task_id": self.request.id,
            "team_id": team_id,
            "user_id": user_id,
            "project_id": project_id,
            "log_type": "PID",
        }
    )

    return (1, make_summary(data, filename))


@shared_task(bind=True, acks_late=True, base=BaseTask, track_started=True)
@active_task_counter
def execute_function(
    self, pickled_function, step, team_id, project_id, pipeline_id, user_id, **kwargs
):
    from engine.base.temp_cache import TempCache

    start_time = time.time()

    logger.userlog(
        {
            "message": "Executing Step: {name}".format(name=step["name"]),
            "data": step,
            "log_type": "PID",
            "UUID": pipeline_id,
            "team_id": team_id,
            "user_id": user_id,
            "project_id": project_id,
            "task_id": self.request.parent_id,
            "child_task_id": self.request.id,
        }
    )

    try:
        func = pickle.loads(pickled_function)

        temp_cache = TempCache(pipeline_id=pipeline_id)

        input_data_key = pop_input_data_key(step)
        input_data = temp_cache.get_file(input_data_key)

        input_data = check_and_convert_datasegments(input_data, step)

        step["feature_table_value"] = temp_cache.get_file(get_feature_table_key(step))

        data, feature_table = func(
            input_data,
            step,
            team_id,
            project_id,
            pipeline_id,
            user_id,
            self.request.parent_id,
            **kwargs,
        )

    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        step.pop("feature_table_value", None)
        logger.warn(
            {
                "message": "Error Executing Step: {name}".format(name=step["name"]),
                "data": {"error": e, "traceback": s_traceback, "step": step},
                "log_type": "PID",
                "UUID": pipeline_id,
                "team_id": team_id,
                "user_id": user_id,
                "project_id": project_id,
                "task_id": self.request.parent_id,
                "child_task_id": self.request.id,
            }
        )

        if settings.DEBUG_FUNCTIONS:
            raise e

        return (None, e.__str__())

    cpu_clock_time = time.time() - start_time

    try:
        pipeline = Sandbox.objects.get(uuid=pipeline_id)
        pipeline.cpu_clock_time = F("cpu_clock_time") + cpu_clock_time
        pipeline.save(update_fields=["cpu_clock_time"])
    except Sandbox.DoesNotExist:
        pass

    logger.userlog(
        {
            "message": "Finished Executing Step: {name}".format(name=step["name"]),
            "data": {
                "name": step["name"],
                "cpu_clock_time": cpu_clock_time,
                "data_size": (
                    len(data) if not isinstance(data, DataFrame) else data.shape[0]
                ),
                "data": input_data_key,
            },
            "UUID": pipeline_id,
            "log_type": "PID",
            "team_id": team_id,
            "user_id": user_id,
            "task_id": self.request.parent_id,
            "child_task_id": self.request.id,
        }
    )

    return (1, data)


@shared_task(bind=True, acks_late=True, base=BaseTask)
def sleep_time(self, sleep, sleep_times=5, **kwargs):
    import time

    start = time.time()

    logger.info(
        {
            "message": "Starting Sleep",
            "data": {
                "start_time": start,
            },
            "log_type": "autoscaling",
        }
    )

    for index in range(sleep_times):
        logger.info(
            {
                "message": "Still sleeping Sleep",
                "data": {"elapsed_time": time.time() - start, "index": index},
                "log_type": "autoscaling",
            }
        )
        time.sleep(sleep)

    logger.info(
        {
            "message": "Finishing Sleep",
            "data": {
                "elapsed_time": time.time() - start,
            },
            "log_type": "autoscaling",
        }
    )
