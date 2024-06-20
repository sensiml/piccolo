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

from sensiml.datamanager.pipeline import PipelineStep


class GeneratorCallSet(PipelineStep):
    """The base class for a collection of generator calls"""

    def __init__(self, name=""):
        super(GeneratorCallSet, self).__init__(name=name, step_type="GeneratorCallSet")
        self._input_data = ""
        self._generator_calls = []
        self._group_columns = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, value):
        self._input_data = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def generator_calls(self):
        return self._generator_calls

    def add_generator_call(self, *generator_call):
        """Adds one or more generator calls to the collection.

        Args:
            generator_call (GeneratorCall or list[GeneratorCall]): object(s) to append
        """
        for g in generator_call:
            self._generator_calls.append(g)

    def remove_generator_call(self, *generator_calls):
        """Removes a generator call from the collection.

        Args:
            generator_calls (GeneratorCall): object to remove
        """
        for generator_call in generator_calls:
            self._generator_calls = [
                f for f in self._generator_calls if f != generator_call
            ]
        # Note:  We should probably re-populate inputs and outputs here

    @property
    def group_columns(self):
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        self._group_columns = value

    def _to_list(self):
        gencalls = []
        for item in self._generator_calls:
            gencalls.append(item._to_dict())
        return gencalls

    def _to_dict(self):
        gencalls_set = []
        set_dict = {}
        for item in self._generator_calls:
            gencalls_set.append(item._to_dict())
        set_dict["name"] = self._name
        set_dict["type"] = "generatorset"
        set_dict["set"] = gencalls_set
        set_dict["inputs"] = {}
        set_dict["inputs"]["group_columns"] = self._group_columns
        set_dict["inputs"]["input_data"] = self._input_data
        set_dict["outputs"] = self._outputs
        return set_dict
