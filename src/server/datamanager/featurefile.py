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
import traceback
from uuid import uuid4

import pandas as pd
from binaryornot.check import is_binary_string
from django.conf import settings
from django.core import exceptions, serializers
from django.db.utils import IntegrityError
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from logger.log_handler import LogHandler
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed,
    NotFound,
    ValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from datamanager import utils
from datamanager.decorators import permission_required
from datamanager.exceptions import FileUploadError
from datamanager.models import FeatureFile, Project
from datamanager.renderers import BinaryRenderer
from datamanager.datastore import (
    get_datastore,
    get_datastore_basedir,
    ensure_parent_dir_exists,
)

from datamanager.serializers import FeatureFileSerializer
from datamanager.util_err_defs import FileErrors

logger = LogHandler(logging.getLogger(__name__))


def validate_is_feature(value):
    if value in [True, "True"]:
        return True
    elif value in ["False", False]:
        return False
    else:
        raise ValidationError("Is Feature must be True/False")


def validate_label_columns(value):
    if isinstance(value, str) and len(value) < 64:
        return True
    if value is None:
        return True

    raise ValidationError("Invalid label_column")


def _serializer(featurefile):
    value = serializers.serialize(
        "json", [featurefile], fields=("name", "uuid", "is_features")
    )
    return json.loads(value)[0]["fields"]


def _check_parents(user, project_uuid):
    return Project.objects.with_user(user=user, uuid=project_uuid).exists()


def _locate_feature_file(user, project_uuid, feature_uuid=""):
    feature_files = FeatureFile.objects.with_user(user=user, project__uuid=project_uuid)
    return feature_files if feature_uuid == "" else feature_files.get(uuid=feature_uuid)


def _get_featurefile_datastore(feature_file):
    if feature_file.is_features:
        basedir = get_datastore_basedir(settings.SERVER_FEATURE_FILE_ROOT)
    else:
        basedir = get_datastore_basedir(settings.SERVER_DATA_ROOT)

    return get_datastore(folder=os.path.join(basedir, str(feature_file.project.uuid)))


def _get_featurefile_name(feature_file):

    if feature_file.version == 1:
        return "{}.{}".format(str(feature_file.uuid), feature_file.format)
    else:
        return "{}{}".format(str(feature_file.uuid), feature_file.format)


def _get_feature_file(request, project_uuid, feature_uuid):
    if feature_uuid != "":
        try:
            feature_file = _locate_feature_file(
                request.user, project_uuid, feature_uuid
            )
            return Response(FeatureFileSerializer(feature_file).data)

        except exceptions.ObjectDoesNotExist as e:
            raise NotFound(e)
    else:
        try:
            feature_files = _locate_feature_file(request.user, project_uuid)

            return Response(FeatureFileSerializer(feature_files, many=True).data)
        except Exception as e:
            raise APIException(e)


# TODO: Return proper REST response with proper encoding
#       Partially done now!
def _get_feature_file_binary(request, project_uuid, feature_uuid):
    if feature_uuid != "":
        try:
            feature_file = _locate_feature_file(
                request.user, project_uuid, feature_uuid
            )
            # Load file and send as binary
            datastore = _get_featurefile_datastore(feature_file)
            datastore.get(
                _get_featurefile_name(feature_file),
                feature_file.path,
            )
            with open(feature_file.path, "rb") as f:
                returndata = f.read()
            datastore.delete_local_copy(feature_file.path)
            return Response(
                returndata,
                headers={
                    "Content-Disposition": "attachment; filename={}".format(
                        feature_file.name
                    )
                },
            )

        except exceptions.ObjectDoesNotExist as e:
            raise NotFound("Couldn't find feature file {0} ".format(feature_uuid))

    else:
        raise NotFound()


def _get_feature_file_json(request, project_uuid, feature_uuid):

    if feature_uuid:
        try:

            feature_file = _locate_feature_file(
                request.user, project_uuid, feature_uuid
            )
            datastore = _get_featurefile_datastore(feature_file)
            data = datastore.get_data(
                _get_featurefile_name(feature_file),
            )

            sample_size = settings.MAX_FEATUREFILE_RETURN_SIZE
            if data.shape[0] > sample_size:
                data = data.sample(n=sample_size, replace=False)

            if isinstance(data, pd.Series):
                response = data.to_dict()

            elif isinstance(data, pd.DataFrame):
                response = data.to_dict("list")

            return JsonResponse(
                response, safe=False, json_dumps_params={"separators": (",", ":")}
            )

        except exceptions.ObjectDoesNotExist as e:
            raise NotFound(f"Couldn't find Feature File UUID {feature_uuid}")

    else:
        raise NotFound(f"Invalid Feature File UUID {feature_uuid}")


@permission_required("datamanager.add_featurefile")
def _post_feature_file(request, project_uuid, feature_uuid):
    if feature_uuid:
        raise MethodNotAllowed("POST")
    if _check_parents(request.user, project_uuid):
        new_uuid = uuid4()
        try:
            # Prefer name parameter from model. Using custom http headers can cause compatibility issues
            file_name = str(request.data.get("name"))
            is_features = validate_is_feature(request.data.get("is_features", False))

            label_column = request.data.get("label_column", None)
            if not validate_label_columns(label_column):
                label_column = None

            name, ext = os.path.splitext(file_name)
            if ext.lower() in settings.BANNED_FILE_EXTENSIONS or ext.lower() != ".csv":
                raise ValidationError("Only CSV files are allowed.")
            if is_features:
                file_path = os.path.join(
                    settings.SERVER_FEATURE_FILE_ROOT, project_uuid, str(new_uuid) + ext
                )
            else:
                file_path = os.path.join(
                    settings.SERVER_DATA_ROOT, project_uuid, str(new_uuid) + ext
                )
            ensure_parent_dir_exists(file_path)
        except KeyError as e:
            logger.error({"message": traceback.format_exc(), "log_type": "data_upload"})
            raise FileUploadError(e)
        try:
            with open(file_path, "wb+") as f:
                # allow either "file" or "data_file" to improve consistency across api
                uploaded_file = request.data.get("file") or request.data.get(
                    "data_file"
                )
                if is_binary_string(uploaded_file.read(1024)):
                    raise ValidationError("CSV failed validation.")
                uploaded_file.seek(0)
                for chunk in uploaded_file:
                    f.write(chunk)
                f.seek(0)

        except Exception as e:
            logger.error({"message": traceback.format_exc(), "log_type": "datamanager"})
            raise FileUploadError(e)
        try:
            project = Project.objects.with_user(user=request.user).get(
                uuid=project_uuid
            )

            feature_file = FeatureFile(
                uuid=new_uuid,
                project=project,
                name=file_name,
                is_features=is_features,
                format=ext,
                path=file_path,
                version=2,
                label_column=label_column,
            )

            data_store = _get_featurefile_datastore(feature_file)

            if data_store.is_remote:
                feature_file.path = data_store.save(
                    _get_featurefile_name(feature_file), file_path
                )

            feature_file.save()

            return Response(_serializer(feature_file))
        except IntegrityError as e:
            os.remove(file_path)
            raise FileUploadError(e)
    else:
        raise NotFound("invalid path to object")


@permission_required("datamanager.change_featurefile")
def _put_feature_file(request, project_uuid, feature_uuid):
    if not feature_uuid:
        raise MethodNotAllowed("PUT")
    if _check_parents(request.user, project_uuid):
        try:
            # take actual model field as parameter, fallback to old name
            file_name = str(request.data.get("name"))
            is_features = validate_is_feature(request.data.get("is_features", False))
            label_column = validate_label_columns(
                request.data.get("label_column", None)
            )
            name, ext = os.path.splitext(file_name)
            if ext.lower() in settings.BANNED_FILE_EXTENSIONS:
                raise ValidationError("Executable files are not allowed.")
        except KeyError as e:
            raise FileUploadError(e)
        try:
            feature_file = _locate_feature_file(
                request.user, project_uuid, feature_uuid
            )

        except exceptions.ObjectDoesNotExist as e:
            raise NotFound()
        if is_features:
            file_path = os.path.join(
                settings.SERVER_FEATURE_FILE_ROOT,
                project_uuid,
                str(feature_file.uuid) + ext,
            )
            feature_file.label_column = label_column
        else:
            file_path = os.path.join(
                settings.SERVER_DATA_ROOT, project_uuid, str(feature_file.uuid) + ext
            )

        if feature_file.is_features != is_features:
            if feature_file.is_features:
                raise FileUploadError(
                    "Current file is a feature file. Can not upload a data file"
                )
            else:
                raise FileUploadError(
                    "Current file is a data file. Can not upload as a featurer file"
                )
        ensure_parent_dir_exists(file_path)
        try:
            with open(file_path, "wb+") as f:
                # allow either "file" or "data_file" to improve consistency across api
                uploaded_file = request.data.get("file") or request.data.get(
                    "data_file"
                )
                if is_binary_string(uploaded_file.read(1024)):
                    raise ValidationError("CSV failed validation.")
                uploaded_file.seek(0)
                for chunk in uploaded_file:
                    f.write(chunk)
                f.seek(0)

        except Exception as e:
            logger.error({"message": traceback.format_exc(), "log_type": "datamanager"})
            raise FileUploadError(e)

        datastore = _get_featurefile_datastore(feature_file)
        if datastore.is_remote:
            feature_file.path = datastore.save(
                _get_featurefile_name(feature_file), file_path
            )
        feature_file.save()

        return Response(_serializer(feature_file))

    else:
        raise FileUploadError(FileErrors.fil_inv_path)


@permission_required("datamanager.delete_featurefile")
def _delete_feature_file(request, project_uuid, feature_uuid):
    if not feature_uuid:
        raise MethodNotAllowed("DELETE")
    if _check_parents(request.user, project_uuid):
        try:
            feature_file = _locate_feature_file(
                request.user, project_uuid, feature_uuid
            )

            datastore = _get_featurefile_datastore(feature_file)

            datastore.delete(_get_featurefile_name(feature_file))

            feature_file.delete()

        except exceptions.ObjectDoesNotExist as e:
            raise NotFound()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        raise FileUploadError(FileErrors.fil_inv_path)


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
@renderer_classes((BinaryRenderer,))
def feature_file_binary(request, project_uuid, uuid=""):
    return _get_feature_file_binary(request, project_uuid, uuid)


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def feature_file_json(request, project_uuid, uuid=""):
    return _get_feature_file_json(request, project_uuid, uuid)


# @csrf_exempt
@extend_schema_view(
    get=extend_schema(
        summary="Get Feature File",
        description="Return information about the feature file ",
    ),
    put=extend_schema(
        summary="Update Project by UUID",
        description="Update information about a project",
    ),
    post=extend_schema(
        summary="Upload a new FeatureFile",
        description="Update information about a project",
    ),
    delete=extend_schema(
        summary="Delete a Project",
        description="Deletes a project and all associated models and data",
    ),
)
@api_view(("GET", "POST", "PUT", "DELETE"))
@permission_classes((IsAuthenticated,))
def feature_file(request, project_uuid, uuid=""):
    utils.ensure_path_exists(settings.SERVER_DATA_ROOT)
    if request.method == "GET":
        return _get_feature_file(request, project_uuid, uuid)
    elif request.method == "POST":
        return _post_feature_file(request, project_uuid, uuid)
    elif request.method == "PUT":
        return _put_feature_file(request, project_uuid, uuid)
    elif request.method == "DELETE":
        return _delete_feature_file(request, project_uuid, uuid)
