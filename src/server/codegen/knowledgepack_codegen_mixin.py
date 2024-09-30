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

from codegen.knowledgepack_codegen_train_mixin import TrainMixin
from codegen.knowledgepack_device_command_mixin import sensor_macro_from_plugin_name
from codegen.model_gen.model_gen import ModelGen
from codegen.utils import c_line, c_line_nr, c_model_name, uuid_str_to_c_array
from django.conf import settings
from logger.log_handler import LogHandler

model_gen = ModelGen()
logger = LogHandler(logging.getLogger(__name__))


FEATURE_GENERATOR_CALL = "int32_t {function_name}(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);"


class CodeGenMixin(TrainMixin):
    """Codegen Mixin is responsible for taking a model graph dictionary and generating FILL_XXX dictionary
    that contains c code that can be directly inserted into our template files

    kb_data - a dictionary containing key:value pairs where the keys are the
    name of a fill in the templates and the values is generated c code

    """

    def codegen(self, kb_models, model_groups):
        classifier_types = set()

        for model in kb_models:
            classifier_types.add(model["classifier_config"]["classifier"])
            self.platform.execution_parameters["sample_rate"] = (
                self.get_model_sample_rate(model)
            )
            self.platform.execution_parameters.update(self.get_model_ranges(model))
            self.platform.execution_parameters.update(
                self.get_model_enabled_sensors(model)
            )

        kb_data = dict()

        kb_data["embedded_sdk_license"] = settings.EMBEDDED_SDK_LICENSE
        kb_data["makefile_library_name_main"] = (
            f"MAIN = $(OUT)/{settings.KNOWLEDGEPACK_LIBRARY_NAME}.a"
        )
        kb_data["makefile_dll_library_name_main"] = (
            f"MAIN = $(OUT)/{settings.KNOWLEDGEPACK_LIBRARY_NAME}.dll"
        )

        # Get the Total model count.

        kb_data["model_count"] = [
            "#define TOTAL_NUMBER_OF_MODELS {}".format(len(kb_models))
        ]

        # combine model specific information to get generated c code strings

        kb_data["debug"] = self.create_debug_flagging()
        kb_data["use_profiler"] = self.create_profiler_includes()

        # Build kb_model data structure information and other global type information
        kb_data["model_function_defs"] = self.create_model_function_definitions(
            kb_models
        )
        kb_data["kb_models"] = self.create_kb_models(kb_models)
        kb_data["kb_model_indexes"] = self.create_kb_model_indexes(kb_models)
        kb_data["model_map"] = self.create_kb_model_map(kb_models)
        kb_data["model_class_map"] = self.create_kb_model_class_map(kb_models)
        kb_data["pipeline_data_structures"] = self.create_pipeline_data_structures(
            kb_models
        )
        kb_data["ring_buffer_init_sizes"] = self.create_ring_buffer_init_size(kb_models)
        kb_data["temp_data"] = self.create_temp_data_length(kb_models)

        # Handle converting incoming sensor streams into data columns
        kb_data["number_of_sensors"] = self.create_number_of_sensors(kb_models)
        kb_data["kb_data_streaming"] = self.create_data_streaming(kb_models)
        kb_data["sensor_column_names"] = self.create_combine_model_data(
            kb_models, "sensor_column_names"
        )
        kb_data["data_column_names"] = self.create_combine_model_data(
            kb_models, "data_column_names"
        )

        kb_data["segmenter_parameters"] = self.create_combine_model_data(
            kb_models, "segmenter_parameters"
        )
        kb_data["segment_filter_reset"] = self.create_combine_model_data(
            kb_models, "segment_filter_reset"
        )
        kb_data["segmenter_reset"] = self.create_segmenter_reset(kb_models)
        kb_data["segmenter_typedef"] = self.create_segmenter_typedef(kb_models)
        kb_data["kb_data_segmentation"] = self.create_data_segmentation(kb_models)

        # Extract Features from the segment of data
        kb_data["max_feature_selection"] = self.create_max_feature_selection()
        kb_data["max_vector_size"] = self.create_max_vector_size(kb_models)
        kb_data["max_ringbuffers_used"] = self.create_max_ringbuff_size(kb_models)
        kb_data["kb_feature_generators"] = self.create_kb_feature_gen(kb_models)
        kb_data["feature_vector_size"] = self.create_feature_vector_size(kb_models)
        kb_data["kb_feature_transforms"] = self.create_feature_transform_calls(
            kb_models
        )

        # Generate Classifier Trained Models and Temp Parameters Settings
        kb_data.update(self.create_classifier_structures(classifier_types, kb_models))

        kb_data["classification_result_info"] = (
            self.create_sml_classification_result_info(kb_models)
        )

        kb_data["classification_result_info_print"] = (
            self.create_sml_classification_result_print_info(kb_models)
        )

        # CLASSIFIER INIT AND INCLUDE FILLS
        kb_data["kb_classifiers"] = self.create_classifier_calls(kb_models)
        kb_data["kb_classifier_inits"] = self.create_kb_classifier_init(
            classifier_types
        )
        kb_data["kb_classifier_includes"] = self.create_kb_classifier_headers(
            classifier_types
        )
        kb_data["classifier_header_calls"] = (
            self.create_kb_classifier_header_calls_only(classifier_types)
        )

        # ON DEVICE MODEL MANIPULATION
        kb_data["add_last_pattern"] = self.create_kb_add_last_pattern(kb_models)
        kb_data["add_custom_pattern"] = self.create_kb_add_custom_pattern(kb_models)
        kb_data["score_model"] = self.create_kb_score_model(kb_models)
        kb_data["retrain_model"] = self.create_kb_retrain_model(kb_models)
        kb_data["print_model_score"] = self.create_kb_print_model_score(kb_models)
        kb_data["flush_model"] = self.create_kb_flush_model(kb_models)
        kb_data["get_model_header"] = self.create_kb_get_model_header(kb_models)
        kb_data["get_model_pattern"] = self.create_kb_get_model_pattern(kb_models)

        # IDENTIFYING INFORMATION
        kb_data["ble_version_num"] = self.create_ble_app_version_str()
        kb_data["model_json"] = self.create_kb_model_json(kb_models)
        kb_data["model_json_h"] = self.create_kb_model_json_h(kb_models)

        kb_data["starter_edition_check_define"] = self.create_starter_check_define()
        if self.platform.execution_parameters.get("uses_sensiml_interface", False):
            sis_config_list = self.create_sis_configuration_list(kb_models)
            # this is MQTT / SensiML interface spec
            kb_data["sensiml_interface_sensor_config"] = sis_config_list
            # First and last lines don't count in structure definition.
            kb_data["sensiml_interface_config_num_msgs"] = (
                self.create_sis_configuration_count(sis_config_list)
            )

        kb_data["custom_feature_generators"] = (
            self.create_custom_feature_generator_header_include()
        )

        kb_data["tensorflow_build_flags"] = self.create_tensorflow_build_flags(
            kb_models
        )

        # TODO: only adds a single binary?
        self.docker_libtensorflow.model_binary = self.create_kb_model_tf_micro_binary(
            kb_models
        )

        # Describes how the models should be run
        kb_data.update(self.create_run_model_call(kb_models, model_groups))

        logger.debug(
            {
                "message": "kb data keys",
                "data": list(kb_data.keys()),
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        return kb_data, classifier_types

    def create_tensorflow_build_flags(self, models):
        tf_micro_cflags = """
ifeq ($(BUILD_TENSORFLOW), y)
    LDLIBS += -ltensorflow-microlite
    CFLAGS += -DTF_LITE_STATIC_MEMORY -DNDEBUG -DGEMMLOWP_ALLOW_SLOW_SCALAR_FALLBACK -DTF_LITE_STATIC_MEMORY
endif
"""
        for model in models:
            if self.is_tensorflow(model["classifier_config"]["classifier"]):
                if self.nn_inference_engine == "nnom":
                    #TODO: NNoM
                    pass

                if self.nn_inference_engine == "tf_micro":
                    return tf_micro_cflags


        return ""

    def create_kb_model_tf_micro_binary(self, models):
        for model in models:
            if self.is_tensorflow(model["classifier_config"]["classifier"]):
                if self.nn_inference_engine == "nnom":
                    #TODO: NNoM
                    pass

                if self.nn_inference_engine == "tf_micro":
                    return model["model_arrays"]["tflite"]

    def create_sml_classification_result_info(self, models_data):
        model_fill = {}
        model_fill["TF Micro"] = (
            "{\n\ttf_micro_model_results_object(kb_models[model_index].classifier_id, (model_results_t *)model_results);\n}"
        )
        model_fill["TensorFlow Lite for Microcontrollers"] = (
            "{\n\ttf_micro_model_results_object(kb_models[model_index].classifier_id, (model_results_t *)model_results);\n}"
        )

        model_fill["Decision Tree Ensemble"] = (
            "{\n\ttree_ensemble_model_results_object(kb_models[model_index].classifier_id, (model_results_t *)model_results);\n}"
        )

        return self.create_case_fill_template_classifier_type(models_data, model_fill)

    def create_sml_classification_result_print_info(self, models_data):
        model_fill = {}
        model_fill[
            "TensorFlow Lite for Microcontrollers"
        ] = """{
               sml_classification_result_info(model_index, &model_result);\n
               pbuf += sprintf(pbuf, ",\\"ModelDebug\\":[");
               for (int32_t i=0; i<model_result.num_outputs; i++)
               {
                 pbuf += sprintf(pbuf, "%f, ", model_result.output_tensor[i]);
               }
               pbuf += sprintf(pbuf, "]");
                }

            """

        return self.create_case_fill_template_classifier_type(models_data, model_fill)

    def create_classifier_structures(self, classifier_types, kb_models):
        tmp_data = {}

        formated_classifier_types = [
            x.lower().replace(" ", "_") for x in classifier_types
        ]

        formated_classifier_types = [
            x if x != "tensorflow_lite_for_microcontrollers" else "tf_micro"
            for x in formated_classifier_types
        ]

        logger.debug(
            {
                "message": "CLASSIFIER TYPE INFORMATION",
                "data": formated_classifier_types,
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        tmp_data["model_results_info_init"] = []

        for classifier in formated_classifier_types:
            tmp_data[f"{classifier}_classifier_structs"] = (
                model_gen.create_classifier_structures(classifier, kb_models)
            )
            tmp_data[f"{classifier}_max_tmp_parameters"] = (
                model_gen.create_max_tmp_parameters(classifier, kb_models)
            )
            tmp_data[f"{classifier}_trained_model_header"] = (
                model_gen.create_trained_model_header_fills(classifier, kb_models)
            )
            tmp_data.update(
                model_gen.create_direct_model_updates(classifier, kb_models)
            )

        return tmp_data

    def get_classifier_type_map(self, classifier_config):
        # PME is here for backwards compatibility, but most models should have a classifier type by now
        classifier_type = classifier_config.get("classifier", "PME")
        if classifier_type in ["PME"]:
            return 1
        elif classifier_type in ["Decision Tree Ensemble"]:
            return 2
        elif classifier_type in ["Boosted Tree Ensemble"]:
            return 3
        elif classifier_type in ["Bonsai"]:
            return 4
        elif classifier_type in ["TF Micro", "TensorFlow Lite for Microcontrollers", "Neural Network"]:
            return 5
        elif classifier_type in ["Linear Regression"]:
            return 6
        else:
            raise Exception(f"{classifier_type} not supported Classifier Type for code generation")

    def create_debug_flagging(self):
        ret = []
        if self.device_config.get("debug", None):
            debug_level = self.device_config.get("debug_level", 1)
            profile = 0 if self.device_config.get("profile", False) is False else 1
            if debug_level not in [1, 2, 3, 4]:
                raise Exception("Invalid Debug Level")
            ret = [
                "#define SML_DEBUG 1",
                "#define KB_LOG_LEVEL {}".format(debug_level),
                "#define SML_PROFILER {}".format(profile),
            ]
        return ret

    def create_kb_classifier_headers(self, classifier_types):
        output = []

        if "PME" in classifier_types:
            output.append('#include "pme.h"')
            output.append('#include "pme_trained_neurons.h"')

        if "Decision Tree Ensemble" in classifier_types:
            output.append('#include "tree_ensemble.h"')
            output.append('#include "tree_ensemble_trained_models.h"')

        if "Boosted Tree Ensemble" in classifier_types:
            output.append('#include "boosted_tree_ensemble.h"')
            output.append('#include "boosted_tree_ensemble_trained_models.h"')

        if "Bonsai" in classifier_types:
            output.append('#include "bonsai.h"')
            output.append('#include "bonsai_trained_models.h"')

        if self.is_tensorflow(classifier_types):
            if self.nn_inference_engine == "nnom":
                output.append('#include "nnom.h"')
                output.append('#include "nnom_middleware.h"')

            if self.nn_inference_engine == "tf_micro":
                output.append('#include "tf_micro.h"')
                output.append('#include "tf_micro_trained_models.h"')

        if "Linear Regression" in classifier_types:
            output.append('#include "linear_regression.h"')
            output.append('#include "linear_regression_trained_models.h"')

        return output

    def create_kb_classifier_header_calls_only(self, classifier_types):
        output = []

        if "PME" in classifier_types:
            output.append('#include "pme.h"')

        if "Decision Tree Ensemble" in classifier_types:
            output.append('#include "tree_ensemble.h"')

        if "Boosted Tree Ensemble" in classifier_types:
            output.append('#include "boosted_tree_ensemble.h"')

        if "Bonsai" in classifier_types:
            output.append('#include "bonsai.h"')

        if self.is_tensorflow(classifier_types):
            if self.nn_inference_engine == "nnom":
                #TODO: NNoM
                pass

            if self.nn_inference_engine == "tf_micro":
                output.append('#include "tf_micro.h"')

        if "Linear Regression" in classifier_types:
            output.append('#include "linear_regression.h"')

        return output

    def create_kb_classifier_init(self, classifier_types):
        output = []

        if "PME" in classifier_types:
            output.append(
                c_line(
                    1, "pme_simple_init(kb_classifier_rows, KB_NUM_PME_CLASSIFIERS);"
                )
            )

        if "Decision Tree Ensemble" in classifier_types:
            output.append(
                c_line(1, "tree_ensemble_init(tree_ensemble_classifier_rows, 0);")
            )

        if "Boosted Tree Ensemble" in classifier_types:
            output.append(
                c_line(
                    1,
                    "boosted_tree_ensemble_init(boosted_tree_ensemble_classifier_rows, 0);",
                )
            )

        if "Bonsai" in classifier_types:
            output.append(c_line(1, "bonsai_init(bonsai_classifier_rows, 0);"))

        if self.is_tensorflow(classifier_types):
            if self.nn_inference_engine == "nnom":
                output.append(c_line(1, "nnom_init(tf_micro_classifier_rows, 0);"))                

            if self.nn_inference_engine == "tf_micro":
                output.append(c_line(1, "tf_micro_init(tf_micro_classifier_rows, 0);"))

        if "Linear Regression" in classifier_types:
            output.append(
                c_line(1, "linear_regression_init(linear_regression_rows, 0);")
            )

        return output

    def create_classifier_calls(self, models_data):
        output_str = ""
        for index, model in enumerate(models_data):
            output_str += f"\nint32_t recognize_vector_{index}(void * model)\n"
            output_str += c_line(0, "{")
            output_str += c_line(1, "int32_t ret;")
            output_str += c_line(1, "kb_model_t * kb_model = (kb_model_t*)model;")

            if self.platform.profiling_enabled:
                profile_str = self.get_profile_start()
                for line in profile_str:
                    output_str += c_line(3, line)

            if model["classifier_config"].get("classifier", "PME") in ["PME"]:
                output_str += c_line(
                    1,
                    "ret = pme_simple_submit_pattern(kb_model->classifier_id, kb_model->pfeature_vector, kb_model->pmodel_results);",
                )

            elif model["classifier_config"]["classifier"] == "Decision Tree Ensemble":
                output_str += c_line(
                    1,
                    "ret = tree_ensemble_simple_submit(kb_model->classifier_id, kb_model->pfeature_vector, kb_model->pmodel_results);",
                )

            elif model["classifier_config"]["classifier"] == "Boosted Tree Ensemble":
                output_str += c_line(
                    1,
                    "ret = boosted_tree_ensemble_simple_submit(kb_model->classifier_id, kb_model->pfeature_vector, kb_model->pmodel_results);",
                )

            elif model["classifier_config"]["classifier"] == "Bonsai":
                output_str += c_line(
                    1,
                    "ret = bonsai_simple_submit(kb_model->classifier_id, kb_model->pfeature_vector, kb_model->pmodel_results);",
                )

            elif model["classifier_config"]["classifier"] == "Linear Regression":
                output_str += c_line(
                    1,
                    "ret = linear_regression_simple_submit(kb_model->classifier_id, kb_model->pfeature_vector, kb_model->pmodel_results);",
                )

            elif model["classifier_config"]["classifier"] in [
                "TF Micro",
                "TensorFlow Lite for Microcontrollers",
                "Neural Network"
            ]:
                if self.nn_inference_engine=='tf_micro':
                    output_str += c_line(
                        1,
                        "ret = tf_micro_simple_submit(kb_model->classifier_id, kb_model->pfeature_vector, kb_model->pmodel_results);",
                    )
                if self.nn_inference_engine=='nnom':
                        output_str += c_line(
                        1,
                        "ret = nnom_simple_submit(kb_model->classifier_id, kb_model->pfeature_vector, kb_model->pmodel_results);",
                    )
            else:
                raise Exception("Classifier is not supported for codegeneration.")

            if self.platform.profiling_enabled:
                profile_str = self.get_profile_classifier_stop()
                for line in profile_str:
                    output_str += c_line(3, line)

            output_str += c_line(1, "return ret;")
            output_str += c_line(0, "\n}")

        return [output_str]

    def create_custom_feature_generator_header_include(self):
        output = []

        for transform in self.add_user_generated_c_files:
            output.append(
                FEATURE_GENERATOR_CALL.format(function_name=transform.c_function_name)
            )

        return output

    def create_starter_check_define(self):
        if self.has_classification_limit:
            return ["#define STARTER_EDITION_CHECK 1"]
        else:
            return ["#define STARTER_EDITION_CHECK 0"]

    def create_ble_app_version_str(self):
        try:
            execution_params = self.platform.execution_parameters
        except ValueError:
            return [""]
        version = execution_params.get("ble_version", None)
        if version is None:
            return [""]
        else:
            return ["{}".format(version)]

    def create_arm_cpu_flags(self):
        ret = {}
        ret["readme_compile_string"] = self.platform.get_compile_string()

        float_str, float_hw, float_spec = self.platform.get_float_specs()

        cpu = self.platform.get_cpu_flag()
        if cpu is not None:
            ret["cpu_type"] = ["CPU_TYPE={}".format(cpu)]
        if float_hw is not None:
            ret["float_hardware"] = ["FLOAT_HARDWARE={}".format(float_hw)]
        if float_spec is not None:
            ret["float_type"] = ["FLOAT_TYPE={}".format(float_spec)]
        if float_str is not None:
            ret["float_string"] = float_str

        return ret

    def create_test_data_debugger(self, test_data, sensors):
        test_data_h = ["#define USE_TEST_RAW_SAMPLES"]
        test_data_h.append("#define TD_NUMROWS {}".format(len(test_data)))
        test_data_h.append("#define TD_NUMCOLS {}".format(len(sensors)))
        test_data_h.append("const short testdata[TD_NUMROWS][TD_NUMCOLS] = ")
        test_data_h.append("{")
        num_sensors = len(sensors)

        format_str = "{{" + "{}," * num_sensors + "}},"
        test_data_h.extend(
            [format_str.format(*x) for x in test_data[sensors].astype(int).values[:-1]]
        )

        test_data_h.append(format_str.format(*test_data.iloc[-1].astype(int).values))

        test_data_h.append("};")

        return {"test_data_h": test_data_h}

    def create_max_vector_size(self, models):
        feature_vector_size = 0
        for model in models:
            feature_vector_size = max(
                feature_vector_size, model.get("feature_vector_size")
            )

        return ["#define MAX_VECTOR_SIZE {0}".format(feature_vector_size)]

    def create_max_ringbuff_size(self, models):
        num_rbuffs = 0
        for model in models:
            num_rbuffs = max(num_rbuffs, model.get("number_of_ringbuffs"))

        return ["#define MAX_RINGBUFFERS_USED {0}".format(num_rbuffs)]

    def create_run_model_call(self, models, model_groups):
        """creates the subsegment call for model"""

        def build_run_call(models, model_name, data="(int16_t *)data", index=0):
            model = get_model_by_name(models, model_name)
            output = []

            if model.get("cascade_reset", None) in [True, False]:
                # If there is a parent model and we have cascade windowing, we'll need to run model multiple times
                # in order to get all the features and return a classification

                if model["cascade_reset"] == True:
                    call = "kb_run_model_with_cascade_reset"
                else:
                    call = "kb_run_model_with_cascade_features"

                if model.get("parent", None) is None:
                    output.append(c_line_nr(2 + index, "ret=-2;"))
                    output.append(
                        c_line_nr(
                            2 + index,
                            "ret = {call}({data}, num_sensors, {model_name});".format(
                                call=call,
                                data=data,
                                model_name=c_model_name(model["name"]),
                            ),
                        )
                    )
                else:
                    output.append(
                        c_line_nr(
                            2 + index,
                            "ret = kb_generate_classification({model_name});".format(
                                model_name=c_model_name(model["name"])
                            ),
                        )
                    )
            else:
                output.append(
                    c_line_nr(
                        2 + index,
                        "ret = kb_run_model({}, num_sensors, {});".format(
                            data, c_model_name(model["name"])
                        ),
                    )
                )
            output.append(c_line_nr(2 + index, "if (ret >= 0){"))

            if (
                model["results"]
                and all(v == "Report" for v in model["results"].values()) == False
            ):
                output.append(c_line_nr(3 + index, "switch(ret){"))
                for classification, submodel in model["results"].items():
                    if submodel != "Report":
                        output.append(
                            c_line_nr(
                                4 + index, "case({}):".format(int(classification))
                            )
                        )
                        output.extend(
                            build_run_call(
                                models, submodel, data="NULL", index=index + 4
                            )
                        )
                        output.append(c_line_nr(4 + index, "break;"))
                    else:
                        output.append(
                            c_line_nr(
                                4 + index, "case({}):".format(int(classification))
                            )
                        )
                        output.append(
                            c_line_nr(
                                4,
                                "sml_output_results({}, ret);".format(
                                    c_model_name(model["name"])
                                ),
                            )
                        )
                        output.append(c_line_nr(4 + index, "break;"))
                output.append(c_line_nr(3, "default :"))
                output.append(
                    c_line_nr(
                        4,
                        "sml_output_results({}, ret);".format(
                            c_model_name(model["name"])
                        ),
                    )
                )
                output.append(c_line_nr(4, "break;"))
                output.append(c_line_nr(3, "};"))
            else:
                output.append(
                    c_line_nr(
                        3 + index,
                        "sml_output_results({}, ret);".format(
                            c_model_name(model["name"])
                        ),
                    )
                )

            output.append(
                c_line_nr(
                    3 + index, "kb_reset_model({});".format(index_lookup[model["name"]])
                )
            )
            # TODO: Figure out a way to make this work for the DCL
            # output.append(
            #     c_line_nr(
            #         3 + index, "return ret;".format(index_lookup[model["name"]])
            #     )
            # )
            output.append(c_line_nr(2 + index, "};"))
            return output

        output = {}

        parents = [parent[0] for parent in model_groups]

        index_lookup = {model["name"]: index for index, model in enumerate(models)}

        output["recognition_flush_model"] = []

        def sanitize_name(name):
            return name.replace(" ", "_").replace("(", "").replace(")", "").lower()

        for index, model in enumerate(models):
            if model["name"] in parents:
                if (
                    output.get(
                        "run_model_{}".format(
                            sanitize_name(model["sensor_plugin_name"])
                        ),
                        None,
                    )
                    is None
                ):
                    output[
                        "run_model_{}".format(
                            sanitize_name(model["sensor_plugin_name"])
                        )
                    ] = []
                output[
                    "run_model_{}".format(sanitize_name(model["sensor_plugin_name"]))
                ].extend(build_run_call(models, model["name"]))

            sensor_plugin_name = model["sensor_plugin_name"].replace(" ", "_").upper()
            self.platform.execution_parameters["sensor_plugin_name"] = (
                sensor_plugin_name
            )
            reset_string = """if ({0}==sensor_id) kb_flush_model_buffer({1});"""
            reset_string = reset_string.format(
                sensor_macro_from_plugin_name(sensor_plugin_name),
                c_model_name(model.get("name", index)),
            )

            output["recognition_flush_model"].append(reset_string)

        return output

    def create_sml_abstraction_calls(self, models):
        sensor_inputs = []
        ret = {}
        for index, model in enumerate(models):
            defined_model_name = c_model_name(model.get("name", index))
            if model["sensor_plugin"].lower() == "motion":
                sensor_inputs.append("motion")
                ret["sml_motion_model_index"] = [
                    "model_idx = {};".format(defined_model_name)
                ]
            elif model["sensor_plugin"].lower() == "audio":
                sensor_inputs.append("audio")
                ret["sml_audio_model_index"] = [
                    "model_idx = {};".format(defined_model_name)
                ]

        output_options = self.device_config.get("output_options", ["ble"])

        sensor_starts = ["sml_{}_start();".format(inp) for inp in sensor_inputs]
        sensor_stops = ["sml_{}_stop();".format(inp) for inp in sensor_inputs]
        sensor_inits = ["sml_{}_init();".format(s_in) for s_in in sensor_inputs]

        os_used = self.device_config.get("application", None)

        if os_used is not None:
            if "freertos" in os_used.lower():
                ret["sensiml_freertos_tasks"] = [
                    "TaskHandle_t {}Task;".format(inp) for inp in sensor_inputs
                ]
                ret["sensiml_freertos_queues"] = [
                    "QueueHandle_t {}Queue;".format(inp) for inp in sensor_inputs
                ]
                ret["freertos_tasks_extern"] = [
                    "extern TaskHandle_t {}Task;".format(inp) for inp in sensor_inputs
                ]
                ret["freertos_queues_extern"] = [
                    "extern QueueHandle_t {}Queue;".format(inp) for inp in sensor_inputs
                ]
                ret["sensor_usages"] = [
                    "#define SENSIML_FREERTOS_USE_{} 1".format(inp.upper())
                    for inp in sensor_inputs
                ]

                queue_str = (
                    r"{0}Queue = xQueueCreate( 10, sizeof( sml_{0}_raw_t ) ); \n"
                )
                queue_str += r"if({0}Queue == NULL) {1} \n"
                queue_str += r'NRF_LOG_ERROR("Could Not create {0} queue!\\r\\n"); \n'
                queue_str += r"return SML_ERR_QUEUE_NULL; \n"
                queue_str += r"{2}"

                ret["freertos_sensor_queue_create"] = [
                    queue_str.format(inp, "{", "}") for inp in sensor_inputs
                ]

                task_str = 'r = xTaskCreate(vSensiML{0}TaskCode, "sm{1}", 128, (void*)NULL, configMAX_PRIORITIES - 1, &{0}Task); \n'
                task_str += "if(r != pdPASS) \n"
                task_str += "{2} \n"
                task_str += 'NRF_LOG_ERROR("Could Not create {0} task!\\\\r\\\\n"); \n'
                task_str += "return SML_ERR_TASK_NULL; \n"
                task_str += "{3}"
                ret["freertos_sensor_task_create"] = [
                    task_str.format(inp, inp[0:2], "{", "}") for inp in sensor_inputs
                ]

        output_funcs = [
            "sml_output_{}(model, classification);".format(out.lower())
            for out in output_options
        ]

        ret["sml_sensor_starts"] = sensor_starts
        ret["sml_sensor_stops"] = sensor_stops
        ret["sml_sensor_inits"] = sensor_inits
        ret["sml_output_functions"] = output_funcs

        return ret

    def create_profiler_includes(self):
        """Create includes for mbed to profile based on time" """
        ret = []
        if self.add_profile_data:
            # THIS is for MBED.
            ret.append('#include "mbed.h"')
            ret.append("Timer profile_timer;")
        else:
            self.kb_generated_files.append("sml_profile_utils.h")
            ret.append('#include "sml_profile_utils.h"')
            ret.append("static uint32_t profile_cycle_count = 0;")
            ret.append("static float profile_total_time = 0.0f;")
            ret.append("static float profile_avg_iter_time = 0.0f;")
        return ret

    def create_sample_rate(self):
        return [
            "#define SAMPLE_RATE {0}".format(
                int(self.device_config.get("sample_rate", 100))
            )
        ]

    def create_combine_model_data(self, models_data, key):
        output_data = []
        for model in models_data:
            output_data.extend(model.get(key))

        return output_data

    def create_feature_vector_size(self, models_data):
        feature_vector_size = []

        iterations = 0
        for model in models_data:
            feature_vector_size.append(
                "#define FEATURE_VECTOR_SIZE_{} ({})".format(
                    iterations, model["feature_vector_size"]
                )
            )
            iterations += 1

        return feature_vector_size

    def create_temp_data_length(self, models_data):
        output_str = "\n"
        temp_data_length = 0
        for model in models_data:
            temp_data_length = max(temp_data_length, model.get("temp_data_length"))

        output_str += "#define SORTED_DATA_LEN {0}".format(temp_data_length)
        output_str += "\nint16_t sortedData[SORTED_DATA_LEN];"

        return [output_str]

    def create_model_function_definitions(self, models_data):
        output_str = ""
        for index, model in enumerate(models_data):
            output_str += (
                f"\nint32_t data_streaming_{index}(void* model, int16_t *pSample);\n"
            )
            output_str += f"\nint32_t data_segmentation_{index}(void* model, int32_t model_index);\n"
            output_str += (
                f"\nint32_t feature_gen_{index}(void * model, int32_t *nfeats);\n"
            )
            output_str += f"\nint32_t feature_transform_{index}(void* model);\n"
            output_str += f"\nint32_t recognize_vector_{index}(void* model);\n"
        return [output_str]

    def create_kb_feature_gen(self, models_data):
        output_str = ""
        for index, model in enumerate(models_data):
            output_str += (
                f"\nint32_t feature_gen_{index}(void * model, int32_t *nfeats)\n"
            )
            output_str += c_line(0, "{")

            output_str += c_line(1, "int32_t column = 0;")
            output_str += c_line(1, "int32_t num_params = 1;")
            output_str += c_line(1, "kb_model_t * kb_model = (kb_model_t*)model;")
            output_str += c_line(1, "int32_t nframes = kb_model->sg_length;")
            output_str += c_line(
                1,
                "int32_t CompIdx = (kb_model->feature_bank_index) * (kb_model->pfeature_bank->bank_size);",
            )

            for key in [
                "segment_transforms",
            ]:
                output_str = "\t\n".join([output_str] + model.get(key))

            for key in [
                "generate_features_calls",
            ]:
                output_str = "\t\n".join([output_str] + model.get(key))

            for key in [
                "segment_filters",
            ]:
                output_str = "\t\n".join([output_str] + model.get(key))

            output_str += c_line(1, "\nreturn 1;\n}")

        return [output_str]

    def create_feature_transform_calls(self, models_data):
        output_str = ""
        for index, model in enumerate(models_data):
            output_str += f"\nint32_t feature_transform_{index}(void * model)\n"
            output_str += c_line(0, "{")
            output_str += c_line(1, "kb_model_t * kb_model = (kb_model_t*)model;")

            for key in ["transforms_feature_vectors"]:
                output_str = "\t\n".join([output_str] + model.get(key))

            output_str += c_line(1, "return 1;")
            output_str += c_line(0, "\n}")

        return [output_str]

    def create_kb_model_json(self, models_data, model_parameters=True):
        model_indexes = {}
        model_descriptions = []

        for index, model in enumerate(models_data):
            model_indexes[index] = model.get("name", index)

            model_description = get_generic_model_description(
                model.get("name", index),
                model.get("class_map"),
                model.get("classifier_config"),
                model.get("feature_summary"),
            )

            if model_parameters:
                if model["classifier_config"].get("classifier", "NULL") == "PME":
                    model_description.update(
                        convert_to_pme_model_to_json_file_format(
                            model["model_arrays"], model["classifier_config"]
                        )
                    )

                model_description["knowledgepack_summary"] = self.knowledgepacks[
                    model_indexes[index]
                ]["knowledgepack"].knowledgepack_summary["recognition_pipeline"]
                model_description["sensors_columns"] = self.knowledgepacks[
                    model_indexes[index]
                ]["sensor_columns"]
                model_description["uuid"] = str(
                    self.knowledgepacks[model_indexes[index]]["knowledgepack"].uuid
                )
            else:
                model_description.pop("FeatureNames")

            model_descriptions.append(model_description)

        output_dict = {
            "NumModels": len(models_data),
            "ModelIndexes": model_indexes,
            "ModelDescriptions": model_descriptions,
        }

        return [json.dumps(output_dict)]

    def create_kb_model_json_h(self, models_data):
        data = self.create_kb_model_json(models_data, model_parameters=False)[0]

        return '{"' + data.replace(" ", "").replace('"', '\\"').replace(" ", "") + '"};'

    def create_kb_model_class_map(self, models_data):
        output_str = ""
        for index, model in enumerate(models_data):
            if model["class_map"]:
                output_str += c_line(1, "case({}):".format(index))
                output_str += c_line(2, dict_to_c_string_printf(model["class_map"]))
                output_str += c_line(2, "if(output != NULL)")
                output_str += c_line(2, "{")
                output_str += c_line(2, dict_to_c_string_sprintf(model["class_map"]))
                output_str += c_line(2, "}")
                output_str += c_line(2, "break;")

        return [output_str]

    def create_data_streaming(self, models_data):
        output_str = ""
        for index, model in enumerate(models_data):
            output_str += (
                f"\nint32_t data_streaming_{index}(void* model, int16_t *pSample)\n"
            )

            output_str += "{\n"
            output_str += c_line(1, "int32_t FrameIdx = 0;")
            output_str += c_line(1, "kb_model_t * kb_model = (kb_model_t*)model;")

            if model.get("parent") is None:
                for key in ["transforms_sensors"]:
                    output_str = "\n\t".join([output_str] + model.get(key))
                output_str += c_line(
                    1,
                    "\nsaveSensorData(kb_model->pdata_buffer->data, kb_model->input_data, kb_model->pdata_buffer->size);",
                )
            output_str += c_line(1, "return 1;\n}")

        return [output_str]

    def create_data_segmentation(self, models_data):
        output_str = ""
        for index, model in enumerate(models_data):
            output_str += f"\nint32_t data_segmentation_{index}(void* model, int32_t model_index)\n"
            output_str += "{\n"
            output_str += c_line(1, "int32_t FrameIdx = 0;")
            output_str += c_line(
                1, "kb_model_t * kb_model = (kb_model_t*)model+model_index;"
            )

            # if it has no parent, it is a top level model
            if model.get("parent") is None:
                output_str += c_line(
                    1,
                    "int32_t new_samples = rb_num_items(kb_model->pdata_buffer->data, kb_model->last_read_idx);",
                )
                output_str += c_line(1, "int32_t i;")
                output_str += c_line(1, "for (i=0; i<new_samples; i++){")
                output_str += c_line(3, "kb_model->last_read_idx += 1;")
                output_str += c_line(2, "\n".join(model.get("segmenter_call")))
                output_str += c_line(3, "return 1;")
                output_str += c_line(2, "}")
                output_str += c_line(1, "}")
                output_str += c_line(1, "// Colect more samples")
                output_str += c_line(1, "return -1;\n}")
            elif model.get("segmenter_from", None) == "parent":
                # check if the ring buffer is locked or not (note: we may modify
                # how this works
                # get the model struct that we are subsegment from
                output_str += c_line(
                    1, "if (kb_model->pdata_buffer->data->lock != true) return -1;"
                )
                output_str += c_line(
                    1,
                    "kb_model_t * kb_model_parent = (kb_model_t*)model+kb_model->parent;",
                )
                output_str += c_line(
                    1, "kb_model->sg_index = kb_model_parent->sg_index;"
                )
                output_str += c_line(
                    1, "kb_model->sg_length = kb_model_parent->sg_length;"
                )
                output_str += c_line(1, "return 1;\n}")
            else:  # use the models internal segmenter to subsegment the parent segment
                # model.get('segment', 'self') == 'self'
                output_str += c_line(
                    1,
                    "kb_model_t * kb_model_parent = (kb_model_t*)model+kb_model->parent;",
                )
                output_str += c_line(1, "int32_t i;")
                output_str += c_line(1, "if (kb_model->feature_bank_index==0){")
                output_str += c_line(
                    2, "kb_model->sg_index = kb_model_parent->sg_index;"
                )
                output_str += c_line(2, "kb_model->sg_length = 0;")
                output_str += c_line(1, "}")
                output_str += c_line(1, "for (i=0; i<kb_model_parent->sg_length;i++){")
                output_str += c_line(2, "\n".join(model.get("segmenter_call")))
                output_str += c_line(3, "return 1;")
                output_str += c_line(2, "}")
                output_str += c_line(1, "}")
                output_str += c_line(1, "// No Subsegment Found")
                output_str += c_line(1, "return -1;\n}")

        return [output_str]

    def create_kb_model_indexes(self, models_data):
        output = []
        for index, model in enumerate(models_data):
            output.append(
                "#define {} {}".format(c_model_name(model.get("name", index)), index)
            )
        return output

    def create_kb_model_map(self, models_data):
        output_str = 'printf("{\\"NumModels\\":'
        output_str += "{},".format(len(models_data))

        for index, model in enumerate(models_data):
            output_str += '\\"{}\\":\\"{}\\",'.format(index, model.get("name", index))
        output_str = output_str[:-1]
        output_str += '}");'

        return [output_str]

    def create_pipeline_data_structures(self, models_data):
        output = []
        number_of_models = len(models_data)
        model_names = [model["name"] for model in models_data]
        parent_model_names = [
            model["name"] for model in models_data if model["parent"] is None
        ]
        number_of_parents = len(parent_model_names)
        parent_model_indexes = range(number_of_parents)

        def create_model_arrays(data_type, name, model_obj_name, model_names):
            model_items = []
            for model_name in model_names:
                model_items.append("{0}_{1}".format(model_obj_name, model_name))
            return (
                f"{data_type} *{name}[NUMBER_OF_MODELS] = {{{','.join(model_items)}}};"
            )

        def create_model_parent_arrays(data_type, name, model_names):
            model_items = []
            for model_name in model_names:
                model_items.append("{0}_{1}".format(name, model_name))

            return f"{data_type} *{name}[NUMBER_OF_PARENT_MODELS] = {{{','.join(model_items)}}};"

        def create_model_variable(data_type, name, index, fill):
            return f"{data_type} {name}_{index}[{fill}];"

        def create_model_define(data_name, index, fill):
            return f"#define {data_name}_{index} {fill}"

        def create_model_uuid_define(data_name, index, value):
            return f"static uint8_t {data_name}_{index}[16] = {value};"

        def create_variable_init(variable_type, variable_name, size):
            return f"{variable_type} {variable_name}[{size}];"

        output.append(f"#define NUMBER_OF_PARENT_MODELS {number_of_parents}")
        output.append(f"#define NUMBER_OF_MODELS {number_of_models}")
        output.append(f"#define NUMBER_OF_SEGMENTERS {number_of_models}")

        rbuffers_lengths = []
        sbuffers_lengths = []
        starter_limit = []
        for index, model in enumerate(models_data):
            index = model["model_index"]
            model.get("name", index)

            model_defines = [
                (
                    "NUMBER_OF_FEATURE_BANKS",
                    model["model_index"],
                    model.get("num_feature_banks"),
                ),
                (
                    "NUMBER_OF_FEATURES_PER_BANK",
                    model["model_index"],
                    model.get("num_features_per_bank"),
                ),
                (
                    "TOTAL_FEATURES",
                    model["model_index"],
                    model.get("num_features_per_bank") * model.get("num_feature_banks"),
                ),
                (
                    "OUTPUT_TENSORS",
                    model["model_index"],
                    model_gen.get_output_tensor_size(model["classifier_type"], model),
                ),
            ]

            if self.has_classification_limit:
                starter_limit.append(str(settings.STARTER_CLASSIFICATION_LIMIT))

            if model["parent"] is None:
                rbuffers_lengths.append(str(model.get("number_of_ringbuffs")))
                sbuffers_lengths.append(str(model.get("number_of_sbuffs")))

                model_defines += [
                    (
                        "NUMBER_OF_RINGBUFFS",
                        model["model_index"],
                        model.get("number_of_ringbuffs"),
                    ),
                    (
                        "_RAWDATABUF_LEN",
                        model["model_index"],
                        model.get("raw_buffer_length"),
                    ),
                    (
                        "NUMBER_OF_SBUFFS",
                        model["model_index"],
                        model.get("number_of_sbuffs", 0),
                    ),
                    (
                        "_RAWDATASBUF_LEN",
                        model["model_index"],
                        model.get("raw_sbuffer_length", 0)
                        * model.get("number_of_sbuffs", 0),
                    ),
                ]

            for param in model_defines:
                output.append(create_model_define(*param))

        num_models = "NUMBER_OF_MODELS"
        num_parents = "NUMBER_OF_PARENT_MODELS"
        model_variable_init = [
            ("static kb_model_t", "kb_models", num_models),
            ("static seg_params", "segParams", num_parents),
            ("static data_buffers_t", "data_buffers", num_parents),
            ("static data_buffers_t", "sdata_buffers", num_parents),
            ("static feature_bank_t", "feature_banks", num_models),
            ("static feature_vector_t", "feature_vectors", num_models),
            ("static model_results_t", "model_results", num_models),
            ("static float_data_t", "output_tensors", num_models),
        ]

        for param in model_variable_init:
            output.append(create_variable_init(*param))

        output.append(
            "static int32_t rbuffers_len[NUMBER_OF_PARENT_MODELS] = {{{0}}};".format(
                ", ".join(rbuffers_lengths)
            )
        )

        output.append(
            "static int32_t sbuffers_len[NUMBER_OF_PARENT_MODELS] = {{{0}}};".format(
                ", ".join(sbuffers_lengths)
            )
        )

        if self.has_classification_limit:
            output.append(
                "static const int32_t max_classifications[NUMBER_OF_MODELS] = {{{0}}};".format(
                    ",".join(starter_limit)
                )
            )

        for index, model in enumerate(models_data):
            output.append(
                create_model_uuid_define(
                    "model_uuid",
                    index,
                    uuid_str_to_c_array(self.knowledgepacks[model["name"]]["uuid"]),
                )
            )

            model_varaibles = [
                (
                    "static float",
                    "pFeatures",
                    index,
                    f"TOTAL_FEATURES_{index}",
                ),
                (
                    f"static {model_gen.get_input_feature_def(model)}",
                    "feature_vector_arr",
                    index,
                    f"FEATURE_VECTOR_SIZE_{index}",
                ),
                (
                    "static float",
                    "output_tensor",
                    index,
                    f"OUTPUT_TENSORS_{index}",
                ),
            ]

            if model["parent"] is None:
                model_varaibles += [
                    (
                        "static int16_t",
                        "input_data",
                        model["model_index"],
                        f"NUMBER_OF_RINGBUFFS_{model['model_index']}",
                    ),
                    (
                        "int16_t",
                        "RAW_DATA_BUFFER",
                        model["model_index"],
                        f"_RAWDATABUF_LEN_{model['model_index']}",
                    ),
                    (
                        "ring_buffer_t",
                        "rbuffers",
                        model["model_index"],
                        f"NUMBER_OF_RINGBUFFS_{model['model_index']}",
                    ),
                    (
                        "int16_t",
                        "RAW_SDATA_BUFFER",
                        model["model_index"],
                        f"_RAWDATASBUF_LEN_{model['model_index']}",
                    ),
                    (
                        "ring_buffer_t",
                        "sbuffers",
                        model["model_index"],
                        f"NUMBER_OF_SBUFFS_{model['model_index']}",
                    ),
                ]

            if self.platform.profiling_enabled:
                model_varaibles += [
                    (
                        "static float",
                        "pfeature_gen_times",
                        model["name"],
                        f"TOTAL_FEATURES_{index}",
                    ),
                    (
                        "static uint32_t",
                        "pfeature_gen_cycles",
                        model["name"],
                        f"TOTAL_FEATURES_{index}",
                    ),
                ]

            for param in model_varaibles:
                output.append(create_model_variable(*param))

        model_arrays = []

        if self.platform.profiling_enabled:
            model_arrays += [
                (
                    "static float",
                    "pfeature_gen_times",
                    "pfeature_gen_times",
                    model_names,
                ),
                (
                    "static uint32_t",
                    "pfeature_gen_cycles",
                    "pfeature_gen_cycles",
                    model_names,
                ),
            ]

        parent_model_arrays = [
            ("static int16_t", "input_data", parent_model_indexes),
            ("int16_t", "RAW_DATA_BUFFER", parent_model_indexes),
            ("ring_buffer_t", "rbuffers", parent_model_indexes),
            ("int16_t", "RAW_SDATA_BUFFER", parent_model_indexes),
            ("ring_buffer_t", "sbuffers", parent_model_indexes),
        ]

        for param in model_arrays:
            output.append(create_model_arrays(*param))

        for param in parent_model_arrays:
            output.append(create_model_parent_arrays(*param))

        return output

    def create_kb_models(self, models_data):
        output = []

        def create_model_parameter(parameter, value, model_index):
            return f"kb_models[{model_index}].{parameter} = {value};"

        def create_model_structs(key, param, value, model_index):
            return f"{key}[{model_index}].{param} = {value};"

        def create_model_pointers(parameter, value, model_index, value_index):
            return f"kb_models[{model_index}].{parameter} = {value}_{value_index};"

        def create_model_object_pointers(parameter, value, model_index, value_index):
            return f"kb_models[{model_index}].{parameter} = {value}[{value_index}];"

        parent_index = get_parent_index_map(models_data)

        classifier_counter = {}

        for model in models_data:
            index = model["model_index"]
            name = model.get("name", index)

            ## Keep track of the numer of classifiers of each type
            classifier_type = self.get_classifier_type_map(
                models_data[index]["classifier_config"]
            )
            if classifier_counter.get(classifier_type, None) is None:
                classifier_counter[classifier_type] = 0
            else:
                classifier_counter[classifier_type] += 1

            model_structs = {
                f"feature_vectors": [
                    ("typeID", model_gen.get_input_feature_type(model)),
                    ("size", f"FEATURE_VECTOR_SIZE_{index}"),
                    ("data", f"feature_vector_arr_{index}"),
                ],
                f"output_tensors": [
                    ("size", f"OUTPUT_TENSORS_{index}"),
                    ("data", f"output_tensor_{index}"),
                ],
                f"model_results": [
                    ("model_type", model_gen.get_model_type(model)),
                    ("result", 0),
                    ("output_tensor", f"&output_tensors[{index}]"),
                ],
                f"feature_banks": [
                    ("num_banks", f"NUMBER_OF_FEATURE_BANKS_{index}"),
                    ("bank_size", f"NUMBER_OF_FEATURES_PER_BANK_{index}"),
                    ("pFeatures", f"pFeatures_{index}"),
                    ("filled_flag", "false"),
                ],
            }

            if model["parent"] is None:
                model_structs.update(
                    {
                        f"data_buffers": [
                            ("size", f"NUMBER_OF_RINGBUFFS_{parent_index[name]}"),
                            ("data", f"rbuffers[{parent_index[name]}]"),
                        ],
                        f"sdata_buffers": [
                            ("size", f"NUMBER_OF_SBUFFS_{parent_index[name]}"),
                            ("data", f"sbuffers[{parent_index[name]}]"),
                        ],
                    }
                )

            model_states = [
                ("model_uuid", f"model_uuid_{index}", index),
                ("parent", f"{parent_index[name]}", index),
                ("sg_length", "0", index),
                ("sg_index", "0", index),
                ("last_read_idx", "0", index),
                ("feature_bank_index", "0", index),
                (
                    "streaming_filter_length",
                    models_data[index]["streaming_filter_length"],
                    index,
                ),
                ("classifier_id", classifier_counter[classifier_type], index),
                (
                    "classifier_type",
                    self.get_classifier_type_map(
                        models_data[index]["classifier_config"]
                    ),
                    index,
                ),
                (
                    "m_profile.enabled",
                    f"{1 if self.platform.profiling_enabled else 0}",
                    index,
                ),
            ]

            if self.platform.profiling_enabled:
                model_states += [
                    (
                        "m_profile.feature_gen_times",
                        f"pfeature_gen_times[{index}]",
                        index,
                    ),
                    (
                        "m_profile.feature_gen_cycles",
                        f"pfeature_gen_cycles[{index}]",
                        index,
                    ),
                    ("m_profile.classifier_time", 0, index),
                    ("m_profile.classifier_cycles", 0, index),
                ]

            model_pointers = [
                ("input_data", "input_data", index, parent_index[name]),
                ("data_streaming", f"data_streaming", index, index),
                ("data_segmentation", f"data_segmentation", index, index),
                ("feature_gen", f"feature_gen", index, index),
                ("feature_transform", f"feature_transform", index, index),
                ("recognize_vector", f"recognize_vector", index, index),
            ]

            model_object_pointers = [
                ("psdata_buffer", "&sdata_buffers", index, parent_index[name]),
                ("pdata_buffer", "&data_buffers", index, parent_index[name]),
                ("psegParams", "&segParams", index, parent_index[name]),
                ("pfeature_bank", "&feature_banks", index, index),
                ("pfeature_vector", "&feature_vectors", index, index),
                ("pmodel_results", "&model_results", index, index),
            ]

            for key, params in model_structs.items():
                for param in params:
                    output.append(create_model_structs(key, param[0], param[1], index))

            for param in model_states:
                output.append(create_model_parameter(*param))

            for param in model_pointers:
                output.append(create_model_pointers(*param))

            for params in model_object_pointers:
                output.append(create_model_object_pointers(*params))

        output.append("if(reset_num_classes){\n")
        for model in models_data:
            output.append(
                create_model_parameter(
                    "total_classifications", str(0), model["model_index"]
                )
            )

        output.append("reset_num_classes = false;")
        output.append("}")

        return output

    def create_segmenter_reset(self, models_data):
        output = ["switch(model_index)\n{"]
        for index, model in enumerate(models_data):
            if model.get("segmenter_reset", None):
                output.append("case({}):".format(index))
                output.append(model.get("segmenter_reset")[0])
                output.append("break;")
        output.append("}")

        return output

    def create_segmenter_typedef(self, models_data):
        parameters_key = []
        parameters = []
        for index, model in enumerate(models_data):
            for parameter in model.get("segmenter_typedef_parameters", []):
                if parameter["name"] not in parameters_key:
                    parameters_key.append(parameter["name"])
                    parameters.append(parameter)

        return create_struct_typedef_from_parameters(parameters, "seg_params")

    def create_max_feature_selection(self):
        return ["#define MAX_FEATURE_SELECTION {}".format(self.max_feature_selection)]

    def create_number_of_sensors(self, models_data):
        max_sensors = 0
        for index, model in enumerate(models_data):
            # due to parent models getting all of the sensors but not having
            # them, this needs to be changed to number_of_ring buffs
            # which makes a better measure for the max number of columns we can
            # see across all types of calls
            max_sensors = max(
                len(model.get("used_data_columns", [])),
                max_sensors,
                len(model.get("used_sensor_columns", [])),
            )

        return ["#define NUMBER_OF_SENSORS {0}".format(max_sensors)]

    def create_ring_buffer_init_size(self, models_data):
        output = []

        count = 0
        for index, model in enumerate(models_data):
            if model.get("parent") is None:
                output.append("case({0}):".format(count))
                output.append(
                    "\t\tcbuflen = _RAWDATABUF_LEN_{0} / NUMBER_OF_RINGBUFFS_{0};".format(
                        model.get("model_index")
                    )
                )
                if model.get("raw_sbuffer_length", 0):
                    output.append(
                        "\t\tsbuflen = _RAWDATASBUF_LEN_{0} / NUMBER_OF_SBUFFS_{0};".format(
                            model.get("model_index")
                        )
                    )
                else:
                    output.append("sbuflen = 0;")
                output.append("break;")
                count += 1

        return output

    def get_model_sample_rate(self, model):
        capture_config = model["capture_configuration"]
        rate = None

        if not capture_config:
            rate = self.device_config.get("sample_rate", 0)
        else:
            capture_sources = capture_config.configuration.get("capture_sources", None)

            for source in capture_sources:
                rate = source.get("sample_rate", 0)

        if rate is None:
            if self.build_type == "bin":
                raise Exception(
                    "Sample rate was not configured. Must be configured for binary download!"
                )
            elif self.build_type == "lib" or self.build_type == "source":
                # sample rate doesn't matter for library/source builds
                rate = 100

        return rate

    @staticmethod
    def get_model_enabled_sensors(model):
        capture_config = model["capture_configuration"]
        ret = dict()

        if not capture_config:
            return ret
        else:
            capture_sources = capture_config.configuration.get("capture_sources", None)

            for source in capture_sources:
                for sensor in source.get("sensors", list()):
                    stype = sensor.get("type", None)
                    if stype is None:
                        continue
                    ret[f"sensor_{stype.lower()}"] = 1

        return ret

    @staticmethod
    def get_model_ranges(model):
        capture_config = model["capture_configuration"]
        ranges = dict()

        if not capture_config:
            return ranges
        else:
            capture_sources = capture_config.configuration.get("capture_sources", None)

            for source in capture_sources:
                for sen in source.get("sensors", list()):
                    stype = sen.get("type", None)
                    if stype is None:
                        continue
                    for p in sen.get("parameters", list()):
                        if p["name"].lower() == "sensor range":
                            param = p["name"].lower()
                            key = "{}_{}".format(stype.lower(), param.replace(" ", "_"))
                            ranges[key] = p["value"]

        return ranges

    def create_sis_configuration_list(self, kb_models):
        output = []
        output.extend(self.create_sis_config_start())
        # Contains Device Command protocol, generate that code properly.
        for model in [m for m in kb_models if not m["parent"]]:
            # Only generate for parent models.
            output.extend(self.create_sis_config_add_from_model(model))

        output.extend(self.create_sis_config_end())

        # First and last lines don't count in structure definition.
        return output

    def create_sis_configuration_count(self, config_list):
        return ["#define SENSIML_INTERFACE_CONFIG_NUM_MSGS {}".format(len(config_list))]


def create_struct_typedef_from_parameters(parameters, struct_typedef):
    def sanitize_param_type(param_type):
        if param_type == "boolean":
            return "bool"

        return param_type

    struct = []
    struct.append("#define SEG_PARAMS")
    struct.append("typedef struct{")
    for param in parameters:
        struct.append(
            "    {0} {1};".format(sanitize_param_type(param["type"]), param["name"])
        )
    struct.append("}} {};".format(struct_typedef))

    return struct


def get_parent_index_map(models_data):
    parent_index_map = {}
    parent_map = {}
    for _, model in enumerate(models_data):
        if model["parent"] is None:
            parent_map[model["name"]] = model["model_index"]
            parent_index_map[model["name"]] = parent_map[model["name"]]

    for _, model in enumerate(models_data):
        if model["parent"] is not None:
            parent_index_map[model["name"]] = parent_map[model.get("parent")]

    return parent_index_map


def get_model_by_name(models, model_name):
    for model in models:
        if model["name"] == model_name:
            return model
    return None


def dict_to_c_string_printf(tmp_dict):
    output_str = 'printf("{'
    for k, v in tmp_dict.items():
        output_str += '\\"{0}\\":\\"{1}\\",'.format(str(k), v)
    output_str = output_str[:-1]
    output_str += '}");'
    return output_str


def dict_to_c_string_sprintf(tmp_dict):
    output_str = 'sprintf( output,"{'
    for k, v in tmp_dict.items():
        output_str += '\\"{0}\\":\\"{1}\\",'.format(str(k), v)
    output_str = output_str[:-1]
    output_str += '}");'
    return output_str


def convert_to_pme_model_to_json_file_format(model_array, configuration):
    influences = []
    identifiers = []
    vectors = []
    categories = []

    for pattern in model_array:
        influences.append(pattern["AIF"])
        categories.append(pattern["Category"])
        identifiers.append(pattern["Identifier"])
        vectors.append(pattern["Vector"])

    tmp_dict = {}
    tmp_dict["AIF"] = influences
    tmp_dict["Category"] = categories
    tmp_dict["Vector"] = vectors
    tmp_dict["Identifiers"] = identifiers

    if configuration.get("distance_mode") == "KB_DISTANCE_LSUP":
        tmp_dict["DistanceMode"] = 1
    else:
        tmp_dict["DistanceMode"] = 0

    return tmp_dict


def get_generic_model_description(name, class_map, configuration, feature_summary):
    tmp_dict = {}

    tmp_dict["Name"] = name
    tmp_dict["ClassMaps"] = class_map
    tmp_dict["ModelType"] = configuration.get("classifier")
    tmp_dict["FeatureNames"] = [
        feature.get("Feature", str(index))[9:]
        for index, feature in enumerate(feature_summary)
    ]
    tmp_dict["FeatureFunctions"] = [
        feature.get("Generator", str(index))
        for index, feature in enumerate(feature_summary)
    ]

    return tmp_dict
