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
import datetime
import sensiml.base.utility as utility
from typing import Optional, TYPE_CHECKING
from requests import Response

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project

logger = logging.getLogger(__name__)


class CaptureConfiguration(object):
    """Base class for a Capture."""

    def __init__(
        self,
        connection: Connection,
        project: Project,
        name: str = "",
        uuid: str = "",
        configuration: Optional[dict] = None,
        created_at: Optional[datetime.datetime] = None,
        **kwargs,
    ):
        """Initialize a Capture instance."""
        self._connection = connection
        self._project = project
        self._uuid = uuid
        self._configuration = configuration
        self._name = name
        self._created_at = created_at

    @property
    def uuid(self):
        """Auto generated unique identifier for the Capture object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        """Auto generated unique identifier for the Capture object"""
        self._uuid = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def created_at(self):
        """Date of the Pipeline creation"""
        return self._created_at

    @created_at.setter
    def created_at(self, value: str):
        if value is None:
            return
        self._created_at = datetime.datetime.strptime(
            value[:-6], "%Y-%m-%dT%H:%M:%S.%f"
        )

    @property
    def configuration(self):
        """The local or server path to the Capture file data"""
        return self._configuration

    @configuration.setter
    def configuration(self, value: dict):
        self._configuration = value

    def insert(self) -> Response:
        """Calls the REST API to insert a new Capture."""
        url = f"project/{self._project.uuid}/captureconfiguration/"
        data = {"name": self.name, "configuration": self.configuration}
        if self.uuid:
            data["uuid"] = self.uuid
        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self._uuid = response_data["uuid"]

        return response

    def update(self) -> Response:
        """Calls the REST API to update the capture."""
        url = f"project/{self._project.uuid}/captureconfiguration/{self._uuid}/"

        data = {"name": self.name}
        if self.configuration is not None:
            data["configuration"] = self.configuration

        response = self._connection.request("put", url, data)
        response_data, err = utility.check_server_response(response)

        return response

    def delete(self) -> Response:
        """Calls the REST API to delete the capture from the server."""
        url = f"project/{self._project.uuid}/captureconfiguration/{self._uuid}/"
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)

        return Response

    def refresh(self) -> Response:
        """Calls the REST API and self populates properties from the server."""
        url = f"project/{self._project.uuid}/captureconfiguration/{self._uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.name = response_data["name"]
            self.configuration = response_data["configuration"]

        return response

    @classmethod
    def initialize_from_dict(cls, data: dict):
        """Reads a dictionary or properties and populates a single capture.

        Args:
            capture_dict (dict): contains the capture's 'name' property

        Returns:
            capture object
        """
        assert isinstance(data, dict)

        return CaptureConfiguration(**data)
