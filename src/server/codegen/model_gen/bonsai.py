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

import codegen.model_gen.utils as utils


def create_bonsai_classifier_arrays(model_index, model, sizes):
    outputs = []

    def assign_values(model_index, name, values, value_type="float"):
        return "{4} {1}_bonsai_{0}[{3}] = {{{2}}};".format(
            model_index, name, str(values)[1:-1], len(values), value_type
        )

    def clean(values, size):
        return [float(values[i]) for i in range(size)]

    outputs.append(assign_values(model_index, "V", clean(model.V, sizes["V"])))
    outputs.append(assign_values(model_index, "W", clean(model.W, sizes["W"])))
    outputs.append(
        assign_values(model_index, "Theta", clean(model.Theta, sizes["Theta"]))
    )
    outputs.append(assign_values(model_index, "Z", clean(model.Z, sizes["Z"])))
    outputs.append(assign_values(model_index, "X", clean(model.X, sizes["X"])))
    outputs.append(assign_values(model_index, "mean", clean(model.mean, sizes["Mean"])))

    return outputs


def create_bonsai_classifier_struct(model_index, model):
    outputs = []

    outputs.append("bonsai_t bonsai_model_{0} = ".format(model_index) + "{")
    outputs.append("\t\t.Theta = Theta_bonsai_{0},".format(model_index))
    outputs.append("\t\t.W = W_bonsai_{0},".format(model_index))
    outputs.append("\t\t.V = V_bonsai_{0},".format(model_index))
    outputs.append("\t\t.Z = Z_bonsai_{0},".format(model_index))
    outputs.append("\t\t.X = X_bonsai_{0},".format(model_index))
    outputs.append("\t\t.mean = mean_bonsai_{0},".format(model_index))
    outputs.append("\t\t.depth = {0},".format(model.depth))
    outputs.append("\t\t.d_l = {0},".format(model.d_l))
    outputs.append("\t\t.d_input = {0},".format(model.d_input))
    outputs.append("\t\t.d_proj = {0},".format(model.d_proj))
    outputs.append("\t\t.num_nodes = {0},".format(model.num_nodes))
    outputs.append("};")

    return outputs


def create_classifier_structures(models):
    from library.classifiers.bonsai import get_bonsai_c_struct

    outputs = []

    iterations = 0
    for model in models:
        if model["classifier_config"].get("classifier", "PME") == "Bonsai":
            bonsai, sizes = get_bonsai_c_struct(model["model_arrays"])

            outputs.extend(create_bonsai_classifier_arrays(iterations, bonsai, sizes))
            outputs.extend(create_bonsai_classifier_struct(iterations, bonsai))
            iterations += 1

    iterations = 0

    outputs.append(
        (
            "bonsai_classifier_rows_t bonsai_classifier_rows[{}] = ".format(
                utils.get_number_classifiers(models, "Bonsai")
            )
            + "{"
        )
    )

    for model in models:
        if model["classifier_config"].get("classifier", None) == "Bonsai":
            outputs.append("\n\t{")
            outputs.append("\t\t.bonsai = &bonsai_model_{},".format(iterations))
            outputs.append("\t},")
            iterations += 1

    outputs.append("};")

    return outputs


def create_max_tmp_parameters(kb_models):
    max_projection = 0
    max_input_dimensions = 0
    max_num_nodes = 0
    max_number_classes = 0

    for model in kb_models:
        if model["classifier_config"].get("classifier", "PME") == "Bonsai":
            if max_projection < model["model_arrays"]["projection_dimension"]:
                max_projection = model["model_arrays"]["projection_dimension"]
            if max_input_dimensions < model["model_arrays"]["num_features"]:
                max_input_dimensions = model["model_arrays"]["num_features"]
            if max_num_nodes < model["model_arrays"]["num_nodes"]:
                max_num_nodes = model["model_arrays"]["num_nodes"]
            if max_number_classes < model["model_arrays"]["num_classes"]:
                max_number_classes = model["model_arrays"]["num_classes"]

    return [
        "#define MAX_PROJECTION_DIMENSION {}".format(max_projection),
        "#define MAX_INPUT_DIMENSION {}".format(max_input_dimensions),
        "#define MAX_NUM_NODES {}".format(max_num_nodes),
        "#define MAX_NUMBER_CLASSES {}".format(max_number_classes),
    ]


def validate_model_parameters(data):
    cleaned_data = data

    return cleaned_data


def validate_model_configuration(data):
    return data


def get_output_tensor_size(model):
    return 0
