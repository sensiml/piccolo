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
from numpy import array


class PMEBase(ModelGenerator):
    """Base Class for generating models using the PME classifier"""

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
        super(PMEBase, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )

        self.neuron_range = config.get("neuron_range", [0, 0])
        self.number_of_neurons = int(config.get("number_of_neurons", 2056))

        distance_map = {"l1": 0, "lsup": 1, "dtw": 2}
        self.distance_mode = distance_map[config.get("distance_mode", "l1").lower()]
        self.classification_mode = (
            1 if config.get("classification_mode", "rbf").lower() == "knn" else 0
        )
        self.num_channels = config.get("num_channels", 1)
        self.max_aif = config.get("max_aif", 16384)
        self.min_aif = config.get("min_aif", 2)

        # Populate from the kwargs
        self._classifier.initialize_model(
            self.number_of_neurons + 1, self.number_of_features
        )
        self._remove_unknown = config.get("remove_unknown", False)

        self._set_classifier_settings()

    def _set_classifier_settings(self):
        self._classifier.set_classification_mode(self.classification_mode)
        self._classifier.set_distance_mode(self.distance_mode)
        self._classifier.set_max_aif(self.max_aif)
        self._classifier.set_min_aif(self.min_aif)
        self._classifier.set_num_channels(self.num_channels)

    def _package(self, data):
        vector_list = []
        for item in range(len(data)):
            item_ints = [int(i) for i in data[item][:-1]]
            pkg_dict = {
                "Category": int((data[item][-1])),
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Vector": list(item_ints),
                "DesiredResponses": 1,
            }
            vector_list.append(pkg_dict)
        return vector_list

    def _package_model_parameters(self, model_parameters, **kwargs):

        unknown_category = self.get_unknown_category_id()

        packaged_model = []

        counter = 0
        for _, neuron in enumerate(model_parameters):

            if unknown_category == neuron["Category"]:
                continue

            pkg_dict = {
                "Category": neuron["Category"],
                "Vector": neuron["Vector"][: self.number_of_features],
                "AIF": neuron["AIF"],
                "Identifier": counter,
            }

            counter += 1
            packaged_model.append(pkg_dict)

        return packaged_model

    def get_unknown_category_id(self):

        if self._remove_unknown and self.class_map.get("Unknown", None) is not None:
            return self.class_map["Unknown"]

        return None

    def _write(self, neurons):
        """Package set of vectors and AIFs for the simulator and write neurons.

        Used in the clustering algorithm instead of learning. There is a special
        case when the user requests number_of_neurons = 0. They are expecting a
        classifier to be created with the number of neurons required to reach
        homogeneity. Therefore this initializes the engine to the length of the
        incoming clusters instead of reseting the neuron array to its original
        size."""

        # Initialize the classifier
        self._classifier.initialize_model(len(neurons) + 1, self.number_of_features)
        self._classifier.load_model(neurons)
        self._set_classifier_settings()

    def _test(self, data):
        """Package set of vectors for the simulator and recognize the tensor with
        KBEngine."""
        test_data = array(data)
        reco_vector_list = self._package(test_data)

        # As a precaution, reset the classification mode and distance mode before recognizing
        self._set_classifier_settings()

        stats = self._classifier.recognize_vectors(reco_vector_list)

        return stats
