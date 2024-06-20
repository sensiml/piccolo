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

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from logger.models import Application, Log, LogLevel, Tag

logger = logging.getLogger(__name__)


class LogSerializer(serializers.ModelSerializer):
    tag = serializers.CharField(default="")
    application = serializers.CharField(default="")
    loglevel = serializers.CharField(default="")

    def validate_application(self, value):
        try:
            application = Application.objects.get(name=value)
        except ObjectDoesNotExist:
            application = Application.objects.get(name="INVALID")

        return application

    def validate_loglevel(self, value):
        try:
            loglevel = LogLevel.objects.get(name=value)
        except ObjectDoesNotExist:
            loglevel = Application.objects.get(name="INVALID")

        return loglevel

    def validate_tag(self, value):
        if value is None:
            return value

        tag_strings = value.split(",")
        tags = Tag.objects.filter(name__in=tag_strings)

        if len(tags) != len(tag_strings):
            for tag in tag_strings:
                try:
                    tags.get(name=tag)
                except ObjectDoesNotExist:
                    Tag(name=tag).save()

            tags = Tag.objects.filter(name__in=tag_strings)

        return tags

    def validate_client_information(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        return value

    def create(self, validated_data):

        log_data = {
            "log_type": "client_logs",
            "loglevel": validated_data["loglevel"].name,
            "username": validated_data["username"],
            "application": validated_data["application"].name,
            "message": validated_data["message"],
            "stacktrace": validated_data["stacktrace"],
            "tag": [tag.name for tag in validated_data["tag"]],
            "client_information": validated_data["client_information"],
        }

        logger.info(json.dumps(log_data))

        return super(LogSerializer, self).create(validated_data)

    class Meta:
        model = Log
        fields = (
            "loglevel",
            "application",
            "message",
            "stacktrace",
            "username",
            "tag",
            "client_information",
        )
