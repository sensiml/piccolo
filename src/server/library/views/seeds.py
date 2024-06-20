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
from library.models import PipelineSeed
from library.serializers.serializers import PipelineSeedSerializer
from rest_framework import generics
from rest_framework.exceptions import ValidationError


@extend_schema_view(
    get=extend_schema(exclude=True),
)
class ValidationErrorListView(generics.ListAPIView):
    queryset = None
    serializer_class = None

    def list(self, request, *args, **kwargs):
        raise ValidationError(
            "\n\n######################################\n\n\n\n\nSensiML Python SDK is out of date. Update your sensiml package to connect to SensiML Cloud.\n\n\n\n\n############################\n\n\n"
        )


@extend_schema_view(
    get=extend_schema(exclude=True),
)
class PipelineSeedListView(generics.ListAPIView):
    queryset = PipelineSeed.objects.all()
    serializer_class = PipelineSeedSerializer


@extend_schema_view(
    get=extend_schema(exclude=True),
)
class PipelineSeedDetailView(generics.RetrieveAPIView):
    queryset = PipelineSeed.objects.all()
    serializer_class = PipelineSeedSerializer
    lookup_field = "pk"


urlpatterns = [
    url(r"^seed/$", ValidationErrorListView.as_view(), name="seed-list"),
    url(r"^seed/v2/$", PipelineSeedListView.as_view(), name="seed-list"),
    url(r"^seed/(?P<pk>[^/]+)/$", PipelineSeedDetailView.as_view(), name="seed-detail"),
]
