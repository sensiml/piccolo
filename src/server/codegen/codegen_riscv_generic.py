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

from codegen.knowledgepack_base import KnowledgePackCodeGeneratorBase
from datamanager.exceptions import KnowledgePackGenerationError
from datamanager.utils import ensure_path_exists
from django.conf import settings
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class RISCVGNUGenericCodeGenerator(KnowledgePackCodeGeneratorBase):
    def __init__(
        self,
        knowledgepacks,
        uuid,
        task_id,
        device_conf,
        build_type,
        test_data=None,
        target_os=None,
    ):
        super(RISCVGNUGenericCodeGenerator, self).__init__(
            knowledgepacks, uuid, task_id, device_conf, build_type
        )
        self.kb_generated_files = ["Makefile", "testdata.h"]
        self.test_data = test_data
        self.target_os = target_os

    def generate(self, build_type="lib"):
        logger.header = {"UUID": self.uuid}

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

        if isinstance(self.test_data, DataFrame):
            kb_data.update(
                self.create_test_data_debugger(
                    self.test_data[sensor_columns], sensor_columns
                )
            )

            kb_data["use_test_data"] = ["#define SML_USE_TEST_DATA"]

        elif (
            build_type == "bin"
            and self.application == "testdata_runner"
            and self.test_data is None
        ):
            raise KnowledgePackGenerationError(
                "Test data required for this application"
            )

        if self.is_tensorflow(classifier_types):
            
            proc = self.platform.target_processor

            target_arch = proc.compiler_cpu_flag.split("=")[1]

            if "hard" in self.device_config["float_options"]:
                target_arch += "+fp"

            if "softfp" in self.device_config["float_options"]:
                target_arch += "+sfp"


            logger.debug(
                {
                    "message": f"Building NN Library {self.nn_inference_engine}",
                    "log_type": "KPID",
                    "UUID": self.uuid,
                }
            )

            if self.nn_inference_engine == "nnom":
                self.docker_nnom.build_code_bin(build_type, self.application)
                self.compile_nnom = True

            else:
                raise (f"{self.nn_inference_engine} not supported")

        self.copy_application_files(
            output_data=kb_data,
            application=self.application,
            out_dir=os.path.join(kp_base_dir, "application"),
        )

        self.fill_template_files(kb_data, kp_base_dir)
        self.fill_kb_files(kb_data, kp_base_dir, classifier_types)
        self.fill_build_files(kb_data, kp_base_dir)
        self.copy_external_lib_files(kp_base_dir)

        return self.docker_libsensiml.build_code_bin(self.build_type, self.application)
