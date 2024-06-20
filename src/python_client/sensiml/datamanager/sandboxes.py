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
from sensiml.datamanager.sandbox import Sandbox
import sensiml.base.utility as utility

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project


class SandboxExistsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Sandboxes:
    """Base class for a collection of sandboxes."""

    def __init__(self, connection: Connection, project: Project):
        self._connection = connection
        self._project = project

    def build_sandbox_list(self) -> dict:
        """Populates the function_list property from the server."""
        sandbox_list = {}

        sandbox_response = self.get_sandboxes()
        for sandbox in sandbox_response:
            sandbox_list[sandbox.name] = sandbox

        return sandbox_list

    def get_or_create_sandbox(self, name: str) -> Sandbox:
        """Calls the REST API and gets the sandbox by name, if it doesn't exist insert a new sandbox

        Args:
            name (str): name of the sandbox

        Returns:
            sandbox object
        """
        sandbox = self.get_sandbox_by_name(name)

        if sandbox is None:
            print(f"Sandbox {name} does not exist, creating a new sandbox.")
            sandbox = self.new_sandbox()
            sandbox.name = name
            sandbox.insert()

        return sandbox

    def create_sandbox(self, name: str, steps: list[dict]) -> Sandbox:
        """Creates a sandbox using the given name and steps

        Args:
            name (str): name of the sandbox
            steps (list[dict]): list of dictionaries specifying the pipeline steps

        Returns:
            sandbox object
        """
        if self.get_sandbox_by_name(name) is not None:
            raise SandboxExistsError(f"sandbox {name} already exists.")

        sandbox = self.new_sandbox()
        sandbox.name = name
        sandbox._steps = steps
        sandbox.insert()
        return sandbox

    def get_sandbox_by_name(self, name: str) -> Sandbox:
        """Calls the REST API and gets the sandbox by name

        Args:
            name (str): name of the sandbox

        Returns:
            sandbox object
        """
        sandbox_list = self.get_sandboxes()
        for sandbox in sandbox_list:
            if sandbox.name == name:
                return sandbox
        return None

    def new_sandbox(self, data: Optional[dict] = None) -> Sandbox:
        """Creates a new sandbox but does not insert in on the server

        Args:
            dict (optional[dict]): contains name and steps properties of the sandbox

        Returns:
            sandbox object
        """
        if data is None:
            data = list()
        sandbox = Sandbox(self._connection, self._project)
        if len(data) != 0:
            sandbox.initialize_from_dict(data)

        return sandbox

    def get_sandboxes(self) -> list[Sandbox]:
        """Gets all sandboxes from server and turns them into local sandbox objects.

        Returns:
            list[sandbox]
        """
        # Query the server and get the json
        url = f"project/{self._project.uuid}/sandbox/"
        response = self._connection.request("get", url)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        # Populate each sandbox from the server
        sandboxes = []
        if err is False:
            for sandbox_params in response_data:
                sandboxes.append(self.new_sandbox(sandbox_params))
        return sandboxes

    def __str__(self):
        output_string = "Sandboxes:\n"
        for s in self.get_sandboxes():
            output_string += f"    {s.name}\n"

        return output_string
