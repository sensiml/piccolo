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

from django.conf import settings
from django.core.management.base import BaseCommand
from library.models import PlatformDescriptionVersion2


class Command(BaseCommand):
    """
    python manage.py pull_latest_docker
    """

    help = "Pull latest docker images to local machine"

    def add_arguments(self, parser):
        parser.add_argument(
            "platform_name",
            nargs="+",
            type=str,
        )

    def handle(self, *args, **options):
        os.system("aws ecr get-login --no-include-email | bash")

        platform_name = options.get("platform_name")

        platforms = PlatformDescriptionVersion2.objects.all()
        for platform in platforms:

            if platform_name and platform.name != platform_name:
                continue

            if platform.docker_image is None or platform.docker_image == "":
                compilers = platform.supported_compilers.all()
                for c in compilers:
                    os.system(
                        f"docker pull {settings.DOCKER_REGISTRY}/{c.docker_image_base}:{c.compiler_version}"
                    )
            for version in platform.platform_versions:
                try:
                    os.system(
                        f"docker pull {settings.DOCKER_REGISTRY}/{platform.docker_image}:{version}"
                    )
                except:
                    print(
                        f"FAILED TO PULL LATEST DOCKER FOR  {settings.DOCKER_REGISTRY}/{platform.docker_image}:{version}"
                    )
