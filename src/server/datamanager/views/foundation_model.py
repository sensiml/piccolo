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

from datamanager.models import FoundationModel
from datamanager.serializers import FoundationModelSerializer
from django.urls import re_path as url
from rest_framework import generics, permissions
from rest_framework.urlpatterns import format_suffix_patterns


class FoundationModelListView(generics.ListAPIView):
    queryset = FoundationModel.objects.all()
    serializer_class = FoundationModelSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^foundation-model/$",
            FoundationModelListView.as_view(),
            name="foundation-model-list",
        ),
    ]
)
