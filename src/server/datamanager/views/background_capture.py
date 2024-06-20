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

from os.path import basename

from datamanager.models import Capture
from datamanager.renderers import BinaryRenderer
from datamanager.datastore import get_datastore
from datamanager.serializers.capture import (
    CaptureDetailSerializer,
    CaptureSerializer,
)
from django.conf import settings
from django.shortcuts import redirect
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.parsers import (
    FileUploadParser,
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.urlpatterns import format_suffix_patterns


@extend_schema_view(
    get=extend_schema(
        summary="Get list of Background Captures",
        description="Returns a list of Background captures in a project",
    ),
)
class BackgorundCaptureListView(generics.ListAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = CaptureSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser, JSONParser)

    def get_serializer_class(self):
        if self.request is None:
            return CaptureSerializer

        if self.request.method == "GET":
            return CaptureDetailSerializer

        return CaptureSerializer

    def get_queryset(self):
        return Capture.objects.select_related("capture_configuration").filter(
            project__uuid=settings.BACKGROUND_CAPTURE_PROJECT_UUID
        )


@extend_schema_view(
    get=extend_schema(
        summary="Download the Capture file",
        description="Downloads the CSV/WAV file from the server",
    ),
)
class BackgroundCaptureFileView(generics.GenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    renderer_classes = (BinaryRenderer,)
    serializer_class = CaptureSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return Capture.objects.filter(
            project__uuid=settings.BACKGROUND_CAPTURE_PROJECT_UUID
        )

    def get(self, request, *args, **kwargs):
        capture = self.get_object()

        datastore = get_datastore(bucket=settings.AWS_S3_BUCKET)

        # TODO: DATASTORE fix this so its a single call
        if capture.file:
            if datastore.is_remote:
                return redirect(datastore.get_url(capture.file))
            else:
                with open(capture.file, "rb") as f:
                    returndata = f.read()
                return Response(
                    returndata,
                    headers={
                        "Content-Disposition": "attachment; filename={}".format(
                            capture.name
                        )
                    },
                )
        else:
            raise NotFound("No capture found or no file found for this capture.")


@extend_schema_view(
    post=extend_schema(
        summary="Get the download the URLS for multiple capture files",
        description="Get the download the URLS for multiple capture files",
    ),
)
class BackgroundCaptureFilesView(generics.GenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = CaptureSerializer

    def get_queryset(self):
        return Capture.objects.filter(
            project__uuid=settings.BACKGROUND_CAPTURE_PROJECT_UUID
        )

    def get_local_url(self, uuid):
        return reverse(
            "capture-file",
            kwargs={
                "project_uuid": settings.BACKGROUND_CAPTURE_PROJECT_UUID,
                "uuid": uuid,
            },
            request=self.request,
        )

    def post(self, request, *args, **kwargs):

        capture_uuid_list = self.request.data.get("background_capture_uuids")
        expires_in = min(self.request.data.get("expires_in", 100), 1000)
        datastore = get_datastore(bucket=settings.AWS_S3_BUCKET)

        queryset = self.get_queryset().filter(uuid__in=capture_uuid_list)

        # TODO: DATASTORE make this local and remote call
        if not datastore.is_remote:
            return Response(
                [
                    {
                        "uuid": capture.uuid,
                        "url": self.get_local_url(capture.uuid),
                        "file": capture.file,
                        "name": capture.name,
                        "local": True,
                    }
                    for capture in queryset
                ],
                status=200,
            )

        redirect_urls = []
        for capture in queryset:
            if datastore.is_remote:
                redirect_urls.append(
                    {
                        "uuid": capture.uuid,
                        "url": datastore.get_url(capture.file, expires=expires_in),
                        "name": capture.name,
                    }
                )

        return Response(redirect_urls, status=200)


@extend_schema_view(
    get=extend_schema(
        summary="Download the Capture file",
        description="Downloads the CSV/WAV file from the server directly",
    ),
)
class BackgroundCaptureFileViewLocal(BackgroundCaptureFileView):
    def get(self, request, *args, **kwargs):
        capture = self.get_object()

        datastore = get_datastore(folder=os.path.join("capture", capture.project.uuid))
        datastore.get(basename(capture.file), capture.file)

        if capture.file:
            with open(capture.file, "rb") as f:
                returndata = f.read()
            return Response(
                returndata,
                headers={
                    "Content-Disposition": "attachment; filename={}".format(
                        capture.name
                    )
                },
            )
        else:
            raise NotFound("No capture found or no file found for this capture.")


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^background-capture/$",
            BackgorundCaptureListView.as_view(),
            name="background-capture-list",
        ),
        url(
            r"^background-capture/(?P<uuid>[^/]+)/file/$",
            BackgroundCaptureFileView.as_view(),
            name="background-capture-file",
        ),
        url(
            r"^background-capture-files/$",
            BackgroundCaptureFilesView.as_view(),
            name="background-capture-files",
        ),
        url(
            r"^background-capture/(?P<uuid>[^/]+)/file/local/$",
            BackgroundCaptureFileViewLocal.as_view(),
            name="background-capture-file-local",
        ),
    ]
)
