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

"""
These functions are initial submission of vector filtering and vector separation.
"""

import random

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform


def create_random_conf(df, config_num, group_columns, label_column):
    """
    dim = #features
    -------------------------------------------------------------------------------------------------------------------
    outlier_boundry  ==> (dim/2) * (8 < outlier_boundry < 128)    ==> (dim/2) * range(8, 128)
    frame_AIF        ==> (dim/2) *3 < frame_AIF < outlier_boundry ==> range((dim/2) *3, outlier_boundry)
    -------------------------------------------------------------------------------------------------------------------
    large_nv         ==> #vectors / #features     ==> range(3, #vectors / #label)
    medium_nv        ==> 2 < medium_nv < large_nv ==> range(2, large_nv)
    small_nv         ==> 1 < small_nv < medium_nv ==> range(1, medium_nv)
    """

    dim = len(set(df.columns) - set(group_columns))
    config_list = []

    for i in range(config_num):
        norm = random.choice(["Lsup", "L1"])
        outlier_boundry = (dim / 2) * random.choice(range(8, 128))
        frame_AIF = random.choice(range((dim / 2) * 3, outlier_boundry))

        large_nv = random.choice(range(3, (len(df) / len(np.unique(df[label_column])))))
        medium_nv = random.choice(range(2, large_nv))
        small_nv = random.choice(range(1, medium_nv))
        config = {
            "norm": norm,
            "frame_AIF": frame_AIF,
            "outlier_boundry": outlier_boundry,
            "small_nv": small_nv,
            "medium_nv": medium_nv,
            "large_nv": large_nv,
        }

        config_list.append(config)

    return config_list


def meta_data(train_set, label_column):
    """
    :param train_set:
    :return: meta data for train_set
    """
    index = [np.unique(train_set[label_column]).tolist()][0]
    index.append("quality")
    columns = ["vector", "core", "border", "noise", "outlier", "edge"]
    summary_table = pd.DataFrame([], index=index, columns=columns)

    for i in np.unique(train_set[label_column]):
        temp_df = train_set[train_set[label_column] == i]
        temp = []
        temp.append(len(temp_df))
        for seg in columns[1:]:
            temp.append(
                str((temp_df["Segregate"] == seg).sum())
                + "("
                + str(100 * (temp_df["Segregate"] == seg).sum() / temp[0])
                + "%)"
            )
        summary_table.loc[i] = temp

    # quality of the train_set
    temp = []
    temp.append(len(train_set))
    for seg in columns[1:]:
        temp.append(
            str((train_set["Segregate"] == seg).sum())
            + "("
            + str(100 * (train_set["Segregate"] == seg).sum() / temp[0])
            + "%)"
        )
    summary_table.loc["quality"] = temp
    return summary_table


def set_supset(train_set, segregate_list):
    new_train_set_indx = []
    for label_indx in segregate_list:
        temp_indx = train_set[train_set["Segregate"] == label_indx].index.tolist()
        new_train_set_indx = new_train_set_indx + temp_indx

    return train_set.loc[new_train_set_indx]


def create_dist_df(norm, train_set, group_columns):
    if norm == "L1":
        dist_metric = "cityblock"
    elif norm == "Lsup":
        dist_metric = "chebyshev"

    vector_col = list(set(train_set.columns) - set(group_columns))
    train_set_list = np.array(train_set[vector_col])
    train_set_indx = train_set[vector_col].index

    dist_list = pdist(train_set_list, dist_metric)
    dist_df = pd.DataFrame(
        squareform(dist_list), index=train_set_indx, columns=train_set_indx
    )
    return dist_df


def find_category_of_the_vector(dist_df, config, train_set, label_column, indx):
    """
    # ==============================================================================
    #                               DEFINITIONS
    # ==============================================================================
    #              Conditions                Operator  Parameter   C  O  N  B
    # (# vectors of same category < CLOSE)       >       LARGE     T  -  -  -
    # (# vectors of same category < CLOSE)       <       SMALL     -  -  T  -
    # (# vectors of different category < CLOSE)  <=      SMALL     T  -  -  -
    # (# vectors of different category < CLOSE)  >       LARGE     -  -  T  -
    # (# vectors of different category < CLOSE)  >       MEDIUM    -  -  -  T
    # (# vectors of same category < CLOSE)       >       MEDIUM    -  -  -  T
    # (# vectors of any category < Far)          <       SMALL     -  T  -  -
    # ==============================================================================
    """

    # find all vectors in the CLOSE
    index_of_vectors_in_CLOSE = dist_df[dist_df[indx] < config["frame_AIF"]].index
    index_of_vectors_in_CLOSE = list(set(index_of_vectors_in_CLOSE) - set([indx]))

    # label of pivot vector
    pv_label = train_set.loc[indx, label_column]
    # number_of_vectors_in_same_category
    nm_vsc = (
        train_set.loc[index_of_vectors_in_CLOSE, label_column].tolist().count(pv_label)
    )
    # number_of_vectors_in_different_category
    nm_vdc = len(index_of_vectors_in_CLOSE) - nm_vsc

    # order of the next 4 if conditions is important, DON'T change it
    if (nm_vsc > config["large_nv"]) & (nm_vdc <= config["small_nv"]):
        return "core"

    # large_nv is replaced with medium_nv
    elif (nm_vsc < config["small_nv"]) & (nm_vdc > config["medium_nv"]):
        return "noise"

    elif (nm_vsc > config["medium_nv"]) & (nm_vdc > config["medium_nv"]):
        return "border"

    elif (len(dist_df[dist_df[indx] < config["outlier_boundry"]]) - 1) <= config[
        "small_nv"
    ]:
        return "outlier"

    else:
        return "edge"


def create_set_of_config(train_set, config_num, group_columns, label_column):
    config_list = create_random_conf(train_set, config_num, group_columns, label_column)
    df_results = pd.DataFrame(
        [], columns=["core", "border", "noise", "outlier", "edge", "config"]
    )  # ,'used_vector(%)'
    dist_df_Lsup = create_dist_df("Lsup", train_set, group_columns)
    dist_df_L1 = create_dist_df("L1", train_set, group_columns)

    for config in config_list:
        if config["norm"] == "Lsup":
            dist_df = dist_df_Lsup
        elif config["norm"] == "L1":
            dist_df = dist_df_L1
        else:
            raise Exception("Invalid Configuration for norm")

        train_set["Segregate"] = [
            find_category_of_the_vector(dist_df, config, train_set, label_column, i)
            for i in train_set.index
        ]
        df_meta_data = meta_data(train_set, label_column)
        meta_data_list = df_meta_data.loc["quality"].tolist()[1:]
        meta_data_list.append(config)
        df_results.loc[len(df_results)] = meta_data_list

    return df_results
