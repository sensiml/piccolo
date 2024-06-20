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
from sensiml.datamanager.function import Function
from sensiml.method_calls import (
    AugmentationCall,
    AugmentationCallSet,
    CaptureFileCall,
    ClassifierCall,
    DataFileCall,
    FeatureFileCall,
    FunctionCall,
    GeneratorCall,
    GeneratorCallSet,
    OptimizerCall,
    QueryCall,
    SelectorCall,
    SelectorCallSet,
    TrainAndValidationCall,
    TrainingAlgorithmCall,
    ValidationMethodCall,
)
from six import string_types
from typing import TYPE_CHECKING, Tuple, Optional


if TYPE_CHECKING:
    from sensiml.connection import Connection


class FunctionExistsError(Exception):
    """Base class for a function exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Functions:
    """Base class for a collection of functions"""

    def __init__(self, connection: Connection):
        self._connection = connection
        self._function_list = {}
        self.build_function_list()

    @property
    def function_list(self) -> dict:
        if not self._function_list:
            self.build_function_list()

        return self._function_list

    @function_list.setter
    def function_list(self, value: dict):
        self._function_list = value

    def build_function_list(self):
        """Populates the function_list property from the server."""
        function_list = {}

        function_response = self.get_functions()
        for function in function_response:
            function_list[function.name] = function

        self._function_list = function_list

    def get_function_by_name(self, name: str) -> Function:
        """Gets a function from the server by name.

        Args:
            name (str): function name

        Returns:
            function
        """
        func = self.function_list.get(name, None)
        if func is None:
            raise Exception(f"No function named {name}")

        return func

    def _new_function_from_dict(self, init_dict: dict) -> Function:
        """Creates and populates a function from a set of properties.

        Args:
            dict (dict): contains properties of a function

        Returns:
            function
        """
        function = Function(self._connection)
        function.initialize_from_dict(init_dict)
        return function

    def get_functions(self, function_type: str = "") -> Function:
        """Gets all functions as function objects.

        Args:
            function_type (optional[str]): type of function to retrieve

        Returns:
            list of functions
        """
        url = "transform/"
        response = self._connection.request("get", url)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        functions = []
        for function_params in response_data:
            functions.append(self._new_function_from_dict(function_params))

        if function_type:
            functions = [f for f in functions if f.type == function_type]

        return functions

    def create_query_call(self, name: str = "Query") -> QueryCall:
        """Creates a query call.

        Returns:
            QueryCall
        """
        qy = QueryCall(name)
        return qy

    def create_featurefile_call(self, name: str) -> FeatureFileCall:
        """Creates a featurefile call.

        Args:
            name: name of the featurefile

        Returns:
            FeatureFileCall
        """
        return FeatureFileCall(name)

    def create_datafile_call(self, name: str) -> DataFileCall:
        """Creates a datafile call.

        Args:
            name: name of the datafile

        Returns:
            FeatureFileCall
        """
        return DataFileCall(name)

    def create_capturefile_call(self, name: str) -> CaptureFileCall:
        """Creates a capturefile call.

        Args:
            name: name of the featurefile

        Returns:
            FeatureFileCall
        """
        return CaptureFileCall(name)

    def create_train_and_validation_call(
        self, name: str = "TVO"
    ) -> TrainAndValidationCall:
        """Creates an empty train and validation call.

        Returns:
            TrainAndValidationCall
        """
        tvo = TrainAndValidationCall()
        tvo.name = name
        return tvo

    def get_functions_by_type(
        self, function_type: str = "", subtype: str = ""
    ) -> Function:
        """Gets all functions or functions of a particular function ype or all functions
        of a particular subtype as function objects.

        Args:
            subtype (optional[str]): subtype to retrieve

        Returns:
            list of functions
        """
        # Populate each function from the server

        if function_type:
            functions = [
                f for f in self.function_list.values() if f.type == function_type
            ]

        elif subtype:
            functions = [f for f in self.function_list.values() if f.subtype == subtype]

        else:
            functions = [f for f in self.function_list.values()]

        return functions

    def __str__(self, function_type: str = "") -> str:
        output_string = ""
        all_functions = self.get_functions_by_type(function_type=function_type)
        for s in set([f.type for f in all_functions]):
            output_string += f"{s}:\n"
            for t in [
                tr
                for tr in all_functions
                if tr.type == s
                and (
                    tr.has_c_version
                    or tr.type not in ["Transform", "Segmenter", "Feature Generator"]
                )
            ]:
                if t.subtype:
                    output_string += f"    {t.name} ({t.subtype})\n"
                else:
                    output_string += f"    {t.name}\n"
            output_string += "\n"

        return output_string

    def __call__(self, function_type):
        return self.__str__(function_type)

    def __getitem__(self, key: str) -> Function:
        return self.get_function_by_name(key).__str__()

    def _initialize_docstring(self, function: Function) -> Tuple[dict, dict, str]:
        ic_dict = function.input_contract
        # oc_dict = function.output_contract
        inputs = {
            i["name"]: None for i in ic_dict if not i.get("handle_by_set", False)
        }  # Parse arguments from the input contract

        # Construct a user-friendly docstring using the description and input/output contracts
        docstring = function.description
        docstring += "\n \nInputs\n---------- \n"

        for i in ic_dict:
            if i.get("default", None):
                docstring += f"  {i['name']}: {i['type']} - (default: {i['default']})\n"
            else:
                docstring += f"  {i['name']}: {i['type']} \n"

        # docstring += '\nOutputs\n---------- \n'
        # for i in oc_dict:
        #     docstring += '  {0} \n'.format(i['type'])

        docstring += "\nUsage\n---------- \n"
        docstring += "For DataFrame inputs, provide a string reference to the\nDataFrame output of a previous step in the pipeline.\n"
        docstring += "For Dataframe output, provide a string name that subsequent\noperations can refer to."

        return ic_dict, inputs, docstring

    def _warn_if_not_transcoded(self, function: Function):
        if (
            function.type in ("Transform", "Segmenter", "Feature Generator")
            and not function.has_c_version
        ):
            print(
                "Warning: {0} is not supported by KnowledgePack code generation. \n"
                "It can be used for cloud-based modeling but cannot be downloaded or flashed to a device. \n".format(
                    function.name
                )
            )

    def create_function_call(self, function: Function, name: Optional[str] = None):
        """Creates a function call object.

        Args:
            function (Function object or str): the function for which to create a call object or its
            string name

        Returns:
            function call object or None if the function is not found

        Raises:
            error if no call object can be initialized for the function type
        """
        if name:
            print(
                "The use of the second input parameter is no longer necessary and will be deprecated."
            )

        if isinstance(function, string_types):

            function = self.function_list.get(function, None)

            if function is None:
                print("No function found")
                return None

        self._warn_if_not_transcoded(function)

        try:
            return getattr(
                self, f"create_{function.type.lower().replace(' ', '_')}_call"
            )(function)

        except Exception as e:
            print(
                f'No function call for function type "{function.type.lower()}" found.'
            )

            raise (e)

    def _create_base_call(
        self, function: Function, CallFunction, ignore_columns: Optional[list] = None
    ):
        """Creates a base subclass on the fly for the specified function.

        Parses the passed function's I/O contracts and builds class properties accordingly. Returns an instance of the
        new class.
        """

        if ignore_columns is None:
            ignore_columns = []

        if isinstance(function, string_types):
            function = self.function_list[function]

        self._warn_if_not_transcoded(function)
        ic_dict, inputs, docstring = self._initialize_docstring(function)

        for column in ignore_columns:
            inputs.pop(column, None)

        for contract in ic_dict:
            if "default" in contract.keys():
                inputs[contract["name"]] = contract["default"]

        # Add docstring to inputs structure and create the new class
        inputs["__doc__"] = docstring
        fname = str(function.name)

        Call = type(fname, (CallFunction,), inputs)

        return Call(function.name, function_type=function.type.lower())

    def create_transform_call(self, function: Function, name: Optional[str] = None):
        """Creates a FunctionCall for the specified transform.

        Parses the passed function's I/O contracts and builds class properties accordingly. Returns an instance of the
        new class.

            Args:
                function (Function): function with which to create a transform call

            Returns:
                instance of FunctionCall customized for the input function
        """

        ic_dict, inputs, docstring = self._initialize_docstring(function)

        # Add docstring to inputs structure and create the new class
        inputs["__doc__"] = docstring
        fname = str("kb_" + function.name.lower().replace(" ", "_"))

        for contract in ic_dict:
            if "default" in contract.keys():
                inputs[contract["name"]] = contract["default"]

        Call = type(
            fname, (FunctionCall,), dict({"_input_contract": ic_dict}, **inputs)
        )
        return Call(name=function.name, function_type=function.type.lower())

    def create_segmenter_call(self, function: Function, name: Optional[str] = None):

        return self.create_transform_call(function, name=name)

    def create_sampler_call(self, function: Function, name: Optional[str] = None):

        return self.create_transform_call(function, name=name)

    def create_feature_generator_call(self, function: Function):
        """Creates a GeneratorCall for the specified generator.

        Args:
            function (Function): function with which to create a feature generator call

        Returns:
            instance of GeneratorCall customized for the input function
        """
        ignore_columns = ["group_columns", "input_data"]

        return self._create_base_call(
            function, GeneratorCall, ignore_columns=ignore_columns
        )

    def create_augmentation_call(self, function: Function):
        """
        Creates a AugmentationCall for the specified time series augmentation.

        Args:
            function (Function): function with which to create a augmentation call

        Returns:
            instance of AugmentationCall customized for the input function

        """
        ignore_columns = [
            "ignore_columns",
            "input_data",
            "label_column",
            "num_features",
        ]

        return self._create_base_call(
            function, AugmentationCall, ignore_columns=ignore_columns
        )

    def create_feature_selector_call(self, function: Function):
        """Creates a SelectorCall for the specified selector.

        Args:
            function (Function): function with which to create a feature selector call

        Returns:
            instance of SelectorCall customized for the input function
        """
        ignore_columns = [
            "ignore_columns",
            "input_data",
            "label_column",
            "num_features",
        ]

        return self._create_base_call(
            function, SelectorCall, ignore_columns=ignore_columns
        )

    def create_validation_method_call(
        self, function: Function, name: Optional[str] = None
    ):
        """Creates a ValidationMethodCall for the specified function.

        Args:
            function (Function): function with which to create a validation method call

        Returns:
            instance of ValidationMethodCall customized for the input function
        """
        return self._create_base_call(function, ValidationMethodCall)

    def create_classifier_call(self, function: Function):
        """Creates a ClassifierCall for the specified function.

        Args:
            function (Function): function with which to create a classifier call

        Returns:
            instance of ClassifierCall customized for the input function
        """
        return self._create_base_call(function, ClassifierCall)

    def create_optimizer_call(self, function: Function, name: Optional[str] = None):
        """Creates an OptimizerCall for the specified function.

        Args:
            function (Function): function with which to create an optimizer call

        Returns:
            instance of OptimizerCall customized for the input function
        """
        return self._create_base_call(function, OptimizerCall)

    def create_generator_subtype_call(self, subtype: str):
        """Creates a GeneratorCall for the specified subtype of generators.

        Uses the input contract of one function of the subtype (assumed to be constant for all generators of the subtype),
        and builds class properties accordingly.

            Args:
                subtype (str): name of the subtype for which to create a generator call

            Returns:
                instance of GeneratorCall customized for the subtype
        """

        function_list = self.get_functions_by_type(subtype=subtype)
        if len(function_list) > 0:
            function = function_list[0]
            ic_dict, inputs, docstring = self._initialize_docstring(function)
        else:
            print(
                "Error: No generators of subtype {0}; length of function list {1}".format(
                    subtype, len(function_list)
                )
            )
            return None

        for function in function_list:
            self._warn_if_not_transcoded(function)

        ignore_columns = ["group_columns", "input_data"]

        for column in ignore_columns:
            inputs.pop(column, None)

        for contract in ic_dict:
            if "default" in contract.keys():
                inputs[contract["name"]] = contract["default"]

        # Add docstring to inputs structure and create the new class
        inputs["__doc__"] = docstring
        inputs["_subtype"] = subtype

        Call = type(subtype, (GeneratorCall,), inputs)
        return Call(function.name, "generator")

    def create_generator_call_set(self, name: str = "GeneratorCallSet"):
        """Creates an empty generator call set."""
        gcs = GeneratorCallSet(name)
        return gcs

    def create_selector_call_set(self, name: str = "SelectorCallSet"):
        """Creates an empty selector call set."""
        scs = SelectorCallSet(name)
        return scs

    def create_augmentation_call_set(self, name: str = "AugmentationCallSet"):
        """Creates an empty augmentation call set."""
        acs = AugmentationCallSet(name)
        return acs

    def create_training_algorithm_call(
        self, function: Function, name: Optional[str] = None
    ):
        """Creates a training algorithm method call for the specified function.

        Args:
            function (Function): function with which to create a training algorithm call

        Returns:
            instance of TrainingAlgorithmCall customized for the input function
        """
        return self._create_base_call(function, TrainingAlgorithmCall)
