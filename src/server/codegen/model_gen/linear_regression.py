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


def create_linear_regression_arrays(model_index, model):
    outputs = []

    def assign_values(model_index, name, values, value_type="uint8_t"):
        return f"{value_type} model_{model_index}_{name}_linear_regression[{len(values)}] = {{{ str(values)[1:-1]}}};"

    def clean_float(values):
        return [float(x) for x in values]

    outputs.append(
        assign_values(
            model_index,
            "coefficients",
            clean_float(model["coefficients"]),
            value_type="float_t",
        )
    )

    return outputs


def create_linear_regression_struct(model_index, model):
    outputs = []

    outputs.append(
        f"linear_regression_model_t linear_regression_model_{model_index} = {{"
    )
    outputs.append(
        f"\t\t.coefficients = model_{model_index}_coefficients_linear_regression,"
    )

    outputs.append(f"\t\t.num_coefficients = {len(model['coefficients'])},")

    outputs.append(f"\t\t.intercept = {model['intercept']},")

    outputs.append("};")

    return outputs


def create_classifier_structures(kb_models):
    """

    typedef struct linear_regression_model
    {
        float_t *coefficients;
        int32_t num_coefficients;
    } linear_regression_model_t;


    typedef struct linear_regression_model_rows
    {
        linear_regression_model_t *model;
        float_t result;
    } linear_regression_model_rows_t;

    """
    output = []

    iterations = 0
    for model in kb_models:
        if model["classifier_config"].get("classifier") == "Linear Regression":
            output.extend(
                create_linear_regression_arrays(iterations, model["model_arrays"])
            )
            output.extend(
                create_linear_regression_struct(iterations, model["model_arrays"])
            )
            iterations += 1

    iterations = 0
    output.append(
        (
            "linear_regression_model_rows_t linear_regression_rows[{}] = ".format(
                utils.get_number_classifiers(kb_models, "Linear Regression")
            )
            + "{"
        )
    )

    for model in kb_models:
        if model["classifier_config"].get("classifier") == "Linear Regression":
            output.append("\n\t{")
            output.append(f"\t\t.model = &linear_regression_model_{iterations},")
            output.append("\t},")
            iterations += 1

    output.append("};")

    return output


def create_max_tmp_parameters(kb_models):
    pass

    for model in kb_models:
        if model["classifier_config"].get("classifier", "PME") == "Linear Regression":
            pass

    return []


def validate_model_parameters(data):
    cleaned_data = data

    return cleaned_data


def validate_model_configuration(data):
    return data


def get_output_tensor_size(model):
    max_classifier = 0

    return max_classifier
