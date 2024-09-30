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


def create_classifier_arrays(model_index, model):
   
    pass


def create_classifier_struct(model_index, model):
    pass


def create_classifier_structures(models):
    """ typedef struct nnom_classifier_rows
        {
            uint16_t num_inputs;
            uint8_t num_outputs;
            float threshold;
            uint8_t estimator_type;
            nnom_model_t* model;
        } nnom_classifier_rows_t;
    """
    
    outputs = []

    iterations = 0
    for model in models:
        if model["classifier_config"].get("classifier", "PME") in [
            "TF Micro",
            "TensorFlow Lite for Microcontrollers",
            "Neural Network"
        ]:
            #outputs.extend(
            #    create_tf_micro_classifier_arrays(iterations, model["model_arrays"])
            #)
            iterations += 1

    iterations = 0

    outputs.append(
        (
            "nnom_classifier_rows_t nnom_classifier_rows[{}] = ".format(
                utils.get_number_classifiers(
                    models, "TF Micro"
                )+utils.get_number_classifiers(
                    models, "TensorFlow Lite for Microcontrollers"
                )+utils.get_number_classifiers(
                    models, "Neural Network"
                )
            )
            + "{"
        )
    )

    for model in models:
        if model["classifier_config"].get("classifier", "PME") in [
            "TF Micro",
            "TensorFlow Lite for Microcontrollers",
             "Neural Network"
        ]:
            outputs.append("\n\t{")
            outputs.append(
                "\t\t.num_inputs = {0},".format(model["model_arrays"]["num_inputs"])
            )
            outputs.append(
                "\t\t.num_outputs = {0},".format(model["model_arrays"]["num_outputs"])
            )
            outputs.append(
                "\t\t.threshold = {0},".format(
                    model["model_arrays"].get("threshold", 0.0) * 256
                    - 127  # convert to int8 value
                )
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
   return []

def validate_model_parameters(data):
    pass

def validate_model_configuration(data):
    return data


def get_output_tensor_size(model):
    pass
