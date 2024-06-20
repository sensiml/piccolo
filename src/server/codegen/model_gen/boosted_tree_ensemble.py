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
from pandas import DataFrame


def create_boosted_tree_classifier_arrays(model_index, models):
    from library.classifiers.boosted_tree_ensemble import gtree_t

    outputs = []

    def assign_values(model_index, name, index, values, value_type="uint8_t"):
        node_count = len(values)
        return "{5} model_{0}_{1}_boosted_tree_{2}[{4}] = {{{3}}};".format(
            model_index, name, index, str(values)[1:-1], node_count, value_type
        )

    def clean(values):
        return [int(x) if x >= 0 else 0 for x in values]

    def clean_float(values):
        return [float(x) for x in values]

    tree_groups = DataFrame(models).groupby("Tree")

    for index, tree_model in tree_groups:
        # models.append(gtree_t(group))
        # for index, tree_model in enumerate(models):
        model = gtree_t(tree_model)
        outputs.append(
            assign_values(model_index, "node_list", index, clean(model.node_list))
        )
        outputs.append(
            assign_values(
                model_index,
                "leafs",
                index,
                clean_float(model.leafs),
                value_type="float",
            )
        )
        outputs.append(
            assign_values(model_index, "threshold", index, clean(model.threshold))
        )
        outputs.append(
            assign_values(model_index, "features", index, clean(model.features))
        )

    return outputs


def create_boosted_tree_classifier_struct(model_index, models):
    outputs = []

    tree_groups = DataFrame(models).groupby("Tree")

    outputs.append(
        "boosted_tree_t boosted_tree_ensemble_models_{0}[{1}] = ".format(
            model_index, len(tree_groups)
        )
        + "{"
    )
    for index, _ in enumerate(tree_groups):
        outputs.append("\t{")
        outputs.append(
            "\t\t.node_list = model_{1}_node_list_boosted_tree_{0},".format(
                index, model_index
            )
        )
        outputs.append(
            "\t\t.leafs = model_{1}_leafs_boosted_tree_{0},".format(index, model_index)
        )
        outputs.append(
            "\t\t.threshold = model_{1}_threshold_boosted_tree_{0},".format(
                index, model_index
            )
        )
        outputs.append(
            "\t\t.features = model_{1}_features_boosted_tree_{0},".format(
                index, model_index
            )
        )
        outputs.append("\t},")
    outputs.append("};")

    return outputs


def create_classifier_structures(kb_models):
    """
    typedef struct tree{
        uint8_t *node_list;
        float *leafs;
        uint8_t *threshold;
        uint8_t *features;
    } tree_t;


    typedef struct tree_ensemble_classifier_rows{
        uint8_t number_of_trees;
        tree_t * tree_ensemble;
    } tree_ensemble_classifier_rows_t;

    """
    output = []

    iterations = 0
    for model in kb_models:
        if (
            model["classifier_config"].get("classifier", "PME")
            == "Boosted Tree Ensemble"
        ):
            output.extend(
                create_boosted_tree_classifier_arrays(iterations, model["model_arrays"])
            )
            output.extend(
                create_boosted_tree_classifier_struct(iterations, model["model_arrays"])
            )
            iterations += 1

    iterations = 0
    output.append(
        (
            "boosted_tree_ensemble_classifier_rows_t boosted_tree_ensemble_classifier_rows[{}] = ".format(
                utils.get_number_classifiers(kb_models, "Boosted Tree Ensemble")
            )
            + "{"
        )
    )

    for model in kb_models:
        if (
            model["classifier_config"].get("classifier", "PME")
            == "Boosted Tree Ensemble"
        ):
            tree_groups = DataFrame(model["model_arrays"]).groupby("Tree")
            output.append("\n\t{")
            output.append("\t\t.number_of_trees = {},".format(len(tree_groups)))
            output.append(
                "\t\t.boosted_tree_ensemble = boosted_tree_ensemble_models_{},".format(
                    iterations
                )
            )
            output.append("\t},")
            iterations += 1

    output.append("};")

    return output


def validate_model_parameters(data):
    cleaned_data = data

    return cleaned_data


def validate_model_configuration(data):
    return data


def create_max_tmp_parameters(kb_models):
    return []


def get_output_tensor_size(model):
    return len(model["class_map"])
