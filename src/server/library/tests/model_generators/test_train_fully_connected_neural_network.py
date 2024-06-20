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

import pytest
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_generators.neural_network_base import features_to_tensor_convert
from library.model_validation.validation_methods import get_validation_method
from pandas import DataFrame

logger = logging.getLogger(__name__)

# fmt: off

@pytest.fixture
def data():
    train_data = DataFrame(
        [
            [80, 6, 1, 3, 9, 241, 253, 251, 253, 253, 253, 252, 2, 254, 253, 252, 252, 250, 245, 1, 2, 2, 1, 1, 1, 1, 1],
            [144, 3, 2, 4, 7, 248, 251, 252, 253, 252, 253, 252, 4, 253, 253, 253, 251, 251, 221, 2, 1, 1, 0, 0, 1, 2, 1],
            [67, 248, 252, 251, 247, 17, 4, 1, 2, 2, 1, 1, 252, 1, 1, 0, 3, 7, 31, 253, 254, 253, 253, 254, 253, 253, 2],
            [84, 248, 251, 250, 242, 13, 4, 0, 1, 0, 0, 1, 250, 0, 1, 2, 2, 5, 33, 253, 253, 253, 253, 253, 253, 253, 2],
        ]
    )

    train_data = train_data.T
    train_data.columns = ["gen_1", "gen_2", "gen_3", "gen_4"]
    labels = [1] * 13 + [2] * 14
    train_data["Label"] = labels

    return train_data

@pytest.mark.django_db
def test_train_fully_connected_neural_network(data, loaddata):
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
                "dense_layers": [8, 4],
                "final_activation":"softmax",
                "drop_out": 0.1,
                "epochs":5,
                "validation_method": "Recall",
                "optimizer": "Train Fully Connected Neural Network",
                "classifier": "TF Micro",
                "class_map":{"1":1,"2":2,"0":0},
                "metric":"accuracy",
                "batch_normalization":True,
                "input_type":"int8",
                "early_stopping_threshold":.8,
                "early_stopping_patience":1,
            }


    validation_method = get_validation_method(config, data)

    classifier = get_classifier(config)

    model_generator = get_model_generator(
        config, classifier=classifier, validation_method=validation_method, project_id="test_project", pipeline_id='27b5f5e7-40f2-4fa9-99e2-3de2e91b5f55', team_id='Test'
    )

    model_generator.run()

    results = model_generator.get_results()

    assert results["models"]["Fold 0"]["parameters"]["tensor_arena_size"] > 0



@pytest.mark.django_db
def test_train_fully_connected_neural_network_no_save(data, loaddata):
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
                "dense_layers": [8, 4],
                "final_activation":"softmax",
                "drop_out": 0.1,
                "epochs":5,
                "validation_method": "Recall",
                "optimizer": "Train Fully Connected Neural Network",
                "classifier": "TF Micro",
                "class_map":{"1":1,"2":2,"0":0},
                "metric":"accuracy",
                "batch_normalization":True,
                "early_stopping_threshold":.8,
                "early_stopping_patience":1,

                "input_type":"int8"
            }


    validation_method = get_validation_method(config, data)

    classifier = get_classifier(config)

    model_generator = get_model_generator(
        config, classifier=classifier, validation_method=validation_method, project_id="test_project", pipeline_id='27b5f5e7-40f2-4fa9-99e2-3de2e91b5f55', team_id='Test', save_model_parameters=False
    )

    model_generator.run()

    results = model_generator.get_results()

    assert results["models"]["Fold 0"]["parameters"] == {}

def test_build_nn_layers(data):

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
                "dense_layers": [8, 4],
                "final_activation":"softmax",
                "drop_out": 0.1,
                "epochs":5,
                "validation_method": "Recall",
                "optimizer": "Train Fully Connected Neural Network",
                "classifier": "TF Micro",
                "reverse_map":{1:1,2:2,0:0},
                "metric":"accuracy",
                "batch_normalization":False,
                "input_type":"int8",
                "early_stopping_threshold":.8,
                "early_stopping_patience":1,
            }

    validation_method = get_validation_method(config, data)

    classifier = get_classifier(config)

    model_generator = get_model_generator(
        config, classifier=classifier, validation_method=validation_method, project_id="test_project", pipeline_id='27b5f5e7-40f2-4fa9-99e2-3de2e91b5f55',  team_id='Test'
    )

    x_train, y_train = features_to_tensor_convert(data,{1:1,2:2,0:0})

    tf_model = model_generator.initialize_model(x_train, y_train)

    assert len(tf_model.get_config()['layers']) == 8
