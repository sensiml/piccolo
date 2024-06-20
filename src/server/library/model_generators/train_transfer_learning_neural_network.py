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

import numpy as np
from datamanager.models import FoundationModel
from engine.base.model_store import load_model
from library.model_generators.neural_network_base import NeuralNetworkBase
from tensorflow.keras import Sequential, layers
import uuid


class ExceedsNumberOfBaseLayers(Exception):
    pass


class TransferLearningNeuralNetwork(NeuralNetworkBase):
    """Creates optimal order-agnostic training set and trains  with the resulting vector."""

    def __init__(
        self,
        config,
        classifier,
        validation_method,
        team_id,
        project_id,
        pipeline_id,
        save_model_parameters,
    ):
        """Initialize with defaults for missing values."""

        super(TransferLearningNeuralNetwork, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )

        self._params = {
            "estimator_type": config["estimator_type"],
            "learning_rate": config["learning_rate"],
            "threshold": config["threshold"],
            "batch_size": config["batch_size"],
            "loss_function": config["loss_function"],
            "tensorflow_optimizer": config["tensorflow_optimizer"],
            "label_column": config["label_column"],
            "metrics": config["metrics"],
            "base_model": config["base_model"],
            "epochs": config["epochs"],
            "dense_layers": config["dense_layers"],
            "final_activation": config["final_activation"],
            "batch_normalization": config["batch_normalization"],
            "drop_out": config["drop_out"],
            "early_stopping_threshold": config["early_stopping_threshold"],
            "early_stopping_patience": config["early_stopping_patience"],
            "random_bias_noise": config["random_bias_noise"],
            "random_sparse_noise": config["random_sparse_noise"],
            "random_frequency_mask": config["random_frequency_mask"],
            "random_time_mask": config["random_time_mask"],
            "auxiliary_augmentation": config["auxiliary_augmentation"],
            "training_size_limit": config["training_size_limit"],
            "validation_size_limit": config["validation_size_limit"],
            "input_type": config["input_type"],
            "number_of_trainable_base_layer_blocks": config.get(
                "number_of_trainable_base_layer_blocks", 9999
            ),
            "quantization_aware_step": config.get("quantization_aware_step", False),
            "qaware_epochs": config.get("qaware_epochs", 2),
            "qaware_batch_size": config.get("qaware_batch_size", 32),
            "qaware_learning_rate": config.get("qaware_learning_rate", 0.001),
            "qaware_training_size_factor": config.get(
                "qaware_training_size_factor", 0.7
            ),
        }

    def initialize_model(self, x_train, y_train):
        fm = FoundationModel.objects.get(uuid=self._params["base_model"])
        project_id = fm.neuron_array["model_store"]["model"]["root"]
        domain = fm.neuron_array["model_store"]["model"]["domain"]
        model_id = fm.neuron_array["model_store"]["model"]["model_id"]
        trainable_layer_groups = fm.trainable_layer_groups
        n_trainable = self._params.get("number_of_trainable_base_layer_blocks", 0)

        base_model = load_model(project_id, domain, model_id)

        if fm.auxiliary_datafile:
            self._params["auxiliary_datafile"] = fm.auxiliary_datafile

        if np.prod(base_model.input_shape[1:]) != x_train.shape[1]:
            message = "Input training data cannot be reshaped to match the input shape of the chosen model. \n"
            message += "Input Vector Shape: " + str(x_train.shape[1]) + "\n"
            message += "Model Input Shape: " + str(base_model.input_shape[1:]) + "\n"
            raise Exception(message)

        transfer_model = Sequential()
        for layer in base_model.layers[:-1]:  # go through until last layer
            transfer_model.add(layer)

        # freezing all base layers
        for layer in transfer_model.layers:
            layer.trainable = False

        # relax the requested number of base layers and make them trainable
        if (
            trainable_layer_groups
            and n_trainable > 0
            and str(n_trainable) in trainable_layer_groups
        ):
            for layer in transfer_model.layers[
                -trainable_layer_groups[str(n_trainable)] :
            ]:
                layer.trainable = True
        elif (
            trainable_layer_groups is not None
            and not str(n_trainable) in trainable_layer_groups
        ):
            for layer in transfer_model.layers:
                layer.trainable = True

        for layer_index in self._params["dense_layers"]:

            layer_uuid = str(uuid.uuid4()).split("-")[0]

            transfer_model.add(
                layers.Dense(
                    layer_index,
                    name=f"new_dense_layer_{layer_index}_{layer_uuid}",
                )
            )

            if self._params.get("batch_normalization"):
                transfer_model.add(
                    layers.BatchNormalization(
                        name=f"new_batch_norm_layer_{layer_index}_{layer_uuid}"
                    )
                )

            transfer_model.add(
                layers.Activation(
                    "relu", name=f"new_activation_{layer_index}_{layer_uuid}"
                )
            )

            if self._params.get("drop_out"):
                transfer_model.add(
                    layers.Dropout(
                        self._params["drop_out"],
                        name=f"new_dropout_layer_{layer_index}_{layer_uuid}",
                    )
                )

        transfer_model.add(
            layers.Dense(
                y_train.shape[1],
                activation=self._params["final_activation"],
                name="dense_output",
            )
        )

        transfer_model.compile(
            loss=self._params["loss_function"],
            optimizer=self._params["tensorflow_optimizer"],
            metrics=[self._params["metrics"]],
        )

        transfer_model.optimizer.lr = self._params["learning_rate"]

        return transfer_model
