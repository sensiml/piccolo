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

import datamanager.pipeline_queue as pipeline_queue
from datamanager.models import Query
from datamanager.serializers.query import QuerySerializer
from datamanager.tasks import querydata_async
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.urlpatterns import format_suffix_patterns


@extend_schema_view(
    get=extend_schema(
        summary="List all queries in a project by UUID",
        description="Returns a list of all queries created within a project.",
    ),
    post=extend_schema(
        summary="Create a new query",
        description="Create a new query in a project.",
    ),
)
class QueryListView(generics.ListCreateAPIView):

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = QuerySerializer

    def get_queryset(self):
        return Query.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"]
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get information about query by UUID",
        description="Returns information about a query.",
    ),
    put=extend_schema(
        summary="Update API for query by UUID",
        description="Update a single query.",
    ),
    patch=extend_schema(
        summary="Update API for query by UUID",
        description="Update a single query.",
    ),
    delete=extend_schema(
        summary="Delete API for query by UUID",
        description="Delete a single query along with any cached data.",
    ),
)
class QueryDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = QuerySerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return Query.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"]
        )


# @csrf_exempt
@extend_schema_view(
    get=extend_schema(
        summary="Get information about query cache build job",
        description="Returns information about a query cache status.",
    ),
    post=extend_schema(
        summary="Rebuild the query cache",
        description="Submits a job request to build the query cache.",
    ),
    delete=extend_schema(
        summary="Stop the query cache build pipeline",
        description="Terminates the query cache build job if one is running.",
    ),
)
@api_view(("GET", "POST", "DELETE"))
@permission_classes((permissions.IsAuthenticated,))
def query_cache_api(request, project_uuid, query_uuid):

    query = Query.objects.with_user(request.user).get(
        project__uuid=project_uuid, uuid=query_uuid
    )

    if request.method == "GET":

        if query.task_status == "COMPLETE":
            return Response(
                {
                    "status": "Query Completed",
                }
            )

        status, message, detail = pipeline_queue.get_pipeline_status(
            project_id=query.project.uuid, sandbox_id=query.uuid
        )

        return Response(
            {
                "status": status,
                "message": message,
                "detail": detail,
            }
        )

    elif request.method == "POST":

        pipeline_queue.set_start_sandbox(
            project_id=query.project.uuid, sandbox_id=query.uuid
        )

        pipeline_queue.set_query_to_active(
            project_uuid=query.project.uuid,
            query_uuid=query.uuid,
            execution_type="query_data",
        )

        sent_job = querydata_async.delay(
            request.user.id, query.project.uuid, query.uuid
        )
        query.task = sent_job.task_id
        query.task_status = "BUILDING"
        query.cache = None
        query.summary_statistics = None
        query.segment_info = None
        query.save()

        pipeline_queue.set_pipeline_task_id(query.project.uuid, query.uuid, query.task)

        return Response(status=200)

    elif request.method == "DELETE":

        result = pipeline_queue.kill_query(
            project_id=query.project.uuid, query_id=query.uuid
        )

        if result.task_id:
            return Response(
                "Query '{}' execution was terminated.".format(result.task_id)
            )
        else:
            return Response("Query is not currently running.")


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^project/(?P<project_uuid>[^/]+)/query/(?P<uuid>[^/]+)/$$",
            QueryDetailView.as_view(),
            name="query-detail",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/query/$",
            QueryListView.as_view(),
            name="query-list",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/query/(?P<query_uuid>[^/]+)/cache/$",
            query_cache_api,
            name="query-cache",
        ),
    ]
)
