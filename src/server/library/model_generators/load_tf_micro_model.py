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

from library.model_generators.model_generator import ModelGenerator
from library.model_generators.neural_network_training_utils import decode_tflite


class EmtpyeModelParameters(Exception):
    pass


class LoadTensorFlowMicroModel(ModelGenerator):
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
        super(LoadTensorFlowMicroModel, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )
        self.model_parameters = config.get("model_parameters", None)

        self.model_parameters["estimator_type"] = config.get("estimator_type")
        self.model_parameters["threshold"] = config.get("threshold", 0.0)

        if self.model_parameters is None:
            raise EmtpyeModelParameters("No Model Parameters Provided.")

    def _train(self, train_data, validate_data=None, test_data=None):
        return self._package_model_parameters(self.model_parameters), None

    def _package_model_parameters(self, model_parameters):

        model_profile = self._classifier.get_model_profile(
            decode_tflite(model_parameters)
        )
        model_parameters["tensor_arena_size"] = (
            self._classifier.compute_tensor_arena_size(model_profile)
        )
        model_parameters["size"] = model_profile["summary"]["tflite_size"]
        model_parameters.update(
            self._classifier.get_input_output_details(model_parameters)
        )

        return model_parameters
