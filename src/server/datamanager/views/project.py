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
import time
import traceback

from datamanager.decorators import login_required
from datamanager import pipeline_queue, utils
from datamanager.exceptions import FileUploadError
from datamanager.models import Project, CaptureLabelValue
from datamanager.datastore import get_datastore, get_datastore_basedir
from datamanager.serializers import (
    ProjectActivePipelineSerializer,
    ProjectSerializer,
    ProjectSummarySerializer,
    TeamProjectSerializer,
)
from django.http import JsonResponse
from datamanager.tasks import delete_project_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, transaction
from django.shortcuts import redirect
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from logger.log_handler import LogHandler
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.urlpatterns import format_suffix_patterns

logger = LogHandler(logging.getLogger("datamanager"))


@extend_schema_view(
    get=extend_schema(
        summary="Get active pipelines",
        description="Returns a list of the active pipelines in a project.",
        tags=["project"],
    ),
)
class ProjectActivePipelineView(generics.RetrieveAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    lookup_field = "uuid"

    serializer_class = ProjectActivePipelineSerializer

    def get_queryset(self):
        return Project.objects.with_user(self.request.user).all()


@extend_schema_view(
    list=extend_schema(
        summary="List project summaries",
        description="Returns a list of project summaries",
        tags=["project"],
    ),
)
class ProjectSummaryView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = ProjectSummarySerializer

    def list(self, request, uuid=None):
        time.time()
        projects = Project.objects.with_user(self.request.user).all()

        if uuid is not None:
            projects = projects.filter(uuid=uuid)

        if not projects:
            return Response(ProjectSummarySerializer(instance=[], many=True).data)

        projectUuids = ", ".join("'" + p.uuid + "'" for p in projects)

        segments_query_string = """
                SELECT
                    p.uuid,
                    count(DISTINCT l.id) segments
                FROM
                    public.datamanager_project p
                    LEFT OUTER JOIN public.datamanager_capturelabelvalue l ON p.id = l.project_id
                WHERE
                    p.uuid in ({})
                GROUP BY p.uuid;
                """.format(
            projectUuids
        )
        segments_cursor = connection.cursor()
        segments_cursor.execute(segments_query_string)
        segment_counts = {}
        for row in segments_cursor.fetchall():
            segment_counts[row[0]] = row[1]

        query_string = """
                SELECT
                    p.uuid,
                    p.name,
                    p.created_at,
                    p.description,
                    c.files,
                    c.size_mb,
                    s.pipelines,
                    q.queries,
                    k.models,
                    cv.videos,
                    cv.video_size_mb
                FROM
                    public.datamanager_project p
                    LEFT OUTER JOIN (
                        SELECT
                            project_id,
                            count(id) files,
                            sum(file_size) / power(1024, 2) size_mb
                        FROM
                            public.datamanager_capture
                        GROUP BY
                            project_id
                    ) c ON p.id = c.project_id
                    LEFT JOIN (
                        SELECT
                            count(1) videos,
                            sum(cvi.file_size) / power(1024, 2) video_size_mb,
                            cvc.project_id
                        FROM
                            public.datamanager_capturevideo cvi
                        JOIN (SELECT id, project_id FROM public.datamanager_capture) AS cvc ON cvi.capture_id = cvc.id
                        GROUP BY
                            cvc.project_id
                    ) AS cv ON p.id = cv.project_id
                    LEFT OUTER JOIN (
                        SELECT
                            count(s.id) pipelines, s.project_id
                        FROM
                            public.datamanager_sandbox s
                        WHERE s.private = false                            
                        GROUP BY
                            project_id                                                    
                    ) as s
                    ON s.project_id = p.id        
                    LEFT OUTER JOIN (
                        SELECT
                            count(q.id) queries, q.project_id
                        FROM
                            public.datamanager_query q                        
                        GROUP BY
                            project_id                                                    
                    ) as q
                    ON q.project_id = p.id       
                    LEFT OUTER JOIN (
                        SELECT
                            count(k.id) models, k.project_id
                        FROM
                            public.datamanager_knowledgepack k                    
                        GROUP BY
                            project_id                                                    
                    ) as k
                    ON k.project_id = p.id                            
                WHERE
                    p.uuid in ({project_uuid})
                """.format(
            project_uuid=projectUuids
        )

        cursor = connection.cursor()
        cursor.execute(query_string)
        result_list = []

        for row in cursor.fetchall():
            result_obj = {
                "uuid": row[0],
                "name": row[1],
                "created_at": row[2],
                "description": row[3],
                "files": row[4] if row[4] is not None else 0,
                "size_mb": round(float(row[5]), 2) if row[5] is not None else 0,
                "pipelines": row[6] if row[6] is not None else 0,
                "queries": row[7] if row[7] is not None else 0,
                "models": row[8] if row[8] is not None else 0,
                "videos": row[9] if row[9] is not None else 0,
                "video_size_mb": round(float(row[10]), 2) if row[10] is not None else 0,
                "segments": (
                    segment_counts[row[0]] if segment_counts[row[0]] is not None else 0
                ),
            }

            if uuid is not None:
                return Response(ProjectSummarySerializer(instance=result_obj).data)

            result_list.append(result_obj)

        response = ProjectSummarySerializer(instance=result_list, many=True).data

        return Response(response)


def fields(cursor):
    """Given a DB API 2.0 cursor object that has been executed, returns
    a dictionary that maps each field name to a column index; 0 and up."""
    results = {}
    column = 0
    for d in cursor.description:
        results[d[0]] = column
        column = column + 1

    return results


def generate_sessions(clv):
    sessions = []
    session_name_index = {}

    if clv is None:
        return sessions

    for segment in clv:
        if session_name_index.get(segment.segmenter.name) is None:
            session_name_index[segment.segmenter.name] = len(sessions)
            sessions.append({"session_name": segment.segmenter.name, "segments": []})

        session_index = session_name_index[segment.segmenter.name]

        sessions[session_index]["segments"].append(
            {
                "name": segment.label.name,
                "value": segment.label_value.value,
                "start": segment.capture_sample_sequence_start,
                "end": segment.capture_sample_sequence_end,
            }
        )

    return sessions


@login_required
def get_dcli(request, project_uuid):
    capture_stats = []
    if Project.objects.with_user(user=request.user, uuid=project_uuid).exists():
        project_id = Project.objects.get(uuid=project_uuid).id

        clv = (
            CaptureLabelValue.objects.with_user(request.user)
            .select_related("capture", "label", "label_value", "segmenter")
            .only(
                "capture_sample_sequence_start",
                "capture_sample_sequence_end",
                "capture",
                "label",
                "segmenter",
                "label_value",
                "capture__name",
                "label__name",
                "segmenter__name",
                "label_value__value",
            )
            .filter(project__uuid=project_uuid)
        )

        capture_lv = {}
        for segment in list(clv):
            if segment.capture.name not in capture_lv:
                capture_lv[segment.capture.name] = [segment]
            else:
                capture_lv[segment.capture.name].append(segment)

        label_values_query_string = """SELECT l.name 
            FROM public.datamanager_label  l 
            WHERE  l.project_id  = {}
            AND l.metadata = true 
            ORDER BY l.name ;""".format(
            project_id
        )
        cursor = connection.cursor()
        cursor.execute(label_values_query_string)

        label_values = []
        label_value_string = ""

        for row in cursor.fetchall():
            label_values.append(row[0])

        if label_values:
            column_type = '" character varying(1000)'
            label_value_string = '{}, "'.format(column_type)
            label_value_string = (
                ', "' + label_value_string.join(label_values) + column_type
            )

        crosstab_query = """
            SELECT c.name, x.* 
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
            	WHERE c.project_id = {}  ORDER BY c.uuid, l.name') 
            AS ct(capture_uuid character varying(1000){}) 
            ) as x 
            ON c.uuid = x.capture_uuid 
            LEFT JOIN (SELECT clv.capture_id, count(1) total_events 
            	  FROM public.datamanager_capturelabelvalue clv  
            	  WHERE clv.project_id  = {}
            	   GROUP BY clv.capture_id) as cc 
            ON cc.capture_id = c.id 
            WHERE c.project_id= {}""".format(
            project_id, label_value_string, project_id, project_id
        )

        cursor = connection.cursor()
        cursor.execute(crosstab_query)
        field_map = fields(cursor)

        for row in cursor.fetchall():
            metadata = []

            for label_value in label_values:
                metadata.append(
                    {"name": label_value, "value": row[field_map[label_value]]}
                )

            capture_stat = {
                "file_name": row[field_map["name"]],
                "metadata": metadata,
                "sessions": generate_sessions(capture_lv.get(row[field_map["name"]])),
            }

            capture_stats.append(capture_stat)

    return JsonResponse(capture_stats, safe=False)


@extend_schema_view(
    list=extend_schema(
        summary="Get the  project summary",
        description="Returns the project summary for a specific project",
        tags=["project"],
    ),
)
class ProjectSummaryViewDetail(ProjectSummaryView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSummarySerializer


@extend_schema_view(
    get=extend_schema(
        summary="List Projects",
        description="Return a list of all the projects in the team.",
        tags=["project"],
    ),
    post=extend_schema(
        summary="Create a project",
        description="Create a new project in your team",
        tags=["project"],
    ),
)
class ProjectListView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    lookup_field = "uuid"

    def get_queryset(self):
        return Project.objects.with_user(self.request.user).all()

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return ProjectSerializer
        else:
            return TeamProjectSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Get Project by UUID",
        description="Get detailed information about a project",
        tags=["project"],
    ),
    put=extend_schema(
        summary="Update Project by UUID",
        description="Update information about a project",
        tags=["project"],
    ),
    patch=extend_schema(
        summary="Update Project by UUID",
        description="Update information about a project",
        tags=["project"],
    ),
    delete=extend_schema(
        summary="Delete a Project",
        description="Deletes a project and all associated models and data",
        tags=["project"],
    ),
)
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = ProjectSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return Project.objects.with_user(self.request.user).all()

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return ProjectSerializer
        else:
            return TeamProjectSerializer

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        try:
            name = request.META["COMPUTERNAME"]
        except Exception:
            name = "name unavailable"
        logger.info(
            {
                "message": "Deleting project: {0}, request made by {1}, on {2}".format(
                    project.name, request.user.username, name
                ),
                "log_type": "datamanager",
            }
        )
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        summary="Get the Project thumbnail",
        description="Get the project image thumbnail",
        tags=["project"],
    ),
    post=extend_schema(
        summary="Set the project image thumbnail",
        description="Upload a new project image",
        tags=["project"],
    ),
)
class ProjectImageView(generics.GenericAPIView):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)

    lookup_field = "uuid"

    def get_queryset(self):
        queryset = Project.objects.all()

        return queryset

    def get(self, request, *args, **kwargs):
        project = self.get_object()

        if project.image_file_name is None:
            # return default image if an image file is not set
            return redirect("/static/images/noimage_icon.png")

        datastore = get_datastore(folder="projectimages")

        if datastore.is_remote:
            return redirect(datastore.get_url(project.image_file_name))
        else:
            return redirect(f"/static/projectimages/{project.image_file_name}")

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        try:
            utils.ensure_path_exists(settings.SERVER_PROJECT_IMAGE_ROOT)
            folder = os.path.join(settings.SERVER_PROJECT_IMAGE_ROOT)
            if not os.path.isdir(folder):
                os.mkdir(folder)

            file_name = str(request.data.get("name"))
            name, ext = os.path.splitext(file_name)
            new_file_name = "{0}{1}".format(project.uuid, ext.lower())
            file_path = "{0}/{1}".format(folder, new_file_name)

            with open(file_path, "wb") as f:
                uploaded_file = request.data.get("file")
                uploaded_file.seek(0)
                for chunk in uploaded_file:
                    f.write(chunk)
                f.seek(0)

            datastore = get_datastore(
                folder=get_datastore_basedir(settings.SERVER_PROJECT_IMAGE_ROOT)
            )

            if datastore.is_remote:
                datastore.save(new_file_name, file_path, delete=True)
                project.image_file_name = new_file_name
            else:
                project.image_file_name = new_file_name

            project.save()
            return Response(True)
        except Exception as e:
            logger.error({"message": traceback.format_exc(), "log_type": "datamanager"})
            raise FileUploadError(e)


@extend_schema_view(
    post=extend_schema(
        summary="Set the project image",
        description="Upload a new project image",
        exclude=True,
    ),
    delete=extend_schema(
        summary="Set the project image",
        description="Upload a new project image",
        exclude=True,
    ),
)
class ProjectProfileView(generics.GenericAPIView):
    permission_classes = (permissions.DjangoModelPermissions,)
    lookup_field = "uuid"

    def get_queryset(self):
        return Project.objects.with_user(self.request.user).all()

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        project.optimized = True
        project.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        project.profile = None
        project.optimized = False

        project.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        summary="Get project delete status",
        description="Get detailed information about a project",
        tags=["project"],
    ),
    post=extend_schema(
        summary="Delete a Project asynchronously",
        description="Deletes a project and all associated models and data asynchronously",
        tags=["project"],
    ),
    delete=extend_schema(
        summary="Clears the state and kills the project delete task",
        description="Terminates any task that is running the delete project job and resets the state",
        tags=["project"],
    ),
)
class ProjectDestroyView(generics.GenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = serializers.Serializer()
    lookup_field = "uuid"

    def get_queryset(self):
        return Project.objects.with_user(self.request.user).all()

    def get(self, request, *args, **kwargs):
        try:
            project = self.get_object()
        except ObjectDoesNotExist:
            return Response("Project does not exist", status=404)
        except Exception:
            return Response("Project does not exist", status=404)

        return Response(
            {"status": pipeline_queue.get_task_status("project", project.uuid)}
        )

    def post(self, request, *args, **kwargs):
        return self.async_delete(request, self.kwargs["uuid"])

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object()
        except ObjectDoesNotExist:
            return Response("Project does not exist", status=404)
        except Exception:
            return Response("Project does not exist", status=404)

        result = pipeline_queue.kill_task("project", self.kwargs["uuid"])

        if result.task_id:
            logger.userlog(
                {
                    "message": "project delete terminated",
                    "log_type": "PID",
                    "project_uuid": self.kwargs["uuid"],
                    "task_id": result.task_id,
                }
            )

            return Response(
                "Project '{}' delete execution was terminated.".format(result.task_id)
            )
        else:
            return Response("Project not currently being deleted.")

    def async_delete(self, request, uuid):
        try:
            self.get_object()
        except ObjectDoesNotExist:
            return Response("Project does not exist", status=404)
        except Exception:
            return Response("Project does not exist", status=404)

        pipeline_queue.set_start_task("project", uuid)

        sent_job = delete_project_task.delay(request.user.id, uuid)

        pipeline_queue.set_task_id("project", uuid, sent_job.task_id)
        logger.userlog(
            {
                "message": "Project Set to delete",
                "log_type": "PID",
                "UUID": uuid,
                "task_id": sent_job.task_id,
            }
        )

        return Response("Project delete task started.", status=200)


urlpatterns = [
    url(r"^project/$", ProjectListView.as_view(), name="project-list"),
    url(
        r"^project/(?P<uuid>[^/]+)/$",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),
    url(
        r"^project-summary/$",
        ProjectSummaryView.as_view({"get": "list"}),
        name="project-summary",
    ),
    url(
        r"^project-delete/(?P<uuid>[^/]+)/$",
        ProjectDestroyView.as_view(),
        name="project-delete",
    ),
    url(
        r"^project-summary/(?P<uuid>[^/]+)/$",
        ProjectSummaryViewDetail.as_view({"get": "list"}),
        name="project-summary-detail",
    ),
    url(
        r"^project/(?P<uuid>[^/]+)/profile/$",
        ProjectProfileView.as_view(),
        name="project-profile",
    ),
    url(
        r"^project/(?P<uuid>[^/]+)/active/$",
        ProjectActivePipelineView.as_view(),
        name="project-active",
    ),
    url(
        r"^project/(?P<uuid>[^/]+)/image/$",
        ProjectImageView.as_view(),
        name="project-image",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/dcli/$",
        get_dcli,
        name="dcli",
    ),
]
urlpatterns = format_suffix_patterns(urlpatterns)
