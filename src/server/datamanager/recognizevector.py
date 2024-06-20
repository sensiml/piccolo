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

from datamanager import pipeline_queue
from datamanager.knowledgepack import locate_knowledgepack
from datamanager.models import Sandbox
from datamanager.tasks import recognize_signal_async
from datamanager.validation import validate_kb_description
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from engine.base.temp_table import TempVariableTable
from engine.recognitionengine import RecognitionEngine
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def feature_recognition(request, project_uuid, sandbox_uuid, uuid):
    feature_vector = request.data
    kp = locate_knowledgepack(request.user, project_uuid, uuid)
    # Try to get the knowledgepack and start the new instance
    r = RecognitionEngine(None, request.user, project_uuid, feature_vector, kp)
    results = json.dumps(r.recognize())

    return HttpResponse(results, content_type="application/json")


def async_submit(request, project_uuid, sandbox_uuid, uuid):
    """Put the sandbox execution task in a celery queue.
    Assembles a DataFrame from the sandbox pipeline and stores it in the sandbox cache.
    """

    pipeline_queue.set_start_sandbox(project_uuid, uuid)

    data = request.data
    stop_step = data.pop("stop_step", None)
    segmenter = data.pop("segmenter", True)
    platform = data.pop("platform", "cloud")
    kb_description = data.pop("kb_description", None)
    compare_labels = data.pop("compare_labels", False)

    kb_description = validate_kb_description(kb_description, uuid)

    if len(kb_description.keys()) > 1:
        platform = "emulator"

    sent_job = recognize_signal_async.delay(
        request.user.id,
        project_uuid,
        uuid if sandbox_uuid is None else sandbox_uuid,
        uuid,
        data,
        segmenter,
        stop_step,
        platform,
        kb_description,
        compare_labels,
    )

    pipeline_queue.set_pipeline_task_id(project_uuid, uuid, sent_job.task_id)

    return Response(
        {
            "status": None,
            "message": 'Recognizing Signal Submitted. Task ID: "{}")'.format(
                sandbox_uuid
            ),
            "detail": None,
        }
    )


def async_retrieve(request, project_uuid, sandbox_uuid, uuid):
    """Return the asynchronous recognition results requested."""
    status, message, detail = pipeline_queue.get_pipeline_status(project_uuid, uuid)

    if status in ["PENDING", "STARTED", "FAILURE", "REVOKED", "SENT"]:
        return Response({"status": status, "message": message, "detail": detail})

    elif status in [None]:
        return Response(
            {
                "status": None,
                "message": "No stored results for this pipeline.",
                "detail": None,
            }
        )

    return Response(message)


def async_terminate_task_id(request, project_uuid, sandbox_uuid, uuid):
    # delete the status from the queue
    pipeline_queue.remove_sandbox_from_queue(project_uuid, uuid)
    result = pipeline_queue.get_pipeline_task_id_status(project_uuid, uuid)
    result.revoke(terminate=True)

    # clean up the redis cache as well
    temp = TempVariableTable(uuid)
    temp.clean_up_temp()

    if result.task_id:
        return Response(
            {
                "message": "Pipeline '{}' execution was terminated.".format(
                    result.task_id
                )
            }
        )
    else:
        return Response({"message": "No Pipeline was running."})


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Knowledge Pack executing status or results if completed",
        description="""
Retrieve Knowledge Pack status or results if completed""",
    ),
    post=extend_schema(
        summary="Submit a request to execute the Knowledge Pack against test data",
        description="The Knowledge Pack firmware will be compiled and the test data will be fed through it return the expected results.",
    ),
    delete=extend_schema(
        summary="Stop currently executing Knowledge Pack pipeline",
        description="Stop currently executing Knowledge Pack",
    ),
)
class RecognizeAsyncView(APIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    exclude_from_schema = True

    def get_queryset(self):
        return Sandbox.objects.with_user(self.request.user).all()

    def get(self, request, *args, **kwargs):
        """Retrieve sandbox recognition status"""

        return async_retrieve(
            request,
            self.kwargs["project_uuid"],
            self.kwargs.get("sandbox_uuid"),
            self.kwargs["uuid"],
        )

    def post(self, request, *args, **kwargs):
        """Submits sandbox recognition"""

        return async_submit(
            request,
            self.kwargs["project_uuid"],
            self.kwargs.get("sandbox_uuid"),
            self.kwargs["uuid"],
        )

    def delete(self, request, *args, **kwargs):
        """Stops sandbox recognition"""
        return async_terminate_task_id(
            request,
            self.kwargs["project_uuid"],
            self.kwargs.get("sandbox_uuid"),
            self.kwargs["uuid"],
        )


@extend_schema_view(
    post=extend_schema(
        summary="Recognize Feature Vector",
        description="""Given a feature vector compute the results from the model inside the Knowledge Pack""",
    ),
)
@api_view(("POST",))
@permission_classes((IsAuthenticated,))
def recognize_features(request, project_uuid, sandbox_uuid, uuid=""):
    if request.method == "POST":
        return feature_recognition(request, project_uuid, sandbox_uuid, uuid)
