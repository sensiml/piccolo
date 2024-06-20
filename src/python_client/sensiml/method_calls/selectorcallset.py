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


class SelectorCallSet(PipelineStep):
    """The base class for a collection of selector calls"""

    def __init__(self, name=""):
        super(SelectorCallSet, self).__init__(name=name, step_type="SelectorCallSet")
        self._selectors = []
        self._input_data = ""
        self._label_column = None
        self._number_of_features = 10
        self._feature_table = ""
        self._cost_function = ""
        self._remove_columns = []
        self._passthrough_columns = None
        self._refinement = {}

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
    def label_column(self):
        return self._label_column

    @label_column.setter
    def label_column(self, value):
        self._label_column = value

    @property
    def number_of_features(self):
        return self._number_of_features

    @number_of_features.setter
    def number_of_features(self, value):
        self._number_of_features = value

    @property
    def feature_table(self):
        return self._feature_table

    @feature_table.setter
    def feature_table(self, value):
        self._feature_table = value

    @property
    def cost_function(self):
        return self._cost_function

    @cost_function.setter
    def cost_function(self, value):
        self._cost_function = value

    @property
    def refinement(self):
        return self._refinement

    @refinement.setter
    def refinement(self, value):
        self._refinement = value

    @property
    def selectors(self):
        return self._selectors

    def add_selector_call(self, *selectors):
        """Adds one or more selector calls to the collection.

        Args:
            selectors (SelectorCall or list[SelectorCall]): object(s) to append
        """
        for selector in selectors:
            self._selectors.append(selector)

    def remove_selector_call(self, *selectors):
        """Removes one or more selector call from the collection.

        Args:
            selectors (SelectorCall or list[SelectorCall]): object(s) to remove
        """
        for selector in selectors:
            self._selectors = [f for f in self._selectors if f != selector]
        # Note:  We should probably re-populate inputs and outputs here

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def passthrough_columns(self):
        return self._passthrough_columns

    @passthrough_columns.setter
    def passthrough_columns(self, value):
        self._passthrough_columns = value

    @property
    def remove_columns(self):
        return self._remove_columns

    @remove_columns.setter
    def remove_columns(self, value):
        self._remove_columns = value

    def _to_list(self):
        gencalls = []
        for item in self._selectors:
            gencalls.append(item._to_dict())
        return gencalls

    def _to_dict(self):
        selcalls_set = []
        set_dict = {}
        for item in self._selectors:
            selcalls_set.append(item._to_dict())
        set_dict["type"] = "selectorset"
        set_dict["name"] = getattr(self, "_name")
        set_dict["set"] = selcalls_set
        set_dict["inputs"] = {}
        set_dict["inputs"]["remove_columns"] = getattr(self, "_remove_columns")
        set_dict["inputs"]["passthrough_columns"] = getattr(
            self, "_passthrough_columns"
        )
        set_dict["inputs"]["input_data"] = getattr(self, "_input_data")
        set_dict["inputs"]["label_column"] = getattr(self, "_label_column")
        set_dict["inputs"]["number_of_features"] = getattr(self, "_number_of_features")
        set_dict["inputs"]["feature_table"] = getattr(self, "_feature_table")
        if self._cost_function == "":
            self._cost_function = "sum"
        set_dict["inputs"]["cost_function"] = getattr(self, "_cost_function")
        set_dict["outputs"] = self._outputs
        set_dict["refinement"] = getattr(self, "_refinement")
        return set_dict
