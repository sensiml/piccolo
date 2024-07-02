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

import base64
import hashlib
import importlib
import json
import os
import shutil

from django.conf import settings
from django.http import HttpResponse

# from django.http.response import REASON_PHRASES

from datamanager import util_err_defs
from datamanager.renderers import KnowledgeBuilderEncoder

from datamanager.datastore import get_datastore


def _from_fields(jsonvalues):
    newarray = []
    jsonarray = json.loads(jsonvalues)
    for item in jsonarray:
        newarray.append(item["fields"])
    value = json.dumps(newarray)
    return value


def _fix_nesting(from_serializer, *keys):
    """
    Converts nested json strings into proper json objects for sending
    to clients.
    """
    # Basestrings are returned from the serializers operating on
    # lists of objects (all eventschemas, etc)
    # Assumed to be a dictionary. Exceptions will pass to respective
    # objects
    if not isinstance(from_serializer, str):
        ret = from_serializer
    else:
        ret = json.loads(from_serializer)

    for key in keys:
        try:
            if isinstance(ret, list):
                for r in ret:
                    r[key] = json.loads(r[key])
            else:
                ret[key] = json.loads(ret[key])
        except TypeError:
            # Key may not exist on unit tests.
            pass
    return ret


# TODO: Remove this mess


def err_response_send(category, err, extra, excptn=None, code=400):
    """
    Builds HttpResponse message for errors with HTTP status code and reason phrase.

    :rtype : HttpResponse
    :param category: Error Category
    :param err: Specific error in category
    :param extra: extra error information
    :param excptn: If an exception was thrown, exception information.
    :param code: HTTP status code.
    :return:
    """
    resp = HttpResponse(
        status=code,
        content=json.dumps(
            UtilError(category, err, extra, exception=excptn), cls=UtilErrorEncoder
        ),
        content_type="application/json",
    )
    return resp


def _err_response_create_and_send(category, error, extra, exception=None):
    return json.dumps(
        UtilError(category, error, extra, exception=exception), cls=UtilErrorEncoder
    )


class UtilErrorList(object):
    def __init__(self):
        self.err_list = []

    def err_list_add(self, category, err, extra, excptn=None):
        """Add new error to the list"""
        self.err_list.append(UtilError(category, err, extra, exception=excptn))

    def get_list_response(self):
        """Format the list into a JSON message"""
        return json.dumps(self.err_list, cls=UtilErrorEncoder)

    def get_list(self):
        """Return list after the 'errors' index"""
        return self.err_list


class UtilError(object):
    """Create Error object to prevent HTTP 500 errors"""

    def __init__(self, category, err, extra, exception=None):

        self.category = category or util_err_defs.ErrorCategories.general
        self.err = err or util_err_defs.ErrorDefaults.err_default
        self.extra = extra or util_err_defs.ErrorDefaults.extra_default

        if exception is not None:
            self.extra += str(exception)

    def set_contract_mismatch(self, direction, expected, received):
        """Set the direction of contract type mismatch"""
        if self.category is not util_err_defs.ErrorCategories.contract:
            return
        self.err = str(direction)
        self.err += " " + util_err_defs.ContractErrors.type_mismatch
        self.err += "expected " + str(expected)
        self.err += " received " + str(received)


class UtilErrorEncoder(json.JSONEncoder):
    """Serialize Error(s) into JSON message"""

    def default(self, obj):  # pylint: disable=E0202
        if not isinstance(obj, UtilError):
            return super(UtilErrorEncoder, self).default(obj)
        return obj.__dict__


def get_function(transform, function_to_get=""):
    """Dynamically import a module/function from the library path"""
    if function_to_get:
        function_in_file = function_to_get
    else:
        # Default to the object's function_in_file
        function_in_file = transform.function_in_file

    if transform.custom:
        if not os.path.exists(
            os.path.join(
                settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                "{uuid}/embedded_ml_sdk/fg_custom_library_{build_version}.py",
            ).format(
                uuid=transform.library_pack.uuid,
                build_version=transform.library_pack.build_version,
            )
        ):
            datastore = get_datastore(
                folder="custom_transforms/{}".format(transform.library_pack.uuid)
            )
            key = "embedded_ml_sdk.zip"
            local_code_dir = "{0}/{1}".format(
                settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                transform.library_pack.uuid,
            )
            file_path = os.path.join(local_code_dir, key)
            ensure_path_exists(settings.SERVER_CUSTOM_TRANSFORM_ROOT)
            ensure_path_exists(local_code_dir)

            datastore.get(key=key, file_path=file_path)
            shutil.unpack_archive(
                file_path,
                extract_dir=os.path.join(local_code_dir, "embedded_ml_sdk"),
            )

        spec = importlib.util.spec_from_file_location(
            "fg_custom_library",
            os.path.join(
                settings.SERVER_CUSTOM_TRANSFORM_ROOT,
                "{uuid}/embedded_ml_sdk/fg_custom_library_{build_version}.py",
            ).format(
                uuid=transform.library_pack.uuid,
                build_version=transform.library_pack.build_version,
            ),
        )

        lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lib)

        return getattr(lib, function_in_file)

    try:
        is_core_function = transform.core
    except:
        is_core_function = False

    if is_core_function:
        file_name = transform.path.replace("/", ".")[:-3]
    else:
        file_name = str(transform.uuid)

    return getattr(importlib.import_module("library." + file_name), function_in_file)


def ensure_path_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def _jsonify_output(output):
    # Make a list of the output. This is dumped or changed at the end.
    return json.dumps(output, cls=KnowledgeBuilderEncoder)


def _username_from_email(email):
    return base64.urlsafe_b64encode(hashlib.sha1(email.lower()).digest()).strip("=")
