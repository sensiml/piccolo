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

logger = logging.getLogger(__name__)

from requests import Response
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project
    from sensiml.datamanager.label import Label


class LabelValueTypes(object):
    Int = "integer"
    Float = "float"
    String = "string"


class LabelValue(Base):
    """Base class for a label object."""

    _fields = ["uuid", "value", "created_at", "last_modified", "color"]

    def __init__(self, connection: Connection, project: Project, label: Label):
        """Initialize a metadata object.

        Args:
            connection
            project
            label
        """
        if label._metadata:
            raise Exception("Must be label not metadata")

        self._uuid = ""
        self._value = ""
        self._color = None
        self._last_modified = ""
        self._created_at = ""
        self._connection = connection
        self._project = project
        self._label = label

    @property
    def uuid(self) -> str:
        """Auto generated unique identifier for the  label value object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def value(self) -> str:
        """The data type of the label value object"""
        return self._value

    @value.setter
    def value(self, value: str):
        """The data type of the label value object"""
        self._value = value

    @property
    def created_at(self):
        """The created time of the label value object"""
        return self._created_at

    @property
    def label(self) -> Label:
        return self._label

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        self._color = value

    def insert(self) -> Response:
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""

        url = f"project/{self._project.uuid}/{self._label._label_or_metadata}/{self._label.uuid}/labelvalue/"

        data = {"value": self.value, "color": self.color}
        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)

        if err is False:
            self.uuid = response_data["uuid"]

        return response

    def update(self) -> Response:
        """Calls the REST API and updates the object on the server."""
        url = "project/{0}/{1}/{2}/labelvalue/{3}".format(
            self._project.uuid,
            self._label._label_or_metadata,
            self._label.uuid,
            self.uuid,
        )

        data = self._to_representation()

        response = self._connection.request("put", url, data)
        utility.check_server_response(response)

        return response

    def delete(self) -> Response:
        """Calls the REST API and deletes the object from the server."""
        url = "project/{0}/{1}/{2}/labelvalue/{3}".format(
            self._project.uuid,
            self._label._label_or_metadata,
            self._label.uuid,
            self.uuid,
        )
        response = self._connection.request("delete", url)
        utility.check_server_response(response)

        return response

    def refresh(self) -> Response:
        """Calls the REST API and populates the local object's properties from the server."""
        url = "project/{0}/{1}/{2}/labelvalue/{3}".format(
            self._project.uuid,
            self._label._label_or_metadata,
            self._label.uuid,
            self.uuid,
        )
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def initialize_from_dict(self, data: dict):
        """Reads a json dictionary and populates a single metadata object.

        Args:
            dict (dict): contains the uuid, value
        """
        self.uuid = data["uuid"]
        self.value = data["value"]
        self.color = data["color"]
        self._data = data


class LabelValueSet(BaseSet):
    def __init__(self, connection, project, label, initialize_set=True):
        """Initialize a metadata object.

        Args:
            connection
            project
        """
        self._connection = connection
        self._project = project
        self._label = label
        self._set = None
        self._objclass = LabelValue
        self._attr_key = "value"

        if initialize_set:
            self.refresh()

    @property
    def label_values(self):
        return self.objs

    @property
    def get_set_url(self) -> str:
        return f"project/{self._project.uuid}/{self._label._label_or_metadata}/{self._label.uuid}/labelvalue/"

    def _new_obj_from_dict(self, data: dict) -> LabelValue:
        """Creates a new label from data in the dictionary.

        Args:
            data (dict): contains label_value properties value, uuid

        Returns:
            label object

        """

        obj = self._objclass(self._connection, self._project, self._label)
        obj.initialize_from_dict(data)
        return obj

    def __str__(self) -> str:
        s = ""
        if self._set:
            label = self._set[0]._label
            s = "LABEL\n"
            s += "\tname: " + str(label.name) + " uuid: " + str(label.uuid) + "\n"
            s += "LABEL VALUES\n"
            for lbv in self._set:
                s += "\tvalue: " + str(lbv.value) + " uuid:" + str(lbv.uuid) + "\n"

        return s
