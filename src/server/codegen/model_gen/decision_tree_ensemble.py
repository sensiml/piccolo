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


def create_dte_tree_ensemble_arrays(model_index, models):
    outputs = []

    def assign_uint8_t_values(model_index, name, index, values):
        node_count = len(values)
        return "uint8_t model_{0}_{1}_tree_{2}[{4}] = {{{3}}};".format(
            model_index, name, index, str(values)[1:-1], node_count
        )

    def assign_uint16_t_values(model_index, name, index, values):
        node_count = len(values)
        return "uint16_t model_{0}_{1}_tree_{2}[{4}] = {{{3}}};".format(
            model_index, name, index, str(values)[1:-1], node_count
        )

    def clean(values):
        return [int(x) if x >= 0 else 0 for x in values]

    for index, model in enumerate(models):
        outputs.append(
            assign_uint16_t_values(
                model_index, "left_children", index, clean(model["children_left"])
            )
        )
        outputs.append(
            assign_uint16_t_values(
                model_index, "right_children", index, clean(model["children_right"])
            )
        )
        outputs.append(
            assign_uint8_t_values(
                model_index, "threshold", index, clean(model["threshold"])
            )
        )
        outputs.append(
            assign_uint16_t_values(
                model_index, "features", index, clean(model["feature"])
            )
        )

    return outputs


def create_tree_ensemble_struct(model_index, models):
    outputs = []
    outputs.append(
        "tree_t forest_ensemble_models_{0}[{1}] = ".format(model_index, len(models))
        + "{"
    )
    for index, _ in enumerate(models):
        outputs.append("\t{")
        outputs.append(
            "\t\t.left_children = model_{1}_left_children_tree_{0},".format(
                index, model_index
            )
        )
        outputs.append(
            "\t\t.right_children = model_{1}_right_children_tree_{0},".format(
                index, model_index
            )
        )
        outputs.append(
            "\t\t.threshold = model_{1}_threshold_tree_{0},".format(index, model_index)
        )
        outputs.append(
            "\t\t.features = model_{1}_features_tree_{0},".format(index, model_index)
        )
        outputs.append("\t},")
    outputs.append("};")

    return outputs


def create_classifier_structures(kb_models):
    """
    typedef struct tree{
        uint16_t *left_children;
        uint16_t *right_children;
        uint8_t *threshold;
        uint8_t *features;
    } tree_t;


    typedef struct tree_ensemble_classifier_rows{
        uint8_t number_of_classes;
        uint8_t number_of_trees;
        tree_t * tree_ensemble;
    } tree_ensemble_classifier_rows_t;

    """
    output = []

    iterations = 0
    for model in kb_models:
        if (
            model["classifier_config"].get("classifier", "PME")
            == "Decision Tree Ensemble"
        ):
            output.extend(
                create_dte_tree_ensemble_arrays(iterations, model["model_arrays"])
            )
            output.extend(
                create_tree_ensemble_struct(iterations, model["model_arrays"])
            )
            iterations += 1

    iterations = 0
    output.append(
        (
            "tree_ensemble_classifier_rows_t tree_ensemble_classifier_rows[{}] = ".format(
                utils.get_number_classifiers(kb_models, "Decision Tree Ensemble")
            )
            + "{"
        )
    )

    for model in kb_models:
        if (
            model["classifier_config"].get("classifier", "PME")
            == "Decision Tree Ensemble"
        ):
            output.append("\n\t{")
            output.append(
                "\t\t.number_of_classes={},".format(
                    len(model["model_arrays"][0]["classes"])
                )
            )
            output.append("\t\t.number_of_trees={},".format(len(model["model_arrays"])))
            output.append(
                "\t\t.tree_ensemble=forest_ensemble_models_{},".format(iterations)
            )
            output.append("\t},")
            iterations += 1

    output.append("};")

    return output


def create_max_tmp_parameters(kb_models):
    max_classifier = 0

    for model in kb_models:
        if model["classifier_config"].get("classifier") == "Decision Tree Ensemble":
            if max_classifier < len(model["model_arrays"][0]["classes"]):
                max_classifier = len(model["model_arrays"][0]["classes"])

    return ["#define MAX_DTE_CLASSIFICATIONS {}".format(max_classifier)]


def get_output_tensor_size(model):
    return len(model["model_arrays"][0]["classes"])


def validate_model_parameters(data):
    cleaned_data = data

    return cleaned_data


def validate_model_configuration(data):
    return data
