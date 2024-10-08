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

from codegen.model_gen import (
    bonsai,
    boosted_tree_ensemble,
    decision_tree_ensemble,
    linear_regression,
    pme,
    tf_micro,
    nnom,
)
from django.core.exceptions import ValidationError

ALLOWED_CLASSIFIER_TYPES = [
    "tf_micro",
    "decision_tree_ensemble",
    "boosted_tree_ensemble",
    "bonsai",
    "pme",
    "linear_regression",
    "nnom",
]

CLASSIFER_MAP = {
    "decision tree ensemble": "decision_tree_ensemble",
    "tensorflow lite for microcontrollers": "tf_micro",
    "Neural Network": "tf_micro",
    "nnom": "nnom",
    "pme": "pme",
    "boosted tree ensemble": "boosted_tree_ensemble",
    "bonsai": "bonsai",
    "linear regression": "linear_regression",
}


def get_classifier_type(model_configuration):
    if not model_configuration.get("classifier"):
        raise ValidationError("No classifier specified!")

    classifier_type = CLASSIFER_MAP.get(model_configuration["classifier"].lower())

    if classifier_type is None:
        raise ValidationError("Invalid Classifier!")

    return classifier_type.lower()


# TODO: Make this an interface that returns the object instead of having all of these if statements
class ModelGen:
    @staticmethod
    def create_classifier_structures(classifier_type, kb_models):
        if classifier_type == "tf_micro":
            return tf_micro.create_classifier_structures(kb_models)

        if classifier_type == "decision_tree_ensemble":
            return decision_tree_ensemble.create_classifier_structures(kb_models)

        if classifier_type == "boosted_tree_ensemble":
            return boosted_tree_ensemble.create_classifier_structures(kb_models)

        if classifier_type == "bonsai":
            return bonsai.create_classifier_structures(kb_models)

        if classifier_type == "pme":
            return pme.create_classifier_structures(kb_models)

        if classifier_type == "linear_regression":
            return linear_regression.create_classifier_structures(kb_models)

        if classifier_type == "nnom":
            return nnom.create_classifier_structures(kb_models)

        return ""

    @staticmethod
    def create_max_tmp_parameters(classifier_type, kb_models):
        if classifier_type == "tf_micro":
            return tf_micro.create_max_tmp_parameters(kb_models)

        if classifier_type == "decision_tree_ensemble":
            return decision_tree_ensemble.create_max_tmp_parameters(kb_models)

        if classifier_type == "boosted_tree_ensemble":
            return boosted_tree_ensemble.create_max_tmp_parameters(kb_models)

        if classifier_type == "bonsai":
            return bonsai.create_max_tmp_parameters(kb_models)

        if classifier_type == "pme":
            return pme.create_max_tmp_parameters(kb_models)

        if classifier_type == "linear_regression":
            return linear_regression.create_max_tmp_parameters(kb_models)

        if classifier_type == "nnom":
            return nnom.create_max_tmp_parameters(kb_models)

        return ""

    @staticmethod
    def create_trained_model_header_fills(classifier_type, kb_models):
        # // FILL_PME_TRAINED_MODEL_HEADER

        if classifier_type == "pme":
            return pme.create_trained_model_header_fills(kb_models)

        return ""

    @staticmethod
    def create_direct_model_updates(classifier_type, kb_models):
        """Any updates that don't fit into the structure of the other fill scripts above."""
        if classifier_type == "pme":
            return pme.direct_model_data_updates(kb_models)

        return {}

    @staticmethod
    def validate_model_parameters(model_parameters, model_configuration):
        classifier_type = get_classifier_type(model_configuration)

        if classifier_type == "tf_micro":
            return tf_micro.validate_model_parameters(model_parameters)

        if classifier_type == "decision_tree_ensemble":
            return decision_tree_ensemble.validate_model_parameters(model_parameters)

        if classifier_type == "boosted_tree_ensemble":
            return boosted_tree_ensemble.validate_model_parameters(model_parameters)

        if classifier_type == "bonsai":
            return bonsai.validate_model_parameters(model_parameters)

        if classifier_type == "pme":
            return pme.validate_model_parameters(model_parameters)

        if classifier_type == "linear_regression":
            return linear_regression.validate_model_parameters(model_parameters)

        if classifier_type == "nnom":
            return nnom.validate_model_parameters(model_parameters)

    @staticmethod
    def validate_model_configuration(model_configuration):
        classifier_type = get_classifier_type(model_configuration)

        if classifier_type == "tf_micro":
            return tf_micro.validate_model_configuration(model_configuration)

        if classifier_type == "decision_tree_ensemble":
            return decision_tree_ensemble.validate_model_configuration(
                model_configuration
            )

        if classifier_type == "boosted_tree_ensemble":
            return boosted_tree_ensemble.validate_model_configuration(
                model_configuration
            )

        if classifier_type == "bonsai":
            return bonsai.validate_model_configuration(model_configuration)

        if classifier_type == "pme":
            return pme.validate_model_configuration(model_configuration)

        if classifier_type == "linear_regression":
            return linear_regression.validate_model_configuration(model_configuration)

        if classifier_type == "nnom":
            return nnom.validate_model_configuration(model_configuration)

    @staticmethod
    def get_output_tensor_size(classifier_type, model):
        if classifier_type == "tf_micro":
            return tf_micro.get_output_tensor_size(model)

        if classifier_type == "decision_tree_ensemble":
            return decision_tree_ensemble.get_output_tensor_size(model)

        if classifier_type == "boosted_tree_ensemble":
            return boosted_tree_ensemble.get_output_tensor_size(model)

        if classifier_type == "bonsai":
            return bonsai.get_output_tensor_size(model)

        if classifier_type == "pme":
            return pme.get_output_tensor_size(model)

        if classifier_type == "linear_regression":
            return linear_regression.get_output_tensor_size(model)

        if classifier_type == "nnom":
            return nnom.get_output_tensor_size(model)

        return 0

    @staticmethod
    def get_input_feature_type(model):
        classifier_type = model["classifier_type"]
        UINT8_T = 1
        FLOAT = 6
        if classifier_type == "tf_micro":
            return UINT8_T

        if classifier_type == "decision_tree_ensemble":
            return UINT8_T

        if classifier_type == "boosted_tree_ensemble":
            return UINT8_T

        if classifier_type == "bonsai":
            return UINT8_T

        if classifier_type == "pme":
            return UINT8_T

        if classifier_type == "linear_regression":
            return FLOAT

        if classifier_type == "nnom":
            return UINT8_T

        raise ValueError("No classifier type found")

    @staticmethod
    def get_input_feature_def(model):
        classifier_type = model["classifier_type"]
        UINT8_T = "uint8_t"
        FLOAT = "float"
        if classifier_type == "tf_micro":
            return UINT8_T

        if classifier_type == "decision_tree_ensemble":
            return UINT8_T

        if classifier_type == "boosted_tree_ensemble":
            return UINT8_T

        if classifier_type == "bonsai":
            return UINT8_T

        if classifier_type == "pme":
            return UINT8_T

        if classifier_type == "linear_regression":
            return FLOAT

        if classifier_type == "nnom":
            return UINT8_T

        raise ValueError("No classifier type found")

    @staticmethod
    def get_model_type(model):
        classifier_type = model["classifier_type"]
        REGRESSION = 2
        CLASSIFICATION = 1
        if classifier_type == "tf_micro":
            return CLASSIFICATION

        if classifier_type == "nnom":
            return CLASSIFICATION

        if classifier_type == "decision_tree_ensemble":
            return CLASSIFICATION

        if classifier_type == "boosted_tree_ensemble":
            return CLASSIFICATION

        if classifier_type == "bonsai":
            return CLASSIFICATION

        if classifier_type == "pme":
            return CLASSIFICATION

        if classifier_type == "linear_regression":
            return REGRESSION

        raise ValueError("No classifier type found")
