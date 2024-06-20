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

# coding=utf-8
import logging
import os

import numpy as np
import pandas as pd
import pytest
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_validation.validation_methods import get_validation_method

assert_almost_equal = np.testing.assert_almost_equal


logger = logging.getLogger(__name__)


@pytest.fixture
def feature_vectors():
    return pd.DataFrame(
        [
            [254, 253, 252, 1],
            [254, 252, 253, 1],
            [254, 252, 252, 1],
            [254, 251, 253, 1],
            [254, 251, 254, 1],
            [253, 250, 253, 1],
            [253, 252, 254, 1],
            [252, 252, 253, 1],
            [254, 252, 253, 1],
            [253, 252, 254, 1],
            [252, 250, 254, 1],
            [254, 250, 254, 1],
            [252, 250, 253, 1],
            [250, 252, 254, 1],
            [249, 253, 253, 1],
            [248, 254, 253, 1],
            [250, 254, 254, 1],
            [8, 2, 0, 2],
            [10, 1, 0, 2],
            [8, 0, 1, 2],
            [7, 1, 1, 2],
            [5, 0, 2, 2],
            [5, 0, 2, 2],
            [6, 2, 3, 2],
            [5, 2, 2, 2],
            [5, 2, 2, 2],
            [3, 2, 2, 2],
            [3, 2, 1, 2],
            [2, 1, 1, 2],
            [3, 2, 1, 2],
            [2, 4, 1, 2],
            [2, 3, 0, 2],
            [0, 2, 0, 2],
            [0, 1, 1, 2],
            [254, 253, 252, 1],
            [254, 252, 253, 1],
            [254, 252, 252, 1],
            [254, 251, 253, 1],
            [254, 251, 254, 1],
            [253, 250, 253, 1],
            [253, 252, 254, 1],
            [252, 252, 253, 1],
            [254, 252, 253, 1],
            [253, 252, 254, 1],
            [252, 250, 254, 1],
            [254, 250, 254, 1],
            [252, 250, 253, 1],
            [250, 252, 254, 1],
            [249, 253, 253, 1],
            [248, 254, 253, 1],
            [250, 254, 254, 1],
            [8, 2, 0, 2],
            [10, 1, 0, 2],
            [8, 0, 1, 2],
            [7, 1, 1, 2],
            [5, 0, 2, 2],
            [5, 0, 2, 2],
            [6, 2, 3, 2],
            [5, 2, 2, 2],
            [5, 2, 2, 2],
            [3, 2, 2, 2],
            [3, 2, 1, 2],
            [2, 1, 1, 2],
            [3, 2, 1, 2],
            [2, 4, 1, 2],
            [2, 3, 0, 2],
            [0, 2, 0, 2],
            [0, 1, 1, 2],
        ]
    )


@pytest.fixture
def iris_data():
    """Generate a list of dict containing test cases
    Below expected results of original permutation sequence
    [False,True,False,True,True,True]
    """
    train_set = pd.read_csv(os.path.join("engine", "tests", "data", "Iris_train.csv"))

    train_set["label"] += 1

    test_set = pd.read_csv(os.path.join("engine", "tests", "data", "Iris_test.csv"))
    test_set["label"] += 1

    return pd.concat([train_set, test_set], ignore_index=True)


@pytest.fixture
def feature_vectors_2k():
    df = pd.read_csv(os.path.join("engine", "tests", "data", "feature_vectors.csv"))
    mapper = {"normal": 1, "outlier": 2}
    df["label"] = df["label"].apply(lambda x: mapper[x])

    return df


class TestTrainRandomForest:
    def setup_model(self, config, data):
        validation_method = get_validation_method(config, data)
        classifier = get_classifier(config)
        model_generator = get_model_generator(
            config, classifier=classifier, validation_method=validation_method
        )

        return validation_method, classifier, model_generator

    def test_train_random_forest_iris_data(self, iris_data):
        config = {
            "classifier": "Decision Tree Ensemble",
            "validation_method": "Recall",
            "optimizer": "Random Forest",
            "label_column": "label",
            "max_depth": 5,
            "n_estimators": 50,
        }

        validation_method, classifier, model_generator = self.setup_model(
            config, iris_data
        )

        # data = classifier.preprocess(3, feature_vectors)

        model_parameters, _ = model_generator._train(iris_data)

        model_generator._classifier.load_model(model_parameters)

        model_generator._test(iris_data)

    def test_train_random_forest_2000_fv(self, feature_vectors_2k):
        config = {
            "classifier": "Decision Tree Ensemble",
            "validation_method": "Recall",
            "optimizer": "Random Forest",
            "label_column": "label",
            "max_depth": 20,
            "n_estimators": 50,
        }

        validation_method, classifier, model_generator = self.setup_model(
            config, feature_vectors_2k
        )

        # data = classifier.preprocess(3, feature_vectors)

        model_parameters, _ = model_generator._train(feature_vectors_2k)
        model_generator._classifier.load_model(model_parameters)

        model_generator._test(feature_vectors_2k)
