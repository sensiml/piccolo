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

import pandas as pd

from library.core_functions.selectors import (
    custom_feature_selection,
    custom_feature_selection_by_index,
)


class TestCustomFeatureSelectors:
    """Test First and Second Derivative functions."""

    def _create_data(self):
        data_dict = {
            "Label": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "SegmentID": {0: 0, 1: 1, 2: 2, 3: 3, 4: 4},
            "gen_0001_AccelerometerXSum": {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
            "gen_0002_AccelerometerYSum": {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
            "gen_0003_AccelerometerZSum": {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
            "gen_0004_GyroscopeXSum": {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
            "gen_0005_GyroscopeYSum": {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
            "gen_0006_GyroscopeZSum": {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
            "gen_0007_hist_bin_000000": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000001": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000002": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000003": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000004": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000005": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000006": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000007": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000008": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000009": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000010": {0: 255, 1: 255, 2: 255, 3: 255, 4: 255},
            "gen_0007_hist_bin_000011": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000012": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000013": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000014": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000015": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000016": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000017": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000018": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0007_hist_bin_000019": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }

        return pd.DataFrame(data_dict)

    def test_custom_select_features_by_name(self):

        expected_columns = [
            "Label",
            "SegmentID",
            "gen_0001_AccelerometerXSum",
            "gen_0003_AccelerometerZSum",
            "gen_0004_GyroscopeXSum",
            "gen_0005_GyroscopeYSum",
            "gen_0006_GyroscopeZSum",
            "gen_0007_hist_bin_000000",
            "gen_0007_hist_bin_000001",
            "gen_0007_hist_bin_000002",
            "gen_0007_hist_bin_000003",
            "gen_0007_hist_bin_000004",
            "gen_0007_hist_bin_000005",
            "gen_0007_hist_bin_000006",
            "gen_0007_hist_bin_000007",
            "gen_0007_hist_bin_000008",
        ]

        expected_unselected_columns = [
            "gen_0002_AccelerometerYSum",
            "gen_0007_hist_bin_000009",
            "gen_0007_hist_bin_000010",
            "gen_0007_hist_bin_000011",
            "gen_0007_hist_bin_000012",
            "gen_0007_hist_bin_000013",
            "gen_0007_hist_bin_000014",
            "gen_0007_hist_bin_000015",
            "gen_0007_hist_bin_000016",
            "gen_0007_hist_bin_000017",
            "gen_0007_hist_bin_000018",
            "gen_0007_hist_bin_000019",
        ]

        return_data, unselected_columns = custom_feature_selection(
            self._create_data(),
            [
                "gen_0001_AccelerometerXSum",
                "gen_0003_AccelerometerZSum",
                "gen_0004_GyroscopeXSum",
                "gen_0005_GyroscopeYSum",
                "gen_0006_GyroscopeZSum",
                "gen_0007_hist_bin_000000",
                "gen_0007_hist_bin_000001",
                "gen_0007_hist_bin_000002",
                "gen_0007_hist_bin_000003",
                "gen_0007_hist_bin_000004",
                "gen_0007_hist_bin_000005",
                "gen_0007_hist_bin_000006",
                "gen_0007_hist_bin_000007",
                "gen_0007_hist_bin_000008",
            ],
            ["Label", "SegmentID"],
        )

        assert set(return_data.columns) == set(expected_columns)
        assert set(unselected_columns) == set(expected_unselected_columns)

    def test_custom_select_features_by_index(self):

        expected_columns = [
            "Label",
            "SegmentID",
            "gen_0001_AccelerometerXSum",
            "gen_0007_hist_bin_000000",
            "gen_0007_hist_bin_000001",
            "gen_0007_hist_bin_000002",
            "gen_0007_hist_bin_000003",
            "gen_0007_hist_bin_000004",
            "gen_0007_hist_bin_000005",
            "gen_0007_hist_bin_000006",
            "gen_0007_hist_bin_000007",
            "gen_0007_hist_bin_000008",
        ]

        expected_unselected_columns = [
            "gen_0002_AccelerometerYSum",
            "gen_0003_AccelerometerZSum",
            "gen_0004_GyroscopeXSum",
            "gen_0005_GyroscopeYSum",
            "gen_0006_GyroscopeZSum",
            "gen_0007_hist_bin_000009",
            "gen_0007_hist_bin_000010",
            "gen_0007_hist_bin_000011",
            "gen_0007_hist_bin_000012",
            "gen_0007_hist_bin_000013",
            "gen_0007_hist_bin_000014",
            "gen_0007_hist_bin_000015",
            "gen_0007_hist_bin_000016",
            "gen_0007_hist_bin_000017",
            "gen_0007_hist_bin_000018",
            "gen_0007_hist_bin_000019",
        ]

        feature_table = [
            {
                "Feature": "gen_0001_AccelerometerXSum",
                "GeneratorTrueIndex": 1,
                "GeneratorFamilyIndex": 0,
            },
            {
                "Feature": "gen_0007_hist_bin_000000",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 0,
            },
            {
                "Feature": "gen_0007_hist_bin_000001",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 1,
            },
            {
                "Feature": "gen_0007_hist_bin_000002",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 2,
            },
            {
                "Feature": "gen_0007_hist_bin_000003",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 3,
            },
            {
                "Feature": "gen_0007_hist_bin_000004",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 4,
            },
            {
                "Feature": "gen_0007_hist_bin_000005",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 5,
            },
            {
                "Feature": "gen_0007_hist_bin_000006",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 6,
            },
            {
                "Feature": "gen_0007_hist_bin_000007",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 7,
            },
            {
                "Feature": "gen_0007_hist_bin_000008",
                "GeneratorTrueIndex": 7,
                "GeneratorFamilyIndex": 8,
            },
        ]

        return_data, unselected_columns = custom_feature_selection_by_index(
            self._create_data(),
            {1: [0], 2: [], 7: [0, 1, 2, 3, 4, 5, 6, 7, 8]},
            ["Label", "SegmentID"],
            feature_table=pd.DataFrame(feature_table),
        )

        print(return_data.columns)

        assert set(return_data.columns) == set(expected_columns)

        assert set(unselected_columns) == set(expected_unselected_columns)
