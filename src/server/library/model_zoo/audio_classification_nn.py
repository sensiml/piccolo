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

import tensorflow as tf
from library.model_zoo import store_model_in_model_zoo, upload_model_as_foundation_model

"""
Require:
    Description of the inputs
    Description of the model

Load model from local files
Upload Model to DataBase as a KnowledgePack

Use models as part of Pipeline Templates

Future: Create List API for description of Transfer Learning Models to show in the UI

"""

domain = "audio_classification_nn"
model_id = "6f3f8ce6-10f2-4988-8e08-6717a1cbad3d"


def train():
    """Training algorithm for building the foundation model"""

    # Train a model
    trained_model = tf.keras.models.Sequential(
        [
            tf.keras.layers.Dense(5, activation="relu", input_shape=(10,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1),
        ]
    )
    trained_model.compile(optimizer="adam", loss="mean_squared_error")

    return trained_model


def load():

    trained_model = train()
    store_model_in_model_zoo(domain, model_id, trained_model)


def upload():
    """Upload the model to the model store"""

    params = {"description": "", "model_size": 1000, "name": "Audio Classification"}

    upload_model_as_foundation_model(domain, model_id, params)
