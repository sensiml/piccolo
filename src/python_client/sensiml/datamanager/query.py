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
import datetime
from pandas import DataFrame
import re
import warnings

import sensiml.base.utility as utility

from typing import TYPE_CHECKING, Optional
from requests import Response

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project


class QueryColumns(object):
    """Base class for the query columns and metadata_columns properties"""

    def __init__(self, columns: Optional[list] = None):
        if columns is None:
            columns = list()

        if len(columns) > 0:
            self._columns = columns
        else:
            self._columns = []

    def add(self, items: list[str]):
        """Adds a column name or names for query selection.

        Args:
            items (str or list[str]): column names to add

        Note:
            The named column(s) must exist in the project and duplicate column names will be ignored
        """
        for item in items:
            if item not in self._columns:
                self._columns.append(item)

    def remove(self, item: str):
        """Removes a column name from query selection.

        Args:
            item (str): column name to remove
        """
        self._columns.remove(item)

    def clear(self):
        """Clears all column names from query selection"""
        self._columns = []

    def __str__(self):
        return json.dumps(self._columns)

    def __iter__(self):
        return iter(self._columns)


class Query(object):
    """Base class for a query.

    Queries extract project data, or a subset of project data, for use in a pipeline. The query must specify which
    columns of data to extract and what filter conditions to apply.
    """

    def __init__(self, connection: Connection, project: Project):
        """Initializes a query instance"""
        self._uuid = ""
        self._name = ""
        self._columns = QueryColumns()
        self._metadata_columns = QueryColumns()
        self._metadata_filter = ""
        self._segmenter = None
        self._label_column = ""
        self._combine_labels = None
        self._dirty = False
        self._capture_configurations = ""
        self._connection = connection
        self._summary_statistics = None
        self._project = project
        self._created_at = None
        self._cache = None
        self._task_status = None
        self._last_modified = None

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def name(self) -> str:
        """Name of the query"""
        return self._name

    @property
    def summary_statistics(self) -> dict:
        """Name of the query"""
        return self._summary_statistics

    @summary_statistics.setter
    def summary_statistics(self, value: dict):
        self._summary_statistics = value

    @name.setter
    def name(self, value: str):
        self._dirty = True
        self._name = value

    @property
    def columns(self) -> list[str]:
        """Sensor columns to include in the query result

        Note:
            Columns must correspond to actual project sensor columns or the reserved word 'SequenceID' for the
            original sample index.
        """
        self._dirty = True
        return self._columns

    @property
    def created_at(self) -> datetime.datetime:
        """Date of the Pipeline creation"""
        return self._created_at

    @created_at.setter
    def created_at(self, value: str):
        self._created_at = datetime.datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")

    @property
    def label_column(self) -> str:
        """Label columns to use in the query result

        Note:
            Columns must correspond to actual project label column"""

        self._dirty = True
        return self._label_column

    @label_column.setter
    def label_column(self, value: str):
        self._dirty = True
        self._label_column = value

    @property
    def combine_labels(self) -> dict:
        """Combine label values into new value to use in the query result

        Label = Gesture
        Label_Values = A,B,C,D,E
        combine_labels = {'Group1':['A','B',C'],'Group2':['D','E']}

        the labels that will be returned will be group1 and group2
        """

        self._dirty = True
        return self._combine_labels

    @combine_labels.setter
    def combine_labels(self, value: dict):
        self._dirty = True
        self._combine_labels = value

    @property
    def metadata_columns(self) -> list[str]:
        """Metadata columns to include in the query result

        Note:
            Columns must correspond to actual project metadata columns.
        """
        self._dirty = True
        return self._metadata_columns

    @property
    def metadata_filter(self) -> str:
        """Filter criteria of the query

        Args:
            value (str): similar to a SQL WHERE clause, the string can contain any number of AND-concatenated
              expressions where square brackets surround the column name and comparison value, with the operator in
              between. Supported operators: >, >=, <, <=, =, !=, IN

        Examples::

            metadata_filter = '[Subject] > [5] AND [Subject] <= [15]'
            metadata_filter = '[Gender] = [Female] AND [Activity] != [Walking]'
            metadata_filter = '[Subject] IN [5, 7, 9, 11, 13, 15]'

        Note:
            Queries do not support OR-concatenation between expressions, but often the IN operator can be used to
            achieve OR-like functionality on a single column. For example::

                [Gesture] IN [A, M, L]

            is equivalent to::

                [Gesture] = [A] OR [Gesture] = [M] OR [Gesture] = [L]

        """
        return self._metadata_filter

    @metadata_filter.setter
    def metadata_filter(self, value: str):
        self._dirty = True
        self._metadata_filter = value

    @property
    def capture_configurations(self):
        return self._capture_configurations

    @capture_configurations.setter
    def capture_configurations(self, value):
        self._dirty = True

        if isinstance(value, str):
            value = [value]

        if not isinstance(value, list):
            raise Exception("capture_configurations must be List or String")

        self._capture_configurations = json.dumps(value)

    @property
    def segmenter(self) -> int:
        """Segmenter to use for the query

        Args:
            value (int): ID of segmenter.

        """
        return self._segmenter

    @segmenter.setter
    def segmenter(self, value: int):
        if value is None or isinstance(value, int):
            self._segmenter = value
        else:
            raise ValueError("Value must be a integer")

    @property
    def task_status(self) -> str:
        return self._task_status

    @task_status.setter
    def task_status(self, value: str):
        self._task_status = value

    @property
    def last_modified(self) -> datetime.datetime:
        return self._last_modified

    @last_modified.setter
    def last_modified(self, value: str):
        self._last_modified = datetime.datetime.strptime(
            value[:19], "%Y-%m-%dT%H:%M:%S"
        )

    @property
    def cache(self) -> list[dict]:
        return self._cache

    @cache.setter
    def cache(self, value: list[dict]):
        self._cache = value

    def insert(self, renderer=None) -> Response:
        """Calls the REST API and inserts a new query."""

        url = f"project/{self._project.uuid}/query/"

        data = {
            "name": self.name,
            "columns": self.columns._columns,
            "metadata_columns": self.metadata_columns._columns,
            "metadata_filter": self.metadata_filter,
            "segmenter_id": self._segmenter,
            "label_column": self.label_column,
            "combine_labels": self.combine_labels,
            "capture_configurations": self.capture_configurations,
        }

        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response, renderer=renderer)
        if err is False:
            self.uuid = response_data["uuid"]
            self._dirty = False

        return response

    def update(self, renderer=None) -> Response:
        """Calls the REST API and updates the query object on the server."""

        url = f"project/{self._project.uuid}/query/{self.uuid}/"

        self._checked = None
        data = {
            "name": self.name,
            "columns": self.columns._columns,
            "metadata_columns": self.metadata_columns._columns,
            "metadata_filter": self.metadata_filter,
            "segmenter_id": self._segmenter,
            "label_column": self.label_column,
            "combine_labels": self.combine_labels,
            "capture_configurations": self.capture_configurations,
        }

        if len(data["columns"]) > 0 or len(data["metadata_columns"]) > 0:
            filters = (
                self._metadata_filter.split("AND")
                if len(self._metadata_filter) > 0
                else []
            )

            for i, filter in enumerate([filter for filter in filters if len(filters)]):
                match = re.search(
                    "\[(?P<key>[0-9A-Za-z_\-\. \)\(]+)\]([ ]*(?P<symbol>[\>\=|\<\=|\=|\<\>|\>|\<|in|IN|!=]+)[ ]*\[(?P<value>.+)\])?",
                    str(filter),
                )
                if not match:
                    self._checked = 1
            if self._checked is None:
                response = self._connection.request("put", url, data)
                utility.check_server_response(response, renderer=renderer)
                return response
            else:
                self._metadata_filter = ""
                print("Metadata Filter is not formatted correctly!")
        else:
            print(
                "Sensor columns and, or metadata columns must be specified in order to query!"
            )

    def delete(self, renderer=None) -> Response:
        """Calls the REST API and deletes the query object from the server."""
        url = f"project/{self._project.uuid}/query/{self.uuid}/"
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response, renderer=renderer)
        self._dirty = False
        if err is False:
            print(response_data["result"])

        return Response

    def cache_query(self, renderer=None):
        """Caches the current version of the query."""
        url = f"project/{self._project.uuid}/query/{self.uuid}/cache/"
        response = self._connection.request("post", url)
        response_data, err = utility.check_server_response(response, renderer=renderer)

        if err is False:
            return response_data

        return response

    def cache_query_status(self, renderer=None):
        """Gest the status of the current caching of the query"""
        url = f"project/{self._project.uuid}/query/{self.uuid}/cache/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response, renderer=renderer)

        return response_data

    def cache_query_stop(self, renderer=None):
        """Kills the job for the currently executing query"""
        url = f"project/{self._project.uuid}/query/{self.uuid}/cache/"
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response, renderer=renderer)

        return response_data

    def statistics_segments(self, renderer=None) -> DataFrame:
        """Returns metadata statistics for the query."""

        url = f"project/{self._project.uuid}/query/{self.uuid}/statistics/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response, renderer=renderer)
        if err is False:
            return DataFrame(response_data)
        else:
            return None

    def get_statistics_summary(self, renderer=None):
        """Returns metadata statistics for the query."""

        url = f"project/{self._project.uuid}/query/{self.uuid}/summary-statistics/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response, renderer=renderer)
        if err is False:
            return response_data

        return response

    def check_query_cache_up_to_date(self, renderer=None):
        """Checks if the current cached query is up to date with the current training data.

        The sensor data in a query is cached when the query is built. If the segments or metadata
        have changed since the last time the sensor data was cached then in order for a query to
        use the new data it needs to be rebuilt. This API returns whether or not the sensor data
        has changed since the last time the query was cached.

        """

        url = f"project/{self._project.uuid}/query/{self.uuid}/cache-status/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response, renderer=renderer)
        if err is False:
            return response_data
        return response

    def plot_statistics(self, renderer=None, **kwargs):
        """Generates a bar plot of the query statistics"""
        data = self.statistics_segments(renderer=renderer)
        if data is not None:
            data.groupby(self.label_column).size().plot(kind="bar")

    def data(self, partition: int = 0) -> DataFrame:
        """Calls the REST API for query execution and returns the result.

        Note:
            Intended for previewing the query result before creating a query call object and using it in a sandbox
            step. The resulting DataFrame is not cached on the server, but once it is used in a sandbox it may be
            cached.
        """
        warnings.warn("This call has a timeout of two minutes.")

        if self._dirty:
            self.update()

        url = f"project/{self._project.uuid}/query/{self.uuid}/data/{partition}"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            error_report = None
            if not isinstance(response_data, list):
                data = DataFrame(response_data)
            else:
                try:
                    data = DataFrame(response_data[0])
                    error_report = response_data[1]
                except:
                    data = DataFrame(response_data)

            return data.sort_index(axis=0), error_report

        return response

    def size(self):
        """Returns the size of the dataframe which would result from the query."""
        # Sync the client-side query with server-side query object before we check the size
        if self._dirty:
            self.update()

        url = f"project/{self._project.uuid}/query/{self.uuid}/size/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if not err:
            return response_data

        return response

    def refresh(self):
        """Calls the REST API and self populate using the uuid."""
        url = f"project/{self._project.uuid}/query/{self.uuid}/"
        request = self._connection.request("get", url)
        response, err = utility.check_server_response(request)

        if err is False:
            self.uuid = response["uuid"]
            self.name = response["name"]
            self._columns = QueryColumns(response["columns"])
            self._label_column = response["label_column"]
            self._metadata_columns = QueryColumns(response["metadata_columns"])
            self.metadata_filter = response["metadata_filter"]
            self.segmenter = response["segmenter_id"]
            self.combine_labels = response["combine_labels"]
            self.capture_configurations = response["capture_configurations"]
            self.cache = response["cache"]
            self.task_status = response["task_status"]
            self.last_modified = response["last_modified"]
            self.summary_statistics = response["summary_statistics"]
            self._dirty = False

    def initialize_from_dict(self, data):
        """Reads a json dict and populates a single query."""
        self.uuid = data["uuid"]
        self.name = data["name"]
        self.created_at = data["created_at"]
        self.last_modified = data["last_modified"]
        self._columns = QueryColumns(data["columns"])
        self._metadata_columns = QueryColumns(data["metadata_columns"])
        self.metadata_filter = data["metadata_filter"]
        self.label_column = data.get("label_column", "")
        self.segmenter = data.get("segmenter_id", None)
        self.combine_labels = data.get("combine_labels", None)
        self.capture_configurations = data.get("capture_configurations", "")
        self.cache = data.get("cache", None)
        self.task_status = data.get("task_status", None)
        self.summary_statistics = data.get("summary_statistics")

        self._dirty = False

    def post_feature_statistics(self, window_size: int = None):
        """Returns metadata statistics for the query."""
        data = {"window_size": window_size}
        url = f"project/{self._project.uuid}/query/{self._uuid}/featurestatistics/"
        response = self._connection.request("post", url, data)

        response_data, err = utility.check_server_response(response)

        if err is False:
            return response_data

        return response

    def get_feature_statistics(self):
        """Returns metadata statistics for the query."""
        url = f"project/{self._project.uuid}/query/{self._uuid}/featurestatistics/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)

        if err is False:
            return response_data

        return response

    def __str__(self):
        return (
            "NAME: {0}\n"
            "COLUMNS: {1}\n"
            "METADATA_COLUMNS: {2}\n"
            "METADATA FILTER: {3}\n"
            "SEGMENTER ID: {4}\n"
            "LABEL COLUMN {5}\n"
            "COMBINE LABELS {6}\n"
            "CAPTURE CONFIGURATIONS {7}"
        ).format(
            self.name,
            self.columns,
            self.metadata_columns,
            self.metadata_filter,
            self.segmenter,
            self.label_column,
            self.combine_labels,
            self.capture_configurations,
        )

    def _to_dict(self):
        return {
            "name": self.name,
            "sensor_columns": self.columns._columns,
            "metadata_columns": self.metadata_columns._columns,
            "metadata_filter": self.metadata_filter,
            "segmenter_id": self.segmenter,
            "label_column": self.label_column,
            "capture_configurations": self.capture_configurations,
        }
