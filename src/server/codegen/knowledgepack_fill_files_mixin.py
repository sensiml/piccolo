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
import re
from shutil import copyfile, copytree

from datamanager.exceptions import KnowledgePackGenerationError
from datamanager.datastore import get_datastore
from django.conf import settings
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


class FillFilesMixin(object):
    def fill_kb_files(
        self, output_data, out_dir, classifier_types, libfolder="libsensiml"
    ):
        self.fill_library_files(output_data, os.path.join(out_dir, libfolder))
        self.fill_custom_user_library_files(
            output_data, os.path.join(out_dir, libfolder)
        )
        self.fill_common_files(output_data, os.path.join(out_dir, libfolder))
        self.fill_classifier(
            output_data, out_dir, classifier_types, libfolder=libfolder
        )

    def fill_template_files(self, output_data, out_dir, libfolder="libsensiml"):
        self.fill_files(
            self.kb_generated_files,
            os.path.join(
                settings.CODEGEN_PLATFORM_DIR,
                *self.platform.codegen_file_location,
                libfolder
            ),
            output_data,
            os.path.join(out_dir, libfolder),
        )

    def fill_files(self, files, file_dir, output_data, out_dir, overwrite=True):
        for file_name in files:
            if not os.path.exists(os.path.join(file_dir, file_name)):
                continue
            if os.path.isdir(os.path.join(file_dir, file_name)):
                continue
            if not overwrite and os.path.exists((os.path.join(out_dir, file_name))):
                continue
            if file_name[-2:] == ".a":
                copyfile(
                    os.path.join(file_dir, file_name), os.path.join(out_dir, file_name)
                )
                continue
            with open(os.path.join(file_dir, file_name), "r") as b:
                output_str = b.read()
            for key in output_data.keys():
                if "FILL_{}".format(key.upper()) in output_str:
                    if isinstance(output_data.get(key), list):

                        output_str = re.sub(
                            r"// FILL_{}\b".format(key.upper()),
                            "\n".join(output_data.get(key)),
                            output_str,
                        )
                    elif isinstance(output_data.get(key), str):
                        try:
                            output_str = re.sub(
                                r"// FILL_{}\b".format(key.upper()),
                                output_data.get(key),
                                output_str,
                            )
                        except Exception:
                            output_str = output_str.replace(
                                r"// FILL_{}".format(key.upper()), output_data.get(key)
                            )
                    else:
                        raise Exception("Invalid output data format")

            # Write the file back out
            with open(os.path.join(out_dir, file_name), "w+") as out:
                out.write(output_str)

    def fill_custom_user_library_files(self, output_data, out_dir):

        for transform in self.add_user_generated_c_files:

            datastore = get_datastore(
                folder=os.path.join(
                    "custom_transforms", str(transform.library_pack.uuid)
                )
            )
            if datastore.is_remote:
                local_code_dir = os.path.join(
                    settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                    str(transform.library_pack.uuid),
                )
                file_path = os.path.join(
                    local_code_dir, transform.customtransform.file_path
                )

                datastore.get(
                    key=transform.customtransform.file_path, file_path=file_path
                )

            filepath = os.path.join(
                settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                str(transform.library_pack.uuid),
                transform.customtransform.file_path,
            )

            copyfile(filepath, os.path.join(out_dir, transform.c_file_name))

    def fill_library_files(self, output_data, out_dir):
        transcode_src_files = [
            f
            for f in os.listdir(
                os.path.join(settings.CODEGEN_C_FUNCTION_LOCATION, "src")
            )
            if not f.startswith("sg_")
            and not f.startswith("fg_")
            and not f.startswith("tr_")
        ]
        transcode_src_files.extend(self.add_c_files)

        transcode_include_files = os.listdir(
            os.path.join(settings.CODEGEN_C_FUNCTION_LOCATION, "include")
        )

        self.fill_files(
            transcode_src_files,
            os.path.join(settings.CODEGEN_C_FUNCTION_LOCATION, "src"),
            output_data,
            out_dir,
        )

        self.fill_files(
            transcode_include_files,
            os.path.join(settings.CODEGEN_C_FUNCTION_LOCATION, "include"),
            output_data,
            out_dir,
        )

    def fill_common_files(self, output_data, out_dir):
        files = [
            f for f in os.listdir(os.path.join(settings.CODEGEN_SUPPORT_DIR, "common"))
        ]

        self.fill_files(
            files,
            os.path.join(settings.CODEGEN_SUPPORT_DIR, "common"),
            output_data,
            out_dir,
        )

    def copy_application_files(self, output_data, application, out_dir):

        application_dir = os.path.join(
            settings.CODEGEN_PLATFORM_DIR,
            *self.platform.codegen_file_location,
            self.platform.codegen_app_location(application)
        )

        if not os.path.isdir(application_dir):
            raise KnowledgePackGenerationError(
                "Application does not exist for that platform."
            )

        for project_dir in os.listdir(application_dir):
            copy_to = os.path.join(out_dir, project_dir)
            if os.path.isdir(os.path.join(application_dir, project_dir)):
                copytree(os.path.join(application_dir, project_dir), copy_to)
                self.fill_directory_files(copy_to, output_data)
            else:
                copyfile(os.path.join(application_dir, project_dir), copy_to)
                self.fill_files([project_dir], out_dir, output_data, out_dir)

    def copy_common_application_files(self, output_data, out_dir):

        common_dir = os.path.join(
            settings.CODEGEN_PLATFORM_DIR,
            *self.platform.codegen_file_location,
            "..",
            "common"
        )

        if os.path.isdir(common_dir):
            for common_project_dir in os.listdir(common_dir):
                copy_to = os.path.join(out_dir, common_project_dir)
                if os.path.isdir(os.path.join(common_dir, common_project_dir)):
                    copytree(os.path.join(common_dir, common_project_dir), copy_to)
                    self.fill_directory_files(copy_to, output_data)
                else:
                    copyfile(os.path.join(common_dir, common_project_dir), copy_to)
                    self.fill_files([project_dir], out_dir, output_data, out_dir)

    def copy_external_lib_files(self, out_dir):
        """Copies all files in self.external_library_files to out_dir
        external_library_files should be a list of tuples
        [
            (file_path_from_codgen_location, file_path_to_copy_to_from_kb_base_dir),
            ...
        ]"""

        for file_path, file_name in self.external_library_files:
            copyfile(
                os.path.join(
                    settings.CODEGEN_PLATFORM_DIR,
                    *self.platform.codegen_file_location,
                    file_path
                ),
                os.path.join(out_dir, file_name),
            )

    def fill_directory_files(self, src_dir, output_data):
        src_files = [
            f
            for f in os.listdir(src_dir)
            if not os.path.isdir(os.path.join(src_dir, f))
        ]

        self.fill_files(src_files, src_dir, output_data, src_dir)

    def fill_classifier(
        self, output_data, out_dir, classifier_types, libfolder="libsensiml"
    ):
        if "PME" in classifier_types:
            self.fill_classifier_support(
                output_data, os.path.join(out_dir, libfolder), "pme"
            )
            self.fill_trained_models(
                output_data, os.path.join(out_dir, libfolder), "pme"
            )

        if "Decision Tree Ensemble" in classifier_types:
            self.fill_classifier_support(
                output_data, os.path.join(out_dir, libfolder), "tree_ensemble"
            )
            self.fill_trained_models(
                output_data, os.path.join(out_dir, libfolder), "tree_ensemble"
            )

        if "Boosted Tree Ensemble" in classifier_types:
            self.fill_classifier_support(
                output_data, os.path.join(out_dir, libfolder), "boosted_tree_ensemble"
            )
            self.fill_trained_models(
                output_data, os.path.join(out_dir, libfolder), "boosted_tree_ensemble"
            )

        if "Bonsai" in classifier_types:
            self.fill_classifier_support(
                output_data, os.path.join(out_dir, libfolder), "bonsai"
            )
            self.fill_trained_models(
                output_data, os.path.join(out_dir, libfolder), "bonsai"
            )

        if "Linear Regression" in classifier_types:
            self.fill_classifier_support(
                output_data, os.path.join(out_dir, libfolder), "linear_regression"
            )
            self.fill_trained_models(
                output_data, os.path.join(out_dir, libfolder), "linear_regression"
            )

        if self.is_tensorflow(classifier_types):
            if self.nn_inference_engine == "nnom":
                self.fill_classifier_support(
                    output_data, os.path.join(out_dir, libfolder), "nnom_middleware"
                )
                #self.fill_trained_models(
                #    output_data, os.path.join(out_dir, libfolder), "nnom_middleware"
                #)

            if self.nn_inference_engine == "tf_micro":
                self.fill_classifier_support(
                    output_data, os.path.join(out_dir, libfolder), "tf_micro"
                )
                self.fill_trained_models(
                    output_data, os.path.join(out_dir, libfolder), "tf_micro"
                )

    def fill_classifier_support(self, output_data, out_dir, classifier_type):
        file_dir = os.path.join(
            settings.CODEGEN_C_FUNCTION_LOCATION, "classifiers", classifier_type
        )

        files = [f for f in os.listdir(file_dir) if f[-2:] in [".c", ".h"]]

        self.fill_files(files, file_dir, output_data, out_dir)

        if self.target_processor.architecture.name == "x86":
            self.fill_classifier_dsp_support(output_data, out_dir, classifier_type)

    def fill_classifier_dsp_support(self, output_data, out_dir, classifier_type):

        file_dir = os.path.join(
            settings.CODEGEN_C_FUNCTION_LOCATION,
            "classifiers",
            classifier_type,
            "arm_dsp",
        )

        if not os.path.exists(file_dir):
            return

        files = [f for f in os.listdir(file_dir) if f[-2:] in [".c", ".h"]]

        self.fill_files(files, file_dir, output_data, out_dir)

    def fill_trained_models(self, output_data, out_dir, classifier_type):
        file_dir = os.path.join(
            settings.CODEGEN_SUPPORT_DIR, "trained_classifiers", classifier_type
        )
        files = [f for f in os.listdir(file_dir)]

        self.fill_files(files, file_dir, output_data, out_dir)

    def fill_build_files(self, output_data, out_dir):

        # Fill build file first
        self.fill_files(
            self.build_files,
            os.path.join(settings.CODEGEN_PLATFORM_DIR, "..", "build"),
            output_data,
            out_dir,
        )

        # Overwrite with platform specific build files
        self.fill_files(
            self.build_files,
            os.path.join(
                settings.CODEGEN_PLATFORM_DIR, *self.platform.codegen_file_location
            ),
            output_data,
            out_dir,
        )

    def generate_directories(self, outdir, libfolder="libsensiml"):
        for directory in [libfolder, self.application]:
            dir_path = os.path.join(outdir, directory)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
