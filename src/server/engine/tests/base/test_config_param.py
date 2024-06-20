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

from itertools import permutations

import pandas as pd
import pytest

from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_validation.validation_methods import get_validation_method

import numpy as np

assert_almost_equal = np.testing.assert_almost_equal


class TestConfigParamUnitTest:

    """Test optimization of hyperparameters

    An internal "fixture" (class attributes) of training data was provided by Luis:
      Input feature vectors (2-D) with labels (1 and 2, blue and red)
      Expected neurons (for each permutation of the feature vector training sequence)
      Expected recognition labels (for each of the training vectors after training)
    """

    def setup_class(self):
        """Generate a list of dict containing test cases"""
        self.train_set = [[0, 0, 1], [10, 10, 2]]
        self.feature_names = None
        self.index = None
        self.make_train_set(self)

        self.test_cases = []
        for i, index in enumerate(permutations(self.train_set.index)):
            # print i, index
            self.test_cases += [{}]
            self.train_set = self.train_set.reindex(index).copy()
            self.test_cases[i]["input"] = self.train_set
            self.test_cases[i]["results"] = self.train_set
            self.test_cases[i]["num_labels"] = len(self.train_set)
            self.test_cases[i]["name"] = "Three 2-D Vectors By Luis, Example {}".format(
                i + 1
            )
            self.test_cases[i]["neurons"] = []

        self.config = {
            "classifier": "PME",
            "validation_method": "Recall",
            "optimizer": "RBF with Neuron Allocation Optimization",
            "label_column": "label",
            "number_of_iterations": 1,
            "distance_mode": "L1",
            "max_aif": 255,
            "min_aif": 2,
        }
        self.classifier = get_classifier(self.config)

    def make_train_set(self):
        if self.train_set is None:
            raise ValueError("Need data for training set!!")
        if not isinstance(self.train_set, pd.DataFrame):
            self.train_set = pd.DataFrame(
                self.train_set,
                index=range(len(self.train_set)),
                columns=range(len(self.train_set[0])),
            )
        if self.feature_names is None:
            self.feature_names = [
                "feature{}".format(i) for i in range(len(self.train_set.columns) - 1)
            ]
        self.feature_names = self.feature_names + ["label"]
        if self.index is None:
            self.index = np.arange(len(self.train_set))
        self.train_set = pd.DataFrame(
            self.train_set.values, index=self.index, columns=list(self.feature_names)
        )

    @pytest.mark.django_db
    def test_config_param(self, loaddata):
        loaddata("test_classifier_costs")
        expected_result = {"Lsup": 10, "L1": 20}

        test_case = self.test_cases[0]
        for metric in ("Lsup", "L1"):
            print(metric, "test")
            self.config["distance_mode"] = metric
            validation_method = get_validation_method(self.config, test_case["input"])
            classifier = get_classifier(self.config)
            model_generator = get_model_generator(
                self.config, classifier=classifier, validation_method=validation_method
            )
            model_generator.run()
            results = model_generator.get_results()
            model_parameters = results["models"]["Fold 0"]["parameters"]
            aif_result = model_parameters[0]["AIF"]
            print(model_generator.distance_mode)
            print(
                "Assertion: result", aif_result, "== expected", expected_result[metric]
            )
            assert (
                aif_result == expected_result[metric]
            ), "Parameter config Lsup/L1 test failed..."

    @pytest.mark.django_db
    def test_config_param_maxaif(self, loaddata):
        loaddata("test_classifier_costs")
        #  Start maxAIF configuration test
        newMaxAIF = 4
        expected_result = {"maxAIF": newMaxAIF}
        test_case = self.test_cases[0]
        self.config["max_aif"] = newMaxAIF
        validation_method = get_validation_method(self.config, test_case["input"])
        classifier = get_classifier(self.config)
        model_generator = get_model_generator(
            self.config, classifier=classifier, validation_method=validation_method
        )
        model_generator.run()
        results = model_generator.get_results()

        model_parameters = results["models"]["Fold 0"]["parameters"]

        assert len(model_parameters) > 0

        for neuron in model_parameters:
            assert neuron["AIF"] <= newMaxAIF

    @pytest.mark.django_db
    def test_config_param_minaif(self, loaddata):
        loaddata("test_classifier_costs")
        #  Start minAIF configuration test
        print("minAIF test")
        newMinAIF = 10
        self.config["max_aif"] = 100
        self.config["min_aif"] = newMinAIF
        expected_result = {"minAIF": newMinAIF}
        test_case = self.test_cases[0]
        self.config["min_aif"] = newMinAIF
        validation_method = get_validation_method(self.config, test_case["input"])
        classifier = get_classifier(self.config)
        model_generator = get_model_generator(
            self.config, classifier=classifier, validation_method=validation_method
        )
        model_generator.run()
        results = model_generator.get_results()

        model_parameters = results["models"]["Fold 0"]["parameters"]

        assert len(model_parameters) > 0

        for neuron in model_parameters:
            assert neuron["AIF"] > newMinAIF
