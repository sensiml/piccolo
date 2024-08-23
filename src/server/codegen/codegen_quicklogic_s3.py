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

from codegen.knowledgepack_base import (
    KnowledgePackCodeGeneratorBase,
)
from codegen.knowledgepack_device_command_mixin import DeviceCommandMixin
from datamanager.utils import ensure_path_exists
from django.conf import settings
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class QuickLogicS3CodeGenerator(KnowledgePackCodeGeneratorBase, DeviceCommandMixin):
    def __init__(
        self, knowledgepacks, uuid, task_id, device_conf, build_type, test_data=None
    ):
        super(QuickLogicS3CodeGenerator, self).__init__(
            knowledgepacks, uuid, task_id, device_conf, build_type
        )
        self.kb_generated_files = ["Makefile"]

        self.test_data = test_data
        self._deprecated_versions = ["1.0", "1.1"]
        self._device_command_versions = ["1.3", "1.3.1", "1.2"]

    def generate(self, build_type="lib"):
        kp_base_dir = "{0}/{1}".format(settings.SERVER_CODEGEN_ROOT, self.uuid)
        ensure_path_exists(kp_base_dir)
        logger.debug(
            {
                "message": "Knowledgepack base dir: {}".format(kp_base_dir),
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        kb_models, model_groups = self.get_model_data()
        kb_data, classifier_types = self.codegen(kb_models, model_groups)

        self.generate_directories(kp_base_dir)
        sensor_columns = kb_models[0]["used_sensor_columns"]

        kb_data.update(self.create_sml_abstraction_calls(kb_models))
        kb_data.update(self.create_arm_cpu_flags())

        if self.platform.execution_parameters.get("uses_sensiml_interface", False):
            # this is MQTT / SensiML interface spec. Done in base codegen.
            pass

        elif self.platform.execution_parameters.get("uses_device_command", False):
            config_list, num_msg = self.create_device_command_configuration_list(
                kb_models
            )

            kb_data["device_command_sensor_config"] = config_list
            # First and last lines don't count in structure definition.
            kb_data["device_command_num_config_msgs"] = [
                "#define SML_DEVICE_COMMAND_NUM_MSGS {}".format(num_msg)
            ]

        if isinstance(self.test_data, DataFrame):
            kb_data.update(
                self.create_test_data_debugger(
                    self.test_data[sensor_columns], sensor_columns
                )
            )
            self.kb_generated_files.append("testdata.h")
            kb_data["use_test_data"] = ["#define SML_USE_TEST_DATA"]

        self.copy_application_files(
            output_data=kb_data,
            application=self.application,
            out_dir=os.path.join(kp_base_dir, "application"),
        )

        self.fill_template_files(kb_data, kp_base_dir)
        self.fill_kb_files(kb_data, kp_base_dir, classifier_types)
        self.fill_build_files(kb_data, kp_base_dir)

        if self.is_tensorflow(classifier_types):
            logger.debug(
                {
                    "message": "Building Tensorflow Library",
                    "log_type": "KPID",
                    "UUID": self.uuid,
                }
            )
            self.docker_libtensorflow.set_tensorflow_compile(
                platform="cortex_m_generic",
                target_arch="cortex-m4+fp",
                hardware_accelerator=self.platform.hardware_accelerator_kernel,
            )
            self.docker_libtensorflow.build_code_bin(build_type, self.application)
            self.docker_libsensiml.compile_tensorflow = True

        return self.docker_libsensiml.build_code_bin(self.build_type, self.application)

    def create_device_command_configuration_list(self, kb_models):
        output = []
        output.extend(self.create_device_command_structure_def())
        # Contains Device Command protocol, generate that code properly.
        for model in [m for m in kb_models if not m["parent"]]:
            # Only generate for parent models.
            sensor_plugin_name = model.get("sensor_plugin", "").lower()
            if sensor_plugin_name in ["motion", "audio", "custom"]:
                output.extend(
                    self.create_device_command_from_source_selection(sensor_plugin_name)
                )
            else:
                # we have a UUID of capture configuration to pull from
                output.extend(self.create_device_command_from_capture_config(model))

        output.extend(self.create_device_command_structure_end())

        # First and last lines don't count in structure definition.
        return output, len(output) - 2
