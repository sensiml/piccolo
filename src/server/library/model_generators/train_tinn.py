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

from library.classifiers.tinn import Tinn
from library.model_generators.model_generator import ModelGenerator
from numpy import argmax, array


class TrainTinn(ModelGenerator):
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
        super(TrainTinn, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )

        self._reverse_class_map = config.get("reverse_map")

        self._params = {
            "iterations": config.get("iterations", 100),
            "num_hidden_layer": config.get("num_hidden_layer", 20),
            "learning_rate": config.get("learning_rate", 0.01),
        }

    def _package_model_parameters(self, models):
        """convert a list of dicision tree classifier to a json serializable form that can be
        saved and used to create a model for our tree_ensemble.c function"""

    def _test(self, data):
        """Package set of vectors for the simulator and recognize the tensors returns the stats of the recogntion"""
        test_data = array(data)
        reco_vector_list = self._package(test_data)

        return self._classifier.recognize_vectors(reco_vector_list)

    def _train(self, train_data, validate_data=None, test_data=None):

        clf = Tinn()

        # -1 because train_data last column is the label
        clf.initialize_tinn(
            train_data.shape[1] - 1,
            len(list(self._reverse_class_map.keys())),
            self._params["num_hidden_layer"],
        )

        loss = []
        for _ in range(self._params["iterations"]):
            loss.append(clf.fit(train_data.iloc[:, :-1], train_data.iloc[:, -1]))

        return clf.dump_model(), {"train_loss": loss}


def clean(values):
    return [int(x) if x >= 0 else 0 for x in values]


def clean_classes(values):
    return [argmax(x) for x in values]


def merge_features_classses(features, classes):

    for i, feature in enumerate(features):
        if feature == -2:
            features[i] = classes[i]

    return list(features)
