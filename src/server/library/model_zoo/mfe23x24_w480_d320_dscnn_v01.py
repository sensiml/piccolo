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

import os

from library.model_zoo import store_model_in_model_zoo, upload_model_as_foundation_model
from tensorflow.keras.models import load_model

"""
Require:
    Description of the inputs
    Description of the model

Load model from local files
Upload Model to DataBase as a KnowledgePack

Use models as part of Pipeline Templates

Future: Create List API for description of Transfer Learning Models to show in the UI

"""

domain = "kw_spotting"
model_id = "64fd2662-8628-4a2b-8515-c76918573f20"


def train():
    """Description of training process for this model"""


def load():
    """Loading foundation model into our local model zoo"""

    tf_model = load_model(
        os.path.join(
            os.path.dirname(__file__), "data", "mfe23x24_w480_d320_dscnn_v01.h5"
        )
    )

    store_model_in_model_zoo(domain, model_id, tf_model)


def upload():
    """Upload the model to the model store"""

    params = {
        "description": "Google KW base model, DS-CNN, 25,623 params.",
        "name": "mfe23x24_w480_d320_dscnn_v01",
        "auxiliary_datafile": "Google_KW_mfe23x24_w480_d320_scaled_8000samples.csv",
        "trainable_layer_groups": {
            "0": 0,
        },
        "model_profile": {},
    }

    upload_model_as_foundation_model(domain, model_id, params)
