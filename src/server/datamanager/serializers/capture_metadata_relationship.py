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

from datamanager.fields import CurrentCaptureDefault, CurrentProjectDefault
from datamanager.models import (
    CaptureMetadataValue,
    Label,
    LabelValue,
)
from datamanager.serializers.serializers import (
    BulkAtomicCreateUpdateListSerializer,
    ModelObjectUUIDField,
)
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


logger = logging.getLogger(__name__)


class V2CaptureMetadataValueSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(default=None, allow_null=True)
    capture = serializers.HiddenField(default=CurrentCaptureDefault())
    project = serializers.HiddenField(default=CurrentProjectDefault())
    label = serializers.ModelField(model_field=Label()._meta.get_field("uuid"))
    label_value = serializers.ModelField(
        model_field=LabelValue()._meta.get_field("uuid")
    )

    def validate_label(self, label):
        kwargs = self.context["request"].parser_context["kwargs"]

        try:
            db_label = Label.objects.get(
                uuid=label, project__uuid=kwargs["project_uuid"]
            )
        except Label.DoesNotExist as e:
            raise ValidationError(e)
        return db_label

    # TODO: Validate that the label value is associated with the passed in label
    def validate_label_value(self, label_value):
        try:
            db_label_v = LabelValue.objects.get(uuid=label_value)
        except Label.DoesNotExist as e:
            raise ValidationError(e)
        return db_label_v

    def to_representation(self, instance):
        uuid = None
        label_value_uuid = None
        if instance is not None:
            uuid = instance.uuid
            label_value_uuid = instance.label_value.uuid

        ext_repr = dict(
            uuid=uuid,
            capture=self.context["request"].parser_context["kwargs"]["capture_uuid"],
            label=instance.label.uuid,
            label_value=label_value_uuid,
            created_at=instance.created_at,
            last_modified=instance.last_modified,
        )
        return ext_repr

    def update(self, instance, validated_data):
        label = validated_data.get("label", None)
        label_value = validated_data.get("label_value", None)

        if label_value.label != label:
            raise ValidationError("Label value is not associated with this Label")

        instance.label = label
        instance.label_value = label_value

        if isinstance(self._kwargs["data"], dict):
            try:
                instance.save()
            except IntegrityError as e:
                raise ValidationError(e)

        return instance

    def create(self, validated_data):
        label = validated_data["label"]
        label_value = validated_data["label_value"]
        project = validated_data["project"]
        capture = validated_data["capture"]

        relationship = CaptureMetadataValue(
            project=project, capture=capture, label=label, label_value=label_value
        )

        if isinstance(self._kwargs["data"], dict):
            try:
                relationship.save()
            except IntegrityError as e:
                raise ValidationError(e)

        return relationship

    class Meta:
        model = CaptureMetadataValue
        fields = (
            "uuid",
            "label",
            "label_value",
            "capture",
            "project",
            "created_at",
            "last_modified",
        )
        read_only_fields = ("uuid", "created_at", "last_modified")
        list_serializer_class = BulkAtomicCreateUpdateListSerializer
        validators = []


class V2CaptureMetadataRelationshipManySerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(default=None, allow_null=True)
    project = ModelObjectUUIDField()
    capture = ModelObjectUUIDField()
    label = ModelObjectUUIDField()
    label_value = ModelObjectUUIDField()

    def to_representation(self, instance):
        uuid = None
        label_value_uuid = None
        if instance is not None:
            uuid = instance.uuid
            label_value_uuid = instance.label_value.uuid

        ext_repr = dict(
            uuid=uuid,
            capture=instance.capture.uuid,
            label=instance.label.uuid,
            label_value=label_value_uuid,
            created_at=instance.created_at,
            last_modified=instance.last_modified,
        )
        return ext_repr

    def update(self, instance, validated_data):
        label = validated_data.pop("label", None)
        label_value = validated_data.pop("label_value", None)
        capture = validated_data.pop("capture", None)

        if label != label_value.label:
            raise ValidationError("Label is not associated with this Label Value.")

        instance.label = label
        instance.label_value = label_value
        instance.capture = capture

        if isinstance(self._kwargs["data"], dict):
            try:
                instance.save()
            except IntegrityError as e:
                raise ValidationError(e)

        return instance

    def create(self, validated_data):
        label = validated_data["label"]
        label_value = validated_data["label_value"]
        capture = validated_data["capture"]
        project = validated_data["project"]

        if label != label_value.label:
            raise ValidationError("Label is not associated with this Label Value.")

        relationship = CaptureMetadataValue(
            project=project, capture=capture, label=label, label_value=label_value
        )

        if isinstance(self._kwargs["data"], dict):
            try:
                relationship.save()
            except IntegrityError as e:
                raise ValidationError(e)

        return relationship

    class Meta:
        model = CaptureMetadataValue
        fields = (
            "uuid",
            "label",
            "label_value",
            "capture",
            "project",
            "created_at",
            "last_modified",
        )
        read_only_fields = ("uuid", "created_at", "last_modified")
        list_serializer_class = BulkAtomicCreateUpdateListSerializer
        validators = []
