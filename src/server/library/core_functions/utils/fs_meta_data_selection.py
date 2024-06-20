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

from copy import deepcopy
from library.core_functions.utils.fs_information_gain import (
    feature_selector_with_information_gain,
)


class MetaDataSelection:
    """
    Grouping the data based based on meta data by using information gain scores.

    Args:
        new_training_data: DataFrame, it holds input data
        label : class label
    Return:
        Dict: Dictionary that has list of grouped class

    """

    def __init__(self, new_training_data, label):
        self.new_training_data = deepcopy(new_training_data)
        self.label = label

    def create_class_combination(self):
        df_combination = pd.DataFrame(
            [], columns=["Combination", "Group1", "Group2", "IG", "Std", "Dist"]
        )
        group_1_list = []
        group_2_list = []
        combination_list = []

        class_list = np.unique(self.new_training_data[self.label]).tolist()

        for i in range(1, 2 ** (len(class_list) - 1)):
            s = bin(i)[2:].zfill(len(class_list))
            group_1_list.append(
                [class_list[indx] for indx, v in enumerate(s) if v == "1"]
            )
            group_2_list.append(list(set(class_list) - set(group_1_list[-1])))
            combination_list.append([s])

        df_combination["Group1"] = group_1_list
        df_combination["Group2"] = group_2_list
        df_combination["Combination"] = combination_list

        self.df_combination = df_combination

    def score_class_combination(self):
        self.create_class_combination()
        self.new_training_data["new_label"] = None
        non_feature_columns = [
            i for i in self.new_training_data.columns.tolist() if ("gen_" != i[:4])
        ]

        for comb_indx in self.df_combination.index:
            group_1 = self.df_combination.iloc[comb_indx]["Group1"]
            group_1_indx = self.new_training_data[
                self.new_training_data[self.label].isin(group_1)
            ].index
            self.new_training_data.loc[group_1_indx, "new_label"] = [1] * len(
                self.new_training_data[self.new_training_data[self.label].isin(group_1)]
            )

            group_2 = self.df_combination.iloc[comb_indx]["Group2"]
            group_2_indx = self.new_training_data[
                self.new_training_data[self.label].isin(group_2)
            ].index
            self.new_training_data.loc[group_2_indx, "new_label"] = [0] * len(
                self.new_training_data[self.new_training_data[self.label].isin(group_2)]
            )

            df = feature_selector_with_information_gain(
                self.new_training_data,
                "new_label",
                1,
                ignore_col=non_feature_columns,
                return_score_list=True,
            )

            score_0 = round(
                df[0]
                .head(int(1 + len(df[0]) / 4))[["IG_target_sensor", "Std", "Dist"]]
                .median(),
                3,
            )
            score_1 = round(
                df[1]
                .head(int(1 + len(df[1]) / 4))[["IG_target_sensor", "Std", "Dist"]]
                .median(),
                3,
            )

            self.df_combination.loc[comb_indx, ["IG", "Std", "Dist"]] = np.mean(
                [score_0, score_1], axis=0
            )

        self.df_combination = self.df_combination.sort_values(
            by=["IG", "Std", "Dist"], ascending=[False, True, False]
        ).reset_index(drop=True)

        return self.df_combination.loc[0, ["Group1", "Group2"]].to_dict()
