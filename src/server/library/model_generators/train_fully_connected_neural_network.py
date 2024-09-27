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

# from numpy import argmax, array
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
from library.model_generators.neural_network_base import NeuralNetworkBase
from tensorflow.keras import Sequential, layers
import uuid


class TrainFullyConnectedNeuralNetwork(NeuralNetworkBase):
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

        super(TrainFullyConnectedNeuralNetwork, self).__init__(
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
            "drop_out": config["drop_out"],
            "epochs": config["epochs"],
            "dense_layers": config["dense_layers"],
            "final_activation": config["final_activation"],
            "batch_normalization": config["batch_normalization"],
            "early_stopping_threshold": config["early_stopping_threshold"],
            "early_stopping_patience": config["early_stopping_patience"],
            "quantization_aware_step": config.get("quantization_aware_step", False),
            "qaware_epochs": config.get("qaware_epochs", 2),
            "qaware_batch_size": config.get("qaware_batch_size", 32),
            "qaware_learning_rate": config.get("qaware_learning_rate", 0.001),
            "qaware_training_size_factor": config.get(
                "qaware_training_size_factor", 0.7
            ),
        }

    def initialize_model(self, x_train, y_train):

        tf_model = Sequential()
        
        tf_model.add(
                layers.Input(shape=(x_train.shape[1],))
        )

        layer_index = self._params["dense_layers"][0]
        layer_uuid = str(uuid.uuid4()).split("-")[0]

        tf_model.add(
            layers.Dense(
                layer_index,
                name=f"dense_layer_{layer_index}_{layer_uuid}",
            )
        )

        if self._params["batch_normalization"]:
            tf_model.add(
                layers.BatchNormalization(
                    name=f"batch_norm_layer_{layer_index}_{layer_uuid}"
                )
            )

        tf_model.add(
            layers.Activation("relu", name=f"activation_{layer_index}_{layer_uuid}")
        )

        if self._params["drop_out"]:
            tf_model.add(
                layers.Dropout(
                    self._params["drop_out"],
                    name=f"dropout_layer_{layer_index}_{layer_uuid}",
                )
            )

        for layer_index in self._params["dense_layers"][1:]:

            layer_uuid = str(uuid.uuid4()).split("-")[0]

            tf_model.add(
                layers.Dense(
                    layer_index,
                    name=f"dense_layer_{layer_index}_{layer_uuid}",
                )
            )

            if self._params["batch_normalization"]:
                tf_model.add(
                    layers.BatchNormalization(
                        name=f"batch_norm_layer_{layer_index}_{layer_uuid}"
                    )
                )

            tf_model.add(
                layers.Activation("relu", name=f"activation_{layer_index}_{layer_uuid}")
            )

            if self._params["drop_out"]:
                tf_model.add(
                    layers.Dropout(
                        self._params["drop_out"],
                        name=f"dropout_layer_{layer_index}_{layer_uuid}",
                    )
                )

        tf_model.add(
            layers.Dense(y_train.shape[1], activation=self._params["final_activation"])
        )

        tf_model.compile(
            loss=self._params["loss_function"],
            optimizer=self._params["tensorflow_optimizer"],
            metrics=[self._params["metrics"]],
        )

        tf_model.optimizer.lr = self._params["learning_rate"]

        return tf_model
