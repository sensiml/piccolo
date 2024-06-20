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


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sensiml.connection import Connection


class Function(object):
    """Base class for a transform object"""

    _uuid = ""
    _type = None
    _name = None
    _function_in_file = ""
    _description = ""
    _input_contract = ""
    _subtype = ""
    _has_c_version = False
    _library_pack = ""
    _automl_available = False

    def __init__(self, connection: Connection):
        self._connection = connection

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def type(self) -> str:
        return self._type

    @property
    def has_c_version(self) -> bool:
        return self._has_c_version

    @has_c_version.setter
    def has_c_version(self, value: bool):
        self._has_c_version = value

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def input_contract(self) -> list:
        return self._input_contract

    @input_contract.setter
    def input_contract(self, value: list):
        self._input_contract = value

    @property
    def subtype(self) -> str:
        return self._subtype

    @subtype.setter
    def subtype(self, value: str):
        self._subtype = value

    @property
    def library_pack(self) -> str:
        return self._library_pack

    @library_pack.setter
    def library_pack(self, value: str):
        self._library_pack = value

    @property
    def automl_available(self) -> bool:
        return self._automl_available

    @automl_available.setter
    def automl_available(self, value: bool):
        self._automl_available = value

    def get_function_info(self) -> dict:
        """Returns function properties after checking integrity constraints.

        Returns:
            (dict): containing the function's name, type, subtype, and has_c_version

        Raises:
            error if function does not have a name
            error if function does not have a type
        """
        # Sanity Checks
        try:
            assert self.name is not None
        except Exception as e:
            print("Function name cannot be None")
            raise (e)

        try:
            assert self.type is not None
        except Exception as e:
            print(
                "Function type cannot be None, please set to the correct type (ie. Transform, Optimizer, etc.)"
            )
            raise (e)

        function_info = {
            "name": self.name,
            "type": self.type,
            "subtype": self.subtype,
            "has_c_version": self.has_c_version,
            "library_pack": self.library_pack,
            "automl_available": self.automl_available,
        }

        return function_info

    def refresh(self):
        """Calls the REST API and populates the local object properties from the server."""
        url = f"transform/{self.uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.name = response_data["name"]
            self.type = response_data["type"]
            self.subtype = response_data["subtype"]
            self.description = response_data["description"]
            self.input_contract = response_data["input_contract"]
            self.has_c_version = response_data["has_c_version"]
            self.library_pack = response_data["library_pack"]
            self.automl_available = response_data["automl_available"]

        return response_data

    def data(self):
        """Calls the REST API and request a transform file's binary data."""
        url = f"transform/{self.uuid}/data/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response_data

    def initialize_from_dict(self, input_dictionary: dict):
        """Populates a single transform object from a dictionary of properties from the server.

        Args:
            input_dictionary (dict): containing uuid, type, subtype, name, function_in_file, description,
            input_contract, and subtype
        """
        self.uuid = input_dictionary["uuid"]
        self.type = input_dictionary["type"]
        self.subtype = input_dictionary["subtype"]
        self.name = input_dictionary["name"]
        self.description = input_dictionary["description"]
        self.input_contract = input_dictionary["input_contract"]
        self.subtype = input_dictionary["subtype"]
        self.has_c_version = input_dictionary["has_c_version"]
        self.library_pack = input_dictionary["library_pack"]
        self.automl_available = input_dictionary["automl_available"]

    def __str__(self):
        input_string = ""
        for input_ in [
            i
            for i in self.input_contract
            if i["name"]
            not in [
                "classifiers",
                "validation_methods",
                "number_of_times",
                "sample_size",
            ]
        ]:
            if "element_type" in input_:
                input_string += "\n    {name} ({type} of {element_type})".format(
                    **input_
                )
            else:
                input_string += "\n    {name} ({type})".format(**input_)
            if "options" in input_:
                options_string = ""
                for option in input_["options"]:
                    options_string += "{name}, ".format(**option)
                input_string += f" {{options: {options_string[:-2]}}}"
            if "description" in input_:
                input_string += ": {description}".format(**input_)

        return (
            "NAME: {0}\n"
            "TYPE: {1}\n"
            "SUBTYPE: {2}\n"
            "DESCRIPTION: {3}\n"
            "LIBRARY PACK {4}\n"
        ).format(
            self.name, self.type, self.subtype, self.description, self.library_pack
        )
