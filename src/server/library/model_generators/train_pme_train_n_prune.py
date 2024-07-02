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

import operator

from numpy import array

from library.model_generators.pme_base import PMEBase


class TrainNPrune(PMEBase):
    """Class for the TrainNPrune learning algorithm."""

    def _prune_test(self, validation_set):
        """Runs reco_vectors and accumulates resulting stats with the validation set."""

        category_list = sorted(set([int(vec["Category"]) for vec in validation_set]))
        cm_list = list(category_list) + ["UNC", "UNK"]

        stats = self._classifier.recognize_vectors(validation_set)

        row_total = {}
        row_se_total = {}
        col_total = {}
        diag_total = 0
        total_total = 0
        total_se_total = 0

        for i in category_list:
            row_total[i] = 0
            row_se_total[i] = 0
            for j in cm_list:
                if j not in ["UNC", "UNK"]:
                    row_total[i] += stats["ConfusionMatrix"][i][j]
                    row_se_total[i] += stats["ConfusionMatrix"][i][j]
                    if j not in col_total:
                        col_total[j] = stats["ConfusionMatrix"][i][j]
                    else:
                        col_total[j] += stats["ConfusionMatrix"][i][j]
                    if j == i:
                        diag_total += stats["ConfusionMatrix"][i][j]
                if j == "UNK":
                    row_se_total[i] += stats["ConfusionMatrix"][i][j]

            total_total += row_total[i]
            total_se_total += row_se_total[i]

        try:
            total_accuracy = float(diag_total) / float(total_total)
        except ZeroDivisionError:
            total_accuracy = 0.0

        return stats, total_accuracy

    def _train(self, train_data, validate_data=None, test_data=None):
        """Calls the Train-N-Prune learning algorithm within a cross-validation loop.

        Gathers self.results, performs final testing, and makes one or more recommendations.
        """

        learning_vector_list = self._package(array(train_data))
        validation_set = self._package(array(validate_data))

        chunk_size = self._config["chunk_size"]
        inverse_relearn_frequency = self._config["inverse_relearn_frequency"]
        max_neurons = int(self._config.get("max_neurons", 128))  # Neuron budget

        chunks = [
            learning_vector_list[x : x + chunk_size]
            for x in range(0, len(learning_vector_list), chunk_size)
        ]

        num_chunks = len(chunks)

        working_neurons = []

        confusion_matrices = {}
        confusion_matrices["Train"] = []
        confusion_matrices["Prune"] = []
        confusion_matrices["Relearn"] = []

        accuracies = {}
        accuracies["Train"] = []
        accuracies["Prune"] = []
        accuracies["Relearn"] = []

        statistics = {}

        for i in range(0, num_chunks - 1):
            confusion_matrices["Train"].append([])
            confusion_matrices["Prune"].append([])
            confusion_matrices["Relearn"].append([])
            accuracies["Train"].append([])
            accuracies["Prune"].append([])
            accuracies["Relearn"].append([])
            for j in range(0, inverse_relearn_frequency):
                if (i + j) < num_chunks:
                    chunk = list(chunks[i + j])
                # Should update this to vanilla burlington (turbo/non-turbo) one pass
                # There is already a classifier that exists; it will have neurons from the last iteration/chunk
                self._classifier.learn_vectors(chunk)

                stats, total_accuracy = self._prune_test(validation_set)
                confusion_matrices["Train"][i].append(stats["ConfusionMatrix"])
                accuracies["Train"][i].append(total_accuracy)

                # Sort based on fire count - this sorting function should be swappable with others
                # Parameterize the cost / sorting function
                # Neuron index 0 invalid
                fire_counts = stats["NeuronFireCount"]
                fire_counts.pop(0, None)
                sorted_fire_counts = sorted(
                    fire_counts.items(), key=operator.itemgetter(1), reverse=True
                )
                working_neurons_list = self._classifier.dump_model()
                working_neurons = []
                remaining_neurons = set()
                for nrn in working_neurons_list:
                    remaining_neurons.add(nrn["Identifier"])

                # Prune - want a new model with neuron count smaller than or equal to neuron budget
                for index in range(0, min(max_neurons, len(sorted_fire_counts))):
                    working_neurons.append(
                        working_neurons_list[sorted_fire_counts[index][0] - 1]
                    )
                    remaining_neurons.discard(sorted_fire_counts[index][0])
                for ndx in remaining_neurons:
                    if len(working_neurons) >= max_neurons:
                        break
                    working_neurons.append(working_neurons_list[ndx - 1])

                self._classifier.load_model(working_neurons)
                # COULD RE-TRAIN WITH THE WORKING SET HERE INSTEAD OF RE-WRITING THE NEURONS
                # self._classifier.initialize(self.numNeurons, self.numFeatures)
                # self._classifier.learn_vectors(workingNeurons)

                stats, total_accuracy = self._prune_test(validation_set)
                confusion_matrices["Prune"][i].append(stats["ConfusionMatrix"])
                accuracies["Prune"][i].append(total_accuracy)

            # Relearning
            self._classifier._reset_pme_database()
            self._classifier.learn_vectors(working_neurons)

            # Need to save two sets of models - the second one that meets budget and the third that relearns as well
            stats, total_accuracy = self._prune_test(validation_set)
            confusion_matrices["Relearn"][i].append(stats["ConfusionMatrix"])
            accuracies["Relearn"][i].append(total_accuracy)
            statistics[i] = stats

        return (
            self._package_model_parameters(self._classifier.dump_model()),
            None,
        )
