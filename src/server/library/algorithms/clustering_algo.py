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

import copy

import numpy as np
import pandas as pd
from fastdtw import fastdtw
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import euclidean, pdist
from scipy.stats import mode


class ImproperCentroidMethodException(Exception):
    pass


class ImproperAIFMethodException(Exception):
    pass


##################################################
# Wrapper for clustering algorithm
# Inputs:
# X - dataframe containing feature matrix
# y - dataframe containing labels
# num_neurons - 0 (homogenity criterion), any positive value, or list containing min and max values (list option used only for neuron optimization)
# cluster_method - 'DLHC', 'DLC', or 'kmeans'
# centroid_calculation = 'robust', 'mean', or 'median'
# norm_order = '1', or 'np.inf'
# linkage_method = 'average', 'complete', or 'single'
# AIF_method = 'max', 'min', 'mean', or 'median'
# singleton_AIF = 0 or any positive value
# num_neurons_max = 128 or any positive value
# Outputs:
# Model containing neurons (feature vector, label, and AIF)


def call_clustering(
    X,
    y,
    num_neurons,
    cluster_method="kmeans",
    centroid_calculation="robust",
    distance_mode=0,
    linkage_method="average",
    aif_method="max",
    singleton_aif=0,
    num_neurons_max=128,
    sort_data=0,
    convert_to_int=True,
    min_number_of_dominant_vector=3,
    max_number_of_weak_vector=1,
    min_aif=2,
):

    if distance_mode == 0:
        distance_mode = "L1"
        norm_order = 1
    elif distance_mode == 1:
        distance_mode = "Lsup"
        norm_order = 2
    elif distance_mode == 2:
        distance_mode = "DTW"
        norm_order = 3
    else:
        assert "Err: Distance_mode values is not assigned"

    if y.size == 0 | X.size == 0:
        model = pd.DataFrame()

    elif y.size == 1:
        model = X
        model["Label"] = y
        model["AIF"] = singleton_aif

    elif (
        y.size <= num_neurons
    ):  # if demanded num_neurons is bigger than provided samples, each sample point will be its own centroid
        model = X
        model["Label"] = y
        model["AIF"] = [singleton_aif for x in range(y.size)]

    else:

        cluster_crit = "distance"
        # dist_metric='cityblock'

        if norm_order == 1:
            dist_metric = "cityblock"
        elif norm_order == 2:  # (norm_order == np.inf):
            dist_metric = "chebyshev"
        elif norm_order == 3:
            dist_metric = "DTW"

        if cluster_method == "DHC":
            model = dist_hierarch_clustering(
                X,
                y,
                num_neurons,
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
                min_aif,
            )

        elif cluster_method == "DLHC":
            model = dist_and_label_hierarch_clustering(
                X,
                y,
                num_neurons,
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
                min_aif,
            )

        elif cluster_method == "kmeans":
            model = k_means_clustering(
                X,
                y,
                num_neurons,
                norm_order,
                aif_method,
                singleton_aif,
                convert_to_int,
                dist_metric,
                min_aif,
            )

        else:
            raise ImproperCentroidMethodException(
                "Error: Must select proper clustering method"
            )

    return model


def compute_distance(vectors, dist_metric):
    if dist_metric == "DTW":
        distance = []
        for i in range(len(vectors) - 1):
            for j in range(i + 1, len(vectors)):
                temp_distance, path = fastdtw(vectors[i], vectors[j], dist=euclidean)
                distance.append(temp_distance)
        distance = np.array(distance)

    else:
        distance = pdist(vectors, dist_metric)

    return distance


def robust_average(data, dist_metric):
    data_median = np.median(data, axis=0)
    epsilon = 1

    if type(data_median.tolist()) != list:
        dist = [
            float(compute_distance([[x], [data_median]], dist_metric) + epsilon)
            for x in data
        ]
    else:
        dist = [
            float(compute_distance([x, data_median.tolist()], dist_metric) + epsilon)
            for x in data
        ]

    weights = np.divide(1.0, dist)
    weights = np.divide(weights, np.sum(weights))
    centroid = sum(w * x for (w, x) in zip(weights, data))

    return centroid


# Checks if all the items have the same value
def homog_check(items):
    return all([x == items[0] for x in items])


# Returns list of lists. Each list is a cluster.
def cluster_lists(T):
    # Returns list of lists. Each list is a cluster.
    clists = [[] for j in range(max(T) + 1)]
    for j, c in enumerate(T):
        clists[c].append(j)

    clists.sort(key=len, reverse=True)

    return clists[:-1]


# Inputs:
#   feature: feature vectors
#   method: centroid calculation method
#   dist_metric: distance norm
# Outputs:
#   centroids
def compute_centroids(feature, method, dist_metric, convert_to_int):

    if method == "robust":
        centroid = robust_average(feature, dist_metric)

    elif method == "mean":
        centroid = np.mean(feature, axis=0)

    elif method == "median":
        centroid = np.median(feature, axis=0)

    else:
        raise ImproperCentroidMethodException(
            "Centroid calculation technique must be robust, mean, or median."
        )

    if convert_to_int:
        centroid = centroid.astype(np.int64)

    return centroid


# Flattens list of lists. e.g., [[4,5], [2]] = [4,5,2]
def flatten_list(list_of_lists):

    flat_list = [k for sublist in list_of_lists for k in sublist]

    return flat_list


# Inputs:
#   y: array of labels
#   ListofLists: List of clusters
# Outputs:
#   Remainder: All the items that in y, that are not in List of clusters
def get_remainder(y, list_of_lists):

    remainder = [x for x in range(len(y)) if x not in flatten_list(list_of_lists)]

    return remainder


# Cluster remaining points into homogenous clusters
def cluster_remaining_points(remainder, y, final_homog, homog_check):

    if len(remainder) > 0:
        if homog_check(y[remainder]):
            final_homog.append(remainder)
        else:
            final_homog.append([remainder[0]])
            final_homog.append([remainder[1]])

    return final_homog


# Calculate centroid for a single cluster and add it to the list of centroids
def update_centroids(
    X, label, centroid_calculation, dist_metric, centroids, convert_to_int
):
    centroid = compute_centroids(X, centroid_calculation, dist_metric, convert_to_int)
    centroids.append(np.append(centroid, label))
    return centroids


def get_dist_from_neuron(centroid, samples, dist_metric, convert_to_int):
    dist_from_neuron = []
    for sample in samples:
        dist_from_neuron.append(compute_distance([centroid, sample], dist_metric)[0])

    if convert_to_int:
        dist_from_neuron = [x.astype(np.int64) for x in dist_from_neuron]

    return dist_from_neuron


def calc_aif(dist_from_neuron, aif_method, singleton_aif, dist_metric, convert_to_int):

    if aif_method == "max":
        if convert_to_int:
            aif_value = np.max(dist_from_neuron) + 1
        else:
            aif_value = np.max(dist_from_neuron)

    elif aif_method == "min":
        aif_value = np.min(dist_from_neuron) + 1

    elif aif_method == "robust":
        aif_value = robust_average(np.array(dist_from_neuron), dist_metric)

    elif aif_method == "median":
        aif_value = np.median(dist_from_neuron, axis=0)

    elif aif_method == "mean":
        aif_value = np.mean(dist_from_neuron, axis=0)
    else:
        raise ImproperAIFMethodException(
            "AIF computation technique must be max, min, robust, median, or mean."
        )

    if convert_to_int:
        aif_value = aif_value.astype(np.int32)  # convert AIF into int
    if aif_value < 1e-6:
        aif_value = singleton_aif

    return aif_value


def get_aif(
    centroids,
    samples,
    dist_metric,
    aif_method,
    singleton_aif,
    convert_to_int,
    norm_order=1,
):
    centroids = np.array(centroids)
    aif = []
    for i in range(len(centroids)):
        dist_from_neuron = get_dist_from_neuron(
            centroids[i], samples[i], dist_metric, convert_to_int
        )
        aif.append(
            calc_aif(
                dist_from_neuron, aif_method, singleton_aif, dist_metric, convert_to_int
            )
        )

    return aif


# Calculates clusters from the linkage matrix
# Inputs:
#   linkageIdx: index into linkage matrix
#   data_link:  linkage matrix
#   criterion: 'distance'
# Outputs:
#   clusters: list of lists
def get_clusters(linkageIdx, data_link, criterion):
    thr = data_link[linkageIdx, 2] - 0.001  # -thr_min
    # Forms flat clusters from the hierarchical clustering defined by the linkage matrix
    T = fcluster(data_link, thr, criterion)
    # Returns list of lists. Each list is a cluster.
    clusters = cluster_lists(T)
    return clusters


# Find the clusters in which all the objects have the same label
def get_homog_clusters(clusters, y):

    homog_clusters = [
        clusters[k] for k in range(len(clusters)) if homog_check(y[clusters[k]])
    ]

    return homog_clusters


# Find the clusters which contains objects belonging to 2 or more classes
def get_hetrog_clusters(clusters, y):

    hetrog_clusters = [
        clusters[k] for k in range(len(clusters)) if (not homog_check(y[clusters[k]]))
    ]

    return hetrog_clusters


def pruning_func(clusters, y, min_number_of_dominant_vector, max_number_of_weak_vector):

    for cluster in clusters:
        label_list = np.unique(y[cluster])
        max_cnt = 0
        min_cnt = 1e6
        label_count = []
        for label_indx in label_list:
            label_count.append(np.count_nonzero(y[cluster] == label_indx))
            if label_count[-1] < min_cnt:
                min_cnt = label_count[-1]
                min_val_label = label_indx

            if label_count[-1] > max_cnt:
                max_cnt = label_count[-1]
                max_val_label = label_indx

        if (
            (len(label_count) == 2)
            and (
                (min(label_count) > 0)
                and (min(label_count) <= max_number_of_weak_vector)
            )
            and (max(label_count) >= min_number_of_dominant_vector)
        ):  # (np.unique(label_count) == 2)

            swap_val = max_val_label
            swap_index = np.array(cluster)[np.where(y[cluster] == min_val_label)]
            y[swap_index] = swap_val

    return y


# Find homogenous and heterogenous clusters
# Inputs:
#    y: array of labels
#    linkageIdx: index into linkage matrix
#    data_link: linkage matrix
#    cluster_crit: 'distance'
#    final_homog: list of homogenous clusters
# Outputs:
#    hetrog_clusters: list of heterogenous clusters
#    final_homog: list of homogenous clusters
#    nHetro: number of heterogenous clusters
#    nHomo: number of homogenous clusters


def get_het_hom_clusters(
    y,
    linkageIdx,
    data_link,
    cluster_crit,
    min_number_of_dominant_vector,
    max_number_of_weak_vector,
    final_homog=[],
):

    # Calculates clusters from the linkage matrix
    clusters = get_clusters(linkageIdx, data_link, cluster_crit)
    ############## here new optimization will be placed  ##############
    y = pruning_func(
        clusters, y, min_number_of_dominant_vector, max_number_of_weak_vector
    )

    # Find the clusters in which all the objects have the same label
    homog_clusters = get_homog_clusters(clusters, y)
    hetrog_clusters = get_hetrog_clusters(clusters, y)
    n_hetro = len(hetrog_clusters)

    for l in homog_clusters:
        if len(set(l).intersection(set(flatten_list(final_homog)))) == 0:
            final_homog.append(l)

    n_homo = len(final_homog)

    return (hetrog_clusters, final_homog, n_hetro, n_homo)


# This function will take a pandas dataframe as input and produce an 2d numpy array without duplicates
def drop_duplicate_feature_vectors(X, y):

    X.columns = range(0, np.shape(X)[1])
    X.reset_index(drop=True, inplace=True)
    Xlist = X.values.tolist()
    X = [
        [float(Xlist[i][k]) for k in range(np.shape(Xlist)[1])]
        for i in range(np.shape(Xlist)[0])
    ]
    X = pd.DataFrame(X)
    ind_dup = np.where([X.apply(np.round, args=[2]).duplicated()])[1]
    ind_nondup = np.where([~X.apply(np.round, args=[2]).duplicated()])[1]
    X = np.array(X)

    y.reset_index(drop=True, inplace=True)
    y = np.array(y)
    y = [float(y[i]) for i in range(len(y))]

    y = np.array(y)
    if len(ind_dup) > 0:

        X = X[ind_nondup]
        y = np.delete(y, ind_dup)

    X = np.array(X)
    y = np.array(y)

    return (X, y)


def calc_linkage_matrix(X, y, linkage_method, dist_metric, sort_data):

    if sort_data:
        if X.shape[1] > 1:

            data = pd.concat([X, y], axis=1)
            sorted_data = data.sort_values(by=list(data.columns)).reset_index(drop=True)

            X = sorted_data.iloc[:, :-1]
            y = sorted_data.iloc[:, -1]

    X = np.array(X)
    y = np.array(y)

    # Computing **unique** el-1 distances using pdist function, this will return an **array** (not matrix) of length N-choose-2 for the NxM matrix
    distances = compute_distance(X, dist_metric)
    data_link = linkage(
        distances, method=linkage_method, metric=dist_metric
    )  # Computing 4x(N-1) Linkage matrix which "agglomeratively" merges objects at different el-1 norm distance values

    return (X, y, data_link)


def hcluster_wrapper(
    final_homog,
    X,
    y,
    centroid_calculation,
    convert_to_int,
    dist_metric,
    removed_item_list,
    ref_final_homog,
    min_aif,
    aif_method,
    singleton_aif,
    norm_order,
    hetrog_clusters,
    hetrog_clusters_flag=False,
    model_flag=False,
):

    list_flag = False
    for rm_vec in np.unique(removed_item_list).tolist():
        if rm_vec in final_homog:
            final_homog.remove(rm_vec)
            list_flag = True

    if list_flag:
        removed_item_list = np.unique(removed_item_list).tolist()

    if (final_homog != ref_final_homog) or hetrog_clusters_flag or model_flag:
        centroids = []
        samples = []

        # run this part if final_homog is changed
        for indM in final_homog:  # diff_final_list: #final_homog:
            centroids = update_centroids(
                X[indM, :],
                y[indM][0],
                centroid_calculation,
                dist_metric,
                centroids,
                convert_to_int,
            )

            samples.append(X[indM, :])

        if hetrog_clusters_flag or model_flag:
            for indT in hetrog_clusters:
                centroids = update_centroids(
                    X[indT, :],
                    mode(y[indT])[0],
                    centroid_calculation,
                    dist_metric,
                    centroids,
                    convert_to_int,
                )

                samples.append(X[indT, :])

        out_centroids = pd.DataFrame(centroids).iloc[:, :-1]
        out_labels = pd.DataFrame(centroids).iloc[:, -1]
        aif = get_aif(
            out_centroids,
            samples,
            dist_metric,
            aif_method,
            singleton_aif,
            convert_to_int,
            norm_order,
        )

        # Put the output model together
        temp_model = out_centroids
        temp_model["Label"] = out_labels
        temp_model["AIF"] = aif

        temp_model = temp_model.drop_duplicates()

        if norm_order == 1:
            norm = "L1"
        elif norm_order == 2:
            norm = "Lsup"
        elif norm_order == 3:
            norm = "DTW"

        if model_flag:
            temp_model = temp_model[temp_model["AIF"] >= min_aif]
            # Optimization
            mo = model_optimization(temp_model, norm, min_aif)
            temp_model, _, _ = mo.optimize_model()
            nan_index = temp_model[pd.isnull(temp_model["AIF"])].index.tolist()

            if nan_index:
                temp_model = temp_model.drop(nan_index)

            temp_model = temp_model.reset_index(drop=True)
            return temp_model

        min_aif_indx = temp_model[temp_model["AIF"] < min_aif].index.tolist()
        temp_model = temp_model[temp_model["AIF"] >= min_aif]

        # Optimization
        mo = model_optimization(temp_model, norm, min_aif)
        temp_model, removed_item_list_indx, _ = mo.optimize_model()

        if (len(removed_item_list_indx) + len(min_aif_indx)) > 0:
            removed_item_list_indx = removed_item_list_indx + min_aif_indx
            temp_final_homog = []
            for i in range(len(final_homog)):
                if i not in removed_item_list_indx:  # [0] + min_aif_indx :
                    temp_final_homog.append(final_homog[i])
                else:
                    removed_item_list.append(final_homog[i])

            final_homog = temp_final_homog

    ref_final_homog = copy.copy(final_homog)

    return final_homog, removed_item_list, ref_final_homog


# Distance and label-based hierarchical clustering
def dist_and_label_hierarch_clustering(
    X,
    y,
    num_neurons,
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
    min_aif=2,
):

    X, y, data_link = calc_linkage_matrix(X, y, linkage_method, dist_metric, sort_data)

    final_homog = []
    centroids = []
    samples = []
    removed_item_list = []
    ref_final_homog = []
    hetrog_clusters = []

    model = pd.DataFrame()

    if homog_check(y):  # Bypassing clustering if all samples have the same label
        centroids = update_centroids(
            X, y[0], centroid_calculation, dist_metric, centroids, convert_to_int
        )
        samples.append(X)

        out_centroids = pd.DataFrame(centroids).iloc[:, :-1]
        out_labels = pd.DataFrame(centroids).iloc[:, -1]

        aif = get_aif(
            out_centroids,
            samples,
            dist_metric,
            aif_method,
            singleton_aif,
            convert_to_int,
            norm_order,
        )

        # Put the output model together
        model = out_centroids
        model["Label"] = out_labels
        model["AIF"] = aif

    elif num_neurons == 0:
        # Default case of running clustering until all clusters are homogeneous
        # therefore min_aif will not be evaluated

        for i in range(len(data_link) - 1, -1, -1):
            clusters = get_clusters(i, data_link, criterion=cluster_crit)
            homog_clusters = get_homog_clusters(clusters, y)

            for l in homog_clusters:
                if len(set(l).intersection(set(flatten_list(final_homog)))) == 0:
                    final_homog.append(l)

        remainder = get_remainder(y, final_homog)
        final_homog = cluster_remaining_points(remainder, y, final_homog, homog_check)

        for ind in final_homog:
            centroids = update_centroids(
                X[ind, :],
                y[ind][0],
                centroid_calculation,
                dist_metric,
                centroids,
                convert_to_int,
            )
            samples.append(X[ind, :])

        out_centroids = pd.DataFrame(centroids).iloc[:, :-1]
        out_labels = pd.DataFrame(centroids).iloc[:, -1]

        aif = get_aif(
            out_centroids,
            samples,
            dist_metric,
            aif_method,
            singleton_aif,
            convert_to_int,
            norm_order,
        )

        # Put the output model together
        model = out_centroids
        model["Label"] = out_labels
        model["AIF"] = aif

    elif num_neurons == 1:
        centroids = update_centroids(
            X, mode(y)[0], centroid_calculation, dist_metric, centroids, convert_to_int
        )
        samples.append(X)
        out_centroids = pd.DataFrame(centroids).iloc[:, :-1]
        out_labels = pd.DataFrame(centroids).iloc[:, -1]

        aif = get_aif(
            out_centroids,
            samples,
            dist_metric,
            aif_method,
            singleton_aif,
            convert_to_int,
            norm_order,
        )

        # Put the output model together
        model = out_centroids
        model["Label"] = out_labels
        model["AIF"] = aif

    elif num_neurons > 1:
        nD = num_neurons
        for loopIdx in range(len(data_link) - 1, -1, -1):

            hetrog_clusters, final_homog, nHetro, nHomo = get_het_hom_clusters(
                y,
                loopIdx,
                data_link,
                cluster_crit,
                min_number_of_dominant_vector,
                max_number_of_weak_vector,
                final_homog,
            )

            final_homog, removed_item_list, ref_final_homog = hcluster_wrapper(
                final_homog,
                X,
                y,
                centroid_calculation,
                convert_to_int,
                dist_metric,
                removed_item_list,
                ref_final_homog,
                min_aif,
                aif_method,
                singleton_aif,
                norm_order,
                hetrog_clusters,
            )

            nHetro = len(hetrog_clusters)
            nHomo = len(final_homog)

            nBudget = nD - (nHetro + nHomo)

            if nBudget == 0:
                break
            elif nBudget < 0:
                step_index = 1
                while nBudget < 0 and (loopIdx + step_index < data_link.shape[0]):
                    # # If budget of desired num_neurons is exceeded at layer loopIdx, go back as many steps as needed
                    hetrog_clusters, final_homog, nHetro, nHomo = get_het_hom_clusters(
                        y,
                        loopIdx + step_index,
                        data_link,
                        cluster_crit,
                        min_number_of_dominant_vector,
                        max_number_of_weak_vector,
                        final_homog,
                    )

                    final_homog, removed_item_list, ref_final_homog = hcluster_wrapper(
                        final_homog,
                        X,
                        y,
                        centroid_calculation,
                        convert_to_int,
                        dist_metric,
                        removed_item_list,
                        ref_final_homog,
                        min_aif,
                        aif_method,
                        singleton_aif,
                        norm_order,
                        hetrog_clusters,
                    )

                    nHetro = len(hetrog_clusters)
                    nHomo = len(final_homog)

                    nBudget = nD - (nHetro + nHomo)
                    step_index += 1

                break

        # add one last puruning here ---------------------------------
        all_covered = final_homog + hetrog_clusters
        # get_remainder: if index of y and all_covered does not match
        remainder = get_remainder(y, all_covered)
        final_homog = cluster_remaining_points(remainder, y, final_homog, homog_check)
        # If nBudget < 0 condition holds, that may cause unchecked neurons. Therefore, purify one more time
        final_homog, removed_item_list, ref_final_homog = hcluster_wrapper(
            final_homog,
            X,
            y,
            centroid_calculation,
            convert_to_int,
            dist_metric,
            removed_item_list,
            ref_final_homog,
            min_aif,
            aif_method,
            singleton_aif,
            norm_order,
            hetrog_clusters,
            hetrog_clusters_flag=True,
        )

        # final purifying .....
        model = hcluster_wrapper(
            final_homog,
            X,
            y,
            centroid_calculation,
            convert_to_int,
            dist_metric,
            removed_item_list,
            ref_final_homog,
            min_aif,
            aif_method,
            singleton_aif,
            norm_order,
            hetrog_clusters,
            model_flag=True,
        )

    return model


# Purely distance-based hierarchical clustering
def dist_hierarch_clustering(
    X,
    y,
    num_neurons,
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
    min_aif=2,
):

    X, y, data_link = calc_linkage_matrix(X, y, linkage_method, dist_metric, sort_data)

    final_homog = []
    centroids = []
    samples = []
    model = pd.DataFrame()

    if homog_check(y):  # Bypassing clustering if all samples have the same label
        centroids = update_centroids(
            X, y[0], centroid_calculation, dist_metric, centroids, convert_to_int
        )
        samples.append(X)
    elif (
        num_neurons == 0
    ):  # Default case of running clustering until all clusters are homogeneous
        for i in range(len(data_link) - 1, -1, -1):
            clusters = get_clusters(i, data_link, criterion=cluster_crit)
            homog_clusters = get_homog_clusters(clusters, y)
            if len(homog_clusters) == len(clusters):
                final_homog = homog_clusters
                break

        for ind in final_homog:
            centroids = update_centroids(
                X[ind, :],
                y[ind][0],
                centroid_calculation,
                dist_metric,
                centroids,
                convert_to_int,
            )
            samples.append(X[ind, :])

    elif num_neurons == 1:
        centroids = update_centroids(
            X, mode(y)[0], centroid_calculation, dist_metric, centroids, convert_to_int
        )
        samples.append(X)

    elif num_neurons > 1:
        nD = num_neurons
        for loopIdx in range(len(data_link) - 1, -1, -1):
            clusters = get_clusters(loopIdx, data_link, criterion=cluster_crit)
            if len(clusters) == nD:
                homog_clusters = get_homog_clusters(clusters, y)
                hetrog_clusters = get_hetrog_clusters(clusters, y)
                break
            elif len(clusters) > nD:
                step_index = 1
                while len(clusters) - nD > 0 and (
                    loopIdx + step_index < data_link.shape[0]
                ):
                    # If budget of desired num_neurons is exceeded at layer loopIdx, go back as many steps as needed
                    clusters = get_clusters(
                        loopIdx + step_index, data_link, criterion=cluster_crit
                    )
                    homog_clusters = get_homog_clusters(clusters, y)
                    hetrog_clusters = get_hetrog_clusters(clusters, y)
                    step_index += 1
                break

        for indM in homog_clusters:
            centroids = update_centroids(
                X[indM, :],
                y[indM][0],
                centroid_calculation,
                dist_metric,
                centroids,
                convert_to_int,
            )
            samples.append(X[indM, :])

        for indT in hetrog_clusters:
            centroids = update_centroids(
                X[indT, :],
                mode(y[indT])[0],
                centroid_calculation,
                dist_metric,
                centroids,
                convert_to_int,
            )
            samples.append(X[indT, :])

    else:
        return model

    out_centroids = pd.DataFrame(centroids).iloc[:, :-1]
    out_labels = pd.DataFrame(centroids).iloc[:, -1]

    aif = get_aif(
        out_centroids,
        samples,
        dist_metric,
        aif_method,
        singleton_aif,
        convert_to_int,
        norm_order,
    )

    model = out_centroids
    model["Label"] = out_labels
    model["AIF"] = aif

    if norm_order == 1:
        norm = "L1"
    elif norm_order == 2:
        norm = "Lsup"
    elif norm_order == 3:
        norm = "DTW"

    # Optimization
    if num_neurons > 1:
        model = model[model["AIF"] >= min_aif]

    mo = model_optimization(model, norm, min_aif)
    model, removed_item_list_indx, _ = mo.optimize_model()
    model = model.reset_index(drop=True)

    return model


# Computes labels only for k-means clustering
def get_centroid_labels(y, clusters):
    return [int(mode(y[clusters[i]])[0]) for i in range(len(clusters))]


# k-means clustering
def k_means_clustering(
    X,
    y,
    num_neurons,
    norm_order,
    aif_method,
    singleton_aif,
    convert_to_int,
    dist_metric,
    min_aif=2,
):
    from sklearn.cluster import KMeans

    X = np.array(X).astype(int)
    y = np.array(y).astype(int)

    if num_neurons == 0:
        # Default case of running clustering until all clusters are homogeneous
        min_aif = 1
        k_means = KMeans(
            n_clusters=128,
            init="k-means++",
            max_iter=100,
            n_init=1,
            verbose=0,
            random_state=0,
        )
    else:
        k_means = KMeans(
            n_clusters=num_neurons,
            init="k-means++",
            max_iter=100,
            n_init=1,
            verbose=0,
            random_state=0,
        )

    k_means.fit(X)
    # centroids = k_means.cluster_centers_
    cluster_indices = k_means.labels_
    # add 1 to adjust 0 offset of labels
    clusters = cluster_lists(1 + cluster_indices)
    clusters = [
        x for x in clusters if x != []
    ]  # to protect against empty lists since kmr sometimes gives inconsistent cluster indices
    samples = [X[clusters[k]] for k in range(len(clusters))]
    centroid_labels = get_centroid_labels(y, clusters)

    # since index of k_means.cluster_centers_ is not assigned, re-compute centers
    centroids = [np.mean(samples[i], axis=0).tolist() for i in range(len(samples))]

    aif = get_aif(
        pd.DataFrame(centroids),
        samples,
        dist_metric,
        aif_method,
        singleton_aif,
        convert_to_int,
        norm_order,
    )

    model = pd.DataFrame(centroids)
    model["Label"] = centroid_labels
    model["AIF"] = aif

    if norm_order == 1:
        norm = "L1"
    elif norm_order == 2:
        norm = "Lsup"
    elif norm_order == 3:
        norm = "DTW"

    # Optimization
    model = model[model["AIF"] >= min_aif]
    mo = model_optimization(model, norm, min_aif)
    model, removed_item_list_indx, _ = mo.optimize_model()
    model = model.reset_index(drop=True)

    return model


class model_optimization:
    def __init__(self, df_model, norm, min_aif):
        self.df_model = df_model
        self.norm = norm
        self.min_aif = min_aif

        if norm == "L1":
            self.dist_metric = "cityblock"
        elif norm == "Lsup":
            self.dist_metric = "chebyshev"
        elif norm == "DTW":
            self.dist_metric = "DTW"
        else:
            raise Exception("Err: Distance norm is not defined!!!!")

    def _find_nested_neurons(self):
        df_model = self.df_model
        self.feature_labels = df_model.columns[:-2]

        df_nested = pd.DataFrame([], columns=["orj_index", "same_label", "diff_label"])
        self.label_indx_list = df_model.index

        for pv_indx in self.label_indx_list:

            pv_vector = df_model.loc[pv_indx, self.feature_labels].tolist()
            pv_AIF = df_model.loc[pv_indx, "AIF"]
            pv_label = df_model.loc[pv_indx, "Label"]

            same_label = []
            diff_label = []
            temp_label_indx_list = self.label_indx_list.drop(pv_indx)

            for indx in temp_label_indx_list:
                temp_vector = df_model.loc[indx, self.feature_labels].tolist()
                temp_AIF = df_model.loc[indx, "AIF"]
                temp_label = df_model.loc[indx, "Label"]

                # if nested_bool is True: temp_vector is in pv_vector
                nested_bool = (
                    compute_distance([pv_vector, temp_vector], self.dist_metric)[0]
                    + temp_AIF
                    <= pv_AIF
                )

                if nested_bool:
                    if pv_label == temp_label:
                        same_label.append(indx)
                    else:
                        diff_label.append(indx)

            if (same_label != []) or (diff_label != []):
                df_nested.loc[len(df_nested)] = [pv_indx, same_label, diff_label]

        return df_nested

    def _clean_df_model(self, df_nested, itr_num):
        label_indx_list = self.label_indx_list
        removed_item_list_indx = []

        for nest_indx in df_nested.index:

            if (df_nested.loc[nest_indx, "same_label"] != []) & (
                df_nested.loc[nest_indx, "diff_label"] == []
            ):
                # if If pivot neuron has only list_1 then Remove all nested neurons in the pv_neuron
                remove_labels = [
                    item_label
                    for item_label in df_nested.loc[nest_indx, "same_label"]
                    if item_label in label_indx_list
                ]
                if remove_labels:
                    label_indx_list = label_indx_list.drop(remove_labels)

                    for item_label in remove_labels:
                        if item_label not in removed_item_list_indx:
                            removed_item_list_indx.append(item_label)

            else:
                # If pivot neuron has only list_1 and/or list_2
                # 	- Resize pv_neuron
                # 	- revisit neurons in list_1
                # 		- If they are still nested neuron then remove them from the dataframe

                pv_indx = df_nested.loc[nest_indx, "orj_index"]
                diff_indx = df_nested.loc[nest_indx, "diff_label"]

                if pv_indx in self.df_model.index:
                    pv_vector = self.df_model.loc[pv_indx, self.feature_labels].tolist()
                else:
                    pv_indx = self.df_model.index[0]

                temp_vector = [
                    self.df_model.loc[temp_indx, self.feature_labels].tolist()
                    for temp_indx in diff_indx
                    if temp_indx in self.df_model.index
                ]

                if temp_vector:
                    # new aif for pv_neuron
                    self.df_model.loc[pv_indx, "AIF"] = min(
                        [
                            compute_distance([pv_vector, vec], self.dist_metric)
                            for vec in temp_vector
                        ]
                    )[0]

                self.df_model = self.df_model[self.df_model["AIF"] >= self.min_aif]
                # avoid to reach max recursion
                itr_num = itr_num + 1
                if itr_num <= 8:
                    mo = model_optimization(self.df_model, self.norm, self.min_aif)
                    self.df_model, removed_item_list_indx, itr_num = mo.optimize_model(
                        itr_num
                    )

                    for item in removed_item_list_indx:
                        if item in label_indx_list:
                            label_indx_list = label_indx_list.drop(item)

        return self.df_model.loc[label_indx_list], removed_item_list_indx, itr_num

    def optimize_model(self, itr_num=0):
        df_nested = self._find_nested_neurons()
        clean_df_model, removed_item_list_indx, itr_num = self._clean_df_model(
            df_nested, itr_num
        )
        clean_df_model = clean_df_model.dropna()
        return clean_df_model, removed_item_list_indx, itr_num
