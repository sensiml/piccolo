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
import pytest
from pandas import DataFrame

from library.model_validation.validation_method import ValidationMethod, ValidationSet


class TestValidationMethod:
    """
    Tests the ValidationMethod base class.
    """

    df = DataFrame(
        {
            "Alabel": [0, 0, 1, 1, 0, 0, 1, 1, 0, 1],
            "Bfeature1": np.random.randn(10),
            "Cgroup2": [3, 3, 4, 4, 4, 3, 3, 4, 4, 4],
            "Dfeature2": np.random.randn(10),
            "Eunused1": np.random.randn(10),
            "Ffeature3": np.random.randn(10),
            "Ggroup1": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
        }
    )

    class mockValidation(ValidationMethod):
        def generate_validation(self, **kwargs):
            self._sets.extend(
                [
                    ValidationSet([0, 1, 2, 3], [4, 5, 6, 7, 8, 9], []),
                    ValidationSet([4, 6, 8], [0, 1, 2, 3], [5, 7, 9]),
                ]
            )
            self._is_generated = True
            return len(self._sets)

    @pytest.fixture(autouse=True)
    def setup(self):
        # Provide only mandatory fields initially
        self.config = {"label_column": "Alabel"}
        self.data = self.df.copy()

    def test_sort_columns(self):
        new_columns, new_features = ValidationMethod.sort_columns(
            self.data.columns, self.config["label_column"]
        )
        expected_columns = [
            "Bfeature1",
            "Cgroup2",
            "Dfeature2",
            "Eunused1",
            "Ffeature3",
            "Ggroup1",
            "Alabel",
        ]
        expected_features = [
            "Bfeature1",
            "Cgroup2",
            "Dfeature2",
            "Eunused1",
            "Ffeature3",
            "Ggroup1",
        ]
        assert expected_columns == new_columns
        assert expected_features == new_features

    def test_sort_columns_with_unused(self):
        new_columns, new_features = ValidationMethod.sort_columns(
            self.data.columns, self.config["label_column"], unused=["Eunused1"]
        )
        expected_columns = [
            "Bfeature1",
            "Cgroup2",
            "Dfeature2",
            "Ffeature3",
            "Ggroup1",
            "Alabel",
        ]
        expected_features = [
            "Bfeature1",
            "Cgroup2",
            "Dfeature2",
            "Ffeature3",
            "Ggroup1",
        ]
        assert expected_columns == new_columns
        assert expected_features == new_features

    def test_sort_columns_with_multi_unused(self):
        new_columns, new_features = ValidationMethod.sort_columns(
            self.data.columns,
            self.config["label_column"],
            unused=["Eunused1", "Cgroup2"],
        )
        expected_columns = ["Bfeature1", "Dfeature2", "Ffeature3", "Ggroup1", "Alabel"]
        expected_features = ["Bfeature1", "Dfeature2", "Ffeature3", "Ggroup1"]
        assert expected_columns == new_columns
        assert expected_features == new_features

    def test_sort_columns_with_groupby(self):
        new_columns, new_features = ValidationMethod.sort_columns(
            self.data.columns, self.config["label_column"], group_columns=["Ggroup1"]
        )
        expected_columns = [
            "Bfeature1",
            "Cgroup2",
            "Dfeature2",
            "Eunused1",
            "Ffeature3",
            "Ggroup1",
            "Alabel",
        ]
        expected_features = [
            "Bfeature1",
            "Cgroup2",
            "Dfeature2",
            "Eunused1",
            "Ffeature3",
        ]
        assert expected_columns == new_columns
        assert expected_features == new_features

    def test_sort_columns_with_multi_groupby(self):
        new_columns, new_features = ValidationMethod.sort_columns(
            self.data.columns,
            self.config["label_column"],
            group_columns=["Ggroup1", "Cgroup2"],
        )
        expected_columns = [
            "Bfeature1",
            "Dfeature2",
            "Eunused1",
            "Ffeature3",
            "Ggroup1",
            "Cgroup2",
            "Alabel",
        ]
        expected_features = ["Bfeature1", "Dfeature2", "Eunused1", "Ffeature3"]
        assert expected_columns == new_columns
        assert expected_features == new_features

    def test_sort_columns_with_feature(self):
        new_columns, new_features = ValidationMethod.sort_columns(
            self.data.columns,
            self.config["label_column"],
            feature_columns=["Ffeature3"],
        )
        expected_columns = [
            "Ffeature3",
            "Bfeature1",
            "Cgroup2",
            "Dfeature2",
            "Eunused1",
            "Ggroup1",
            "Alabel",
        ]
        expected_features = [
            "Ffeature3",
            "Bfeature1",
            "Cgroup2",
            "Dfeature2",
            "Eunused1",
            "Ggroup1",
        ]
        assert expected_columns == new_columns
        assert expected_features == new_features

    def test_sort_columns_with_multi_feature(self):
        new_columns, new_features = ValidationMethod.sort_columns(
            self.data.columns,
            self.config["label_column"],
            feature_columns=["Ffeature3", "Dfeature2"],
        )
        expected_columns = [
            "Ffeature3",
            "Dfeature2",
            "Bfeature1",
            "Cgroup2",
            "Eunused1",
            "Ggroup1",
            "Alabel",
        ]
        expected_features = [
            "Ffeature3",
            "Dfeature2",
            "Bfeature1",
            "Cgroup2",
            "Eunused1",
            "Ggroup1",
        ]
        assert expected_columns == new_columns
        assert expected_features == new_features

    def test_sort_columns_with_full_config(self):
        new_columns, new_features = ValidationMethod.sort_columns(
            self.data.columns,
            self.config["label_column"],
            unused=["Eunused1"],
            group_columns=["Ggroup1", "Cgroup2"],
            feature_columns=["Ffeature3", "Dfeature2"],
        )
        expected_columns = [
            "Ffeature3",
            "Dfeature2",
            "Bfeature1",
            "Ggroup1",
            "Cgroup2",
            "Alabel",
        ]
        expected_features = ["Ffeature3", "Dfeature2", "Bfeature1"]
        assert expected_columns == new_columns
        assert expected_features == new_features

    def test_constructor(self):
        new_vm = ValidationMethod(self.config, self.data)
        assert not (new_vm.is_generated)
        assert not (new_vm.train_indices)
        assert not (new_vm.test_indices)
        assert not (new_vm.validate_indices)

    def test_constructor_with_groupby(self):
        self.config["group_columns"] = ["Ggroup1"]
        new_vm = ValidationMethod(self.config, self.data)

        # Check that the grouping is performed correctly
        assert not (new_vm.is_generated)
        assert 2 == len(new_vm._grouped.groups)
        assert self.config["group_columns"] == new_vm._group_columns

    def test_constructor_subclass(self):
        new_vm = self.mockValidation(self.config, self.data)

        # Check that new_vm is an instance of ValidationMethod
        assert isinstance(new_vm, ValidationMethod)
        assert not (new_vm.is_generated)

    def test_generate_validations_subclass(self):
        new_vm = self.mockValidation(self.config, self.data)

        # Check return value from subclass.generate_validations
        assert 2 == new_vm.generate_validation()
        assert new_vm.is_generated

    def test_next_validation(self):
        new_vm = self.mockValidation(self.config, self.data)
        total_sets = new_vm.generate_validation()

        # Check that current set is populated
        for i in range(total_sets):
            train_data, validate_data, test_data = new_vm.next_validation()
            assert 7 == train_data.shape[1]
            assert 7 == validate_data.shape[1]
            assert [] != new_vm.train_indices
            assert [] != new_vm.validate_indices

        # Last set has test_data (and test_indices) populated
        assert 7 == test_data.shape[1]
        assert [] != new_vm.test_indices

    def test_next_validation_raises_past_last_index(self):
        new_vm = self.mockValidation(self.config, self.data)
        total_sets = new_vm.generate_validation()

        for i in range(total_sets):
            new_vm.next_validation()

        # Check that the following call raises a StopIteration exception

        raised_exception = False
        try:
            new_vm.next_validation()
        except StopIteration:
            raised_exception = True

        assert raised_exception

    def test_reserve_test_set(self):
        new_vm = ValidationMethod(self.config, self.data)
        labels, test_indices = new_vm.reserve_test_set(
            True, test_size=0.2, random_state=0
        )

        # Check that two rows are reserved for testing-- random_state seeds the random generator
        assert (8,) == labels.shape
        np.testing.assert_array_equal(np.array([8, 7]), test_indices)

    def test_reserve_test_set_none(self):
        new_vm = ValidationMethod(self.config, self.data)
        labels, test_indices = new_vm.reserve_test_set(
            False, test_size=0.2, random_state=0
        )

        # Check that no rows are reserved for testing-- extra args don't have an effect
        assert (10,) == labels.shape
        assert [] == test_indices

    def test_permute_indices(self):
        self.config.update(
            {
                "ignore_columns": ["Eunused1"],
                "group_columns": ["Ggroup1", "Cgroup2"],
                "feature_columns": ["Ffeature3", "Dfeature2"],
            }
        )
        new_vm = self.mockValidation(self.config, self.data)
        num_sets = new_vm.generate_validation()

        for set in range(num_sets):
            train_data, validate_data, test_data = new_vm.next_validation()
            train_idx, validate_idx, test_idx = new_vm.permute_indices()
            assert sorted(train_data.index) == sorted(train_idx)
            assert sorted(validate_data.index) == sorted(validate_idx)
            assert sorted(test_data.index) == sorted(test_idx)

    def test_permute_current_set(self):
        self.config.update(
            {
                "ignore_columns": ["Eunused1"],
                "group_columns": ["Ggroup1", "Cgroup2"],
                "feature_columns": ["Ffeature3", "Dfeature2"],
            }
        )
        new_vm = self.mockValidation(self.config, self.data)
        num_sets = new_vm.generate_validation()

        for set in range(num_sets):
            train_data, validate_data, test_data = new_vm.next_validation()
            (
                new_train_data,
                new_validate_data,
                new_test_data,
            ) = new_vm.permute_current_set()
            assert sorted(train_data.index) == sorted(new_train_data.index)
            assert sorted(validate_data.index) == sorted(new_validate_data.index)
            assert sorted(test_data.index) == sorted(new_test_data.index)
            assert 4 == len(new_train_data.columns)
            assert 4 == len(new_validate_data.columns)
            assert 4 == len(new_test_data.columns)

    def test_permute_current_set_fixed_cols(self):
        self.config.update(
            {
                "ignore_columns": ["Eunused1"],
                "group_columns": ["Ggroup1", "Cgroup2"],
                "feature_columns": ["Ffeature3", "Dfeature2"],
            }
        )
        new_vm = self.mockValidation(self.config, self.data)
        num_sets = new_vm.generate_validation()
        num_features = 1

        for set in range(num_sets):
            train_data, validate_data, test_data = new_vm.next_validation()
            (
                new_train_data,
                new_validate_data,
                new_test_data,
            ) = new_vm.permute_current_set(num_features)
            assert sorted(train_data.index) == sorted(new_train_data.index)
            assert sorted(validate_data.index) == sorted(new_validate_data.index)
            assert sorted(test_data.index) == sorted(new_test_data.index)
            assert num_features + 1 == len(new_train_data.columns)
            assert num_features + 1 == len(new_validate_data.columns)
            assert num_features + 1 == len(new_test_data.columns)

    def test_permute_current_set_too_many_cols(self):
        self.config.update(
            {
                "ignore_columns": ["Eunused1"],
                "group_columns": ["Ggroup1", "Cgroup2"],
                "feature_columns": ["Ffeature3", "Dfeature2"],
            }
        )
        new_vm = self.mockValidation(self.config, self.data)
        num_sets = new_vm.generate_validation()

        for set in range(num_sets):
            train_data, validate_data, test_data = new_vm.next_validation()

            raised_exception = False
            try:
                new_vm.permute_current_set(5)
            except:
                raised_exception = True

            assert raised_exception
