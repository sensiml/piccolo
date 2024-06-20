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

from datamanager.models import CaptureConfiguration
from datamanager.serializers import (
    CaptureConfigurationDetailSerializer,
    CaptureConfigurationSerializer,
)
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework.urlpatterns import format_suffix_patterns


@extend_schema_view(
    get=extend_schema(
        summary="List Capture Configurations associated with a project UUID",
        description="Return a list of capture configurations for a project.",
    ),
    post=extend_schema(
        summary="Create a capture configuration",
        description="Post a capture configuration to the server and associate it with a specific project.",
    ),
)
class CaptureConfigurationListView(generics.ListCreateAPIView):

    serializer_class = CaptureConfigurationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def get_queryset(self):
        return CaptureConfiguration.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"]
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get a capture configuration by UUID",
        description="Get detailed information about a capture configuration",
    ),
    put=extend_schema(
        summary="Update a capture configuration by UUID",
        description="Update information about a capture configuration",
    ),
    patch=extend_schema(
        summary="Update a capture configuration by UUID",
        description="Update information about a capture configuration",
    ),
    delete=extend_schema(
        summary="Delete a capture configuration",
        description="Deletes a capture configuration and removes its associate from any capture files",
    ),
)
class CaptureConfigurationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    serializer_class = CaptureConfigurationDetailSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return CaptureConfiguration.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"]
        )


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^project/(?P<project_uuid>[^/]+)/captureconfiguration/$",
            CaptureConfigurationListView.as_view(),
            name="capture-configuration-list",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/captureconfiguration/(?P<uuid>[^/]+)/$",
            CaptureConfigurationDetailView.as_view(),
            name="capture-configuration-detail",
        ),
    ]
)
