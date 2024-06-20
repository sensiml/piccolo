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

class BaseMethodCall(object):
    """The base class for calls to functions.
    Child classes have their own additional properties and overwrite this docstring.
    """

    def __init__(self, name="", function_type=""):
        self._name = name
        self._type = function_type

    def _public_properties(self):
        """Returns the object's public properties, i.e. those that do not start with _"""
        return (name for name in dir(self) if not name.startswith("_"))

    def _to_dict(self):
        prop_dict = {}
        prop_dict["inputs"] = {}
        for prop in self._public_properties():
            if getattr(self, prop) is not None:
                prop_dict["inputs"][prop] = getattr(self, prop)
        prop_dict["name"] = self._name
        return prop_dict
