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

import inspect
import logging
import re
import sys
from uuid import uuid4

from datamanager import models
from datamanager.fields import (
    CurrentlabelDefault,
    CurrentProjectDefault,
    CurrentTeamDefault,
    SegmenterPrimaryKeyRelatedField,
)
from datamanager.models import (
    Capture,
    CaptureConfiguration,
    FeatureFile,
    FoundationModel,
    Label,
    LabelValue,
    Project,
    Segmenter,
    Team,
)
from datamanager.serializers.mixin_dynamic_fields import DynamicFieldsMixin
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone
from logger.log_handler import LogHandler
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from rest_framework.fields import CreateOnlyDefault  # NOQA # isort:skip


logger = LogHandler(logging.getLogger(__name__))


reserved_words = ["_Capture_", "_GroupRows_"]


class ModelObjectUUIDField(serializers.Field):
    """
    We use this when we are doing bulk create/update. Since multiple instances share
    many of the same fk objects we validate and query the objects first, then modify the request data
    with the fk objects. This allows us to pass the objects in to be validated.
    """

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class AtomicCreateListSerializer(serializers.ListSerializer):
    @transaction.atomic
    def create(self, validated_data):
        return [self.child.create(attrs) for attrs in validated_data]

    @transaction.atomic
    def update(self, instances, validated_data):
        instances_hash = {instance.uuid: instance for instance in instances}

        result = [
            self.child.update(instances_hash[attrs["uuid"]], attrs)
            for attrs in validated_data
        ]
        return result


def bulk_update_capture_last_modified(instances):
    if not instances:
        return

    if hasattr(instances[0], "capture"):
        captures = {instance.capture for instance in instances}

    else:
        captures = instances

    last_modified = timezone.now()

    for capture in captures:
        capture.last_modified = last_modified
        capture.version = F("version") + 1

    Capture.objects.bulk_update(captures, ["last_modified", "version"])


class BulkAtomicCreateUpdateListSerializer(serializers.ListSerializer):
    @transaction.atomic
    def create(self, validated_data):
        if not hasattr(validated_data, "__iter__"):
            validated_data = [validated_data]

        result = [self.child.create(attrs) for attrs in validated_data]

        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)

        bulk_update_capture_last_modified(result)

        return result

    @transaction.atomic
    def update(self, instances, validated_data):
        if not hasattr(instances, "__iter__"):
            instances = [instances]

        instances_hash = {instance.uuid: instance for instance in instances}
        result = [
            self.child.update(instances_hash[attrs["uuid"]], attrs)
            for attrs in validated_data
            if attrs["uuid"] in instances_hash
        ]

        writable_fields = [
            x
            for x in self.child.Meta.fields
            if x not in self.child.Meta.read_only_fields
        ]

        # bulk update doesn't modify auto_now fields in django
        if "last_modified" in self.child.Meta.fields:
            writable_fields += ["last_modified"]
            last_modified = timezone.now()
            for instance in result:
                instance.last_modified = last_modified

        try:
            self.child.Meta.model.objects.bulk_update(result, writable_fields)
        except IntegrityError as e:
            raise ValidationError(e)

        bulk_update_capture_last_modified(result)

        return result


def validate_label_value(value):
    if value is None:
        return value

    value = str(value)

    if not re.match("^[a-zA-Z0-9_ .:-]*$", value):
        raise serializers.ValidationError(
            'Value "{}" can only contain letters, numbers and underscores.'.format(
                value
            )
        )

    if len(value) > 64:
        raise serializers.ValidationError(
            'Value "{}" must be less than 64 characters.'.format(value)
        )

    if value.upper() in reserved_words:
        raise serializers.ValidationError(
            'Value "{}" is a reserved word.'.format(value)
        )

    return value


def validate_label_name(value):
    if value is None:
        return value

    value = str(value)

    if not re.match("^[a-zA-Z0-9_ ]*$", value):
        raise serializers.ValidationError(
            'Value "{}" can only contain letters, numbers and underscores.'.format(
                value
            )
        )

    if len(value) > 64:
        raise serializers.ValidationError(
            'Value "{}" must be less than 64 characters.'.format(value)
        )

    if value in reserved_words:
        raise serializers.ValidationError(
            'Value "{}" is a reserved word.'.format(value)
        )

    return value


class ProjectSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(
        default=CreateOnlyDefault(uuid4), read_only=True
    )  # validators=[UniqueValidator(queryset=Project.objects.all())])
    name = serializers.CharField()
    team = serializers.SlugRelatedField(
        queryset=Team.objects.all(), slug_field="name", default=CurrentTeamDefault()
    )
    settings = serializers.JSONField(allow_null=True, default=None)
    url = serializers.HyperlinkedIdentityField(
        view_name="project-detail", lookup_field="uuid"
    )
    captures = serializers.SerializerMethodField(read_only=True)
    labels = serializers.SerializerMethodField(read_only=True)
    segmenters = serializers.SerializerMethodField(read_only=True)
    optimized = serializers.BooleanField(default=False)
    plugin_config = serializers.JSONField(allow_null=True, default=None)
    active_pipelines = serializers.JSONField(
        allow_null=True, default=None, read_only=True
    )

    def get_captures(self, o):
        return reverse(
            "capture-list",
            kwargs={"project_uuid": o.uuid},
            request=self.context.get("request"),
            format=self.context.get("format"),
        )

    def get_labels(self, o):
        return reverse(
            "label-list",
            kwargs={"project_uuid": o.uuid, "label_or_metadata": "label"},
            request=self.context.get("request"),
            format=self.context.get("format"),
        )

    def get_segmenters(self, o):
        return reverse(
            "segmenter-list",
            kwargs={"project_uuid": o.uuid},
            request=self.context.get("request"),
            format=self.context.get("format"),
        )

    def validate_settings(self, value):
        """Ensure settings is a dictionary or NoneType."""
        if value is None:
            return value
        if type(value) is not dict:
            raise serializers.ValidationError("Settings must be a dictionary object.")
        return value

    def validate_name(self, value):
        if not re.match("^[a-zA-Z0-9_ .-]*$", value):
            raise serializers.ValidationError(
                'Value "{}" can only contain letters, numbers and underscores and spaces.'.format(
                    value
                )
            )
        return value

    def create(self, validated_data):
        validated_data["description"] = settings.NEW_PROJECT_DESCRIPTION

        return super(ProjectSerializer, self).create(validated_data)

    class Meta:
        model = Project
        fields = (
            "uuid",
            "url",
            "name",
            "labels",
            "capture_sample_schema",
            "captures",
            "team",
            "settings",
            "optimized",
            "segmenters",
            "profile",
            "plugin_config",
            "created_at",
            "active_pipelines",
            "description",
            "lock_schema",
            "last_modified",
        )
        read_only_fields = (
            "uuid",
            "active_pipelines",
            "team",
            "created_at",
            "optimized",
            "profile",
            "plugin_config",
            "capture_sample_schema",
            "last_modified",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Project.objects.all(), fields=("team", "name")
            )
        ]


class LabelValueDetailSerializer(serializers.ModelSerializer):
    value = serializers.CharField(required=True, allow_null=False)
    label = serializers.HiddenField(default=CurrentlabelDefault())

    def validate_value(self, value):
        return validate_label_value(value)

    def validate_color(self, value):
        if value is None:
            return value

        if not re.match("^#([0-9a-fA-F]{6}|[A-Fa-f0-9]{8})$", value):
            raise serializers.ValidationError(
                '"{}" is not a valid color.'.format(value)
            )
        return value

    class Meta:
        model = LabelValue
        read_only_fields = ("uuid", "label", "created_at", "last_modified")
        fields = ("uuid", "value", "label", "created_at", "last_modified", "color")


class LabelValueSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    @staticmethod
    def is_num(value):
        return re.match(r"^[0-9.\-+e]+$", value)

    def get_value(self, o):
        return str(o.value)

    def validate_value(self, value):
        validate_label_value(value)

    def validate_color(self, value):
        if value is None:
            return value

        if not re.match("^#([0-9a-fA-F]{6}|[A-Fa-f0-9]{8})$", value):
            raise serializers.ValidationError(
                '"{}" is not a valid color.'.format(value)
            )
        return value

    class Meta:
        model = LabelValue
        read_only_fields = ("uuid", "created_at", "last_modiied")
        fields = ("value", "color", "uuid", "created_at", "last_modified")


class LabelSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=["string", "integer", "float"])
    label_values = LabelValueSerializer(many=True, default=[])
    values = serializers.ListField(write_only=True, default=[])
    project = serializers.HiddenField(default=CurrentProjectDefault())
    metadata = serializers.BooleanField()

    def validate_name(self, value):
        return validate_label_name(value)

    def create(self, data):
        label_values = data.pop("label_values")
        values = data.pop("values")
        data["metadata"] = self.get_metadata(None)
        data["name"] = validate_label_value(data["name"])
        label = Label.objects.create(**data)

        for value in label_values:
            value = validate_label_value(value)
            LabelValue.objects.create(label=label, **value)
        for value in values:
            value = validate_label_value(value)
            LabelValue.objects.create(label=label, value=value)

        return label

    def update(self, instance, valid_data):
        instance.name = valid_data["name"]
        instance.is_dropdown = valid_data["is_dropdown"]
        instance.type = valid_data["type"]

        instance.save()

        return instance

    def get_url(self, o):
        if self.context.get("request"):
            label_or_metadata = self.context["request"].parser_context["kwargs"][
                "label_or_metadata"
            ]
        else:
            label_or_metadata = "label"
        return reverse(
            "label-detail",
            kwargs={
                "project_uuid": self.context["request"].parser_context["kwargs"][
                    "project_uuid"
                ],
                "label_or_metadata": label_or_metadata,
                "uuid": o.uuid,
            },
            request=self.context.get("request"),
            format=self.context.get("format"),
        )

    def get_metadata(self, o):
        if self.context.get("request"):
            return (
                True
                if self.context["request"].parser_context["kwargs"]["label_or_metadata"]
                == "metadata"
                else False
            )

        return False

    class Meta:
        model = Label
        read_only_fields = ("uuid", "created_at", "last_modiied")
        fields = (
            "name",
            "project",
            "uuid",
            "type",
            "values",
            "label_values",
            "metadata",
            "is_dropdown",
            "created_at",
            "last_modified",
        )


class SegmenterSerializer(serializers.ModelSerializer):
    project = serializers.HiddenField(default=CurrentProjectDefault())
    parent = SegmenterPrimaryKeyRelatedField(
        queryset=Segmenter.objects.all(), allow_null=True, default=None
    )

    class Meta:
        model = Segmenter
        fields = "__all__"


class ProjectSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    uuid = serializers.CharField()
    name = serializers.CharField()
    created_at = serializers.DateTimeField()
    files = serializers.IntegerField()
    size_mb = serializers.FloatField()
    pipelines = serializers.IntegerField()
    queries = serializers.IntegerField()
    models = serializers.IntegerField()
    videos = serializers.IntegerField()
    video_size_mb = serializers.FloatField()
    segments = serializers.IntegerField()
    description = serializers.CharField()


class ProjectActivePipelineSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(default=CreateOnlyDefault(uuid4), read_only=True)
    active_pipelines = serializers.JSONField(
        allow_null=True, default=None, read_only=True
    )

    class Meta:
        model = Project
        fields = ("uuid", "active_pipelines")
        read_only_fields = ("uuid", "active_pipelines")
        lookup_field = "uuid"


class TeamProjectSerializer(ProjectSerializer):
    team = serializers.SlugRelatedField(
        queryset=CurrentTeamDefault(), default=CurrentTeamDefault(), slug_field="name"
    )


class GroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        read_only=True, validators=[UniqueValidator(queryset=Group.objects.all())]
    )

    class Meta:
        model = Group
        fields = ("name",)


class SandboxConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sandbox
        read_only_fields = ("uuid", "device_config")
        fields = ("uuid", "device_config")


class SandboxSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for Sandbox objects"""

    def get_url(self, o):
        return reverse(
            "sandbox-detail",
            kwargs={
                "project_uuid": self.context["request"].parser_context["kwargs"][
                    "project_uuid"
                ],
                "uuid": o.uuid,
            },
            request=self.context.get("request"),
            format=self.context.get("format"),
        )

    class Meta:
        model = models.Sandbox
        fields = (
            "uuid",
            "name",
            "project",
            "created_at",
            "last_modified",
            "cpu_clock_time",
            "active",
            "pipeline",
            "cache_enabled",
            "cache",
            "device_config",
            "hyper_params",
            "result_type",
        )
        read_only_fields = (
            "uuid",
            "project",
            "name",
            "created_at",
            "last_modified",
            "cpu_clock_time",
            "active",
            "cache",
            "result_type",
        )
        # exclude = ("id", "project", "users", "private")
        # fields = ('name', 'uuid', 'pipeline', 'cache_enabled', 'device_config', 'url')


class FoundationModelSerializer(serializers.ModelSerializer):
    """Foundation Model Serializer"""

    features_count = serializers.SerializerMethodField()
    model_size = serializers.SerializerMethodField()

    class Meta:
        model = FoundationModel
        read_only_fields = (
            "uuid",
            "name",
            "features_count",
            "model_size",
            "created_at",
            "knowledgepack_description",
            "last_modified",
        )

        fields = (
            "uuid",
            "name",
            "features_count",
            "model_size",
            "created_at",
            "knowledgepack_description",
            "last_modified",
        )

    def get_features_count(self, obj):
        return len(obj.feature_summary) if obj.feature_summary is not None else 0

    def get_model_size(self, obj):
        return obj.model_results.get("model_size", None)


class FeatureFileSerializer(serializers.ModelSerializer):
    """FeatureFile Serializer"""

    class Meta:
        model = FeatureFile
        read_only_fields = ("uuid",)
        exclude = ("id", "path")


class CaptureConfigurationSerializer(serializers.ModelSerializer):
    project = serializers.HiddenField(default=CurrentProjectDefault())

    def validate_version_1_configuration(self, configuration):
        """TODO: Implement Configuration validation (currently done by DCL)"""
        return configuration

    def validate_version_2_configuration(self, configuration):
        """TODO: Implement Configuration validation (currently done by DCL)"""
        return configuration

    def migrate_version_1_to_2(self, configuration):
        """Version 1 has no version number, version 2 adds the required bytes field"""
        for capture_source in configuration["capture_sources"]:
            for sensor in capture_source["sensors"]:
                for parameter in sensor["parameters"]:
                    parameter["num_bytes"] = 1

        configuration["version"] = 2

        return configuration

    def validate_configuration(self, configuration):
        if configuration.get("version", 1) == 1:
            self.validate_version_1_configuration(configuration)
            configuration = self.migrate_version_1_to_2(configuration)

        if configuration.get("vesion", 2) == 2:
            self.validate_version_2_configuration(configuration)

        return configuration

    def create(self, validated_data):
        self.context["request"]

        capture_configuration = CaptureConfiguration(**validated_data)

        capture_configuration.save()

        return capture_configuration

    class Meta:
        model = models.CaptureConfiguration
        read_only_fields = ("project", "created_at", "version")
        fields = (
            "project",
            "uuid",
            "name",
            "configuration",
            "created_at",
            "last_modified",
        )


class CaptureConfigurationDetailSerializer(CaptureConfigurationSerializer):
    class Meta:
        model = models.CaptureConfiguration
        read_only_fields = ("uuid", "project", "created_at")
        fields = (
            "project",
            "uuid",
            "name",
            "configuration",
            "created_at",
            "last_modified",
        )


# Only export classes by default
__all__ = [cls[0] for cls in inspect.getmembers(sys.modules[__name__], inspect.isclass)]
