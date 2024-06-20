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


def compute_information_gain(
    key, vector_groups_based_on_labels, all_class, min_max_dict, total_points, features
):

    # number of key feature values in key features(min/max) boundaries
    true_points_in_key = len(vector_groups_based_on_labels.get_group(key))

    # entropy(parent)
    tr_val = true_points_in_key / total_points
    rst_val = (total_points - true_points_in_key) / total_points
    parent_entropy = -tr_val * np.log(tr_val) - rst_val * np.log(rst_val)

    target_keys = list(set(all_class) - set([key]))

    key_means = vector_groups_based_on_labels.get_group(key)[features].mean()

    # this will be used for sorting the features
    distance_df_list = [
        abs(
            key_means
            - vector_groups_based_on_labels.get_group(key_target)[features].mean()
        )
        for key_target in target_keys
    ]
    median_difference = pd.concat(distance_df_list, axis=1).T.median()

    target_vectors = pd.concat(
        [
            vector_groups_based_on_labels.get_group(key_target)
            for key_target in target_keys
        ]
    )[features]

    # number of false feature values in key features boundaries
    false_point_in_key = (
        (target_vectors >= min_max_dict[key][0])
        & (target_vectors <= min_max_dict[key][1])
    ).sum()

    # total number of features in key features boundaries
    total_point_in_key = true_points_in_key + false_point_in_key

    # TODO: Check for divide by zero error which shows up in logs
    part_1 = (
        -1
        * (true_points_in_key / total_point_in_key)
        * np.log(true_points_in_key / total_point_in_key)
    )

    part_2 = (
        -1
        * (false_point_in_key / total_point_in_key)
        * np.log(false_point_in_key / total_point_in_key)
    ).fillna(0)

    child_1_entropy = part_1 / part_2
    child_1_entropy = child_1_entropy.fillna(0)

    average_entropy_children = (total_point_in_key / total_points) * child_1_entropy

    information_gain = parent_entropy - average_entropy_children
    results = pd.concat(
        [min_max_dict[key], median_difference, information_gain], axis=1, sort=False
    )

    results.columns = ["min_val", "max_val", "Std", "Dist", "IG_target_sensor"]

    return results.sort_values(
        by=["IG_target_sensor", "Std", "Dist"], ascending=[False, True, False]
    )


def sort_sensors(df_selected_features, list_of_labels, feature_number):
    feature_list = []
    df_sorted_list = []

    for label in list_of_labels:
        df = df_selected_features[label]
        df_sorted_list.append(df)
        feature_list.extend(df[:feature_number].index.tolist())

    return list(np.unique(feature_list)), df_sorted_list


def feature_selector_with_information_gain(
    input_data, label_column, feature_number, ignore_col=None, return_score_list=None
):
    """
    This is a supervised feature selection algorithm that selects features based on Information Gain (one class vs other
    classes approaches).

    First, it calculates Information Gain (IG) for each class separately to all features then sort features based on IG
    scores, std, and mean differences. Feature with higher IG is better feature to differentiate the class from others. At the end, each feature
    has their own feature list.

    Args:
            input_data: DataFrame, it holds input data
            label_column: Name of the label column
            feature_number: Number of features will be selected for each class.

    Return:
        DataFrame: DataFrame which includes selected features and the passthrough columns.

    """

    # Compute some statistics that will be used for IG
    features = [i for i in input_data.columns if "gen_" in i]
    vector_groups_based_on_labels = input_data.groupby(label_column)
    total_points = len(input_data)
    list_of_labels = input_data[label_column].unique()

    min_max_dict = {}
    for key in list_of_labels:
        min_max_dict[key] = pd.concat(
            [
                vector_groups_based_on_labels.get_group(key)[features].min(),
                vector_groups_based_on_labels.get_group(key)[features].max(),
                vector_groups_based_on_labels.get_group(key)[features].std(),
            ],
            axis=1,
        )

    # Compute IG for each class
    df_selected_features = {}
    for key in list_of_labels:
        df_selected_features[key] = compute_information_gain(
            key,
            vector_groups_based_on_labels,
            list_of_labels,
            min_max_dict,
            total_points,
            features,
        )

    # Sort features for each class based on given the given target_sensor_weight
    feature_list, df_sorted = sort_sensors(
        df_selected_features, list_of_labels, feature_number
    )

    # return score table if it is requested. i.e: Autogroup requests this data
    if return_score_list:
        return df_sorted

    return_col = ignore_col + feature_list
    return_col[return_col.index(label_column)] = label_column
    return return_col
