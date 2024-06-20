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


class TestTurboLearn:

    """
    Test turbo learning (train until no new neurons possible) an nonturbo (single-pass)

    Parameter to control enabling/disabling of “Turbo Training”. Turbo is when the training set is presented again to
    the Vanilla Burlington trainer to add any neurons that were not created in the previous cycle. This ensures 100%
    recall accuracy, which we don’t always want.

    An internal "fixture" (class attributes) of training data was provided by Luis:
    Input feature vectors (2-D) with labels (1 and 2, blue and red)
    Expected neurons (for each permutation of the feature vector training sequence)
    Expected recognition labels (for each of the training vectors after training)
    """

    def setup_class(self):
        """Generate a list of dict containing test cases
        Below expected results of original permutation sequence
        [False,True,False,True,True,True]
        """

        train_set = pd.read_csv(
            os.path.join("engine", "tests", "data", "Iris_train.csv")
        )

        train_set["label"] += 1

        test_set = pd.read_csv(os.path.join("engine", "tests", "data", "Iris_test.csv"))

        test_set["label"] += 1

        self.data = pd.concat([train_set, test_set], ignore_index=True)

        self.config = {
            "classifier": "PME",
            "validation_method": "Recall",
            "optimizer": "RBF with Neuron Allocation Optimization",
            "label_column": "label",
            "number_of_iterations": 10,
            "ranking_metric": "accuracy",
        }

    def setup_model(self, config, data):
        validation_method = get_validation_method(config, data)
        classifier = get_classifier(config)
        model_generator = get_model_generator(
            config, classifier=classifier, validation_method=validation_method
        )
        return validation_method, classifier, model_generator

    @pytest.mark.django_db
    def test_pme_ranking_metric(self, loaddata):
        """
        The below algorithm does the following:
           - permutations of the training set are created to test all sequences
           - for each sequence two models are created, one for “Turbo on” and one for “Turbo off”
           - for each sequence, results of these two models are compared (true, false)
           - compared results are used to create the Computed results
           - At the end of the sequence, the Computed results compared with Expected Results
        """

        loaddata("test_classifier_costs")

        for ranking_metric in ["f1_score", "accuracy", "sensitivity"]:
            self.config["ranking_metric"] = ranking_metric
            validation_method, classifier, model_generator = self.setup_model(
                self.config, self.data
            )
            model_generator.run()
            results = model_generator.get_results()
            print(results)
