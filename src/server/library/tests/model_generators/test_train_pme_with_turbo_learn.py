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
from itertools import permutations

import pandas as pd
import pytest
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_validation.validation_methods import get_validation_method

np = pd.np
assert_almost_equal = np.testing.assert_almost_equal


logger = logging.getLogger(__name__)


class TestTurboLearn:

    """Test turbo learning (train until no new neurons possible) an nonturbo (single-pass)

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

        self.bool_sequence = [False, True, False, True, True, True]
        self.train_set = np.array([[0, 10, 1], [10, 3, 1], [5, 0, 2]])
        self.feature_names = None
        self.index = None
        self.make_train_set(self)

        self.test_cases = []
        for i, index in enumerate(permutations(self.train_set.index)):
            self.test_cases += [{}]
            self.train_set = self.train_set.reindex(index).copy()
            self.test_cases[i]["input"] = self.train_set
            self.test_cases[i]["results"] = self.train_set
            self.test_cases[i]["num_labels"] = len(self.train_set)
            self.test_cases[i]["name"] = "Three 2-D Vectors By Luis, Example {}".format(
                i + 1
            )
            self.test_cases[i]["neurons"] = []

        self.config_turbo_off = {
            "classifier": "PME",
            "validation_method": "Recall",
            "optimizer": "RBF with Neuron Allocation Optimization",
            "label_column": "label",
            "turbo": False,
            "number_of_iterations": 1,
        }
        self.turbo_off_classifier = get_classifier(self.config_turbo_off)

        self.config_turbo_on = {
            "classifier": "PME",
            "validation_method": "Recall",
            "optimizer": "RBF with Neuron Allocation Optimization",
            "label_column": "label",
            "turbo": True,
            "number_of_iterations": 1,
        }
        self.turbo_on_classifier = get_classifier(self.config_turbo_on)

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

    def setup_model(self, turbo_condition, test_case):
        validation_method = get_validation_method(turbo_condition, test_case["input"])
        classifier = get_classifier(turbo_condition)
        model_generator = get_model_generator(
            turbo_condition, classifier=classifier, validation_method=validation_method
        )
        return validation_method, classifier, model_generator

    def neuron_comparison_func(self, neuron_turbo_on, neuron_turbo_off):
        if len(neuron_turbo_on) != len(neuron_turbo_off):
            return False

        n = []
        for i in range(len(neuron_turbo_on)):
            n = n + [
                [
                    neuron_turbo_on[i]["Category"],
                    neuron_turbo_on[i]["AIF"],
                    neuron_turbo_on[i]["Vector"],
                ]
            ]

        for i in range(len(neuron_turbo_off)):
            if not (
                [
                    neuron_turbo_off[i]["Category"],
                    neuron_turbo_off[i]["AIF"],
                    neuron_turbo_off[i]["Vector"],
                ]
                in n
            ):
                return False

        return True

    @pytest.mark.skip(reason="Not sure what this is doing")
    def test_turbo_learn(self):
        """
        The below algorithm does the following:
           - permutations of the training set are created to test all sequences
           - for each sequence two models are created, one for “Turbo on” and one for “Turbo off”
           - for each sequence, results of these two models are compared (true, false)
           - compared results are used to create the Computed results
           - At the end of the sequence, the Computed results compared with Expected Results
        """

        bool_sequence = []

        for test_case in self.test_cases:
            neurons = []
            for x in ("on", "off"):
                if x == "on":
                    turbo_condition = self.config_turbo_on
                else:
                    turbo_condition = self.config_turbo_off
                # Creating the model
                validation_method, classifier, model_generator = self.setup_model(
                    turbo_condition, test_case
                )
                model_generator.run()
                results = model_generator.get_results()
                neurons = neurons + [results["neurons"]]
                # print (results['neurons'])

            bool_sequence = bool_sequence + [
                self.neuron_comparison_func(neurons[0], neurons[1])
            ]

        assert bool_sequence == self.bool_sequence, "Turbo on/off test NOT PASS "
