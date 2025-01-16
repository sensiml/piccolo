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
import os
import tempfile
import time
from shutil import copyfile
from uuid import uuid4

from datamanager import utils
from datamanager.fields import AsyncTaskResult, AsyncTaskState, CurrentProjectDefault
from datamanager.models import Capture, CaptureConfiguration, DataTypes
from datamanager.datastore import get_datastore
from datamanager.utils.file_reader import CSVFileReader, WaveFileReader
from django.conf import settings
from django.db import transaction
from logger.data_logger import usage_log
from logger.log_handler import LogHandler
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault,
)


logger = LogHandler(logging.getLogger(__name__))


def parse_capture_datatype(schema):
    for _, item in schema.items():
        if item.get("type") == "float":
            return DataTypes.FLOAT32

    return DataTypes.INT32


def validate_capture_file(capture, tmp_name):
    # TODO: look at doing this validation without reading into memory

    if capture.format == ".csv":
        reader = CSVFileReader(tmp_name)

    elif capture.format == ".wav":
        wave_reader = WaveFileReader(tmp_name)
        f = tempfile.NamedTemporaryFile("w", delete=True)
        tmp_name = f.name
        reader = wave_reader.to_CSVFileReader(tmp_name)
        f.close()
    else:
        raise Exception("File type not supported")

    if not capture.project.capture_sample_schema:
        # TODO: Could have a potential race condition here, would prefer to
        # post the schema to the project instead of create here
        capture.project.capture_sample_schema = reader.schema
        capture.project.save(update_fields=["capture_sample_schema"])

    else:
        update_capture_sample_schema = False
        # TODO: for backwards compatibility we can update old schemas
        for index, (key, item) in enumerate(
            capture.project.capture_sample_schema.items()
        ):
            if item.get("index"):
                item.pop("index")
                update_capture_sample_schema = True

        for key in reader.schema.keys():
            if key not in capture.project.capture_sample_schema:
                capture.project.capture_sample_schema[key] = reader.schema[key]
                update_capture_sample_schema = True

        if capture.project.lock_schema:
            project_columns = sorted(list(capture.project.capture_sample_schema.keys()))
            capture_columns = sorted(list(reader.schema.keys()))
            if project_columns != capture_columns:
                raise serializers.ValidationError(
                    "Uploaded file does not match project schema {project_schema}. The uploaded file schema is: {capture_schema}".format(
                        project_schema=project_columns, capture_schema=capture_columns
                    )
                )

        if update_capture_sample_schema:
            capture.project.save(update_fields=["capture_sample_schema"])

    return (
        reader.num_samples,
        reader._dataframe.index[-1],
        reader.schema,
    )


class CaptureSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(default=CreateOnlyDefault(uuid4), read_only=True)
    name = serializers.CharField()
    capture_configuration_uuid = serializers.UUIDField(required=False)
    file = serializers.FileField(write_only=True)
    file_size = serializers.IntegerField(read_only=True)
    asynchronous = serializers.BooleanField(write_only=True, default=False)
    task_state = AsyncTaskState()
    task_result = AsyncTaskResult()

    def get_capture_configuration_uuid(self, o):
        if o.capture_configuration:
            return str(o.capture_configuration.uuid)

        return None

    def validate_name(self, name):
        if self.context["request"].method == "POST":
            if Capture.objects.filter(
                project__uuid=self.context["request"].parser_context["kwargs"][
                    "project_uuid"
                ],
                name=name,
            ).exists():
                raise ValidationError(
                    f"Project already contains a file with the name {name}"
                )

        return name

    @transaction.atomic
    def create(self, validated_data):
        start_time = time.time()

        request = self.context["request"]

        # making this work correctly
        # This is what I think is happening.  Previously django rest framework was filling in default argument in serializer if it wasn't passed in (1.9)
        # Now it is no longer filling in the default (). Our api has it as a kwargs in the url instead of part of the
        # request json which is causing it to not see it as an input. There is probably a better way to do this
        # I'm just not sure what it is.

        default_project = CurrentProjectDefault()
        default_project.set_context(self)
        validated_data["project"] = default_project()

        capture_configuration_uuid = validated_data.pop(
            "capture_configuration_uuid", None
        )
        if capture_configuration_uuid:
            capture_configuration = CaptureConfiguration.objects.get(
                project=validated_data["project"], uuid=capture_configuration_uuid
            )
            validated_data["capture_configuration"] = capture_configuration

        uploaded_file = validated_data.pop("file")
        validated_data.pop("asynchronous", False)

        if not uploaded_file:
            raise ValidationError("No data included in request!")

        ext = os.path.splitext(uploaded_file.name)[1]

        if ext not in (".csv", ".wav"):
            raise ValidationError("Extension {0} is not allowed.".format(ext))

        key = str(uuid4())
        capture = Capture(**validated_data)
        capture.file_size = uploaded_file.size

        capture.format = ext
        folder = "capture/{}".format(request.parser_context["kwargs"]["project_uuid"])
        (
            capture.number_samples,
            capture.max_sequence,
            capture.schema,
        ) = validate_capture_file(capture, uploaded_file.file.name)

        capture.datatype = parse_capture_datatype(capture.schema)

        datastore = get_datastore(folder=folder)
        # TODO: implement this in datastore
        if datastore.is_remote:
            datastore.save(key, uploaded_file.file.name, delete=True)
            capture.file = datastore._fold(key)
        else:
            utils.ensure_path_exists(settings.SERVER_CAPTURE_ROOT)
            folder = os.path.join(
                settings.SERVER_CAPTURE_ROOT,
                request.parser_context["kwargs"]["project_uuid"],
            )
            if not os.path.isdir(folder):
                os.mkdir(folder)
            copyfile(uploaded_file.file.name, os.path.join(folder, key))
            capture.file = os.path.join(folder, key)

        capture.save()

        usage_log(
            operation="capture_upload",
            team=capture.project.team,
            team_member=request.user.teammember,
            PJID=capture.project,
            CID=capture,
            runtime=time.time() - start_time,
        )

        return capture

    class Meta:
        model = Capture
        fields = (
            "uuid",
            "created_at",
            "last_modified",
            "last_modified_video",
            "version",
            "name",
            "file",
            "file_size",
            "asynchronous",
            "task_state",
            "task_result",
            "calculated_sample_rate",
            "max_sequence",
            "set_sample_rate",
            "number_samples",
            "capture_configuration_uuid",
        )
        read_only_fields = (
            "created_at",
            "last_modiied",
            "last_modified_video",
            "version",
            "max_sequence",
            "number_samples",
        )


class CaptureDetailSerializer(CaptureSerializer):
    file = serializers.HiddenField(default=None)
    capture_configuration_uuid = serializers.SerializerMethodField(allow_null=True)


class CaptureUpdateSerializer(CaptureSerializer):
    file = serializers.HiddenField(default=None)
    capture_configuration_uuid = serializers.UUIDField(required=False)

    def update(self, instance, validated_data):
        default_project = CurrentProjectDefault()
        default_project.set_context(self)
        project = default_project()

        capture_configuration_uuid = validated_data.pop(
            "capture_configuration_uuid", None
        )
        if capture_configuration_uuid:
            capture_configuration = CaptureConfiguration.objects.get(
                project=project, uuid=capture_configuration_uuid
            )
            validated_data["capture_configuration"] = capture_configuration

        for key, value in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        instance.version += 1

        instance.save()

        return instance
