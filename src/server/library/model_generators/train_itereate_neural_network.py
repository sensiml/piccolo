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

from datamanager.models import KnowledgePack
from engine.base.model_store import load_model
from library.model_generators.neural_network_base import NeuralNetworkBase


class TrainIterateNeuralNetwork(NeuralNetworkBase):
    """Creates optimal order-agnostic training set and trains  with the resulting vector."""

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

        super(TrainIterateNeuralNetwork, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )

        self._params = {
            "estimator_type": config["estimator_type"],
            "learning_rate": config["learning_rate"],
            "threshold": config["threshold"],
            "batch_size": config["batch_size"],
            "loss_function": config["loss_function"],
            "tensorflow_optimizer": config["tensorflow_optimizer"],
            "label_column": config["label_column"],
            "metrics": config["metrics"],
            "base_model": config["base_model"],
            "epochs": config["epochs"],
        }

    def initialize_model(self, x_train, y_train):

        kp = KnowledgePack.objects.get(uuid=self._params["base_model"])
        team_id = kp.sandbox.project.team.uuid
        pipeline_id = kp.sandbox.uuid
        model_id = kp.neuron_array["model_store"]["model"]["model_id"]

        tf_model = load_model(team_id, pipeline_id, model_id)

        # TODO: assert inputs are the same as outputs

        weights = tf_model.get_weights()

        tf_model.compile(
            loss=self._params["loss_function"],
            optimizer=self._params["tensorflow_optimizer"],
            metrics=[self._params["metrics"]],
        )

        tf_model.optimizer.lr = self._params["learning_rate"]

        tf_model.set_weights(weights)

        return tf_model
