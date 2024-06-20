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

import logging

import numpy as np
import pandas as pd
import pytest
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_validation.validation_methods import get_validation_method

assert_almost_equal = np.testing.assert_almost_equal


logger = logging.getLogger(__name__)


class TestdegenerateNeuron:

    """
    Parameter to enable/disable a new algorithm that removes any degenerate neurons (as defined by AIF < minAIF)
    """

    def setUp(self):
        """Generate a list of dict containing test cases"""
        self.train_set = [[2, 8, 1], [5, 8, 2], [6, 8, 1], [8, 8, 2], [4, 8, 1]]

        self.feature_names = None
        self.index = None
        self.make_train_set()

        # to create dictionary frame
        self.test_cases = {}
        self.test_cases["input"] = self.train_set
        self.test_cases["results"] = self.train_set
        self.test_cases["num_labels"] = len(self.train_set)
        self.test_cases["neurons"] = []

        self.config = {
            "classifier": "PME",
            "validation_method": "Recall",
            "optimizer": "RBF with Neuron Allocation Optimization",
            "label_column": "label",
            "number_of_iterations": 1,
            "degenerate_neurons": "keep_degenerate_neurons",
            "turbo": False,
            "min_aif": 25,
            "classification_mode": "RBF",
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

    def setup_model(self):
        # this function is used to create a model
        validation_method = get_validation_method(self.config, self.test_cases["input"])
        classifier = get_classifier(self.config)
        model_generator = get_model_generator(
            self.config, classifier=classifier, validation_method=validation_method
        )

        return validation_method, classifier, model_generator

    @pytest.mark.django_db
    def test(self, loaddata):
        loaddata("test_classifier_costs")
        self.setUp()

        for degenerate_neurons_parameter in (
            "keep",
            "remove_at_the_end",
            "remove_immediately",
        ):
            # changing the parameter
            self.config["degenerate_neurons"] = degenerate_neurons_parameter
            # creating model
            validation_method, classifier, model_generator = self.setup_model()
            model_generator.run()
            results = model_generator.get_results()
            model_parameters = results["models"]["Fold 0"]["parameters"]

            neurons = pd.DataFrame(model_parameters)
            for i in range(len(neurons)):
                neurons.at[i, "Vector"] = str(neurons["Vector"][i][0:3])
                neurons.at[i, "Degenerated Neurons"] = (
                    neurons["Category"][i] in self.train_set["label"].tolist()
                )

            # to display the results  ----------------------------------
            # print neurons[['Degenerated Neurons','Category','Identifier','AIF','Context','Vector']], '\n'

            if degenerate_neurons_parameter == "keep":
                assert (False not in neurons["Degenerated Neurons"].values) & (
                    True in neurons["Degenerated Neurons"].values
                ), (degenerate_neurons_parameter + " test FAILED")
            else:
                assert False not in neurons["Degenerated Neurons"].values, (
                    degenerate_neurons_parameter + " test FAILED"
                )
