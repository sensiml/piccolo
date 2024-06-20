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
import sensiml.base.utility as utility
from sensiml.datamanager.capture import Capture, BackgroundCapture
from typing import Optional, Tuple, TYPE_CHECKING
from pandas import DataFrame


if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project


class CaptureExistsError(Exception):
    """Base class for a Capture exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Captures:
    """Base class for a collection of Captures."""

    def __init__(self, connection: Connection, project: Project):
        self._connection = connection
        self._project = project
        self._reserved_metadata_names = ["capture_uuid", "segment_uuid"]
        self._capture_list = {}

    def __getitem__(self, key: str) -> Capture:
        if type(key) == str:
            return self.get_capture_by_filename(key)
        else:
            return self.get_captures()[key]

    def create_capture(
        self,
        filename: str,
        filepath: str,
        asynchronous: bool = True,
        capture_info: Optional[dict] = None,
    ) -> Capture:
        """Creates a capture object from the given filename and filepath.

        Args:
            filename (str): desired name of the file on the server
            filepath (str): local path to the file to be uploaded
            asynchronous (bool): Whether to process asynchronously

        Returns:
            capture object

        Raises:
            CaptureExistsError, if the Capture already exists on the server
        """
        capture_dict = {
            "connection": self._connection,
            "project": self._project,
            "filename": filename,
        }

        if self.get_capture_by_filename(filename) is not None:
            raise CaptureExistsError(f"capture {filename} already exists.")
        else:
            capture = Capture.initialize_from_dict(capture_dict)
            capture.path = filepath
            capture.capture_info = (
                capture_info if isinstance(capture_info, dict) else {}
            )
            capture.insert(asynchronous=asynchronous)

        return capture

    def get_or_create(
        self,
        filename: str,
        filepath: str,
        asynchronous: bool = True,
        capture_info: Optional[dict] = None,
    ) -> Capture:
        """Creates a capture object from the given filename and filepath.

        Args:
            filename (str): desired name of the file on the server
            filepath (str): local path to the file to be uploaded
            asynchronous (bool): Whether to process asynchronously

        Returns:
            capture object

        Raises:
            CaptureExistsError, if the Capture already exists on the server
        """
        capture_dict = {
            "connection": self._connection,
            "project": self._project,
            "filename": filename,
        }

        if self.get_capture_by_filename(filename) is not None:
            return self.get_capture_by_filename(filename)
        else:
            capture = Capture.initialize_from_dict(capture_dict)
            capture.path = filepath
            capture.capture_info = (
                capture_info if isinstance(capture_info, dict) else {}
            )
            capture.insert(asynchronous=asynchronous)

        return capture

    def build_capture_list(self, force: bool = True) -> dict:
        """Populates the function_list property from the server."""

        if not force and self._capture_list:
            return self._capture_list

        capture_response = self.get_captures()
        for capture in capture_response:
            self._capture_list[capture.filename] = capture

        return self._capture_list

    def get_capture_by_filename(self, filename: str, force: bool = False) -> Capture:
        """Gets a capture object from the server using its filename property.

        Args:
            filename (str): the capture's name
            force (bool): rebuild the cached list of files

        Returns:
            capture object or None if it does not exist
        """
        capture_list = self.build_capture_list(force=force)

        return capture_list.get(filename)

    def get_capture_by_uuid(self, uuid: str) -> Capture:
        """Gets a capture object from the server using its filename property.

        Args:
            filename (str): the capture's name

        Returns:
            capture object or None if it does not exist
        """
        """Calls the REST API to update the capture."""
        url = f"project/{self._project.uuid}/capture/{uuid}/"

        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        return self._new_capture_from_dict(response_data)

    def get_capture_urls_by_uuid(self, capture_uuids: str, expires_in: int = 100):

        url = f"project/{self._project.uuid}/capture-files/"
        data = {"capture_uuids": capture_uuids, "expires_in": expires_in}

        response = self._connection.request("post", url, json=data)
        response_data, err = utility.check_server_response(response)

        return response_data

    def get_capture_urls_by_name(self, capture_list: list[str], expires_in: int = 100):

        capture_uuids = [
            x.uuid
            for key, x in self.build_capture_list().items()
            if key in capture_list
        ]

        return self.get_capture_urls_by_uuid(capture_uuids, expires_in=expires_in)

    def get_statistics(self) -> Tuple[DataFrame, bool]:  # type: ignore
        """Gets all capture statistics for the project.

        Returns:
            DataFrame of capture statistics
        """
        url = f"project/{self._project.uuid}/statistics/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            data, error_report = utility.make_statistics_table(response_data)
            return data, error_report
        else:
            return None

    def get_metadata_names_and_values(self) -> list[dict]:
        """Gets all the metadata names and possible values for a project.

        Returns:
            list(dict) containing metadata names and values
        """
        url = f"project/{self._project.uuid}/metadata/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            metadata_values = [
                {
                    "name": item["name"],
                    "values": [i["value"] for i in item["label_values"]],
                }
                for item in response_data
            ]
            return metadata_values

    def get_metadata_names(self) -> list[str]:
        """Gets all the metadata names within a project.

        Returns:
            list of metadata names
        """
        url = f"project/{self._project.uuid}/metadata/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return [
                item["name"] for item in response_data
            ] + self._reserved_metadata_names

    def get_captures_by_metadata(self, key: str, value: any):
        """Gets captures by existing metadata key-values.

        Args:
            key (str): the name of the metadata item
            value (str, int, or float): the value to search for

        Returns:
            list of captures that have the desired metadata key-value pair
        """
        url = f"project/{self._project.uuid}/capture/metadata/[{key}]=[{value}]/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            captures = []
            for capture_params in response_data:
                captures.append(self._new_capture_from_dict(capture_params))
            return captures

    def get_label_names_and_values(self) -> dict:
        """Gets all the label names and possible values for a project.

        Returns:
            list(dict) containing metadata names and values
        """
        url = f"project/{self._project.uuid}/label/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            metadata_values = [
                {
                    "name": item["name"],
                    "values": [i["value"] for i in item["label_values"]],
                }
                for item in response_data
            ]
            return metadata_values

    def get_label_names(self) -> list[str]:
        """Gets all the label names within a project.

        Returns:
            list of label names
        """
        url = f"project/{self._project.uuid}/label/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return [item["name"] for item in response_data]

    def _new_capture_from_dict(self, capture_dict) -> Capture:
        """Creates a new capture using the dictionary.

        Args:
            capture_dict (dict): dictionary of capture properties

        Returns:
            capture object
        """
        capture_dict.update({"connection": self._connection, "project": self._project})
        return Capture.initialize_from_dict(capture_dict)

    def get_captures(self) -> list[Capture]:
        """Gets all captures from the server.

        Returns:
            list of captures for the project
        """
        # Query the server and get the json
        url = f"project/{self._project.uuid}/capture/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        # Populate each capture from the server
        captures = []
        if err is False:
            for capture_params in response_data:
                captures.append(self._new_capture_from_dict(capture_params))

        return captures


class BackgroundCaptures:
    """Base class for a collection of Background Captures."""

    def __init__(self, connection):
        self._connection = connection

    def get_background_captures(self) -> list[Capture]:
        """Gets all captures from the server.

        Returns:
        list of all available background captures
        """

        # Query the server and get the json
        url = "background-capture/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        # Populate each capture from the server
        captures = []
        if err is False:
            for capture_params in response_data:
                capture_params["filename"] = capture_params["name"]
                captures.append(
                    BackgroundCapture(
                        self._connection,
                        **capture_params,
                    )
                )

        return captures

    def get_background_capture_urls_by_uuid(
        self, capture_uuids: list[str], expires_in: int = 100
    ) -> list[Capture]:

        url = f"background-capture-files/"
        data = {"background_capture_uuids": capture_uuids, "expires_in": expires_in}

        response = self._connection.request("post", url, json=data)
        response_data, err = utility.check_server_response(response)

        return response_data
