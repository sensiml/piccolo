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
import os
from datamanager.decorators import login_required
from datamanager.models import Capture, Project, Segmenter
from datamanager.renderers import BinaryRenderer
from datamanager.datastore import get_datastore
from datamanager.serializers.capture import (
    CaptureDetailSerializer,
    CaptureSerializer,
    CaptureUpdateSerializer,
)
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
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
from rest_framework.urlpatterns import format_suffix_patterns


@extend_schema_view(
    get=extend_schema(
        summary="Get list of Captures",
        description="Returns a list of captures in a project",
    ),
    post=extend_schema(
        summary="Upload a CSV/WAV Capture file",
        description="Create and upload a CSV/WAV file the SensiML CLoud to use for training machine learning models",
    ),
)
class CaptureListView(generics.ListCreateAPIView):
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
        return (
            Capture.objects.with_user(self.request.user)
            .select_related("capture_configuration")
            .filter(project__uuid=self.kwargs["project_uuid"])
        )


@login_required
def captures_stats(request, project_uuid):
    capture_stats = []
    project_qs = Project.objects.with_user(user=request.user, uuid=project_uuid)
    if project_qs.exists():
        project_id = project_qs.first().id
        param_segmenter_id = request.GET.get("segmenter")
        segmenter_id = ""

        if param_segmenter_id:
            segmenter_id = (
                Segmenter.objects.with_user(user=request.user, id=param_segmenter_id)
                .first()
                .id
            )

        label_values_query_string = f"""SELECT l.name 
            FROM public.datamanager_label  l 
            WHERE  l.project_id  = {project_id}
            AND l.metadata = true
            ORDER BY l.name;
        """
        cursor = connection.cursor()
        cursor.execute(label_values_query_string)

        label_values = [row[0] for row in cursor.fetchall()]
        label_value_string = ""

        if label_values:
            label_value_string = ", " + ", ".join(
                f'"{val}" character varying(1000)' for val in label_values
            )

        segmenter_filter_query = (
            f"AND clv.segmenter_id = {segmenter_id}" if segmenter_id else ""
        )

        crosstab_query = f"""
            SELECT
                c.name,
                c.uuid,
                c.created_at created,
                ROUND(CAST(c.file_size/power(1024,2) AS NUMERIC),2) file_size_mb,
                c_cnf.uuid capture_configuration_uuid,
                x.*,
                coalesce(cc.total_events, 0) total_events
            FROM public.datamanager_capture c
            LEFT JOIN ( 
            SELECT * FROM
            crosstab(' 
            SELECT c.uuid, l.name, lv.value 
            	FROM public.datamanager_capture c 
                JOIN public.datamanager_label l 
            	ON c.project_id = l.project_id 
            	AND l.metadata = true 
            	LEFT JOIN public.datamanager_capturemetadatavalue cmv 
            	ON cmv.capture_id = c.id  
            	AND l.id = cmv.label_id 
            	LEFT JOIN public.datamanager_labelvalue lv 
            	ON cmv.label_value_id = lv.id 
            	WHERE c.project_id = {project_id} ORDER BY c.uuid, l.name') 
            AS ct(capture_uuid character varying(1000){label_value_string}) 
            ) as x 
            ON c.uuid = x.capture_uuid
            LEFT JOIN (SELECT c_cnf.uuid, c_cnf.id
                FROM public.datamanager_captureconfiguration c_cnf
                WHERE c_cnf.project_id = {project_id}) as c_cnf
            ON c_cnf.id = c.capture_configuration_id
            LEFT JOIN (SELECT clv.capture_id, count(1) total_events 
                FROM public.datamanager_capturelabelvalue clv  
                WHERE clv.project_id = {project_id} {segmenter_filter_query}
                GROUP BY clv.capture_id) as cc 
            ON cc.capture_id = c.id 
            WHERE c.project_id= {project_id};
        """

        cursor = connection.cursor()
        cursor.execute(crosstab_query)

        column_names = [desc[0] for desc in cursor.description]

        def row_to_dict(row):
            return dict(zip(column_names, row))

        capture_stats = [row_to_dict(row) for row in cursor.fetchall()]

    return JsonResponse(capture_stats, safe=False)


@extend_schema_view(
    get=extend_schema(
        summary="Get detailed information about a Capture file",
        description="",
    ),
    put=extend_schema(
        summary="Update properties of the Capture file",
        description="Update the name, calculated_sample_rate, set_sample_rate and capture_configuration of the Capture file",
    ),
    patch=extend_schema(
        summary="Update properties of the Capture file",
        description="Update the name, calculated_sample_rate, set_sample_rate and capture_configuration of the Capture file",
    ),
    delete=extend_schema(
        summary="Delete a Capture from the Server",
    ),
)
class CaptureDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = CaptureDetailSerializer
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return CaptureUpdateSerializer

        return CaptureDetailSerializer

    def get_queryset(self):
        return Capture.objects.with_user(self.request.user).all()


@extend_schema_view(
    get=extend_schema(
        summary="Download the Capture file",
        description="Downloads the CSV/WAV file from the server",
    ),
)
class CaptureFileView(generics.GenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    renderer_classes = (BinaryRenderer,)
    serializer_class = CaptureSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return Capture.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"]
        )

    def get(self, request, *args, **kwargs):
        capture = self.get_object()

        datastore = get_datastore(bucket=settings.AWS_S3_BUCKET)

        if capture.file:
            if datastore.is_remote:
                return redirect(datastore.get_url(capture.file))
            else:
                with open(capture.file, "rb") as f:
                    returndata = f.read()
                return Response(
                    returndata,
                    headers={
                        "Content-Disposition": f"attachment; filename={capture.name}"
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
class CaptureFilesView(generics.GenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = CaptureSerializer

    def get_queryset(self):
        return Capture.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"]
        )

    def get_local_url(self, uuid):
        return f"project/{self.kwargs['project_uuid']}/capture/{uuid}/file/local/"

    def post(self, request, *args, **kwargs):
        capture_uuid_list = self.request.data.get("capture_uuids")
        expires_in = min(self.request.data.get("expires_in", 100), 1000)
        datastore = get_datastore(bucket=settings.AWS_S3_BUCKET)
        queryset = self.get_queryset().filter(uuid__in=capture_uuid_list)

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
        else:
            redirect_urls = []
            for capture in queryset:
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
class CaptureFileViewLocal(CaptureFileView):
    def get(self, request, *args, **kwargs):
        capture = self.get_object()

        s3 = get_datastore(folder=os.path.join("capture", capture.project.uuid))
        s3.get("{}".format(basename(capture.file)), capture.file)

        if capture.file:
            with open(capture.file, "rb") as f:
                returndata = f.read()
            return Response(
                returndata,
                headers={"Content-Disposition": f"attachment; filename={capture.name}"},
            )
        else:
            raise NotFound("No capture found or no file found for this capture.")


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture/$",
            CaptureListView.as_view(),
            name="capture-list",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture-stats/$",
            captures_stats,
            name="captures-stats",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture/(?P<uuid>[^/]+)/$",
            CaptureDetailView.as_view(),
            name="capture-detail",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture/(?P<uuid>[^/]+)/file/$",
            CaptureFileView.as_view(),
            name="capture-file",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture-files/$",
            CaptureFilesView.as_view(),
            name="capture-files",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/capture/(?P<uuid>[^/]+)/file/local/$",
            CaptureFileViewLocal.as_view(),
            name="capture-file-local",
        ),
    ]
)
