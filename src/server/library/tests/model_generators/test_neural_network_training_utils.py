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

# coding=utf-8
import logging
import numpy as np
import pandas as pd

from library.model_generators.neural_network_training_utils import (
    add_column_row_random_noise,
    add_sparse_random_noise,
    augment_feature_with_unknown,
    copy,
    features_to_tensor_convert,
    get_data_aux_indices,
    get_label_stat,
    mask_image,
    resample,
)

logger = logging.getLogger(__name__)


def xy_sanity_check(X, y, n_labels):

    xx = np.floor(X.reshape(-1))
    n = len(n_labels)
    for j in range(n):
        yi_ = np.zeros(n)
        yi_[j] = 1
        for i in range(len(xx)):
            if xx[i] == n_labels[j]:
                np.testing.assert_array_equal(y[i], yi_)


def generate_one_hot_encoded(n_label_list):

    N = np.sum(n_label_list)  # labels distribution
    n = len(n_label_list)  # number of labels

    y_values_encoded = np.zeros((N, n))
    x_values = np.zeros((N, 1))
    idx = np.random.choice(range(N), size=N, replace=False)

    s = 0
    for j in range(n):
        e = s + n_label_list[j]
        for i in idx[s:e]:
            y_values_encoded[i][j] = 1
            x_values[i][0] = n_label_list[j] + np.random.random()
        s = e

    return x_values, y_values_encoded


def make_feature_vector(n_unknown=5, n_A=5, n_B=5):

    N = n_unknown + n_A + n_B

    fv_ar = np.zeros((N))
    fv_ar[:n_unknown] = np.linspace(0, 0.1, n_unknown, endpoint=False)
    fv_ar[n_unknown : n_unknown + n_A] = np.linspace(1, 2, n_A, endpoint=False)
    fv_ar[n_unknown + n_A :] = np.linspace(2, 3, n_B, endpoint=False)

    fv_in = pd.DataFrame.from_dict({"FV": fv_ar})
    fv_in["Label"] = 1  # unknown
    fv_in["Label"].iloc[n_unknown : n_unknown + n_A] = 2  # A
    fv_in["Label"].iloc[n_unknown + n_A :] = 3  # B

    # fv_in calss map
    class_map = {"Unknown": 1, "A": 2, "B": 3}

    return fv_in, class_map


def make_auxiliary_data():

    arr = np.zeros((50))
    arr[0:5] = np.arange(10, 10.5, 0.1)
    arr[5:10] = np.arange(20, 20.5, 0.1)
    arr[10:15] = np.arange(30, 30.5, 0.1)
    arr[15:20] = np.arange(40, 40.5, 0.1)
    arr[20:] = np.arange(100, 100.3, 0.01)

    auxiliary_fv = pd.DataFrame.from_dict({"FV": arr})
    auxiliary_fv["Label"] = "Unknown"  # auxiliary unknowns
    auxiliary_fv["Label"].iloc[0:5] = "a"  # auxiliary label 'a'
    auxiliary_fv["Label"].iloc[5:10] = "b"  # auxiliary label 'b'
    auxiliary_fv["Label"].iloc[10:15] = "c"  # auxiliary label 'c'
    auxiliary_fv["Label"].iloc[15:20] = "d"  # auxiliary label 'd'

    return auxiliary_fv


class TestAugment:
    def data(self):
        return np.zeros((10, 6, 8, 1))

    def test_add_column_row_random_noise(self):

        X_in = self.data()

        N = X_in.shape[0]
        nR = X_in.shape[1]  # number of rows
        nC = X_in.shape[2]  # number of columns

        # bias value = bias = 3
        # either changing a column or row
        bias = 3
        X_out = add_column_row_random_noise(
            X_in, max_change=1, bias_range=(bias, bias + 1), fraction=1
        )

        for i in range(N):
            s = np.sum(X_out[i])
            assert s == 0 or s == bias * nR or s == bias * nC

    def test_add_sparse_random_noise(self):

        X_in = copy.deepcopy(self.data())

        N = X_in.shape[0]

        # bias value = mask = 3
        # either changing a column or row
        bias = 3
        X_out = add_sparse_random_noise(
            X_in, max_change=2, bias_range=(bias, bias + 1), fraction=1
        )
        for i in range(N):
            s = np.sum(X_out[i])
            assert s == 0 or s == bias or s == bias * 2

        X_out = add_sparse_random_noise(
            copy.deepcopy(self.data()),
            max_change=2,
            bias_range=(bias, bias + 1),
            fraction=0,
        )
        for i in range(N):
            s = np.sum(X_out[i])
            assert s == 0

    def test_mask_image(self):

        X_in = self.data()

        N = X_in.shape[0]
        nR = X_in.shape[1]  # number of rows
        nC = X_in.shape[2]  # number of columns

        # bias value = mask = 3
        # either changing a column or row
        mask = 3
        X_out = mask_image(
            X_in, max_change=1, mask_value=(mask, mask + 1), fraction=1, mode="row"
        )
        for i in range(N):
            s = np.sum(X_out[i])
            assert s == 0 or s == mask * nC

        mask = 5
        X_out = mask_image(
            self.data(),
            max_change=1,
            mask_value=(mask, mask + 1),
            fraction=1,
            mode="column",
        )
        for i in range(N):
            s = np.sum(X_out[i])
            assert s == 0 or s == mask * nR

    def test_augment_feature_with_unknown(self):

        #### 1: preparing the input data frame (provided by user)
        fv_in, class_map = make_feature_vector()

        #### 2: preparing the auxiliary data frame (provided with the base model)
        auxiliary_fv = make_auxiliary_data()

        #### 3: the augmentation process
        # note: labels 'c' and 'd' are treated as unknown keywords
        # note: labels 'a' and 'b' overlap with labels provided
        # by the user and hence they are ignored

        (
            ix_fv_keywords,
            ix_fv_unknown,
            ix_aux_unknown_kw,
            ix_aux_unknown,
        ) = get_data_aux_indices(fv_in, auxiliary_fv, class_map)

        feature_columns = fv_in.columns
        n_fv = len(feature_columns) - 1
        auxiliary_fv = auxiliary_fv[auxiliary_fv.columns[:n_fv]]
        auxiliary_fv.columns = feature_columns[:n_fv]
        auxiliary_fv[feature_columns[-1]] = class_map["Unknown"]

        train_data_ix, ix_aux = augment_feature_with_unknown(
            ix_fv_unknown,
            ix_fv_keywords,
            ix_aux_unknown,
            ix_aux_unknown_kw,
            size_input_unknown=10,
            size_aux_unknown_kw=7,
            size_aux_unknown=12,
        )

        augmented_fv = pd.concat(
            [fv_in.iloc[train_data_ix], auxiliary_fv.iloc[ix_aux]]
        ).reset_index(drop=True)

        #### 4: testing the augmented data frame
        assert len(augmented_fv[augmented_fv["Label"] == 2]) == 5  # label A
        assert len(augmented_fv[augmented_fv["Label"] == 3]) == 5  # label B

        aug_fv_values = np.floor(augmented_fv["FV"].values)

        assert np.sum(aug_fv_values == 1) == 5  # Label A from input array
        assert np.sum(aug_fv_values == 2) == 5  # Label B from input array

        # none of the similar keywords from the auxiliary array should be propagated
        assert np.sum(aug_fv_values == 10) == 0  # Label 'a' from auxiliary array
        assert np.sum(aug_fv_values == 20) == 0  # Label 'b' from auxiliary array

        # All Unknowns: 29 = 10 + 7 + 12
        assert len(augmented_fv[augmented_fv["Label"] == 1]) == 29

        assert np.sum(aug_fv_values == 0) == 10  # input unknowns
        assert (
            np.sum((aug_fv_values == 30) | (aug_fv_values == 40)) == 7
        )  # unknown keywords: labels "c" and "d"
        assert np.sum(aug_fv_values == 100) == 12  # auxiliary unknowns

    def test_features_to_tensor_convert(self):

        train_data, class_map = make_feature_vector()
        x_values, y_values_encoded = features_to_tensor_convert(train_data, class_map)

        ## testing train_data
        fv = train_data["FV"].values.reshape(-1)
        np.testing.assert_array_equal(x_values.reshape(-1), fv)

        ## testing the encoded labels
        np.testing.assert_array_equal(y_values_encoded[0], np.asarray([1, 0, 0]))
        np.testing.assert_array_equal(y_values_encoded[5], np.asarray([0, 1, 0]))
        np.testing.assert_array_equal(y_values_encoded[10], np.asarray([0, 0, 1]))

    def test_get_label_stat(self):

        _, y_values_encoded = generate_one_hot_encoded([11, 7, 3])

        n_labels, min_n_labels, max_n_labels = get_label_stat(y_values_encoded)

        assert len(n_labels) == 3
        assert min_n_labels == 3
        assert max_n_labels == 11

        np.testing.assert_array_equal(np.sort(n_labels), np.asarray([3, 7, 11]))

    def test_resample(self):

        n_labels = [13, 12, 5]
        x_values, y_values = generate_one_hot_encoded(n_labels)

        selected_indices = resample(y_values)
        x_re = x_values[selected_indices]
        y_re = y_values[selected_indices]
        xx = np.floor(x_re.reshape(-1))
        assert len(xx) == 39
        assert np.sum(xx == 13) == 13
        assert np.sum(xx == 12) == 13
        assert np.sum(xx == 5) == 13
        xy_sanity_check(x_re, y_re, n_labels)

        selected_indices = resample(y_values, method="undersample")
        x_re = x_values[selected_indices]
        y_re = y_values[selected_indices]
        xx = np.floor(x_re.reshape(-1))
        assert len(xx) == 15
        assert np.sum(xx == 13) == 5
        assert np.sum(xx == 12) == 5
        assert np.sum(xx == 5) == 5
        xy_sanity_check(x_re, y_re, n_labels)

        selected_indices = resample(y_values, method="mean")
        x_re = x_values[selected_indices]
        y_re = y_values[selected_indices]
        xx = np.floor(x_re.reshape(-1))
        assert len(xx) == 30
        assert np.sum(xx == 13) == 10
        assert np.sum(xx == 12) == 10
        assert np.sum(xx == 5) == 10
        xy_sanity_check(x_re, y_re, n_labels)

        selected_indices = resample(y_values, method="median")
        x_re = x_values[selected_indices]
        y_re = y_values[selected_indices]
        xx = np.floor(x_re.reshape(-1))
        assert len(xx) == 36
        assert np.sum(xx == 13) == 12
        assert np.sum(xx == 12) == 12
        assert np.sum(xx == 5) == 12
        xy_sanity_check(x_re, y_re, n_labels)
