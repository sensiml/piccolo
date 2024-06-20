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
import tensorflow as tf
import numpy as np
from library.model_generators.neural_network_base import NeuralNetworkBase
import uuid


def is_power_of_two(n):
    """Return True if n is a power of two."""
    if n <= 0:
        return False
    else:
        return n & (n - 1) == 0


def name(layer, idx: int = -1, prefix="tmprl_"):
    s = layer + "_" + str(uuid.uuid4()).split("-")[0]
    if idx >= 0:
        s = prefix + str(idx) + "_" + s
    return s


class InvalidTemporalLayerArchitecture(Exception):
    pass


def get_padding_size(input_shape, kernel_size, dilation_rate):

    input_shape_ = [1] + list(input_shape)
    x = np.arange(np.prod(input_shape_), dtype="float64").reshape(input_shape_)
    y = tf.keras.layers.Conv2D(
        2,
        kernel_size=(kernel_size, 1),
        strides=(1, 1),
        dilation_rate=dilation_rate,
        padding="valid",
    )(x)
    return input_shape[0] - y.shape[1]


class TrainTemporalConvolutionalNeuralNetwork(NeuralNetworkBase):
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

        super(TrainTemporalConvolutionalNeuralNetwork, self).__init__(
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
            "feature_columns": config["feature_columns"],
            "n_temporal_blocks": config.get("number_of_temporal_blocks", 1),
            "n_temporal_layers": config.get("number_of_temporal_layers", 1),
            "n_filters": config.get("number_of_convolutional_filters", 8),
            "kernel_size": config.get("kernel_size", 3),
            "residual_block": config.get("residual_block", True),
            "initial_dilation_rate": config.get("initial_dilation_rate", 1),
            "n_slice": config.get("number_of_latest_temporal_features", 0),
            "quantization_aware_step": config.get("quantization_aware_step", False),
            "qaware_epochs": config.get("qaware_epochs", 2),
            "qaware_batch_size": config.get("qaware_batch_size", 32),
            "qaware_learning_rate": config.get("qaware_learning_rate", 0.001),
            "qaware_training_size_factor": config.get(
                "qaware_training_size_factor", 0.7
            ),
        }

    def initialize_model(self, x_train, y_train):

        feature_columns = self._params["feature_columns"]

        n_features = len(feature_columns)

        n_temporal_blocks = self._params["n_temporal_blocks"]
        n_temporal_layers = self._params["n_temporal_layers"]
        n_filters = self._params["n_filters"]

        if n_temporal_blocks < 1:
            raise InvalidTemporalLayerArchitecture(
                "Number of temporal block(s) must be greater than or equal to one !"
            )
        if n_filters < 1:
            raise InvalidTemporalLayerArchitecture(
                "Number of convolutional filters should be a positive integer !"
            )

        cascade_size = 1
        if "gen_c" == feature_columns[0][:5]:
            x = [f.split("_")[1] for f in feature_columns]
            cascade_size = len(set(x))

        if cascade_size == 1:
            raise InvalidTemporalLayerArchitecture(
                "To use the temporal architecture, the cascade size must be larger than one !"
            )

        current_dilation_rate = self._params["initial_dilation_rate"]

        input_shape = [cascade_size, n_features // cascade_size, 1]
        kernel_size = self._params["kernel_size"]
        dropout_rate = self._params["drop_out"]
        residual = self._params["residual_block"]

        if not is_power_of_two(current_dilation_rate):
            raise InvalidTemporalLayerArchitecture(
                "Dilation rate ({}) must be power of two !".format(
                    current_dilation_rate
                )
            )

        try:
            pad_size = get_padding_size(input_shape, kernel_size, current_dilation_rate)
        except Exception as e:
            print(e)
            raise InvalidTemporalLayerArchitecture(
                "Consider reducing the kernel size ({}) or dilation rate ({}) !".format(
                    kernel_size, current_dilation_rate
                )
            )

        pad_size = get_padding_size(input_shape, kernel_size, current_dilation_rate)

        inputs = tf.keras.Input(shape=input_shape, name=name("input"))

        ## First Temporal Block

        for i in range(n_temporal_layers):

            if i == 0:  # coonecting first layer to the input layer
                #  ((top_pad, bottom_pad), (left_pad, right_pad))
                x = tf.keras.layers.ZeroPadding2D(
                    padding=((pad_size, 0), (0, 0)), name=name("pad", i)
                )(inputs)
            else:
                x = tf.keras.layers.ZeroPadding2D(
                    padding=((pad_size, 0), (0, 0)), name=name("pad", i)
                )(x)
            x = tf.keras.layers.Conv2D(
                n_filters,
                kernel_size=(kernel_size, 1),
                strides=(1, 1),
                dilation_rate=current_dilation_rate,
                padding="valid",
                name=name("c2d", i),
            )(x)
            x = tf.keras.layers.BatchNormalization(name=name("btn", i))(x)
            x = tf.keras.layers.ReLU(name=name("rlu", i))(x)
            x = tf.keras.layers.Dropout(rate=dropout_rate, name=name("drp", i))(x)

        ## Residual Block

        if residual:
            residuals = tf.keras.layers.Conv2D(
                1, kernel_size=1, padding="same", name=name("resid")
            )(x)

            if inputs.shape[2] > 1:
                input_reshaped = tf.keras.layers.Conv2D(
                    1, kernel_size=1, padding="same", name=name("reshape_input")
                )(inputs)
                x = tf.keras.layers.add([input_reshaped, residuals], name=name("add"))
            else:
                x = tf.keras.layers.add([inputs, residuals], name=name("add"))

        ## Other temporal blocks

        for _iter in range(n_temporal_blocks - 1):

            current_dilation_rate *= 2
            tensor_shape = x.shape[1:]

            pad_size = get_padding_size(
                tensor_shape, kernel_size, current_dilation_rate
            )

            for i in range(n_temporal_layers):

                if i == 0:  # connecting first layer to the input layer
                    #  ((top_pad, bottom_pad), (left_pad, right_pad))
                    y = tf.keras.layers.ZeroPadding2D(
                        padding=((pad_size, 0), (0, 0)), name=name("pad", i)
                    )(x)
                else:
                    y = tf.keras.layers.ZeroPadding2D(
                        padding=((pad_size, 0), (0, 0)), name=name("pad", i)
                    )(y)
                y = tf.keras.layers.Conv2D(
                    n_filters,
                    kernel_size=(kernel_size, 1),
                    strides=(1, 1),
                    dilation_rate=current_dilation_rate,
                    padding="valid",
                    name=name(f"c2d", i),
                )(y)
                y = tf.keras.layers.BatchNormalization(name=name("btn", i))(y)
                y = tf.keras.layers.ReLU(name=name("rlu", i))(y)
                y = tf.keras.layers.Dropout(rate=dropout_rate, name=name("drp", i))(y)

            if residual:
                residuals = tf.keras.layers.Conv2D(
                    1, kernel_size=1, padding="same", name=name("resid")
                )(y)

                if y.shape[2] > 1:
                    input_reshaped = tf.keras.layers.Conv2D(
                        1, kernel_size=1, padding="same", name=name("reshape_input")
                    )(x)
                    y = tf.keras.layers.add(
                        [input_reshaped, residuals],
                        name=name("add"),
                    )
                else:
                    y = tf.keras.layers.add([x, residuals], name=name("add"))

            x = y

        tensor_shape = x.shape[1:]
        n_slice = self._params["n_slice"]
        if n_slice > tensor_shape[0]:
            raise InvalidTemporalLayerArchitecture(
                "The slicing size ({}) of the temporal tensor must be smaller than its original size ({}) !".format(
                    n_slice, tensor_shape[0]
                )
            )

        ## Fully Connected BLock

        n_labels = y_train.shape[1]
        dense_layers = self._params["dense_layers"]
        dropout_rate = self._params["drop_out"]
        batch_normalization = self._params["batch_normalization"]
        final_activation = self._params["final_activation"]

        if x.shape[2] > 1:
            x = tf.keras.layers.Conv2D(
                1, kernel_size=1, padding="same", name=name("reshape_input")
            )(x)

        if n_slice > 0:
            # x = x[:, -n_slice:, :, :] # not compatible with quantization aware
            x_shape = x.shape
            F = tf.keras.layers.Lambda(
                lambda x, n_slice: x[:, -n_slice:, :, :],
                output_shape=(n_slice, x_shape[2], x_shape[3]),
                name="lambda_layer",
            )  # Define your lambda layer
            F.arguments = {"n_slice": n_slice}  # Update extra arguments to F
            x = F(x)
            x = tf.keras.layers.Flatten(name=name("flatten"))(x)
        else:
            x = tf.keras.layers.Flatten(name=name("flatten"))(x)

        for size in dense_layers:
            x = tf.keras.layers.Dense(size, name=name("dense", idx=size, prefix=""))(x)
            if batch_normalization:
                x = tf.keras.layers.BatchNormalization(
                    name=name("dense_btn", idx=size, prefix="")
                )(x)
            x = tf.keras.layers.ReLU(name=name("activation", idx=size, prefix=""))(x)

            if dropout_rate > 0 and dropout_rate < 1:
                x = tf.keras.layers.Dropout(
                    rate=dropout_rate, name=name("dense_drp", idx=size, prefix="")
                )(x)

        outputs = tf.keras.layers.Dense(
            n_labels, activation=final_activation, name=name("outlayer")
        )(x)

        tf_model = tf.keras.models.Model(
            inputs=inputs, outputs=outputs, name=name("TEMPORAL_MODEL")
        )

        tf_model.compile(
            loss=self._params["loss_function"],
            optimizer=self._params["tensorflow_optimizer"],
            metrics=[self._params["metrics"]],
        )

        tf_model.optimizer.lr = self._params["learning_rate"]

        return tf_model
