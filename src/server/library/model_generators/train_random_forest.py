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
from numpy import argmax, array
from sklearn.ensemble import RandomForestClassifier


class TrainRandomForest(ModelGenerator):
    """Creates optimal order-agnostic training set and trains with the resulting vector."""

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
        super(TrainRandomForest, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )

        self._params = {
            "n_estimators": config.get("n_estimators", 10),
            "max_depth": config.get("max_depth", 3),
            "bootstrap": "True",
        }

    def _package_model_parameters(self, models):
        """convert a list of dicision tree classifier to a json serializable form that can be
        saved and used to create a model for our tree_ensemble.c function"""
        data = []
        for model in models:
            model_data = {}
            model_data["children_left"] = clean(model.tree_.children_left)
            model_data["children_right"] = clean(model.tree_.children_right)
            model_data["threshold"] = clean(model.tree_.threshold)
            model_data["feature"] = merge_features_classses(
                convert_to_int(model.tree_.feature), clean_classes(model.tree_.value)
            )
            model_data["classes"] = convert_to_int(list(model.classes_))
            model_data["feature_importances"] = convert_to_float(
                list(model.feature_importances_)
            )
            data.append(model_data)

        return data

    def _test(self, data):
        """Package set of vectors for the simulator and recognize the tensors returns the stats of the recogntion"""
        test_data = array(data)
        reco_vector_list = self._package(test_data)

        return self._classifier.recognize_vectors(reco_vector_list)

    def _train(self, train_data, validate_data=None, test_data=None):

        clf = RandomForestClassifier(**self._params)
        label = self._config.get("label_column")

        X_q = train_data[[x for x in train_data.columns if x != label]]
        y = train_data[label]

        clf.fit(X_q, y)

        return self._package_model_parameters(clf.estimators_), None


def clean(values):
    return [int(x) if x >= 0 else 0 for x in values]


def convert_to_int(values):
    return [int(x) for x in values]


def convert_to_float(values):
    return [float(x) for x in values]


def clean_classes(values):
    return [int(argmax(x)) for x in values]


def merge_features_classses(features, classes):

    for i, feature in enumerate(features):
        if feature == -2:
            features[i] = classes[i]

    return list(features)
