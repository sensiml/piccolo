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

import time
from copy import deepcopy

import pytest
from library.core_functions.samplers import (
    augment_pad_segment,
    concat,
    isolation_forest_filtering,
    local_outlier_factor_filtering,
    np,
    one_class_SVM_filtering,
    robust_covariance_filtering,
    sample_autogroup_labels,
    sample_by_metadata,
    sample_combine_labels,
    sample_metadata_max_pool,
    sample_zscore_filter,
    sigma_outliers_filtering,
    undersample_majority_classes,
)
from numpy import arange, pi, random, sin, unique
from pandas import DataFrame, read_csv


class TestSampling:
    """Test sampling functions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = DataFrame({"AccelerometerX": range(10), "Subject": range(20, 30)})
        self.data2 = DataFrame(
            [
                [-3, 6, 5, "A"],
                [3, 7, 8, "B"],
                [0, 6, 3, "C"],
                [-2, 8, 7, "C"],
                [2, 9, 6, "D"],
            ],
            columns=["feature1", "feature2", "feature3", "label"],
        )

        df = DataFrame([], columns=["Label"] + ["gen_00" + str(c) for c in range(50)])
        Fs = 50
        f = 10
        sample = 50
        x = arange(sample)

        y = sin(2 * pi * f * x / Fs) * 1000
        for r in range(20):
            df.loc[len(df)] = ["Red"] + [i * random.random() for i in y]

        df.loc[len(df)] = ["Blue"] + [i * random.random() for i in y]
        df.loc[len(df)] = ["Green"] + [i * random.random() for i in y]

        y = sin(1.5 * pi * f * x / Fs) * 2000
        for r in range(20):
            df.loc[len(df)] = ["Blue"] + [i * random.random() for i in y]

        df.loc[len(df)] = ["Red"] + [i * random.random() for i in y]
        df.loc[len(df)] = ["Green"] + [i * random.random() for i in y]

        y = sin(1 * pi * f * x / Fs) * 3000
        for r in range(20):
            df.loc[len(df)] = ["Green"] + [i * random.random() for i in y]

        df.loc[len(df)] = ["Red"] + [i * random.random() for i in y]
        df.loc[len(df)] = ["Blue"] + [i * random.random() for i in y]

        self.data3 = df

    def test_sample_by_metadata(self):
        """Sample the DataFrame using the 'Subject' metadata column and ensure
        that all returned rows have allowable Subject values."""
        allowed_values = [1, 3, 21, 24, 29, 20]
        sampled_data = sample_by_metadata(self.data, "Subject", allowed_values)
        assert set(sampled_data["Subject"]).issubset(set(allowed_values))

    def test_sample_combine_labels(self):
        sampled_data = sample_combine_labels(
            self.data2, "label", {"Group1": ["A", "B"], "Group2": ["C"]}
        )

        expected_result = {
            "feature1": {0: -3, 1: 3, 2: 0, 3: -2, 4: 2},
            "feature2": {0: 6, 1: 7, 2: 6, 3: 8, 4: 9},
            "feature3": {0: 5, 1: 8, 2: 3, 3: 7, 4: 6},
            "label": {0: "Group1", 1: "Group1", 2: "Group2", 3: "Group2", 4: "D"},
        }

        assert sampled_data.to_dict() == expected_result

    def test_sample_zscore_filter(self):
        orj_index = self.data3.index.tolist()

        received_result = sample_zscore_filter(
            self.data3,
            "Label",
            zscore_cutoff=3,
            feature_threshold=1,
            feature_columns=None,
        )
        received_result_index = received_result.index.tolist()
        expected_result_index = [64, 65, 61, 62, 63, 60]

        results_index = list(set(orj_index) - set(received_result_index))

        for result_index in results_index:
            assert result_index in expected_result_index

        orj_index = self.data3.index.tolist()
        received_result = sample_zscore_filter(
            self.data3.copy(),
            "Label",
            zscore_cutoff=3,
            feature_threshold=1,
            feature_columns=None,
            assign_unknown=True,
        )

        assert "Unknown" in received_result.Label.unique()

    def test_sigma_outliers_filtering(self):
        orj_index = self.data3.index.tolist()
        received_result = sigma_outliers_filtering(
            self.data3.copy(), "Label", sigma_threshold=2.1
        )
        received_result_index = received_result.index.tolist()
        assert len(set(orj_index) - set(received_result_index)) > 2

        orj_index = self.data3.index.tolist()
        received_result = sigma_outliers_filtering(
            self.data3.copy(), "Label", sigma_threshold=2.1, assign_unknown=True
        )
        assert "Unknown" in received_result.Label.unique()

    def test_local_outlier_factor_filtering(self):
        orj_index = self.data3.index.tolist()
        received_result = local_outlier_factor_filtering(
            self.data3.copy(), "Label", number_of_neighbors=10
        )
        received_result_index = received_result.index.tolist()
        expected_result_index = [64, 65, 60, 61, 62, 63]
        assert (
            list(set(orj_index) - set(received_result_index)) == expected_result_index
        )

        orj_index = self.data3.index.tolist()

        received_result = local_outlier_factor_filtering(
            self.data3.copy(),
            "Label",
            filtering_label=["Red", "Green", "Blue", "Orange"],
            number_of_neighbors=10,
            assign_unknown=True,
        )
        assert "Unknown" in received_result.Label.unique()

        received_result = local_outlier_factor_filtering(
            self.data3.copy(),
            "Label",
            filtering_label=["Red"],
            number_of_neighbors=10,
            assign_unknown=False,
        )

        assert "Green" in received_result.Label.unique()
        assert "Red" in received_result.Label.unique()
        assert "Blue" in received_result.Label.unique()
        assert "Unknown" not in received_result.Label.unique()

        received_result = local_outlier_factor_filtering(
            self.data3.copy(),
            "Label",
            filtering_label=["Orange"],
            number_of_neighbors=10,
            assign_unknown=True,
        )

        assert "Unknown" not in received_result.Label.unique()

    def test_isolation_forest_filtering(self):
        self.data3.index.tolist()
        received_result = isolation_forest_filtering(self.data3, "Label")
        # received_result_index = received_result.index.tolist()
        # expected_result_index = [64, 65, 60, 61, 62, 63]
        # print(list(set(orj_index) - set(received_result_index)))
        # assert(
        #    list(
        #        set(orj_index) -
        #        set(received_result_index)) == expected_result_index)

        # orj_index = self.data3.index.tolist()
        received_result = isolation_forest_filtering(
            self.data3.copy(), "Label", assign_unknown=True
        )
        assert "Unknown" in received_result.Label.unique()

        received_result = isolation_forest_filtering(
            self.data3.copy(),
            "Label",
            filtering_label=["Red", "Green", "Blue", "Orange"],
            assign_unknown=True,
        )
        assert "Unknown" in received_result.Label.unique()

        received_result = isolation_forest_filtering(
            self.data3.copy(), "Label", filtering_label=["Red"], assign_unknown=False
        )

        assert "Green" in received_result.Label.unique()
        assert "Red" in received_result.Label.unique()
        assert "Blue" in received_result.Label.unique()
        assert "Unknown" not in received_result.Label.unique()

        received_result = isolation_forest_filtering(
            self.data3.copy(), "Label", filtering_label=["Orange"], assign_unknown=True
        )

        assert "Unknown" not in received_result.Label.unique()

        failed = False
        try:
            received_result = isolation_forest_filtering(
                self.data3.copy(),
                "Label",
                assign_unknown=False,
                outliers_fraction=1,
            )
        except ValueError:
            failed = True

        assert failed

    def test_one_class_SVM_filtering(self):
        orj_index = self.data3.index.tolist()
        received_result = one_class_SVM_filtering(
            self.data3.copy(), "Label", outliers_fraction=0.15
        )
        received_result_index = received_result.index.tolist()
        expected_result_index = [64, 65, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
        assert (
            list(set(orj_index) - set(received_result_index)) == expected_result_index
        )

        orj_index = self.data3.index.tolist()
        received_result = one_class_SVM_filtering(
            self.data3.copy(), "Label", outliers_fraction=0.15, assign_unknown=True
        )

        assert "Unknown" in received_result.Label.unique()

    def test_robust_covariance_filtering(self):
        gen_01 = [
            21.40640182284953,
            -58.29134098553432,
            -40.07113769544756,
            -84.93336988348683,
            -38.62946625611666,
            -76.38681483971548,
            -69.15139469532203,
            -48.002542540466834,
            -36.83559952558708,
            -85.2327949988885,
            -66.50176263195995,
            -89.15600509167535,
            -22.998628125654808,
            -82.26533917830331,
            -35.492107785247235,
            -32.14965097877289,
            -54.698576665404104,
            -67.60753803340815,
            -82.15590759945779,
            -27.850363582994895,
            156.90105909887601,
            255.58362315005414,
        ]
        gen_02 = [
            3.6253254992507458,
            -56.67797865908408,
            -104.72313139328382,
            -53.16435009143963,
            -118.78454225746007,
            -53.35173552773053,
            -45.0894955354117,
            -101.69835680150584,
            -3.4163320951572036,
            -33.060745069147586,
            -36.564049467961155,
            -64.74454258105666,
            -66.1615300754127,
            -88.33552989100434,
            -71.41244551667133,
            -17.284728559730333,
            -69.46729213998728,
            -76.13959554933037,
            -110.33888828150899,
            -45.94153106263478,
            248.223377095728196,
            231.36714138326153,
        ]
        label = ["Blue"] * len(gen_01)

        df_temp = DataFrame([])
        df_temp["Label"] = label
        df_temp["gen_01"] = gen_01
        df_temp["gen_02"] = gen_02

        orj_index = df_temp.index.tolist()
        received_result = robust_covariance_filtering(
            df_temp, "Label", outliers_fraction=0.05
        )
        received_result_index = received_result.index.tolist()
        expected_result_index = [20, 21]
        assert (
            list(set(orj_index) - set(received_result_index)) == expected_result_index
        )

        orj_index = self.data3.index.tolist()
        received_result = robust_covariance_filtering(
            df_temp, "Label", outliers_fraction=0.05, assign_unknown=True
        )

        assert "Unknown" in received_result.Label.unique()

    def test_sample_combine_labels_auto(self):
        data = DataFrame()
        data["gestures"] = ["A"] * 5 + ["B"] * 5 + ["C"] * 5
        data["gen_1"] = 5 * [0] + 4 * [0] + 1 * [10] + 5 * [10]
        results = sample_autogroup_labels(deepcopy(data), "gestures", {})
        class_labels = [i for i in unique(results.gestures)]
        expected_results = [["A", "B"], ["C"]]
        temp = [list(np.sort(i)) in expected_results for i in class_labels]
        assert all(temp)

        data = DataFrame()
        data["gestures"] = ["A"] * 5 + ["B"] * 5 + ["C"] * 5
        data["gen_1"] = 5 * [0] + 2 * [0] + 3 * [10] + 5 * [10]
        results = sample_autogroup_labels(deepcopy(data), "gestures", {})
        class_labels = [i for i in unique(results.gestures)]
        expected_results = [["A"], ["B", "C"]]
        temp = [list(np.sort(i)) in expected_results for i in class_labels]
        assert all(temp)

        data = DataFrame()
        data["gestures"] = [1] * 5 + [2] * 5 + [3] * 5
        data["gen_1"] = 5 * [0] + 2 * [0] + 3 * [10] + 5 * [10]
        results = sample_autogroup_labels(deepcopy(data), "gestures", {})
        class_labels = [i for i in unique(results.gestures)]
        expected_results = [[1], [2, 3]]
        temp = [list(np.sort(i)) in expected_results for i in class_labels]
        assert all(temp)

    def test_undersample_majority_classes(self):
        df = DataFrame(["A"] * 100 + ["B"] * 100 + ["C"] * 50, columns=["Label"])

        results = undersample_majority_classes(df, "Label")

        expected_results = DataFrame(
            ["A"] * 50 + ["B"] * 50 + ["C"] * 50, columns=["Label"]
        )

        assert results.equals(expected_results)

        results = undersample_majority_classes(df, "Label", target_class_size=10)

        expected_results = DataFrame(
            ["A"] * 10 + ["B"] * 10 + ["C"] * 10, columns=["Label"]
        )

        assert results.equals(expected_results)

        results = undersample_majority_classes(df, "Label", target_class_size=60)

        expected_results = DataFrame(
            ["A"] * 50 + ["B"] * 50 + ["C"] * 50, columns=["Label"]
        )

        assert results.equals(expected_results)

        df = DataFrame(["A"] * 100 + ["B"] * 100 + ["C"] * 50, columns=["Label"])

        df["F1"] = range(250)

        resultsA = undersample_majority_classes(
            df, "Label", target_class_size=10, seed=5
        )

        resultsB = undersample_majority_classes(
            df, "Label", target_class_size=10, seed=5
        )

        assert resultsA.equals(resultsB)

        resultsA = undersample_majority_classes(
            df, "Label", target_class_size=10, seed=10
        )

        resultsB = undersample_majority_classes(
            df, "Label", target_class_size=10, seed=5
        )

        assert not resultsA.equals(resultsB)

        results = undersample_majority_classes(
            df, "Label", maximum_samples_size_per_class=75
        )

        expected_results = ["A"] * 75 + ["B"] * 75 + ["C"] * 50

        assert results["Label"].tolist() == expected_results

    @pytest.mark.skip("Used for profiling")
    def test_undersample_majority_classes_profiling(self):
        csv_path = ""

        start = time.time()

        df = read_csv(csv_path, sep="\t")
        print("read csv in ", time.time() - start)
        start = time.time()
        results = undersample_majority_classes(
            df, "Labels", target_class_size=0, maximum_samples_size_per_class=0, seed=0
        )
        print("finished undersample in", time.time() - start)

    def test_segment_augment(self):
        """Create a dataset"""

        Fs = 50
        f = 3
        sample = 1000
        x = arange(sample)
        y = (sin(2 * pi * f * x / Fs) + 1) * 10 - 10

        df_list = []
        df_sine = DataFrame([], columns=["Word", "SegmentID"])
        df_sine["AccelerometerX"] = y
        df_sine["AccelerometerY"] = y * (-2)
        df_sine["AccelerometerZ"] = y * 4
        df_sine.Word = "Sine"
        df_sine.SegmentID = 1
        df_list.append(df_sine)

        passthrough_columns = ["Word", "SegmentID"]
        data = concat(df_list)
        input_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
        data[input_columns] = data[input_columns].astype(int)

        result = augment_pad_segment(data, passthrough_columns, sample * 2, 0)

        assert len(result) == sample * 2


def test_sample_metadata_max_pool():
    data = {
        "Label": [1, 1, 1, 1, 2, 2, 1, 3, 1],
        "SegmentID": [1, 1, 1, 2, 2, 2, 3, 3, 3],
    }

    result = sample_metadata_max_pool(
        DataFrame(data), group_columns=["SegmentID"], metadata_name="Label"
    )

    expected_result = {
        "Label": [1, 1, 1, 2, 2, 2, 1, 1, 1],
        "SegmentID": [1, 1, 1, 2, 2, 2, 3, 3, 3],
    }

    assert expected_result == result.to_dict(orient="list")
