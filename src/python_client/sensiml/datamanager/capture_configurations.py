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
from sensiml.datamanager.capture_configuration import CaptureConfiguration
import sensiml.base.utility as utility
from typing import Optional, List, TYPE_CHECKING
from typing import Optional


if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project


class CaptureConfigurationExistsError(Exception):
    """Base class for a Capture exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class CaptureConfigurations:
    """Base class for a collection of Captures."""

    def __init__(self, connection: Connection, project: Project):
        self._connection = connection
        self._project = project

    def __getitem__(self, key) -> CaptureConfiguration:
        return self.get_capture_configurations()[key]

    def create_capture_configuration(
        self, name: str, configuration: dict, uuid: Optional[str] = None
    ) -> CaptureConfiguration:
        """Creates a capture object from the given filename and filepath.

        Args:
            name (str): desired name of the file on the server
            configuration (dict): configuration file
            uuid (str): Specify the uuid this configuration will be created with

        Returns:
            capture_configuration object

        Raises:
            CaptureClonfigurationExistsError, if the Capture already exists on the server
        """
        data = {"connection": self._connection, "project": self._project, "name": name}

        if self.get_capture_configuration_by_name(name) is not None:
            raise CaptureConfigurationExistsError(
                f"capture configuration {name} already exists."
            )
        else:
            instance = CaptureConfiguration.initialize_from_dict(data)
            instance.configuration = configuration
            instance.uuid = uuid
            instance.insert()

        return instance

    def build_capture_list(self) -> dict:
        """Populates the function_list property from the server."""
        capture_list = {}

        response = self.get_capture_configurations()
        for capture_configuration in response:
            capture_list[capture_configuration.name] = capture_configuration

        return capture_list

    def get_capture_configuration_by_name(self, name: str) -> CaptureConfiguration:
        """Gets a capture configuration object from the server using its name property.

        Args:
            name (str): the capture configuration's name

        Returns:
            capture configuration  object or None if it does not exist
        """
        capture_list = self.get_capture_configurations()

        for capture in capture_list:
            if capture.name == name:
                return capture

        return None

    def _new_capture_configuration_from_dict(self, data: dict) -> CaptureConfiguration:
        """Creates a new capture using the dictionary.

        Args:
            data (dict): dictionary of capture properties

        Returns:
            capture configuration object
        """
        data.update({"connection": self._connection, "project": self._project})
        return CaptureConfiguration.initialize_from_dict(data)

    def get_capture_configurations(self) -> List[CaptureConfiguration]:
        """Gets all capture configurations from the server.

        Returns:
            list of capture configurations for the project
        """
        # Query the server and get the json
        url = f"project/{self._project.uuid}/captureconfiguration/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        # Populate each capture from the server
        data = []
        if err is False:
            for params in response_data:
                data.append(self._new_capture_configuration_from_dict(params))

        return data
