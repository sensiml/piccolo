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
from shutil import rmtree

from codegen.codegen_platform_mapper import KnowledgePackPlatformMapper
from codegen.docker_runner import get_docker_runner
from codegen.knowledgepack_codegen_mixin import CodeGenMixin
from codegen.knowledgepack_fill_files_mixin import FillFilesMixin
from codegen.knowledgepack_model_graph_mixin import ModelGraphMixin
from datamanager.models import KnowledgePack
from django.conf import settings


class NoSampleRateDefinedException(Exception):
    pass


class NoSpotterDefinedException(Exception):
    pass


logger = logging.getLogger(__name__)


class NeuronNumberException(Exception):
    pass


class NeuronVectorException(Exception):
    pass


class InvalidConfigurationException(Exception):
    pass


def get_team_from_uuid(uuid):
    return KnowledgePack.objects.get(uuid=uuid).project.team.uuid


class KnowledgePackCodeGeneratorBase(
    FillFilesMixin,
    CodeGenMixin,
    ModelGraphMixin,
):
    """
    #The knowledgepackcodegenerator class consists of 3 main types of functions
    which adhear to the following design paradigm.

    ModelGraphMixin - get information from the knowledgepack models to be used to fill in information

    CodegenMixin - creates a list of strings that will replace a FILL_xxx in the template c code files

    FillFilesMixin- copy template files and replace FILL_xxx in these files with
    generated c code in the keys value of the kb_data dictionary

    """

    def __init__(self, knowledgepacks, uuid, task_id, device_conf, build_type):
        self.kb_generated_files = []
        self.codegen_dict = {}
        self.knowledgepacks = knowledgepacks
        self.team_uuid = get_team_from_uuid(uuid)
        self.uuid = str(uuid)
        self.task_id = str(task_id)
        self.device_config = device_conf
        platform_id = self.device_config["target_platform"]
        self.platform = KnowledgePackPlatformMapper(platform_id, self.device_config)
        self.application = device_conf.get("application")

        self.add_profile_data = self.device_config.get("profile_data", False)
        self.build_type = build_type
        self.spotter_name = None
        self.max_feature_selection = 0
        self.kb_generated_files = []
        self.build_files = [
            "build.sh",
            "copy_files.sh",
            "README.md",
            "config_sensor_files.sh",
            "build_binary.sh",
            "package_library.sh",
        ]
        self.compile_tensorflow = False

        base_code_dir = "{0}/{1}".format(settings.SERVER_CODEGEN_ROOT, self.uuid)

        self.ensure_path_exists(base_code_dir)
        self.docker_libsensiml = get_docker_runner("sensiml")(
            base_code_dir,
            self.uuid,
            self.task_id,
            device_conf.get("debug", False),
            self.platform,
            self.device_config,
        )

        self.docker_libtensorflow = get_docker_runner("tensorflow")(
            base_code_dir,
            self.uuid,
            self.task_id,
            device_conf.get("debug", False),
            self.platform,
            self.device_config,
        )

        self.add_c_files = []
        self.add_user_generated_c_files = set()
        self.class_map = self.build_class_map()
        self.external_library_files = []
        if self.build_type == "bin" and not self.platform.can_build_binary:
            raise InvalidConfigurationException(
                "\nBinary downloads are not supported for this Platform."
            )

    @property
    def execution_parameters(self):
        return self.platform.execution_parameters

    @property
    def platform_name(self):
        return self.platform.name

    @property
    def platform_version(self):
        return self.platform.version

    @property
    def target_processor(self):
        return self.platform.target_processor

    @property
    def has_classification_limit(self):
        return self.device_config.get("has_classification_limit", False)

    def build_class_map(self):
        class_map = {}
        for name, model in self.knowledgepacks.items():
            class_map[name] = (
                model["knowledgepack"].class_map
                if model["knowledgepack"].class_map
                else {}
            )
            class_map[name]["0"] = "Unknown"
        return class_map

    def is_tensorflow(self, classifier_types):
        if "TF Micro" in classifier_types:
            return True

        if "TensorFlow Lite for Microcontrollers" in classifier_types:
            return True

        return False

    def ensure_path_exists(self, dir_path):
        if os.path.exists(dir_path):
            rmtree(dir_path)
        os.mkdir(dir_path)

    def generate(self, build_type="lib"):
        pass

    def log_debug(self, debug_str, debug_vars=None):
        if debug_vars is None:
            return 'printf("{}]\\\\n");'.format(debug_str)

        if not isinstance(debug_vars, list):
            debug_vars = [debug_vars]
        return 'printf("{}\\\\n",{});'.format(debug_str, ",".join(debug_vars))

    def generate_directories(self, outdir):
        for directory in ["libsensiml", "application"]:
            dir_path = os.path.join(outdir, directory)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
