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


# AugmentationCallSet
class AugmentationCallSet(PipelineStep):
    """The base class for a collection of augmentation calls"""

    def __init__(self, name=""):
        super(AugmentationCallSet, self).__init__(
            name=name, step_type="AugmentationCallSet"
        )
        self._augmentations = []
        self._input_data = ""
        self._label_column = None
        self._passthrough_columns = None
        self._group_columns = None
        self._percent = 0.1

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

    def add_augmentation_call(self, *augmentations):
        """Adds one or more augmentation calls to the collection.

        Args:
            augmentation (AugmentationCall or list[AugmentationCall]): object(s) to append
        """
        for augmentation in augmentations:
            self._augmentations.append(augmentation)

    def remove_augmentation_call(self, *augmentations):
        """Removes one or more augmentation call from the collection.

        Args:
            augmentations (AugmentationCall or list[AugmentationCall]): object(s) to remove
        """
        for augmentation in augmentations:
            self._augmentations = [f for f in self._augmentations if f != augmentation]

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
    def group_columns(self):
        return self._passthrough_columns

    @group_columns.setter
    def group_columns(self, value):
        self._group_columns = value

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, value):
        self._percent = value

    def _to_list(self):
        gencalls = []
        for item in self._augmentations:
            gencalls.append(item._to_dict())
        return gencalls

    def _to_dict(self):
        selcalls_set = []
        set_dict = {}

        for item in self._augmentations:
            selcalls_set.append(item._to_dict())

        set_dict["type"] = "augmentationset"
        set_dict["name"] = getattr(self, "_name")
        set_dict["set"] = selcalls_set
        set_dict["inputs"] = {}

        set_dict["inputs"]["passthrough_columns"] = getattr(
            self, "_passthrough_columns"
        )
        set_dict["inputs"]["label_column"] = getattr(self, "_label_column")

        set_dict["inputs"]["group_columns"] = getattr(self, "_group_columns")

        set_dict["inputs"]["input_data"] = getattr(self, "_input_data")
        set_dict["label_column"] = getattr(self, "_label_column")

        set_dict["outputs"] = self._outputs

        return set_dict
