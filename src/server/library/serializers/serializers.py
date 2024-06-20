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

import os
import time
from shutil import copyfile
from uuid import uuid4

from datamanager import utils
from datamanager.fields import AsyncTaskResult, AsyncTaskState
from datamanager.datastore import get_datastore
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from engine.base.utils import clean_results
from library.models import CustomTransform, LibraryPack, Transform
from pandas import DataFrame
from rest_framework import serializers

from rest_framework.fields import CreateOnlyDefault  # NOQA # isort:skip


class TransformSerializer(serializers.ModelSerializer):
    # library_pack = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Transform
        fields = [
            "uuid",
            "name",
            "input_contract",
            "output_contract",
            "description",
            "type",
            "subtype",
            "has_c_version",
            "library_pack",
            "automl_available",
        ]
        read_only_fields = [
            "uuid",
            "name",
            "input_contract",
            "output_contract",
            "description",
            "type",
            "subtype",
            "has_c_version",
            "library_pack",
            "automl_available",
        ]


class ExecuteSegmenterSerializer(serializers.Serializer):
    inputs = serializers.DictField(write_only=True)

    def validate(self, attrs):
        input_args = {}
        for key, value in attrs["inputs"].iteritems():
            newkey = str(key).strip("u'")
            input_args[newkey] = value

        input_args["input_data"] = DataFrame(input_args["input_data"])
        input_args["input_data"].index = input_args["input_data"].index.astype(
            int
        )  # Make sure index is type integer
        input_args["input_data"].sort_index(inplace=True)  # Resort by the integer index

        transform_call = utils.get_function(
            self.instance, function_to_get=self.instance.function_in_file + "_dcl"
        )
        result = transform_call(**input_args)

        # The result is a DataFrame that needs to be returned as json with the
        # integer index converted to strings
        return clean_results(result.to_dict())


class PlatformDescriptionSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    board_name = serializers.CharField(max_length=255)
    hardware_accelerators = serializers.JSONField(default=dict)
    #############################################################
    # this is for backwards compatibility with clients <2.6.
    # Remove at some point where we dont support the old method.
    board = serializers.JSONField(default=dict)
    #############################################################
    can_build_binary = serializers.BooleanField(default=False)
    platform = serializers.CharField(max_length=255)
    platform_version = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    ota_capable = serializers.BooleanField(default=False)
    execution_parameters = serializers.JSONField(default=dict)
    supported_source_drivers = serializers.JSONField(default=dict)
    supported_outputs = serializers.JSONField(default=list)
    target_os_options = serializers.JSONField(default=list)
    url = serializers.HyperlinkedIdentityField("platform-detail", lookup_field="pk")


class ProcessorSerializer(serializers.Serializer):
    architecture = serializers.StringRelatedField(many=False)
    float_options = serializers.JSONField()
    manufacturer = serializers.CharField(max_length=255)
    display_name = serializers.CharField(max_length=255)
    profiling_enabled = serializers.BooleanField()
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        fields = [
            "architecture",
            "float_options",
            "manufacturer",
            "display_name",
            "profiling_enabled",
            "uuid",
        ]


class CompilerSerializer(serializers.Serializer):
    supported_architecture = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )
    name = serializers.CharField(max_length=255, read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    compiler_version = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        fields = ["supported_architecture", "name", "uuid", "compiler_version"]


class PlatformDescriptionVersion2Serializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    uuid = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField(allow_null=True)
    hardware_accelerators = serializers.JSONField(default=dict)
    description = serializers.CharField(max_length=1000)
    can_build_binary = serializers.BooleanField(default=False)
    supported_source_drivers = serializers.JSONField(default=dict)
    platform_versions = serializers.JSONField(default=list)
    processors = ProcessorSerializer(many=True)
    applications = serializers.JSONField(default=list)
    supported_compilers = CompilerSerializer(read_only=True, many=True)
    default_selections = serializers.JSONField(default=dict)
    url = serializers.HyperlinkedIdentityField("platform2-detail", lookup_field="uuid")
    description = serializers.CharField(max_length=1000)
    documentation = serializers.CharField(max_length=255)
    platform_type = serializers.CharField(max_length=8)
    manufacturer = serializers.CharField(max_length=64)


class PipelineSeedSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    pipeline = serializers.JSONField()
    input_contract = serializers.JSONField()


class CustomTransformSerializerBase(serializers.ModelSerializer):
    uuid = serializers.UUIDField(default=CreateOnlyDefault(uuid4), read_only=True)
    file = serializers.FileField(write_only=True)
    task_state = AsyncTaskState()
    task_result = AsyncTaskResult()

    def validate_function_name(self, value):
        if Transform.objects.filter(custom=False, name=value).count():
            raise Exception("Invalid Name for the function, already exists!")

        return value

    def validate_c_function_name(self, value):
        if Transform.objects.filter(custom=False, c_function_name=value).count():
            raise Exception("Invalid Name for the file, already exists!")

        return value

    def validate_input_contract(self, value):

        valid_value = []
        has_columns = False
        for param in value:
            if param.get("name", None) is None:
                raise Exception("Invalid parameter Name")

            if param["name"] == "columns":
                has_columns = True
                param["type"] = "list"
                param["element_type"] = "str"
                if not param.get("description", ""):
                    param[
                        "description"
                    ] = "Set of columns on which to apply the transform"
                if param.get("num_columns", None) is None:
                    raise Exception(
                        "Must define a num_columns property for this feature generator!"
                    )
                if param["num_columns"] not in [-1, 1, 2, 3, 4, 5, 6]:
                    raise Exception("Invalid num_columns value!")
            elif param.get("c_param", None) is None:
                continue
            else:
                if param.get("type", None) not in ["int", "float"]:
                    raise Exception(
                        "Invalid parameter type {}".format(param.get("type", None))
                    )
                if param.get("default", None):
                    raise Exception("Invalid parameter default")
                if param.get("description", None) is None:
                    param["description"] = ""
                if not isinstance(param["description"], str):
                    raise Exception("Invalid parameter description")
                if param.get("c_param", None) is None:
                    raise Exception("Invalid parameter c_param")
                if not isinstance(param["c_param"], int):
                    raise Exception("paramter index must be type int")
                if param.get("range", None) is None:
                    raise Exception("Invalid parameter range")
                if not isinstance(param["range"], list):
                    raise Exception("paramter range must be type list")
                if len(param["range"]) != 2:
                    raise Exception(
                        "paramter range must have two values, left and right ranges."
                    )

                expected_type = int if param["type"] == "int" else float
                for x in param["range"]:
                    if not isinstance(x, expected_type):
                        raise Exception(
                            "paramter range must be of type {expected_type}".format(
                                param["type"]
                            )
                        )

            valid_value.append(param)

        if not has_columns:
            raise Exception("columns paramter not defined!")

        default_params = [
            {"name": "input_data", "type": "DataFrame"},
            {
                "name": "group_columns",
                "type": "list",
                "element_type": "str",
                "handle_by_set": True,
                "description": "Set of columns by which to aggregate",
            },
        ]

        valid_value.extend(default_params)

        return valid_value

    def validate_output_contract(self, value):

        """

        output_contract defaults to
            {"name": "output_data", "type": "DataFrame"}

        optional fields:
            familiy (bool): False if only returns single feature generator, True otherwise
            output_formula (str): A formula describing how to calculate the number of features this function will return

                This can be some combination of numbers, math operations, len(), and stored params:

                For example, a histogram which returns a feature based on the number of bins in its params would be

                            "output_formula": "params['number_of_bins']"

                You could also do one that returns the number of features that it has as input columns

                            "output_formula": "len(params['columns'])"

                Or a combination of parameters and columns

                            "output_formula": "params['new_length']*len(params['columns'])"

                The params argument must be one of the params that is in the input contract

            scratch_buffer (str): The size of the buffer this functions needs, you can access this buffer as a global called sortedData. You can assume this can be overwritten between functions.
                If no scratch_buffer size is provided, it is assumed this function does not use it.

                "scratch_buffer": {"type":"segment_size"}
                "scratch_buffer": {"type":"ring_buffer"}
                "scratch_buffer": {"type":"fixed_value", "value":512}
                "scratch_buffer": {"type":"parameter", "name":"number_of_bins"}

                 The scratch_buffer type segment_size, will be set to the size of a single ring buffer, so if you have windowing size 512 and have 6 channels. The size will be 512.
                 The scratch_buffer type ring_buffer, will be set to the size of the entire ring buffer, so if you have windowing size 512 and 6 channels the size will be 6*512 which is 3072.
                 The scratch_buffer type fixed_value, will set the value of the extra buffer to 512.
                 The scratch_buffer type paramter, will set the value of the extra buffer to the value of a parameter.

        """

        # TODO: Parse this function to sanitize it
        def parse_output_formula(value):
            return value

        if not isinstance(value, list):
            raise Exception("Invalid output contract format.")

        if not isinstance(value[0], dict):
            raise Exception("Invalid output contract formula")

        value = value[0]

        output_contract = {"name": "output_data", "type": "DataFrame"}

        if value.get("family", None) is not None:
            if isinstance(value.get("family"), bool) is False:
                raise Exception("Invlaid family type, must be Bool or empty")

            output_contract["family"] = value.get("family")
        if value.get("output_formula", None) is not None:
            output_contract["output_formula"] = parse_output_formula(
                value["output_formula"]
            )

        if value.get("scratch_buffer", None) is not None:
            scratch_buffer = value["scratch_buffer"]

            if scratch_buffer.get("type", None) is None:
                raise Exception("Invalid type for scratch buffer")

            if scratch_buffer["type"] not in [
                "segment_size",
                "ring_buffer",
                "fixed_value",
                "parameter",
            ]:
                raise Exception("Invalid type for scratch buffer")

            if scratch_buffer["type"] == "fixed_value":
                if (
                    int(scratch_buffer["value"]) > settings.MAX_SEGMENT_SIZE
                    or int(scratch_buffer["value"]) < 0
                ):
                    raise Exception(
                        "Value must be between 0 and {max_buffer}".format(
                            settings.MAX_SEGMENT_SIZE
                        )
                    )

                output_contract["scratch_buffer"] = {
                    "type": "fixed_value",
                    "value": int(scratch_buffer["value"]),
                }
            elif scratch_buffer["type"] == "parameter":
                if not isinstance(scratch_buffer.get("name", None), str):
                    raise Exception(
                        "name must be one of the parameters in the input contract"
                    )
                output_contract["scratch_buffer"] = {
                    "type": "parameter",
                    "name": scratch_buffer["name"],
                }

            else:
                output_contract["scratch_buffer"] = {"type": scratch_buffer.get("type")}

        return [output_contract]


class CustomTransformSerializer(CustomTransformSerializerBase):
    uuid = serializers.UUIDField(default=CreateOnlyDefault(uuid4), read_only=True)
    file = serializers.FileField(write_only=True)
    task_state = AsyncTaskState()
    task_result = AsyncTaskResult()
    library_pack = serializers.UUIDField()

    def validate_library_pack(self, value):
        return LibraryPack.objects.get(
            uuid=value, team=self.context["request"].user.teammember.team
        )

    @transaction.atomic
    def create(self, validated_data):
        from datamanager.tasks import process_custom_transform

        uploaded_file = validated_data.pop("file")

        if not uploaded_file:
            raise ValidationError("No data included in request!")

        ext = os.path.splitext(uploaded_file.name)[1]
        os.path.splitext(uploaded_file.name)[0]
        if ext not in (".c"):
            raise Exception("Extension {0} is not allowed.".format(ext))
        else:
            custom_transform = CustomTransform(**validated_data)
            custom_transform.uuid = uuid4()
            custom_transform.name = validated_data["name"]
            custom_transform.library_pack = validated_data["library_pack"]
            custom_transform.c_function_name = validated_data["c_function_name"]
            custom_transform.function_in_file = validated_data["c_function_name"]
            custom_transform.c_file_name = validated_data["c_function_name"] + ".c"
            custom_transform.automl_available = False
            custom_transform.custom = True
            custom_transform.has_c_version = True
            custom_transform.unit_tests = validated_data["unit_tests"]
            custom_transform.save()

            key = str(custom_transform.uuid)

            folder = f"custom_transforms/{validated_data['library_pack'].uuid}"
            datastore = get_datastore(folder=folder)

            # TODO: DATASTORE put all in single call
            if datastore.is_remote:
                datastore.save(key, uploaded_file.file.name, delete=True)
            else:
                utils.ensure_path_exists(settings.SERVER_CUSTOM_TRANSFORM_ROOT)
                folder = os.path.join(
                    settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                    str(validated_data["library_pack"].uuid),
                )
                if not os.path.isdir(folder):
                    os.mkdir(folder)
                copyfile(uploaded_file.file.name, os.path.join(folder, key))

            custom_transform.file_path = key

            custom_transform.save()

        task = process_custom_transform.s(custom_transform.pk, folder, key)

        time.sleep(1)
        result = task.apply_async()
        custom_transform.task = result.id
        custom_transform.task_result = "SENT"
        custom_transform.save()

        return custom_transform

    class Meta:
        model = CustomTransform
        fields = [
            "uuid",
            "file",
            "name",
            "c_function_name",
            "input_contract",
            "output_contract",
            "description",
            "type",
            "subtype",
            "task_state",
            "task_result",
            "created_at",
            "last_modified",
            "unit_tests",
            "library_pack",
        ]
        read_only_fields = [
            "uuid",
            "task_state",
            "task_result",
            "created_at",
            "last_modified",
        ]


class CustomTransformDetailsSerializer(CustomTransformSerializerBase):
    @transaction.atomic
    def update(self, instance, validated_data):
        from datamanager.tasks import process_custom_transform

        uploaded_file = validated_data.pop("file")

        if not uploaded_file:
            raise ValidationError("No data included in request!")

        ext = os.path.splitext(uploaded_file.name)[1]
        os.path.splitext(uploaded_file.name)[0]
        if ext not in (".c"):
            raise ValidationError("Extension {0} is not allowed.".format(ext))
        else:
            custom_transform = instance
            key = custom_transform.file_path
            custom_transform.logs = None
            custom_transform.automl_available = False
            folder = "custom_transforms/{}".format(custom_transform.library_pack.uuid)
            datastore = get_datastore(folder=folder)

            # TODO: DATASTORE put in single call
            if datastore.is_remote:
                datastore.save(key, uploaded_file.file.name, delete=True)
            else:
                utils.ensure_path_exists(settings.SERVER_CUSTOM_TRANSFORM_ROOT)
                folder = os.path.join(
                    settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                    str(custom_transform.library_pack.uuid),
                )
                if not os.path.isdir(folder):
                    os.mkdir(folder)
                copyfile(uploaded_file.file.name, os.path.join(folder, key))

            custom_transform.save()

        time.sleep(1)
        task = process_custom_transform.s(custom_transform.pk, folder, key)

        result = task.apply_async()
        custom_transform.task = result.id
        custom_transform.task_result = "SENT"
        custom_transform.save()

        return custom_transform

    class Meta:
        model = CustomTransform
        fields = [
            "uuid",
            "file",
            "name",
            "c_function_name",
            "input_contract",
            "output_contract",
            "description",
            "type",
            "subtype",
            "task_state",
            "task_result",
            "unit_tests",
            "logs",
            "library_pack",
        ]
        read_only_fields = [
            "uuid",
            "task_state",
            "task_result",
            "name",
            "logs",
            "library_pack",
            "c_function_name",
            "type",
            "subtype",
        ]


class LibraryPackSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        library_pack = LibraryPack(**validated_data)
        library_pack.team = self.context["request"].user.teammember.team
        library_pack.save()

        return library_pack

    class Meta:
        model = LibraryPack
        fields = ["uuid", "name", "build_version", "description", "maintainer"]
        read_only_fields = ["uuid", "build_version"]
