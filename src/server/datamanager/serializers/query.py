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
from collections import OrderedDict
from collections.abc import Mapping

from datamanager.exceptions import QueryFormatError
from datamanager.fields import SegmenterPrimaryKeyRelatedField
from datamanager.models import CaptureConfiguration, Label, Project, Query, Segmenter
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http.request import QueryDict
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_error_detail, set_value

from rest_framework.fields import SkipField  # NOQA # isort:skip


def _check_valid_columns(columns, valid_columns):

    invalid_inputs = [c for c in columns if c not in valid_columns]

    if invalid_inputs:
        raise QueryFormatError(
            "One or more column names not found in project: {}".format(invalid_inputs)
        )

    return json.dumps([c for c in columns if c in valid_columns])


def _get_project(context):
    user = context["request"].user
    project_id = context["request"].parser_context["kwargs"]["project_uuid"]

    return Project.objects.with_user(user).get(uuid=project_id)


def get_project_labels(project):
    """Returns a list of all the unique metadata, eventmetadata, and eventlabel names associated with events."""
    return set([m.name for m in Label.objects.filter(project=project, metadata=False)])


def get_project_schema(project):

    STATIC_PROJECT_SCHEMA_NAMES = ["SequenceID"]

    return list(project.capture_sample_schema.keys()) + STATIC_PROJECT_SCHEMA_NAMES


def get_project_metadata_schema(project):
    STATIC_METADATA_NAMES = ["capture_uuid", "segment_uuid"]

    return set(
        [m.name for m in Label.objects.filter(project=project, metadata=True)]
        + STATIC_METADATA_NAMES
    )


class QuerySerializer(serializers.ModelSerializer):
    metadata_filter = serializers.CharField(required=False, allow_blank=True)
    segmenter_id = SegmenterPrimaryKeyRelatedField(
        required=True, allow_null=False, queryset=Segmenter.objects.all()
    )

    capture_configurations = serializers.CharField(required=False, allow_blank=True)

    def validate_columns(self, value, project=None):

        if project is None:
            return ""

        if not value:
            raise QueryFormatError("Query Columns cannot be Empty.")

        valid_columns = get_project_schema(project)

        return _check_valid_columns(value, valid_columns)

    def validate_metadata_columns(self, value, project=None):
        if project is None:
            return ""

        if not value:
            raise QueryFormatError("Metadata Columns cannot be Empty.")

        valid_columns = get_project_metadata_schema(project)

        return _check_valid_columns(value, valid_columns)

    def validate_label_column(self, value, project=None):

        project = _get_project(self.context)

        valid_columns = get_project_labels(project)

        if value not in valid_columns:
            raise QueryFormatError(
                "Label column not found in project: {}".format(value)
            )

        return value

    def _check_capture_configurations_for_unique_sample_rate(self, configuration_items):
        sample_rate_list = set(
            [
                configuration_item.configuration["capture_sources"][0]["sample_rate"]
                for configuration_item in configuration_items
            ]
        )

        if len(sample_rate_list) > 1:
            return False

        return True

    def validate_capture_configurations(self, value):
        if value in ["", '[""]']:
            return ""
        else:
            project = _get_project(self.context)

            value_validated = [
                i
                for i in CaptureConfiguration.objects.filter(project__uuid=project.uuid)
                if str(i.uuid) in json.loads(value)
            ]

            if self._check_capture_configurations_for_unique_sample_rate(
                value_validated
            ):
                return value_validated
            else:
                error_msg = "The capture configurations selected for this query have different sample rates. A query can only be created from capture configurations with the same sample rate."
                raise ValidationError(error_msg)

    def validate_combine_labels(self, value):
        "We done support this currently."
        return None

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """

        if not isinstance(data, Mapping):
            message = self.error_messages["invalid"].format(
                datatype=type(data).__name__
            )
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="invalid"
            )

        ret = OrderedDict()
        errors = OrderedDict()
        fields = self._writable_fields

        for field in fields:

            validate_method = getattr(self, "validate_" + field.field_name, None)
            primitive_value = field.get_value(data)

            try:
                # these are stored as a string, but come in as a list
                # we will validate them at the end
                if field.field_name in ["metadata_columns", "columns"]:
                    validated_value = primitive_value
                else:
                    validated_value = field.run_validation(primitive_value)

                if validate_method is not None:
                    validated_value = validate_method(validated_value)

            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        project = _get_project(self.context)

        if isinstance(self.initial_data, QueryDict):
            ret["columns"] = self.validate_columns(
                self.initial_data.getlist("columns"), project
            )

            ret["metadata_columns"] = self.validate_metadata_columns(
                self.initial_data.getlist("metadata_columns"), project
            )
        else:
            ret["columns"] = self.validate_columns(
                self.initial_data.get("columns"), project
            )

            ret["metadata_columns"] = self.validate_metadata_columns(
                self.initial_data.get("metadata_columns"), project
            )

        return ret

    def create(self, validated_data):
        validated_data["segmenter"] = validated_data.pop("segmenter_id")
        validated_data["project"] = _get_project(self.context)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["segmenter"] = validated_data.pop("segmenter_id")
        instance.task_status = None
        instance.cache = None
        instance.summary_statistics = None
        instance.segment_info = None
        instance.segment_statistics = None
        return super().update(instance, validated_data)

    def to_representation(self, instance):

        ret = super().to_representation(instance)
        ret["columns"] = json.loads(ret["columns"])
        ret["metadata_columns"] = json.loads(ret["metadata_columns"])
        # following kept for backwards compatibility v2019.3.4 of sensiml client
        ret["created_at"] = ret["created_at"][:24]
        ret["segmenter"] = ret["segmenter_id"]
        ret["capture_configurations"] = [
            str(x.uuid) for x in instance.capture_configurations.all()
        ]

        return ret

    class Meta:
        model = Query
        read_only_fields = (
            "uuid",
            "created_at",
            "last_modiied",
            "cache",
            "task_status",
            "summary_statistics",
        )
        fields = (
            "uuid",
            "name",
            "columns",
            "label_column",
            "metadata_columns",
            "metadata_filter",
            "segmenter_id",
            "combine_labels",
            "created_at",
            "capture_configurations",
            "last_modified",
            "cache",
            "task_status",
            "summary_statistics",
        )
