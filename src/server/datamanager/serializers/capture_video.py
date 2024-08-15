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

from django.db import transaction
from rest_framework import serializers
from shutil import move
from uuid import uuid4
from datamanager import utils

from rest_framework.fields import CreateOnlyDefault
from django.conf import settings
from datamanager.datastore import get_datastore
from rest_framework.exceptions import NotAcceptable, ValidationError
from datamanager.fields import CurrentCaptureDefault
from datamanager.models import CaptureVideo
from rest_framework.reverse import reverse


def get_video_limit():
    return settings.CAPTURE_VIDEO_MAX_MB * 1000000


class CaptureVideoSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(default=CreateOnlyDefault(uuid4), read_only=True)
    name = serializers.CharField(required=True)
    file = serializers.FileField(
        write_only=True, required=False, max_length=(get_video_limit())
    )
    file_size = serializers.IntegerField(required=False)
    video = serializers.SerializerMethodField(read_only=True)
    upload_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CaptureVideo
        fields = (
            "uuid",
            "name",
            "file",
            "file_size",
            "keypoints",
            "video",
            "upload_url",
            "created_at",
            "last_modified",
        )
        read_only_fields = ("uuid",)

    def get_upload_url(self, obj):
        if hasattr(obj, "upload_url") and obj.upload_url:
            return obj.upload_url
        return None

    def get_video(self, obj):
        return reverse(
            "capture-video-file",
            kwargs={
                "project_uuid": obj.capture.project.uuid,
                "capture_uuid": obj.capture.uuid,
                "uuid": obj.uuid,
            },
        )

    def validate(self, attrs):
        uploaded_file = attrs.get("file")
        if not uploaded_file:
            if not attrs.get("file_size"):
                raise ValidationError(
                    "When file is not uploaded file_size should be provided"
                )
        return super().validate(attrs)

    def validate_name(self, name):
        if not name:
            return name

        ext = os.path.splitext(name)[1]
        if ext not in settings.CAPTURE_VIDEOS_EXT_LIST:
            raise ValidationError(
                f"Video format {ext} is not in supported list. Use {''.join(settings.CAPTURE_VIDEOS_EXT_LIST)}"
            )

        return name

    def validate_file_size(self, file_size):
        if file_size > (get_video_limit()):
            raise ValidationError(
                f"Maximum size of capture video is {settings.CAPTURE_VIDEO_MAX_MB} MB"
            )
        return file_size

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        project_uuid = request.parser_context["kwargs"]["project_uuid"]
        default_capture = CurrentCaptureDefault()
        default_capture.set_context(self)

        uploaded_file = validated_data.pop("file") if "file" in validated_data else None
        capture_video = CaptureVideo(capture=default_capture(), **validated_data)

        if uploaded_file:
            if not capture_video.name:
                capture_video.name = uploaded_file.name

            capture_video.file_size = uploaded_file.size

        ext = os.path.splitext(capture_video.name)[1][1:]
        file_key_name = f"{capture_video.uuid}.{ext}"

        datastore = get_datastore(
            folder=f"{settings.CAPTURE_VIDEO_S3_ROOT}/{project_uuid}"
        )

        if not uploaded_file:
            try:
                upload_url = datastore.create_url(
                    key=file_key_name,
                    content_type=f"video/{ext}",
                    content_length=capture_video.file_size,
                )
                capture_video.save()
                capture_video.upload_url = upload_url
                return capture_video
            except NotImplementedError as error:
                raise NotAcceptable(error)
        else:
            # TODO: DATASTORE fix this so its in the same call
            if datastore.is_remote:
                datastore.save(file_key_name, uploaded_file.file.name, delete=True)
            else:
                utils.ensure_path_exists(settings.SERVER_CAPTURE_VIDEO_ROOT)
                folder = capture_video.get_folder(project_uuid)
                if not os.path.isdir(folder):
                    os.mkdir(folder)
                move(uploaded_file.file.name, os.path.join(folder, file_key_name))

        capture_video.save()
        return capture_video


class CaptureVideoDetailSerializer(CaptureVideoSerializer):
    file = serializers.HiddenField(default=None)


class CaptureVideoBulkSerializer(CaptureVideoSerializer):
    capture_uuid = serializers.SerializerMethodField(read_only=True)

    class Meta(CaptureVideoSerializer.Meta):
        fields = CaptureVideoSerializer.Meta.fields + ("capture_uuid",)

    def get_capture_uuid(self, obj):
        return obj.capture.uuid
