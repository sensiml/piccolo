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

import library.algorithms.clustering_algo_with_caching as ca
import engine.base.utils as utils
import numpy as np
from library.model_generators.train_pme_cluster import ClusterLearning

CLASS_MODES = {0: "rbf", 1: "knn"}
METRICS = ["sensitivity", "precision", "f1_score"]
HAS_KEYS = {
    "sensitivity": True,
    "precision": True,
    "f1_score": True,
    "accuracy": False,
    "specificity": False,
}
AVG = "average"


class NeuronOptimization(ClusterLearning):
    """Creates optimal order-agnostic training set and trains PME with the resulting vector.

    Works with defaults if nothing specified:
    neuron_range = 15
    centroid_calculation = 'robust'
    distance_mode = 1
    distance_metric = 'cityblock'
    flip = 1
    linkage_method = 'average'
    cluster_method = 'DLHC'
    aif_method = 'max'
    singleton_aif = 0
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
        """Initialize with defaults for missing values."""
        super(NeuronOptimization, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )
        self.neuron_range = config.get("neuron_range", [2, 30])
        self.cluster_method = config.get("cluster_method", "DLHC")
        if self.num_channels > 1:
            raise Exception("NeuronOptimization only supports num_channels=1")

    # Distance and label-based hierarchical clustering with caching
    def _train(self, train_data, validate_data=None, test_data=None):

        label_col = train_data.columns[-1]
        label_col_idx = len(train_data.columns) - 1
        X = train_data.iloc[:, :label_col_idx]
        y = train_data[label_col]

        cached_model = ca.call_clustering_with_caching(
            X,
            y,
            neuron_range=self.neuron_range,
            cluster_method=self.cluster_method,
            centroid_calculation=self.centroid_calculation,
            distance_mode=self.distance_mode,
            aif_method=self.aif_method,
            linkage_method=self.linkage_method,
            singleton_aif=self.singleton_aif,
            num_neurons_max=self.num_neurons_max,
            convert_to_int=self.convert_to_int,
        )

        return cached_model, None

    def run(self):
        """Calls the cluster-based learning algorithm with the specified validation method. Scales the resulting
        centroids, trains the simulator, gathers results and returns a summary of model performance
        """

        self._initialize_validation_method()

        # Place to collect results
        self.results = {"models": {}, "neurons": {}, "metrics": {}}

        for fold in range(self._validation_method.number_of_sets):
            (
                train_data,
                validate_data,
                test_data,
            ) = self._validation_method.next_validation()
            # Get cluster centroids and AIFs and convert to int
            # Run method for the chosen cluster_method

            train_data = train_data.sort_values(
                by=list(train_data.columns)
            ).reset_index(drop=True)

            cached_model, _ = self._train(train_data)

            model_keys = cached_model.iloc[:, -1].unique()

            for model_key in model_keys:

                model = cached_model[cached_model.num_neurons == model_key].iloc[:, :-1]

                model.columns = range(0, np.shape(model)[1])
                model = model.astype(np.int64)

                aif, centroids = self._parse_clustering(model, train_data.columns)

                neurons = self._package_model_parameters(centroids, aif)

                for classification_mode in [0, 1]:
                    key = "Fold {}, Neurons {}, Classification {}".format(
                        fold, model_key, CLASS_MODES[classification_mode]
                    )
                    self.results["models"][key] = {}
                    self.classification_mode = classification_mode

                    # Write neurons
                    self._write(neurons)

                    # store the model data
                    self._store_model_data(
                        key,
                        parameters=neurons,
                    )

                    # call and store classification results
                    self._get_classification_and_metrics(
                        key,
                        train_data=train_data,
                        validate_data=validate_data,
                        test_data=test_data,
                    )

        result_matrix = utils.get_metric_matrix(self.results)
        aggregate_metrics = utils.get_metric_matrix_stats(
            result_matrix, group_columns=["Neurons", "Classification"]
        )

        best_params = sorted(
            aggregate_metrics.to_dict("records"),
            key=lambda x: x["f1_score"],
            reverse=True,
        )[0]
        self.results["models"]["Fold 0"] = self.results["models"][
            "Fold 0, Neurons {}, Classification {}".format(
                best_params["Neurons"], best_params["Classification"]
            )
        ]

        self.results["metrics"] = aggregate_metrics.to_dict("records")
