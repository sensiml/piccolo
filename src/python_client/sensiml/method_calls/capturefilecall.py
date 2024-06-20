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


class CaptureFileCall(PipelineStep):
    """The base class for a featurefile call"""

    def __init__(self, name):
        super(CaptureFileCall, self).__init__(name=name, step_type="CaptureFileCall")
        self.name = name
        self._data_columns = None
        self._group_columns = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, list):
            name = [name]
        self._name = name

    @property
    def data_columns(self):
        return self._data_columns

    @data_columns.setter
    def data_columns(self, value):
        self._data_columns = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs

    @property
    def group_columns(self):
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        print(
            "Capture files do not have group columns, use a data file if you need group columns."
        )

    def _to_dict(self):
        capturefile_dict = {}
        capturefile_dict["name"] = self.name
        capturefile_dict["type"] = "capturefile"
        capturefile_dict["data_columns"] = getattr(self, "_data_columns")
        capturefile_dict["group_columns"] = getattr(self, "_group_columns")
        capturefile_dict["outputs"] = getattr(self, "_outputs")
        return capturefile_dict
