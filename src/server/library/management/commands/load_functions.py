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

import importlib
import json
import os
import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.commands import loaddata
from library.models import FunctionCost, ParameterInventory, Transform
from pandas import isnull


class FunctionLoadException(Exception):
    pass


class NoDocstringException(Exception):
    pass


class DocStringParseException(Exception):
    pass


class Command(BaseCommand):
    help = "Loads all functions or just the function of the given name [--function]."

    def add_arguments(self, parser):
        parser.add_argument("load_cost", nargs="?", type=bool, default=True)
        parser.add_argument("--load_dev", nargs="?", type=bool, default=False)

    def handle(self, *args, **options):
        dir_ = os.path.dirname(os.path.realpath(__file__))

        call_command(
            loaddata.Command(), "{0}/../../fixtures/functions_prod.yml".format(dir_)
        )

        if options.get("load_dev", False):
            call_command(
                loaddata.Command(), "{0}/../../fixtures/functions_dev.yml".format(dir_)
            )

        ParameterInventory.objects.all().delete()
        call_command(
            loaddata.Command(),
            "{0}/../../fixtures/parameter_inventory.yml".format(dir_),
        )

        for function_data in Transform.objects.filter(custom=False):
            try:
                self.update_function(function_data)
            except Exception as e:
                print("ERROR LOADING FUNCTION", function_data.name)
                print(e)
                function_data.delete()

        # Report out any core functions needing cost data that don't have it
        costs = [c.c_function_name for c in FunctionCost.objects.all()]
        functions = Transform.objects.filter(has_c_version=True)
        for function in functions:
            if function.c_function_name not in costs:
                print(
                    "\nWARNING: {} needs an entry in function_costs.yml!".format(
                        function.c_function_name
                    )
                )

    @staticmethod
    def update_function(function):
        print("Loading Contracts for {0}...".format(function.name))

        defaults = {
            "core": True,
            "has_c_version": False,
            "c_file_name": "",
            "dcl_executable": False,
            "uuid": None,
        }
        defaults.update(function.__dict__)

        module = function.path.replace("/", ".")[:-3]
        path = "{0}/../../".format(os.path.dirname(os.path.realpath(__file__)))
        sys.path.append(path)

        try:
            contracts = getattr(
                importlib.import_module(module),
                defaults["function_in_file"] + "_contracts",
            )
            contracts["description"] = getattr(
                importlib.import_module(module),
                defaults["function_in_file"],
            ).__doc__
            contracts.pop("costs", [])
        except AttributeError as e:
            raise Exception("Convert input contract for ", function.name)
            print("{}; looking for contracts in docstring...".format(e))

        if not contracts["description"]:
            raise NoDocstringException(
                "{0} needs a docstring with a description".format(function.name)
            )

        if (
            function.has_c_version
            and function.type != "Segmenter"
            and function.subtype != "Feature Vector"
        ):
            c_param_index = 0
            for param in contracts["input_contract"]:
                if param["name"] in [
                    "group_columns",
                    "columns",
                    "input_data",
                    "input_columns",
                    "label_column",
                    "input_column",
                ]:
                    continue

                if param.get("c_param", None) is None:
                    print("No c_param for this function", param, function.name)
                    continue
                if param.get("c_param") != c_param_index:
                    print(c_param_index, param, function.name, function.path)
                    raise Exception("Invalid c_param index")
                if (
                    param.get("range", None) is None
                    and param.get("options", None) is None
                ):
                    print(param, function.name, function.path)
                    raise Exception("Invalid Range")

                c_param_index += 1

        for contract in ["input_contract", "output_contract", "c_contract"]:
            # Test that there is a valid contract accompanying the loaded function
            if contracts.get(contract, None):
                json.loads(
                    json.dumps(contracts[contract])
                    if isinstance(contracts[contract], list)
                    or isinstance(contracts[contract], dict)
                    else contracts[contract]
                )

        defaults.update(contracts)

        for k, v in defaults.items():
            if isinstance(v, str):
                try:
                    v = json.loads(v)
                except ValueError:
                    pass
            if isinstance(v, float) and isnull(v):
                v = None
            setattr(function, k, v)

        function.save()
