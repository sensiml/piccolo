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

from library.model_generators.pme_base import PMEBase


class NoNeuronArrayException(Exception):
    pass


class LoadPMEModel(PMEBase):
    """Loads a neuron array into PME and classifies feature vectors."""

    def __init__(
        self,
        config,
        classifier,
        validation_method,
        team_id,
        project_id,
        pipeline_id,
        save_model_parameters,
    ):
        """Initialize with defaults for missing values."""
        super(LoadPMEModel, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )
        self.neuron_array = config.get("neuron_array", None)
        if self.neuron_array is None:
            raise NoNeuronArrayException("No Neuron array was provided.")
        # There is an off-by-one problem if you use the exact number!
        self.max_neuron_count = len(self.neuron_array) + 1
        self.max_vector_size = len(self.neuron_array[0]["Vector"])
        self._classifier.load_model(self.neuron_array)

    def _train(self, train_data, validate_data=None, test_data=None):
        return self.neuron_array, None
