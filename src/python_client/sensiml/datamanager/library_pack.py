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
from sensiml.base import utility
from sensiml.datamanager.base import Base, BaseSet
from requests import Response

from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from sensiml.connection import Connection


class LibraryPack(Base):
    """Base class for a library pack object"""

    _uuid = ""
    _name = ""
    _build_version = None
    _maintainer = ""
    _description = ""

    _fields = [
        "uuid",
        "name",
        "build_version",
        "description",
        "maintainer",
    ]

    _read_only_fields = ["uuid", "build_version"]

    def __init__(self, connection: Connection, uuid: Optional[str] = None):
        self._connection = connection
        if uuid:
            self.uuid = uuid
            self.refresh()

    @property
    def base_url(self) -> str:
        return "library-pack/"

    @property
    def detail_url(self) -> str:
        return f"library-pack/{self.uuid}/"

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def build_version(self) -> str:
        return self._build_version

    @build_version.setter
    def build_version(self, value: str):
        self._build_version = value

    @property
    def maintainer(self) -> str:
        return self._maintainer

    @maintainer.setter
    def maintainer(self, value: str):
        self._maintainer = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

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

    def insert(self) -> Response:
        """Calls the REST API to insert a new object."""

        data = self._to_representation()

        response = self._connection.request("post", self.base_url, data)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def update(self) -> Response:
        """Calls the REST API and updates the object on the server."""

        data = self._to_representation()

        response = self._connection.request("put", self.detail_url, data)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response


class LibraryPackSet(BaseSet):
    def __init__(self, connection: Connection, initialize_set: bool = True):
        """Initialize a libraryPack object.

        Args:
            connection
        """
        self._connection = connection
        self._set = None
        self._objclass = LibraryPack
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    @property
    def library_packs(self):
        return self.objs

    @property
    def get_set_url(self) -> str:
        return "library-pack/"

    def _new_obj_from_dict(self, data: dict) -> LibraryPack:
        """Creates a new object from the response data from the server.

        Args:
            data (dict): contains properties of the object

        Returns:
            obj of type _objclass

        """
        obj = self._objclass(self._connection)
        obj.initialize_from_dict(data)
        return obj
