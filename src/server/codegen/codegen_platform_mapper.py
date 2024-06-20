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
import logging
import os

from codegen.docker_libsensiml import CompilationErrorException
from codegen.utils import is_valid_uuid4
from django.conf import settings
from library.models import PlatformDescriptionVersion2
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


class KnowledgePackPlatformMapper(object):
    def __init__(self, platform_id, device_config=None):
        if isinstance(platform_id, PlatformDescriptionVersion2):
            self._platform = platform_id
        elif is_valid_uuid4(platform_id):
            self._platform = PlatformDescriptionVersion2.objects.get(uuid=platform_id)
        else:
            raise Exception("Invalid Platform ID")

        self._device_config = device_config if device_config else {}
        self.selected_platform_version = device_config.get(
            "selected_platform_version", ""
        )
        self._execution_parameters = self.init_execution_parameters()

    @property
    def id(self):
        return self._platform.uuid

    @property
    def execution_parameters(self):
        return self._execution_parameters

    @property
    def device_config(self):
        return self._device_config

    @property
    def name(self):
        return self._platform.name

    @property
    def version(self):
        if self._platform.docker_image is None:
            return f"{self.compiler_version}-{self.compiler_docker_image_version}"
        else:
            return (
                f"{self.selected_platform_version}-{self.platform_docker_image_version}"
            )

    @property
    def platform_docker_image_version(self):
        return f"{self._platform.docker_image_version}"

    @property
    def compiler_version(self):
        return "{}".format(self.target_compiler.compiler_version.replace(" ", "-"))

    @property
    def compiler_docker_image_version(self):
        return "{}".format(self.target_compiler.docker_image_version.replace(" ", "-"))

    @property
    def target_processor(self):
        return self._device_config.get("target_processor", None)

    @property
    def target_compiler(self):
        return self._device_config.get("target_compiler", None)

    @property
    def supported_source_drivers(self):
        return self._platform.supported_source_drivers

    @property
    def can_build_binary(self):
        return self._platform.can_build_binary

    @property
    def docker_image(self):
        return self._platform.docker_image

    @property
    def hardware_accelerators(self):
        return self._platform.hardware_accelerators

    @property
    def hardware_accelerator_kernel(self):
        if self.hardware_accelerators.get(
            self.device_config.get("hardware_accelerator", "")
        ):
            return self.hardware_accelerators[
                self.device_config["hardware_accelerator"]
            ]["kernel"]
        return ""

    @property
    def codegen_file_location(self):
        return self._platform.codegen_file_location

    @property
    def target_os_options(self):
        return None

    @property
    def board_name(self):
        return ""

    @property
    def profiling_enabled(self):
        if self.target_processor.profiling_enabled:
            return self.device_config.get("profile", False)
        else:
            return False

    def init_execution_parameters(self):
        execution_parameters = copy.deepcopy(self._platform.codegen_parameters)

        appdata = self.get_codegen_application_data(
            self._device_config.get("application", None)
        )

        execution_parameters.update(appdata.get("codegen_parameters", dict()))
        return execution_parameters

    def get_float_specs(self):
        if self.target_processor.architecture.name == "ARM":
            float_str = self._device_config.get("float_options", None)

            if float_str is None:
                raise Exception("Float options were not specified.")

            float_hw = "soft"
            float_specification = "auto"

            for item in float_str.split(" "):
                if "-mfloat-abi" in item:
                    float_hw = item.split("=")[1]
                if "-mfpu" in item:
                    float_specification = item.split("=")[1]

            return float_str, float_hw, float_specification

        return None, None, None

    def get_compile_string(self):
        if self.target_processor.architecture.name == "x86":
            return "`g++ main.c a.out -L../libsensiml -lsensiml -lm -I../libsensiml`"
        elif self.target_processor.architecture.name == "ARM":
            cpu = self.get_cpu_flag()
            float_str, float_hw, float_spec = self.get_float_specs()
            return "`g++ main.c a.out -L../libsensiml -lsensiml -lm -I../libsensiml` {0} -mcpu-{1}".format(
                float_str, cpu
            )

        return ""

    def get_ecs_task_family(self, fargate=False):
        if self._platform.docker_image is None:
            ret = "{}-{}-{}-{}".format(
                str(self._platform.uuid)[:8],
                str(self.target_compiler.uuid)[:8],
                self.target_compiler.name,
                self.version,
            )
        else:
            ret = "{}-{}-{}".format(
                str(self._platform.uuid)[:8], self._platform.name, self.version
            )

        if fargate:
            ret = f"{ret}-fargate-{settings.ENVIRONMENT}"

        return (
            ret.replace(".", "-")
            .replace(" ", "-")
            .replace("---", "-")
            .replace("(", "")
            .replace(")", "")
        )

    def get_cpu_flag(self):
        cpu = None
        if self.target_processor.architecture.name == "ARM":
            cpu = self.target_processor.compiler_cpu_flag

        return cpu

    def get_compiler_flags(self):
        return self.target_processor.compiler_cpu_flag

    def get_target_architecture(self):
        tmp = self.target_processor.compiler_cpu_flag.split("=")
        if len(tmp) == 2:
            return tmp[1]

        return self.target_processor.display_name.lower().replace(" ", "-")

    def get_docker_image(self):
        if self._platform.docker_image is not None:
            return f"{settings.DOCKER_REGISTRY}/{self._platform.docker_image}:{str(self.selected_platform_version)}-{self._platform.docker_image_version}"

        if self.target_compiler is None:
            raise CompilationErrorException("Docker image not found")
        else:
            return f"{settings.DOCKER_REGISTRY}/{self.target_compiler.docker_image_base}:{self.compiler_version}-{self.compiler_docker_image_version}"

    def get_codegen_application_name(self, application_name):
        application = self._platform.applications.get(application_name, None)

        if application is None:
            raise Exception("Invalid Application: {}".format(application_name))

        return application["codegen_app_name"]

    def get_codegen_application_data(self, application_name):
        if not self._platform.applications:
            return {}

        application = self._platform.applications.get(application_name, None)

        if application is None:
            raise Exception("Invalid Application: {}".format(application_name))

        return application

    def codegen_app_location(self, application_name):
        if not self._platform.applications:
            return "applications"

        application = self._platform.applications.get(application_name, None)

        if application is None:
            raise Exception("Invalid Application: {}".format(application_name))

        app_location = application.get("codegen_app_location", None)
        app_folder = application.get("codegen_app_name")
        if app_location:
            return os.path.join(app_location, "applications", app_folder)

        return os.path.join("applications", app_folder)

    def get_application_environment(self):
        return [
            {"name": k, "value": v}
            for k, v in self._platform.codegen_parameters.get(
                "app_environment", dict()
            ).items()
        ]
