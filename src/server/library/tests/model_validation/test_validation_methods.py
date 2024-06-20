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

import os

import numpy as np
import pandas as pd
import pytest
from sklearn.utils._testing import assert_array_equal
from library.core_functions.augmentation import (
    augment_uuid,
    copy,
    is_augmented,
    semi_original_uuid,
    similar_root_uuid,
    uuid4,
)
from library.model_validation.validation_method import is_original

from library.model_validation.validation_methods import (
    GroupAndLabelKFold,
    LeaveOneGroupOutValidation,
    MetadataAndLabelKFoldValidation,
    MetadataKFoldValidation,
    SetSampler,
    SetSampleValidation,
    SplitByMetadataValue,
    StratifiedKFoldCrossValidation,
    StratifiedShuffleSplitValidation,
)


def generate_uuid_list(size):

    UIDS = [str(uuid4())]
    i = 1
    while i < size:

        if np.random.randint(2):
            UIDS.append(str(uuid4()))
            UIDS.append(str(uuid4()))
            i += 1
        else:
            ix = np.random.randint(i)
            idd = UIDS[ix]
            if np.random.randint(2):
                if not is_augmented(idd):
                    UIDS.append(semi_original_uuid(idd))
                    UIDS.append(semi_original_uuid(idd))
                else:
                    UIDS.append(augment_uuid(idd))
                    UIDS.append(augment_uuid(idd))
                i += 1
            else:
                UIDS.append(augment_uuid(idd))

        i += 1

    return UIDS[:size]


class TestLeaveOneGroupOutValidation:
    """Tests the LeaveOneGroupOut cross-validation method."""

    def setup_class(self):

        self.data = pd.read_csv(
            os.path.join(
                "engine", "tests", "data", "Validation_TestCase_LeaveOneOut.csv"
            )
        )

        self.config = {
            "label_column": "Label",
            "validation_seed": 1,
            "number_of_folds": 0,
            "group_columns": ["Group"],
        }

    def test_generate_validation(self):

        self.loso = LeaveOneGroupOutValidation(self.config, self.data)
        self.loso.generate_validation(**self.config)

        print(self.data)
        # Reference ski-kit learn call
        from sklearn.model_selection import LeaveOneGroupOut

        cv = LeaveOneGroupOut()

        for index, (train, test) in enumerate(
            cv.split(self.data["Label"], self.data["Label"], self.data["Group"])
        ):
            np.testing.assert_array_equal(train, self.loso._sets[index].train)
            np.testing.assert_array_equal(test, self.loso._sets[index].validate)

            # All validation sets should consist of one group
            val_group = set(self.data.iloc[self.loso._sets[index].validate]["Group"])
            # print val_group
            assert val_group in (set([3]), set([4]), set([5]), set([6]))

            # All train sets should contain all samples from all other groups
            train_group = set(self.data.iloc[self.loso._sets[index].train]["Group"])
            # print train_group
            assert train_group in (
                set([3, 4, 5]),
                set([3, 4, 6]),
                set([3, 5, 6]),
                set([4, 5, 6]),
            )

            # Train and validate sets should be mutually exclusive
            assert set([]) == val_group.intersection(train_group)

    def test_generate_validation_with_augmentation(self):

        df = copy.deepcopy(self.data)
        df["segment_uuid"] = [
            "120bce8c-e013-4bbd-8eb1-c375232e490e",
            "120bce8c-2e48-eeef-81ca-121f21200dee",
            "120bce8c-5ea0-eeef-bf5b-9c2a26b3fcee",
            "120bce8c-5ea0-ffff-9c2a-8815f90e4f00",
            "81df4291-2fda-4710-ba38-d753a94b285a",
            "fab36796-7fee-492f-8f56-1e15da858b37",
            "120bce8c-e013-ffff-c375-5963777d1f00",
            "d72daab5-0d5d-460c-a339-6f875e381b94",
            "3ee6689a-6743-4ea9-ad55-f89aa000415d",
            "d222cb42-3d5e-4d84-adb8-6d6a6eac661a",
            "d6baa66e-caf3-4bfb-b21c-33cba124ed7d",
            "3ee6689a-6743-ffff-f89a-2937f4ef6f00",
            "aeec14a1-8d4f-440f-9740-665dd01700fc",
            "20e3000b-c80c-4d42-9d19-b063d7a71dbc",
            "3ee6689a-6743-ffff-2937-6594a60d3f01",
            "d222cb42-4374-eeef-9156-53fd19b92eee",
            "d222cb42-05b0-eeef-b3fa-8a8dfc840cee",
            "23aa61ef-5a63-49e2-863d-e98c8b03e55e",
            "1a814670-5a83-42b1-84ff-e50f515faac6",
            "3ee6689a-6743-ffff-6594-1a7bb59e4f02",
            "3ee6689a-6743-ffff-6594-e298c2eebf02",
        ]

        df["Group0"] = 13
        config = {
            "label_column": "Label",
            "validation_seed": 1,
            "number_of_folds": 0,
            "group_columns": ["Group", "Group0"],
        }

        self.loso = LeaveOneGroupOutValidation(config, df)
        self.loso.generate_validation(**config)

        # Reference ski-kit learn call
        from sklearn.model_selection import LeaveOneGroupOut

        cv = LeaveOneGroupOut()

        for index, (train, validate) in enumerate(
            cv.split(
                self.loso._data["Label"],
                self.loso._data["Label"],
                self.loso._data["Group"],
            )
        ):
            indx_train = self.loso._sets[index].train
            indx_validate = self.loso._sets[index].validate
            np.testing.assert_array_equal(
                self.loso._original_indices[validate], indx_validate
            )

            # All validation sets should consist of one group
            val_group = set(
                self.loso._all_data.iloc[indx_validate][["Group", "Group0"]]
                .apply(lambda row: "/".join([str(r) for r in row]), axis=1)
                .values
            )
            # print val_group
            assert val_group in (
                set(["3/13"]),
                set(["4/13"]),
                set(["5/13"]),
                set(["6/13"]),
            )

            #####################################################################
            # # All train sets should contain all samples from all other groups
            train_group = set(
                self.loso._all_data.iloc[indx_train][["Group", "Group0"]]
                .apply(lambda row: "/".join([str(r) for r in row]), axis=1)
                .values
            )
            # print train_group
            assert train_group in (
                set(["3/13", "4/13", "5/13"]),
                set(["3/13", "4/13", "6/13"]),
                set(["3/13", "5/13", "6/13"]),
                set(["4/13", "5/13", "6/13"]),
            )

            # # Train and validate sets should be mutually exclusive
            assert set([]) == val_group.intersection(train_group)
            #####################################################################

            # no augmented segment must be present in the validation set
            assert sum(is_original(df.iloc[indx_validate])) == len(indx_validate)

            # making sure that none of the augmented version of validation segments are in the training set
            check = True
            for idd in df.iloc[indx_train]["segment_uuid"].values:
                if is_augmented(idd):
                    for jdd in df.iloc[indx_validate]["segment_uuid"].values:
                        if similar_root_uuid(idd, jdd):
                            check = False
            assert check


class TestStratifiedKFoldValidation:
    """Tests the StratifiedKFold cross-validation method."""

    def setup_class(self):
        """Use skateboarding ground data."""

        self.data = pd.read_csv(
            os.path.join(
                "engine", "tests", "data", "Validation_TestCase_Stratified.csv"
            ),
            sep=",",
        )

        self.config = {
            "label_column": "label",
            "validation_seed": 1,
            "number_of_folds": 5,
        }

    def test_skf_generate_validation(self):

        self.cv = StratifiedKFoldCrossValidation(self.config, self.data)
        self.cv.generate_validation(**self.config)

        from sklearn.model_selection import StratifiedKFold

        cv = StratifiedKFold(self.config["number_of_folds"])

        for index, (train, test) in enumerate(
            cv.split(self.data["label"], self.data["label"])
        ):
            np.testing.assert_array_equal(train, self.cv._sets[index].train)
            np.testing.assert_array_equal(test, self.cv._sets[index].validate)

    def test_skf_generate_validation_with_augmentation(self):

        df = copy.deepcopy(self.data)
        df["segment_uuid"] = generate_uuid_list(df.shape[0])
        self.cv = StratifiedKFoldCrossValidation(self.config, df)
        self.cv.generate_validation(**self.config)

        from sklearn.model_selection import StratifiedKFold

        cv = StratifiedKFold(self.config["number_of_folds"])

        for index, (train, validate) in enumerate(
            cv.split(self.cv._data["label"], self.cv._data["label"])
        ):

            indx_train = self.cv._sets[index].train
            indx_validate = self.cv._sets[index].validate
            np.testing.assert_array_equal(
                self.cv._original_indices[validate], indx_validate
            )

            # no augmented segment must be present in the validation set
            assert sum(is_original(df.iloc[indx_validate])) == len(indx_validate)

            # making sure that none of the augmented version of validation segments are in the training set
            check = True
            for idd in df.iloc[indx_train]["segment_uuid"].values:
                if is_augmented(idd):
                    for jdd in df.iloc[indx_validate]["segment_uuid"].values:
                        if similar_root_uuid(idd, jdd):
                            check = False
            assert check


class TestShuffleSplitValidation:
    """Tests the StratifiedKFold cross-validation method."""

    def setup_class(self):
        """Use skateboarding ground data."""

        self.data = pd.read_csv(
            os.path.join(
                "engine", "tests", "data", "Validation_TestCase_Stratified.csv"
            ),
            sep=",",
        )

        self.config = {
            "label_column": "label",
            "validation_seed": 1,
            "number_of_folds": 5,
            "test_size": 0,
            "validation_size": 0.5,
        }

    def test_sss_generate_validation(self):

        self.cv = StratifiedShuffleSplitValidation(self.config, self.data)
        self.cv.generate_validation(**self.config)

        from sklearn.model_selection import StratifiedShuffleSplit

        cv = StratifiedShuffleSplit(
            n_splits=self.config["number_of_folds"],
            test_size=self.config["validation_size"],
            random_state=self.config["validation_seed"],
        )

        for index, (train, test) in enumerate(
            cv.split(self.data["label"], self.data["label"])
        ):
            np.testing.assert_array_equal(train, self.cv._sets[index].train)
            np.testing.assert_array_equal(test, self.cv._sets[index].validate)

    def test_sss_generate_validation_with_augmentation(self):

        df = copy.deepcopy(self.data)
        df["segment_uuid"] = generate_uuid_list(df.shape[0])
        self.cv = StratifiedShuffleSplitValidation(self.config, df)
        self.cv.generate_validation(**self.config)

        from sklearn.model_selection import StratifiedShuffleSplit

        cv = StratifiedShuffleSplit(
            n_splits=self.config["number_of_folds"],
            test_size=self.config["validation_size"],
            random_state=self.config["validation_seed"],
        )

        for index, (train, validate) in enumerate(
            cv.split(self.cv._data["label"], self.cv._data["label"])
        ):

            indx_train = self.cv._sets[index].train
            indx_validate = self.cv._sets[index].validate
            np.testing.assert_array_equal(
                self.cv._original_indices[validate], indx_validate
            )

            # no augmented segment must be present in the validation set
            assert sum(is_original(df.iloc[indx_validate])) == len(indx_validate)

            # making sure that none of the augmented version of validation segments are in the training set
            check = True
            for idd in df.iloc[indx_train]["segment_uuid"].values:
                if is_augmented(idd):
                    for jdd in df.iloc[indx_validate]["segment_uuid"].values:
                        if similar_root_uuid(idd, jdd):
                            check = False
            assert check


class TestSplitByMetadataValue:
    """Tests the StratifiedKFold cross-validation method."""

    def setup_class(self):
        """Use skateboarding ground data."""

        train_set = pd.read_csv(
            os.path.join("engine", "tests", "data", "Iris_train.csv")
        )
        train_set["label"] += 1
        train_set["trainOrtest"] = "train"
        test_set = pd.read_csv(os.path.join("engine", "tests", "data", "Iris_test.csv"))
        test_set["label"] += 1
        test_set["trainOrtest"] = "test"
        self.data = pd.concat([train_set, test_set], ignore_index=True)

        self.config = {
            "label_column": "label",
            "validation_seed": 1,
            "test_size": 0,
            "metadata_name": "trainOrtest",
            "training_values": ["train"],
            "validation_values": ["test"],
            "group_columns": ["trainOrtest"],
        }

        self.cv = SplitByMetadataValue(self.config, self.data)

    def test_smv_generate_validation(self):
        self.cv.generate_validation(**self.config)

        train_index_ref = range(0, 60)
        test_index_ref = range(60, 90)

        for data_set in self.cv._sets:
            np.testing.assert_array_equal(train_index_ref, data_set.train)
            np.testing.assert_array_equal(test_index_ref, data_set.validate)


class TestStratifiedValidation_2:
    """Tests the StratifiedKFold cross-validation method."""

    def setup_class(self):
        """Use skateboarding ground data."""

        self.data = pd.read_csv(
            os.path.join(
                "engine", "tests", "data", "Validation_TestCase_Stratified.csv"
            ),
            sep=",",
        )

        self.config = {
            "label_column": "label",
            "validation_seed": 1,
            "number_of_folds": 5,
        }

        self.cv = StratifiedKFoldCrossValidation(self.config, self.data)

    def test_skf_generate_validation(self):

        self.cv.generate_validation(**self.config)
        self.cv.next_validation()

        ground_data = pd.read_csv(
            os.path.join(
                "engine", "tests", "data", "Validation_TestCase_Stratified_Ref.csv"
            ),
            sep=",",
        )

        assert 5 == len(self.cv._sets)
        np.testing.assert_array_equal(
            np.array(ground_data).flatten(), self.cv._current_set.train
        )


class TestStratifiedShuffleSplitValidation_2:
    """Tests the StratifiedKFold cross-validation method."""

    def setup_class(self):
        """Use skateboarding ground data."""

        self.data = pd.read_csv(
            os.path.join(
                "engine", "tests", "data", "Validation_TestCase_Stratified.csv"
            ),
            sep=",",
        )

        self.config = {
            "label_column": "label",
            "validation_seed": 1,
            "number_of_folds": 5,
            "test_size": 0.2,
            "validation_size": 0.5,
        }

        self.cv = StratifiedShuffleSplitValidation(self.config, self.data)

    def test_sss_generate_validation_reserve(self):

        self.cv.generate_validation(**self.config)
        self.cv.next_validation()

        assert self.config["number_of_folds"] == len(self.cv._sets)
        assert 60 == len(self.cv._current_set.train)
        assert 100 == len(self.cv._current_set.validate)
        assert 40 == len(self.cv._current_set.test)

    def test_sss_generate_validation_no_reserve(self):

        self.config = {
            "label_column": "label",
            "validation_seed": 1,
            "number_of_folds": 7,
            "validation_size": 0.5,
            "test_size": 0,
        }

        cv = StratifiedShuffleSplitValidation(self.config, self.data)

        cv.generate_validation(**self.config)
        cv.next_validation()

        assert self.config["number_of_folds"] == len(cv._sets)
        assert 100 == len(cv._current_set.train)
        assert 100 == len(cv._current_set.validate)
        assert 0 == len(cv._current_set.test)


@pytest.mark.skip()
class TestSetSampleValidation:
    """Tests the Set Sampler method."""

    def setup_class(self):
        """Use randomly generated data."""
        data_array = np.array(
            [
                [106, 156],
                [97, 185],
                [90, 161],
                [103, 201],
                [101, 139],
                [81, 178],
                [89, 162],
                [108, 161],
                [86, 193],
                [96, 156],
                [95, 174],
                [105, 144],
                [92, 173],
                [90, 155],
                [94, 151],
                [112, 160],
                [107, 143],
                [90, 195],
                [89, 191],
                [102, 165],
                [100, 131],
                [98, 183],
                [98, 148],
                [110, 177],
                [86, 177],
                [98, 151],
                [82, 169],
                [96, 136],
                [110, 137],
                [99, 134],
                [101, 161],
                [106, 143],
                [88, 102],
                [108, 150],
                [111, 155],
                [118, 140],
                [98, 153],
                [100, 143],
                [88, 159],
                [98, 168],
                [102, 154],
                [101, 153],
                [92, 157],
                [94, 160],
                [91, 120],
                [83, 150],
                [101, 172],
                [91, 132],
                [101, 129],
                [109, 147],
                [94, 154],
                [96, 141],
                [85, 157],
                [101, 169],
                [98, 114],
                [97, 177],
                [88, 136],
                [116, 165],
                [108, 170],
                [110, 158],
                [92, 115],
                [92, 146],
                [100, 111],
                [103, 176],
                [119, 147],
                [97, 187],
                [106, 147],
                [96, 157],
                [92, 143],
                [86, 152],
                [107, 122],
                [111, 175],
                [113, 110],
                [112, 135],
                [99, 175],
                [83, 143],
                [121, 144],
                [116, 196],
                [105, 166],
                [99, 186],
                [85, 152],
                [104, 134],
                [101, 147],
                [97, 157],
                [105, 160],
                [105, 161],
                [90, 160],
                [90, 115],
                [117, 162],
                [100, 180],
                [92, 151],
                [89, 136],
                [106, 170],
                [120, 132],
                [107, 129],
                [99, 174],
                [100, 141],
                [99, 116],
                [106, 151],
                [95, 141],
            ]
        )
        features = pd.DataFrame(data_array, columns=["feature1", "feature2"])
        features["label"] = 1
        data_array = np.array(
            [
                [195, 52],
                [210, 42],
                [204, 52],
                [200, 49],
                [204, 50],
                [193, 49],
                [201, 47],
                [202, 45],
                [193, 45],
                [189, 46],
                [203, 47],
                [197, 52],
                [195, 49],
                [211, 51],
                [207, 46],
                [198, 46],
                [214, 49],
                [200, 50],
                [197, 49],
                [207, 50],
                [195, 58],
                [198, 43],
                [202, 40],
                [205, 55],
                [198, 54],
                [197, 54],
                [205, 51],
                [198, 42],
                [205, 53],
                [202, 48],
                [206, 46],
                [200, 49],
                [199, 46],
                [201, 44],
                [194, 48],
                [207, 41],
                [200, 44],
                [201, 50],
                [195, 47],
                [196, 50],
                [201, 48],
                [212, 53],
                [194, 49],
                [204, 45],
                [207, 53],
                [205, 43],
                [204, 45],
                [197, 51],
                [191, 59],
                [197, 51],
                [188, 52],
                [205, 50],
                [209, 41],
                [201, 54],
                [192, 49],
                [200, 48],
                [197, 47],
                [200, 52],
                [204, 54],
                [212, 51],
                [202, 51],
                [196, 44],
                [204, 55],
                [192, 53],
                [197, 40],
                [195, 61],
                [195, 47],
                [196, 53],
                [208, 37],
                [203, 49],
                [197, 49],
                [198, 57],
                [206, 48],
                [203, 54],
                [204, 48],
                [204, 56],
                [193, 42],
                [209, 52],
                [197, 53],
                [201, 44],
                [212, 42],
                [199, 53],
                [205, 61],
                [191, 48],
                [200, 42],
                [196, 53],
                [203, 46],
                [199, 45],
                [193, 40],
                [202, 48],
                [200, 47],
                [202, 52],
                [198, 50],
                [203, 53],
                [198, 53],
                [203, 49],
                [194, 53],
                [198, 50],
                [201, 47],
                [203, 56],
            ]
        )
        data = pd.DataFrame(data_array, columns=["feature1", "feature2"])
        data["label"] = 2
        self.data = features.append(data).reset_index(drop=True)

        self.ssv_config = {
            "validation_method": "set sample validation",
            "data_columns": ["feature1", "feature2"],
            "label_column": "label",
            "retries": 50,
            "norm": "L1",
            "samples_per_class": {1: 30, 2: 29},
            "validation_samples_per_class": {},
            "binary_class1": "",
            "set_mean": {},
            "set_stdev": {},
            "mean_limit": {},
            "stdev_limit": {},
            "optimize_mean_std": "both",
        }

        self.ssv = SetSampleValidation(self.ssv_config, self.data)
        self.ss = SetSampler(
            self.ssv._data_columns,
            self.ssv._label_column,
            retries=self.ssv._retries,
            norm=self.ssv._norm,
            optimize_mean_std=self.ssv._optimize_mean_std,
            random_state=np.random.RandomState(256),
        )

    def test_ssv_generate_validation_reserve(self):

        self.ssv._sets = []
        self.ssv.generate_validation(reserve_test=True)
        for data_set in self.ssv._sets:
            total_num_samples = 0
            for c in self.ssv_config["samples_per_class"]:
                total_num_samples += self.ssv_config["samples_per_class"][c]
            # Test whether the subsets have the correct number of samples and are mutually exclusive.
            np.testing.assert_equal(
                len(data_set.train),
                total_num_samples,
                err_msg="Training set does not have the requested number of samples.",
            )
            np.testing.assert_equal(
                len(data_set.validate),
                total_num_samples,
                err_msg="Validation set does not have the requested number of samples.",
            )
            np.testing.assert_equal(
                len(data_set.test),
                total_num_samples,
                err_msg="Test set does not have the requested number of samples.",
            )
            # Test whether the subsets are mutually exclusive.
            np.testing.assert_equal(
                set(data_set.train).intersection(set(data_set.validate)),
                set([]),
                err_msg="Training and validation sets are not mutually exclusive.",
            )
            np.testing.assert_equal(
                set(data_set.train).intersection(set(data_set.test)),
                set([]),
                err_msg="Training and testing sets are not mutually exclusive.",
            )
            np.testing.assert_equal(
                set(data_set.validate).intersection(set(data_set.test)),
                set([]),
                err_msg="Validation and testing sets are not mutually exclusive.",
            )

        return

    def test_ssv_generate_validation_no_reserve(self):

        self.ssv._sets = []
        self.ssv.generate_validation(reserve_test=False)
        for data_set in self.ssv._sets:
            total_num_samples = 0
            for c in self.ssv_config["samples_per_class"]:
                total_num_samples += self.ssv_config["samples_per_class"][c]
            # Test whether the subsets have the correct number of samples.
            np.testing.assert_equal(
                len(data_set.train),
                total_num_samples,
                err_msg="Training set does not have the requested number of samples.",
            )
            np.testing.assert_equal(
                len(data_set.validate),
                total_num_samples,
                err_msg="Validation set does not have the requested number of samples.",
            )
            np.testing.assert_equal(
                len(data_set.test),
                0,
                err_msg="Test set does not have the requested number of samples.",
            )
            # Test whether the subsets are mutually exclusive.
            np.testing.assert_equal(
                set(data_set.train).intersection(set(data_set.validate)),
                set([]),
                err_msg="Training and validation sets are not mutually exclusive.",
            )
            np.testing.assert_equal(
                set(data_set.train).intersection(set(data_set.test)),
                set([]),
                err_msg="Training and testing sets are not mutually exclusive.",
            )
            np.testing.assert_equal(
                set(data_set.validate).intersection(set(data_set.test)),
                set([]),
                err_msg="Validation and testing sets are not mutually exclusive.",
            )

    def test_ss_setsample_classes(self):
        data_set_mean = {}
        data_set_stdev = {}
        for c in self.data["label"].unique():
            data_set_mean[c] = self.data[self.data["label"] == c][
                self.ssv_config["data_columns"]
            ].mean()
            data_set_stdev[c] = self.data[self.data["label"] == c][
                self.ssv_config["data_columns"]
            ].std()
        subset, remainder = self.ss.setsample_classes(
            self.data,
            data_set_mean,
            data_set_stdev,
            self.ssv_config["samples_per_class"],
            self.ssv_config["mean_limit"],
            self.ssv_config["stdev_limit"],
        )
        expected_subset = {1: 30, 2: 29}
        expected_remainder = {1: 70, 2: 71}
        for c in self.data["label"].unique():
            np.testing.assert_equal(
                len(subset[subset["label"] == c]),
                expected_subset[c],
                err_msg="Subset size is not requested size.",
            )
            np.testing.assert_equal(
                len(remainder[remainder["label"] == c]),
                expected_remainder[c],
                err_msg="Remainder size is not requested size.",
            )
        np.testing.assert_equal(
            set(subset.index).intersection(set(remainder.index)),
            set([]),
            err_msg="Subset and remainder sets are not mutually exclusive.",
        )

    def test_ss_get_subset(self):

        class_data = self.ssv._set_data[self.ssv._set_data["label"] == 1][
            ["feature1", "feature2"]
        ]
        class_data_mean = class_data.mean()
        class_data_stdev = class_data.std()
        class_subset_size = 30
        mean_limit = np.array([1, 1])
        stdev_limit = np.array([1, 1])
        subset_remainder = self.ss.get_subset(
            class_data,
            class_data_mean,
            class_data_stdev,
            class_subset_size,
            mean_limit=mean_limit,
            stdev_limit=mean_limit,
        )

        # Test whether subset and remainder are the correct size.
        np.testing.assert_equal(
            len(subset_remainder["subset"]),
            class_subset_size,
            err_msg="Subset size is not requested size.",
        )
        np.testing.assert_equal(
            len(subset_remainder["remainder"]),
            len(class_data) - class_subset_size,
            err_msg="Remainder size is not expected size.",
        )

        # Test whether the subset and remainder are mutually exclusive.
        np.testing.assert_equal(
            set(subset_remainder["subset"].index).intersection(
                set(subset_remainder["remainder"].index)
            ),
            set([]),
            err_msg="Subset and remainder sets are not mutually exclusive.",
        )

        # Test whether the subset is within the acceptible statistical limits, or if close.
        subset_mean = subset_remainder["subset"].mean()
        assert (
            np.abs(subset_mean - class_data_mean).sum() < mean_limit.sum()
        ), "Subset mean is not close to the mean of the full data set."

        subset_stdev = subset_remainder["subset"].std()
        assert (
            np.abs(subset_stdev - class_data_stdev).sum() < stdev_limit.sum()
        ), "Subset stdev is not close to the mean of the full data set."

    def test_ss_remap_keys_to_integers(self):
        # Test whether the reverse map is consistent with the class labels
        class_size_dict = self.ssv_config["samples_per_class"]
        class_map, reverse_map = self.ss.remap_keys_to_integers(class_size_dict)

        np.testing.assert_equal(
            reverse_map[1],
            self.ssv._set_data.ix[0]["label"],
            err_msg="Reverse map does not match data labels.",
        )
        np.testing.assert_equal(
            reverse_map[2],
            self.ssv._set_data.ix[100]["label"],
            err_msg="Reverse map does not match data labels.",
        )
        np.testing.assert_equal(
            class_map[self.ssv._set_data.ix[0]["label"]],
            1,
            err_msg="Class map does not match data labels.",
        )
        np.testing.assert_equal(
            class_map[self.ssv._set_data.ix[100]["label"]],
            2,
            err_msg="Class map does not match data labels.",
        )

    def test_ss_reduce_to_binary_classes(self):
        # Test whether binary classes are the corect sizes
        data_binary, other_classes = self.ss.reduce_to_binary_classes(
            self.data, 1, label_column="label"
        )
        np.testing.assert_equal(
            len(data_binary[data_binary["label"] == 1]),
            100,
            err_msg="Working class has wrong number of elements.",
        )
        np.testing.assert_equal(
            len(data_binary[data_binary["label"] == 2]),
            100,
            err_msg="Other class has wrong number of elements.",
        )


class TestMetadataAndLabelKfold:
    def test_smv_generate_validation(self):

        config = {
            "label_column": "Label",
            "group_columns": ["Group"],
            "number_of_folds": 2,
            "metadata_name": "Group",
        }

        data = pd.DataFrame(
            {
                0: [1, 2, 3, 4, 5, 6, 6, 6, 7, 8, 9, 10, 11],
                "Group": [3, 0, 3, 0, 3, 3, 2, 0, 1, 4, 4, 4, 4],
                "Label": [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
            }
        )

        validator = MetadataAndLabelKFoldValidation(config, data)
        validator.generate_validation()

        validator_set = next(validator._sets_iterator)
        train_index = validator_set.train
        test_index = validator_set.validate

        assert_array_equal(train_index, [1, 3, 6, 7])
        assert_array_equal(test_index, [0, 2, 4, 5, 8, 9, 10, 11, 12])

        validator_set = next(validator._sets_iterator)
        train_index = validator_set.train
        test_index = validator_set.validate

        assert_array_equal(train_index, [0, 2, 4, 5, 8, 9, 10, 11, 12])
        assert_array_equal(test_index, [1, 3, 6, 7])

    def test_smv_generate_validation_with_augmentation(self):

        config = {
            "label_column": "Label",
            "group_columns": ["Group"],
            "number_of_folds": 2,
            "metadata_name": "Group",
        }

        df = pd.DataFrame(
            {
                0: [1, 2, 3, 4, 5, 6, 6, 6, 7, 8, 9, 10, 11],
                "Group": [3, 0, 3, 0, 3, 3, 2, 0, 1, 4, 4, 4, 4],
                "Label": [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
            }
        )
        df["segment_uuid"] = generate_uuid_list(df.shape[0])

        validator = MetadataAndLabelKFoldValidation(config, df)
        validator.generate_validation()

        validator_set = next(validator._sets_iterator)
        train_index = validator_set.train
        validate_index = validator_set.validate

        train_groups = set(
            df.iloc[train_index][["Group", "Label"]]
            .apply(lambda row: "/".join([str(r) for r in row]), axis=1)
            .values
        )

        validate_groups = set(
            df.iloc[validate_index][["Group", "Label"]]
            .apply(lambda row: "/".join([str(r) for r in row]), axis=1)
            .values
        )

        # testing for group overlaps between validation and training sets after augmentation
        for g in validate_groups:
            assert not g in train_groups

    def test_group_and_label_kfold(self):
        rng = np.random.RandomState(0)

        # Parameters of the test
        n_groups = 15
        n_samples = 1000
        n_splits = 5
        n_classes = 5

        X = np.ones(n_samples)

        # Construct the test data
        tolerance = 0.05 * n_samples  # 5 percent error allowed
        groups = rng.randint(0, n_groups, n_samples)
        y = rng.randint(0, n_classes, n_samples)

        ideal_n_groups_per_fold = n_samples // n_splits

        len(np.unique(groups))
        # Get the test fold indices from the test set indices of each fold
        folds = np.zeros(n_samples)
        lkf = GroupAndLabelKFold(n_splits=n_splits)
        for i, (_, test) in enumerate(lkf.split(X, y, groups)):
            folds[test] = i

        # Check that folds have approximately the same size
        assert len(folds) == len(groups)
        for i in np.unique(folds):
            assert tolerance >= abs(sum(folds == i) - ideal_n_groups_per_fold)

        lkf = GroupAndLabelKFold(n_splits=2)

        groups = np.array([3, 0, 3, 0, 3, 3, 2, 0, 1])

        y = np.array([1, 1, 1, 1, 1, 2, 2, 2, 2])

        X = np.array([1, 2, 3, 4, 5, 6, 6, 6, 7])

        splits = lkf.split(X, y, groups)

        train_index, test_index = next(splits)

        assert_array_equal(train_index, [1, 3, 6, 7])
        assert_array_equal(test_index, [0, 2, 4, 5, 8])

        train_index, test_index = next(splits)

        assert_array_equal(train_index, [0, 2, 4, 5, 8])
        assert_array_equal(test_index, [1, 3, 6, 7])

        groups = np.array([3, 0, 3, 0, 3, 3, 2, 0, 1, 4, 4, 4, 4])
        y = np.array([1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])
        X = np.array([1, 2, 3, 4, 5, 6, 6, 6, 7, 8, 9, 10, 11])

        splits = lkf.split(X, y, groups)

        train_index, test_index = next(splits)

        assert_array_equal(train_index, [1, 3, 6, 7])
        assert_array_equal(test_index, [0, 2, 4, 5, 8, 9, 10, 11, 12])

        train_index, test_index = next(splits)

        assert_array_equal(train_index, [0, 2, 4, 5, 8, 9, 10, 11, 12])
        assert_array_equal(test_index, [1, 3, 6, 7])


class TestMetadataKfold:
    def test_metadata_generate_validation(self):

        config = {
            "label_column": "Label",
            "group_columns": ["Group"],
            "number_of_folds": 2,
            "metadata_name": "Group",
        }

        data = pd.DataFrame(
            {
                0: [1, 2, 3, 4, 5, 6, 6, 6, 7, 8, 9, 10, 11],
                "Group": [3, 0, 3, 0, 3, 3, 2, 0, 1, 4, 4, 4, 4],
                "Label": [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
            }
        )

        validator = MetadataKFoldValidation(config, data)
        validator.generate_validation()

        validator_set = next(validator._sets_iterator)
        train_index = validator_set.train
        test_index = validator_set.validate

        assert_array_equal(train_index, [0, 2, 4, 5, 6, 8])
        assert_array_equal(test_index, [1, 3, 7, 9, 10, 11, 12])

        validator_set = next(validator._sets_iterator)
        train_index = validator_set.train
        test_index = validator_set.validate

        assert_array_equal(train_index, [1, 3, 7, 9, 10, 11, 12])
        assert_array_equal(test_index, [0, 2, 4, 5, 6, 8])

    def test_metadata_generate_validation_with_augmentation(self):

        config = {
            "label_column": "Label",
            "group_columns": ["Group"],
            "number_of_folds": 2,
            "metadata_name": "Group",
        }

        df = pd.DataFrame(
            {
                0: [1, 2, 3, 4, 5, 6, 6, 6, 7, 8, 9, 10, 11],
                "Group": [3, 0, 3, 0, 3, 3, 2, 0, 1, 4, 4, 4, 4],
                "Label": [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
            }
        )
        df["segment_uuid"] = generate_uuid_list(df.shape[0])

        validator = MetadataKFoldValidation(config, df)
        validator.generate_validation()

        validator_set = next(validator._sets_iterator)
        train_index = validator_set.train
        validate_index = validator_set.validate

        train_groups = set(df.iloc[train_index]["Group"].values)
        validate_groups = set(df.iloc[validate_index]["Group"].values)

        for g in validate_groups:
            assert not g in train_groups

        # making sure that none of the augmented version of validation segments are in the training set
        check = True
        for idd in df.iloc[train_index]["segment_uuid"].values:
            if is_augmented(idd):
                for jdd in df.iloc[validate_index]["segment_uuid"].values:
                    if similar_root_uuid(idd, jdd):
                        check = False
        assert check
