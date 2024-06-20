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
from datamanager.models import FoundationModel
from engine.base.model_store import save_model
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_generators.neural_network_base import features_to_tensor_convert
from library.model_validation.validation_methods import get_validation_method
from modelstore import ModelStore
from tensorflow.keras import Sequential, layers

logger = logging.getLogger(__name__)

# fmt: off

@pytest.fixture
def data():
    tmp_df = pd.read_csv( os.path.join(os.path.dirname(__file__),'data','transfer_learning_nn.csv'))
    columns = ["gen_0002_GyroscopeYStd","gen_0014_GyroscopeYVariance","gen_0024_AccelerometerZMean","gen_0026_GyroscopeYZeroCrossings","gen_0032_GyroscopeYPositiveZeroCrossings","gen_0040_AccelerometerXMedian","gen_0048_AccelerometerZIQR","gen_0054_AccelerometerZ25Percentile","gen_0068_GyroscopeYSum","gen_0072_AccelerometerZSum","Label"]
    class_map = {'Hook':1, "Jab":2, "Uppercut":3, "Cross": 4, "Overhand":5}
    tmp_df.Label=tmp_df.Label.apply(lambda x: class_map[x])
    tmp_df.columns
    return tmp_df[columns]

@pytest.fixture
@pytest.mark.django_db
def model_uuid(data):


    project_uuid='project_id'
    domain="c4d99af6-363a-4d57-8934-6f0af2e4c211"
    #model_id="ee65de7e-9ecd-49f1-a31b-b0e3e5f42819"
    model_store_path = os.path.join(os.path.join(os.path.dirname(__file__), "data"))
    model_store = ModelStore.from_file_system(root_directory=model_store_path)



    tf_model = Sequential()
    tf_model.add(
        layers.Dense(
            16,
            input_dim=data.shape[1]-1,
            activation="relu",
        )
    )

    tf_model.add(
        layers.Dense(5, activation='softmax')
    )

    tf_model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy'],
    )


    model_store_params = save_model(
                project_uuid=project_uuid, pipeline_id=domain, model=tf_model
            )

    fm = FoundationModel()
    fm.neuron_array={'model_store':model_store_params}  
    fm.save()

    return str(fm.uuid)


@pytest.mark.django_db
def test_train_transfer_learning_neural_network(data, loaddata, model_uuid):
    loaddata("test_classifier_costs")


    config = {
                "estimator_type": "classification",
                "iterations": 2,
                "learning_rate": 0.01,
                "threshold": 0.0,
                "batch_size": 8,
                "loss_function": "categorical_crossentropy",
                "tensorflow_optimizer": "adam",
                "label_column": "Label",
                "metrics": "accuracy",
                "final_activation":"softmax",
                "base_model":model_uuid,
                "epochs":5,
                "validation_method": "Recall",
                "optimizer": "Transfer Learning",
                "classifier": "TensorFlow Lite for Microcontrollers",
                "class_map":{'Hook':1, "Jab":2, "Uppercut":3, "Cross": 4, "Overhand":5},
                "metric":"accuracy",
                "dense_layers":[],
                "batch_normalization":False,
                "input_type":"int8",
                "early_stopping_threshold":True,
                "add_bias_noise":True,
                "drop_out":0.4,
                "auxiliary_augmentation": False,
                "random_frequency_mask":True,
                "random_sparse_noise":True,
                "random_bias_noise":True,
                "random_time_mask":True,
                "early_stopping_patience":1,
                "training_size_limit": None,
                "validation_size_limit": None,
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
def test_initialize_model(data, model_uuid):

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
                "base_model":model_uuid,
                "final_activation":"softmax",
                "epochs":5,
                "validation_method": "Recall",
                "optimizer": "Transfer Learning",
                "classifier": "TensorFlow Lite for Microcontrollers",
                "metric":"accuracy",
                "dense_layers":[24,8],
                "batch_normalization":False,
                "input_type":"int8",
                "early_stopping_threshold":True,
                "add_bias_noise":True,
                "drop_out":0.0,
                "auxiliary_augmentation": False,
                "random_frequency_mask":True,
                "random_sparse_noise":True,
                "random_bias_noise":True,
                "random_time_mask":True,
                "early_stopping_patience":1,
                "training_size_limit": None,
                "validation_size_limit": None,
            }

    validation_method = get_validation_method(config, data)

    classifier = get_classifier(config)

    model_generator = get_model_generator(
        config, classifier=classifier, validation_method=validation_method, project_id="test_project",  pipeline_id='27b5f5e7-40f2-4fa9-99e2-3de2e91b5f55',  team_id='Test'
    )

    x_train, y_train = features_to_tensor_convert(data,{1:1,2:2,3:3,4:4,5:0})

    tf_model = model_generator.initialize_model(x_train, y_train)

    assert len(tf_model.get_config()['layers']) == 7
    
    n_activation_layers = 0
    for layer in tf_model.layers:
        if "activation" in layer.name:
            n_activation_layers+=1
    
    assert n_activation_layers == 2

    assert tf_model.input_shape[1]==10
    assert tf_model.output_shape[1]==5
