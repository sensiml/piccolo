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

from datamanager.models import (
    Capture,
    CaptureLabelValue,
    CaptureMetadataValue,
    Label,
    LabelValue,
    Project,
    Segmenter,
    update_capture_last_modified,
)
from datamanager.serializers.capture_label_relationship import (
    V1CaptureLabelValueSerializer,
    V2CaptureLabelValueSerializer,
    V2ProjectCaptureLabelValueSerializer,
)
from datamanager.serializers.serializers import bulk_update_capture_last_modified
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.views import APIView
from datamanager.utils.pagination import QueryParamCursorPagination


@extend_schema_view(
    get=extend_schema(
        summary="List all capture label relationships for a capture",
        description="Returns a list of all capture label value relationships. A capture label value relationship describes how a label value is associated with a capture file including information about the session it belongs to, the label, and the start and end values.",
        tags=["label-relationship"],
    ),
    post=extend_schema(
        summary="Bulk create API for capture label relationships",
        description="Post one or more capture label relationships to the server to associate labels with regions of a capture. A capture label value relationship describes how a label value is associated with a capture file including information about the session it belongs to, the label, and the start and end values.",
        tags=["label-relationship"],
    ),
    put=extend_schema(
        summary="Bulk update API for capture label relationships",
        description="Update one or more capture label relationships to the server to associate labels with regions of a capture. A capture label value relationship describes how a label value is associated with a capture file including information about the session it belongs to, the label, and the start and end values.",
        tags=["label-relationship"],
    ),
)
class V2LabelRelationshipListView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = V2CaptureLabelValueSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        if isinstance(kwargs.get("data"), dict):
            kwargs["data"] = [kwargs["data"]]
            kwargs["many"] = True

        return super(V2LabelRelationshipListView, self).get_serializer(*args, **kwargs)

    def get_queryset(self, uuids=None):
        if uuids:
            return CaptureLabelValue.objects.with_user(self.request.user).filter(
                project__uuid=self.kwargs["project_uuid"],
                capture__uuid=self.kwargs["capture_uuid"],
                uuid__in=uuids,
            )

        return (
            CaptureLabelValue.objects.with_user(self.request.user)
            .select_related("capture", "label", "label_value", "segmenter")
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

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        uuids = self.validate_uuids(request)
        instances = self.get_queryset(uuids=uuids)
        serializer = self.get_serializer(
            instances, data=request.data, partial=False, many=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


@extend_schema_view(
    get=extend_schema(
        summary="Get all capture label relationships by Segmenter ID",
        description="Returns all capture label relationships that are associated with a specific Segmenter.",
        tags=["label-relationship"],
    ),
)
class LabelRelationshipBySegmenterListView(generics.ListAPIView):
    serializer_class = V1CaptureLabelValueSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def get_queryset(self):
        # TODO: Use tree traversal like django-mptt or something once my head isn't plugged up
        return CaptureLabelValue.objects.with_user(self.request.user).filter(
            Q(segmenter__pk=self.kwargs["segmenter_pk"])
            | Q(segmenter__parent__pk=self.kwargs["segmenter_pk"])
        )


@extend_schema_view(
    get=extend_schema(
        summary="Return all capture label relationships by project UUID",
        description="Returns all capture label relationships that are associated with a specific Project.",
    ),
)
class ProjectLabelRelationshipListView(generics.ListAPIView):
    serializer_class = V2CaptureLabelValueSerializer

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def get_queryset(self):
        return (
            CaptureLabelValue.objects.with_user(self.request.user)
            .select_related("capture", "label", "label_value", "segmenter")
            .filter(project__uuid=self.kwargs["project_uuid"])
        )


@extend_schema_view(
    post=extend_schema(
        summary="Bulk Delete of capture label relationships by project UUID",
        description="Delete one or more capture label relationships that are associated with a specific Project.",
        tags=["label-relationship"],
    ),
)
class ProjectLabelRelationshipDeleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def validate_uuids(self, request):
        data = request.data

        if isinstance(data, list):
            uuid_list = [uuid.UUID(x) for x in data]

            if len(uuid_list) != len(set(uuid_list)):
                raise ValidationError(
                    "Multiple updates to a single label value relationship found. "
                )

            return uuid_list

        return [uuid.UUID(data)]

    def get_queryset(self, uuids):
        if self.kwargs["label_or_metadata"] == "label":
            return CaptureLabelValue.objects.with_user(self.request.user).filter(
                project__uuid=self.kwargs["project_uuid"],
                uuid__in=uuids,
            )
        else:
            return CaptureMetadataValue.objects.with_user(self.request.user).filter(
                project__uuid=self.kwargs["project_uuid"],
                uuid__in=uuids,
            )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Deletes a list of label/metatadata value relationships returns number deleted"""

        uuids = self.validate_uuids(request)

        queryset = self.get_queryset(uuids)

        if len(queryset) != len(uuids):
            raise ValidationError("One or more UUIDs to delete was invalid.")

        captures = list({instance.capture for instance in queryset})

        response = queryset.delete()[0]

        bulk_update_capture_last_modified(captures)

        return Response(response, content_type="application/json")


@extend_schema_view(
    post=extend_schema(
        summary="Get capture label relationships associatd with a list of capture UUIDs",
        description="Return all capture label relationships associated with each capture UUID in the request.",
        tags=["label-relationship"],
    ),
)
class ProjectCaptureLabelRelationshipDetailListView(APIView):
    serializer_class = V2CaptureLabelValueSerializer

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    def validate_capture_uuids(self):
        return {uuid.UUID(x) for x in self.request.data.get("capture_uuid_list")}

    def get_queryset(self):
        capture_uuids = self.validate_capture_uuids()

        self._queryset = (
            CaptureLabelValue.objects.with_user(self.request.user)
            .select_related("capture", "label", "label_value", "segmenter")
            .filter(
                project__uuid=self.kwargs["project_uuid"],
                capture__uuid__in=capture_uuids,
            )
        )

        return self._queryset

    def post(self, request, *args, **kwargs):
        # We are mimicing a get request here but need to send lots of parameters so we pass it as a post in the body

        serializer = V2CaptureLabelValueSerializer(self._queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Get information about a capture label relationship by UUID",
        description="Returns information about a capture label relationship.",
        tags=["label-relationship"],
    ),
    put=extend_schema(
        summary="Update API for capture label relationships by UUID",
        description="Update a single capture label relationship.",
        tags=["label-relationship"],
    ),
    patch=extend_schema(
        summary="Update API for capture label relationships by UUID",
        description="Update a single capture label relationship.",
        tags=["label-relationship"],
    ),
    delete=extend_schema(
        summary="Delete API for capture label relationships by UUID",
        description="Delete a single capture label relationship.",
        tags=["label-relationship"],
    ),
)
class V2LabelRelationshipDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    lookup_field = "uuid"

    serializer_class = V2CaptureLabelValueSerializer

    def get_queryset(self):
        queryset = CaptureLabelValue.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"],
            capture__uuid=self.kwargs["capture_uuid"],
            uuid=self.kwargs["uuid"],
        )

        return queryset

    def perform_destroy(self, instance):
        instance.delete()
        update_capture_last_modified(None, instance)

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        if isinstance(kwargs.get("data"), dict):
            kwargs["data"] = [kwargs["data"]]
            kwargs["many"] = True

        return super(V2LabelRelationshipDetailView, self).get_serializer(
            *args, **kwargs
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get information about a capture label relationship for a Segment ID",
        description="Returns information about a capture label relationship.",
        tags=["label-relationship"],
    ),
    put=extend_schema(
        summary="Bulk update API for capture label relationships associated with a  Segment ID",
        description="Update one or more capture label relationships associated with a SegmentID.",
        tags=["label-relationship"],
    ),
    post=extend_schema(
        summary="Bulk create API for capture label relationships associated with a  Segment ID",
        description="Create one or more capture label relationships associated with a SegmentID.",
        tags=["label-relationship"],
    ),
    delete=extend_schema(
        summary="Bulk Delete API for capture label relationships associated with a SegmentID",
        description="Delete one ore more capture label relationships for a Segment ID.",
        tags=["label-relationship"],
    ),
)
class V2LabelRelationshipBySegmenterListView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    pagination_class = QueryParamCursorPagination
    serializer_class = V2ProjectCaptureLabelValueSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        if isinstance(kwargs.get("data"), dict):
            kwargs["data"] = [kwargs["data"]]
            kwargs["many"] = True

        return super(V2LabelRelationshipBySegmenterListView, self).get_serializer(
            *args, **kwargs
        )

    def get_queryset(self, uuids=None):
        if uuids:
            return CaptureLabelValue.objects.with_user(self.request.user).filter(
                project__uuid=self.kwargs["project_uuid"],
                segmenter__pk=self.kwargs["segmenter_pk"],
                uuid__in=uuids,
            )

        return CaptureLabelValue.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"],
            segmenter__pk=self.kwargs["segmenter_pk"],
        )

    def validate_uuids(self, data, field="uuid", unique=True):
        if isinstance(data, list):
            uuid_list = [uuid.UUID(x[field]) for x in data]

            if unique and len(uuid_list) != len(set(uuid_list)):
                raise ValidationError(
                    "Multiple updates to a single {} found".format(field)
                )

            return uuid_list

        return [uuid.UUID(data)]

    def validate_data(self, request, *args, **kwargs):

        label_uuids = set(
            self.validate_uuids(request.data, field="label", unique=False)
        )

        label_value_uuids = set(
            self.validate_uuids(request.data, field="label_value", unique=False)
        )
        capture_uuids = set(
            self.validate_uuids(request.data, field="capture", unique=False)
        )

        labels_queryset = Label.objects.filter(
            project__uuid=kwargs["project_uuid"], uuid__in=label_uuids
        )
        labels = {str(x.uuid): x for x in labels_queryset}

        captures = {
            str(x.uuid): x
            for x in Capture.objects.filter(
                project__uuid=kwargs["project_uuid"], uuid__in=capture_uuids
            )
        }

        label_values = {
            str(x.uuid): x
            for x in LabelValue.objects.filter(uuid__in=label_value_uuids)
        }

        for label_value in label_values.values():
            if label_value.label not in labels_queryset:
                raise Exception("Label Value is not associated with Label.")

        try:
            project = Project.objects.with_user(request.user).get(
                uuid=kwargs["project_uuid"]
            )
        except ObjectDoesNotExist:
            raise ValidationError("Project does not exist.")

        segmenter = None

        if kwargs.get("segmenter_pk", None):
            try:
                segmenter = Segmenter.objects.get(
                    pk=kwargs["segmenter_pk"],
                    project__uuid=kwargs["project_uuid"],
                )
            except ObjectDoesNotExist:
                raise ValidationError("Segmenter does not exist.")

        for index, instance in enumerate(request.data):
            instance["label"] = labels.get(instance["label"])
            instance["capture"] = captures.get(instance["capture"])
            instance["label_value"] = label_values.get(instance["label_value"])
            instance["project"] = project
            if segmenter is not None:
                instance["segmenter"] = segmenter

    def post(self, request, *args, **kwargs):
        self.validate_data(request, *args, **kwargs)

        return super(V2LabelRelationshipBySegmenterListView, self).post(
            request, *args, **kwargs
        )

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        uuids = self.validate_uuids(request.data)
        instances = self.get_queryset(uuids=uuids)
        self.validate_data(request, *args, **kwargs)
        serializer = self.get_serializer(
            instances, data=request.data, partial=False, many=True
        )
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


v1_url_patterns = [
    url(
        r"^project/(?P<project_uuid>[^/]+)/label-relationship/",
        ProjectLabelRelationshipListView.as_view(),
        name="project-label-relationship-list",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/capture-label-relationship/",
        ProjectCaptureLabelRelationshipDetailListView.as_view(),
        name="project-capture-label-relationship-list",
    ),
]

v2_url_patterns = [
    url(
        r"^project/(?P<project_uuid>[^/]+)/capture/(?P<capture_uuid>[^/]+)/label-relationship/$",
        V2LabelRelationshipListView.as_view(),
        name="label-relationship-list",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/capture/(?P<capture_uuid>[^/]+)/label-relationship/(?P<uuid>[^/]+)/$",
        V2LabelRelationshipDetailView.as_view(),
        name="label-relationship-detail",
    ),
    url(
        r"^v2/project/(?P<project_uuid>[^/]+)/(?P<label_or_metadata>label|metadata)-relationship/delete/$",
        ProjectLabelRelationshipDeleteView.as_view(),
        name="relationship-delete",
    ),
    url(
        r"^v2/project/(?P<project_uuid>[^/]+)/segmenter/(?P<segmenter_pk>[^/]+)/label-relationship/$",
        V2LabelRelationshipBySegmenterListView.as_view(),
        name="v2-segmenter-label-relationship-list",
    ),
]


urlpatterns = format_suffix_patterns(v1_url_patterns + v2_url_patterns)
