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

import logging

from django.conf import settings
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from logger.log_handler import LogHandler
from redis import StrictRedis
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.views import APIView

logger = LogHandler(logging.getLogger(__name__))


@extend_schema_view(
    get=extend_schema(summary="Check the health of the server", tags=["Reporting"]),
)
class HealthView(APIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):

        # Check redis status
        try:
            r = StrictRedis(settings.REDIS_ADDRESS)
            r.get("__health__")
            redis = "up"
        except Exception as e:
            logger.error({"message": e, "log_type": "datamanager"})
            redis = "down"

        return Response(
            {
                "server": "up",  # If we can display this page the server is up
                "redis": redis,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    get=extend_schema(summary="Get the current server version", tags=["Reporting"]),
)
class VersionView(APIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        from server import __version__

        ret = {"Piccollo Engine": __version__}

        return Response(ret)


urlpatterns = format_suffix_patterns(
    [
        url(r"^health/$", HealthView.as_view(), name="health"),
        url(r"^version/$", VersionView.as_view(), name="version"),
    ]
)
