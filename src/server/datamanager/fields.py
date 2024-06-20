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

import re
from functools import reduce

from celery.result import AsyncResult
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from datamanager.models import Capture, Label, Project, Team, Segmenter

uuid_match = re.compile(
    r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"
)


class CurrentProjectDefault(object):
    def set_context(self, serializer_field):
        try:
            self.project = Project.objects.with_user(
                serializer_field.context["request"].user
            ).get(
                uuid=serializer_field.context["request"].parser_context["kwargs"][
                    "project_uuid"
                ]
            )
        except ObjectDoesNotExist:
            raise ValidationError("Project does not exist.")

    def __call__(self):
        return self.project

    def __repr__(self):
        return str(self.__class__.__name__)


class CurrentSegmenterDefault(object):
    def set_context(self, serializer_field):
        try:
            self.segmenter = Segmenter.objects.get(
                pk=serializer_field.context["request"].parser_context["kwargs"][
                    "segmenter_pk"
                ],
                project__uuid=serializer_field.context["request"].parser_context[
                    "kwargs"
                ]["project_uuid"],
            )
        except ObjectDoesNotExist:
            raise ValidationError("Segmenter does not exist.")

    def __call__(self):
        return self.segmenter

    def __repr__(self):
        return str(self.__class__.__name__)


class CurrentlabelDefault(object):
    def set_context(self, serializer_field):
        try:
            self.label = Label.objects.get(
                uuid=serializer_field.context["request"].parser_context["kwargs"][
                    "label_uuid"
                ]
            )
        except ObjectDoesNotExist:
            raise ValidationError("Label Does not Exist.")

    def __call__(self):
        return self.label

    def __repr__(self):
        return str(self.__class__.__name__)


class CurrentCaptureDefault(object):
    def set_context(self, serializer_field):
        try:
            self.capture = Capture.objects.with_user(
                serializer_field.context["request"].user
            ).get(
                uuid=serializer_field.context["request"].parser_context["kwargs"][
                    "capture_uuid"
                ],
                project__uuid=serializer_field.context["request"].parser_context[
                    "kwargs"
                ]["project_uuid"],
            )
        except ObjectDoesNotExist:
            raise ValidationError("Capture Does not Exist.")

    def __call__(self):
        return self.capture

    def __repr__(self):
        return str(self.__class__.__name__)


class CurrentCapturePkDefault(CurrentCaptureDefault):
    """
    Return Capture PK instead of Capture instance for use specifically with CaptureSampleSerializer
    """

    def __call__(self):
        return self.capture.pk


class CurrentTeamDefault(object):
    def set_context(self, serializer_field):
        self.team = reduce(
            lambda x, y: getattr(x, y, None),
            ["user", "teammember", "team"],
            serializer_field.context.get("request"),
        )

    def __call__(self):
        return self.team

    def __repr__(self):
        return str(self.__class__.__name__)


class TeamSlugRelatedField(serializers.SlugRelatedField):
    """
    SlugRelatedField but will create Team if it doesn't exist
    """

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            # self.fail('does_not_exist', slug_name=self.slug_field, value=smart_text(data))
            return Team(**{self.slug_field: data})
        except (TypeError, ValueError):
            self.fail("invalid")


class SegmenterPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Limits to only selecting segmenters in the same project"""

    def get_queryset(self):
        return self.queryset.filter(
            project__uuid=self.context["request"].parser_context["kwargs"][
                "project_uuid"
            ]
        )


class AsyncTaskState(serializers.ReadOnlyField):
    """String representation of celery task state.

    Model must have `task` field containing task uuid
    """

    def get_attribute(self, o):
        return o

    def to_representation(self, o):
        if uuid_match.match(str(o.task)):
            status = AsyncResult(str(o.task)).status
            # PENDING doesnt guarantee task even exists so just say none
            if status == "PENDING":
                return None
            else:
                return status
        else:
            return o.task


class AsyncTaskResult(serializers.ReadOnlyField):
    """String representation of celery task result.

    Model must have `task` field containing task uuid
    """

    def get_attribute(self, o):
        return o

    def to_representation(self, o):

        if o.task in ["SUCCESS", None]:
            return None

        elif o.task == "FAILURE":
            return o.task_result or None

        elif uuid_match.match(str(o.task)):
            res = AsyncResult(str(o.task)).result
            if res:
                return str(res)

        if not hasattr(o, "task_result"):
            return None

        return o.task_result
