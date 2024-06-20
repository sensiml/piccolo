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

from rest_framework import generics, permissions
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.parsers import (
    FileUploadParser,
    FormParser,
    JSONParser,
    MultiPartParser,
)

from datamanager.models import CaptureVideo
from datamanager.renderers import BinaryRenderer
from datamanager.datastore import get_datastore
from datamanager.serializers.capture_video import (
    CaptureVideoSerializer,
    CaptureVideoDetailSerializer,
    CaptureVideoBulkSerializer,
)

from django.urls import re_path as url
from django.shortcuts import redirect

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiParameter,
)


@extend_schema_view(
    get=extend_schema(
        summary="Get list of Capture Videos",
        description="Returns a list of capture videos in a project",
    ),
    post=extend_schema(
        summary="Upload a Capture video file",
        description="Create and upload a Capture video file",
        examples=[
            OpenApiExample(
                name="CaptureVideo object example",
                value=[
                    {
                        "uuid": "302672c6-714c-40e1-a08c-a61e518ebdf6",
                        "name": "Test.mp4",
                        "file_size": 1570024,
                        "keypoints": {
                            "trim_sensor_start": 2000,
                            "trim_sensor_end": 320000,
                            "trim_video_start": 0.11,
                            "trim_video_end": 0.88,
                            "keyframes": [
                                {"sensor_location": 1, "video_location": 10},
                                {"sensor_location": 20, "video_location": 30},
                            ],
                        },
                        "video": "/project/7be78efe-4ce7-451f-9bbf-ef3b5b5a3c84/capture/8dbeed81-388a-48a8-abc1-bc2e979d645d/video/302672c6-714c-40e1-a08c-a61e518ebdf6/video/",
                        "upload_url": "",  # for POST request with file_size
                        "created_at": "2024-04-24T04:30:38.701615Z",
                        "last_modified": "2024-04-24T04:30:38.701676Z",
                    }
                ],
            )
        ],
    ),
)
class CaptureVideoListCreateView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = CaptureVideoSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser, JSONParser)

    def get_queryset(self):
        return CaptureVideo.objects.with_user(self.request.user).filter(
            capture__uuid=self.kwargs.get("capture_uuid")
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get list of Capture Videos",
        description="Returns a list of capture videos in a project",
        parameters=[
            OpenApiParameter(
                name="capture_uuids[]",
                description="Optional to filter capture videos by multipy captures",
                examples=[
                    OpenApiExample(
                        name="?capture_uuids[]=uuid1&capture_uuids[]=uuid2&capture_uuids[]=uuid3"
                    )
                ],
            ),
        ],
    ),
)
class CaptureVideoBulkListView(generics.ListAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = CaptureVideoBulkSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser, JSONParser)

    def get_queryset(self):
        params = getattr(
            self.request, "query_params", getattr(self.request, "GET", None)
        )
        uuids = params.getlist("capture_uuids[]")
        if uuids:
            return CaptureVideo.objects.with_user(self.request.user).filter(
                capture__uuid__in=uuids
            )
        return CaptureVideo.objects.with_user(self.request.user).filter(
            capture__project__uuid=self.kwargs.get("project_uuid")
        )


class CaptureVideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = CaptureVideoDetailSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return CaptureVideo.objects.with_user(self.request.user).filter(
            capture__uuid=self.kwargs.get("capture_uuid")
        )


class CaptureVideoView(generics.GenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    renderer_classes = (BinaryRenderer,)
    lookup_field = "uuid"

    def get_queryset(self):
        res = CaptureVideo.objects.with_user(self.request.user).filter(
            capture__uuid=self.kwargs["capture_uuid"]
        )
        return res

    def get(self, request, *args, **kwargs):
        capture_video = self.get_object()
        datastore = get_datastore()

        if datastore.is_remote:
            return redirect(datastore.get_url(key=capture_video.remote_path))

        elif os.path.exists(capture_video.file_path):
            with open(capture_video.file_path, "rb") as f:
                returndata = f.read()
            return Response(
                returndata,
                headers={
                    "Content-Disposition": "attachment; filename={}".format(
                        capture_video.name
                    )
                },
            )

        raise NotFound("No capture video found.")


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^project/(?P<project_uuid>[^/]+)/video/$",
            CaptureVideoBulkListView.as_view(),
            name="capture-video-bulk-list",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture/(?P<capture_uuid>[^/]+)/video/$",
            CaptureVideoListCreateView.as_view(),
            name="capture-video-list",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture/(?P<capture_uuid>[^/]+)/video/(?P<uuid>[^/]+)/$",
            CaptureVideoDetailView.as_view(),
            name="capture-video",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture/(?P<capture_uuid>[^/]+)/video/(?P<uuid>[^/]+)/video/$",
            CaptureVideoView.as_view(),
            name="capture-video-file",
        ),
    ]
)
