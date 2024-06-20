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

import logging

from library.model_generators.linear_regression.lasso import TrainLinearRegressionLasso
from library.model_generators.linear_regression.ols import TrainLinearRegressionOLS
from library.model_generators.linear_regression.ridge import TrainLinearRegressionRidge
from library.model_generators.load_pme_model import LoadPMEModel
from library.model_generators.load_tf_micro_model import LoadTensorFlowMicroModel
from library.model_generators.model_generator import ModelGeneratorError
from library.model_generators.train_bonsai import TrainBonsai
from library.model_generators.train_fully_connected_neural_network import (
    TrainFullyConnectedNeuralNetwork,
)
from library.model_generators.train_gradient_boosting import TrainGradientBoosting
from library.model_generators.train_itereate_neural_network import (
    TrainIterateNeuralNetwork,
)
from library.model_generators.train_pme_cluster import ClusterLearning
from library.model_generators.train_pme_cluster_optimized import NeuronOptimization
from library.model_generators.train_pme_train_n_prune import TrainNPrune
from library.model_generators.train_pme_vanilla_burlington import VanillaBurlington
from library.model_generators.train_random_forest import TrainRandomForest
from library.model_generators.train_temporal_convolutional_neural_network import (
    TrainTemporalConvolutionalNeuralNetwork,
)
from library.model_generators.train_transfer_learning_neural_network import (
    TransferLearningNeuralNetwork,
)

"""
A module for collecting and referencing the various model generators in the train-validate-optimize step.
"""

logger = logging.getLogger(__name__)


def get_model_generator(
    config,
    classifier,
    validation_method,
    team_id=None,
    project_id=None,
    pipeline_id=None,
    save_model_parameters=True,
):
    """
    Gets a ModelGenerator instance with the given configuration and feature data.
    :NOTE: Hard-coded options (below) means no user-uploaded model generators will be supported.
    :param config: A configuration dictionary suitable for instantiating a ModelGenerator object.
    :param classifier: An instantiated Classifier object.
    :param validation_method: An instantiated ValidationMethod object.
    :return: an instantiated ModelGenerator object.
    """

    allowed_model_generators = {
        "RBF with Neuron Allocation Optimization": VanillaBurlington,
        "Hierarchical Clustering with Neuron Optimization": ClusterLearning,
        "RBF with Neuron Allocation Limit": TrainNPrune,
        "Neuron Optimization": NeuronOptimization,
        "Load Neuron Array": LoadPMEModel,
        "Bonsai Tree Optimizer": TrainBonsai,
        "Random Forest": TrainRandomForest,
        "xGBoost": TrainGradientBoosting,
        "Load Model PME": LoadPMEModel,
        "Load Model TF Micro": LoadTensorFlowMicroModel,
        "Load Model TensorFlow Lite for Microcontrollers": LoadTensorFlowMicroModel,
        "Train Fully Connected Neural Network": TrainFullyConnectedNeuralNetwork,
        "Iterate Neural Network": TrainIterateNeuralNetwork,
        "Transfer Learning": TransferLearningNeuralNetwork,
        "Train Temporal Convolutional Neural Network": TrainTemporalConvolutionalNeuralNetwork,
        "Ordinary Least Squares": TrainLinearRegressionOLS,
        "L1 Lasso": TrainLinearRegressionLasso,
        "L2 Ridge": TrainLinearRegressionRidge,
    }

    try:
        model_generator_type = config["optimizer"]
    except:
        raise ModelGeneratorError(
            "No optimizer configuration supplied in train-validate-optimize pipeline step."
        )

    try:
        model_generator = allowed_model_generators[model_generator_type]
    except:
        msg = "Supplied optimizer({0}) does not match an existing configuration.  Allowable optimizers are:\n{1}\n  ".format(
            model_generator_type, "\n  ".join(allowed_model_generators.keys())
        )
        raise ModelGeneratorError(msg)

    return model_generator(
        config,
        classifier,
        validation_method,
        team_id,
        project_id,
        pipeline_id,
        save_model_parameters,
    )


def validate_config(config):
    """
    A check for valid combinations of configuration parameters.
    Logs any combinations which are not recognized/acceptable.
    :return: True if a set of configuration parameters is currently allowed.  False otherwise.
    """

    assert "validation_method" in config
    assert "classifier" in config
    assert "optimizer" in config

    return True
