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

# coding=utf-8
import logging
import os

import pandas as pd
import pytest
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_generators.neural_network_base import features_to_tensor_convert
from library.model_validation.validation_methods import get_validation_method

logger = logging.getLogger(__name__)


@pytest.fixture
def data():
    tmp_df = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "kw_spotting_mfcc23x49.csv")
    )
    feature_columns = [col for col in tmp_df.columns if "gen" in col]
    columns = feature_columns + ["Label"]
    class_map = {"Unknown": 1, "Bed": 2}
    tmp_df.Label = tmp_df.Label.apply(lambda x: class_map[x])
    tmp_df.columns
    return tmp_df[columns]


@pytest.mark.django_db
def test_temporal_neural_network(data, loaddata):

    loaddata("test_classifier_costs")

    config = {
        "estimator_type": "classification",
        "iterations": 2,
        "learning_rate": 0.01,
        "threshold": 0.0,
        "batch_size": 16,
        "loss_function": "categorical_crossentropy",
        "tensorflow_optimizer": "adam",
        "label_column": "Label",
        "metrics": "accuracy",
        "final_activation": "softmax",
        "epochs": 5,
        "validation_method": "Recall",
        "optimizer": "Train Temporal Convolutional Neural Network",
        "classifier": "TensorFlow Lite for Microcontrollers",
        "metric": "accuracy",
        "dense_layers": [8],
        "batch_normalization": True,
        "input_type": "int8",
        "early_stopping_threshold": 0.9,
        "add_bias_noise": True,
        "drop_out": 0.4,
        "random_frequency_mask": True,
        "random_sparse_noise": False,
        "random_bias_noise": False,
        "random_time_mask": True,
        "early_stopping_patience": 1,
        "training_size_limit": 120,
        "validation_size_limit": 30,
        "feature_columns": data.columns.values[:-1],
        "class_map": {"Unknown": 1, "Bed": 2},
        "n_temporal_blocks": 4,
        "n_temporal_layers": 2,
        "n_filters": 16,
        "kernel_size": 3,
        "residual_block": True,
        "initial_dilation_rate": 1,
        "n_slice": 5,
    }

    validation_method = get_validation_method(config, data)

    classifier = get_classifier(config)

    model_generator = get_model_generator(
        config,
        classifier=classifier,
        validation_method=validation_method,
        project_id="test_project",
        pipeline_id="7b8b9b91-1fde-4ce5-afab-1d50833baa43",
        team_id="Test",
    )

    model_generator.run()

    results = model_generator.get_results()

    assert results["models"]["Fold 0"]["parameters"]["tensor_arena_size"] > 0


def get_tf_model(config, data, class_map):

    validation_method = get_validation_method(config, data)
    classifier = get_classifier(config)
    model_generator = get_model_generator(
        config,
        classifier=classifier,
        validation_method=validation_method,
        project_id="test_project",
        pipeline_id="4b6c17b7-3967-4149-ae02-bee59f7fa386",
        team_id="Test",
    )

    x_train, y_train = features_to_tensor_convert(data, class_map)
    tf_model = model_generator.initialize_model(x_train, y_train)

    return tf_model


@pytest.mark.django_db
def test_initialize_model(data, loaddata):

    class_map = {"Unknown": 1, "Bed": 2}
    num_cols = 23  # number of MFCCs
    row_size = 49  # cascade size
    n_temporal_block = 4
    n_temporal_layer = 3
    n_filters = 16
    n_slice = 5

    loaddata("test_classifier_costs")

    config = {
        "estimator_type": "classification",
        "iterations": 2,
        "learning_rate": 0.01,
        "threshold": 0.0,
        "batch_size": 16,
        "loss_function": "categorical_crossentropy",
        "tensorflow_optimizer": "adam",
        "label_column": "Label",
        "metrics": "accuracy",
        "final_activation": "softmax",
        "epochs": 5,
        "validation_method": "Recall",
        "optimizer": "Train Temporal Convolutional Neural Network",
        "classifier": "TensorFlow Lite for Microcontrollers",
        "metric": "accuracy",
        "dense_layers": [8],
        "batch_normalization": True,
        "input_type": "int8",
        "early_stopping_threshold": 0.9,
        "add_bias_noise": True,
        "drop_out": 0.4,
        "random_frequency_mask": True,
        "random_sparse_noise": False,
        "random_bias_noise": False,
        "random_time_mask": True,
        "early_stopping_patience": 1,
        "training_size_limit": 120,
        "validation_size_limit": 30,
        "feature_columns": data.columns.values[:-1],
        "class_map": class_map,
        "number_of_temporal_blocks": n_temporal_block,
        "number_of_temporal_layers": n_temporal_layer,
        "number_of_convolutional_filters": n_filters,
        "kernel_size": 3,
        "residual_block": False,
        "initial_dilation_rate": 1,
        "number_of_latest_temporal_features": n_slice,
    }

    tf_model = get_tf_model(config, data, class_map)

    assert tf_model.input_shape[1] == row_size
    assert tf_model.input_shape[2] == num_cols
    assert tf_model.output_shape[1] == len(class_map)

    n_temp = 0
    for layer in tf_model.layers:
        if "_c2d_" in layer.name and "tmprl_" in layer.name:
            assert layer.output_shape[-1] == n_filters
            n_temp += 1

    assert n_temp == n_temporal_block * n_temporal_layer

    # fully connected block
    for layer in tf_model.layers:
        if "flatten" in layer.name:
            assert layer.output_shape[1] == n_slice * num_cols
