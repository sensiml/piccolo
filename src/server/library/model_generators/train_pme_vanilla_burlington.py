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

from library.model_generators.pme_base import PMEBase
from numpy import array


class VanillaBurlington(PMEBase):
    """
    "description": "Train PME with the classic Burlington learning algorithm.\
    Works with defaults if nothing specified.\
    DEFAULTS: number_of_neurons=10000, number_of_features=128, number_of_iterations=20"
    }
    """

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
        super(VanillaBurlington, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )
        self.turbo = True if config.get("turbo", True) not in (False, 0) else False
        self.degenerate_neurons = config.get(
            "degenerate_neurons", "keep_degenerate_neurons"
        )

    def _train_turbo_off(self, vector_list):
        """Package set of vectors for the simulator. Calls the engine's learn_vector method once for each vector."""

        for vector in vector_list:
            self._classifier._learn_vector(0, vector["Vector"], vector["Category"])
            if self.degenerate_neurons == "remove_immediately":
                self._remove_degenerate_neurons()

        if self.degenerate_neurons == "remove_at_the_end":
            self._remove_degenerate_neurons()

        return self._classifier.dump_model()

    def _train_turbo_on(self, vector_list):
        """
        Train Burlington model on the provided list of training vectors.
        The format of vector_list is [{'Vector': [], 'Category': number}].
        """
        previous_count = 0
        classifier_id = 0
        previous_count_full_train = 0
        neuron_count = 0
        remove_vector_list = []
        done = False

        # The below algorithm does the following:
        #   - Run through the training set and for each vector that results
        #     in a new neuron, remove that vector
        #   - Run through the training set again (this time only with those
        #     vectors that did not create new neurons)
        #   - If no new knowledge (neurons) are created on a subsequent run,
        #     we are done
        while not done:
            for i in range(0, len(vector_list)):
                # Added second condition because the routine was adding
                # neurons beyond the initialized max neuron count\

                if (neuron_count < self._classifier.get_max_patterns() - 1) and (
                    i not in remove_vector_list
                ):
                    neuron_count = int(
                        self._classifier._learn_vector(
                            classifier_id,
                            vector_list[i]["Vector"],
                            vector_list[i]["Category"],
                        )
                    )

                if previous_count < neuron_count:
                    # New neuron allocated for this vector, take vector off
                    # list of training
                    remove_vector_list.append(i)

                    if self.degenerate_neurons == "remove_immediately":
                        neuron_count = self._remove_degenerate_neurons()

                    previous_count = neuron_count

            if neuron_count - previous_count_full_train > 0:
                previous_count_full_train = neuron_count
            else:
                done = True

        self._remove_degenerate_neurons()

        return self._classifier.dump_model()

    def _check_previous_neuron_for_degeneracy(self):
        # read current neurons

        neurons = self._classifier.dump_model()

        if neurons[-1]["AIF"] < self.min_aif or neurons[i]["Category"] > 3000:

            del neurons[-1]

            self._classifier.load_model(neurons)

            return len(neurons)

        return len(neurons)

    def _remove_degenerate_neurons(self):
        # read current neurons
        degenerate_neurons_flag = False
        neurons = self._classifier.dump_model()

        new_neurons = []
        for i in range(len(neurons)):
            # TODO: [SDL-1265] Fix this in the hwsimulator
            if neurons[i]["AIF"] >= self.min_aif and neurons[i]["Category"] < 3000:
                new_neurons.append(neurons[i])
            else:
                degenerate_neurons_flag = True

        if degenerate_neurons_flag:
            self._classifier.load_model(new_neurons)

        return len(new_neurons)

    def _train(self, train_data, validate_data=None, test_data=None):
        """Package set of vectors for the simulator and teach the tensor to
        KBEngine. Uses the engine's iterative learn_vectors method."""

        training_metrics = {
            "validation": {"f1_score": [], "sensitivity": [], "accuracy": []},
            "train": {"f1_score": [], "sensitivity": [], "accuracy": []},
        }

        for iteration in range(self._config["number_of_iterations"]):
            train_indices, _, _ = self._validation_method.permute_indices()
            train_iteration = train_data.reindex(train_indices).copy()

            learning_vector_list = self._package(array(train_iteration))

            self._classifier._reset_pme_database()

            if not self.turbo:
                model_parameters = self._train_turbo_off(learning_vector_list)
            else:
                model_parameters = self._train_turbo_on(
                    vector_list=learning_vector_list
                )

            stats_validation = self._test(validate_data)
            stats_train = self._test(validate_data)

            training_metrics["train"]["f1_score"].append(stats_train["f1_score"])
            training_metrics["train"]["accuracy"].append(stats_train["accuracy"])
            training_metrics["train"]["sensitivity"].append(stats_train["sensitivity"])
            training_metrics["validation"]["f1_score"].append(
                stats_validation["f1_score"]
            )
            training_metrics["validation"]["accuracy"].append(
                stats_validation["accuracy"]
            )
            training_metrics["validation"]["sensitivity"].append(
                stats_validation["sensitivity"]
            )

            if isinstance(stats_validation[self.ranking_metric], dict):
                score = stats_validation[self.ranking_metric]["average"]
            else:
                score = stats_validation[self.ranking_metric]

            if iteration == 0:
                best_iteration_score = score
                best_model_parameters = model_parameters

            elif score > best_iteration_score:
                best_model_parameters = model_parameters

        return (
            self._package_model_parameters(best_model_parameters),
            None,
        )
