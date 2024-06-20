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

import copy
import os
import shutil
from uuid import uuid4

from datamanager import utils
from datamanager.models import (
    Capture,
    CaptureConfiguration,
    CaptureLabelValue,
    CaptureMetadataValue,
    Label,
    LabelValue,
    Project,
    Segmenter,
)
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    python manage.py <path-to-csv>
    """

    help = "Add all users of a teams to all sandboxes in that team"

    def add_arguments(self, parser):
        parser.add_argument(
            "source_project_uuid",
            nargs="+",
            type=str,
        )

        parser.add_argument(
            "new_project_name",
            nargs="+",
            type=str,
        )

    def handle(self, *args, **options):
        initial_project_uuid = options.get("source_project_uuid")
        new_project_name = options.get("new_project_name")
        initial_project = Project.objects.get(uuid=initial_project_uuid)
        new_project = copy.deepcopy(initial_project)
        new_project.uuid = str(uuid4())
        new_project.pk = None
        new_project.name = new_project_name
        new_project.save()

        print("copying capture config")

        capture_config_dict = {}
        for capture_config in CaptureConfiguration.objects.filter(
            project=initial_project
        ):
            tmp_uuid = capture_config.uuid
            capture_config_dict[capture_config.uuid] = None
            capture_config.uuid = str(uuid4())
            capture_config.pk = None
            capture_config.project = new_project
            capture_config.save()
            capture_config_dict[tmp_uuid] = capture_config

        print("copying captures")
        capture_dict = {}
        for capture in Capture.objects.filter(project=initial_project):
            tmp_uuid = capture.uuid
            capture_dict[capture.uuid] = None
            capture.uuid = str(uuid4())
            capture.pk = None
            capture.project = new_project
            capture.capture_configuration = capture_config_dict[
                capture.capture_configuration.uuid
            ]

            utils.ensure_path_exists(settings.SERVER_CAPTURE_ROOT)
            new_folder = os.path.join(
                settings.SERVER_CAPTURE_ROOT,
                new_project.uuid,
            )
            if not os.path.isdir(new_folder):
                os.mkdir(new_folder)

            shutil.copyfile(
                capture.file, os.path.join(new_folder, os.path.basename(capture.file))
            )
            capture.file = os.path.join(new_folder, os.path.basename(capture.file))
            capture.save()
            capture_dict[tmp_uuid] = capture

        print("copying sessions")

        session_dict = {}
        for session in Segmenter.objects.filter(project=initial_project):
            tmp_uuid = session.pk
            session_dict[session.pk] = None
            session.pk = None
            session.project = new_project
            session.save()
            session_dict[tmp_uuid] = session

        label_dict = {}
        label_value_dict = {}

        print("copying labels")
        for label in Label.objects.filter(project=initial_project):
            tmp_uuid = label.uuid
            label_dict[label.uuid] = None
            label.uuid = str(uuid4())
            label.pk = None
            label.project = new_project
            label.save()
            label_dict[tmp_uuid] = label

            for label_value in LabelValue.objects.filter(label__uuid=tmp_uuid):
                tmp_uuid = label_value.uuid
                label_value_dict[label_value.uuid] = None
                label_value.uuid = str(uuid4())
                label_value.pk = None
                label_value.label = label
                label_value.save()
                label_value_dict[tmp_uuid] = label_value

        print("copying capture label values")
        for capture_label_value in CaptureLabelValue.objects.filter(
            project=initial_project
        ):
            capture_label_value.uuid = str(uuid4())
            capture_label_value.pk = None
            capture_label_value.label = label_dict[capture_label_value.label.uuid]
            capture_label_value.capture = capture_dict[capture_label_value.capture.uuid]
            capture_label_value.label_value = label_value_dict[
                capture_label_value.label_value.uuid
            ]
            capture_label_value.segmenter = session_dict[
                capture_label_value.segmenter.pk
            ]
            capture_label_value.project = new_project
            capture_label_value.save()

        print("copying capture metadata values")
        for capture_metatadata_value in CaptureMetadataValue.objects.filter(
            project=initial_project
        ):
            capture_metatadata_value.uuid = str(uuid4())
            capture_metatadata_value.pk = None
            capture_metatadata_value.label = label_dict[
                capture_metatadata_value.label.uuid
            ]
            capture_metatadata_value.capture = capture_dict[
                capture_metatadata_value.capture.uuid
            ]
            capture_metatadata_value.label_value = label_value_dict[
                capture_metatadata_value.label_value.uuid
            ]
            capture_metatadata_value.project = new_project
            capture_metatadata_value.save()
