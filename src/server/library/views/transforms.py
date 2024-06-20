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
import shutil

from datamanager.datastore import get_datastore
from django.conf import settings
from django.db.models import Q
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from library.models import CustomTransform, LibraryPack, Transform
from library.serializers.serializers import (
    CustomTransformDetailsSerializer,
    CustomTransformSerializer,
    LibraryPackSerializer,
    TransformSerializer,
)
from rest_framework import generics, permissions
from rest_framework.parsers import (
    FileUploadParser,
    FormParser,
    JSONParser,
    MultiPartParser,
)


@extend_schema_view(
    get=extend_schema(
        summary="List Transforms",
        description="List the Transforms that are available to your team.",
    ),
)
class TransformListView(generics.ListAPIView):
    serializer_class = TransformSerializer

    def get_queryset(self):
        return Transform.objects.filter(
            Q(library_pack__team=self.request.user.teammember.team)
            | Q(library_pack__isnull=True)
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get Transform by UUID",
        description="Get detailed information about a specific transform.",
    ),
)
class TransformDetailView(generics.RetrieveAPIView):
    queryset = Transform.objects.all()
    serializer_class = TransformSerializer
    lookup_field = "uuid"


@extend_schema_view(
    get=extend_schema(
        summary="List Segmenters",
        description="List the Segmenters that are available to your team.",
    ),
)
class SegmenterListView(generics.ListAPIView):
    queryset = Transform.objects.filter(type="Segmenter", dcl_executable=True)
    serializer_class = TransformSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Get Segmenters by UUID",
        description="Get detailed information about a specific segmenter.",
    ),
)
class SegmenterDetailView(generics.RetrieveAPIView):
    queryset = Transform.objects.filter(type="Segmenter", dcl_executable=True)
    serializer_class = TransformSerializer
    lookup_field = "uuid"


@extend_schema_view(
    get=extend_schema(
        summary="List Custom Transforms",
        description="List the Custom Transforms that are available to your team",
    ),
    post=extend_schema(
        summary="Create Custom Transform",
        description="Upload a new Custom Transforms to your team",
    ),
)
class CustomTransformListView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    serializer_class = CustomTransformSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser, JSONParser)

    def get_queryset(self):

        return CustomTransform.objects.filter(
            library_pack__team=self.request.user.teammember.team
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get Custom Transforms by UUID",
        description="Get Detail information on a Custom Transforms that is available to your team",
    ),
    put=extend_schema(
        summary="Update Custom Transform",
    ),
    patch=extend_schema(
        summary="Partial Update Custom Transform",
    ),
    delete=extend_schema(
        summary="Delete Custom Transform by UUID",
        description="Delete a Custom Transforms",
    ),
)
class CustomTransformDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    serializer_class = CustomTransformDetailsSerializer
    lookup_field = "uuid"

    def get_queryset(self):

        return CustomTransform.objects.filter(
            library_pack__team=self.request.user.teammember.team
        )

    def perform_destroy(self, instance):

        folder = "custom_transforms/{}".format(self.request.user.teammember.team.uuid)

        datastore = get_datastore(folder=folder)

        # TODO: DATASTORE put into single call
        if datastore.is_remote:
            datastore.delete(instance.file_path)
        else:
            file_path = os.path.join(
                settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                str(instance.library_pack.uuid),
                instance.file_path,
            )
            os.remove(file_path)

        instance.delete()


@extend_schema_view(
    get=extend_schema(
        summary="List Library Packs",
        description="List the Library Packs that are available to your team",
    ),
    post=extend_schema(
        summary="Create a Library Pack",
        description="Create a new Library Pack for your team",
    ),
)
class LibraryPackListView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    serializer_class = LibraryPackSerializer

    def get_queryset(self):

        return LibraryPack.objects.filter(team=self.request.user.teammember.team)


@extend_schema_view(
    get=extend_schema(
        summary="Get a Library Pack by UUID",
        description="Get Detail information on a Library Pack that is available to your team",
    ),
    put=extend_schema(
        summary="Update a Library Pack",
    ),
    patch=extend_schema(
        summary="Partial Update a Library Pack",
    ),
    delete=extend_schema(
        summary="Delete a Library Pack by UUID",
        description="Delete Library Packs and its associated Custom Transforms",
    ),
)
class LibraryPackDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )

    serializer_class = LibraryPackSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return LibraryPack.objects.filter(team=self.request.user.teammember.team)

    def perform_destroy(self, instance):

        folder = f"custom_transforms/{nstance.uuid}"

        datastore = get_datastore(folder=folder)
        # TOOD: DATASTORE put in single call
        if datastore.is_remote:
            datastore.remove_folder("")
        else:
            file_path = os.path.join(
                settings.SERVER_CUSTOM_TRANSFORM_ROOT, str(instance.uuid)
            )
            try:
                shutil.rmtree(file_path)
            except FileNotFoundError:
                pass

        instance.delete()


urlpatterns = [
    url(r"^transform/$", TransformListView.as_view(), name="transform-list"),
    url(
        r"^transform/(?P<uuid>[^/]+)/$",
        TransformDetailView.as_view(),
        name="transform-detail",
    ),
    url(r"^segmenter/$", SegmenterListView.as_view(), name="segmenter-list"),
    url(
        r"^segmenter/(?P<uuid>[^/]+)/$",
        SegmenterDetailView.as_view(),
        name="segmenter-detail",
    ),
    url(
        r"^custom-transform/$",
        CustomTransformListView.as_view(),
        name="custom-transform-list",
    ),
    url(
        r"^custom-transform/(?P<uuid>[^/]+)/$",
        CustomTransformDetailView.as_view(),
        name="custom-transform-detail",
    ),
    url(
        r"^library-pack/$",
        LibraryPackListView.as_view(),
        name="library-pack-list",
    ),
    url(
        r"^library-pack/(?P<uuid>[^/]+)/$",
        LibraryPackDetailView.as_view(),
        name="library-pack-detail",
    ),
]
