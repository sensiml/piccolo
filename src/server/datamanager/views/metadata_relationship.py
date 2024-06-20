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

import uuid

from datamanager.models import CaptureMetadataValue, update_capture_last_modified
from datamanager.serializers.capture_metadata_relationship import (
    V2CaptureMetadataRelationshipManySerializer,
    V2CaptureMetadataValueSerializer,
)
from datamanager.views.label_relationship import V2LabelRelationshipBySegmenterListView
from django.core.exceptions import ValidationError
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.views import APIView


@extend_schema_view(
    get=extend_schema(
        summary="List all capture metadata relationships for a capture",
        description="Returns a list of all capture metadata value relationships.  A capture metadata value relationship describes how a metadata value is associated with a capture file.",
        tags=["metadata-relationship"],
    ),
    post=extend_schema(
        summary="Bulk create API for capture metadata relationships",
        description="Post one or more capture metadata relationships to the server to associate metadata with a capture. A capture metadata value relationship describes how a metadata value is associated with a capture file.",
        tags=["metadata-relationship"],
    ),
    put=extend_schema(
        summary="Bulk update API for capture metadata relationships",
        description="Update one or more capture metadata relationships to the server to associate metadata with a capture. A capture metadata value relationship describes how a metadata value is associated with a capture file.",
        tags=["metadata-relationship"],
    ),
)
class MetadataRelationshipListView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = V2CaptureMetadataValueSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        if isinstance(kwargs.get("data"), dict):
            kwargs["data"] = [kwargs["data"]]
            kwargs["many"] = True

        return super(MetadataRelationshipListView, self).get_serializer(*args, **kwargs)

    def get_queryset(self, uuids=None):
        if uuids:
            return CaptureMetadataValue.objects.with_user(self.request.user).filter(
                project__uuid=self.kwargs["project_uuid"],
                capture__uuid=self.kwargs["capture_uuid"],
                uuid__in=uuids,
            )

        return (
            CaptureMetadataValue.objects.with_user(self.request.user)
            .select_related("label", "label_value")
            .filter(
                project__uuid=self.kwargs["project_uuid"],
                capture__uuid=self.kwargs["capture_uuid"],
            )
        )

    def validate_uuids(self, request):
        data = request.data

        if isinstance(data, list):
            uuid_list = [uuid.UUID(x["uuid"]) for x in data]

            if len(uuid_list) != len(set(uuid_list)):
                raise ValidationError(
                    "Multiple updates to a single label value relationship found. "
                )

            return uuid_list

        return [uuid.UUID(data)]

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        uuids = self.validate_uuids(request)
        instances = self.get_queryset(uuids=uuids)
        serializer = self.get_serializer(
            instances, data=request.data, partial=False, many=True
        )

        serializer.is_valid(raise_exception=True)

        for index, data in enumerate(serializer.validated_data):
            data["uuid"] = instances[index].uuid

        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


@extend_schema_view(
    get=extend_schema(
        summary="Get information about a capture metadata relationship by UUID",
        description="Returns information about a capture metadata relationship.",
        tags=["metadata-relationship"],
    ),
    put=extend_schema(
        summary="Update API for capture metadata relationships by UUID",
        description="Update a single capture metadata relationship.",
        tags=["metadata-relationship"],
    ),
    patch=extend_schema(
        summary="Update API for capture metadata relationships by UUID",
        description="Update a single capture metadata relationship.",
        tags=["metadata-relationship"],
    ),
    delete=extend_schema(
        summary="Delete API for capture metadata relationships by UUID",
        description="Delete a single capture metadata relationship.",
        tags=["metadata-relationship"],
    ),
)
class MetadataRelationshipDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    serializer_class = V2CaptureMetadataValueSerializer
    lookup_field = "uuid"

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        if isinstance(kwargs.get("data"), dict):
            kwargs["data"] = [kwargs["data"]]
            kwargs["many"] = True

        return super(MetadataRelationshipDetailView, self).get_serializer(
            *args, **kwargs
        )

    def get_queryset(self):
        return CaptureMetadataValue.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"],
            capture__uuid=self.kwargs["capture_uuid"],
        )

    def perform_destroy(self, instance):
        instance.delete()
        update_capture_last_modified(None, instance)


@extend_schema_view(
    get=extend_schema(
        summary="Get all capture metadata relationships by Project UUID",
        description="Returns all capture metadata relationships that are associated with a specific Project UUID.",
    ),
    post=extend_schema(
        summary="Bulk create API for capture metadata relationships for a Project UUID",
        description="Create one or more capture metadata relationships for a specific Project UUID.",
    ),
)
class ProjectMetadataRelationshipListView(V2LabelRelationshipBySegmenterListView):
    serializer_class = V2CaptureMetadataRelationshipManySerializer

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def get_queryset(self, uuids=None):
        if uuids:
            return CaptureMetadataValue.objects.with_user(self.request.user).filter(
                project__uuid=self.kwargs["project_uuid"],
                uuid__in=uuids,
            )

        return (
            CaptureMetadataValue.objects.with_user(self.request.user)
            .select_related("capture", "label", "label_value")
            .filter(project__uuid=self.kwargs["project_uuid"])
        )

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        if isinstance(kwargs.get("data"), dict):
            kwargs["data"] = [kwargs["data"]]
            kwargs["many"] = True

        return super(ProjectMetadataRelationshipListView, self).get_serializer(
            *args, **kwargs
        )


@extend_schema_view(
    post=extend_schema(
        summary="Get all capture metadata relationships for a list of captures",
        description="Returns all capture metadata relationships that are associated with a specific Project UUID and are in list of captures.",
        tags=["metadata-relationship"],
    ),
)
class ProjectCaptureMetadataRelationshipListView(APIView):
    serializer_class = V2CaptureMetadataRelationshipManySerializer

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def validate_capture_uuids(self):
        return {uuid.UUID(x) for x in self.request.data.get("capture_uuid_list")}

    def get_queryset(self):
        capture_uuids = self.validate_capture_uuids()

        self._queryset = (
            CaptureMetadataValue.objects.with_user(self.request.user)
            .select_related("capture", "label", "label_value")
            .filter(
                project__uuid=self.kwargs["project_uuid"],
                capture__uuid__in=capture_uuids,
            )
        )

        return self._queryset

    def post(self, request, *args, **kwargs):
        # We are mimicing a get request here but need to send lots of parameters so we pass it as a post in the body

        serializer = V2CaptureMetadataRelationshipManySerializer(
            self._queryset, many=True
        )
        return Response(serializer.data)


v1_url_patterns = [
    url(
        r"^project/(?P<project_uuid>[^/]+)/metadata-relationship/$",
        ProjectMetadataRelationshipListView.as_view(),
        name="project-metadata-relationship-list",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/capture-metadata-relationship/$",
        ProjectCaptureMetadataRelationshipListView.as_view(),
        name="project-capture-metadata-relationship-list",
    ),
]

v2_url_patterns = [
    url(
        r"^v2/project/(?P<project_uuid>[^/]+)/capture/(?P<capture_uuid>[^/]+)/metadata-relationship/$",
        MetadataRelationshipListView.as_view(),
        name="metadata-relationship-list",
    ),
    url(
        r"^v2/project/(?P<project_uuid>[^/]+)/capture/(?P<capture_uuid>[^/]+)/metadata-relationship/(?P<uuid>[^/]+)/$",
        MetadataRelationshipDetailView.as_view(),
        name="metadata-relationship-detail",
    ),
]


urlpatterns = format_suffix_patterns(v1_url_patterns + v2_url_patterns)
