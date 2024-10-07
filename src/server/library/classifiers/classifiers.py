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

from library.classifiers.bonsai import Bonsai
from library.classifiers.boosted_tree_ensemble import BoostedTreeEnsemble
from library.classifiers.classifier import ClassifierError
from library.classifiers.decision_tree_ensemble import DecisionTreeEnsemble
from library.classifiers.pme import PME
from library.classifiers.tensorflow_micro import TensorFlowMicro
from library.classifiers.linear_regression import LinearRegression


def get_classifier(config, save_model_parameters=True):
    """
    Gets a Classifier instance with the given configuration and feature data.
    :param config: A configuration dictionary suitable for instantiating a Classifier object.
    :return: an instantiated Classifier object.
    """
    allowable_classifiers = {
        "PME": PME,  # Onward to the future
        "Bonsai": Bonsai,
        "Decision Tree Ensemble": DecisionTreeEnsemble,
        "Boosted Tree Ensemble": BoostedTreeEnsemble,
        "TF Micro": TensorFlowMicro,
        "TensorFlow Lite for Microcontrollers": TensorFlowMicro,
        "Neural Network": TensorFlowMicro,
        "Linear Regression": LinearRegression,
    }
    try:
        classifier_type = config["classifier"]
    except:
        raise ClassifierError(
            "No classifier supplied in train-validate-optimize pipeline step."
        )

    try:
        classifier = allowable_classifiers[classifier_type]
    except:
        msg = "Supplied classifier ({0}) does not match an existing configuration.  Allowable classifiers are: {1}\n  ".format(
            classifier_type, "\n  ".join(allowable_classifiers.keys())
        )
        raise ClassifierError(msg)

    return classifier(save_model_parameters=save_model_parameters, config=config)
