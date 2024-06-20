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


class TrainAndValidationCall(PipelineStep):
    """The base class for a train-and-validation call."""

    def __init__(self, name=""):
        super(TrainAndValidationCall, self).__init__(
            name=name, step_type="TrainAndValidationCall"
        )
        self._validation_methods = []
        self._classifiers = []
        self._optimizers = []
        self._input_data = ""
        self._feature_table = ""
        self._label_column = None
        self._ignore_columns = None
        self._outputs = []
        self._validation_seed = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def validation_methods(self):
        return self._validation_methods

    @validation_methods.setter
    def validation_methods(self, value):
        self._validation_methods = value

    @property
    def classifiers(self):
        return self._classifiers

    @classifiers.setter
    def classifiers(self, value):
        self._classfiers = value

    @property
    def optimizers(self):
        return self._optimizers

    @optimizers.setter
    def optimizers(self, value):
        self._optimizers = value

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, value):
        self._input_data = value

    @property
    def feature_table(self):
        return self._feature_table

    @feature_table.setter
    def feature_table(self, value):
        self._feature_table = value

    @property
    def label_column(self):
        return self._label_column

    @label_column.setter
    def label_column(self, value):
        self._label_column = value

    @property
    def ignore_columns(self):
        return self._ignore_columns

    @ignore_columns.setter
    def ignore_columns(self, value):
        self._ignore_columns = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def validation_seed(self):
        return self._validation_seed

    @validation_seed.setter
    def validation_seed(self, value):
        self._validation_seed = value

    def add_validation_method(self, validation_method_call):
        """Adds a validation method call to the train-and-validation call.

        Args:
            validation_method_call (ValidationMethodCall): object to append
        """
        self._validation_methods.append(validation_method_call)

    def remove_validation_method(self, validation_method_call):
        """Removes a validation method call from the train-and-validation call.

        Args:
            validation_method_call (ValidationMethodCall): object to remove
        """
        self._validation_methods = [
            f for f in self._validation_methods if f != validation_method_call
        ]

    def add_classifier(self, classifier_call):
        """Adds a classifier call to the train-and-validation call.

        Args:
            classifier_call (ClassifierCall): object to append
        """
        self._classifiers.append(classifier_call)

    def remove_classifier(self, classifier_call):
        """Removes a classifier call from the train-and-validation call.

        Args:
            classifier_call (ClassifierCall): object to remove
        """
        self._classifiers = [f for f in self._classifiers if f != classifier_call]

    def add_optimizer(self, optimizer_call):
        """Adds an optimizer call to the train-and-validation call.

        Args:
            optimizer_call (OptimizerCall): object to append
        """
        self._optimizers.append(optimizer_call)

    def remove_optimizer(self, optimizer_call):
        """Removes an optimizer call from the train-and-validation call.

        Args:
            optimizer_call (OptimizerCall): object to remove
        """
        self._optimizers = [f for f in self._optimizers if f != optimizer_call]

    def _to_dict(self):
        d = {}
        d["name"] = self.name
        d["type"] = "tvo"
        d["input_data"] = self.input_data
        d["feature_table"] = self.feature_table
        d["label_column"] = self.label_column
        d["ignore_columns"] = self.ignore_columns
        d["outputs"] = self._outputs
        d["validation_seed"] = self._validation_seed

        d["optimizers"] = []
        for item in self._optimizers:
            d["optimizers"].append(item._to_dict())

        d["classifiers"] = []
        for item in self._classifiers:
            d["classifiers"].append(item._to_dict())

        d["validation_methods"] = []
        for item in self._validation_methods:
            d["validation_methods"].append(item._to_dict())

        return d
