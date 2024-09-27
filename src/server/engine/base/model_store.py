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

from datamanager.datastore import get_datastore, get_datastore_basedir
from django.conf import settings
from logger.log_handler import LogHandler
from modelstore import ModelStore
from modelstore.utils.exceptions import ModelNotFoundException

logger = LogHandler(logging.getLogger(__name__))


def get_model_store(project_uuid):
    datastore = get_datastore()

    if datastore.is_remote and datastore.storage_type == "S3":
        model_store = ModelStore.from_aws_s3(
            bucket_name=settings.AWS_S3_BUCKET,
            root_prefix=os.path.join(
                get_datastore_basedir(settings.SERVER_MODEL_STORE_ROOT),
                project_uuid,
            ),
        )
    else:
        model_store_path = get_datastore_basedir(settings.SERVER_MODEL_STORE_ROOT)

        if not os.path.exists(model_store_path):
            os.mkdir(model_store_path)

        model_store = ModelStore.from_file_system(
            root_directory=os.path.join(model_store_path, project_uuid),
            create_directory=True,
        )

    return model_store


def download_model(project_uuid, pipeline_id, model_id, path):

    model_store = get_model_store(project_uuid)

    os.makedirs(path, exist_ok=True)
    model_path = model_store.download(
        local_path=path,
        domain=pipeline_id,
        model_id=model_id,
    )

    return model_path


def load_model(project_uuid, pipeline_id, model_id):

    model_store = get_model_store(project_uuid)

    model = model_store.load(
        domain=pipeline_id,
        model_id=model_id,
    )

    return model


def save_model(project_uuid, pipeline_id, model):

    model_store = get_model_store(project_uuid)

    metadata = model_store.upload(domain=pipeline_id, model=model)
    metadata["model"]["root"] = os.path.join(project_uuid)

    return metadata


def delete_model(project_uuid, pipeline_id, model_id):

    model_store = get_model_store(project_uuid)

    try:
        model_store.delete_model(
            domain=pipeline_id, model_id=model_id, skip_prompt=True
        )
    except ModelNotFoundException:
        logger.error(
            {
                "message": "Unable to delete model, it does not exist.",
                "data": {
                    "project_uuid": project_uuid,
                    "domain": pipeline_id,
                    "model_id": model_id,
                },
                "log_type": "datamanager",
            }
        )


def delete_model_store_domain(project_uuid, pipeline_id):

    get_model_store(project_uuid)

    # TODO DELETE MODEL STORE DOMAIN
