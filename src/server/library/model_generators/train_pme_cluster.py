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

import library.algorithms.clustering_algo as ca
from library.model_generators.pme_base import PMEBase
from numpy import array, inf, nan


class ClusterLearning(PMEBase):
    """Creates optimal order-agnostic training set and trains PME with the resulting vector.

    Works with defaults if nothing specified:
        number_of_neurons = 15
        centroid_calculation = 'robust'
        norm_order = 1
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
        super(ClusterLearning, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )
        self.centroid_calculation = config.get("centroid_calculation", "robust")
        self.distance_metric = config.get("distance_metric", "cityblock")
        self.flip = int(config.get("flip", 1))
        self.linkage_method = config.get("linkage_method", "average")
        # This is only used by the distance-based methods
        self.cluster_criterion = "distance"
        self.cluster_method = config.get("cluster_method", "kmeans")
        self.aif_method = config.get("aif_method", "max")
        self.singleton_aif = config.get("singleton_aif", 1)
        self.convert_to_int = config.get("convert_to_int", True)
        self.min_number_of_dominant_vector = config.get(
            "min_number_of_dominant_vector", 3
        )
        self.max_number_of_weak_vector = config.get("max_number_of_weak_vector", 1)
        self.min_aif = config.get("min_aif", 2)

        self.num_neurons_max = 1024
        if self.distance_mode not in [0, 1, 2]:
            raise Exception("Distance Mode Not Supported for this Training Algorithm.")
        if self.num_channels > 1:
            raise Exception("NeuronOptimization only supports num_channels=1")

    def _package_model_parameters(self, centroids, aif):
        centroids = array(centroids)

        unknown_category = self.get_unknown_category_id()

        vector_list = []
        counter = 0
        for index, _ in enumerate(centroids):
            item_ints = [int(i) for i in centroids[index][:-1]]

            if unknown_category == int((centroids[index][-1])):
                continue

            pkg_dict = {
                "Category": int((centroids[index][-1])),
                "Identifier": counter,
                "Vector": list(item_ints),
                "AIF": aif[index],
            }
            counter += 1

            vector_list.append(pkg_dict)

        return vector_list

    def _parse_clustering(self, model, columns):
        model.iloc[:, :-1].replace([inf, inf], nan, inplace=True)
        aif = [int(x) for x in model.iloc[:, -1]]
        centroid_data = model.iloc[:, :-1].fillna(0).astype(int)
        centroid_data.columns = columns

        return aif, centroid_data

    # Distance and label-based hierarchical clustering
    def _train(self, train_data, validate_data=None, test_data=None):

        data_with_label = train_data.reset_index(drop=True)

        label_col = data_with_label.columns[-1]
        label_col_idx = len(data_with_label.columns) - 1
        X = data_with_label.iloc[:, :label_col_idx]
        y = data_with_label[label_col]

        model = ca.call_clustering(
            X,
            y,
            num_neurons=self.number_of_neurons,
            cluster_method=self.cluster_method,
            centroid_calculation=self.centroid_calculation,
            distance_mode=self.distance_mode,
            aif_method=self.aif_method,
            linkage_method=self.linkage_method,
            singleton_aif=self.singleton_aif,
            num_neurons_max=self.num_neurons_max,
            sort_data=self.sort_data,
            convert_to_int=self.convert_to_int,
            min_number_of_dominant_vector=self.min_number_of_dominant_vector,
            max_number_of_weak_vector=self.max_number_of_weak_vector,
            min_aif=self.min_aif,
        )

        aif, centroids = self._parse_clustering(model, train_data.columns)

        return self._package_model_parameters(centroids, aif), None
