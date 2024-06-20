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


class FeatureFileCall(PipelineStep):
    """The base class for a featurefile call"""

    def __init__(self, name):
        super(FeatureFileCall, self).__init__(name=name, step_type="FeatureFileCall")
        self._featurefile = None
        self._feature_columns = None
        self._group_columns = None
        self._label_column = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def feature_columns(self):
        return self._feature_columns

    @feature_columns.setter
    def feature_columns(self, value):
        self._feature_columns = value

    @property
    def group_columns(self):
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        if isinstance(value, list):
            self._group_columns = value
        else:
            print("Group columns must be a list of strings.")

    @property
    def label_column(self):
        return self._label_column

    @label_column.setter
    def label_column(self, value):
        if isinstance(value, str):
            self._label_column = value
        else:
            print("Label Column must be a string")

    @property
    def featurefile(self):
        return self._featurefile

    @featurefile.setter
    def featurefile(self, featurefile):
        self._featurefile = featurefile

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs

    def _to_dict(self):
        featurefile_dict = {}
        featurefile_dict["name"] = self.name
        featurefile_dict["type"] = "featurefile"
        featurefile_dict["feature_columns"] = self.feature_columns
        featurefile_dict["group_columns"] = self.group_columns
        featurefile_dict["label_column"] = self.label_column
        featurefile_dict["outputs"] = self.outputs
        return featurefile_dict
