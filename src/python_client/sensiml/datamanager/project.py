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
import datetime
import json

from pandas import DataFrame

import sensiml.base.utility as utility
from sensiml.datamanager import CaptureConfigurations
from sensiml.datamanager.captures import Captures, BackgroundCaptures
from sensiml.datamanager.capture import BackgroundCapture
from sensiml.datamanager.featurefiles import FeatureFiles
from sensiml.datamanager.knowledgepack import KnowledgePack
from sensiml.datamanager.queries import Queries
from sensiml.datamanager.sandboxes import Sandboxes
from sensiml.method_calls.functioncall import FunctionCall

from typing import TYPE_CHECKING, Optional
from requests import Response

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.capture import Capture


class Project(object):
    """Base class for a project."""

    _uuid = ""
    _name = ""
    _created_at = None
    _schema = {}
    _settings = {}
    _query_optimized = True

    def __init__(self, connection: Connection):
        """Initialize a project instance.

        Args:
            connection (connection object)
        """
        self._connection = connection
        self._feature_files = FeatureFiles(self._connection, self)
        self._captures = Captures(self._connection, self)
        self._background_captures = BackgroundCaptures(self._connection)
        self._background_capture = BackgroundCapture(self._connection)
        self._sandboxes = Sandboxes(self._connection, self)
        self._queries = Queries(self._connection, self)
        self._plugin_config = None
        self._capture_configurations = CaptureConfigurations(self._connection, self)

    @property
    def uuid(self) -> str:
        """Auto generated unique identifier for the project object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def name(self) -> str:
        """Name of the project object"""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def created_at(self) -> datetime.datetime:
        """Date of the project creation"""
        return self._created_at

    @created_at.setter
    def created_at(self, value: str):
        if value:
            self._created_at = datetime.datetime.strptime(
                value[:-6], "%Y-%m-%dT%H:%M:%S.%f"
            )

    @property
    def schema(self) -> dict:
        """Schema of the project object"""
        return self._schema

    @schema.setter
    def schema(self, value: dict):
        self._schema = value

    @property
    def plugin_config(self) -> dict:
        """Plugin Config of the project object"""
        return self._plugin_config

    @plugin_config.setter
    def plugin_config(self, value: dict):
        self._plugin_config = value

    @property
    def settings(self) -> dict:
        """Global settings of the project object"""
        return self._settings

    @property
    def query_optimized(self) -> bool:
        return self._query_optimized

    def add_segmenter(
        self,
        name: str,
        segmenter: FunctionCall,
        preprocess: Optional[dict] = None,
        custom: bool = False,
    ) -> Response:
        """Saves a segmentation algorithm as the project's global segmentation setting.

        Args:
            name(str): Name to call the segmenter
            segmenter(FunctionCall): segmentation call object that the project will use by default
            preprocess(dict): Segment transforms to perform before segmenter
            custom(bool): a custom segmenter, or one of our server side segmenters


        """
        url = f"project/{self.uuid}/segmenter/"
        if segmenter is not None:
            if not isinstance(segmenter, FunctionCall):
                print("segmenter is not a function call.")
                return
            segmenter_dict = segmenter._to_dict()
            if not segmenter_dict["type"] == "segmenter":
                print("segmenter is not a function call for a segmenter")
                return
            parameters = json.dumps(segmenter_dict)
        else:
            parameters = None

        if not isinstance(custom, bool):
            print("Custom must either be true or false.")
            return

        if preprocess:
            if isinstance(preprocess, dict):
                preprocess = json.dumps(preprocess)

        segmenter_info = {
            "custom": custom,
            "name": str(name),
            "parameters": parameters,
            "preprocess": preprocess,
        }

        request = self._connection.request("post", url, segmenter_info)
        response, err = utility.check_server_response(request)
        if err is False:
            print("Segmenter Uploaded.")

        return response

    def insert(self) -> Response:
        """Calls the REST API to insert a new object, uses only the name and schema."""
        url = "project/"
        project_info = {
            "name": self.name,
            "capture_sample_schema": self.schema,
            "settings": self.settings,
            "plugin_config": self.plugin_config,
        }
        request = self._connection.request("post", url, project_info)
        response, err = utility.check_server_response(request)
        if err is False:
            self.uuid = response["uuid"]
            self._settings = response["settings"]
            self._query_optimized = response.get("optimized", True)
            self.plugin_config = response["plugin_config"]

        return response

    def update(self) -> Response:
        """Calls the REST API to update the object."""
        url = f"project/{self.uuid}/"
        project_info = {
            "name": self.name,
            "capture_sample_schema": self.schema,
            "settings": self.settings,
            "plugin_config": self.plugin_config,
        }
        request = self._connection.request("patch", url, project_info)
        response, err = utility.check_server_response(request)
        if err is False:
            self.plugin_config = response.get("plugin_config", None)

        return response

    def delete(self) -> Response:
        """Calls the REST API to delete the object."""
        url = f"project/{self.uuid}/"
        request = self._connection.request("delete", url)
        response, err = utility.check_server_response(request)

        return response

    def delete_async(self) -> Response:
        """Calls the Async REST API to delete the project."""
        url = f"project-delete/{self.uuid}/"
        response = self._connection.request("post", url)
        utility.check_server_response(response)

        return response

    def delete_async_status(self) -> Response:
        """Calls the Async REST API to get the status of deleting the project."""
        url = f"project-delete/{self.uuid}/"
        response = self._connection.request("get", url)
        utility.check_server_response(response)

        return response

    def delete_async_stop(self) -> Response:
        """Calls the Async REST API to stop deleting the project."""
        url = f"project-delete/{self.uuid}/"
        response = self._connection.request("delete", url)
        utility.check_server_response(response)

        return response

    def refresh(self) -> Response:
        """Calls the REST API and self populates from the server."""
        url = f"project/{self.uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.name = response_data["name"]
            self.schema = response_data["capture_sample_schema"]
            self._query_optimized = response_data.get("optimized", True)
            self.plugin_config = response_data.get("plugin_config", None)
            self.created_at = response_data.get("created_at", None)

        return response

    def query_optimize(self, force: bool = False):
        self.refresh()
        """Calls the REST API and optimizes or re-optimizes the project for querying."""
        if not self.schema or not len(self._captures.get_captures()):
            print(
                f"Cannot query optimize {self._name} until there are uploaded captures."
                + "If data was uploaded, try client.project.refresh() followed by client.project.query_optimize()."
            )
        elif not self._query_optimized:
            print(f"{self._name} is not optimized for querying. Optimizing now...")
            self._create_profile()
        elif force:
            print(f"Re-optimizing {self._name} for querying now...")
            self._delete_profile()
            self._create_profile()

    def _create_profile(self) -> Response:
        """Calls the REST API and creates a profile for optimized query times."""
        url = f"project/{self.uuid}/profile/"
        response = self._connection.request("post", url)
        _, err = utility.check_server_response(response, is_octet=True)
        if err is False:
            self.refresh()

        return response

    def _delete_profile(self) -> Response:
        """Calls the REST API and drops the project profile."""
        url = f"project/{self.uuid}/profile/"
        # Make a call to delete the profile
        response = self._connection.request("post", url)
        _, err = utility.check_server_response(response, is_octet=True)
        if err is False:
            self.refresh()
        return response

    def get_knowledgepack(self, kp_uuid: str) -> KnowledgePack:
        """Gets the KnowledgePack(s) created by the sandbox.

        Returns:
            a KnowledgePack instance, list of instances, or None
        """
        url = f"knowledgepack/{kp_uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            kp = KnowledgePack(
                self._connection, self.uuid, response_data.get("sandbox_uuid")
            )
            kp.initialize_from_dict(response_data)
            return kp

    def _get_knowledgepacks(self) -> DataFrame:
        """Gets the KnowledgePack(s) created by the sandbox.

        Returns:
            a KnowledgePack instance, list of instances, or None
        """
        url = f"project/{self.uuid}/knowledgepack/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return DataFrame(response_data)

        return response

    def list_knowledgepacks(self) -> DataFrame:
        """Lists all of the knowledgepacks associated with this project

        Returns:
            DataFrame: knowledgepacks on kb cloud
        """

        knowledgepacks = self._get_knowledgepacks().rename(
            columns={
                "name": "Name",
                "project_name": "Project",
                "sandbox_name": "Pipeline",
                "uuid": "kp_uuid",
                "created_at": "Created",
                "knowledgepack_description": "kp_description",
            }
        )

        if len(knowledgepacks) < 1:
            print("No Knowledgepacks stored for this project on the cloud.")
            return None
        return knowledgepacks[knowledgepacks["Name"] != ""][
            [
                "Name",
                "accuracy",
                "features_count",
                "Created",
                "Project",
                "Pipeline",
                "kp_uuid",
                "kp_description",
            ]
        ]

    def initialize_from_dict(self, data: dict):
        """Reads a json dict and populates a single project.

        Args:
            dict (dict): contains the project's 'name', 'uuid', 'schema', and 'settings' properties
        """
        self.uuid = data["uuid"]
        self.name = data["name"]
        self.schema = data["capture_sample_schema"]
        self._settings = data.get("settings", [])
        self._query_optimized = data.get("optimized", True)
        self.plugin_config = data.get("plugin_config", None)
        self.created_at = data.get("created_at", None)

    def __getitem__(self, key: str) -> Capture:
        if type(key) is str:
            return self.captures.get_capture_by_filename(key)
        else:
            return self.captures.get_captures()[key]

    @property
    def featurefiles(self) -> FeatureFiles:
        return self._feature_files

    @property
    def captures(self) -> Captures:
        return self._captures

    @property
    def sandboxes(self) -> Sandboxes:
        return self._sandboxes

    @property
    def queries(self) -> Queries:
        return self._queries

    @property
    def capture_configurations(self) -> CaptureConfigurations:
        return self._capture_configurations

    def columns(self) -> list[str]:
        """Returns the sensor columns available in the project.

        Returns:
            columns (list[str]): a list of string names of the project's sensor columns
        """
        try:
            columnnames = self.schema.keys()
            return columnnames
        except:
            return None

    def metadata_columns(self) -> list[str]:
        """Returns the metadata columns available in the project.

        Returns:
            columns (list[str]): a list of string names of the project's metadata columns
        """
        return self.captures.get_metadata_names()

    def metadata_values(self) -> dict:
        return self.captures.get_metadata_names_and_values()

    def label_values(self) -> dict:
        return self.captures.get_label_names_and_values()

    def label_columns(self) -> list[str]:
        """Returns the label columns available in the project.

        Returns:
            columns (list[str]): a list of string names of the project's metadata columns
        """
        return self.captures.get_label_names()

    def statistics(self) -> DataFrame:
        """Gets all capture statistics for the project.

        Returns:
            DataFrame of capture statistics
        """
        url = f"project/{self.uuid}/statistics/"
        data = {"events": False}
        response = self._connection.request("get", url, json=data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            data = utility.make_statistics_table(response_data)
            return data
        else:
            return response

    def get_active_pipelines(self):
        url = f"project/{self.uuid}/active/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            if response_data:
                return response_data

        return response

    def get_segmenters(self) -> DataFrame:
        url = f"project/{self.uuid}/segmenter/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            if response_data:
                return DataFrame(response_data).set_index("id")

        return response

    def get_project_summary(self) -> dict:
        url = f"project-summary/{self.uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        return response_data

    def get_capture_stats(self) -> DataFrame:
        url = f"project/{self.uuid}/capture-stats/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            if response_data:
                return DataFrame(response_data)

        return None

    def get_project_dcli(self):
        url = f"project/{self.uuid}/dcli/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return response_data

        return response
