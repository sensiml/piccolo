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

import binascii

import codegen.model_gen.utils as utils


def to_c_hex(tflite_model):
    hex_str = binascii.hexlify(tflite_model).decode()
    return (
        "".join(
            ["0x{}, ".format(hex_str[i : i + 2]) for i in range(0, len(hex_str), 2)]
        )[:-2],
        len(hex_str) // 2,
    )


def create_tf_micro_classifier_arrays(model_index, model):
    outputs = []

    def assign_aligned_values(
        model_index, name, values, value_size, value_type="uint8_t"
    ):
        return "const {value_type} {name}_{model_index}[{value_size}] DATA_ALIGN_ATTRIBUTE = {{{values}}};".format(
            model_index=model_index,
            name=name,
            values=values,
            value_size=value_size,
            value_type=value_type,
        )

    def allocate_aligned_data_array(model_index, name, size, value_type="uint8_t"):
        return "{value_type} {name}_{model_index}[{size}] DATA_ALIGN_ATTRIBUTE;".format(
            model_index=model_index, name=name, size=size, value_type=value_type
        )

    converted_model, model_size = to_c_hex(
        binascii.unhexlify(model["tflite"].encode("ascii"))
    )

    outputs.append(
        assign_aligned_values(
            model_index, "model_data_tf_micro", converted_model, model_size
        )
    )

    outputs.append(
        allocate_aligned_data_array(
            model_index, "tensor_arena_tf_micro", model["tensor_arena_size"]
        )
    )

    return outputs


def create_tf_micro_classifier_struct(model_index, model):
    outputs = []

    outputs.append("tf_micro_t tf_micro_model_{0}  = ".format(model_index) + "{")

    outputs.append("};")

    return outputs


def create_classifier_structures(models):
    outputs = []

    iterations = 0
    for model in models:
        if model["classifier_config"].get("classifier", "PME") in [
            "TF Micro",
            "TensorFlow Lite for Microcontrollers",
            "Neural Network",
        ]:
            outputs.extend(
                create_tf_micro_classifier_arrays(iterations, model["model_arrays"])
            )
            iterations += 1

    iterations = 0

    outputs.append(
        (
            "tf_micro_classifier_rows_t tf_micro_classifier_rows[{}] = ".format(
                utils.get_number_classifiers(
                    models, "TensorFlow Lite for Microcontrollers"
                )
            )
            + "{"
        )
    )

    for model in models:
        if model["classifier_config"].get("classifier", "PME") in [
            "TF Micro",
            "TensorFlow Lite for Microcontrollers",
            "Neural Network",
        ]:
            outputs.append("\n\t{")
            outputs.append(
                "\t\t.num_inputs = {0},".format(model["model_arrays"]["num_inputs"])
            )
            outputs.append(
                "\t\t.num_outputs = {0},".format(model["model_arrays"]["num_outputs"])
            )

            outputs.append(
                "\t\t.model_data = model_data_tf_micro_{0},".format(iterations)
            )
            outputs.append(
                "\t\t.threshold = {0},".format(
                    model["model_arrays"].get("threshold", 0.0) * 256
                    - 127  # convert to int8 value
                )
            )
            outputs.append(
                "\t\t.kTensorArenaSize = {0},".format(
                    model["model_arrays"].get("tensor_arena_size")
                )
            )
            outputs.append(
                "\t\t.tensor_arena = tensor_arena_tf_micro_{0},".format(iterations)
            )
            outputs.append(
                "\t\t.scale_factor = {0},".format(
                    1 / model["model_arrays"].get("input_quantization", (1, 0))[0]
                )
            )
            outputs.append(
                "\t\t.zero_bias = {0},".format(
                    model["model_arrays"].get("input_quantization", (1, 0))[1]
                )  # include the offset for shift to uint8
            )

            c_estimator_type_param_map = {
                "classification": "ESTIMATOR_TYPE_CLASSIFICATION",
                "regression": "ESTIMATOR_TYPE_REGRESSION",
            }
            outputs.append(
                "\t\t.estimator_type = {0},".format(
                    c_estimator_type_param_map[
                        model["model_arrays"].get("estimator_type", "classification")
                    ]
                )
            )
            outputs.append("\t},")
            iterations += 1

    outputs.append("};")

    return outputs


def create_max_tmp_parameters(kb_models):
    max_number_classes = 0
    max_number_inputs = 0

    for model in kb_models:
        if model["classifier_config"].get("classifier", "PME") in [
            "TF Micro",
            "TensorFlow Lite for Microcontrollers",
        ]:
            if max_number_classes < model["model_arrays"]["num_outputs"]:
                max_number_classes = model["model_arrays"]["num_outputs"]
            if max_number_inputs < model["model_arrays"]["num_inputs"]:
                max_number_inputs = model["model_arrays"]["num_inputs"]

    return [
        "#define TF_MICRO_MAX_NUMBER_RESULTS {}".format(max_number_classes),
        "#define TF_MICRO_MAX_NUMBER_INPUTS {}".format(max_number_inputs),
    ]


def validate_model_parameters(data):
    cleaned_data = {}
    cleaned_data["num_inputs"] = data["num_inputs"]
    cleaned_data["num_outputs"] = data["num_outputs"]
    cleaned_data["estimator_type"] = data["estimator_type"]
    cleaned_data["tensor_arena_size"] = data["tensor_arena_size"]
    cleaned_data["input_quantization"] = data["input_quantization"]
    cleaned_data["threshold"] = data["threshold"]
    cleaned_data["tflite"] = data["tflite"]

    return cleaned_data


def validate_model_configuration(data):
    return data


def get_output_tensor_size(model):
    return model["model_arrays"]["num_outputs"]
