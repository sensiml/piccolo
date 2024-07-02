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

from codegen.knowledgepack_base import KnowledgePackCodeGeneratorBase
from datamanager.exceptions import KnowledgePackGenerationError
from datamanager.utils import ensure_path_exists
from django.conf import settings
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class GCCGenericCodeGenerator(KnowledgePackCodeGeneratorBase):
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
        super(GCCGenericCodeGenerator, self).__init__(
            knowledgepacks, uuid, task_id, device_conf, build_type
        )
        self.kb_generated_files = ["Makefile"]
        self.test_data = test_data
        self.target_os = target_os

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

        kb_models = self.update_tensor_arena_size(kb_models, size=100000)
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
            self.kb_generated_files.append("testdata.h")
            kb_data["use_test_data"] = ["#define SML_USE_TEST_DATA"]

        elif (
            build_type == "bin"
            and self.application == "AI Model Runner"
            and self.test_data is None
        ):
            raise KnowledgePackGenerationError(
                "Test data required for this application"
            )

        if self.is_tensorflow(classifier_types):
            self.external_library_files += [
                (
                    os.path.join("libsensiml", "libtensorflow-microlite.a"),
                    "libsensiml/libtensorflow-microlite.a",
                )
            ]
            self.kb_generated_files.append("micro_api.h")

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

    def recognize(self, build_type="recognize"):
        kp_base_dir = "{0}/{1}".format(settings.SERVER_CODEGEN_ROOT, self.uuid)

        self.generate(build_type=build_type)

        return self.parse_recognize(kp_base_dir)

    def parse_recognize(self, base_dir):
        classifications = {}
        segment_id = 0

        if not os.path.exists(os.path.join(base_dir, "recognize.txt")):
            raise Exception(
                "Knowledge Pack failed to produce results. Submit a support ticket and reference this KnowledgePack UUID {uuid}".format(
                    uuid=self.uuid
                )
            )

        with open(os.path.join(base_dir, "recognize.txt"), "r") as fid:
            for _, line in enumerate(fid.readlines()):
                if "NumModels" in line:
                    model_map = json.loads(line)
                elif "FeatureVector" in line:
                    results = json.loads(line)
                    results["SegmentID"] = segment_id
                    results["ModelName"] = model_map[str(results["ModelNumber"])]
                    classifications[segment_id] = results
                    segment_id += 1

        logger.info(
            {
                "message": "parsing results",
                "data": classifications,
                "log_type": "datamanager",
            }
        )
        df_original = DataFrame([v for k, v in classifications.items()])

        if len(df_original) == 0:
            return {"results": {}}

        df_original["SegmentEnd"] = (
            df_original.SegmentStart + df_original.SegmentLength - 1
        )

        df_indexes = (
            df_original.groupby("SegmentEnd", sort=True)["SegmentID"].transform(max)
            == df_original["SegmentID"]
        )
        df_ordered = df_original[df_indexes].copy()
        df_ordered.reset_index(drop=True, inplace=True)
        if "Classification" in df_ordered:
            result_type = "classification"
            df_ordered["ClassificationName"] = df_ordered[
                ["ModelName", "Classification"]
            ].apply(
                lambda x: (
                    self.class_map[x[0]][str(x[1])]
                    if self.class_map.get(x[0])
                    else self.class_map[int(x[0])][str(x[1])]
                ),
                axis=1,
            )
        else:
            result_type = "regression"
        df_ordered["SegmentID"] = range(len(df_ordered))
        df_ordered.drop("ModelNumber", axis=1, inplace=True)

        return {
            "results": df_ordered.to_dict(orient="records"),
            "result_type": {"model_type": result_type},
        }

    def create_compile_flags(self):
        # TODO: These should be read as execution params for CFLAGS< LDFLAGS, etc instead of fill files,
        # TODO: make the make files more generic so they are easier to maintain
        # TODO: These options should be settable by the user
        ret = {}
        ret["readme_compile_string"] = (
            "`gcc main.c -o a.out -L../libsensiml -lsensiml -lm -I../libsensiml`"
        )
        return ret

    def update_tensor_arena_size(self, kb_models, size=100000):
        for model in kb_models:
            if isinstance(model["model_arrays"], dict):
                if model["model_arrays"].get("tensor_arena_size") is not None:
                    model["model_arrays"]["tensor_arena_size"] = size

        return kb_models
