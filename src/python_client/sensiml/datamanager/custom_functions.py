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

from __future__ import annotations
import json
from sensiml.base import utility
from sensiml.datamanager.base import Base, BaseSet
from sensiml.connection import Connection
from requests import Response
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sensiml.connection import Connection


class CustomFunction(Base):
    """Base class for a transform object"""

    _uuid = ""
    _type = None
    _name = None
    _description = ""
    _input_contract = ""
    _output_contract = ""
    _subtype = ""
    _path = ""
    _unit_tests = None
    _logs = ""
    _task_result = ""
    _c_function_name = ""
    _library_pack = ""
    _automl_available = False

    _fields = [
        "uuid",
        "name",
        "transform_type",
        "description",
        "input_contract",
        "output_contract",
        "subtype",
        "unit_tests",
        "logs",
        "task_result",
        "c_function_name",
        "library_pack",
        "task_status",
        "automl_available",
    ]

    _read_only_fields = [
        "uuid",
        "created_at",
        "last_modified",
        "logs",
        "task_result",
        "task_status",
        "automl_available",
    ]

    _field_map = {"transform_type": "type"}

    def __init__(self, connection: Connection, uuid: Optional[str] = None):
        self._connection = connection
        if uuid:
            self.uuid = uuid
            self.refresh()

    @property
    def base_url(self) -> str:
        return "custom-transform/"

    @property
    def detail_url(self) -> str:
        return f"custom-transform/{self.uuid}/"

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def subtype(self) -> str:
        return self._subtype

    @subtype.setter
    def subtype(self, value: str):
        self._subtype = value

    @property
    def transform_type(self) -> str:
        return "Feature Generator"

    @transform_type.setter
    def transform_type(self, value: str):
        self._transform_type = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def c_function_name(self) -> str:
        return self._c_function_name

    @c_function_name.setter
    def c_function_name(self, value: str):
        self._c_function_name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def input_contract(self) -> str:
        return json.dumps(self._input_contract)

    @input_contract.setter
    def input_contract(self, value: dict):
        self._input_contract = value

    @property
    def output_contract(self) -> str:
        return json.dumps(self._output_contract)

    @output_contract.setter
    def output_contract(self, value: dict):
        self._output_contract = value

    @property
    def unit_tests(self):
        return json.dumps(self._unit_tests)

    @unit_tests.setter
    def unit_tests(self, value):
        self._unit_tests = value

    @property
    def logs(self):
        print(self._logs)

    @logs.setter
    def logs(self, value):
        self._logs = value

    @property
    def task_result(self):
        return self._task_result

    @task_result.setter
    def task_result(self, value):
        self._task_result = value

    @property
    def library_pack(self):
        return self._library_pack

    @library_pack.setter
    def library_pack(self, value):
        self._library_pack = value

    @property
    def automl_available(self):
        return self._automl_available

    @automl_available.setter
    def automl_available(self, value):
        self._automl_available = value

    def refresh(self) -> Response:
        """Calls the REST API and populates the local object properties from the server."""

        response = self._connection.request("get", self.detail_url)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def delete(self) -> Response:
        """Calls the REST API and populates the local object properties from the server."""

        response = self._connection.request("delete", self.detail_url)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def insert(self, path: str) -> Response:
        """Calls the REST API to insert a new object."""

        data = self._to_representation()

        response = self._connection.file_request(self.base_url, path, data, "rb")

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def update(self, path: str) -> Response:
        """Calls the REST API to insert a new object."""

        data = self._to_representation()

        data.pop("library_pack")

        response = self._connection.file_request(
            self.detail_url, path, data, "rb", "put"
        )

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response


class CustomFunctionSet(BaseSet):
    def __init__(self, connection: Connection, initialize_set: bool = True):
        """Initialize a custom transform set object.

        Args:
            connection
        """
        self._connection = connection
        self._set = None
        self._objclass = CustomFunction
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    @property
    def library_packs(self):
        return self.objs

    @property
    def get_set_url(self) -> str:
        return "custom-transform/"

    def _new_obj_from_dict(self, data) -> CustomFunction:
        """Creates a new object from the response data from the server.

        Args:
            data (dict): contains properties of the object

        Returns:
            obj of type _objclass

        """
        obj = self._objclass(self._connection)
        obj.initialize_from_dict(data)
        return obj
