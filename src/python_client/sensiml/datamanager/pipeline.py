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

from warnings import warn
from pandas import DataFrame


class PipelineWarning(Warning):
    """Base class for a pipeline warning"""


class PipelineError(Exception):
    """Base class for a pipeline error"""


class PipelineStep(object):
    """Base class for a pipeline step"""

    def __init__(self, name: str, step_type: str = "default"):
        self._inputs = []
        self._outputs = []
        self._name = name
        self._step_type = step_type
        self._feature_table = None

    @property
    def feature_table(self) -> DataFrame:
        return self._feature_table

    @feature_table.setter
    def feature_table(self, value: DataFrame):
        self._feature_table = value

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def step_type(self) -> str:
        return self._step_type

    def _check_inputs(self, output_vars: tuple = ()) -> list:
        """Compares the list of inputs with the given output_vars list.

        Args:
            output_vars (list[str]): strings representing the current set of output variables

        Returns:
            (list): unmatched inputs, or an empty list if all inputs are matched
        """
        unmatched_inputs = []
        for input in self.inputs:
            if not input in output_vars:
                unmatched_inputs.append(input)
        return unmatched_inputs

    def _check_outputs(self, output_vars: tuple = (), is_last: bool = False) -> list:
        """Compares the outputs from the item with the other output_vars from the pipeline.

        Args:
            output_vars (list[str]): strings representing the current set of output variables
            is_last (bool): True if item is the last step, otherwise False (default)

        Returns:
            (list): duplicate outputs, or an empty list if all outputs are unique

        Raises:
            PipelineError if step is not the last one and does not have any outputs
            PipelineWarning if step is the last one and does not have any outputs
        """
        duplicate_outputs = []
        if self.outputs:
            for output in self.outputs:
                if output in output_vars:
                    duplicate_outputs.append(output)
        elif is_last:
            warn(
                f"{self._step_type} {self._name} does not have any outputs.",
                PipelineWarning,
            )
        else:  # is_last = False
            raise PipelineError(
                f"{self._step_type} {self._name} does not have any outputs."
            )
        return duplicate_outputs
