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

import functools
import logging
import math
import operator
import os
import re

from codegen.utils import c_line, c_model_name
from datamanager.models import CaptureConfiguration
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from engine.base.pipeline_utils import (
    flatten_pipeline_json,
    get_max_segment_size,
    get_num_feature_banks,
    make_recognition_pipeline,
    merge_data_streaming,
    merge_sensor_columns,
    parse_recognition_pipeline,
)
from library.models import Transform
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


ACTIVATION_KEY_STR = 'const char kb_act_key[KB_ACTIVATION_KEY_LENGTH] = "{}";'
ACTIVATION_CODE_STR = 'const char kb_act_code[KB_ACTIVATION_CODE_LENGTH] = "{}";'
SPOTTER_WITH_PARAMS_STR = "(kb_model, &input_columns, kb_model->psegParams)"
GENERATOR_INPUT_STR_COLUMN = "(kb_model, &input_columns, &input_params, &kb_model->pfeature_bank->pFeatures[CompIdx]);"
GENERATOR_INPUT_STR_COLUMNS = "(kb_model, &input_columns, &input_params, &kb_model->pfeature_bank->pFeatures[CompIdx]);"
C_FUNCTION_IGNORED_INPUTS = [
    "input_data",
    "columns",
    "group_columns",
    "group_column",
    "passthrough_columns",
    "input_data",
    "input_columns",
    "input_column",
    "pad_length",
    "return_segment_index",
]

function_def_regex = re.compile(
    r"^((static\s)?((unsigned int\*?\s)|(int\*?\s)|(void\*?\s)|(double\*?\s)|(short\*?\s)|(int16_t\*?\s)|(uint32_t\*?\s)|(int32_t\*?\s)|"
    r"(float\*?\s)).*?(\s?\(.*\s*\)))",
    re.IGNORECASE,
)

num_params_regex = re.compile(r".*NUM_PARAMS\ (?P<num_params>\d+)")


class KnowledgePackGenerationError(Exception):
    pass


class ModelGraphMixin(object):
    """ " The model graph mixin is responsible for taking a pipeline or cominination of pipelines and parsing out the model data
    needed to codegen a pipeline of optimized c code.

    name(str): name of this model
    parent(int32_t): parent index of this model
    segmenter_from(bool): does it use its own segmenter or its parent segment
    model_index(int32_t): the index assigned to this particular model for codegen
    results: what to do with the results output

    number_of_sensors(int32_t): number of sensor columns
    sensor_plugin(str): motion, audio or custom
    sensor_column_names(list): defines for the sensors pulled from the device
    data_column_names(list):  defines for the data columns used in the pipeline
    used_sensor_columns(list): the sensor columns that are actually used
    used_data_columns(list): the data columns that are actually used in the pipeline

    raw_sbuffer_length(int32_t): lenght of sensor data buffer needed by sensor transforms
    number_of_sbuffs(int32_t): number of sensor buffers needed by sensor tranform
    transforms_sensors(list):

    segmenter_call(str):
    segmenter_reset(str):
    segment_filter_reset(str):
    transforms_segments(list):

    transforms_feature_vectors:
    generate_features_calls:
    num_feature_banks:
    temp_data_length:

    neuron_vector_size:
    classifier_config:
    number_of_neurons:
    model_arrays:

    cascade_reset: weather to call run_models_with_cascade_reset or run_model
    num_feature_banks: number of feature banks create for this model


    """

    def get_model_data(self, build_type="lib"):
        kb_models = []
        neuron_arrays = []
        classifier_configs = []

        # get model specific information
        for model_index in self.knowledgepacks:
            knowledgepack = self.knowledgepacks[model_index]["knowledgepack"]

            logger.debug(
                {
                    "message": "Compiling KnowledgePack {} information.".format(
                        str(knowledgepack.uuid)
                    ),
                    "log_type": "KPID",
                    "UUID": self.uuid,
                }
            )

            # TODO PULL SENSOR AND DATA COLUMNS FROM CAPTURE CONFIGURATION

            try:
                capture_configuration = CaptureConfiguration.objects.get(
                    uuid=self.knowledgepacks[model_index]["source"]
                )
            except:
                capture_configuration = self.knowledgepacks[model_index]["source"]

            if knowledgepack.knowledgepack_summary:
                pipeline = knowledgepack.knowledgepack_summary["recognition_pipeline"]
                sensor_columns = knowledgepack.knowledgepack_summary["sensor_columns"]
                data_columns = knowledgepack.knowledgepack_summary[
                    "data_columns_ordered"
                ]
            else:
                pipeline, sensor_columns, data_columns = make_recognition_pipeline(
                    knowledgepack.project,
                    capture_configuration=capture_configuration,
                    **knowledgepack.__dict__,
                )

            pipeline_json = parse_recognition_pipeline(pipeline)
            pipeline_json, num_feature_banks, cascade_reset = get_num_feature_banks(
                pipeline_json
            )
            classifier_config = self.get_classifier_init(knowledgepack)

            classifier_configs.append(classifier_config)
            neuron_arrays.append(knowledgepack.neuron_array)
            class_map = knowledgepack.class_map
            self.knowledgepacks[model_index].update(
                {
                    "sensor_columns": sensor_columns,
                    "data_columns": data_columns,
                    "pipeline": pipeline,
                    "pipeline_json": pipeline_json,
                    "knowledgepack": knowledgepack,
                    "neuron_array": knowledgepack.neuron_array,
                    "pvp_config": classifier_config,
                    "num_feature_banks": num_feature_banks,
                    "class_map": class_map,
                    "cascade_reset": cascade_reset,
                }
            )

        model_groups = get_model_group(self.knowledgepacks)

        # merge the data streaming part and map columns to the correct place in
        # the ringbuffer
        for model_group in model_groups:
            sensor_columns = merge_sensor_columns(model_group, self.knowledgepacks)

            (
                data_streaming,
                data_column_map,
                model_data_column_map,
            ) = merge_data_streaming(model_group, self.knowledgepacks)

            # set the data streaming part of the pipeline json to the new for the
            # top level and remove the rest
            for pipeline_name in model_group:
                self.knowledgepacks[pipeline_name][
                    "data_column_map"
                ] = model_data_column_map[pipeline_name]
                # the first is always the parent
                if self.knowledgepacks[pipeline_name]["parent"] is None:
                    self.knowledgepacks[pipeline_name]["pipeline_json"][
                        "Sensor Transforms"
                    ] = data_streaming
                    ivd = {v: k for k, v in data_column_map.items()}
                    self.knowledgepacks[pipeline_name]["data_columns"] = [
                        ivd[x] for x in range(len(ivd.keys()))
                    ]
                    self.knowledgepacks[pipeline_name][
                        "data_column_map"
                    ] = data_column_map
                else:
                    self.knowledgepacks[pipeline_name]["pipeline_json"][
                        "Sensor Transforms"
                    ] = []

        # flatten the pipeline_json and set the pipeline to the modified version
        for model in self.knowledgepacks:
            self.knowledgepacks[model]["pipeline"] = flatten_pipeline_json(
                self.knowledgepacks[model]["pipeline_json"]
            )

        # get model specific information
        for model_index, model_name in enumerate(flatten_groups(model_groups)):
            # get parents first, then get children
            model_data = self.get_pipeline_items(
                self.knowledgepacks[model_name]["pipeline"],
                self.knowledgepacks[model_name]["sensor_columns"],
                self.knowledgepacks[model_name]["data_columns"],
                self.knowledgepacks[model_name]["knowledgepack"].neuron_array,
                self.knowledgepacks[model_name]["data_column_map"],
                model_name,
                model_index,
            )

            model_data["name"] = model_name
            model_data["classifier_type"] = get_classifier_type(
                self.knowledgepacks[model_name]
            )

            # todo: this should be pulled from the plugin or the kb_description
            default_source = self.platform.supported_source_drivers.get(
                "Default", ["custom"]
            )[0].lower()
            model_data["sensor_plugin"] = self.knowledgepacks[model_name].get(
                "source", default_source
            )

            (
                model_data["sensor_plugin_name"],
                model_data["capture_configuration"],
            ) = self.get_capture_configuration(
                model_data["sensor_plugin"],
                self.knowledgepacks[model_name]["knowledgepack"],
            )

            model_data["used_sensor_columns"] = self.knowledgepacks[model_name][
                "sensor_columns"
            ]
            model_data["used_data_columns"] = self.knowledgepacks[model_name][
                "data_columns"
            ]
            model_data["parent"] = self.knowledgepacks[model_name]["parent"]
            model_data["model_index"] = model_index
            model_data["segmenter_from"] = self.knowledgepacks[model_name].get(
                "segmenter_from", None
            )
            model_data["results"] = self.knowledgepacks[model_name].get("results", None)
            model_data["num_feature_banks"] = self.knowledgepacks[model_name][
                "num_feature_banks"
            ]
            model_data["cascade_reset"] = self.knowledgepacks[model_name][
                "cascade_reset"
            ]
            model_data["model_arrays"] = self.knowledgepacks[model_name]["neuron_array"]
            model_data["classifier_config"] = self.knowledgepacks[model_name][
                "pvp_config"
            ]
            model_data["class_map"] = self.knowledgepacks[model_name]["class_map"]
            model_data["feature_summary"] = self.knowledgepacks[model_name][
                "knowledgepack"
            ].feature_summary

            kb_models.append(model_data)

            logger.debug(
                {
                    "message": "KnowledgePack Pipeline {} information.".format(
                        str(knowledgepack.uuid)
                    ),
                    "data": pipeline,
                    "log_type": "KPID",
                    "UUID": self.uuid,
                }
            )

        logger.debug(
            {
                "message": "KnowledgePack Model Data.".format(str(knowledgepack.uuid)),
                "data": kb_models,
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        return kb_models, model_groups

    def get_capture_configuration(self, sensor_plugin, knowlegepack):
        if sensor_plugin.lower() in ["motion", "audio", "custom"]:
            return sensor_plugin.lower(), None
        else:
            try:
                capture_configuration = CaptureConfiguration.objects.get(
                    uuid=sensor_plugin, project=knowlegepack.project
                )
            except ObjectDoesNotExist:
                raise KnowledgePackGenerationError("Invalid Capture Configuration ID")

            validate_capture_config(self.platform, capture_configuration)

            return (
                [
                    p["name"]
                    for p in capture_configuration.configuration.get(
                        "capture_sources", ["custom"]
                    )
                ][0].lower(),
                capture_configuration,
            )

    def get_model_name(self, kp_name, index):
        if kp_name:
            return kp_name
        else:
            return index

    def get_static_function_files(self, pipeline):
        function_decs, function_impl = self.get_function_declaration_implementation(
            pipeline
        )

    def get_pipeline_items(
        self,
        pipeline,
        sensor_columns,
        data_columns,
        neuron_array,
        data_column_map,
        model_name,
        model_index,
        is_parent=True,
    ):
        """
        Returns: Dictionary containing lists of strings for boilerplate replacement
        """
        return_data = {}
        return_data[
            "sensor_column_names"
        ] = []  # defines for the sensors pulled from the device
        return_data["number_of_sensors"] = []
        return_data[
            "data_column_names"
        ] = []  # defines for the data columns used in the pipeline

        return_data["segmenter_call"] = []
        return_data["segmenter_reset"] = []
        return_data["segment_transforms"] = []
        return_data["segment_filters"] = []
        return_data["segment_filter_reset"] = []
        return_data["transforms_sensors"] = []
        return_data["transforms_feature_vectors"] = []
        return_data["generate_features_calls"] = []
        return_data["temp_data_length"] = 0
        return_data["raw_sbuffer_length"] = 0
        return_data["number_of_sbuffs"] = 0
        return_data["streaming_filter_length"] = 1
        return_data["feature_vector_size"] = self.get_feature_vector_size(
            self.knowledgepacks[model_name]["knowledgepack"]
        )

        return_data["data_column_names"] = [
            "#define {} {}".format(
                column_transform(x, "pipeline", model_name), data_column_map[x]
            )
            for x in data_columns
        ]
        return_data["sensor_column_names"] = [
            "#define {} {}".format(column_transform(x[0], "sensor", model_name), x[1])
            for x in zip(sensor_columns, range(len(sensor_columns)))
        ]

        sensors_to_keep = 0
        for sensor_column in sensor_columns:
            if sensor_column.upper() in data_columns:
                return_data["transforms_sensors"].append(
                    "input_columns.data[{0}] = {1};".format(
                        sensors_to_keep,
                        column_transform(sensor_column, "sensor", model_name),
                    )
                )
                sensors_to_keep += 1

        if is_parent:
            return_data["transforms_sensors"].append(
                f"input_columns.size = {sensors_to_keep};"
            )
            return_data["transforms_sensors"].append(
                "FrameIdx += tr_sensor_sensors(pSample, &input_columns, &kb_model->input_data[FrameIdx]);"
            )

        for step in pipeline:
            logger.debug(
                {
                    "message": "Compiling Pipeline Step: {}".format(step["name"]),
                    "log_type": "KPID",
                    "UUID": self.uuid,
                }
            )
            if step["type"] != "generatorset":
                function = Transform.objects.get(name=step["name"])

            if step["type"] == "generatorset":
                return_data["generate_features_calls"] = self.get_feature_generator_set(
                    step, model_name
                )

                query = functools.reduce(
                    operator.or_,
                    (
                        Q(
                            name=fn["function_name"],
                            library_pack__uuid=fn["inputs"].get(
                                "library_pack", settings.SENSIML_LIBRARY_PACK
                            ),
                        )
                        for fn in step["set"]
                    ),
                )

                transforms = Transform.objects.all().filter(query)

                return_data["temp_data_length"] = self.get_max_temp_data(
                    step,
                    model_name,
                    return_data.get("max_buffer_length", 0),
                    transforms,
                    data_columns,
                )

                return_data["num_features_per_bank"] = self.get_num_features_per_bank(
                    step, model_name, transforms
                )

            elif function.type == "Segmenter":
                return_data.update(
                    self.get_segmenter(
                        function,
                        step,
                        sensor_columns,
                        data_columns,
                        model_name,
                        model_index,
                    )
                )

            elif function.type == "Transform":
                if function.subtype == "Sensor":
                    return_data["transforms_sensors"].extend(
                        self.get_transform_sensor(function, step, model_name)
                    )

                elif function.subtype == "Sensor Filter":
                    (
                        sensor_filter_code,
                        buff_length,
                    ) = self.get_streaming_transform_sensor(
                        function, step, model_name, data_columns
                    )
                    return_data["transforms_sensors"].extend(sensor_filter_code)
                    return_data["raw_sbuffer_length"] = max(
                        buff_length, return_data["raw_sbuffer_length"]
                    )
                    return_data["number_of_sbuffs"] += 1
                    return_data[
                        "streaming_filter_length"
                    ] = self.get_streaming_transform_sensor_filter_length(
                        function, step
                    )

                elif function.subtype == "Segment Filter":
                    return_data["segment_filters"].extend(
                        self.get_transform_segment(
                            function, step, model_name, data_columns
                        )
                    )
                    return_data["segment_filter_reset"].append(
                        f"reset_{function.c_function_name}();"
                    )

                elif function.subtype == "Segment":
                    return_data["segment_transforms"].extend(
                        self.get_transform_segment(
                            function, step, model_name, data_columns
                        )
                    )

                elif function.subtype == "Feature Vector":
                    return_data["transforms_feature_vectors"].extend(
                        self.get_transform_feature_vector(
                            function,
                            step,
                            model_name,
                            return_data.get("num_features_per_bank", None),
                        )
                    )

                else:
                    raise Exception('Unknown pipeline step "{}"'.format(step["type"]))

        return_data["number_of_sbuffs"] = (
            return_data["number_of_sbuffs"] * return_data["number_of_ringbuffs"]
        )

        if self.spotter_name is None:
            raise ValueError(
                "A segmenter must be defined for the "
                + "project or included in your pipeline in order to build a knowledgepack."
            )

        return_data["segmenter_reset"].append(
            (
                "{0}_init(&kb_models[model_index], kb_models[model_index].psegParams);".format(
                    self.spotter_name
                )
            )
        )

        self.get_static_function_files(pipeline)

        return return_data

    def get_feature_vector_size(self, knowledgepack):
        return len(
            list(
                filter(
                    lambda x: x.get("EliminatedBy", None) is None,
                    knowledgepack.feature_summary,
                )
            )
        )

    def get_classifier_init(self, knowledgepack):
        """Get the configs and add some error handling

        Returns:
            dict: config variables to use

        Raises:
            NoClassificationModeDefinedException: Description
            NoDistanceModeDefinedException: Description
            NoSampleRateDefinedException: Description
        """
        classifier_config = knowledgepack.device_configuration

        if classifier_config.get("classifier", "PME") in ["PME", "PVP"]:
            distance_type = {
                0: "KB_DISTANCE_L1",
                1: "KB_DISTANCE_LSUP",
                2: "KB_DISTANCE_DTW",
            }
            classification_type = ["KB_CLASSIFICATION_RBF", "KB_CLASSIFICATION_KNN"]

            distance_mode_num = classifier_config.get("distance_mode", None)
            if distance_mode_num is None:
                raise ValueError("Distance Mode was not defined!")
            distance_mode = distance_type[distance_mode_num]

            classification_mode_num = classifier_config.get("classification_mode", None)
            if classification_mode_num is None:
                raise ValueError("Classification Mode was not defined!")
            classification_mode = classification_type[classification_mode_num]

            reserved_patterns = int(classifier_config.get("reserved_patterns", 0))

            num_channels = int(classifier_config.get("num_channels", 1))

            reinforcement_learning = bool(
                classifier_config.get("reinforcement_learning", False)
            )

            return {
                "classifier": "PME",
                "distance_mode": distance_mode,
                "classification_mode": classification_mode,
                "reserved_patterns": reserved_patterns,
                "reinforcement_learning": reinforcement_learning,
                "num_channels": num_channels,
            }

        elif classifier_config["classifier"] == "Decision Tree Ensemble":
            return {"classifier": "Decision Tree Ensemble"}

        elif classifier_config["classifier"] == "Boosted Tree Ensemble":
            return {"classifier": "Boosted Tree Ensemble"}

        elif classifier_config["classifier"] == "Bonsai":
            return {"classifier": "Bonsai"}

        elif classifier_config["classifier"] in [
            "TF Micro",
            "TensorFlow Lite for Microcontrollers",
        ]:
            return {"classifier": "TensorFlow Lite for Microcontrollers"}

        elif classifier_config["classifier"] in ["Linear Regression"]:
            return {"classifier": "Linear Regression"}

        else:
            raise KnowledgePackGenerationError("Unsupported Classifier Configuration")

    def get_feature_generator_set(self, step, model_index):
        generator_set = []
        if self.device_config.get("debug", None):
            if self.device_config.get("debug_level", 1) in [3, 4]:
                generator_set.append('printf("Unscaled Features:");')
        for gen_function in step["set"]:
            generator_set.extend(self.get_feature_generator(gen_function, model_index))

        return generator_set

    def get_num_features_per_bank(self, step, model_index, transforms):
        GeneratorFamilyFeatures = False
        if (
            self.knowledgepacks[model_index]["knowledgepack"]
            .feature_summary[0]
            .get("GeneratorFamilyFeatures", None)
            is None
        ):
            GeneratorFamilyFeatures = True

        num_features_per_bank = 0
        for gen in step["set"]:
            generator_outputs = 0
            transform = transforms.get(
                name=gen["function_name"],
                library_pack__uuid=gen["inputs"].get(
                    "library_pack", settings.SENSIML_LIBRARY_PACK
                ),
            )
            output_formula = transform.output_contract[0].get("output_formula", None)
            if output_formula is not None:
                generator_outputs = calc_feature_output_size(
                    gen["inputs"], output_formula
                )
            else:
                generator_outputs = len(gen["outputs"])

            # backwards compatibility (doesn't work for feature cascaded models)
            if GeneratorFamilyFeatures:
                for index in range(
                    len(
                        self.knowledgepacks[model_index][
                            "knowledgepack"
                        ].feature_summary
                    )
                ):
                    if (
                        self.knowledgepacks[model_index][
                            "knowledgepack"
                        ].feature_summary[index]["Generator"]
                        == gen["function_name"]
                    ):
                        self.knowledgepacks[model_index][
                            "knowledgepack"
                        ].feature_summary[index]["GeneratorFamilyFeatures"] = int(
                            generator_outputs
                        )

            num_features_per_bank += generator_outputs

        return int(num_features_per_bank)

    def get_max_temp_data(
        self, step, model_index, max_buffer, transforms, data_columns
    ):
        temp_length = 0

        for gen_function in step["set"]:
            output_contract = transforms.get(
                name=gen_function["function_name"],
                library_pack__uuid=gen_function["inputs"].get(
                    "library_pack", settings.SENSIML_LIBRARY_PACK
                ),
            ).output_contract[0]

            if output_contract.get("scratch_buffer", None):
                scratch_buffer = output_contract["scratch_buffer"]

                if scratch_buffer["type"] == "segment_size":
                    temp_length = max(max_buffer, temp_length)

                if scratch_buffer["type"] == "ring_buffer":
                    temp_length = max(max_buffer * len(data_columns), temp_length)

                if scratch_buffer["type"] == "fixed_value":
                    temp_length = max(scratch_buffer["value"], temp_length)

                if scratch_buffer["type"] == "parameter":
                    temp_length = max(
                        int(gen_function["inputs"][scratch_buffer["name"]]),
                        temp_length,
                    )

        return temp_length

    def get_function_from_database(self, function):
        function = Transform.objects.get(
            name=function["function_name"],
            library_pack__uuid=function["inputs"].get(
                "library_pack", settings.SENSIML_LIBRARY_PACK
            ),
        )

        if function.custom and self.team_uuid != function.library_pack.team.uuid:
            raise Exception("Function {} not found.".format(function.name))

        return function

    def get_feature_generator(self, gen_function, model_index):
        generator_data = []

        function = self.get_function_from_database(function=gen_function)

        generator_data.extend(get_params_str_list(function, gen_function["inputs"]))

        number_of_streams = len(gen_function["inputs"]["columns"])

        profile = self.device_config.get("profile", None)

        for index, column in enumerate(gen_function["inputs"]["columns"]):
            generator_data.append(
                "input_columns.data[{0}] = {1};".format(
                    index, column_transform(column, "pipeline", model_index)
                )
            )
        generator_data.append(f"input_columns.size={number_of_streams};")

        if profile:
            generator_data.extend(self.get_profile_start(reset_timer=True))

        generator_data.append(
            f"*nfeats = {function.c_function_name}{GENERATOR_INPUT_STR_COLUMNS}"
        )

        if profile:
            generator_data.extend(self.get_profile_feature_stop())

        generator_data.append("CompIdx += *nfeats;")

        if self.device_config.get("debug", None):
            if self.device_config.get("debug_level", 1) == 4:
                generator_data.append("for (int32_t d =0; d<*nfeats; d++){")
                generator_data.append(
                    'printf("%d:  %f", CompIdx-(*nfeats+d), kb_model->pFeatures[CompIdx-(*nfeats+d)]);'.format(
                        gen_function["function_name"]
                    )
                )
                generator_data.append("}")
            elif self.device_config.get("debug_level", 1) == 5:
                generator_data.append("for (int32_t d=0; d<*nfeats; d++){")
                generator_data.append(
                    'printf("{0} %d %d %d %f",  CompIdx-(*nfeats+d), *nfeats, CompIdx, kb_model->pFeatures[CompIdx-(*nfeats+d)]);'.format(
                        gen_function["function_name"]
                    )
                )
                generator_data.append("}")

        return generator_data

    def get_profile_start(self, reset_timer=True):
        ret = list()
        if reset_timer:
            ret.append("sml_profile_reset_timer();")

        ret.append("sml_profile_start_timer();")

        return ret

    def get_profile_feature_stop(self):
        ret = list()
        ret.append("sml_profile_stop_timer();")
        ret.append(
            "kb_model->m_profile.feature_gen_times[CompIdx] = sml_profile_get_total_time();"
        )
        ret.append(
            "kb_model->m_profile.feature_gen_cycles[CompIdx] = sml_profile_get_cycle_count();"
        )
        return ret

    def get_profile_classifier_stop(self):
        ret = list()
        ret.append("sml_profile_stop_timer();")
        ret.append(
            "kb_model->m_profile.classifier_cycles = sml_profile_get_cycle_count();"
        )
        ret.append(
            "kb_model->m_profile.classifier_time = sml_profile_get_total_time();"
        )
        return ret

    def get_transform_feature_vector(
        self, function, step, model_index, num_features_per_bank
    ):
        transform_data = []

        feature_summary = DataFrame(
            self.knowledgepacks[model_index]["knowledgepack"].feature_summary
        )

        if "CascadeIndex" in feature_summary.columns:
            feature_indexes = reduce_context(
                feature_summary.sort_values(by=["CascadeIndex", "ContextIndex"])
            )
        else:
            feature_indexes = reduce_context(
                feature_summary.sort_values(by=["ContextIndex"])
            )

        def remove_cascade(name: str):
            if name[:5] == "gen_c":
                return "_".join(name.split("_")[2:])

            return name

        if (
            function.c_function_name == "min_max_scale"
        ):  ## This should be made into a general function
            maximums = step["inputs"]["feature_min_max_parameters"]["maximums"]
            minimums = step["inputs"]["feature_min_max_parameters"]["minimums"]
            maxbound = step["inputs"]["max_bound"]
            minbound = step["inputs"]["min_bound"]
            transform_data.append(
                c_line(1, f"static struct minmax aminmax[{len(feature_indexes)}] = {{")
            )

            for index, feature_name in enumerate(feature_summary["Feature"].values):
                if feature_name in minimums or remove_cascade(feature_name) in minimums:
                    transform_data.append(
                        "\t\t{{{0}, {1}f, {2}f}},".format(
                            feature_indexes[index],
                            get_feature_scale_value(minimums, feature_name),
                            get_feature_scale_value(maximums, feature_name),
                        )
                    )

            transform_data.append(c_line(1, "};"))
            transform_data.append(
                c_line(
                    1,
                    "int32_t start = (kb_model->feature_bank_index+1) * (kb_model->pfeature_bank->bank_size);",
                )
            )
            transform_data.append(
                c_line(
                    1,
                    "int32_t total_features = (kb_model->pfeature_bank->bank_size) * (kb_model->pfeature_bank->num_banks);",
                )
            )

            # transform_data.extend(self.get_profile_start())
            transform_data.append(
                c_line(
                    1,
                    f"{function.c_function_name}(kb_model->pfeature_bank->pFeatures, kb_model->pfeature_vector, kb_model->pfeature_vector->size, start, total_features, {minbound}, {maxbound}, aminmax);",
                )
            )
            # transform_data.extend(self.get_profile_stop(function.c_function_name))
        else:
            transform_data.append(
                (
                    c_line(
                        1,
                        "{0}(kb_model->pfeature_bank->pFeatures, kb_model->pfeature_vector->size);".format(
                            function.c_function_name
                        ),
                    )
                )
            )

        return transform_data

    def get_streaming_transform_sensor_filter_length(self, function, step):
        if function.c_contract.get("streaming_filter_length", None):
            return step["inputs"][function.c_contract["streaming_filter_length"]]

        return 1

    def get_streaming_transform_sensor(self, function, step, model_index, data_columns):
        transform_data = []

        columns = [x.upper() for x in step["inputs"]["input_columns"]]
        for index, column in enumerate(data_columns):
            if column in columns:
                transform_data.append("input_columns.data[{0}] = 1;".format(index))
            else:
                transform_data.append("input_columns.data[{0}] = 0;".format(index))

        if step["inputs"].get("filter_order", None):
            buffer_size = step["inputs"]["filter_order"] * 2 + 2
        elif step["inputs"].get("filter_length", None):
            buffer_size = step["inputs"]["filter_length"] + 1
        else:
            buffer_size = function.c_contract.get("buffer", 0)

        # this can be evolved as we develop the pattern
        params = function.c_contract.get("params", [])
        params_type = function.c_contract.get("params_type", [])
        param_str = ""
        for p, t in zip(params, params_type):
            if t == "float":
                param_str += f",{float(step['inputs'][p])}f "
            if t in ["int32_t", "int"]:
                param_str += f",{int(step['inputs'][p])} "
            else:
                raise Exception(f"Invalid Parameter Types {p}, {t}")

        transform_data.append(
            f"if ({function.c_function_name}(kb_model->psdata_buffer->data, kb_model->input_data, &input_columns {param_str})==-1) return 0;"
        )

        return (
            transform_data,
            get_nearest_power_2_buffer(buffer_size),
        )

    def get_transform_sensor(self, function, step, model_index):
        transform_data = []

        columns = step["inputs"]["input_columns"]
        for i, column in enumerate(columns):
            transform_data.append(
                "input_columns.data[{0}] = {1};".format(
                    i, column_transform(column, "sensor", model_index)
                )
            )

        transform_data.append(f"input_columns.size={len(columns)};")
        transform_data.append(
            "FrameIdx += {0}(pSample, &input_columns, &kb_model->input_data[FrameIdx]);".format(
                function.c_function_name,
            )
        )

        return transform_data

    def get_transform_segment(self, function, step, model_index, data_columns):
        transform_data = []

        # get the correct columns for segment transforms
        if "input_columns" in step["inputs"].keys():
            columns = step["inputs"]["input_columns"]
        elif "input_column" in step["inputs"].keys():
            columns = [step["inputs"].get("input_column")]
        else:
            columns = []

        # filter out steps to only ones that we should be keeping
        columns = [
            column.upper() for column in columns if column.upper() in data_columns
        ]
        num_data_columns = len(columns)

        for i, column in enumerate(columns):
            transform_data.append(
                "input_columns.data[{0}] = {1};".format(
                    i, column_transform(column, "pipeline", model_index)
                )
            )
        transform_data.append(f"input_columns.size = {num_data_columns};")

        params = get_transform_parameters(step["inputs"], function.input_contract)
        for param in params:
            transform_data.append(
                "\ninput_params.data[{index}] = {value};".format(
                    index=param["index"], value=param["value"]
                )
            )
        transform_data.append(f"input_params.size={len(params)};")
        transform_data.append(
            f"\tif({function.c_function_name}(kb_model, &input_columns, &input_params) == 0) return -1;"
        )

        return transform_data

    def get_segmenter(
        self, function, step, sensor_columns, data_columns, model_name, model_index
    ):
        segmenter_data = {}
        # All attributes that are set are first defined here for our benefit
        segmenter_data["sensor_columns"] = []
        segmenter_data["number_of_sensors"] = []
        segmenter_data["number_of_sensor_columns"] = []
        segmenter_data["number_of_ringbuffs"] = []
        segmenter_data["max_buffer_length"] = []
        segmenter_data["raw_buffer_length"] = []
        segmenter_data["segmenter_call"] = []
        segmenter_data["segmenter_parameters"] = []
        segmenter_data["segmenter_typedef"] = []
        segmenter_data["segmenter_debug_print"] = []

        spotter_name = function.c_function_name

        for i, data_column in enumerate(data_columns):
            segmenter_data["sensor_columns"].append(
                "input_columns.data[{0}] = {1};".format(
                    i, column_transform(data_column, "pipeline", model_name)
                )
            )

        number_of_ringbuffs = len(data_columns)
        segmenter_data["number_of_sensor_columns"] = len(sensor_columns)

        # Some segmenters require a ring buffer of their own we will make this better in the future
        if spotter_name in ["keyless_gesture_segmenter"]:
            number_of_ringbuffs += 1

        segmenter_data["number_of_ringbuffs"] = number_of_ringbuffs

        ###########################################################################################
        # Our Segmenters need a common framework this is what must
        # be done for now
        ###########################################################################################

        # Power of 2 ring buffer
        # nearest power of 2
        rb2_buffer_size = get_nearest_power_2_buffer(get_max_segment_size(step))
        segmenter_data["max_buffer_length"] = rb2_buffer_size
        segmenter_data["raw_buffer_length"] = int(number_of_ringbuffs * rb2_buffer_size)

        # For spotters with single columns
        axis_of_interest = step["inputs"].get("axis_of_interest", None)
        if axis_of_interest is None:
            axis_of_interest = step["inputs"].get("column_of_interest", None)
        if axis_of_interest:
            segmenter_data["segmenter_call"] = [
                "input_columns.data[0] = {0};".format(
                    column_transform(axis_of_interest, "pipeline", model_name)
                )
            ]

        # For spotters with multiple columns
        columns_of_interest = step["inputs"].get("columns_of_interest", None)
        # For spotters with multiple columns of interest
        if columns_of_interest is None:
            for key in step["inputs"].keys():
                if "_column_of_interest" in key:
                    if not columns_of_interest:
                        columns_of_interest = [step["inputs"].get(key)]
                    else:
                        columns_of_interest.append(step["inputs"].get(key))

        if columns_of_interest is not None:
            segmenter_data["segmenter_call"] = []
            for i, column in enumerate(columns_of_interest):
                segmenter_data["segmenter_call"].append(
                    "input_columns.data[{0}] = {1};".format(
                        i, column_transform(column, "pipeline", model_name)
                    )
                )

        else:
            columns_of_interest = []

        segmenter_data["segmenter_call"].append(
            f"input_columns.size = {len(columns_of_interest)};"
        )
        parameters = get_c_params_from_input_contract(function, step["inputs"])

        # Do some segmenter parameter translation
        segmenter_parameters = get_segment_inputs(step, function)
        if segmenter_parameters:
            parameters.extend(segmenter_parameters)

        # add delta = 0 if not in parameters so that all segmenters have a delta param
        # this allows us to correctly calculate the segment length in kb.c (see get_segment_length)
        if not has_input_contract_parameter(parameters, "delta"):
            parameters.append(
                {
                    "name": "delta",
                    "type": "int32_t",
                    "value": 0,
                }
            )

        segmenter_data["segmenter_parameters"].extend(
            create_struct_in_array_from_parameters(parameters, "segParams", model_index)
        )
        segmenter_data["segmenter_call"].append(
            f"\n\tif({function.c_function_name}{SPOTTER_WITH_PARAMS_STR}){{"
        )
        segmenter_data["segmenter_typedef_parameters"] = parameters
        segmenter_data["segmenter_debug_print"].append(
            create_segmenter_debug_print_statement(len(data_columns))
        )

        self.spotter_name = spotter_name

        return segmenter_data

    def add_function_to_gen_dict(self, function_type, function, segmenter=False):
        """
        Adds function to dictionary for compilation. Ensures that each function is only
        added one time.

        Args:
            function_type: Type of function (segmenter, generator, transform), for logging
            name: Name of function.

        Returns: None, contents of function added to internal dictionary.
        """
        if function_type == "generatorset":
            function = Transform.objects.get(
                name=function["function_name"],
                library_pack=function["inputs"].get(
                    "library_pack", settings.SENSIML_LIBRARY_PACK
                ),
            )
        else:
            function = Transform.objects.get(name=function["name"])

        if function.custom:
            self.add_user_generated_c_files.add(function)
        else:
            if not function.has_c_version:
                raise KnowledgePackGenerationError(
                    "C code version needed for {0}".format(function.name)
                )
            func_c_path = "{0}/src/{1}".format(
                settings.CODEGEN_C_FUNCTION_LOCATION, function.c_file_name
            )
            if segmenter == False:
                self.add_c_files.append(function.c_file_name)
                return
            if not os.path.exists(func_c_path):
                raise KnowledgePackGenerationError(
                    "File {0} does not exist".format(func_c_path)
                )

            self.add_c_files.append(function.c_file_name)

    def get_function_declaration_implementation(self, pipeline):
        """
        Pulls the actual function declarations (for a .h file) and implementation
        (for a .c file) out from the recognition pipeline.
        Returns: function_declarations (list), and actual_functions (list)
        """
        function_declarations = []
        actual_functions = []

        for step in pipeline:
            # Continue to pull this out for segmenters because there are other build issues
            # with a static library.
            if step["type"] == "generatorset":
                for i in range(len(step["set"])):
                    self.add_function_to_gen_dict("generatorset", step["set"][i])
            else:
                step["name"]
                self.add_function_to_gen_dict(step["type"], step)

        for funcName, funcBody in self.codegen_dict.items():
            # H file Contents
            func_to_append = funcName + ";"
            if func_to_append not in function_declarations:
                function_declarations.append((funcName + ";"))
            # C File Contents
            if funcName not in actual_functions:
                actual_functions.append(funcName)
                actual_functions.extend(funcBody)
                actual_functions.append("")

        return function_declarations, actual_functions


def has_input_contract_parameter(parameters, value):
    for parameter in parameters:
        if parameter["name"] == value:
            return True

    return False


def get_c_params_from_input_contract(function, inputs):
    parameters = []
    for params in function.input_contract:
        if params.get("c_param", None):
            parameters.append(
                {
                    "name": params["name"],
                    "type": params["type"],
                    "value": inputs[params["name"]],
                }
            )

    return parameters


def create_struct_in_array_from_parameters(parameters, struct_name, index=0):
    struct = []
    for param in parameters:
        struct.append(
            "{struct_name}[{index}].{param_name} = {param_value};".format(
                struct_name=struct_name,
                index=index,
                param_name=param["name"],
                param_value=str(param["value"]).lower(),
            )
        )

    if len(parameters) == 0:
        return [""]

    return struct


def create_segmenter_debug_print_statement(sensor_count):
    seg_debug_line = 'printf("%d:'
    for i in range(sensor_count):
        seg_debug_line += " %d"
    seg_debug_line += '", i'
    for i in range(sensor_count):
        seg_debug_line += (
            ", *get_item_ptr(kb_models[model_index].pringb, {}, i)".format(i)
        )
    seg_debug_line += ");"

    return seg_debug_line


def get_params_str_list(function, inputs_dict):
    def get_input_val(parameter_name, param_list):
        for key, val in param_list.items():
            if str(key) == str(parameter_name).lower():
                return val

    def get_params_for_function(function):
        param_dict = {"num_params": 0, "params": []}

        for param in function.input_contract:
            if param.get("c_param", None) is not None:
                param_dict["num_params"] += 1
                param_dict["params"].append(
                    {
                        "name": param["name"],
                        "index": param["c_param"],
                        "c_param_mapping": param.get("c_param_mapping", None),
                        "default": param.get("default", None),
                    }
                )

        return param_dict

    params_dict = get_params_for_function(function)

    param_list = []
    for index, param in enumerate(params_dict["params"]):
        if param["name"] not in inputs_dict:
            value = param["default"]
        else:
            value = inputs_dict[param["name"]]

        if param.get("c_param_mapping", None) is not None:
            value = param["c_param_mapping"][value]

        param_list.append(f"input_params.data[{index}] = {value};")

    param_list.append(f"input_params.size = {params_dict['num_params']};")

    return param_list


def get_transform_parameters(inputs, input_contract):
    params = []

    for param_info in input_contract:
        if param_info["name"] in C_FUNCTION_IGNORED_INPUTS:
            continue

        if param_info.get("c_param", None) is None:
            continue

        try:
            value = inputs[param_info["name"]]
        except KeyError:
            value = param_info["default"]

        if param_info.get("c_param_mapping"):
            params.append(
                {
                    "value": param_info["c_param_mapping"][value],
                    "name": param_info["name"],
                    "index": param_info["c_param"],
                }
            )
        else:
            params.append(
                {
                    "value": value,
                    "name": param_info["name"],
                    "index": param_info["c_param"],
                }
            )

    return sorted(params, key=lambda x: x["index"])


def get_input_contract_info(key, input_contract):
    for param_info in input_contract:
        if param_info["name"] == key:
            return param_info

    return {}


def get_segment_inputs(step, function):
    segment_data = []

    if function.c_contract:
        for parameter in function.c_contract:
            segment_data.append(parameter)

    if step["name"] == "Double Peak Key Segmentation":
        segment_data.append({"name": "lasttwist", "type": "int32_t", "value": 0})
        segment_data.append({"name": "ts_state", "type": "int32_t", "value": 0})

        return segment_data

    if step["name"] == "Windowing Threshold Segmentation":
        threshold_space = step["inputs"].get("threshold_space", None)
        if threshold_space == "std":
            value = 1
        elif threshold_space == "absolute sum":
            value = 2
        elif threshold_space == "variance":
            value = 3
        elif threshold_space == "absolute sum":
            value = 4
        elif threshold_space == "absolute avg":
            value = 5
        elif threshold_space == "sum":
            value = 6
        else:
            raise Exception("Invalide Threshold Space.")

        segment_data.append(
            {"name": "thresholding_space", "type": "int32_t", "value": value}
        )

        comparison = step["inputs"].get("comparison", "maximum")

        if comparison == "maximum":
            value = 0
        elif comparison == "minimum":
            value = 1
        else:
            raise Exception("Invalid comparison.")

        segment_data.append({"name": "comparison", "type": "int32_t", "value": value})

        return segment_data

    if step["name"] == "Max Min Threshold Segmentation":
        segment_data.append(
            {"name": "valid_segment_flag", "type": "bool", "value": "false"}
        )
        segment_data.append(
            {"name": "searching_segment_flag", "type": "bool", "value": "false"}
        )
        threshold_space = step["inputs"].get("threshold_space", None)

        if threshold_space == "std":
            value = 1
        if threshold_space == "absolute sum":
            value = 2
        if threshold_space == "variance":
            value = 3
        if threshold_space == "absolute sum":
            value = 4
        if threshold_space == "absolute avg":
            value = 5
        if threshold_space == "sum":
            value = 6

        segment_data.append(
            {"name": "thresholding_space", "type": "int32_t", "value": value}
        )

        return segment_data

    if step["name"] == "General Threshold Segmentation":
        segment_data.append(
            {"name": "valid_segment_flag", "type": "bool", "value": "false"}
        )
        segment_data.append(
            {"name": "searching_segment_flag", "type": "bool", "value": "false"}
        )

        threshold_space = step["inputs"].get("first_threshold_space", None)
        if threshold_space:
            if threshold_space == "std":
                value = 1
            if threshold_space == "absolute sum":
                value = 2
            if threshold_space == "variance":
                value = 3
            if threshold_space == "absolute sum":
                value = 4
            if threshold_space == "absolute avg":
                value = 5
            if threshold_space == "sum":
                value = 6

            segment_data.append(
                {"name": "first_thresholding_space", "type": "int32_t", "value": value}
            )

        threshold_space = step["inputs"].get("second_threshold_space", None)
        if threshold_space:
            if threshold_space == "std":
                value = 1
            if threshold_space == "absolute sum":
                value = 2
            if threshold_space == "variance":
                value = 3
            if threshold_space == "absolute sum":
                value = 4
            if threshold_space == "absolute avg":
                value = 5
            if threshold_space == "sum":
                value = 6

            segment_data.append(
                {"name": "second_thresholding_space", "type": "int32_t", "value": value}
            )

        comparison_type = step["inputs"].get("first_comparison", None)
        if comparison_type:
            if comparison_type == "max":
                value = 1
            if comparison_type == "min":
                value = 2

            segment_data.append(
                {"name": "first_comparison", "type": "int32_t", "value": value}
            )

        comparison_type = step["inputs"].get("second_comparison", None)
        if comparison_type:
            if comparison_type == "max":
                value = 1
            if comparison_type == "min":
                value = 2

            segment_data.append(
                {"name": "second_comparison", "type": "int32_t", "value": value}
            )

        return segment_data

    return segment_data


def column_transform(column, column_type, model_index=0):
    # Sanitize column and set its max length

    column = re.sub(r"[^a-zA-Z0-9]", "_", column)
    column = column[:64]

    if column_type == "pipeline":
        return (
            column.upper()
            + "_D"
            + "_{}".format(c_model_name(model_index, add_index=False))
        )
    if column_type == "sensor":
        return (
            column.upper()
            + "_S"
            + "_{}".format(c_model_name(model_index, add_index=False))
        )


def get_model_group(knowledgepacks):
    """returns list of model groups, where the first in the list is the
    name of the parent node and the rest are its children"""

    group = {}
    for name in knowledgepacks:
        if knowledgepacks[name].get("parent", None) is None:
            group[name] = []

    for name in knowledgepacks:
        if knowledgepacks[name].get("parent", None) is not None:
            group[knowledgepacks[name]["parent"]].append(name)

    # flatten dict
    model_groups = []
    for key in group:
        model_groups.append([key] + group[key])

    return model_groups


def flatten_groups(model_groups):
    parents = []
    children = []
    for group in model_groups:
        parents.append(group[0])
        if len(group) > 1:
            children.extend(group[1:])

    return parents + children


def get_nearest_power_2_buffer(buffer_size):
    if buffer_size <= 0:
        return 0
    if buffer_size == 1:
        return 2

    return 2 ** (int(math.log(buffer_size - 1, 2) + 1))


def calc_feature_output_size(params, output_formula):
    return eval(output_formula)


def get_context_cumulative_features(feature_summary):
    generators = {}
    for feature in feature_summary:
        generators[feature["GeneratorTrueIndex"]] = feature["GeneratorFamilyFeatures"]

    cumulative_features = {}
    total = 0

    for key in sorted(generators.keys()):
        cumulative_features[key] = total
        total += generators[key]

    return cumulative_features, total


def reduce_context(feature_summary_df):
    feature_summary = feature_summary_df.to_dict(orient="records")

    cumulative_features, context_total = get_context_cumulative_features(
        feature_summary
    )

    context = []
    for feature in feature_summary:
        context.append(
            context_total * feature.get("CascadeIndex", 0)
            + cumulative_features[feature["GeneratorTrueIndex"]]
            + feature["GeneratorFamilyIndex"]
        )

    return context


def validate_capture_config(platform, capture_config):
    cap_config_name = capture_config.configuration.get("name", None)
    platform_name = platform.name
    if platform.can_build_binary and cap_config_name is not None:
        # [SDL-1939] Only need this for binary builds.
        if cap_config_name.lower().split()[0] not in platform_name.lower() and (
            # Below is for quickai merced boards only. the name in platform does not match name in cap configs from DCL
            "merced" in platform_name.lower()
            and "quickai" not in cap_config_name.lower()
        ):
            raise KnowledgePackGenerationError(
                "The selected data source {} isn't a valid configuration for {}".format(
                    cap_config_name, platform_name
                )
            )

    return True


def get_feature_scale_value(table: dict, name: str) -> float:
    """
    if min max scale was performed before feature cascade, the values will not match up,
    here we map them back to the actual values

    """

    if table.get(name, None) is not None:
        return float(table[name])

    elif name[:5] == "gen_c" and table.get(name[10:], None) is not None:
        return float(table[name[10:]])

    raise Exception("Feature Name {} is not in feature transform".format(name))


def get_classifier_type(knowledgepack):
    classifier_type = (
        knowledgepack["knowledgepack"]
        .device_configuration.get("classifier")
        .lower()
        .replace(" ", "_")
    )

    if classifier_type == "tensorflow_lite_for_microcontrollers":
        classifier_type = "tf_micro"

    return classifier_type
