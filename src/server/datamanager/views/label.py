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

from datamanager.models import Label, LabelValue
from datamanager.serializers import LabelSerializer, LabelValueDetailSerializer
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework.urlpatterns import format_suffix_patterns


@extend_schema_view(
    get=extend_schema(
        summary="Get list of label(or metadata) and their label values",
        description="Returns a list of label(or metadata)  and their label values for a project.",
        tags=["label and metadata"],
    ),
    post=extend_schema(
        summary="Create a label(or metadata) and associated label values",
        description="Create multiple label(or metadata) and their associated label values",
        tags=["label and metadata"],
    ),
)
class LabelListView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = LabelSerializer

    def get_queryset(self):
        return Label.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"],
            metadata=True if self.kwargs["label_or_metadata"] == "metadata" else False,
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get detailed information about a single label(or metadata) and label values",
        description="Get detailed information about a single label(or metadata) and label values",
        tags=["label and metadata"],
    ),
    put=extend_schema(
        summary="Update the name, type or is_dropdown property",
        description="Update the name, type or is_dropdown property",
        tags=["label and metadata"],
    ),
    patch=extend_schema(
        summary="Update the name, type or is_dropdown property",
        description="Update the name, type or is_dropdown property",
        tags=["label and metadata"],
    ),
    delete=extend_schema(
        summary="Delete a label (or metadata) and its corresponding label values",
        description="Delete a label (or metadata) and its corresponding label values",
        tags=["label and metadata"],
    ),
)
class LabelDetailView(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = "uuid"
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = LabelSerializer

    def get_queryset(self):
        return Label.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"],
            metadata=True if self.kwargs["label_or_metadata"] == "metadata" else False,
        )


@extend_schema_view(
    get=extend_schema(
        summary="List label values for a specific label (or metdata)",
        description="Returns a list of label values for a specific label (or metdata)",
    ),
    post=extend_schema(
        summary="Create a  label values for a specific label (or metdata)",
        description="Create a  label values for a specific label (or metdata)",
    ),
)
class LabelValueListView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = LabelValueDetailSerializer

    def get_queryset(self):
        return LabelValue.objects.filter(label__uuid=self.kwargs["label_uuid"])


@extend_schema_view(
    get=extend_schema(
        summary="Get detailed information about a single label value",
        description="",
    ),
    put=extend_schema(
        summary="Update a label value color or value",
        description="",
    ),
    patch=extend_schema(
        summary="Update a label value color or value",
        description="",
    ),
    delete=extend_schema(
        summary="Delete a label value",
        description="",
    ),
)
class LabelValueDetailView(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = "uuid"
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    serializer_class = LabelValueDetailSerializer

    def get_queryset(self):
        return LabelValue.objects.filter(label__uuid=self.kwargs["label_uuid"])


v1_url_patterns = [
    url(
        r"^project/(?P<project_uuid>[^/]+)/(?P<label_or_metadata>label|metadata)/$",
        LabelListView.as_view(),
        name="label-list",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/(?P<label_or_metadata>label|metadata)/(?P<uuid>[^/]+)/$",
        LabelDetailView.as_view(),
        name="label-detail",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/(?P<label_or_metadata>label|metadata)/(?P<label_uuid>[^/]+)/labelvalue/$",
        LabelValueListView.as_view(),
        name="labelvalue-list",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/(?P<label_or_metadata>label|metadata)/(?P<label_uuid>[^/]+)/labelvalue/(?P<uuid>[^/]+)/$",
        LabelValueDetailView.as_view(),
        name="labelvalue-detail",
    ),
]


urlpatterns = format_suffix_patterns(v1_url_patterns)
