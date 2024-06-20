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

import json
import logging
import os
from copy import deepcopy

import numpy as np
from pandas import concat, read_csv

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
import tensorflow_model_optimization as tfmot
from engine.base.model_store import save_model
from library.model_generators.model_generator import ModelGenerator
from library.model_generators.neural_network_training_utils import (
    alter_feature_data,
    augment_feature_with_unknown,
    encode_tflite,
    features_to_tensor_convert,
    get_data_aux_indices,
    get_label_stat,
    resample,
    reshape_input_data_to_model,
)
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


class AuxiliaryDataNotAvailable(Exception):
    pass


class FailedQuantizationAwareStep(Exception):
    pass


class earlyStoppingCallback(tf.keras.callbacks.Callback):
    def __init__(self, threshold=0.85, patience=2, metric="val_accuracy"):

        self.patience = patience
        self.alert = 0
        self.threshold = threshold
        self.metric = metric
        self.stop = False

    def on_epoch_end(self, epoch, logs):

        if logs.get(self.metric) > self.threshold:
            self.alert += 1
            if self.alert > self.patience:
                self.stop = True
                self.model.stop_training = True
        else:
            self.alert = 0


class LoggerCallback(tf.keras.callbacks.Callback):
    def __init__(self, pipeline_id, total_epochs):
        super(LoggerCallback, self).__init__()
        self.pipeline_id = pipeline_id

    def on_epoch_end(self, epoch, logs=None):

        tmp_logs = deepcopy(logs)
        tmp_logs["epoch"] = epoch

        logger.debug(
            {
                "message": tmp_logs,
                "log_type": "PID",
                "UUID": self.pipeline_id,
            }
        )


class NeuralNetworkBase(ModelGenerator):
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

        super(NeuralNetworkBase, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )

        self.train_data_shape = None

    def input_type(self):

        if self._config.get("input_type", "uint8") == "int8":
            return tf.int8

        if self._config.get("input_type", "uint8") == "uint8":
            return tf.uint8

        raise Exception("Invalid Input Format Type Supplied")

    def initialize_model(self, x_train, y_train):
        """Override this function"""

    def _train(self, train_data, validate_data=None, test_data=None):
        """train a model using a specific algorithm

        Args:
            train_data; data used to train the model
            validate_data: data used for model validation during training

        Returns:
            dict: A json serializable version of the model parameters
            dict: the training metrics ie. loss, training  accuracy across epochsW.

        """

        callback_list = [
            LoggerCallback(self.pipeline_id, total_epochs=self._params["epochs"])
        ]

        early_stopping_thresh = self._params.get("early_stopping_threshold", False)
        early_stopping_patience = self._params.get("early_stopping_patience", 2)
        add_bias_noise = self._params.get("random_bias_noise", False)
        add_sparse_noise = self._params.get("random_sparse_noise", False)
        add_feature_mask = self._params.get("random_frequency_mask", False)
        add_time_mask = self._params.get("random_time_mask", False)
        auxiliary_augmentation = self._params.get("auxiliary_augmentation", False)
        input_type = self._params.get("input_type", "int8")

        ## The sample size is currently available just for transfer learning
        ## If not set, put an upper limit on the training/validation sample size per label
        training_size_limit = self._params.get("training_size_limit", 4000)
        validation_size_limit = self._params.get("validation_size_limit", 1000)

        # Quantization aware parameters
        apply_qaware = self._params.get("quantization_aware_step")
        qaware_epochs = self._params.get("qaware_epochs")
        qaware_batch_size = self._params.get("qaware_batch_size")
        qaware_learning_rate = self._params.get("qaware_learning_rate")
        qaware_training_size_factor = self._params.get("qaware_training_size_factor")

        early_stopping = earlyStoppingCallback(
            threshold=early_stopping_thresh, patience=early_stopping_patience
        )
        callback_list += [early_stopping]

        train_history = {"loss": [], "val_loss": [], "accuracy": [], "val_accuracy": []}

        x_train, y_train = features_to_tensor_convert(train_data, self.class_map)

        x_validate, y_validate = features_to_tensor_convert(
            validate_data, self.class_map
        )

        model = self.initialize_model(x_train, y_train)

        x_train_reshaped = reshape_input_data_to_model(x_train, model)
        x_validate_reshaped = reshape_input_data_to_model(x_validate, model)

        auxiliary_datafile = self._params.get("auxiliary_datafile", "FileNotFound")

        if auxiliary_augmentation:

            # making sure that the dataset has the "Unknown" class
            try:
                unknown_code = self.class_map["Unknown"]
            except:
                logger.debug(
                    {
                        "message": 'Auxiliary data augmentation is selected without an "Unknown" label. Continuing without the auxiliary data augmentation!',
                        "log_type": "PID",
                        "UUID": self.pipeline_id,
                    }
                )
                auxiliary_augmentation = False

        if auxiliary_augmentation:

            try:
                auxiliary_fv = read_csv(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../../library/model_zoo/auxiliary_data",
                        auxiliary_datafile,
                    )
                )
            except FileNotFoundError:
                raise (
                    AuxiliaryDataNotAvailable(
                        "The auxiliary data file is not available."
                    )
                )

            # shuffling auxiliary data
            auxiliary_fv = auxiliary_fv.iloc[
                np.random.choice(
                    range(len(auxiliary_fv)), size=len(auxiliary_fv), replace=False
                )
            ]

            # getting the indices of unknown and keywords
            (
                ix_fv_keywords,
                ix_fv_unknown,
                ix_aux_unknown_kw,
                ix_aux_unknown,
            ) = get_data_aux_indices(train_data, auxiliary_fv, self.class_map)

            feature_columns = train_data.columns
            n_fv = len(feature_columns) - 1
            auxiliary_fv = auxiliary_fv[auxiliary_fv.columns[:n_fv]]
            auxiliary_fv = auxiliary_fv.astype(np.int16)

            if input_type == "int8":
                auxiliary_fv -= 127

            auxiliary_fv.columns = feature_columns[:n_fv]
            auxiliary_fv[feature_columns[-1]] = unknown_code

        # iterative training
        for i in range(self._params["epochs"]):

            # TODO: Explore using a loss function with a bias instead of undersampling

            # balancing validation data, undersample unless validation_size_limit is specified
            n_labels_valid, _, _ = get_label_stat(y_validate)

            if (
                validation_size_limit is not None
                and type(validation_size_limit) == int
                and validation_size_limit > 0
            ):
                n_sample_valid = min(validation_size_limit, min(n_labels_valid))
            else:
                n_sample_valid = None

            validate_ix = resample(
                y_validate,
                method="undersample",
                n_sample=n_sample_valid,
            )

            if auxiliary_augmentation:
                train_data_ix, ix_aux = augment_feature_with_unknown(
                    ix_fv_unknown,
                    ix_fv_keywords,
                    ix_aux_unknown,
                    ix_aux_unknown_kw,
                )

                x_train, y_train = features_to_tensor_convert(
                    concat(
                        [train_data.iloc[train_data_ix], auxiliary_fv.iloc[ix_aux]]
                    ).reset_index(drop=True),
                    self.class_map,
                )
                x_train_reshaped = reshape_input_data_to_model(x_train, model)

            # balancing training data, undersample unless training_size_limit is specified
            n_labels_train, _, _ = get_label_stat(y_train)

            if (
                training_size_limit is not None
                and type(training_size_limit) == int
                and training_size_limit > 0
            ):
                n_sample_train = min(training_size_limit, min(n_labels_train))
            else:
                n_sample_train = None

            train_ix = resample(
                y_train,
                method="undersample",
                n_sample=n_sample_train,
            )

            history = model.fit(
                alter_feature_data(
                    x_train_reshaped[train_ix],
                    bias_noise=add_bias_noise,
                    row=add_feature_mask,
                    column=add_time_mask,
                    sparse_noise=add_sparse_noise,
                ),
                y_train[train_ix],
                epochs=1,
                batch_size=self._params["batch_size"],
                validation_data=(
                    x_validate_reshaped[validate_ix],
                    y_validate[validate_ix],
                ),
                verbose=0,
                shuffle=True,
                callbacks=callback_list,
            )

            for key in train_history:
                train_history[key].extend(history.history[key])

            if early_stopping.stop:  # stop training
                break

        # implementation of the Q-aware training step
        if apply_qaware:

            qat_train_history = {
                "qat_loss": [],
                "qat_accuracy": [],
                "qat_val_loss": [],
                "qat_val_accuracy": [],
            }

            try:

                for layer in model.layers:
                    layer.trainable = True

                quantize_model = tfmot.quantization.keras.quantize_model
                q_aware_model = quantize_model(model)

                q_aware_model.compile(
                    optimizer=self._params["tensorflow_optimizer"],
                    loss=self._params["loss_function"],
                    metrics=[self._params["metrics"]],
                )

                q_aware_model.optimizer.lr = qaware_learning_rate

                for epoch in range(qaware_epochs):

                    if (
                        training_size_limit is not None
                        and type(training_size_limit) == int
                        and training_size_limit > 0
                    ):
                        n_sample_train = min(training_size_limit, min(n_labels_train))
                    else:
                        n_sample_train = None

                    train_ix = resample(
                        y_train,
                        method="undersample",
                        n_sample=n_sample_train,
                    )

                    n_train_ix = len(train_ix)
                    N = max(
                        1, np.int(np.floor(qaware_training_size_factor * n_train_ix))
                    )
                    selected_indices = np.random.choice(
                        range(n_train_ix), size=N, replace=True
                    )
                    train_ix = train_ix[selected_indices]

                    validate_ix = resample(
                        y_validate,
                        method="undersample",
                    )

                    # No data augmentation in this phase
                    qat_history = q_aware_model.fit(
                        x_train_reshaped[train_ix],
                        y_train[train_ix],
                        epochs=1,
                        batch_size=qaware_batch_size,
                        validation_data=(
                            x_validate_reshaped[validate_ix],
                            y_validate[validate_ix],
                        ),
                        verbose=0,
                        shuffle=True,
                    )

                    qat_log = {}
                    for key in qat_history.history:
                        qat_train_history["qat_" + key].extend(qat_history.history[key])
                        qat_log["qat_" + key] = qat_history.history[key]

                    qat_log["qat_epoch"] = epoch
                    logger.debug(
                        {
                            "message": qat_log,
                            "log_type": "PID",
                            "UUID": self.pipeline_id,
                        }
                    )

                model = q_aware_model

                # storing QAT metrics as part of the training_history structure
                for key, value in qat_train_history.items():
                    train_history[key] = value

            except:
                raise FailedQuantizationAwareStep(
                    "Quantization aware training step is failed. Please review the Qaware parameters or consider disabling this step for successful completion."
                )

        (tflite_model_full, tflite_model_quant, input_details) = self.cost_function(
            model, x_validate_reshaped
        )

        params = self.package_model_parameters(
            deepcopy(self._params),
            tflite_model_full,
            tflite_model_quant,
            input_details,
            x_train,
            y_train,
        )

        params["model_summary"] = json.loads(model.to_json())

        if self.save_model_parameters:
            params["model_store"] = save_model(
                project_uuid=self.project_id,
                pipeline_id=self.pipeline_id,
                model=model,
            )

        logger.debug(
            {
                "message": "Finished training",
                "log_type": "PID",
                "UUID": self.pipeline_id,
            }
        )

        return params, train_history

    def cost_function(self, tf_model, x_test, ndim=2):

        shape_ndim = len(list(tf_model.input_shape[1:]))

        def representative_dataset_generator():
            for value in x_test:
                # Each scalar value must be inside of a 2D array that is wrapped in a list

                if shape_ndim > 1:
                    yield [np.array([value], dtype=np.float32)]
                else:
                    yield [np.array(value, dtype=np.float32)]

        # Unquantized Model
        converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)
        converter.representative_dataset = representative_dataset_generator
        tflite_model_full = converter.convert()

        # Quantized Model
        converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.allow_custom_ops = True
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

        converter.inference_input_type = self.input_type()
        converter.inference_output_type = self.input_type()
        converter.representative_dataset = representative_dataset_generator

        # add this line before convert()
        # converter._experimental_new_quantizer = True

        tflite_model_quant = converter.convert()

        loaded_model = tf.lite.Interpreter(model_content=tflite_model_quant)
        """
        # Save the model.
        with open(
            "model_quant_{}.tflite".format(self._config.get("input_type")), "wb"
        ) as f:
            f.write(tflite_model_quant)

        # Save the model.
        with open("model_full.tflite", "wb") as f:
            f.write(tflite_model_full)
        """

        return (
            tflite_model_full,
            tflite_model_quant,
            loaded_model.get_input_details(),
        )

    def package_model_parameters(
        self,
        params,
        tflite_model_full,
        tflite_model_quant,
        input_details,
        x_train,
        y_train,
    ):

        params["num_outputs"] = y_train.shape[1]
        params["num_inputs"] = x_train.shape[1]

        params["tflite_quant"] = encode_tflite(tflite_model_quant)
        params["tflite_full"] = encode_tflite(tflite_model_full)
        params["size_full"] = len(params["tflite_full"])
        params["size_quant"] = len(params["tflite_quant"])

        params["size"] = len(params["tflite_quant"])
        params["tflite"] = encode_tflite(tflite_model_quant)

        params["input_shape"] = input_details[0]["shape"].tolist()
        params["input_quantization"] = input_details[0]["quantization"]

        return params
