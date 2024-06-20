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

import logging
import os

from datamanager.models import FoundationModel
from django.conf import settings
from engine.base.model_store import save_model
from modelstore import ModelStore
from modelstore.utils.exceptions import ModelNotFoundException

local_model_store_path = os.path.join(os.path.join(os.path.dirname(__file__)))
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


def upload_model_as_foundation_model(domain, model_id, params):

    try:
        if FoundationModel.objects.get(uuid=model_id):
            logger.info(
                {
                    "message": f"Model {model_id} already exists.",
                    "log_type": "manager",
                }
            )
            return
    except ModelNotFoundException:
        pass
    except FoundationModel.DoesNotExist:
        pass

    local_model_store = ModelStore.from_file_system(
        root_directory=local_model_store_path
    )

    model = local_model_store.load(
        domain=domain,
        model_id=model_id,
    )

    model_store_params = save_model(
        project_uuid=settings.FOUNDATION_MODEL_STORE_PROJECT,
        pipeline_id=settings.FOUNDATION_MODEL_STORE_DOMAIN,
        model=model,
    )

    fm = FoundationModel.objects.create(uuid=model_id)

    fm.description = params["description"]
    fm.neuron_array = {"model_store": model_store_params}
    fm.auxiliary_datafile = params["auxiliary_datafile"]
    fm.model_profile = params["model_profile"]
    fm.name = params["name"]
    fm.trainable_layer_groups = params["trainable_layer_groups"]
    fm.save()


def store_model_in_model_zoo(domain, model_id, model):

    local_model_store = ModelStore.from_file_system(
        root_directory=local_model_store_path
    )

    if check_if_model_in_model_zoo(local_model_store, domain, model_id):
        logger.info(
            {
                "message": f"Model {model_id} already exists in model store.",
                "log_type": "manager",
            }
        )
        return

    model_store_params = local_model_store.upload(
        domain=domain, model_id=model_id, model=model
    )

    return model_store_params


def check_if_model_in_model_zoo(model_store, domain, model_id):

    try:
        model_store.get_model_info(domain=domain, model_id=model_id)
    except ModelNotFoundException:
        return False

    return True
