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
import xml.etree.ElementTree as ET
import zipfile
from shutil import copyfile

from codegen.codegen_platform_mapper import KnowledgePackPlatformMapper
from django.conf import settings


logger = logging.getLogger(__name__)


class DockerRunnerLibTensorflowMixin:
    model_binary = None
    tf_target = None
    tf_platform = None

    def get_container_timeout_setting(self):
        return 600

    def get_ecs_timeout_settings(self):
        return {"Delay": 10, "MaxAttempts": 60}

    def _get_logstream_prefix(self):
        return "tfmicro"

    def set_tensorflow_compile(self, target_arch, platform, hardware_accelerator=""):
        self.tf_target_arch = target_arch
        self.tf_platform = platform
        self.tf_hardware_accelerator = hardware_accelerator

    def _get_build_prefix(self):
        prefix = "{0}".format(str(self.uuid))
        return prefix.replace(".", "-").replace(" ", "-")

    def _get_container_name(self, uuid=None):
        prefix = "{0}_{1}_{2}".format(
            str(uuid) if uuid else str(self.platform.id),
            self.platform.name,
            self.platform.version,
        )
        prefix = prefix.replace(".", "-").replace(" ", "-")
        return "tfmicro_{}".format(self._clean_name(prefix))

    def _process_container_results(self, debug_flag):
        with zipfile.ZipFile(
            "{0}/tflite-micro.zip".format(self.root_dir, self._get_build_prefix()),
            "r",
        ) as zip_ref:
            zip_ref.extractall(self.root_dir)

    def get_execution_params(self, build_type, application):
        execution_params = self.platform.execution_parameters

        if settings.CODEGEN_USE_ECS_FOR_DOCKER:
            execution_params["aws_access"] = settings.AWS_DOCKER_RUNNER_ACCESS_KEY
            execution_params["aws_sec"] = settings.AWS_DOCKER_RUNNER_SECRET_KEY
            execution_params["bucket_name"] = settings.AWS_CODEGEN_BUCKET_NAME

        execution_params["mount_directory"] = self.mount_directory
        execution_params["uuid"] = str(self.uuid)
        execution_params["user_id"] = str(self.user_id)
        execution_params["build_type"] = build_type
        execution_params["platform"] = self.platform.name.replace(" ", "-")
        execution_params["application"] = application
        execution_params["model_binary"] = self.model_binary
        execution_params["test_data"] = [[0, 0, 0]]
        execution_params["target_arch"] = self.tf_target_arch
        execution_params["target"] = self.tf_target_arch
        execution_params["platform"] = self.tf_platform
        execution_params["version"] = self.platform.version
        execution_params["hardware_accelerator"] = self.tf_hardware_accelerator
        execution_params["build_script_name"] = "build_tensorflow.sh"
        execution_params["platform_flags_2"] = (
            ""
            if not self.platform.get_float_specs()[1]
            else f"-mfloat-abi={self.platform.get_float_specs()[1]}"
        )

        self.platform = KnowledgePackPlatformMapper(
            platform_id="1183f67c-c279-4612-87eb-877d4063d75a",
            device_config=self.platform._device_config,
        )

        self.platform.selected_platform_version = (
            settings.CODEGEN_TENSORFLOW_PLATFORM_VERSION
        )

        with open(os.path.join(self.root_dir, "execute.json"), "w+") as f:
            f.write(json.dumps(execution_params))

        copyfile(
            os.path.join(
                settings.CODEGEN_PLATFORM_DIR,
                *self.platform.codegen_file_location,
                "build.sh",
            ),
            os.path.join(self.root_dir, "build_tensorflow.sh"),
        )

        return execution_params

    def retrieve_remote_knowledgepack(self):
        self._datastore.get(
            key=f"{self.uuid}/tflite-micro.zip",
            file_path=os.path.join(self.root_dir, "tflite-micro.zip"),
        )


def parse_robot_xml(root_dir):
    """Parse the generated robot_output.xml for the correct ktensor arena size"""

    tree = ET.parse(os.path.join(root_dir, "libsensiml/logs/robot_output.xml"))
    root = tree.getroot()

    for c in root.find("suite").find("test").iter("kw"):
        if c.attrib["name"] == "Wait For Line On Uart":
            for cc in c.getchildren():
                if cc.text and "Return:" in cc.text:
                    for x in cc.text.split("'"):
                        if "FOUND TENSOR SIZE" in x:
                            tensor_size = int(x.split(":")[1])
                            return (2 + (tensor_size // 1024)) * 1024

    return None


def find_and_replace(base_dir, ktensor_size):
    """fill in the correct tf_micro.h tensor arena size"""

    output = []
    with open(os.path.join(base_dir, "libsensiml/tf_micro.h"), "r") as fid:
        for line in fid.readlines():
            if "#define TF_MICRO_MAX_TENSOR_ARENA_SIZE" in line:
                output.append(
                    "#define TF_MICRO_MAX_TENSOR_ARENA_SIZE {}".format(
                        int(ktensor_size)
                    )
                )
            else:
                output.append(line)

    with open(os.path.join(base_dir, "libsensiml/tf_micro.h"), "w") as out:
        out.write("\n".join(output))
