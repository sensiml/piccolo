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

import numpy as np
import pandas as pd
from scipy.stats import mode

import library.algorithms.clustering_algo as ca

##################################################
# Wrapper for ClusteringAlgorithmWithCaching algorithm
# Inputs:
# X - dataframe containing feature matrix
# y - dataframe containing labels
# neuronRange - list containing min and max values
# cluster_method - 'DLHC', 'DLC', or 'kmeans'
# centroid_calculation = 'robust', 'mean', or 'median'
# norm_order = '1', or 'np.inf'
# linkage_method = 'average', 'complete', or 'single'
# AIF_method = 'max', 'min', 'mean', or 'median'
# singleton_AIF = 0 or any positive value
# num_neurons_max = 128 or any positive value
# Outputs:
# model containing neurons (feature vector, label, and AIF)


class NeuronRangeException(Exception):
    pass


def call_clustering_with_caching(
    X,
    y,
    neuron_range,
    cluster_method="DLHC",
    centroid_calculation="robust",
    distance_mode=0,
    linkage_method="average",
    aif_method="max",
    singleton_aif=0,
    num_neurons_max=128,
    sort_data=1,
    convert_to_int=True,
    min_number_of_dominant_vector=10000,
    max_number_of_weak_vector=1,
    min_aif=2,
):

    if distance_mode == 0:
        distance_mode = "L1"
        norm_order = 1
    elif distance_mode == 1:
        distance_mode = "Lsup"
        norm_order = 2
    else:
        assert "Err: Distance_mode values is not assigned"

    if len(neuron_range) < 2:
        raise NeuronRangeException("Neuron range is not properly specified.")

    elif neuron_range[1] <= neuron_range[0]:
        raise NeuronRangeException("Neuron range start is before neuron range end.")

    elif y.size == 0 | X.size == 0:
        raise NeuronRangeException("The size of your labels/data is 0.")

    elif y.size == 1:
        model = X
        model["Label"] = y
        model["AIF"] = singleton_aif
        model["num_neurons"] = 1

    # if demanded num_neurons is bigger than provided samples, each sample point will be its own centroid
    elif y.size <= neuron_range[0] | y.size <= neuron_range[1]:
        model = X
        model["Label"] = y
        model["AIF"] = [singleton_aif for x in range(y.size)]
        model["num_neurons"] = y.size

    else:
        cluster_crit = "distance"

        if norm_order == 1:
            dist_metric = "cityblock"
        elif norm_order == 2:  # (norm_order == np.inf):
            dist_metric = "chebyshev"

        model = []
        if cluster_method == "DHC":
            model = dist_hierarch_clustering_with_caching(
                X,
                y,
                neuron_range,
                centroid_calculation,
                norm_order,
                aif_method,
                linkage_method,
                cluster_crit,
                dist_metric,
                singleton_aif,
                num_neurons_max,
                sort_data,
                convert_to_int,
            )

        elif cluster_method == "DLHC":
            model = dist_and_label_hierarch_clustering_with_caching(
                X,
                y,
                neuron_range,
                centroid_calculation,
                norm_order,
                aif_method,
                linkage_method,
                cluster_crit,
                dist_metric,
                singleton_aif,
                num_neurons_max,
                sort_data,
                convert_to_int,
                min_number_of_dominant_vector,
                max_number_of_weak_vector,
            )
        else:
            raise Exception(
                "Error: Must select either DLHC or DHC for clustering method"
            )

    return model


# Compute neurons for homogenous and heterogenous clusters
def get_neurons(
    X,
    y,
    final_homog,
    hetrog_clusters,
    centroid_calculation="robust",
    aif_method="max",
    dist_metric="L1",
    singleton_AIF=0,
    convert_to_int=True,
):

    stack_neurons = []

    for indM in final_homog:
        # get centroid
        homog_neuron = list(
            ca.compute_centroids(
                X[indM, :], centroid_calculation, dist_metric, convert_to_int
            )
        )
        homog_neuron.append(y[indM][0])  # append label to homog neuron
        homog_neuron.append(
            ca.get_aif(
                [homog_neuron[:-1]],
                [X[indM, :]],
                dist_metric,
                aif_method,
                singleton_AIF,
                convert_to_int,
            )[0]
        )  # appending AIF for homog cluster
        stack_neurons.append(homog_neuron)

    for indT in hetrog_clusters:
        hetrog_neuron = list(
            ca.compute_centroids(
                X[indT, :], centroid_calculation, dist_metric, convert_to_int
            )
        )
        hetrog_neuron.append(int(mode(y[indT])[0]))
        hetrog_neuron.append(
            ca.get_aif(
                [hetrog_neuron[:-1]],
                [X[indT, :]],
                dist_metric,
                aif_method,
                singleton_AIF,
                convert_to_int,
            )[0]
        )  # appending AIF for hetrog cluster
        stack_neurons.append(hetrog_neuron)

    return stack_neurons


# Compute output stack of models containing neurons, corresponding labels, and AIF. The last column indicates the number of neurons.


def get_cached_dataframe(cached):
    cached_frame = pd.DataFrame(list(cached.values())[0])
    cached_frame["num_neurons"] = list(cached.keys())[0]
    for key in list(cached.keys())[1:]:
        df = pd.DataFrame(cached[key])
        df["num_neurons"] = key
        cached_frame = pd.concat([cached_frame, df], axis=0)
    cached_frame.reset_index(drop=True)
    cached_frame.rename(columns={(np.shape(cached_frame)[1] - 2): "AIF"}, inplace=True)
    cached_frame.rename(
        columns={(np.shape(cached_frame)[1] - 3): "Label"}, inplace=True
    )

    cached_frame = cached_frame.sort_values(by=["num_neurons"]).reset_index(drop=True)

    return cached_frame


# Distance and label-based hierarchical clustering with caching


def dist_and_label_hierarch_clustering_with_caching(
    X,
    y,
    neuron_range,
    centroid_calculation,
    norm_order,
    aif_method,
    linkage_method,
    cluster_crit,
    dist_metric,
    singleton_aif,
    num_neurons_max,
    sort_data,
    convert_to_int,
    min_number_of_dominant_vector,
    max_number_of_weak_vector,
):

    cached_clusters = {}
    X, y, data_link = ca.calc_linkage_matrix(
        X, y, linkage_method, dist_metric, sort_data
    )

    final_homog = []

    nStart = neuron_range[0]
    nEnd = neuron_range[1]

    nD = nEnd
    n_hetro = 0
    n_homo = 0

    for loopIdx in range(len(data_link) - 1, -1, -1):  # Loop through the linkage matrix
        # Find homogenous and heterogenous clusters at a given level
        hetrog_clusters, final_homog, n_hetro, n_homo = ca.get_het_hom_clusters(
            y,
            loopIdx,
            data_link,
            cluster_crit,
            min_number_of_dominant_vector,
            max_number_of_weak_vector,
            final_homog=[],
        )

        # Cache the results only if the number of clusters (hetro + homo) is within a range
        if ((n_hetro + n_homo) >= nStart) & ((n_hetro + n_homo) <= nEnd):
            cached_clusters[n_hetro + n_homo] = get_neurons(
                X,
                y,
                final_homog,
                hetrog_clusters,
                centroid_calculation,
                aif_method,
                dist_metric,
                singleton_aif,
                convert_to_int,
            )

        nBudget = nD - (n_hetro + n_homo)  # Update the budget
        if nBudget == 0:
            break
        elif nBudget < 0:
            # If budget of desired num_neurons is exceeded at layer loopIdx, go back one step
            hetrog_clusters, final_homog, n_hetro, n_homo = ca.get_het_hom_clusters(
                y,
                loopIdx + 1,
                data_link,
                cluster_crit,
                min_number_of_dominant_vector,
                max_number_of_weak_vector,
                final_homog,
            )
            break

    all_covered = final_homog + hetrog_clusters  # Assemble all the clusters
    # Find any points that were not part of any cluster
    remainder = ca.get_remainder(y, all_covered)
    final_homog = ca.cluster_remaining_points(
        remainder, y, final_homog, ca.homog_check
    )  # Cluster those points

    if nEnd > (len(final_homog) + len(hetrog_clusters)):
        cached_clusters[len(final_homog) + len(hetrog_clusters)] = get_neurons(
            X,
            y,
            final_homog,
            hetrog_clusters,
            centroid_calculation,
            aif_method,
            norm_order,
            singleton_aif,
            convert_to_int,
        )
    model = get_cached_dataframe(
        cached_clusters
    )  # Convert the cached clusters into an output dataframe containing a stack of models

    return model


# Purely distance-based hierarchical clustering with caching
def dist_hierarch_clustering_with_caching(
    X,
    y,
    neuron_range,
    centroid_calculation,
    norm_order,
    aif_method,
    linkage_method,
    cluster_crit,
    dist_metric,
    singleton_aif,
    num_neurons_max,
    sort_data,
    convert_to_int,
):

    cached_clusters = {}
    X, y, data_link = ca.calc_linkage_matrix(
        X, y, linkage_method, dist_metric, sort_data
    )

    np.zeros(len(y))

    nStart = neuron_range[0]
    nEnd = neuron_range[1]

    nD = nEnd
    n_hetro = 0
    n_homo = 0

    for loopIdx in range(len(data_link) - 1, -1, -1):
        clusters = ca.get_clusters(loopIdx, data_link, criterion=cluster_crit)
        homog_clusters = ca.get_homog_clusters(clusters, y)
        hetrog_clusters = ca.get_hetrog_clusters(clusters, y)
        n_homo = len(homog_clusters)
        n_hetro = len(hetrog_clusters)

        if (len(clusters) >= nStart) & (len(clusters) <= nEnd):
            cached_clusters[len(clusters)] = get_neurons(
                X,
                y,
                homog_clusters,
                hetrog_clusters,
                centroid_calculation,
                aif_method,
                dist_metric,
                singleton_aif,
                convert_to_int,
            )

        nBudget = nD - (n_hetro + n_homo)
        if nBudget <= 0:
            break

    model = get_cached_dataframe(cached_clusters)

    return model
