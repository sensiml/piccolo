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
import json
import logging
import sys

from codegen.model_gen.model_gen import ModelGen
from datamanager.fields import AsyncTaskResult, AsyncTaskState
from datamanager.models import KnowledgePack, Project, Sandbox, Segmenter
from datamanager.serializers.mixin_dynamic_fields import DynamicFieldsMixin

from django.forms.models import model_to_dict
from logger.log_handler import LogHandler
from rest_framework import serializers

logger = LogHandler(logging.getLogger(__name__))


class KnowledgePackDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Knowledge Pack Serializer"""

    feature_file_uuid = serializers.SerializerMethodField()
    sandbox_uuid = serializers.SerializerMethodField()
    sandbox_name = serializers.SerializerMethodField()
    project_uuid = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    neuron_array = serializers.SerializerMethodField()
    model_results = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgePack
        read_only_fields = (
            "uuid",
            "execution_time",
            "model_results",
            "query_summary",
            "feature_summary",
            "device_configuration",
            "configuration_index",
            "model_index",
            "sensor_summary",
            "class_map",
            "sandbox_uuid",
            "sandbox_name",
            "project_uuid",
            "project_name",
            "featurefile_uuid",
        )
        fields = (
            "uuid",
            "execution_time",
            "neuron_array",
            "model_results",
            "pipeline_summary",
            "query_summary",
            "feature_summary",
            "device_configuration",
            "configuration_index",
            "model_index",
            "transform_summary",
            "sensor_summary",
            "class_map",
            "name",
            "sandbox_uuid",
            "sandbox_name",
            "project_uuid",
            "project_name",
            "feature_file_uuid",
            "knowledgepack_summary",
            "knowledgepack_description",
        )

    def get_feature_file_uuid(self, obj):
        if obj.feature_file:
            return obj.feature_file.uuid

        return None

    def get_project_uuid(self, obj):
        return obj.project.uuid

    def get_sandbox_name(self, obj):
        if obj.sandbox:
            return obj.sandbox.name

        return None

    def get_sandbox_uuid(self, obj):
        if obj.sandbox:
            return obj.sandbox.uuid

        return None

    def get_project_name(self, obj):
        return obj.project.name

    def get_model_results(self, obj):
        model_results = obj.model_results
        if not model_results:
            return {}

        if model_results.get("feature_statistics"):
            model_results["feature_statistics"].pop("train", None)
            model_results["feature_statistics"].pop("test", None)
        model_results.pop("debug", None)
        model_results.pop("test_set", None)
        model_results.pop("train_set", None)
        model_results.pop("validation_set", None)
        model_results.pop("classifier_costs", None)

        return model_results

    def get_neuron_array(self, obj):
        neuron_array = obj.neuron_array

        if isinstance(neuron_array, dict):
            if not self.context["request"].query_params.get("tflite"):
                neuron_array.pop("tflite", None)
                neuron_array.pop("tflite_full", None)
                neuron_array.pop("tflite_quant", None)
            neuron_array.pop("model_store", None)

        return neuron_array


class KnowledgePackSimpleDetailSerializer(serializers.ModelSerializer):
    """Knowledge Pack Serializer"""

    sandbox_uuid = serializers.SerializerMethodField()
    sandbox_name = serializers.SerializerMethodField()
    project_uuid = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    accuracy = serializers.SerializerMethodField()
    features_count = serializers.SerializerMethodField()
    classifier_name = serializers.SerializerMethodField()
    model_size = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgePack
        read_only_fields = (
            "uuid",
            "sandbox_uuid",
            "sandbox_name",
            "project_uuid",
            "project_name",
            "accuracy",
            "features_count",
            "classifier_name",
            "model_size",
            "created_at",
            "knowledgepack_description",
            "last_modified",
        )
        fields = (
            "uuid",
            "name",
            "sandbox_uuid",
            "sandbox_name",
            "project_uuid",
            "project_name",
            "accuracy",
            "features_count",
            "classifier_name",
            "model_size",
            "created_at",
            "knowledgepack_description",
            "last_modified",
        )

    def get_project_uuid(self, obj):
        return obj.project.uuid

    def get_sandbox_name(self, obj):
        if obj.sandbox:
            return obj.sandbox.name
        return None

    def get_sandbox_uuid(self, obj):
        if obj.sandbox:
            return obj.sandbox.uuid
        return None

    def get_project_name(self, obj):
        return obj.project.name

    def get_classifier_name(self, obj):
        return (
            obj.device_configuration.get("classifier")
            if obj.device_configuration
            else None
        )

    def get_accuracy(self, obj):
        try:
            return obj.model_results["metrics"]["validation"]["accuracy"]
        except:
            return 0

    def get_features_count(self, obj):
        return len(obj.feature_summary) if obj.feature_summary is not None else 0

    def get_model_size(self, obj):
        if obj.model_results:
            return obj.model_results.get("model_size", None)

        return 0


class KnowledgePackSerializer(serializers.ModelSerializer):
    """Knowledge Pack Serializer"""

    task_state = AsyncTaskState()
    task_result = AsyncTaskResult()

    class Meta:
        model = KnowledgePack
        read_only_fields = ("uuid",)
        fields = (
            "uuid",
            "execution_time",
            "neuron_array",
            "model_results",
            "pipeline_summary",
            "query_summary",
            "feature_summary",
            "device_configuration",
            "configuration_index",
            "model_index",
            "transform_summary",
            "sensor_summary",
            "class_map",
            "knowledgepack_description",
            "cost_summary",
            "task_state",
            "task_result",
            "name",
            "knowledgepack_summary",
        )


class RetrieveKnowledgePackSerializer(serializers.ModelSerializer):
    task_state = AsyncTaskState()
    task_result = AsyncTaskResult()

    class Meta:
        model = KnowledgePack
        fields = ("task_state", "task_result")


class GenerateKnowledgePackSerializerVersion2(serializers.ModelSerializer):
    task_state = AsyncTaskState()
    task_result = AsyncTaskResult()
    asynchronous = serializers.BooleanField(write_only=True, default=True)
    target_platform = serializers.CharField(write_only=True)
    application = serializers.CharField(write_only=True)
    selected_platform_version = serializers.CharField(
        write_only=True, allow_blank=True, default=""
    )
    target_processor = serializers.CharField(write_only=True)
    target_compiler = serializers.CharField(write_only=True)
    float_options = serializers.CharField(write_only=True, allow_blank=True)
    build_flags = serializers.CharField(write_only=True, default="", allow_blank=True)
    output_file = serializers.CharField(write_only=True, default="", allow_blank=True)
    debug = serializers.BooleanField(write_only=True, default=False)
    profile = serializers.BooleanField(write_only=True, default=False)
    test_data = serializers.CharField(
        write_only=True, default="", allow_blank=True, allow_null=True
    )
    extra_build_flags = serializers.CharField(
        write_only=True, default="", allow_blank=True
    )
    sample_rate = serializers.IntegerField(write_only=True, default=10)
    debug_level = serializers.IntegerField(write_only=True, default=1)
    profile_iterations = serializers.IntegerField(write_only=True, default=1000)
    profile_data = serializers.BooleanField(write_only=True, default=False)
    kb_description = serializers.CharField(write_only=True, default=False)
    output_options = serializers.ListField(
        write_only=True, allow_empty=True, default=list(), required=False
    )
    hardware_accelerator = serializers.CharField(
        write_only=True, default=None, allow_blank=True
    )

    class Meta:
        model = KnowledgePack
        fields = (
            "task_state",
            "task_result",
            "asynchronous",
            "target_platform",
            "selected_platform_version",
            "target_processor",
            "target_compiler",
            "build_flags",
            "output_file",
            "extra_build_flags",
            "debug",
            "debug_level",
            "profile",
            "profile_iterations",
            "test_data",
            "profile_data",
            "sample_rate",
            "kb_description",
            "output_options",
            "float_options",
            "application",
            "hardware_accelerator",
        )


class KnowledgePackExportSerializer(serializers.ModelSerializer):

    query_summary = serializers.SerializerMethodField()
    model_parameters = serializers.SerializerMethodField()
    model_configuration = serializers.SerializerMethodField()

    def get_model_parameters(self, obj):
        return obj.neuron_array

    def get_model_configuration(self, obj):
        return obj.device_configuration

    def get_query_summary(self, obj):

        empty_dict = {}

        if not hasattr(obj, "query_summary") or not obj.query_summary:
            return empty_dict  # for backward compatibility

        obj.query_summary.pop("segment_info", None)

        if isinstance(obj.query_summary["segmenter"], int):
            segmenter = model_to_dict(
                Segmenter.objects.get(
                    project=obj.project, pk=obj.query_summary["segmenter"]
                )
            )
            segmenter.pop("id")
            segmenter.pop("project")
            if segmenter.get("parameters"):
                segmenter["parameters"] = json.loads(segmenter["parameters"])
            if segmenter.get("preprocess"):
                segmenter["preprocess"] = json.loads(segmenter["preprocess"])

            obj.query_summary["segmenter"] = segmenter

        obj.query_summary.pop("cache", None)
        obj.query_summary.pop("uuid", None)
        obj.query_summary.pop("name", None)

        return obj.query_summary

    class Meta:
        model = KnowledgePack
        fields = (
            "uuid",
            "model_parameters",
            "model_configuration",
            "pipeline_summary",
            "query_summary",
            "feature_summary",
            "transform_summary",
            "sensor_summary",
            "class_map",
            "name",
            "project",
            "knowledgepack_summary",
        )


class KnowledgePackCreateSerializer(serializers.ModelSerializer):
    """Knowledge Pack Serializer"""

    project = serializers.UUIDField()
    model_parameters = serializers.JSONField()
    model_configuration = serializers.JSONField()

    def get_sandbox(self, obj):
        return obj.sandbox.uuid

    def get_project(self, obj):
        return obj.project.uuid

    def get_model_parameters(self, obj):
        return obj.neuron_array

    def get_model_configuration(self, obj):
        return obj.device_configuration

    def validate_project(self, value):
        return Project.objects.get(uuid=value)

    def validate_sandbox(self, value):
        return Sandbox.objects.get(uuid=value)

    def validate_model_parameters(self, value):
        model_gen = ModelGen()

        request = self.context["request"]

        return model_gen.validate_model_parameters(
            value, request.data.get("model_configuration")
        )

    def validate_model_configuration(self, value):
        model_gen = ModelGen()

        return model_gen.validate_model_configuration(value)

    def create(self, validated_data):

        validated_data["neuron_array"] = validated_data.pop("model_parameters")
        validated_data["device_configuration"] = validated_data.pop(
            "model_configuration"
        )

        knowledge_pack = KnowledgePack(**validated_data)

        knowledge_pack.save()

        knowledge_pack.model_parameters = knowledge_pack.neuron_array
        knowledge_pack.model_configuration = knowledge_pack.device_configuration

        return knowledge_pack

    class Meta:
        model = KnowledgePack
        fields = (
            "uuid",
            "model_parameters",
            "model_configuration",
            "pipeline_summary",
            "query_summary",
            "feature_summary",
            "transform_summary",
            "sensor_summary",
            "class_map",
            "name",
            "project",
            "knowledgepack_summary",
            "model_results",
        )


# Only export classes by default
__all__ = [cls[0] for cls in inspect.getmembers(sys.modules[__name__], inspect.isclass)]
