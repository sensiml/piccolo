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

import re


def create_pme_classifier_distance_optimizations(models):
    # enable_dtw_distance, max_warp_length
    uses_dtw_dstance = False
    feature_vector_size = 0

    for model in models:
        if model["classifier_config"].get("classifier", None) == "PME":
            if model["classifier_config"].get("distance_mode", None) in [
                "KB_DISTANCE_DTW"
            ]:
                feature_vector_size = max(
                    feature_vector_size, model.get("feature_vector_size")
                )
                uses_dtw_dstance = True

    if uses_dtw_dstance:
        return {
            "enable_dtw_distance": ["#define ENABLE_DTW_DISTANCE 1"],
            "max_warp_length": [
                "#define MAX_WARP_LENGTH {}".format(feature_vector_size)
            ],
        }

    return {}


def get_number_neurons(model_data):
    return len(model_data["model_arrays"])


def get_number_classifiers(models_data, classifier_type):
    num_classifiers = 0
    for model in models_data:
        if model["classifier_config"].get("classifier", "PME") == classifier_type:
            num_classifiers += 1

    return num_classifiers


def get_number_of_categories(class_map):
    return len(class_map.keys())


def create_max_neuron_memory(models_data):
    total = 0
    for model in models_data:
        if model["classifier_config"].get("classifier", "PME") == "PME":
            new_total = get_number_neurons(model) + model["classifier_config"].get(
                "reserved_patterns", 0
            )
            if total < new_total:
                total = new_total

    return ["#define MEMORY_PME_MAX {}".format(total)]


def create_number_pme_classifiers(models_data):
    """Create the pattern matching definitions"""
    pme_define = []
    num_pme_classifiers = get_number_classifiers(models_data, "PME")

    pme_define.append("#define KB_NUM_PME_CLASSIFIERS ({})".format(num_pme_classifiers))

    return pme_define


def create_number_pme_qm_classifiers(models_data):
    """Create the pattern matching definitions"""
    pme_define = []
    num_pme_classifiers = get_number_classifiers(models_data, "PME")

    pme_define.append("#define PME_MAX_CLASSIFIERS ({})".format(num_pme_classifiers))

    return pme_define


def create_number_of_neurons(models_data):
    number_of_neurons = []
    total = 0
    iterations = 0
    for model in models_data:
        if model["classifier_config"].get("classifier", "PME") == "PME":
            total += get_number_neurons(model) + model["classifier_config"].get(
                "reserved_patterns", 0
            )
            number_of_neurons.append(
                "#define NUM_NEURONS_{} ({})".format(
                    iterations, get_number_neurons(model)
                )
            )
            number_of_neurons.append(
                "#define MAX_NUM_NEURONS_{} ({})".format(
                    iterations,
                    get_number_neurons(model)
                    + model["classifier_config"].get("reserved_patterns", 0),
                )
            )
            number_of_neurons.append(
                "#define NUM_CLASSES_{} ({})".format(
                    iterations, get_number_of_categories(model["class_map"])
                )
            )

            iterations += 1
    number_of_neurons.append("#define KB_TOTAL_NUMBER_OF_NEURONS ({})".format(total))

    return number_of_neurons


def create_pme_max_vector_size(models):
    ret = []
    feature_vector_size = 0
    for model in models:
        feature_vector_size = max(feature_vector_size, model.get("feature_vector_size"))
    ret = [
        "#define QM_PME_MAX_VECTOR_LENGTH {0}".format(feature_vector_size),
        "#define PME_COMMON_MAX_VECTOR_LENGTH {0}".format(feature_vector_size),
    ]

    return ret


def create_pme_max_class_size(models):
    number_classes = 0
    for model in models:
        number_classes = max(number_classes, len(list(model["class_map"].keys())))

    return ["#define QM_PME_MAX_CATEGORY_LENGTH {0}".format(number_classes)]


def create_pme_neuron_array(
    iteration_num,
    neuron_array,
    class_map,
    reserved_patterns=0,
    reinforcement_learning=False,
):
    neuron_vector = []
    neuron_attributes = []
    neuron_scores = []

    num_categories = get_number_of_categories(class_map)
    category_str = ",".join(["0" for _ in range(num_categories)])

    neuron_vector.append(
        "static qm_pme_neuron_vector_t kb_neuron_vectors_{0}[MAX_NUM_NEURONS_{0}] = ".format(
            iteration_num
        )
    )

    neuron_vector.append("{")
    neuron_attributes.append(
        "qm_pme_neuron_attribute_t kb_neuron_attribs_{0}[MAX_NUM_NEURONS_{0}] = ".format(
            iteration_num
        )
    )
    neuron_attributes.append("{")
    neuron_scores.append(
        "qm_pme_stored_score_t kb_neuron_scores_{0}[MAX_NUM_NEURONS_{0}] = ".format(
            iteration_num
        )
    )
    neuron_scores.append("{")
    for neuron in neuron_array:
        neuron_vector.append(
            "\t{.vector={" + re.sub(r"[\[\]]", "", str(neuron["Vector"])) + "}},"
        )
        neuron_attributes.append(
            "\t{ .influence="
            + str(neuron["AIF"])
            + ", .category="
            + str(neuron["Category"])
            + " },"
        )
        neuron_scores.append("\t{ .error=0, .class_vector={" + category_str + "} },")

    blank_neuron = [0 for x in range(len(neuron_array[0]["Vector"]))]
    for neuron in range(reserved_patterns):
        neuron_vector.append(
            "\t{.vector={" + re.sub(r"[\[\]]", "", str(blank_neuron)) + "}},"
        )
        neuron_attributes.append("\t{ .influence=0, .category=0},")
        neuron_scores.append("\t{ .error=0, .class_vector={" + category_str + "} },")
    neuron_vector.append("};")
    neuron_attributes.append("};")
    neuron_scores.append("};")

    ret = []
    ret.extend(neuron_vector)
    ret.extend(neuron_attributes)

    if reinforcement_learning:
        ret.extend(neuron_scores)

    return ret


def create_trained_model_header_fills(kb_models):
    # // FILL_PME_TRAINED_MODEL_HEADER

    # PME CLASSIFIER FILLS
    output = create_number_of_neurons(kb_models)
    output.extend(create_number_pme_classifiers(kb_models))

    return output


def create_max_tmp_parameters(kb_models):
    output = create_max_neuron_memory(kb_models)
    output.extend(create_pme_max_vector_size(kb_models))
    output.extend(create_pme_max_class_size(kb_models))
    output.extend(create_number_pme_qm_classifiers(kb_models))

    return output


def create_classifier_structures(kb_models):
    ret = []
    middleware_rows = []
    iteration = 0
    num_pme_classifiers = get_number_classifiers(kb_models, "PME")
    classifier_row_def = "kb_classifier_row_t kb_classifier_rows[{}]".format(
        num_pme_classifiers
    )
    classifier_row_def += " = {\n\t"
    middleware_rows.append(classifier_row_def)

    for _, model in enumerate(kb_models):
        if model["classifier_config"].get("classifier", "PME") in ["PME"]:
            ret.extend(
                create_pme_neuron_array(
                    iteration,
                    model["model_arrays"],
                    model["class_map"],
                    model["classifier_config"].get("reserved_patterns", 0),
                    model["classifier_config"].get("reinforcement_learning", False),
                )
            )
            middleware_rows.append("\n\t{")
            middleware_rows.append("\t\t.classifier_id={},".format(iteration))
            middleware_rows.append(
                "\t\t.num_patterns=NUM_NEURONS_{},".format(iteration)
            )
            middleware_rows.append(
                "\t\t.pattern_size={},".format(model["feature_vector_size"])
            )
            middleware_rows.append(
                "\t\t.max_patterns=MAX_NUM_NEURONS_{},".format(iteration)
            )
            middleware_rows.append("\t\t.num_classes=NUM_CLASSES_{},".format(iteration))
            middleware_rows.append(
                "\t\t.num_channels={},".format(
                    model["classifier_config"]["num_channels"]
                )
            )
            middleware_rows.append(
                "\t\t.classifier_mode={},".format(
                    model["classifier_config"]["classification_mode"]
                )
            )
            middleware_rows.append(
                "\t\t.norm_mode={},".format(model["classifier_config"]["distance_mode"])
            )

            middleware_rows.append(
                "\t\t.stored_patterns=kb_neuron_vectors_{},".format(iteration)
            )
            middleware_rows.append(
                "\t\t.stored_attribs=kb_neuron_attribs_{},".format(iteration)
            )
            if model["classifier_config"].get("reinforcement_learning", False):
                middleware_rows.append(
                    "\t\t.stored_scores=kb_neuron_scores_{},".format(iteration)
                )

            middleware_rows.append("\t},")
            iteration += 1

    middleware_rows.append("};")
    ret.extend(middleware_rows)
    return ret


def direct_model_data_updates(kb_models):
    return create_pme_classifier_distance_optimizations(kb_models)


def validate_model_parameters(data):
    cleaned_data = data

    return cleaned_data


def validate_model_configuration(data):
    return data


def get_output_tensor_size(kb_models):
    return 4
