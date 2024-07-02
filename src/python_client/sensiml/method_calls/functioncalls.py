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


class FunctionCalls(object):
    """Collection of function calls"""

    def __init__(self):
        self._name = ""
        self._function_calls = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def function_calls(self):
        return self._function_calls

    def add_function_call(self, function_call):
        """Adds a function call to the collection.

        Args:
            function_call (FunctionCall): object to append
        """
        self._function_calls.append(function_call)

    def remove_function_call(self, function_call):
        """Removes a function call from the collection.

        Args:
            function_call (FunctionCall): object to remove
        """
        self._function_calls = [f for f in self._function_calls if f != function_call]

    def _to_list(self):
        fcalls = []
        for item in self.function_calls:
            fcalls.append(item._to_dict())
        return fcalls

        # fcalls['name'] = self.name
        # fcalls['type'] = 'transform'
        # query_dict['outputs'] = [self.outputs]
