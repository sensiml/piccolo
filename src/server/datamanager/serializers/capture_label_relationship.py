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

from datamanager.fields import (
    CurrentCaptureDefault,
    CurrentProjectDefault,
    SegmenterPrimaryKeyRelatedField,
)
from datamanager.models import (
    CaptureLabelValue,
    Label,
    LabelValue,
    Segmenter,
)
from datamanager.serializers.serializers import (
    BulkAtomicCreateUpdateListSerializer,
    LabelValueSerializer,
    ModelObjectUUIDField,
    validate_label_name,
    validate_label_value,
)
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class V1CaptureLabelValueSerializer(serializers.ModelSerializer):
    class LabelValueField(serializers.Field):
        def get_attribute(self, obj):
            return obj.label_value

        def to_representation(self, obj):
            try:
                return LabelValueSerializer(obj).data.get("value")
            except ValueError:
                return "NaN"

        def to_internal_value(self, data):
            return str(data)

    capture = serializers.HiddenField(default=CurrentCaptureDefault())
    project = serializers.HiddenField(default=CurrentProjectDefault())
    segmenter = SegmenterPrimaryKeyRelatedField(
        required=False, allow_null=True, queryset=Segmenter.objects.all()
    )
    name = serializers.CharField(source="label.name")
    type = serializers.ChoiceField(
        source="label.type", choices=["string", "integer", "float"]
    )
    value = LabelValueField(source="label_value.value")
    capture_sample_sequence_start = serializers.IntegerField(default=0)
    capture_sample_sequence_end = serializers.IntegerField(default=0)

    def validate_name(self, value):
        """Ensure label name is not a reserved string."""
        value = validate_label_name(value)

        return value

    def update(self, instance, validated_data):
        label = validated_data.pop("label", None)
        if label:
            value_type = label.get("type", None)
            name = label.get("name", None)
            if name:
                name = validate_label_name(name)

        value = validated_data.pop("label_value", {}).get("value", None)

        if label:
            try:
                instance.label = Label.objects.get_or_create(
                    project=instance.project, name=name, type=value_type, metadata=False
                )[0]
            except IntegrityError as e:
                # TODO
                # if there is only one associated with the label.type we update the label_type
                if value_type != instance.label.type:
                    raise ValidationError(
                        'Expected value type of "{}" for "{}", instead received value type "{}"'.format(
                            instance.label.type, name, value_type
                        )
                    )
                raise ValidationError(e.message)

        if value:
            value = validate_label_value(value)
            instance.label_value = LabelValue.objects.get_or_create(
                value=value, label=instance.label
            )[0]

        instance.capture_sample_sequence_start = validated_data.get(
            "capture_sample_sequence_start", instance.capture_sample_sequence_start
        )

        instance.capture_sample_sequence_end = validated_data.get(
            "capture_sample_sequence_end", instance.capture_sample_sequence_end
        )

        instance.segmenter = validated_data.get("segmenter")

        instance.save()

        return instance

    def create(self, validated_data):
        self.context["request"].parser_context["kwargs"]
        value = validated_data["label_value"]["value"]
        name = validated_data["label"]["name"]
        value_type = validated_data["label"]["type"]
        project = validated_data["project"]
        capture = validated_data["capture"]

        try:
            label = Label.objects.get(project=project, name=name, metadata=False)
            if value_type != label.type:
                raise ValidationError(
                    'Values for label "{}" must be of type {}'.format(
                        label.name, label.type
                    )
                )
            if label.metadata:
                raise ValidationError("Attempting to add a label as metadata.")
        except Label.DoesNotExist:
            try:
                label = Label.objects.create(
                    project=project, name=name, type=value_type, metadata=False
                )
            except IntegrityError as e:
                raise ValidationError(e)
        except KeyError as e:
            raise ValidationError(e)
        try:
            label_value, created = LabelValue.objects.get_or_create(
                label=label, value=value
            )
        except ValueError:
            raise ValidationError("{} already exists".format(value))
        except IntegrityError as e:
            raise ValidationError(e)

        data_begin = validated_data.get("capture_sample_sequence_start")
        data_end = validated_data.get("capture_sample_sequence_end")

        if not data_begin and not data_end:
            raise ValidationError("Invalida capture_sample_sequence.")

        relationship = CaptureLabelValue(
            project=project,
            capture=capture,
            label=label,
            label_value=label_value,
            capture_sample_sequence_start=data_begin,
            capture_sample_sequence_end=data_end,
            segmenter=validated_data.get("segmenter"),
        )

        try:
            relationship.save()
        except IntegrityError as e:
            raise ValidationError(e)

        return relationship

    class Meta:
        model = CaptureLabelValue
        fields = (
            "uuid",
            "name",
            "value",
            "type",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "segmenter",
            "capture",
            "project",
            "created_at",
            "last_modified",
        )
        read_only_fields = ("uuid", "created_at", "last_modiied")
        validators = []


class V2CaptureLabelValueSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(default=None, allow_null=True)
    capture = serializers.HiddenField(default=CurrentCaptureDefault())
    project = serializers.HiddenField(default=CurrentProjectDefault())
    segmenter = SegmenterPrimaryKeyRelatedField(
        required=False, allow_null=True, queryset=Segmenter.objects.all()
    )
    label = serializers.ModelField(model_field=Label()._meta.get_field("uuid"))
    # label = serializers.UUIDField(allow_null=True)
    label_value = serializers.ModelField(
        model_field=LabelValue()._meta.get_field("uuid")
    )

    capture_sample_sequence_start = serializers.IntegerField(default=0)
    capture_sample_sequence_end = serializers.IntegerField(default=0)

    def validate(self, data):
        if data["capture_sample_sequence_start"] < 0:
            raise ValidationError(
                "Capture sample sequence start cannot be less than 0."
            )

        if data["capture_sample_sequence_end"] <= data["capture_sample_sequence_start"]:
            raise ValidationError(
                "Capture sample sequence end cannot be less than start."
            )

        # TODO: Make sure capture number samples is always filled in
        if (
            data.get("capture", None)
            and data["capture"].max_sequence is not None
            and data["capture_sample_sequence_end"] > data["capture"].max_sequence
        ):
            raise ValidationError(
                "Capture sample sequence end cannot be greater than the max sequence of the capture file."
            )

        return data

    def validate_label(self, label):
        kwargs = self.context["request"].parser_context["kwargs"]
        project_uuid = kwargs["project_uuid"]
        try:
            db_label = Label.objects.get(uuid=label, project__uuid=project_uuid)
        except Label.DoesNotExist as e:
            raise ValidationError(e)
        return db_label

    def validate_label_value(self, label_value):
        request = self.context["request"]
        if isinstance(request.data, list):
            label = [
                x["label"] for x in request.data if x["label_value"] == str(label_value)
            ][0]
        else:
            label = request.data["label"]

        try:
            db_label_v = LabelValue.objects.get(uuid=label_value, label__uuid=label)
        except LabelValue.DoesNotExist as e:
            raise ValidationError(e)
        return db_label_v

    def to_representation(self, instance):
        label_uuid = None
        segment_id = None
        label_value_uuid = None

        if instance is not None:
            label_uuid = instance.uuid
            segment_id = None if instance.segmenter is None else instance.segmenter.id
            label_value_uuid = instance.label_value.uuid

        ext_repr = dict(
            uuid=label_uuid,
            capture=instance.capture.uuid,
            label=instance.label.uuid,
            label_value=label_value_uuid,
            capture_sample_sequence_start=instance.capture_sample_sequence_start,
            capture_sample_sequence_end=instance.capture_sample_sequence_end,
            segmenter=segment_id,
            created_at=instance.created_at,
            last_modified=instance.last_modified,
        )
        return ext_repr

    def update(self, instance, validated_data):
        label = validated_data["label"]
        value = validated_data["label_value"]

        instance.label = label
        instance.label_value = value

        instance.capture_sample_sequence_start = validated_data.get(
            "capture_sample_sequence_start", instance.capture_sample_sequence_start
        )
        instance.capture_sample_sequence_end = validated_data.get(
            "capture_sample_sequence_end", instance.capture_sample_sequence_end
        )

        instance.segmenter = validated_data.get("segmenter")

        if isinstance(self._kwargs["data"], dict):
            try:
                instance.save()
            except IntegrityError:
                raise ValidationError()

        return instance

    def create(self, validated_data):
        label = validated_data["label"]
        label_value = validated_data["label_value"]
        capture = validated_data["capture"]
        project = validated_data["project"]
        data_begin = validated_data.get("capture_sample_sequence_start")
        data_end = validated_data.get("capture_sample_sequence_end")

        instance = CaptureLabelValue(
            project=project,
            capture=capture,
            label=label,
            label_value=label_value,
            capture_sample_sequence_start=data_begin,
            capture_sample_sequence_end=data_end,
            segmenter=validated_data.get("segmenter"),
        )

        if isinstance(self._kwargs["data"], dict):
            try:
                instance.save()
            except IntegrityError:
                raise ValidationError()

        return instance

    class Meta:
        model = CaptureLabelValue
        fields = (
            "uuid",
            "label",
            "label_value",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "segmenter",
            "capture",
            "project",
            "created_at",
            "last_modified",
        )
        read_only_fields = ("uuid", "created_at", "last_modiied")
        validators = []
        list_serializer_class = BulkAtomicCreateUpdateListSerializer


class V2ProjectCaptureLabelValueSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(default=None, allow_null=True)
    project = ModelObjectUUIDField()
    segmenter = ModelObjectUUIDField()
    capture = ModelObjectUUIDField()
    label = ModelObjectUUIDField()
    label_value = ModelObjectUUIDField()

    capture_sample_sequence_start = serializers.IntegerField(default=0)
    capture_sample_sequence_end = serializers.IntegerField(default=0)

    def validate(self, data):
        if data["capture_sample_sequence_start"] < 0:
            raise ValidationError(
                "Capture sample sequence start cannot be less than 0."
            )

        if data["capture_sample_sequence_end"] <= data["capture_sample_sequence_start"]:
            raise ValidationError(
                "Capture sample sequence end cannot be less than start."
            )

        # TODO: Make sure capture number samples is always filled in
        if (
            data.get("capture", None)
            and data["capture"].max_sequence is not None
            and data["capture_sample_sequence_end"] > data["capture"].max_sequence
        ):
            raise ValidationError(
                "Capture sample sequence end cannot be greater than the max sequence of the capture file."
            )

        return data

    def to_representation(self, instance):
        label_uuid = None
        label_value_uuid = None

        if instance is not None:
            label_uuid = instance.uuid
            None if instance.segmenter is None else instance.segmenter.id
            label_value_uuid = instance.label_value.uuid

        ext_repr = dict(
            uuid=label_uuid,
            capture=instance.capture.uuid,
            label=instance.label.uuid,
            label_value=label_value_uuid,
            capture_sample_sequence_start=instance.capture_sample_sequence_start,
            capture_sample_sequence_end=instance.capture_sample_sequence_end,
            segmenter=instance.segmenter.id,
            created_at=instance.created_at,
            last_modified=instance.last_modified,
        )

        return ext_repr

    def update(self, instance, validated_data):
        label = validated_data["label"]
        value = validated_data["label_value"]
        capture = validated_data["capture"]

        instance.label = label
        instance.label_value = value
        instance.capture = capture
        instance.capture_sample_sequence_start = validated_data.get(
            "capture_sample_sequence_start", instance.capture_sample_sequence_start
        )
        instance.capture_sample_sequence_end = validated_data.get(
            "capture_sample_sequence_end", instance.capture_sample_sequence_end
        )

        instance.segmenter = validated_data.get("segmenter")

        if isinstance(self._kwargs["data"], dict):
            try:
                instance.save()
            except IntegrityError:
                raise ValidationError()

        return instance

    def create(self, validated_data):
        label = validated_data["label"]
        label_value = validated_data["label_value"]
        capture = validated_data["capture"]
        project = validated_data["project"]
        data_begin = validated_data.get("capture_sample_sequence_start")
        data_end = validated_data.get("capture_sample_sequence_end")

        instance = CaptureLabelValue(
            project=project,
            capture=capture,
            label=label,
            label_value=label_value,
            capture_sample_sequence_start=data_begin,
            capture_sample_sequence_end=data_end,
            segmenter=validated_data.get("segmenter"),
        )

        if isinstance(self._kwargs["data"], dict):
            try:
                instance.save()
            except IntegrityError:
                raise ValidationError()

        return instance

    class Meta:
        model = CaptureLabelValue
        fields = (
            "uuid",
            "label",
            "label_value",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "segmenter",
            "capture",
            "project",
            "created_at",
            "last_modified",
        )
        read_only_fields = ("uuid", "created_at", "last_modiied")
        validators = []
        list_serializer_class = BulkAtomicCreateUpdateListSerializer
