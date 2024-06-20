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

from datamanager.models import Segmenter
from datamanager.serializers import SegmenterSerializer
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework.urlpatterns import format_suffix_patterns


@extend_schema_view(
    get=extend_schema(
        summary="List Segmenter associated with a Project UUID",
        description="Returns a list of all the segmenters that have been added to the project",
    ),
    post=extend_schema(
        summary="Create a new segmenter",
        description="Creates a new segmenter and adds it to the project",
    ),
)
class SegmenterListView(generics.ListCreateAPIView):
    serializer_class = SegmenterSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def get_queryset(self):
        return Segmenter.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"]
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get information about a segmenter",
        description="Returns detailed information about a specific segmenter",
    ),
    put=extend_schema(
        summary="Update a Segmenter by id",
        description="Updates the segmenter parameters",
    ),
    patch=extend_schema(
        summary="Update a Segmenter by id",
        description="Partial updates of the segmenter parameters",
    ),
    delete=extend_schema(
        summary="Delete a Segmenter",
        description="Deletes a segmenter",
    ),
)
class SegmenterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SegmenterSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def get_queryset(self):
        return Segmenter.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"]
        )


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^project/(?P<project_uuid>[^/]+)/segmenter/$",
            SegmenterListView.as_view(),
            name="segmenter-list",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/segmenter/(?P<pk>[^/]+)/$",
            SegmenterDetailView.as_view(),
            name="segmenter-detail",
        ),
    ]
)
