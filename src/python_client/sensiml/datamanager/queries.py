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
from sensiml.datamanager.query import Query
import sensiml.base.utility as utility

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project


class QueryExistsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Queries(object):
    """Base class for a collection of queries."""

    def __init__(self, connection: Connection, project: Project):
        self._connection = connection
        self._project = project

    def build_query_list(self) -> dict:
        """Populates the function_list property from the server."""
        query_list = {}

        query_response = self.get_queries()
        for query in query_response:
            query_list[query.name] = query

        return query_list

    def create_query(
        self,
        name: str,
        columns: Optional[list[str]] = None,
        metadata_columns: Optional[list[str]] = None,
        metadata_filter: str = "",
        label_column: str = "",
    ) -> Query:
        """Creates a query with the given input properties and inserts it onto the server

        Args:
            name (str): name of the query
            columns (list[str]): sensor columns to select
            metadata_columns (list(str]): metadata columns to select
            metadata_filter (str): specifies one or more metadata filter conditions

        Returns:
            query object
        """
        if self.get_query_by_name(name) is not None:
            raise QueryExistsError(f"Query {name} already exists.")
        else:
            query = self.new_query()
            query.name = name
            query.columns = columns
            query.metadata_columns = metadata_columns
            query.eventlabel_columns = "NULL"
            query.metadata_filter = metadata_filter
            query.label_column = label_column
            query.insert()
            return query

    def get_or_create_query(self, name: str) -> Query:
        """Calls the REST API and gets the query by name, if it doesn't exist insert a new query

        Args:
            name (str): name of the query

        Returns:
            query object
        """
        query = self.get_query_by_name(name)

        if query is None:
            print(f"Query {name} does not exist, creating a new query.")
            query = self.new_query()
            query.name = name
            query.insert()

        return query

    def get_query_by_name(self, name: str, raise_exception: bool = False) -> Query:
        """Retrieves a query by name from the server, if it exists

        Args:
            name (str)

        Returns:
            query object or None
        """
        query_list = self.get_queries()
        for query in query_list:
            if query.name == name:
                return query

        if raise_exception:
            print(f"Query {name} does not exists")
            raise Exception(f"Query {name} does not exists")

        return None

    def get_query_by_uuid(self, uuid: str) -> Query:
        """Retrieves a query by name from the server, if it exists

        Args:
            name (str)

        Returns:
            query object or None
        """
        url = f"project/{self._project.uuid}/query/{uuid}"
        response = self._connection.request("get", url)

        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        return self._new_query_from_dict(response_data)

    def new_query(self) -> Query:
        """Initializes a new query for the project, but does not assign property values or insert it into the server"""
        query = Query(self._connection, self._project)
        return query

    def _new_query_from_dict(self, data: dict) -> Query:
        """Creates a query object using a dictionary (e.g. one retrieved from the server)

        Args:
            dict (dict): dictionary of query properties
                            - name
                            - columns
                            - metadata_columns
                            - metadata_filter

        Returns:
            query object
        """
        query = self.new_query()
        query.initialize_from_dict(data)
        return query

    def get_queries(self) -> list[Query]:
        """Gets all project queries from the server and creates corresponding local query objects

        Returns:
            list[query]
        """
        # Query the server and get the json
        url = f"project/{self._project.uuid}/query/"
        response = self._connection.request("get", url)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        # Populate each eventlabel from the server
        queries = []
        if err is False:
            try:
                for query_params in response_data:
                    queries.append(self._new_query_from_dict(query_params))
            except Exception as e:
                print(e)
        return queries

    def __str__(self) -> str:
        output_string = "Queries:\n"
        for q in self.get_queries():
            output_string += f"    {q.name}\n"

        return output_string

    def __getitem__(self, key: str) -> str:
        return self.get_query_by_name(key).__str__()
