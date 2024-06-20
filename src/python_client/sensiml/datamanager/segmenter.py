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
from uuid import UUID

import sensiml.base.utility as utility
from sensiml.datamanager.base import Base, BaseSet


from typing import TYPE_CHECKING
from requests import Response

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project


class Segmenter(Base):
    """Base class for a segmenter object."""

    _data = None
    _fields = [
        "uuid",
        "name",
        "parameters",
        "preprocess",
        "custom",
        "parent",
        "is_locked",
        "last_modified",
        "created_at",
    ]
    _field_map = {
        "uuid": "id",
    }

    def __init__(self, connection: Connection, project: Project):
        """Initialize a metadata object.

        Args:
            connection
            project
        """
        self._uuid = ""
        self._name = ""
        self._parameters = None
        self._preprocess = None
        self._custom = True
        self._parent = None
        self._is_locked = False
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
    def parameters(self) -> dict:
        return self._parameters

    @parameters.setter
    def parameters(self, value: dict):
        self._parameters = value

    @property
    def preprocess(self) -> dict:
        return self._preprocess

    @preprocess.setter
    def preprocess(self, value: dict):
        self._preprocess = value

    @property
    def is_locked(self) -> bool:
        return self._is_locked

    @preprocess.setter
    def is_locked(self, value: bool):
        self._is_locked = value

    @property
    def custom(self) -> bool:
        return self._custom

    @custom.setter
    def custom(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("custom must be a bool.")

        self._custom = value

    @property
    def parent(self) -> str:
        return self._parent

    @parent.setter
    def parent(self, value: str):
        if value is None:
            self._parent = None
        else:
            self._parent = UUID(value)

    def insert(self) -> Response:
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""
        url = f"project/{self._project.uuid}/segmenter/"

        data = self._to_representation()

        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)

        if err is False:
            self.uuid = response_data["id"]

        return response

    def update(self) -> Response:
        """Calls the REST API and updates the object on the server."""
        url = f"project/{self._project.uuid}/segmenter/{self.uuid}/"

        data = self._to_representation()

        response = self._connection.request("put", url, data)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def delete(self) -> Response:
        """Calls the REST API and deletes the object from the server."""
        url = f"project/{self._project.uuid}/segmenter/{self.uuid}/"
        response = self._connection.request("delete", url)
        utility.check_server_response(response)

        return response

    def refresh(self) -> Response:
        """Calls the REST API and populates the local object's properties from the server."""
        url = f"project/{self._project.uuid}/segmenter/{self.uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response


class SegmenterSet(BaseSet):

    """Base class for a segmenter object."""

    def __init__(
        self, connection: Connection, project: Project, initialize_set: bool = True
    ):
        self._connection = connection
        self._project = project
        self._set = None
        self._objclass = Segmenter
        self._attr_key = "name"

        if initialize_set:
            self.refresh()

    @property
    def get_set_url(self):
        return f"project/{self._project.uuid}/segmenter/"
