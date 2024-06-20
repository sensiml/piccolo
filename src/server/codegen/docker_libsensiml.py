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
import logging
import os
from codegen.docker_errors import CompilationErrorException, SRAMOverflowException
from django.conf import settings


logger = logging.getLogger(__name__)


class DockerRunnerSensiMLMixin:
    def get_execution_params(self, build_type, application):
        execution_params = self.platform.execution_parameters

        execution_params["bucket_name"] = settings.AWS_CODEGEN_BUCKET_NAME
        execution_params["mount_directory"] = self.mount_directory
        execution_params["project"] = self.platform.get_codegen_application_name(
            application
        )
        execution_params["uuid"] = str(self.uuid)
        execution_params["user_id"] = str(self.user_id)
        execution_params["build_type"] = build_type
        execution_params["debug_flag"] = self.debug_flag
        execution_params["version"] = self.platform.version
        execution_params["platform"] = self.platform.name.replace(" ", "-")
        execution_params["target"] = self.platform.get_target_architecture()
        execution_params["application"] = "application"
        execution_params["build_script_name"] = "build.sh"
        execution_params["profile_data"] = self.device_config.get("profile", False)

        # Code for dynamic name changes
        execution_params["library_name"] = settings.KNOWLEDGEPACK_LIBRARY_NAME
        execution_params["directory_name"] = settings.KNOWLEDGEPACK_DIRECTORY_NAME
        execution_params["extra_build_flags"] = " ".join(
            [
                self.platform.get_compiler_flags(),
                self.device_config.get("extra_build_flags", ""),
            ]
        )
        execution_params["sample_rate"] = self.device_config.get("sample_rate", 100)

        with open(os.path.join(self.root_dir, "execute.json"), "w+") as f:
            f.write(json.dumps(execution_params))
        return execution_params

    def _get_build_prefix(self):
        platform_version = self.platform.version
        prefix = "{0}_{1}_{2}_{3}".format(
            str(self.uuid),
            self.platform.name,
            platform_version,
            self.debug_flag,
        )
        return prefix.replace(".", "-").replace(" ", "-")

    def _get_container_name(self, uuid=None):
        prefix = "{0}_{1}_{2}".format(
            str(uuid) if uuid else str(self.platform.id),
            self.platform.name,
            self.platform.version,
        )
        prefix = prefix.replace(".", "-").replace(" ", "-")
        return "kp_bin_{}".format(self._clean_name(prefix))

    def _process_container_results(self, debug_flag):
        with open("{0}/output_binary_name".format(self.root_dir), "r") as op:
            generated_file_name = op.readline().strip()
        return_path = os.path.join(self.root_dir, "codegen-compiled-output")
        os.rename(return_path, os.path.join(self.root_dir, generated_file_name))

        os.remove("{0}/output_binary_name".format(self.root_dir))
        return os.path.join(self.root_dir, generated_file_name)

    def parse_build_log_for_errors(self, filename):
        with open(filename, "r") as fid:
            M = fid.readlines()
            for i, line in enumerate(M[-20:]):
                if "SRAM" in line:
                    raise SRAMOverflowException(
                        M[-20 + i + 1].split(":")[1][:-1]
                        + ". Try reducing the maximum size of your Segment length or the number of data streams in your pipeline."
                    )

    def get_container_timeout_setting(self):
        return 1000

    def get_ecs_timeout_settings(self):
        return {"Delay": 10, "MaxAttempts": 90}

    def _get_logstream_prefix(self):
        return "codegen"

    def _handle_ecs_build_failures(self):
        sram_overflow_filter = self._cloud_logs.get_log_events(
            logGroupName=settings.AWS_DOCKER_LOGS, logStreamName=self.obj.logs
        )

        sram_events = sram_overflow_filter.get("events", None)
        if sram_events and len(sram_events) > 0:
            for e in sram_events:
                message = e["message"]
                try:
                    idx = message.lower().index("overflowed by")
                    idx = idx if idx - 12 < 0 else idx - 12
                    raise SRAMOverflowException(
                        "Knowledge Pack will not fit: RAM {}".format(message[idx:])
                    )
                except ValueError:
                    pass

        raise CompilationErrorException(
            "\n\nCompile Error: This KnowledgePack configuration failed to compile.\n\nYou can create a support ticket at {0}\n\nInclude the above configuration and this knowledgpack uuid: {1}.".format(
                settings.SENSIML_SUPPORT, self.uuid
            )
        )
