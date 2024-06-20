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
import os

import pandas as pd
from library.core_functions.selectors import feature_selector_by_family


def feature_total_count(results):

    return len(
        set([int(col.split("_")[1]) for col in results.columns if "gen_" in col])
    )


def selected_generators_counts(status):

    df = status
    family_selected_counts = (
        df[["Generator", "GeneratorTrueIndex"]][df.Selected == True]
        .drop_duplicates()
        .groupby(["Generator"])["Generator"]
        .count()
        .to_dict()
    )

    family_all_counts = (
        df[["Generator", "GeneratorTrueIndex"]]
        .drop_duplicates()
        .groupby(["Generator"])["Generator"]
        .count()
        .to_dict()
    )

    for key in family_all_counts:
        if not key in family_selected_counts:
            family_selected_counts[key] = 0

    return family_selected_counts


def build_generator_count(feature_table, return_data):

    status = copy.deepcopy(feature_table)
    status["Selected"] = status.apply(
        lambda df: True if df.Feature in return_data.columns else False, axis=1
    )

    family_counts = selected_generators_counts(status)

    return family_counts, status


class TestFeatureSelectorByFamily:
    """Test First and Second Derivative functions."""

    def _load_data(self):

        input_data = pd.read_csv(
            os.path.join(
                os.path.dirname(__file__), "data", "data_table_selector_family.csv"
            )
        )

        n = len(input_data)
        input_data["Label"] = ["Unknown" for i in range(n)]
        input_data["SegmentID"] = [i for i in range(n)]

        feature_table = pd.read_csv(
            os.path.join(
                os.path.dirname(__file__), "data", "feature_table_selector_family.csv"
            )
        )

        return input_data, feature_table

    def test_feature_selector_by_family(self):

        input_data, feature_table = self._load_data()

        #####################################################################
        # maximum number of families has not been specified
        return_data, unselected_columns = feature_selector_by_family(
            input_data,
            [
                {"generator_names": "Downsample", "number": 2},
                {"generator_names": ["MFCC"], "number": 1},
            ],
            None,
            4,
            passthrough_columns=["Label", "SegmentID"],
            feature_table=feature_table,
        )
        assert feature_total_count(return_data) == 3

        family_counts, status = build_generator_count(feature_table, return_data)

        assert family_counts["Downsample"] == 2
        assert family_counts["MFCC"] == 1
        assert family_counts["Absolute Area"] == 0
        assert family_counts["Power Spectrum"] == 0

        #####################################################################
        # max number of families less than the number of generated families and larger than the sum of selected faimilies from the specified list
        return_data, unselected_columns = feature_selector_by_family(
            input_data,
            [
                {"generator_names": ["Downsample", "Absolute Area"], "number": 2},
                {"generator_names": ["MFCC", "Power Spectrum"], "number": 2},
            ],
            5,
            0,
            passthrough_columns=["Label", "SegmentID"],
            feature_table=feature_table,
        )
        assert feature_total_count(return_data) == 4

        family_counts, status = build_generator_count(feature_table, return_data)

        assert (family_counts["Downsample"] + family_counts["Absolute Area"]) == 2
        assert (family_counts["MFCC"] + family_counts["Power Spectrum"]) == 2

        #####################################################################
        # maximum number of families is less than the generated families
        return_data, unselected_columns = feature_selector_by_family(
            input_data,
            None,
            5,
            1,
            passthrough_columns=["Label", "SegmentID"],
            feature_table=feature_table,
        )
        assert feature_total_count(return_data) == 5

        #####################################################################
        # maximum number of families is larger than the generated families
        return_data, unselected_columns = feature_selector_by_family(
            input_data,
            None,
            10,
            3,
            passthrough_columns=["Label", "SegmentID"],
            feature_table=feature_table,
        )
        assert feature_total_count(return_data) == 8

        #####################################################################
        # no input parameter has been specified
        return_data, unselected_columns = feature_selector_by_family(
            input_data,
            None,
            None,
            0,
            passthrough_columns=["Label", "SegmentID"],
            feature_table=feature_table,
        )
        assert feature_total_count(return_data) == 8
