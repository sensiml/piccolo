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


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
from django.conf import settings
from engine.base import model_store
from sklearn.datasets import load_diabetes
from sklearn.metrics import mean_squared_error

logger = logging.getLogger(__name__)
import shutil

# fmt: off


def test_save_model_load_model_test_model_delete_model():
    # Load the data
    data =  load_diabetes()
    X_train=data.data
    y_train = data.target


    # Train a model
    trained_model = tf.keras.models.Sequential(
        [
            tf.keras.layers.Dense(5, activation="relu", input_shape=(10,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1),
        ]
    )
    trained_model.compile(optimizer="adam", loss="mean_squared_error")
    
    trained_model.fit(X_train, y_train, epochs=10)

    expected_results = mean_squared_error(y_train, trained_model.predict(X_train))

    meta_data = model_store.save_model("PROJECT_ID", 'PIPELINE_ID', model= trained_model)

    stored_model = model_store.load_model("PROJECT_ID", 'PIPELINE_ID', model_id= meta_data["model"]["model_id"])

    results = mean_squared_error(y_train, stored_model.predict(X_train))

    assert results==expected_results

    weights = stored_model.get_weights()

    stored_model.compile(loss="mean_squared_logarithmic_error")

    stored_model.set_weights(weights)

    stored_model.fit(X_train, y_train, epochs=10)

    results = mean_squared_error(y_train, stored_model.predict(X_train))

    file_path = meta_data['storage']['path']
    model_store.delete_model("PROJECT_ID", 'PIPELINE_ID', model_id=meta_data["model"]["model_id"])
        
    model_store.delete_model("PROJECT_ID", 'PIPELINE_ID', model_id='blue')

    assert os.path.exists(file_path) == False

    shutil.rmtree(os.path.join(settings.SERVER_MODEL_STORE_ROOT, "PROJECT_ID"))
