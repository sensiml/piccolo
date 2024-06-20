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

import json
import os

from codegen.codegen_platform_mapper import KnowledgePackPlatformMapper
from codegen.docker_libsensiml import DockerRunnerSensiMLMixin
from django.conf import settings
from django.core.management.base import BaseCommand
from library.models import (
    CompilerDescription,
    ProcessorDescription,
)


class Command(BaseCommand):
    """
    python manage.py run_libsensiml_build --uuid=<Knowledge-Pack-UUID>

    add a config.json to the folder which contains thhe config that would hhave been sent by the client.

    easiest way to generate that is

        import json
        from sensiml import *
        client = SensiML()

        # to see list of platforms
        print(client.platformsv2.platform_dict)

        config = client.platformsv2.platform_dict[<PLATFORM-NAME>].get_config()
        json.dump(config, open('config.json','w'))


    """

    help = "runs the docker build process for a knowledgepack that has already been created."

    def add_arguments(self, parser):
        parser.add_argument("--uuid", type=str)
        parser.add_argument("--platform_id", type=str, default="")
        parser.add_argument("--application", type=str, default="")
        parser.add_argument("--build_type", type=str, default="")
        parser.add_argument("--debug", nargs="?", type=bool, default=False)

    def handle(self, *args, **options):
        """ """

        uuid = options.get("uuid")
        task_id = "test"
        application = options.get("application")
        debug = options.get("debug")
        platform_id = options.get("platform_id")
        build_type = options.get("build_type")
        base_code_dir = "{0}/{1}".format(settings.SERVER_CODEGEN_ROOT, uuid)

        data = {}

        data = json.load(open(os.path.join(base_code_dir, "execute.json"), "r"))
        config = json.load(open(os.path.join(base_code_dir, "config.json"), "r"))
        data.update(config)

        data["output_file"] = "{0}_gen.zip".format(uuid)
        data["application"] = application if application else config["application"]
        data["platform_id"] = platform_id if platform_id else config["target_platform"]
        data["debug"] = debug if debug else config["debug"]
        data["build_type"] = build_type if build_type else data["build_type"]
        data["target_compiler"] = CompilerDescription.objects.get(
            uuid=config["target_compiler"]
        )
        data["target_processor"] = ProcessorDescription.objects.get(
            uuid=config["target_processor"]
        )

        platform = KnowledgePackPlatformMapper(data["platform_id"], data)

        docker_libsensiml = DockerRunnerSensiMLMixin(
            base_code_dir,
            uuid,
            task_id,
            debug,
            platform,
            data,
        )

        docker_libsensiml.build_code_bin(data["build_type"], data["application"])
