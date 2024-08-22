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

import copy

from rest_framework import status


class ContractEnforcer(object):
    """
    input contract parameters (validation parameters and descriptions of input to a function)

    ** - required for all types
    * - required for some types

    **name: the name that will be used for the form shown for this parameter
    **type: the expected type for this parameter
        webui handle types:
            - [int][int16_t][numeric][float]: Number
            - [str]: String
            - [list]: List
            - [dict]: Dictionary

    *element_type: used for [list] or [dict], this is the expected type inside as values
        webui handle types:
            - [int][int16_t][numeric][float]: Number
            - [str]: String
            - [list][list_str]: only for [dict] List of strings

    min_elements: a limit of minimum count of elements for a list
        - used for an editable list where a user can add custom elements
    max_elements: a limit of maximum count of elements for a list
        - used for an editable list where a user can add custom elements

    lookup_field: an instruction about what options will be extracted from a query
        - used for dynamic parameters that depend on a query (group_columns, etc.)
        - overwrites options provided by this parameter
        webui handle values:
            query_columns - columns at query
            query_metadata_columns - metadata columns at query
            query_label_column - label_column at query
            query_combine_labels - combine_labels at query
            label_values - label_values at labels
            metadata_names - list of names from metadata array
            metadata_label_values - list of values from metadata object

    options: the options that are available for this, these are a list of dictionaries with the same properties as the input contract
        - used for [list] type
        - if not provided list should be editable

    default: the default value for this parameter which will be set if nothing is passed by the user

    is_ignored: don't use this field for building pipeline
    is_hidden: hide from user, but use with default value

    range: the range of values that are acceptable
    description: the description will be shown in the documentation

    handle_by_set: This parameter will be set by the Parent function that this transform is part of
    no_display: do not display this to the user
    c_param: the index of the parameter for the c function
    display_name: the display name to be used in a GUI

    num_columns:
            -2: any amount of columns, they will be split up and the feature generator will be called on each column individually
            -1: any amount of columns, all will be used by the feature generator
            1,2..n: takes exactly n input columns
    """

    type_dict = {
        "int": "numeric",
        "float": "numeric",
        "double": "numeric",
        "long": "numeric",
        "text": "str",
        "str": "text",
        "numeric": ["int", "float", "double", "long"],
        "unicode": ["str", "text"],
        "boolean": ["bool"],
        "int16_t": ["int"],
    }

    def __init__(self, step, jsonContract, function_name):
        self._step = step
        self._contract = jsonContract
        self._function_name = function_name
        self._contract_types = []
        self._pipeline_types = []
        self.v = {}
        self._validated_step = None

        self.extract_contract()

    def extract_contract(self):
        for item in self._contract:
            self._contract_types.append(item)

    def get_arguments_dict(self):
        args = {}
        # Load temp variables
        for key, value in self._step["inputs"].items():
            args[key] = value

        return args

    def enforce(self):

        for key, value in self._step["inputs"].items():
            self._pipeline_types.append({key: value.__class__.__name__})

        pipeline_inputs = [list(p.keys())[0] for p in self._pipeline_types]

        expected_inputs = []

        for contract in self._contract_types:
            expected_inputs.append(contract["name"])

            if contract["name"] == "input_data":
                continue
            if contract["name"] not in pipeline_inputs:
                if contract.get("default", "DoesNotExist") == "DoesNotExist":
                    raise ContractError.create(
                        "wrong_number_inputs",
                        self._function_name,
                        self._contract_types,
                        self._pipeline_types,
                    )

            else:
                pipeline_contract = self.get_contract_by_name(
                    self._pipeline_types, contract["name"]
                )

                if not self.types_are_equal(
                    pipeline_contract,
                    contract["type"],
                    contract.get("default", "NoDefault"),
                ):
                    raise ContractError.create(
                        "type_mismatch",
                        self._function_name,
                        contract["type"],
                        pipeline_contract,
                        self._step["inputs"][contract["name"]],
                        contract["name"],
                    )

        self._validate_step(expected_inputs)

        return self.get_arguments_dict()

    def _validate_step(self, expected_inputs):
        self._validated_step = copy.deepcopy(self._step)

        for input in list(self._validated_step["inputs"].keys()):
            if input not in expected_inputs:
                self._validated_step["inputs"].pop(input)

    def get_contract_by_name(self, contracts, name, key="name"):
        for contract in contracts:
            contract_name = list(contract.keys())[0]
            if contract_name == name:
                return contract[contract_name]

        return None

    def types_are_equal(
        self, pipeline_type, contract_type, contract_default="NoDefault"
    ):
        """First, the trivial case: direct equality."""
        if pipeline_type == contract_type:
            return True

        if pipeline_type == "int" and contract_type == "float":
            return True

        """ Some classes allow default input of None as well as a specific type """
        if pipeline_type == "NoneType" and contract_default is None:
            return True

        """ If not trivial, then check for the complex types """
        if pipeline_type in ["numeric", "unicode", "boolean"]:
            v = self.type_dict[pipeline_type]
            for k in range(len(v)):
                if self.types_are_equal(v[k], contract_type):
                    return True
                else:
                    continue
            return False

        if contract_type in ["numeric", "unicode", "boolean", "int16_t"]:
            v = self.type_dict[contract_type]
            for k in range(len(v)):
                if self.types_are_equal(v[k], pipeline_type):
                    return True
                else:
                    continue
            return False

        return False

    def enforce_output(self, contract_length, output_length):
        """Simply checks for equality after transform execution."""
        if contract_length == output_length:
            return True
        else:
            raise ContractError.create(
                "wrong_number_outputs",
                self._function_name,
                contract_length,
                output_length,
            )


class ContractError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    @classmethod
    def create(
        cls,
        error_type,
        function_name,
        expected,
        received,
        input_name="",
        input_parameter="",
    ):
        if error_type == "type_mismatch":
            detail = '\n\nInvalid input for step "{0}", parameter "{3}"\nExpected type "{1}" and got "{2}".\nInvalid input "{3}" = "{4}"'.format(
                function_name, expected, received, input_parameter, input_name
            )
        elif error_type == "wrong_number_inputs":
            missing = [
                x["name"]
                for x in expected
                if x["name"] not in [list(r.keys())[0] for r in received]
            ]
            detail = "Expected {0} input(s) and got {1} while executing {2}. Missing: ".format(
                len(expected), len(received), function_name
            )
            detail += "%3s" * len(missing) % tuple(missing)
        elif error_type == "wrong_number_outputs":
            detail = "Expected {0} output(s) and got {1} while executing {2}".format(
                expected, received, function_name
            )
        else:
            detail = "Unknown contract error"
        return ContractError(detail)
