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
import sys

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "initializes system directories for servers"
    can_import_settings = True

    def handle(self, *args, **options):
        # important system directories for server
        directories = [
            settings.SERVER_DATA_ROOT,
            settings.SERVER_CACHE_ROOT,
            settings.SERVER_CODEGEN_ROOT,
            settings.SERVER_QUERY_ROOT,
            settings.SERVER_FEATURE_FILE_ROOT,
            settings.SERVER_CUSTOM_TRANSFORM_ROOT,
            settings.SERVER_CAPTURE_ROOT,
            settings.SERVER_MODEL_STORE_ROOT,
        ]

        try:
            for directory in directories:
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    print(directory + " Created")

        except OSError as e:
            if e.errno == 13:
                print(
                    e.strerror
                    + " Please check permission on following path: "
                    + directory
                )
                sys.exit(1)

            if e.errno == 17:
                print(
                    "Directory: " + directory + " already in place. skipping creation"
                )
                sys.exit(0)

        except:
            print("Unexpected error occurred during file creation")
            sys.exit(1)
