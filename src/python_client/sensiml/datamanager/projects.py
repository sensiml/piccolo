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
from sensiml.datamanager.project import Project
import sensiml.base.utility as utility


from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from sensiml.connection import Connection


class ProjectExistsError(Exception):
    """Base class for a project exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Projects:
    """Base class for a collection of projects."""

    def __init__(self, connection: Connection):
        self._connection = connection

    def create_project(self, name: str):
        """Creates a project using the name property.

        Args:
            name (str): name of the new project

        Returns:
            project

        Raises:
            ProjectExistsError, if the project already exists on the server
        """
        if self.get_project_by_name(name) is not None:
            raise ProjectExistsError(f"project {name} already exists.")
        else:
            project = self.new_project()
            project.name = name
            project.insert()
            return project

    def get_or_create_project(self, name: str):
        """Calls the REST API and gets the project by name, if it doesn't exist insert a new project

        Args:
            name (str): name of the project

        Returns:
            project object
        """
        project = self.get_project_by_name(name)

        if project is None:
            print(f"Project {name} does not exist, creating a new project.")
            project = self.create_project(name)

        return project

    def get_project_by_name(self, name: str):
        """gets a project from the server using its name property

        Args:
            name (str): name of the project

        Returns:
            project or None if project does not exist
        """
        project_list = self.get_projects()
        for project in project_list:
            if project.name == name:
                if project.schema and not project.query_optimized:
                    if len(project._captures.get_captures()):
                        project.query_optimize()
                return project

        return None

    def __getitem__(self, key) -> Project:
        return self.get_project_by_name(key)

    def new_project(self, data: Optional[dict] = None) -> Project:
        """Creates a new project.

        Args:
            dict (dict): dictionary containing the attributes of the new project

        Returns:
            project
        """

        if data is None:
            data = dict()

        project = Project(self._connection)

        if data:
            project.initialize_from_dict(data)

        return project

    def get_projects(self) -> list[Project]:
        """Gets all projects from the server as project objects.

        Returns:
            list[project]
        """
        url = "project/"
        response = self._connection.request("get", url)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        projects = []
        if err is False:
            # Populate each project from the server if there was no error.
            for project_params in response_data:
                projects.append(self.new_project(project_params))

        return projects

    def build_project_dict(self) -> dict:
        """Populates the function_list property from the server."""
        project_dict = {}

        response = self.get_projects()
        for project in response:
            project_dict[project.name] = project

        return project_dict
