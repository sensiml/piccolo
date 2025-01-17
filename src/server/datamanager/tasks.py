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

from __future__ import absolute_import

import base64
import logging
import os
import sys
import time
import traceback
from collections import deque

import datamanager.pipeline_queue as pipeline_queue
from billiard import current_process
from celery import Task, shared_task
from datamanager.exceptions import (
    KnowledgeBuilderException,
    KnowledgePackGenerationError,
)
from datamanager.models import KnowledgePack, PipelineExecution, Project, Query
from datamanager.utils.model_utils import _locate_sandbox
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from engine.base.pipeline_utils import (
    add_background,
    get_background,
    get_backgroundfile,
    get_capturefile,
    get_capturefile_labels,
    get_capturefile_sizes,
    get_capturefiles,
    get_featurefile,
    get_modified_class_map,
    get_recognize_confusion_matrix,
    reindex_recognize_file,
)
from library.models import CustomTransform
from logger.data_logger import usage_log
from logger.log_handler import LogHandler
from rest_framework.exceptions import NotFound


logger = LogHandler(logging.getLogger(__name__))


class UnlockSandboxTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            pipeline_execution = PipelineExecution.objects.get(task_id=task_id)
            pipeline_execution.status = PipelineExecution.ExecutionStatusEnum.FAILED
            pipeline_execution.save(update_fields=["status"])
        except Exception as e:
            project_id = args[0][1]
            sandbox_id = args[0][2]
            logger.errorlog(
                {
                    "message": "Failed to set Pipeline Execution status to failed",
                    "error": str(e),
                    "log_type": "PID",
                    "sandbox_uuid": sandbox_id,
                    "task_id": task_id,
                    "project_uuid": project_id,
                    "status": "Failed",
                }
            )

    def after_return(self, status, retval, task_id, *args, **kwargs):
        project_id = args[0][1]
        sandbox_id = args[0][2]

        try:
            pipeline_queue.set_pipeline_to_not_active(project_id, sandbox_id)
        except Exception as e:
            logger.errorlog(
                {
                    "message": "Error Setting pipeline to not active",
                    "error": str(e),
                    "log_type": "PID",
                    "sandbox_uuid": sandbox_id,
                    "task_id": task_id,
                    "project_uuid": project_id,
                    "status": status,
                }
            )

        pipeline_queue.remove_sandbox_from_queue(project_id, sandbox_id)

        logger.userlog(
            {
                "message": "Unlocking Sandbox Thread",
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": task_id,
                "project_uuid": project_id,
                "status": status,
            }
        )


class UnlockAutosegmentationTask(Task):
    abstract = True

    def after_return(self, status, retval, task_id, *args, **kwargs):
        project_id = args[0][1]
        sandbox_id = args[0][2]

        try:
            pipeline_queue.set_pipeline_to_not_active(project_id, sandbox_id)
        except Exception as e:
            logger.errorlog(
                {
                    "message": "Error Setting pipeline to not active",
                    "error": str(e),
                    "log_type": "PID",
                    "sandbox_uuid": sandbox_id,
                    "task_id": task_id,
                    "project_uuid": project_id,
                    "status": status,
                }
            )

        pipeline_queue.remove_sandbox_from_queue(project_id, sandbox_id)

        logger.userlog(
            {
                "message": "Unlocking Sandbox Thread",
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": task_id,
                "project_uuid": project_id,
                "status": status,
            }
        )


class UnlockKnowledgepackTask(Task):
    abstract = True

    def after_return(self, status, retval, task_id, *args, **kwargs):
        project_id = args[0][1]
        uuid = args[0][3]

        pipeline_queue.remove_sandbox_from_queue(project_id, uuid)

        logger.userlog(
            {
                "message": "Unlocking KnownledgePack Thread",
                "log_type": "KPID",
                "UUID": uuid,
                "project_uuid": project_id,
                "task_id": task_id,
                "status": status,
            }
        )


class UnlockQueryTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        args[1]
        query_id = args[2]
        query = Query.objects.get(uuid=query_id)
        query.task_status = "FAILED"
        query.save(update_fields=["task_status"])

    def after_return(self, status, retval, task_id, *args, **kwargs):
        project_id = args[0][1]
        query_id = args[0][2]

        try:
            pipeline_queue.set_query_to_not_active(project_id, query_id)
        except Exception as e:
            logger.errorlog(
                {
                    "message": "Error Setting query to not active",
                    "error": str(e),
                    "log_type": "PID",
                    "sandbox_uuid": query_id,
                    "task_id": task_id,
                    "project_uuid": project_id,
                    "status": status,
                }
            )

        pipeline_queue.remove_sandbox_from_queue(project_id, query_id)

        logger.userlog(
            {
                "message": "Unlocking Query Thread {}.{}".format(project_id, query_id),
                "log_type": "PID",
                "UUID": query_id,
                "task_id": task_id,
                "project_uuid": project_id,
                "status": status,
            }
        )


@shared_task(bind=True, base=UnlockSandboxTask, ignore_result=False, track_started=True)
def pipeline_async(self, user_id, project_id, sandbox_id, err_queue=deque()):
    # add worker id to sandbox status in redis
    from engine.parallelexecutionengine import ParallelExecutionEngine

    logger.userlog(
        {
            "message": "Beginning Pipeline Execution",
            "log_type": "PID",
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )

    start = time.time()

    user = User.objects.get(pk=user_id)
    sandbox = _locate_sandbox(user, project_id, sandbox_id)
    project = Project.objects.get(uuid=project_id)
    sandbox.result_type = "pipeline"
    sandbox.save(update_fields=["result_type"])

    try:
        # Run The Execution Engine
        engine = ParallelExecutionEngine(
            self.request.id,
            user,
            project_id,
            sandbox,
            PipelineExecution.ExecutionTypeEnum.PIPELINE,
            err_queue=err_queue,
        )
    except:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "Pipeline Initialization Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        logger.slack(
            {
                "message": "Pipeline Initialization Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        usage_log(
            PJID=project,
            operation="pipeline",
            team=project.team,
            PID=sandbox,
            PROC=self.request.id,
            runtime=time.time() - start,
            detail={"status": "failed", "error": str(e), "traceback": s_traceback},
            team_member=user.teammember,
        )

        raise e

    try:
        tempdata, extra = engine.execute(sandbox.pipeline)
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "Pipeline Execution Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        logger.slack(
            {
                "message": "Pipeline Execution Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        usage_log(
            PJID=project,
            operation="pipeline",
            team=project.team,
            PID=sandbox,
            PROC=self.request.id,
            runtime=time.time() - start,
            detail={"status": "failed", "error": str(e), "traceback": s_traceback},
            team_member=user.teammember,
        )
        engine._temp.clean_up_temp()
        engine.update_team_cpu_usage(
            execution_type=PipelineExecution.ExecutionTypeEnum.PIPELINE,
            status=PipelineExecution.ExecutionStatusEnum.FAILED,
            wall_time=time.time() - start,
        )

        engine._current_step_info["error"] = e.args[0]
        e.args = (engine._current_step_info,)
        raise e

    engine.update_team_cpu_usage(
        execution_type=PipelineExecution.ExecutionTypeEnum.PIPELINE,
        status=PipelineExecution.ExecutionStatusEnum.SUCCESS,
        wall_time=time.time() - start,
    )

    usage_log(
        PJID=project,
        operation="pipeline",
        team=project.team,
        PID=sandbox,
        PROC=self.request.id,
        runtime=time.time() - start,
        team_member=user.teammember,
    )

    logger.userlog(
        {
            "message": "Finished Pipeline Execution",
            "log_type": "PID",
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )

    return engine.execution_summary


@shared_task(bind=True, base=UnlockQueryTask, ignore_result=False, track_started=True)
def querydata_async(
    self, user_id, project_id, query_id, pipeline_id=None, task_id=None
):
    # add worker id to sandbox status in redis
    from datamanager.models import Query
    from datamanager.query import (
        _compute_statistics,
        _get_query_segment_statistics,
        partition_query,
        query_driver_from_csv_to_datasegments,
    )
    from datamanager.datastore import get_datastore, get_datastore_basedir
    from django.conf import settings
    from pandas import DataFrame

    logger.userlog(
        {
            "message": "Beginning Query Execution",
            "log_type": "PID",
            "sandbox_uuid": pipeline_id if pipeline_id is not None else query_id,
            "task_id": task_id if task_id is not None else self.request.id,
            "project_uuid": project_id,
        }
    )

    start = time.time()
    if isinstance(user_id, User):
        user = user_id
    else:
        user = User.objects.get(pk=user_id)

    try:
        query = Query.objects.get(uuid=query_id)

        if not _get_query_segment_statistics(
            user=None, project_uuid=query.project.uuid, query_id=query.uuid, query=query
        ):
            raise Exception("Query returned no segments.")

        query_parser, partitions, drop_capture_uuid = partition_query(query)

        logger.userlog(
            {
                "message": " Querying in {} parts".format(len(partitions)),
                "log_type": "PID",
                "sandbox_uuid": pipeline_id if pipeline_id is not None else query_id,
                "task_id": task_id if task_id is not None else self.request.id,
                "project_uuid": project_id,
            }
        )

        segment_count = 0

        datastore = get_datastore(
            folder=os.path.join(
                get_datastore_basedir(settings.SERVER_QUERY_ROOT), str(query_id)
            )
        )

        cache = []

        for index, partition in enumerate(partitions):
            fmt = ".pkl"
            partition_name = "{}.{}{}".format(query_id, index, fmt)

            tmp_query = {}
            tmp_query["outputs"] = [partition_name]
            tmp_query["query_info"] = partition
            tmp_query["metadata"] = query_parser._metadata
            tmp_query["label"] = query_parser._label
            tmp_query["columns"] = query_parser._columns
            tmp_query["segment_uuid"] = query_parser.return_segment_uuid
            tmp_query["segment_start"] = segment_count

            segment_count += len(partition)

            data = query_driver_from_csv_to_datasegments(
                task_id=task_id if task_id is not None else self.request.id,
                query_info=tmp_query,
                project_id=project_id,
                pipeline_id=pipeline_id if pipeline_id is not None else query_id,
                exclude_metadata_value=["capture_uuid"] if drop_capture_uuid else None,
            )

            cache.append([len(data), partition_name])
            datastore.save_data(data=data, key=partition_name, fmt=fmt)

        query.segment_info = _get_query_segment_statistics(
            user=None, project_uuid=query.project.uuid, query_id=query.uuid, query=query
        )

        query.summary_statistics = _compute_statistics(
            DataFrame(query.segment_info), query.label_column
        )
        query.cache = cache
        query.task_status = "CACHED"

        query.save()

        logger.userlog(
            {
                "message": "Query Statistics",
                "data": {
                    "summary_stats": query.summary_statistics,
                    "cache": query.cache,
                },
                "query_uuid": query.uuid,
                "log_type": "PID",
                "task_id": task_id if task_id is not None else self.request.id,
                "sandbox_uuid": pipeline_id if pipeline_id is not None else query_id,
                "project_uuid": project_id,
            }
        )
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "Query Execution Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "query_uuid": query.uuid,
                "task_id": task_id if task_id is not None else self.request.id,
                "sandbox_uuid": pipeline_id if pipeline_id is not None else query_id,
                "project_uuid": project_id,
            }
        )
        usage_log(
            PJID=query.project,
            operation="query",
            team=query.project.team,
            PID=query,
            PROC=self.request.id,
            runtime=time.time() - start,
            detail={"status": "failed", "error": str(e), "traceback": s_traceback},
            team_member=user.teammember,
        )

        e.args = ({"error": e.args[0]},)
        raise e

    process_id = current_process().pid
    usage_log(
        PJID=query.project,
        operation="query",
        team=query.project.team,
        PID=query,
        PROC=process_id,
        runtime=time.time() - start,
        team_member=user.teammember,
    )

    logger.userlog(
        {
            "message": "Finished Query Execution",
            "log_type": "PID",
            "query_uuid": query.uuid,
            "log_type": "PID",
            "task_id": task_id if task_id is not None else self.request.id,
            "sandbox_uuid": pipeline_id if pipeline_id is not None else query_id,
            "project_uuid": project_id,
        }
    )


@shared_task(bind=True, base=UnlockSandboxTask, ignore_result=False, track_started=True)
def gridsearch_async(
    self, user_id, project_id, sandbox_id, params, run_parallel, err_queue=deque()
):
    from engine.gridsearchengine import GridSearchEngine

    start = time.time()
    logger.userlog(
        {
            "message": "Beginning GridSearch Execution",
            "log_type": "PID",
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )

    user = User.objects.get(pk=user_id)
    sandbox = _locate_sandbox(user, project_id, sandbox_id)

    sandbox.result_type = "grid_search"
    sandbox.save(update_fields=["result_type"])

    try:
        # Run The Execution Engine
        engine = GridSearchEngine(
            self.request.id, user, project_id, sandbox, err_queue=err_queue
        )

        tempdata, extra = engine.execute(params, sandbox.pipeline, run_parallel)
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "Grid Search Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        engine._temp.clean_up_temp()
        engine.update_team_cpu_usage(
            execution_type=PipelineExecution.ExecutionTypeEnum.GRIDSEARCH,
            status=PipelineExecution.ExecutionStatusEnum.FAILED,
            wall_time=time.time() - start,
        )

        engine._current_step_info["error"] = e.args[0]
        e.args = (engine._current_step_info,)
        raise e

    engine.update_team_cpu_usage(
        execution_type=PipelineExecution.ExecutionTypeEnum.GRIDSEARCH,
        status=PipelineExecution.ExecutionStatusEnum.SUCCESS,
        wall_time=time.time() - start,
    )

    project = Project.objects.get(uuid=project_id)
    usage_log(
        PJID=project,
        operation="grid_search",
        team=project.team,
        PID=sandbox,
        PROC=self.request.id,
        runtime=time.time() - start,
        detail=params,
        team_member=user.teammember,
    )

    logger.userlog(
        {
            "message": "Finished GridSearch Execution",
            "log_type": "PID",
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )
    return engine.execution_summary


@shared_task(bind=True, base=UnlockSandboxTask, ignore_result=False, track_started=True)
def auto_async(
    self,
    user_id,
    project_id,
    sandbox_id,
    params,
    run_parallel,
    version="automl",
    err_queue=deque(),
):
    from engine.automationengine import AutomationEngine

    logger.userlog(
        {
            "message": "Beginning AutoML Execution",
            "log_type": "PID",
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )
    start = time.time()

    user = User.objects.get(pk=user_id)
    sandbox = _locate_sandbox(user, project_id, sandbox_id)
    sandbox.hyper_params = params
    sandbox.result_type = "auto"
    sandbox.save(update_fields=["result_type", "hyper_params"])
    project = Project.objects.get(uuid=project_id)

    try:
        engine = AutomationEngine(
            params.get("params", {}),
            self.request.id,
            user,
            project_id,
            sandbox,
            err_queue=err_queue,
        )
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "AutoML Failed to Initialize",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        logger.slack(
            {
                "message": "AutoML Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        usage_log(
            PJID=project,
            operation="automl",
            team=project.team,
            PID=sandbox,
            PROC=self.request.id,
            runtime=time.time() - start,
            detail={"status": "failed", "error": str(e), "traceback": s_traceback},
            team_member=user.teammember,
        )
        raise e

    try:
        tempdata, extra = engine.automate()
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "AutoML Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        logger.slack(
            {
                "message": "AutoML Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        usage_log(
            PJID=project,
            operation="automl",
            team=project.team,
            PID=sandbox,
            PROC=self.request.id,
            runtime=time.time() - start,
            detail={"status": "failed", "error": str(e), "traceback": s_traceback},
            team_member=user.teammember,
        )
        engine._temp.clean_up_temp()
        engine.update_team_cpu_usage(
            execution_type=PipelineExecution.ExecutionTypeEnum.AUTOML,
            status=PipelineExecution.ExecutionStatusEnum.FAILED,
            wall_time=time.time() - start,
        )

        engine._current_step_info["error"] = e.args[0]
        e.args = (engine._current_step_info,)
        raise e

    engine.update_team_cpu_usage(
        execution_type=PipelineExecution.ExecutionTypeEnum.AUTOML,
        status=PipelineExecution.ExecutionStatusEnum.SUCCESS,
        wall_time=time.time() - start,
    )

    usage_log(
        PJID=project,
        operation="automl",
        team=project.team,
        PID=sandbox,
        PROC=self.request.id,
        runtime=time.time() - start,
        detail=params,
        team_member=user.teammember,
    )

    logger.userlog(
        {
            "message": "Finished AutoML Execution",
            "log_type": "PID",
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )
    return engine.execution_summary


@shared_task(
    bind=True, base=UnlockAutosegmentationTask, ignore_result=False, track_started=True
)
def autosegment_async(
    self, user_id, project_id, sandbox_id, params, run_parallel, err_queue=deque()
):
    from engine.autosegmentationengine import AutoSegmentationEngine

    start = time.time()
    logger.userlog(
        {
            "message": "Beginning AutoSegment Search Execution",
            "log_type": "PID",
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )
    user = User.objects.get(pk=user_id)
    sandbox = _locate_sandbox(user, project_id, sandbox_id)

    sandbox.result_type = "autosegment_search"
    sandbox.save(update_fields=["result_type"])

    try:
        # Run The Execution Engine
        engine = AutoSegmentationEngine(
            self.request.id, user, project_id, sandbox, err_queue=err_queue
        )
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "AudoSegment Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )

    try:
        engine.optimize(sandbox.pipeline, params)
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "AudoSegment Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )

        engine._temp.clean_up_temp()
        engine.update_team_cpu_usage(
            execution_type=PipelineExecution.ExecutionTypeEnum.AUTOSEG,
            status=PipelineExecution.ExecutionStatusEnum.FAILED,
            wall_time=time.time() - start,
        )

        e.args = ({"error": e.args[0]},)
        raise e

    engine.update_team_cpu_usage(
        execution_type=PipelineExecution.ExecutionTypeEnum.AUTOSEG,
        status=PipelineExecution.ExecutionStatusEnum.SUCCESS,
        wall_time=time.time() - start,
    )

    process_id = current_process().pid
    project = Project.objects.get(uuid=project_id)
    usage_log(
        PJID=project,
        operation="auto_segmenter",
        team=project.team,
        team_member=user.teammember,
        PID=sandbox,
        PROC=process_id,
        runtime=time.time() - start,
        detail=params,
    )
    logger.userlog(
        {
            "message": "Finished AutoSegment Search Execution",
            "log_type": "PID",
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )
    return engine.execution_summary


def extract_background_data(user, project_id, test_plan):
    background = test_plan.get("background")
    background_capture = test_plan.get("background_capture")

    if background and background_capture:
        raise ValidationError(
            'More than one background files are provided! Use either "background" or "background_capture".'
        )

    if not background and not background_capture:
        raise ValidationError(
            'No background file is provided! Use either "background" or "background_capture".'
        )

    if background:
        if type(background) == str:
            background_data, _, back_sample_rate = get_backgroundfile(background)
            normalize = True
            back_margin = 80000
        else:
            raise ValidationError("Wrong type for background name.")

    if background_capture:
        if type(background_capture) == str:
            background_data, back_sample_rate = get_capturefiles(
                user, project_id, background_capture
            )
            normalize = False
            back_margin = 0
        else:
            raise ValidationError("Wrong type for background name.")

    return background_data, normalize, back_margin, back_sample_rate


@shared_task(
    bind=True, base=UnlockKnowledgepackTask, ignore_result=False, track_started=True
)
def recognize_signal_async(
    self,
    user_id,
    project_id,
    sandbox_id,
    knowledgepack_id,
    data,
    segmenter,
    stop_step,
    platform,
    kb_description,
    compare_labels,
):
    from datamanager.knowledgepack import locate_knowledgepack
    from django.conf import settings
    from engine.recognitionengine import RecognitionEngine
    from pandas import DataFrame

    start = time.time()

    logger.userlog(
        {
            "message": "Beginning Recognize Signal Execution",
            "log_type": "PID",
            "uuid": knowledgepack_id,
            "sandbox_uuid": sandbox_id,
            "task_id": self.request.id,
            "project_uuid": project_id,
        }
    )

    try:
        user = User.objects.get(pk=user_id)

        capture_sample_rate = 0

        if data.get("capture", None):
            capture_sizes = get_capturefile_sizes(project_id, data.get("capture"))
            total_samples = 0

            for capture_size in capture_sizes:
                total_samples += capture_size["number_samples"]

            if total_samples > settings.MAX_RECOGNITION_SAMPLES:
                raise Exception(
                    "Total Samples {total_samples} exceeded the max number of samples allowed {max_samples}".format(
                        total_samples=total_samples,
                        max_samples=settings.MAX_RECOGNITION_SAMPLES,
                    )
                )

            data_frame, capture_sample_rate = get_capturefiles(
                user, project_id, data.get("capture")
            )

        elif data.get("datafile", None):
            data_frame, _ = get_featurefile(user, project_id, data.get("datafile"))
            capture_sizes = [
                {
                    "datafile": data.get("datafile"),
                    "number_samples": data_frame.shape[0],
                }
            ]

        elif data.get("featurefile", None):
            data_frame, _ = get_featurefile(user, project_id, data.get("featurefile"))

        elif data.get("test_plan"):
            test_plan = data.get("test_plan")

            (
                background_data,
                normalize,
                back_margin,
                back_sample_rate,
            ) = extract_background_data(user, project_id, test_plan)

            back_max_level = test_plan.get("back_max_level", 0)
            background_factor = test_plan.get("background_factor", 1)
            sample_rate = test_plan.get("sample_rate", 0)

            data_frame = get_background(
                background_data,
                back_max_level=back_max_level,
                background_factor=background_factor,
                normalize=normalize,
                sample_rate=sample_rate,
                back_sample_rate=back_sample_rate,
            )

        else:
            raise Exception(
                {
                    "error": "Recognize Signal requires either the name of a capture or datafile."
                }
            )

        ############################################################
        if (
            platform == "emulator"
            and (data.get("capture") or data.get("datafile"))
            and data.get("test_plan", None)
        ):
            test_plan = data.get("test_plan")

            (
                background_data,
                normalize,
                back_margin,
                back_sample_rate,
            ) = extract_background_data(user, project_id, test_plan)

            # make sure these parameters are provided by users
            audio_max_level = test_plan.get("audio_max_level", 0)
            audio_factor = test_plan.get("audio_factor", 1.0)
            back_max_level = test_plan.get("back_max_level", 0)
            background_factor = test_plan.get("background_factor", 1.0)
            seed = test_plan.get("random_seed", 0)

            if capture_sample_rate:
                sample_rate = test_plan.get("sample_rate", capture_sample_rate)
            else:
                sample_rate = test_plan.get("sample_rate", 0)

            add_background(
                data_frame,
                capture_sizes,
                background_data,
                audio_max_level=audio_max_level,
                audio_factor=audio_factor,
                back_max_level=back_max_level,
                background_factor=background_factor,
                seed=seed,
                back_margin=back_margin,
                normalize=normalize,
                sample_rate=sample_rate,
                back_sample_rate=back_sample_rate,
            )

        ############################################################

        # Get the knowledgepack and recognize
        kp = locate_knowledgepack(user, project_id, knowledgepack_id)

        try:
            for key in kb_description:
                kb_description[key]["knowledgepack"] = KnowledgePack.objects.get(
                    uuid=kb_description[key]["uuid"]
                )
        except ObjectDoesNotExist as e:
            raise NotFound(e)

        engine = RecognitionEngine(
            self.request.id,
            user,
            project_id,
            data_frame,
            kp,
            stop_step=stop_step,
            segmenter=segmenter,
            compare_labels=compare_labels,
        )

        results = engine.recognize(platform=platform, kb_description=kb_description)

        if not results["results"]:
            return {"results": []}

        if platform == "emulator" and data.get("capture"):
            results["results"] = reindex_recognize_file(
                capture_sizes, results["results"]
            )

            if results.get("result_type")["model_type"] == "classification":
                modified_class_map = get_modified_class_map(kp, kb_description)

                if isinstance(compare_labels, str):
                    results["ground_truth"] = get_capturefile_labels(
                        project_id,
                        filenames=data.get("capture"),
                        label=compare_labels,
                        class_map=modified_class_map,
                    )

                    if len(kb_description.keys()) > 1:
                        class_map = {}
                        for i, v in enumerate(modified_class_map):
                            class_map[i + 1] = v
                    else:
                        class_map = kp.class_map

                    results["confusion_matrix"] = get_recognize_confusion_matrix(
                        DataFrame(results["results"]),
                        DataFrame(results["ground_truth"]),
                        data.get("capture"),
                        class_map,
                    )

        project = Project.objects.get(uuid=project_id)

        usage_log(
            PJID=project,
            operation="recognition",
            team_member=user.teammember,
            team=project.team,
            KPID=kp,
            PROC=self.request.id,
            runtime=time.time() - start,
        )

        logger.userlog(
            {
                "message": "Finished Recognize Signal Execution",
                "log_type": "PID",
                "uuid": knowledgepack_id,
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "Recognize Signal Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "uuid": knowledgepack_id,
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        logger.slack(
            {
                "message": "Recognize Signal Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "PID",
                "uuid": knowledgepack_id,
                "sandbox_uuid": sandbox_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )
        e.args = ({"error": e.args[0]},)
        raise e

    return results


class ProcessUploadTask(Task):
    abstract = True
    # model = s

    def on_success(self, retval, task_id, args, kwargs):
        try:
            obj = self.model.objects.get(pk=args[0])
            obj.task = "SUCCESS"
            obj.task_result = None
            obj.save(update_fields=["task", "task_result"])
        except Exception as e:
            logger.error(e)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            obj = self.model.objects.get(pk=args[0])
            obj.task = "FAILURE"
            obj.task_result = str(exc)
            obj.save(update_fields=["task", "task_result"])
            logger.error(
                {
                    "message": "Task Failed. Logging to Database.",
                    "log_type": "CID",
                    "UUID": str(obj.uuid),
                    "task_id": self.request.id,
                }
            )
        except Exception as e:
            logger.error(
                {"message": e, "log_type": "datamanager", "task_id": self.request.id}
            )


@shared_task(bind=True)
def generate_knowledgepack_v2(self, data, project_uuid, kp_uuid, user_id, build_type):
    """Generates KnowledgePack."""
    from datamanager.knowledgepack import (
        cleanup_generated_items,
        get_generator,
        validate_request_info_v2,
    )

    start = time.time()

    from datamanager.models import KnowledgePack
    from datamanager.datastore import get_datastore
    from django.conf import settings

    kp_uuid = str(kp_uuid)

    logger.userlog(
        {
            "message": "Starting KnowledgePack generation",
            "log_type": "KPID",
            "UUID": kp_uuid,
            "task_id": self.request.id,
            "project_uuid": project_uuid,
        }
    )

    kp_bin_path = ""

    test_data = data.get("test_data", None)

    base_project = Project.objects.get(uuid=project_uuid)

    try:
        if not kp_uuid:
            raise KnowledgeBuilderException("KnowledgePack ID cannot be null!")
        try:
            user = User.objects.get(pk=user_id)
            knowledgepacks = [KnowledgePack.objects.get(uuid=kp_uuid)]
        except ObjectDoesNotExist as e:
            raise NotFound(e)

        if test_data:
            try:
                test_data, _, _ = get_capturefile(user, project_uuid, test_data)
            except:
                test_data, _ = get_featurefile(user, project_uuid, test_data)

        # Clean up any existing data for this knowledgepack for rebuild
        cleanup_generated_items(kp_uuid)

        device_config, kb_description = validate_request_info_v2(data, kp_uuid)

        if base_project.plugin_config is None:
            device_config["capture_sources"] = {}
        else:
            device_config["capture_sources"] = base_project.plugin_config.get(
                "capture_sources", {}
            )

        try:
            for key in kb_description:
                kb_description[key]["knowledgepack"] = KnowledgePack.objects.get(
                    uuid=kb_description[key]["uuid"]
                )
        except ObjectDoesNotExist as e:
            raise NotFound(e)

        generator = get_generator(
            kb_description,
            kp_uuid,
            self.request.id,
            device_config,
            build_type,
            test_data=test_data,
        )

        kp_bin_path = generator.generate(build_type=build_type)

        if not os.path.isfile(kp_bin_path):
            raise KnowledgePackGenerationError("No knowledgepack was generated.")

        # Cleanup in production mode
        if not settings.DEBUG:
            cleanup_generated_items(kp_uuid)

        logger.userlog(
            {
                "message": "Finished KnowledgePack generation",
                "log_type": "KPID",
                "UUID": kp_uuid,
                "task_id": self.request.id,
                "project_uuid": project_uuid,
            }
        )

        process_id = current_process().pid
        usage_log(
            PJID=base_project,
            KPID=kp_uuid,
            operation="kp-gen",
            team=base_project.team,
            team_member=user.teammember,
            PROC=process_id,
            detail=device_config,
            runtime=time.time() - start,
        )
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        s_traceback = "\n".join(traceback.format_tb(exc_traceback))
        logger.errorlog(
            {
                "message": "KnowledgePack Generation Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "KPID",
                "UUID": kp_uuid,
                "task_id": self.request.id,
                "project_uuid": project_uuid,
            }
        )
        logger.slack(
            {
                "message": "KnowledgePack Generation Failed",
                "data": {"error": str(e), "traceback": s_traceback},
                "log_type": "KPID",
                "UUID": kp_uuid,
                "task_id": self.request.id,
                "project_uuid": project_uuid,
            }
        )
        process_id = current_process().pid
        usage_log(
            PJID=base_project,
            KPID=kp_uuid,
            operation="kp-gen",
            team=base_project.team,
            team_member=user.teammember,
            PROC=process_id,
            detail={
                "status": "failed",
                "error": str(e),
                "traceback": s_traceback,
            },
            runtime=time.time() - start,
        )
        e.args = ({"error": e.args[0]},)
        raise e

    if self.request.called_directly:
        with open(kp_bin_path, "rb") as f:
            kp_bin_data = f.read()
        return base64.b64encode(kp_bin_data), kp_bin_path

    datastore = get_datastore(bucket=settings.AWS_CODEGEN_BUCKET_NAME)

    if datastore.is_remote:
        return datastore.save(
            os.path.join(kp_uuid, os.path.basename(kp_bin_path)), kp_bin_path
        )

    return os.path.join(kp_uuid, os.path.basename(kp_bin_path))


class ProcessCustomTransformUploadTask(ProcessUploadTask):
    model = CustomTransform


def validate_custom_transform_unit_tests(logs, build_failure, custom_transform):
    class UnitTestFailedException(Exception):
        pass

    class CompilationFailedException(Exception):
        pass

    # if valid, set state to valid
    for line in logs:
        if "[  FAILED  ]" in line:
            raise UnitTestFailedException(
                "Not all unit tests passed, see logs for details."
            )

        if "make: ***" in line and "Error" in line:
            raise CompilationFailedException("Failed to compile, see logs for details.")

    if build_failure:
        raise Exception("Unit Test failed, see logs for details.")


def validate_custom_transform_library_gen(logs, error_flag, custom_transform):
    # if valid, set state to valid
    for line in logs:
        if "ERROR" in line:
            raise Exception("Unable to generate transform library, see log for details")


@shared_task(
    base=ProcessCustomTransformUploadTask, bind=True, retry_kwargs={"max_retries": 5}
)
def process_custom_transform(self, transform_id, folder_name, key):
    import shutil

    from datamanager.datastore import get_datastore
    from django.conf import settings
    from library.custom_transforms import (
        generate_custom_transform_unit_tests,
        generate_library_pack_python_algorithm_library,
    )

    logger.userlog(
        {
            "message": "Starting Custom Transform Processing",
            "log_type": "KPID",
            "UUID": transform_id,
            "task_id": self.request.id,
        }
    )

    try:
        custom_transform = CustomTransform.objects.get(pk=transform_id)
    except:
        time.sleep(1)
        custom_transform = CustomTransform.objects.get(pk=transform_id)

    library_pack = custom_transform.library_pack
    datastore = get_datastore(
        folder=os.path.join("custom_transforms", str(library_pack.uuid))
    )

    if datastore.is_remote:
        local_code_dir = os.path.join(
            settings.SERVER_CUSTOM_TRANSFORM_ROOT,
            str(library_pack.uuid),
        )
        file_path = os.path.join(local_code_dir, custom_transform.file_path)
        datastore.get(key=custom_transform.file_path, file_path=file_path)

    logs, build_failure = generate_custom_transform_unit_tests(
        transform_uuid=str(custom_transform.uuid), task_id=self.request.id
    )

    # unfortunantley we write to the log object inside the previous function, so lets refresh here
    custom_transform.refresh_from_db()
    custom_transform.logs = "".join(logs)
    custom_transform.save()

    validate_custom_transform_unit_tests(logs, build_failure, custom_transform)

    # generate a new python library that includes the shared library for this teams custom functions
    logs, error_flag = generate_library_pack_python_algorithm_library(
        str(library_pack.uuid),
        version=(
            library_pack.build_version + 1
            if library_pack.build_version is not None
            else 0
        ),
        custom_transform=custom_transform,
    )

    custom_transform.logs += "Library Logs"
    custom_transform.logs += "\n".join(logs)
    custom_transform.save()

    validate_custom_transform_library_gen(logs, error_flag, custom_transform)

    if datastore.is_remote:
        archive = shutil.make_archive(
            base_name=os.path.join(
                settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                str(library_pack.uuid),
                "embedded_ml_sdk",
            ),
            format="zip",
            root_dir=os.path.join(
                settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                str(library_pack.uuid),
                "embedded_ml_sdk",
            ),
        )

        datastore.save("embedded_ml_sdk.zip", archive)

    library_pack.build_version = (
        library_pack.build_version + 1 if library_pack.build_version is not None else 0
    )
    library_pack.save()
    custom_transform.automl_available = True
    custom_transform.save()

    logger.userlog(
        {
            "message": "Finished Custom Transform Processing",
            "log_type": "KPID",
            "UUID": transform_id,
            "task_id": self.request.id,
        }
    )

    return True


class DeleteProjectTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        args[1]

    def after_return(self, *args, **kwargs):
        project_id = args[3][1]
        logger.userlog(
            {
                "message": "Unlocking Project Delete Thread {}".format(project_id),
                "log_type": "PID",
                "UUID": project_id,
                "task_id": self.request.id,
                "project_uuid": project_id,
            }
        )


@shared_task(base=DeleteProjectTask, bind=True, retry_kwargs={"max_retries": 5})
def delete_project_task(self, user_id, project_id):
    project = Project.objects.get(uuid=project_id)

    project.delete()


@shared_task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
