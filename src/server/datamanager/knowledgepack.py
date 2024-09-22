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

# pylint: disable=W0621
import json
import logging
import os
from shutil import rmtree

from celery.result import AsyncResult
from codegen.utils import is_valid_uuid4
from datamanager import renderers
from datamanager.exceptions import (
    BadRequest,
    KnowledgePackConfigError,
    KnowledgePackGenerationError,
    KnowledgePackInvalidDeviceError,
    KnowledgePackTaskExecutingError,
)
from datamanager.models import KnowledgePack, Sandbox
from datamanager.datastore import get_datastore
from datamanager.serializers.knowledgepack import (
    GenerateKnowledgePackSerializerVersion2,
    RetrieveKnowledgePackSerializer,
)
from datamanager.tasks import generate_knowledgepack_v2
from datamanager.utils.reports import cost_report, cost_resource_summary
from datamanager.validation import validate_kb_description
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import re_path
from django.urls import re_path as url
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from library.models import (
    CompilerDescription,
    PlatformDescriptionVersion2,
    ProcessorDescription,
)
from codegen import ARMGCCGenericCodeGenerator
from codegen import GCCGenericCodeGenerator
from codegen import QuickLogicS3CodeGenerator
from codegen import MINGW64GenericCodeGenerator
from codegen import EspressifCodeGenerator
from logger.log_handler import LogHandler
from rest_framework import generics, permissions, views
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.urlpatterns import format_suffix_patterns

from server.celery import UNREADY_STATES

logger = LogHandler(logging.getLogger(__name__))

CODEGEN_PLATFORMS = {
    "ARMGCCGenericCodeGenerator": ARMGCCGenericCodeGenerator,
    "GCCGenericCodeGenerator": GCCGenericCodeGenerator,
    "QuickLogicS3CodeGenerator": QuickLogicS3CodeGenerator,
    "MINGW64GenericCodeGenerator": MINGW64GenericCodeGenerator,
    "EspressifCodeGenerator": EspressifCodeGenerator,
}


def _check_parents(user, project_id, sandbox_id):
    return Sandbox.objects.with_user(
        user=user, uuid=sandbox_id, project__uuid=project_id
    ).exists()


def locate_knowledgepack(user, project_id, knowledgepack_id=None):
    knowledgepacks = KnowledgePack.objects.with_user(
        user=user, project__uuid=project_id
    )
    if knowledgepack_id is not None:
        return knowledgepacks.get(uuid=knowledgepack_id)
    else:
        return knowledgepacks


def validate_request_info_v2(data, knowledgepack_id):

    target_platform = data.get("target_platform", None)
    target_processor = data.get("target_processor", None)
    target_compiler = data.get("target_compiler", None)
    build_flags = data.get("build_flags", None)
    data.get("selected_platform_version", "")
    output_file = data.get("output_file", None)
    sample_rate = data.get("sample_rate", None)
    profile_data = data.get("profile_data", None)
    extra_build_flags = data.get("extra_build_flags", "")
    output_options = data.get("output_options", None)
    cpu_options = data.get("cpu_options", None)
    float_options = data.get("float_options", "")
    data["debug"] = data.get("debug", True)
    hardware_accelerator = data.get("hardware_accelerator", "")
    kb_description = data.get("kb_description", None)
    selected_application = data.get("application", None)
    nn_inference_engine = data.get("nn_inference_engine", "nnom")

    platform = PlatformDescriptionVersion2.objects.get(uuid=target_platform)
    processor = ProcessorDescription.objects.get(uuid=target_processor)
    compiler = CompilerDescription.objects.get(uuid=target_compiler)

    if selected_application in ["SensiML AI Model Runner", "SensiML AI Simple Stream"]:
        # Backwards compatibility
        selected_application = "AI Model Runner"

    if selected_application not in platform.applications.keys():
        raise KnowledgePackConfigError("Invalid application")

    if selected_application:
        data["application"] = selected_application
    if build_flags is None:
        data["build_flags"] = ""
    if output_file is None or output_file == "":
        data["output_file"] = "{0}_gen.zip".format(knowledgepack_id)
    if sample_rate:
        data["sample_rate"] = int(sample_rate)
    if output_options:
        data["output_options"] = output_options
    if cpu_options:
        data["cpu_options"] = cpu_options
    if profile_data:
        data["profile_data"] = profile_data
    if hardware_accelerator:
        if hardware_accelerator not in platform.hardware_accelerators.keys():
            raise Exception("Invalid HW Accelerator Selection")
        data["hardware_accelerator"] = hardware_accelerator
    if hardware_accelerator is None:
        data["hardware_accelerator"] = ""
    data["target_compiler"] = compiler
    data["target_processor"] = processor
    data["float_options"] = float_options
    data["extra_build_flags"] = extra_build_flags
    data["nn_inference_engine"] = nn_inference_engine

    kb_description = validate_kb_description(kb_description, knowledgepack_id)

    return data, kb_description


def get_generator(
    knowledgepacks, uuid, task_id, device_config, build_type, test_data=None
):
    # Switch on device_configs.
    platform_id = device_config["target_platform"]
    if not is_valid_uuid4(platform_id):
        raise Exception("Invalid platform UUID.")

    platform = PlatformDescriptionVersion2.objects.get(
        uuid=device_config["target_platform"]
    )
    platform_name = platform.name

    codegen_class = platform.codegen_parameters.get("codegen_class", None)

    if codegen_class is None:
        raise KnowledgePackInvalidDeviceError(
            'Target "{0}" not supported at this time.'.format(platform_name)
        )
    elif codegen_class in CODEGEN_PLATFORMS:
        generator = CODEGEN_PLATFORMS.get(codegen_class)(
            knowledgepacks,
            uuid,
            task_id,
            device_config,
            build_type,
            test_data=test_data,
        )
        if generator is None:
            raise KnowledgePackGenerationError(
                f'Target "{platform_name}" did not have a valid generator.'
            )
        return generator
    else:
        logger.info({"message": CODEGEN_PLATFORMS, "log_type": "datamanager"})
        raise KnowledgePackInvalidDeviceError(
            f"Target {codegen_class} not found in globals"
        )


def cleanup_generated_items(uuid):
    if settings.KB_CODEGEN_REMOVE_LOCAL_FILES:
        dir_path = os.path.join(settings.SERVER_CODEGEN_ROOT, uuid)
        if os.path.isdir(dir_path):
            rmtree(dir_path)


def make_knowledgepack(
    sandbox,
    feature_file,
    index,
    results_key,
    model_stats,
    model_parameters,
    sensor_summary,
    query_summary,
    feature_summary,
    device_configuration,
    transform_summary,
    class_map,
    cost_summary,
    pipeline_summary,
    knowledgepack_summary,
    name="",
    **kwargs,
):
    """Generate the knowledgepack.

    DEPRECATED: Please use KnowledgePack.objects.create directly instead
    """
    return KnowledgePack.objects.create(
        pipeline_summary=pipeline_summary,
        sandbox=sandbox,
        project=sandbox.project,
        feature_file=feature_file,
        neuron_array=model_parameters,
        model_results=model_stats,
        configuration_index=results_key,
        knowledgepack_summary=knowledgepack_summary,
        model_index=index,
        sensor_summary=sensor_summary,
        query_summary=query_summary,
        feature_summary=feature_summary,
        device_configuration=device_configuration,
        transform_summary=transform_summary,
        class_map=class_map,
        cost_summary=cost_summary,
        name=name,
    )


def terminate_knowledge_pack_generate(kp):

    if kp.task is None:
        return Response({"message": "No Knowledge Pack was being generated."})

    result = AsyncResult(str(kp.task))
    result.revoke()

    kp.task = None
    kp.save(update_fields=["task"])

    return Response(
        {"message": "Knowledge '{}' generation was terminated.".format(result.task_id)}
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get status of Knowledge Pack firmware generation. Return model if it is complete",
        description="",
        tags=["knowledgepack"],
    ),
    post=extend_schema(
        summary="Start Knowledge Pack firmware generation",
        description="Starts a job to execute the Knowlededge pack firmware generation for the provided parameters.",
        tags=["knowledgepack"],
    ),
    delete=extend_schema(
        summary="Stop the Knowledge Pack firmware generation execution",
        description="Terminates the job compiling the Knowledge Pack firmware.",
        tags=["knowledgepack"],
    ),
)
class GenerateKnowledgePackView(generics.GenericAPIView):
    """Get Knowledgepack"""

    queryset = KnowledgePack.objects.none()
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = GenerateKnowledgePackSerializerVersion2
    lookup_field = "uuid"

    def get_queryset(self):
        return KnowledgePack.objects.with_user(self.request.user)

    def finalize_response(self, request, response, *args, **kwargs):
        """custom finalizer to override content negotiation in some cases"""
        response = super(GenerateKnowledgePackView, self).finalize_response(
            request, response, *args, **kwargs
        )
        if response.content_type == renderers.BinaryRenderer.media_type:
            response.accepted_renderer = renderers.BinaryRenderer()
            response.accepted_media_type = renderers.BinaryRenderer.media_type

        return response

    def check_perms(self, build_type, request):

        if build_type not in ["lib", "bin", "source"]:
            raise BadRequest("Invalid build type")

    def delete(self, request, *args, **kwargs):
        kp = self.get_object()
        return terminate_knowledge_pack_generate(kp)

    def post(self, request, *args, **kwargs):
        return self.generate(request, kwargs["build_type"])

    def generate(self, request, build_type):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        self.check_perms(build_type, request)

        data["has_classification_limit"] = request.user.has_perm(
            "datamanager.has_classification_limit"
        )

        platform = PlatformDescriptionVersion2.objects.get(uuid=data["target_platform"])

        valid_permission = False

        if platform.permissions.get("starter", False):
            valid_permission = True

        if platform.permissions.get("enterprise", False):
            if request.user.has_perm("datamanager.can_get_enterprise"):
                valid_permission = True

        if platform.permissions.get("developer", False):
            if request.user.has_perm("datamanager.can_get_developer"):
                valid_permission = True

        if not valid_permission:
            raise PermissionDenied(
                "Your account does not have access to this Knowledge Pack Platform."
            )

        kp = self.get_object()

        task = generate_knowledgepack_v2.s(
            data,
            str(kp.project.uuid),
            str(kp.uuid),
            request.user.id,
            build_type,
        )

        if kp.task and AsyncResult(str(kp.task)).status in UNREADY_STATES:
            raise KnowledgePackTaskExecutingError()
        result = task.delay()
        kp.task = result.id
        kp.save(update_fields=["task"])
        data["task_state"] = result.id

        return Response(data=data)

    def get(self, request, *args, **kwargs):
        self.serializer_class = RetrieveKnowledgePackSerializer
        obj = self.get_object()
        data = self.serializer_class(obj).data

        if data["task_state"] == "SUCCESS" and not "status" in request.query_params:
            key = data["task_result"]
            local_path = os.path.join(settings.SERVER_CODEGEN_ROOT, key)
            datastore = get_datastore(bucket=settings.AWS_CODEGEN_BUCKET_NAME)
            if datastore.is_remote:
                datastore.get(key, local_path)
            with open(local_path, "rb") as f:
                response = Response(
                    f.read(),
                    content_type="application/octet-stream",
                    headers={
                        "Access-Control-Expose-Headers": "Content-Disposition",
                        "Content-Disposition": 'attachment; filename="{}"'.format(
                            os.path.basename(local_path)
                        ),
                    },
                )
            response.accepted_renderer = renderers.BinaryRenderer()
            if not settings.DEBUG:
                cleanup_generated_items(str(obj.uuid))
            return response
        elif not data["task_state"]:
            raise BadRequest(
                "Requested knowledge pack was not found. Your client may be out of date. Upgrade your client or be sure to generate the knowledge pack first using a POST request."
            )
        elif data["task_state"] == "FAILURE":
            obj.task = None
            obj.save(update_fields=["task"])
            return Response(data)
        else:
            return Response(data)


@extend_schema_view(
    get=extend_schema(
        summary="Get the profile information for a Knowledge Pack",
        description="Generate a report describing the Knowledge Pack profile information",
        tags=["knowledgepack"],
        parameters=[
            OpenApiParameter("accelerator", str),
            OpenApiParameter("processor_uuid", str),
        ],
    ),
)
class ReportView(views.APIView):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [
        renderers.PlainTextRenderer
    ]

    def get(self, request, *args, **kwargs):
        try:
            kp = KnowledgePack.objects.with_user(self.request.user).get(
                project__uuid=kwargs["project_uuid"],
                uuid=kwargs["uuid"],
            )

        except ObjectDoesNotExist:
            raise BadRequest("Knowledge pack not found")

        # reports located in datamanager/utils/reports.py
        report_as_string = ""
        if kwargs["report_type"] == "cost":
            report_as_string += (
                cost_report(kp.sandbox.device_config, kp.cost_summary, kp.neuron_array)
                + "\n\n\n"
            )
            return Response(report_as_string)
        if kwargs["report_type"] == "json":
            return Response(json.dumps(kp.cost_summary))
        if kwargs["report_type"] == "resource_summary":
            processor = None
            accelerator = request.query_params.get("accelerator")
            if request.query_params.get("processor") is not None:
                processor = ProcessorDescription.objects.get(
                    uuid=request.query_params["processor"]
                )

            rs = cost_resource_summary(kp.cost_summary, processor, accelerator)

            if not rs:
                return Response(json.dumps({}))

            return Response(rs)

        else:
            raise BadRequest("Report type not recognized")


urlpatterns = format_suffix_patterns(
    [
        re_path(
            r"^project/(?P<project_uuid>[^/]+)/sandbox/(?P<sandbox_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/(?:generate_(?P<build_type>[\w]+))/v2$",
            GenerateKnowledgePackView.as_view(),
            name="sandbox-knowledgepack-generate",
        ),
        re_path(
            r"^project/(?P<project_uuid>[^/]+)/sandbox/(?P<sandbox_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/(?:generate_(?P<build_type>[\w]+))/$",
            GenerateKnowledgePackView.as_view(),
            name="sandbox-knowledgepack-generate-v1",
        ),
        re_path(
            r"^project/(?P<project_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/(?:generate_(?P<build_type>[\w]+))/v2$",
            GenerateKnowledgePackView.as_view(),
            name="knowledgepack-generate",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/report/(?P<report_type>[^/]+)/$",
            ReportView.as_view(),
            name="report-view",
        ),
    ]
)
