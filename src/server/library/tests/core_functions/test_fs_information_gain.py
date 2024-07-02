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


import pytest

# feature_selector_with_information_gain
from library.core_functions.utils.fs_information_gain import (
    compute_information_gain,
    feature_selector_with_information_gain,
    sort_sensors,
)
from pandas import DataFrame


class TestInformationGain:
    """Test First and Second Derivative functions."""

    @pytest.fixture(autouse=True)
    def setup(self):

        data = DataFrame()
        data["gestures"] = ["A"] * 5 + ["B"] * 5 + ["C"] * 5
        data["gen_A"] = 5 * [10] + 5 * [0] + 5 * [0]
        data["gen_B"] = 5 * [0] + 5 * [10] + 5 * [0]
        data["gen_C"] = 5 * [0] + 5 * [0] + 5 * [10]
        data["gen_Rnd"] = [5, 21, 3, 10, 19, 7, 8, 24, 1, 22, 0, 26, 20, 6, 16]

        self.data = data
        self.label_column = "gestures"
        self.passthrough_columns = ["gestures"]

        self.target_sensor = "5"

    def test_feature_selector_with_information_gain_1(self):
        """ " feature_selector_with_information_gain results for given parameters"""
        return_data = feature_selector_with_information_gain(
            self.data, self.label_column, 1, ignore_col=self.passthrough_columns
        )

        expected_data = ["gestures", "gen_A", "gen_B", "gen_C"]

        assert return_data == expected_data

    def test_feature_selector_with_information_gain_2(self):
        """ " feature_selector_with_information_gain results for given parameters"""
        return_data = feature_selector_with_information_gain(
            self.data,
            self.label_column,
            1,
            ignore_col=self.passthrough_columns,
            return_score_list=True,
        )

        assert return_data[0].index.tolist()[0] == "gen_A"
        assert return_data[1].index.tolist()[0] == "gen_B"
        assert return_data[2].index.tolist()[0] == "gen_C"

    def test_feature_selector_with_information_gain_std(self):
        """ " for the same ig score sort based on std"""

        data = DataFrame()
        data["gestures"] = ["A"] * 5 + ["B"] * 5 + ["C"] * 5
        data["gen_1"] = 5 * [5] + 5 * [0] + 5 * [10]
        data["gen_2"] = 5 * [5] + 5 * [0] + 5 * [10]
        data["gen_2"] = data["gen_2"] + [
            1.28,
            1.52,
            1.64,
            1.54,
            0.12,
            0.48,
            1.66,
            1.82,
            0.96,
            0.3,
            0.8,
            1.14,
            0.54,
            1.96,
            0.92,
        ]

        return_data = feature_selector_with_information_gain(
            data,
            self.label_column,
            1,
            ignore_col=self.passthrough_columns,
            return_score_list=True,
        )

        assert return_data[0].index.tolist()[0] == "gen_1"
        assert return_data[1].index.tolist()[0] == "gen_1"
        assert return_data[2].index.tolist()[0] == "gen_1"

    def test_feature_selector_with_information_gain_mean_difference(self):
        """for the same ig and std score sort based on mean differences"""

        data = DataFrame()
        data["gestures"] = ["A"] * 5 + ["B"] * 5 + ["C"] * 5
        data["gen_1"] = 5 * [5] + 5 * [0] + 5 * [10]
        data["gen_2"] = 5 * [2] + 5 * [5] + 5 * [8]

        return_data = feature_selector_with_information_gain(
            data,
            self.label_column,
            1,
            ignore_col=self.passthrough_columns,
            return_score_list=True,
        )

        assert return_data[0].index.tolist()[0] == "gen_1"
        assert return_data[1].index.tolist()[0] == "gen_1"
        assert return_data[2].index.tolist()[0] == "gen_1"

    def test_compute_information_gain(self):

        key = "A"
        features = ["gen_A", "gen_B", "gen_C", "gen_Rnd"]

        # vector_groups_based_on_labels
        vector_groups_based_on_labels = self.data.groupby(self.label_column)
        all_class = ["A", "B", "C"]
        min_max_dict = {}
        min_max_dict["A"] = DataFrame(
            {0: [10, 0, 0, 3], 1: [10, 0, 0, 21], 2: [0.0, 0.0, 0.0, 8.1117199162693]},
            index=features,
        )
        min_max_dict["B"] = DataFrame(
            {
                0: [0, 10, 0, 1],
                1: [0, 10, 0, 24],
                2: [0.0, 0.0, 0.0, 10.064790112068906],
            },
            index=features,
        )
        min_max_dict["C"] = DataFrame(
            {
                0: [0, 0, 10, 0],
                1: [0, 0, 10, 26],
                2: [0.0, 0.0, 0.0, 10.526157893552615],
            },
            index=features,
        )
        total_points = 15

        return_data = compute_information_gain(
            key,
            vector_groups_based_on_labels,
            all_class,
            min_max_dict,
            total_points,
            features,
        )

        assert round(return_data.loc["gen_A", "IG_target_sensor"], 2) == 0.64
        assert round(return_data.loc["gen_B", "IG_target_sensor"], 2) == -0.03
        assert round(return_data.loc["gen_C", "IG_target_sensor"], 2) == -0.03

    def test_sort_sensors(self):

        features = ["gen_A", "gen_B", "gen_C", "gen_Rnd"]

        df_selected_features = {}
        df_selected_features["A"] = DataFrame(
            {
                "min_val": [10, 0, 0, 3],
                "max_val": [10, 0, 0, 21],
                "Std": [0.0, 0.0, 0.0, 8.11],
                "Dist": [10.0, 5.0, 5.0, 1.4],
                "IG_target_sensor": [0.636, -0.03, -0.03, -0.03],
            },
            index=features,
        )
        df_selected_features["B"] = DataFrame(
            {
                "min_val": [10, 0, 0, 1],
                "max_val": [10, 0, 0, 24],
                "Std": [0.0, 0.0, 0.0, 10.065],
                "Dist": [10.0, 5.0, 5.0, 1.0],
                "IG_target_sensor": [0.636, -0.03, -0.03, -0.423],
            },
            index=features,
        )
        df_selected_features["C"] = DataFrame(
            {
                "min_val": [10, 0, 0, 0],
                "max_val": [10, 0, 0, 26],
                "Std": [0.0, 0.0, 0.0, 10.526157893552615],
                "Dist": [10.0, 5.0, 5.0, 1.56],
                "IG_target_sensor": [0.636, -0.03, -0.03, -0.719],
            },
            index=features,
        )

        list_of_labels = ["A", "B", "C"]
        feature_number = 1

        feature_list, df_sorted = sort_sensors(
            df_selected_features, list_of_labels, feature_number
        )

        assert feature_list == ["gen_A"]
