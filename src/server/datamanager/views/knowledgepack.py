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

import boto3
from datamanager.models import KnowledgePack
from datamanager.serializers.knowledgepack import (
    KnowledgePackCreateSerializer,
    KnowledgePackDetailSerializer,
    KnowledgePackExportSerializer,
    KnowledgePackSimpleDetailSerializer,
)
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import re_path as url
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
)
from rest_framework import generics, permissions, views
from rest_framework.urlpatterns import format_suffix_patterns


@extend_schema_view(
    get=extend_schema(
        summary="List Knowledge Pack",
        description="List Knowledge Packs associated with a project",
    ),
    post=extend_schema(
        summary="Post Knowledge Pack",
        description="Post Knowledge Pack to a project",
    ),
)
class KnowledgePackProjectListView(generics.ListCreateAPIView):
    serializer_class = KnowledgePackSimpleDetailSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def get_queryset(self):
        return (
            KnowledgePack.objects.with_user(self.request.user)
            .select_related("project", "sandbox")
            .filter(
                project__uuid=self.kwargs["project_uuid"],
            )
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return KnowledgePackSimpleDetailSerializer
        elif self.request.method == "POST":
            return KnowledgePackCreateSerializer


@extend_schema_view(
    get=extend_schema(
        summary="List Knowledge Pack",
        description="List Knowledge Packs associated with a Sanbdox",
    ),
)
class KnowledgePackSandboxListView(generics.ListAPIView):
    serializer_class = KnowledgePackSimpleDetailSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def get_queryset(self):
        return (
            KnowledgePack.objects.with_user(self.request.user)
            .select_related("sandbox", "sandbox__project")
            .filter(sandbox__uuid=self.kwargs["sandbox_uuid"])
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get Knowledge Pack by UUID",
        description="Get detailed information about a Knowledge Pack 1",
        parameters=[
            OpenApiParameter(
                name="fields[]",
                description="Optional to include fields to response.",
                examples=[OpenApiExample(name="?fields[]=uuid&fields[]=name")],
            ),
            OpenApiParameter(
                name="omit_fields[]",
                description="Optional to exclude fields from response.",
                examples=[
                    OpenApiExample(name="?omit_fields[]=uuid&omit_fields[]=name")
                ],
            ),
        ],
    ),
    put=extend_schema(
        summary="Update Knowledge Pack by UUID",
        description="Update information about a Knowledge Pack",
    ),
    patch=extend_schema(
        summary="Update Knowledge Pack by UUID",
        description="Update information about a Knowledge Pack",
    ),
    delete=extend_schema(
        summary="Delete a Knowledge Pack by UUID",
        description="Deletes a Knowledge Pack",
    ),
)
class KnowledgePackDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = KnowledgePackDetailSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    lookup_field = "uuid"

    def get_queryset(self):
        return KnowledgePack.objects.with_user(self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="Get Knowledge Pack build logs",
        description="Downloads the build logs from a Knowledge Pack when it fails to compile",
    ),
)
class KnowledgePackExportView(generics.RetrieveAPIView):
    serializer_class = KnowledgePackExportSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    lookup_field = "uuid"

    def get_queryset(self):
        return KnowledgePack.objects.with_user(self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="Get Knowledge Pack build logs",
        description="Downloads the build logs from a Knowledge Pack when it fails to compile",
    ),
)
class KnowledgePackBuildLogsView(views.APIView):
    def get(self, request, *args, **kwargs):

        try:
            kp = KnowledgePack.objects.with_user(self.request.user).get(
                uuid=kwargs["uuid"],
            )
        except KnowledgePack.ObjectDoesNotExist:
            raise ObjectDoesNotExist("Knowledge Pack not found")

        if settings.AWS_S3_BUCKET:
            cloud_logs = boto3.client(
                "logs",
                region_name=settings.AWS_DOCKER_RUNNER_REGION,
                aws_access_key_id=settings.AWS_DOCKER_RUNNER_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_DOCKER_RUNNER_SECRET_KEY,
            )

            try:
                log_stream = cloud_logs.get_log_events(
                    logGroupName=settings.AWS_DOCKER_LOGS, logStreamName=kp.logs
                )
            except:
                raise ObjectDoesNotExist(
                    "Failed to get build logs for this knowledge pack"
                )

            log_stream = [x["message"] for x in log_stream["events"]]
            file_data = ""
            recording = False
            for log in log_stream:
                if log == "LOG STOP":
                    recording = False
                if recording:
                    file_data += log + "\n"
                if log == "LOG START":
                    recording = True

        else:
            kp_dir = os.path.join(settings.SERVER_CODEGEN_ROOT, str(kp.uuid))

            if not os.path.exists(kp_dir):
                raise ObjectDoesNotExist("No Knowledge Pack logs.")

            log_name = ""
            for f in os.listdir(kp_dir)[::-1]:
                if str(kp.uuid) in f and "build.log" in f:
                    log_name = f
                    break

            if not log_name:
                raise ObjectDoesNotExist("No Knowledge Pack logs.")

            try:
                file_location = os.path.join(kp_dir, log_name)
                with open(file_location, "r") as f:
                    file_data = f.read()

            except IOError:
                # handle file not exist case here
                response = HttpResponseNotFound("File not found")

        # sending response
        response = HttpResponse(file_data, content_type="application/txt")
        response["Content-Disposition"] = 'attachment; filename="{}_build.log"'.format(
            kp.uuid
        )

        return response


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^project/(?P<project_uuid>[^/]+)/knowledgepack/$",
            KnowledgePackProjectListView.as_view(),
            name="knowledgepack-list-project",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/sandbox/(?P<sandbox_uuid>[^/]+)/knowledgepack/$",
            KnowledgePackSandboxListView.as_view(),
            name="knowledgepack-list-sandbox",
        ),
        url(
            r"^knowledgepack/(?P<uuid>[^/]+)/$",
            KnowledgePackDetailView.as_view(),
            name="knowledgepack-detail-user",
        ),
        url(
            r"^^project/(?P<project_uuid>[^/]+)/sandbox/(?P<sandbox_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/$",
            KnowledgePackDetailView.as_view(),
            name="project-sandbox-knowledgepack-detail-user",
        ),
        url(
            r"^^project/(?P<project_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/$",
            KnowledgePackDetailView.as_view(),
            name="project-knowledgepack-detail-user",
        ),
        url(
            r"^knowledgepack/(?P<uuid>[^/]+)/build-logs/$",
            KnowledgePackBuildLogsView.as_view(),
            name="knowledge-pack-build-logs-view",
        ),
        url(
            r"^knowledgepack/(?P<uuid>[^/]+)/export/$",
            KnowledgePackExportView.as_view(),
            name="knowledge-pack-export-view",
        ),
    ]
)
