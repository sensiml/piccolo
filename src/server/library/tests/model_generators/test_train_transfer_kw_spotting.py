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
from library.model_generators.neural_network_base import (
    features_to_tensor_convert,
)
from library.model_validation.validation_methods import get_validation_method
from modelstore import ModelStore
from tensorflow.keras.layers import (
    Activation,
    AveragePooling2D,
    BatchNormalization,
    Conv2D,
    Dense,
    DepthwiseConv2D,
    Dropout,
    Flatten,
    Input,
)
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2

logger = logging.getLogger(__name__)

# fmt: off

def build_tf_model(input_shape, num_class): # model_name == 'ds_cnn':

    # print("DS CNN model invoked")

    filters = 12
    weight_decay = 1e-4
    regularizer = l2(weight_decay)

    final_pool_size = (int(input_shape[0]/2), int(input_shape[1]/2))

    # Model layers
    # Input pure conv2d

    inputs = Input(shape=input_shape)
    x = Conv2D(filters, (10,4), strides=(2,2), padding='same', kernel_regularizer=regularizer)(inputs)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Dropout(rate=0.2)(x)

    # First layer of separable depthwise conv2d
    # Separable consists of depthwise conv2d followed by conv2d with 1x1 kernels
    x = DepthwiseConv2D(depth_multiplier=1, kernel_size=(3,3), padding='same', kernel_regularizer=regularizer)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv2D(filters, (1,1), padding='same', kernel_regularizer=regularizer)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    # Fourth layer of separable depthwise conv2d
    x = DepthwiseConv2D(depth_multiplier=1, kernel_size=(3,3), padding='same', kernel_regularizer=regularizer)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv2D(filters, (1,1), padding='same', kernel_regularizer=regularizer)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    # Reduce size and apply final softmax
    x = Dropout(rate=0.4)(x)

    x = AveragePooling2D(pool_size=final_pool_size)(x)
    x = Flatten()(x)
    outputs = Dense(num_class, activation='softmax')(x)

    # Instantiate model.
    model = Model(inputs=inputs, outputs=outputs)

    return model


@pytest.fixture
def data():
    tmp_df = pd.read_csv( os.path.join(os.path.dirname(__file__),'data','kw_spotting_mfcc23x49.csv'))
    feature_columns = [col for col in tmp_df.columns if 'gen' in col]
    columns = feature_columns + ["Label"]
    class_map = {"Unknown": 1, "Bed": 2}
    tmp_df.Label=tmp_df.Label.apply(lambda x: class_map[x])
    tmp_df.columns
    return tmp_df[columns]

@pytest.fixture
@pytest.mark.django_db
def model_uuid(data):


    project_uuid='project_id'
    domain="ce248c94-5980-11ed-9b6a-0242ac120002"
    model_store_path = os.path.join(os.path.join(os.path.dirname(__file__), "data"))
    model_store = ModelStore.from_file_system(root_directory=model_store_path)

    input_shape = (49, 23, 1)
    tf_model = build_tf_model(input_shape, 27)
    tf_model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=["accuracy"])

    model_store_params = save_model(
                project_uuid=project_uuid, pipeline_id=domain, model=tf_model
            )

    fm = FoundationModel()
    fm.neuron_array={'model_store':model_store_params}
    fm.auxiliary_datafile = "auxiliary_test.csv"
    fm.trainable_layer_groups = {
        "0": 0,
        "1": 6,
    }
    fm.save()

    return str(fm.uuid)


@pytest.mark.django_db
def test_train_transfer_kw_spotting(data, loaddata, model_uuid):
    loaddata("test_classifier_costs")

    config = {
                "estimator_type": "classification",
                "iterations": 1,
                "learning_rate": 0.01,
                "threshold": 0.0,
                "batch_size": 8,
                "loss_function": "categorical_crossentropy",
                "tensorflow_optimizer": "adam",
                "label_column": "Label",
                "metrics": "accuracy",
                "final_activation":"softmax",
                "base_model":model_uuid,
                "epochs":1,
                "validation_method": "Recall",
                "optimizer": "Transfer Learning",
                "classifier": "TensorFlow Lite for Microcontrollers",
                "class_map":{"Unknown": 1, "Bed": 2},
                "metric":"accuracy",
                "dense_layers":[],
                "batch_normalization":False,
                "input_type":"int8",
                "early_stopping_threshold":True,
                "add_bias_noise":True,
                "drop_out":0.4,
                "auxiliary_augmentation": True,
                "random_frequency_mask":True,
                "random_sparse_noise":True,
                "random_bias_noise":True,
                "random_time_mask":True,
                "early_stopping_patience":1,
                "training_size_limit": 120,
                "validation_size_limit": 30,
            }
    
    

    validation_method = get_validation_method(config, data)
    classifier = get_classifier(config)

    model_generator = get_model_generator(
        config, classifier=classifier, validation_method=validation_method, project_id="test_project", pipeline_id='27b5f5e7-40f2-4fa9-99e2-3de2e91b5f55', team_id='Test'
    )

    model_generator.run()
    results = model_generator.get_results()

    assert results["models"]["Fold 0"]["parameters"]["tensor_arena_size"] > 0


def get_tf_model(config, data, class_map):

    validation_method = get_validation_method(config, data)
    classifier = get_classifier(config)
    model_generator = get_model_generator(
        config, classifier=classifier, validation_method=validation_method, project_id="test_project",  pipeline_id='27b5f5e7-40f2-4fa9-99e2-3de2e91b5f55',  team_id='Test'
    )

    x_train, y_train = features_to_tensor_convert(data, class_map)
    tf_model = model_generator.initialize_model(x_train, y_train)
    
    return tf_model
   

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
                "drop_out":0.4,
                "auxiliary_augmentation": True,
                "random_frequency_mask":True,
                "random_sparse_noise":True,
                "random_bias_noise":True,
                "random_time_mask":True,
                "early_stopping_patience":1,
                "training_size_limit": 120,
                "validation_size_limit": 30,
                "quantization_aware_step": True,
            }


    class_map = {"Unknown": 1, "Bed": 2}
    num_cols=23   # number of MFCCs
    row_size=49   # cascade size

    tf_model = get_tf_model(config, data, class_map)

    # tf_data_train = convert_to_tensorflow_data_loader(
    #         x_train, y_train, 32, tf_model
    #     )


    assert len(tf_model.layers) == 26
    assert tf_model.input_shape[1]==row_size
    assert tf_model.input_shape[2]==num_cols
    assert tf_model.output_shape[1]==len(class_map)
    
    # by default all base layers are trainable
    assert sum([l.trainable for l in tf_model.layers]) == 26   
    
    # making the last block of the base model trainable, consisting of 6 layers
    config["number_of_trainable_base_layer_blocks"] = 1
    tf_model = get_tf_model(config, data, class_map)
    assert sum([l.trainable for l in tf_model.layers]) == 13
    
    # making all layers of the base model trainable
    config["number_of_trainable_base_layer_blocks"] = 100000
    tf_model = get_tf_model(config, data, class_map)
    
    for layer in tf_model.layers:
        assert layer.trainable == True
