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
import logging

import sensiml.base.utility as utility
from sensiml.datamanager.base import Base, BaseSet

from requests import Response
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project

logger = logging.getLogger(__name__)


class LabelType(object):
    Int = "integer"
    Float = "float"
    String = "string"


class Label(Base):
    """Base class for a label object."""

    _fields = [
        "uuid",
        "name",
        "value_type",
        "is_dropdown",
        "metadata",
        "last_modified",
        "created_at",
    ]

    _field_map = {"value_type": "type"}

    def __init__(self, connection: Connection, project: Project):
        """Initialize a metadata object.

        Args:
            connection
            project
        """
        self._uuid = ""
        self._name = ""
        self._value_type = "string"
        self._is_dropdown = False
        self._last_modified = ""
        self._created_at = ""
        self._connection = connection
        self._project = project

    @property
    def uuid(self) -> str:
        """Auto generated unique identifier for the metadata object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def name(self) -> str:
        """The name property of the metadata object"""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def value_type(self) -> str:
        """The data type of the metadata object"""
        return self._value_type

    @value_type.setter
    def value_type(self, value: str):
        if value not in ["string", "int", "float"]:
            raise Exception("Invalid value type")
        self._value_type = value

    @property
    def _label_or_metadata(self) -> str:
        return "label"

    @property
    def _metadata(self) -> bool:
        return False

    @property
    def metadata(self) -> bool:
        return False

    @property
    def is_dropdown(self) -> bool:
        return self._is_dropdown

    @is_dropdown.setter
    def is_dropdown(self, value: bool):
        if not isinstance(value, bool):
            raise Exception("Invalid Value")

        self._is_dropdown = value

    def insert(self) -> Response:
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""
        url = f"project/{self._project.uuid}/{self._label_or_metadata}/"
        data = self._to_representation()
        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data["uuid"]

        return response

    def update(self) -> Response:
        """Calls the REST API and updates the object on the server."""
        url = f"project/{self._project.uuid}/{self._label_or_metadata}/{self.uuid}/"

        data = self._to_representation()
        response = self._connection.request("put", url, data)
        utility.check_server_response(response)

        return response

    def delete(self) -> Response:
        """Calls the REST API and deletes the object from the server."""
        url = f"project/{self._project.uuid}/{self._label_or_metadata}/{self.uuid}/"
        response = self._connection.request("delete", url)
        utility.check_server_response(response)

        return response

    def refresh(self) -> Response:
        """Calls the REST API and populates the local object's properties from the server."""
        url = f"project/{self._project.uuid}/{self._label_or_metadata}/{self.uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def initialize_from_dict(self, data: dict):
        """Reads a json dictionary and populates a single metadata object.

        Args:
            data (dict): contains the uuid, name, type
        """
        self.uuid = data["uuid"]
        self.name = data["name"]
        if data["type"] == LabelType.Int:
            self.value_type = int(data["type"])
        elif data["type"] == LabelType.Float:
            self.value_type = float(data["type"])
        else:
            self.value_type = data["type"]

        self._data = data


class LabelSet(BaseSet):
    def __init__(self, connection: Connection, project: Project, initialize_set=True):
        """Initialize a metadata object.

        Args:
            connection
            project
        """
        self._connection = connection
        self._project = project
        self._set = None
        self._objclass = Label
        self._attr_key = "name"

        if initialize_set:
            self.refresh()

    @property
    def labels(self):
        return self.objs

    @property
    def get_set_url(self) -> str:
        return f"project/{self._project.uuid}/label/"
