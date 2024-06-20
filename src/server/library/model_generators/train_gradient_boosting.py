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
from numpy import argmax
from xgboost import XGBClassifier


class TrainGradientBoosting(ModelGenerator):
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
        super(TrainGradientBoosting, self).__init__(
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
        }

    def _package_model_parameters(self, model):
        """convert a list of dicision tree classifier to a json serializable form that can be
        saved and used to create a model for our tree_ensemble.c function"""

        return model._Booster.trees_to_dataframe().to_dict(orient="records")

    def _train(self, train_data, validate_data=None, test_data=None):

        clf = XGBClassifier(**self._params)
        label = self._config.get("label_column")

        X_q = train_data[[x for x in train_data.columns if x != label]].values
        y = train_data[label]

        if len(y.unique()) > 2:
            raise Exception(
                "Gradient Boosting currently only supports binary classification"
            )

        clf.fit(X_q, y)

        return self._package_model_parameters(clf), None


def clean(values):
    return [int(x) if x >= 0 else 0 for x in values]


def clean_classes(values):
    return [argmax(x) for x in values]


def merge_features_classses(features, classes):

    for i, feature in enumerate(features):
        if feature == -2:
            features[i] = classes[i]

    return list(features)
