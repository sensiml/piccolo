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

import os

import pandas as pd
import pytest
from datamanager.models import KnowledgePack, User
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_validation.validation_methods import get_validation_method
from engine.recognitionengine import RecognitionEngine
from numpy import array

pytestmark = pytest.mark.django_db  # All tests use db


@pytest.fixture()
def knowledgepack():
    """Sets up a base knowledgepack for recognition"""

    kp = KnowledgePack()
    kp.pipeline_summary = [{"classifiers": [{"name": "PME"}]}]
    kp.class_map = {"0": 0, "1": 1, "2": 2, "3": 3}
    kp.neuron_array = [
        {"AIF": 9, "Category": 3, "Context": 1, "Identifier": 1, "Vector": [50, 14]},
        {"AIF": 6, "Category": 2, "Context": 1, "Identifier": 2, "Vector": [74, 64]},
        {"AIF": 6, "Category": 2, "Context": 1, "Identifier": 3, "Vector": [64, 55]},
        {"AIF": 2, "Category": 1, "Context": 1, "Identifier": 4, "Vector": [49, 34]},
        {"AIF": 6, "Category": 1, "Context": 1, "Identifier": 5, "Vector": [56, 40]},
        {"AIF": 0, "Category": 2, "Context": 1, "Identifier": 6, "Vector": [49, 45]},
        {"AIF": 6, "Category": 1, "Context": 1, "Identifier": 7, "Vector": [65, 45]},
        {"AIF": 3, "Category": 2, "Context": 1, "Identifier": 8, "Vector": [58, 50]},
    ]

    return kp


class TestLSup:
    """Compares KB Engine output to ground truth for LSup distance mode."""

    def setup_class(self):
        # Import training and test sets
        self.train_file_path = os.path.join(
            os.path.dirname(__file__), "data", "Iris_train.csv"
        )
        self.test_file_path = os.path.join(
            os.path.dirname(__file__), "data", "Iris_test.csv"
        )
        self.train = pd.read_csv(self.train_file_path)
        self.test = pd.read_csv(self.test_file_path)

        # The label 0 in the data files needs to be manually changed to a different integer (3)
        self.train.label = self.train.label.apply(lambda x: x if x != 0 else 3)
        self.test.label = self.test.label.apply(lambda x: x if x != 0 else 3)

        # Neurons for the recognition-only test

        # TVO configuration (matches the offline simulator settings that generated the ground data)
        self.config = {
            "classifier": "PME",
            "distance_mode": "lsup",
            "validation_method": "Recall",
            "optimizer": "RBF with Neuron Allocation Optimization",
            "label_column": "label",
            "number_of_iterations": 1,
            "classification_mode": "rbf",
            "max_aif": 10,
            "turbo": True,
            "aggressive_neuron_creation": True,
        }

    def test_lsup_write_and_recognize(self, knowledgepack):
        """Tests LSup recognition.

        Ensures correct predictions given a set of neurons and known ground data predictions."""

        user = User.objects.get(email="unittest@piccolo.com")
        validation_method = get_validation_method(self.config, self.train)
        classifier = get_classifier(self.config)
        self.model_generator = get_model_generator(
            self.config,
            classifier=classifier,
            validation_method=validation_method,
        )

        packaged_data = self.model_generator._package(array(self.test))

        reco_engine = RecognitionEngine(
            None,
            user,
            None,
            packaged_data,
            config=self.config,
            knowledgepack=knowledgepack,
        )
        result = reco_engine.reco_many_vector(with_labels=True)

        predictions = [v["CategoryVector"][0] for v in result["vectors"]]
        ground_truth = [
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            2,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            1,
            2,
            2,
            1,
            1,
            2,
            0,
        ]

        assert ground_truth, predictions
        assert 1, reco_engine.kbe.get_distance_mode()

    # @pytest.mark.skip()
    def test_lsup_train_and_recognize(self, knowledgepack):
        """Tests LSup learning and recognition.

        Ensures that Burlington learning with aggressive neuron creation gives correct predictions."""
        # print(self.train)

        user = User.objects.get(email="unittest@piccolo.com")
        validation_method = get_validation_method(self.config, self.train)
        classifier = get_classifier(self.config)
        self.model_generator = get_model_generator(
            self.config, classifier=classifier, validation_method=validation_method
        )

        learning_vector_list = self.model_generator._package(array(self.train))

        self.model_generator._classifier._reset_pme_database()

        model_parameters = self.model_generator._train_turbo_on(learning_vector_list)

        packaged_data = self.model_generator._package(array(self.test))

        knowledgepack.neuron_array = model_parameters

        # Test with RecognitionEngine to see individual predictions
        reco_engine = RecognitionEngine(
            None,
            user,
            None,
            packaged_data,
            config=self.config,
            knowledgepack=knowledgepack,
        )

        result = reco_engine.reco_many_vector(with_labels=True)

        predictions = [v["CategoryVector"][0] for v in result["vectors"]]

        ground_truth = [
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            2,
            1,
            2,
            1,
            1,
            1,
            1,
            2,
            1,
            1,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
        ]

        assert ground_truth == predictions
        assert 1 == self.model_generator._classifier.pme_classifiers[0].norm_mode
        assert 1, reco_engine.kbe.get_distance_mode()
