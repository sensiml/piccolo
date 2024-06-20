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

from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from library.models import PlatformDescriptionVersion2
from library.serializers.serializers import (
    PlatformDescriptionVersion2Serializer,
)
from rest_framework import generics


@extend_schema_view(
    get=extend_schema(
        summary="List Supported Platforms",
        description="Returns a list of information about currently supported platforms",
    ),
)
class PlatformDescriptionVersion2ListView(generics.ListAPIView):
    queryset = PlatformDescriptionVersion2.objects.filter(permissions__enterprise=True)
    serializer_class = PlatformDescriptionVersion2Serializer


@extend_schema_view(
    get=extend_schema(
        summary="Get Supported Platforms by UUID",
        description="Returns a detailed information about a specific platforms",
    ),
)
class PlatformDescriptionVersion2DetailView(generics.RetrieveAPIView):
    queryset = PlatformDescriptionVersion2.objects.all()
    serializer_class = PlatformDescriptionVersion2Serializer
    lookup_field = "uuid"


urlpatterns = [
    url(
        r"^platforms/v2$",
        PlatformDescriptionVersion2ListView.as_view(),
        name="platform2-list",
    ),
    url(
        r"^platforms/v2/(?P<uuid>[^/]+)/$",
        PlatformDescriptionVersion2DetailView.as_view(),
        name="platform2-detail",
    ),
]
