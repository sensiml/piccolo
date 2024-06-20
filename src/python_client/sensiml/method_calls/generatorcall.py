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

from sensiml.method_calls.basemethodcall import BaseMethodCall


class GeneratorCall(BaseMethodCall):
    """The base class for a generator call.

    Child classes have their own additional properties and overwrite this docstring."""

    def __init__(self, name, function_type="Feature Generator"):
        super(GeneratorCall, self).__init__(name=name, function_type=function_type)

    def _to_dict(self):
        prop_dict = {}
        if not hasattr(self, "_subtype"):
            prop_dict["function_name"] = self._name
        else:
            prop_dict["subtype"] = self._subtype

        prop_dict["inputs"] = {}
        for prop in self._public_properties():
            prop_dict["inputs"][prop] = getattr(self, prop)
        return prop_dict
