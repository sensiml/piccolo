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

import logging

import numpy as np
from library.model_validation.validation_method import (
    ValidationError,
    ValidationMethod,
    ValidationSet,
)
from numpy import abs, array, ones, zeros
from numpy.random import choice, seed
from pandas import DataFrame, concat
from sklearn.model_selection import (
    GroupKFold,
    LeaveOneGroupOut,
    StratifiedKFold,
    StratifiedShuffleSplit,
    train_test_split,
)
from sklearn.model_selection._split import _BaseKFold
from sklearn.utils.validation import check_array

logger = logging.getLogger(__name__)


def get_validation_method(config, data):
    """
    Gets a ValidationMethod instance with the given configuration and feature data.
    :NOTE: Hard-coded options (below) means no user-uploaded validation methods will be supported.
    :param config: A configuration dictionary suitable for instantiating a ValidationMethod object.
    :param data: A feature dataframe, including all desired features, label, and group columns \
        (and other non-feature columns identified in config['ignore_columns'])
    :return: an instantiated ValidationMethod object.
    """
    # Allowable validation methods-- add new entries below
    allowable_methods = {
        "k_fold_strat": StratifiedKFoldCrossValidation,
        "stratified k-fold cross-validation": StratifiedKFoldCrossValidation,
        "leave-one-subject-out": LeaveOneGroupOutValidation,
        "shuffle": StratifiedShuffleSplitValidation,
        "set sample validation": SetSampleValidation,
        "stratified shuffle split": StratifiedShuffleSplitValidation,
        "split by metadata value": SplitByMetadataValue,
        "recall": Recall,
        "stratified metadata k-fold": MetadataAndLabelKFoldValidation,
        "metadata k-fold": MetadataKFoldValidation,
    }

    try:
        validation_method_type = config["validation_method"].lower()
    except:
        raise ValidationError(
            "No validation_method supplied in train-validate-optimize pipeline step."
        )

    try:
        validation_method = allowable_methods[validation_method_type]
    except:
        msg = "Supplied validation_method ({0}) does not match an existing configuration. Allowable methods are:\n  {1} ".format(
            validation_method_type, "\n  ".join(list(allowable_methods.keys()))
        )
        raise ValidationError(msg)

    return validation_method(config, data)


class Recall(ValidationMethod):
    """Simplest validation method possible -- re-recognize the training set"""

    def __init__(self, config, data):
        super(Recall, self).__init__(config, data)

    def generate_validation(self, **kwargs):
        """Duplicate the training set to create a validation set

        :param kwargs: arguments to pass to sklearn's StratifiedShuffleSplit (e.g. test_size, random_seed)
        """

        if self._random_seed is not None:
            kwargs["random_state"] = int(self._random_seed)

        train_indices = self._data.index
        validate_indices = self._data.index

        train, validate, test = self.add_augmented_indices(
            self._original_indices[train_indices],
            self._original_indices[validate_indices],
            [],
        )

        self._sets.append(ValidationSet(train=train, validate=validate, test=[]))


class StratifiedShuffleSplitValidation(ValidationMethod):
    """
    Splits the data (X) into three sets (training, test, and validation) all
    balanced by the labels (y). The size of each group is controlled
    by the pct parameters.

    :param test_size: the portion of data reserved for testing
    :return: the number of cross-validations generated.
    """

    def __init__(self, config, data):

        super(StratifiedShuffleSplitValidation, self).__init__(config, data)

    def generate_validation(self, **kwargs):

        reserve_test, test_set_args = self.get_test_set_args()

        train_set_args = {
            "test_size": kwargs.get("validation_size", 0.2) / (1 - self._test_size)
        }

        if self._random_seed:
            test_set_args["random_state"] = int(self._random_seed)
            train_set_args["random_state"] = int(self._random_seed)

        indicies, test_indices = self.reserve_test_set(reserve_test, **test_set_args)

        y = self._data.iloc[indicies][self._label_column].values
        X = np.zeros(len(y))

        cv = StratifiedShuffleSplit(n_splits=self._number_of_folds, **train_set_args)

        for train_indices, validate_indices in cv.split(X, y):

            train, validate, test = self.add_augmented_indices(
                self._original_indices[indicies[train_indices]],
                self._original_indices[indicies[validate_indices]],
                self._original_indices[test_indices],
            )

            self._sets.append(
                ValidationSet(
                    train=train,
                    validate=validate,
                    test=test,
                )
            )


class StratifiedKFoldCrossValidation(ValidationMethod):
    def __init__(self, config, data):
        super(StratifiedKFoldCrossValidation, self).__init__(config, data)
        self.shuffle = config.get("shuffle", False)

    def generate_validation(self, **kwargs):
        """
        Generates a set of stratified k-fold cross validations, with optional reserved indices for testing.
        :param reserve_test: whether or not to reserve a set of data, unseen by any training, for final testing
        :param test_size: the portion of data reserved for testing
        :return: the number of cross-validations generated.
        """
        reserve_test, test_set_args = self.get_test_set_args()

        if self._random_seed is not None and self.shuffle:
            kwargs["random_state"] = int(self._random_seed)
            skf_args = {"random_state": int(self._random_seed)}
        else:
            skf_args = {"random_state": None}
            kwargs["random_state"] = None

        indicies, test_indices = self.reserve_test_set(reserve_test, **test_set_args)

        y = self._data.iloc[indicies][self._label_column].values
        X = np.zeros(len(y))

        cv = StratifiedKFold(self._number_of_folds, shuffle=self.shuffle, **skf_args)

        for train_indices, validate_indices in cv.split(X, y):

            train, validate, test = self.add_augmented_indices(
                self._original_indices[indicies[train_indices]],
                self._original_indices[indicies[validate_indices]],
                self._original_indices[test_indices],
            )

            self._sets.append(
                ValidationSet(
                    train=train,
                    validate=validate,
                    test=test,
                )
            )


class LeaveOneGroupOutValidation(ValidationMethod):
    def __init__(self, config, data):
        super(LeaveOneGroupOutValidation, self).__init__(config, data)
        self._group_columns = config["group_columns"]

    def generate_validation(self, **kwargs):
        """
        Generates a set of "leave-one-label-out"-type cross validations, with optional reserved indices for testing.
        "Label" corresponds to each unique set of column values provided in config['group_columns'].
        :param reserve_test:  whether to reserve a set of test data or not
        :param kwargs: arguments to pass so sklearn's StratifiedShuffleSplit (e.g. test_size, random_seed)
        :return: the number of cross-validations generated
        """

        reserve_test, test_set_args = self.get_test_set_args()
        indicies, test_indices = self.reserve_test_set(False, **kwargs)

        # Construct an array of integer labels for the groups
        if len(self._group_columns) > 1:
            # multiple keys returned as tuple
            unique_grps = list(self._grouped.groups.keys())
            group_labels = self._data[self._group_columns].apply(
                lambda row: unique_grps.index(tuple(row[:])), axis=1
            )
        elif len(self._group_columns):
            unique_grps = list(self._grouped.groups.keys())
            group_labels = self._data[self._group_columns[0]].apply(
                lambda row: unique_grps.index(row)
            )
        else:  # shouldn't be trying to leave one group out if we don't have an identified group
            raise ValidationError("No grouping identified with groupby key")

        # Restrict groups to training/validation set (i.e. exclude any test_indices)
        group_labels = group_labels.iloc[indicies]

        # Generate temporary indices from labels
        cv = LeaveOneGroupOut()

        y = self._data.iloc[indicies][self._label_column].values
        X = np.zeros(len(y))

        for train_tmp, validate_tmp in cv.split(X, y, group_labels):

            # Translate label indices to original label indices
            train_indices = group_labels.index[train_tmp]
            validate_indices = group_labels.index[validate_tmp]
            group_key = unique_grps[group_labels[validate_indices].unique()[0]]
            if len(self._group_columns) > 1:
                group_key_str = str(group_key[0])
                for additional_key in range(1, len(self._group_columns)):
                    group_key_str += "/{}".format(group_key[additional_key])
                group_key = group_key_str

            # TODO: make sure after adding the augmented data to the training set
            # wrong validation groups are not presented in the training set
            train, validate, test = self.add_augmented_indices(
                self._original_indices[train_indices],
                self._original_indices[validate_indices],
                self._original_indices[test_indices],
                group_columns=self._group_columns,
                group_key=group_key,
            )

            self._sets.append(
                ValidationSet(
                    train=train,
                    validate=validate,
                    test=test,
                    name=group_key,
                )
            )

    def reserve_test_set(self, reserve_test, **kwargs):
        """
        A method to reserve all observations of a single group for model selection after model tuning.
        This is an override of the default stratified reserve_test_set method.
        :param reserve_test: whether to reserve a set of test data or not
        :param kwargs: arguments to pass to sklearn's StratifiedShuffleSplit (e.g. test_size, random_seed)
        :return: The reduced set of labels for training-validation as a Series
        """

        def group_mask(group_values):
            """Creates a boolean mask DF for easy application of an arbitrary
            number of group column equality criteria."""
            combined_mask = DataFrame()
            for name in self._group_columns:
                mask = self._data[name] == group_values.iloc[0][name]
                combined_mask = concat([combined_mask, mask], axis=1)
            return combined_mask

        # Choose one observation's group columns at random with the random_state

        if reserve_test:
            labels = self._data[self._label_column]
            seed(self._random_seed)
            random_group = self._data.loc[choice(self._data.index, 1)][
                self._group_columns
            ]
            # Reserve all the samples matching the randomly selected group
            mask = group_mask(random_group)
            test_indices = self._data.iloc[mask.all(axis=1)].index
            tv_indices = self._data.iloc[mask.all(axis=1)].index
            new_labels = labels.iloc[tv_indices]  # select out remaining rows
            new_indicies = []
        else:
            test_indices = []
            new_indicies = self._data.index
        return new_indicies, test_indices


class SplitByMetadataValue(ValidationMethod):
    def __init__(self, config, data):
        super(SplitByMetadataValue, self).__init__(config, data)
        self._metadata_name = config["metadata_name"]
        self._training_values = config["training_values"]
        self._validation_values = config["validation_values"]

    def _expand_value_list(self, value_list):
        """Try to cast text values to float and numeric values to string and
        include all coherent representations in the output. This is useful
        when the user wants to split by metadata of ambiguous type."""

        if value_list and isinstance(value_list[0], str):
            try:
                value_list = list(set(value_list).union(map(float, set(value_list))))
            except:
                pass
        elif value_list:
            try:
                value_list = list(set(value_list).union(map(str, set(value_list))))
            except:
                pass
        else:
            raise Exception("No metadata values provided for splitting the dataset.")

        return value_list

    def generate_validation(self, **kwargs):
        """
        Generates a set of cross validations based on the user's desired split
        defined by a metadata column, with optional reserved indices for testing
        (taken from the validation group).

        :param reserve_test:  whether to reserve a set of test data or not
        :param kwargs: arguments to pass to sklearn's StratifiedShuffleSplit (e.g. test_size, random_seed)
        """

        if self._random_seed is not None:
            kwargs["random_state"] = int(self._random_seed)

        # Expand lists of training and validation values to include both numeric and text representations
        self._training_values = self._expand_value_list(self._training_values)
        self._validation_values = self._expand_value_list(self._validation_values)

        train_indices = self._data[
            self._data[self._metadata_name].isin(self._training_values)
        ].index
        validate_indices = self._data[
            self._data[self._metadata_name].isin(self._validation_values)
        ].index

        reserve_test, test_set_args = self.get_test_set_args()
        validate_indices, test_indices = self.reserve_test_set(
            reserve_test, validate_indices, **kwargs
        )

        train, validate, test = self.add_augmented_indices(
            self._original_indices[train_indices],
            self._original_indices[validate_indices],
            self._original_indices[test_indices],
        )

        self._sets.append(
            ValidationSet(
                train=train,
                validate=validate,
                test=test,
            )
        )

    def reserve_test_set(self, reserve_test, indicies, **kwargs):
        """
        A method to reserve a stratified subset of feature data for model selection after model tuning.
        This overrides the superclass method so that test indices are taken from the specified
        validation indices, rather than the whole original set.

        :param reserve_test: whether to reserve a set of test data or not
        :param kwargs: arguments to pass to sklearn's StratifiedShuffleSplit (e.g. test_size, random_seed)
        :return: The reduced set of labels for validation as a Series
        """

        if reserve_test:
            y = self._data.loc[indicies][self._label_column]
            X = np.zeros(len(y))

            cv = StratifiedShuffleSplit(n_splits=1, **kwargs)

            new_indicies, test_indices = next(cv.split(X, y))
        else:
            test_indices = []
            new_indicies = indicies
        return new_indicies, test_indices


class SetSampleValidation(ValidationMethod):
    def __init__(self, config, data):
        super(SetSampleValidation, self).__init__(config, data)
        self._set_data = data
        self._data_columns = self.feature_columns  # config['data_columns']
        self._label_column = self.label_column  # config['label_column']
        self._set_mean = config["set_mean"]
        self._set_stdev = config["set_stdev"]
        self._mean_limit = config["mean_limit"]
        self._stdev_limit = config["stdev_limit"]
        self._samples_per_class = config["samples_per_class"]
        self._optimize_mean_std = config["optimize_mean_std"]
        self._retries = config["retries"]
        self._norm = config["norm"]
        self._validation_samples_per_class = config["validation_samples_per_class"]
        self._binary_class1 = config["binary_class1"]

    def generate_validation(self, reserve_test=False, **kwargs):
        """
        Generates mean-variance-balanced sets from a larger set, with optional reserved indices for testing.
        :param test_size: the portion of data reserved for testing
        """
        # Instantiate a SetSampler object
        ss = SetSampler(
            self._data_columns,
            self._label_column,
            retries=self._retries,
            norm=self._norm,
            optimize_mean_std=self._optimize_mean_std,
        )
        class_map, reverse_map = ss.remap_keys_to_integers(self._samples_per_class)
        # For set composition, use binary decomposition from reduce_to_binary_classes()
        if len(self._binary_class1) != 0:
            binary_class_int = class_map[self._binary_class1]
            self._data, other_classes = ss.reduce_to_binary_classes(
                self._data, class_map[self._binary_class1], self._label_column
            )
            new_samples_per_class = {}
            new_samples_per_class[self._binary_class1] = self._samples_per_class[
                self._binary_class1
            ]
            new_samples_per_class["other"] = 0
            for c in other_classes:
                new_samples_per_class["other"] += self._samples_per_class[
                    reverse_map[c]
                ]
            self._samples_per_class = new_samples_per_class.copy()
            if len(self._validation_samples_per_class) != 0:
                new_samples_per_class[
                    self._binary_class1
                ] = self._validation_samples_per_class[self._binary_class1]
                new_samples_per_class["other"] = 0
                for c in other_classes:
                    new_samples_per_class[
                        "other"
                    ] += self._validation_samples_per_class[reverse_map[c]]
                self._validation_samples_per_class = new_samples_per_class.copy()
            # class_map, reverse_map = ss.remap_keys_to_integers( self._samples_per_class )
            reverse_map = {
                binary_class_int: self._binary_class1,
                other_classes[0]: "other",
            }
        # Get mean, stdev for the features
        if len(self._set_mean) == 0:
            set_mean = {}
            for a in self._data[self._label_column].unique():
                set_mean[reverse_map[a]] = self._data[
                    self._data[self._label_column] == a
                ][self._data_columns].mean()
        else:
            set_mean = self._set_mean
        if len(self._set_stdev) == 0:
            set_stdev = {}
            for a in self._data[self._label_column].unique():
                set_stdev[reverse_map[a]] = self._data[
                    self._data[self._label_column] == a
                ][self._data_columns].std()
        else:
            set_stdev = self._set_stdev
        # Generate sets
        train_subset, remainder = ss.setsample_classes(
            self._data,
            set_mean,
            set_stdev,
            self._samples_per_class,
            self._mean_limit,
            self._stdev_limit,
            reverse_map=reverse_map,
        )
        if len(self._validation_samples_per_class) == 0:
            validation_samples_per_class = self._samples_per_class
        else:
            validation_samples_per_class = self._validation_samples_per_class
        val_subset, remainder = ss.setsample_classes(
            remainder,
            set_mean,
            set_stdev,
            validation_samples_per_class,
            self._mean_limit,
            self._stdev_limit,
            reverse_map=reverse_map,
        )
        test_subset = self.reserve_test_set(
            reserve_test, ss, remainder, set_mean, set_stdev
        )
        # Append indices for the label to the train, validation, and test sets
        train_indices = []
        validate_indices = []
        test_indices = []
        train_indices.extend(train_subset.index.tolist())
        validate_indices.extend(val_subset.index.tolist())
        test_indices.extend(test_subset.index.tolist())

        train, validate, test = self.add_augmented_indices(
            self._original_indices[train_indices],
            self._original_indices[validate_indices],
            self._original_indices[test_indices],
        )

        self._sets.append(ValidationSet(train=train, validate=validate, test=test))

    def reserve_test_set(
        self, reserve_test, set_sampler_obj, validate_remainder, set_mean, set_stdev
    ):
        """
        A method to reserve a  subset of feature data for model selection after model tuning.
        This overrides the superclass method so that test indices are taken from the
        reminder of the validation set, rather than the whole original set.
        :param reserve_test: whether to reserve a set of test data or not
        :param validate_remainder: the remainder of the valadation set sample
        :param set_mean: the mean of the full data set for each class
        :param set_stdev: the stdev of the full data set for each class
        :return: The reduced set of labels for validation as a Series
        """
        if reserve_test:
            test_subset, remainder = set_sampler_obj.setsample_classes(
                validate_remainder,
                set_mean,
                set_stdev,
                self._samples_per_class,
                self._mean_limit,
                self._stdev_limit,
            )
        else:
            test_subset = DataFrame()
        return test_subset


# Internal class for set sampling


class SetSampler:
    """
    Splits the data into a statistically similar (mean, stdev) subset and a remainder.
    May be used iteratively to generate multiple subsets.


    Example:
     samples = {'Class 1':2500, "Class 2":2500}
     validation = {'Class 1':2000, "Class 2":2000}

     client.pipeline.set_validation_method({"name": "Set Sample Validation",
                                         "inputs": {"samples_per_class": samples,
                                                    "validation_samples_per_class": validation}})


    Args:
        data_keys : pandas.core.index.Index or list of columns with feature data
        retries : int, Number of attempts to find a subset with similar statistics
        norm : str, ['Lsup','L1'] Distance norm for determining whether subset is withing user defined limits
        optimize_mean_std : str, , ['both','mean'] Logic to use for optimizing subset.
         If 'mean', then only mean distance must be improved. If 'both', then both mean and stdev must improve.
        random_state : int, Set random subset generator seed if desired.
    """

    def __init__(
        self,
        data_keys,
        label_column,
        retries=50,
        norm="Lsup",
        optimize_mean_std="both",
        random_state=None,
    ):
        self.data_keys = data_keys
        self.retries = retries
        self.norm = norm
        self.optimize_mean_std = optimize_mean_std
        self.random_state = random_state
        self.label_column = label_column
        assert norm in ["L1", "Lsup"], "Norm must be either L1 or Lsup"
        assert optimize_mean_std in [
            "both",
            "mean",
        ], "optimize_mean_std must be either both or mean"

    def get_subset(
        self,
        data,
        data_set_mean,
        data_set_stdev,
        subset_size,
        mean_limit=[],
        stdev_limit=[],
    ):
        """
        Method to return subset and a remainder.
        May be used iteratively to generate multiple subsets.
        The statistical similarity is controled by parameters: mean_limit, stdev_limit
            Parameters
            data : pandas.DataFrame, Feature data scaled to [0,255]
            data_set_mean : numpy.array of floats, mean value of each feature in dataset
            data_set_stdev : numpy.array of floats, standard deviation of each feature in dataset
            subset_size : int, Number of members in subset
            mean_limit : numpy.array of floats,
                minimum acceptable difference between mean of subset and data for any feature
            stdev_limit : numpy.array of floats,
                minimum acceptable difference between standard deviation of subset and data for any feature
            Returns
            opt_sample : dict with the subset, remainder, statistical information, and success for meeting criteria
        """
        assert subset_size < len(
            data
        ), "Requested number of samples in each subset is greater than total samples"
        if (
            len(mean_limit) == 0
        ):  # If no mean_limit given, default is zero for all features
            mean_limit = zeros(len(self.data_keys))
        if len(stdev_limit) == 0:
            stdev_limit = zeros(len(self.data_keys))
        opt_sample = {}  # Container to hold the optimal sample
        # initialize the min_mean to capture the first sample
        min_mean = 1000 * ones(len(self.data_keys))
        min_stdev = 1000 * ones(len(self.data_keys))
        for r in range(self.retries):
            # remainder, subset = train_test_split(data, test_size=subset_size, random_state=prng)
            remainder, subset = train_test_split(
                data, test_size=subset_size, random_state=self.random_state
            )
            mean_diff = abs(subset[self.data_keys].mean() - data_set_mean)
            stdev_diff = abs(subset[self.data_keys].std() - data_set_stdev)

            update = False
            update_opt_mean = False
            update_opt_stdev = False
            if self.norm == "Lsup":
                if min_mean.max() > mean_diff.max():
                    update_opt_mean = True
                if min_stdev.max() > stdev_diff.max():
                    update_opt_stdev = True
            if self.norm == "L1":
                if min_mean.sum() > mean_diff.sum():
                    update_opt_mean = True
                if min_stdev.sum() > stdev_diff.sum():
                    update_opt_stdev = True
            if array(stdev_limit).sum() == 0:
                update_opt_stdev = True  # update best subset without stdev improvement
            if self.optimize_mean_std == "mean" and update_opt_mean:
                update = True  # update best subset without stdev improvement
            if (
                self.optimize_mean_std == "both"
                and update_opt_mean
                and update_opt_stdev
            ):
                update = True  # update best subset with both mean and stdev improvement

            if update:
                min_mean = mean_diff
                min_stdev = stdev_diff
                opt_sample["subset"] = subset
                opt_sample["remainder"] = remainder
                opt_sample["subset_mean"] = min_mean
                opt_sample["subset_stdev"] = min_stdev
                opt_sample["subset_mean_diff_limit"] = min_mean - mean_limit
                opt_sample["subset_stdev_diff_limit"] = min_stdev - stdev_limit
                opt_sample["num_of_attempts"] = [self.retries, self.retries]
                if self.norm == "Lsup":
                    mean_test = (mean_diff - mean_limit).max() < 0
                    stdev_test = (stdev_diff - stdev_limit).max() < 0
                if self.norm == "L1":
                    mean_test = (mean_diff - mean_limit).sum() < 0
                    stdev_test = (stdev_diff - stdev_limit).sum() < 0
                opt_sample["mean_limit_test"] = mean_test
                opt_sample["stdev_limit_test"] = stdev_test
                if mean_test and (
                    sum(stdev_limit) == 0 or self.optimize_mean_std == "mean"
                ):
                    opt_sample["num_of_attempts"] = [r + 1, self.retries]
                    return opt_sample
                if stdev_test and sum(mean_limit) == 0:
                    opt_sample["num_of_attempts"] = [r + 1, self.retries]
                    return opt_sample
                if mean_test and stdev_test:
                    opt_sample["num_of_attempts"] = [r + 1, self.retries]
                    return opt_sample
        return opt_sample

    def setsample_classes(
        self,
        data,
        data_set_mean,
        data_set_stdev,
        class_subset_size,
        mean_limit=[],
        stdev_limit=[],
        reverse_map={},
    ):
        """
        Method to return subset and a remainder for combined classes. Runs self.get_subset
        on each class and then appends the class to generate a subset and remainder with the
        number of events a defined by the user.
        The statistical similarity is controled by parameters: mean_limit, stdev_limit
            Parameters
            data : pandas.DataFrame, Feature data scaled to [0,255]
            data_set_mean : dict of numpy.array of floats,
                minimum acceptable difference between mean of subset and data for any feature for each class
            data_set_stdev : dict of numpy.array of floats,
                minimum acceptable difference between standard deviation of subset and data for any feature for each class
            subset_size : int, Number of members in subset
            mean_limit : dict of numpy.array of floats,
                minimum acceptable difference between mean of subset and data for any feature for each class
            stdev_limit : dict of numpy.array of floats,
                minimum acceptable difference between standard deviation of subset and data for any feature for each class
            Returns
            opt_sample : subset and remainder
        """
        subset = DataFrame([])
        remainder = DataFrame([])
        if len(reverse_map) == 0:
            class_map, reverse_map = self.remap_keys_to_integers(class_subset_size)
        for c in data[self.label_column].unique():
            # Slice the data from that class
            class_data = data[data[self.label_column] == c]
            if len(mean_limit) > 0:
                class_mean_limit = mean_limit[reverse_map[c]]
            else:
                class_mean_limit = []
            if len(stdev_limit) > 0:
                class_stdev_limit = stdev_limit[reverse_map[c]]
            else:
                class_stdev_limit = []
            subset_remainder = self.get_subset(
                class_data,
                data_set_mean[reverse_map[c]],
                data_set_stdev[reverse_map[c]],
                class_subset_size[reverse_map[c]],
                mean_limit=class_mean_limit,
                stdev_limit=class_stdev_limit,
            )
            subset = subset.append(subset_remainder["subset"])
            remainder = remainder.append(subset_remainder["remainder"])
            self.num_of_attempts = subset_remainder["num_of_attempts"]
        return subset, remainder

    def reduce_to_binary_classes(self, data, binary_class1, label_column="Label"):
        """
        Method for Set Composition protocol that combines all classes besides the binary_class1 into a single class called 'other'.
        The statistical similarity is controled by parameters: mean_limit, stdev_limit
            Parameters
            data : pandas.DataFrame, Feature data scaled to [0,255]
            binary_class1 : int, the working class chosen to be separate from the 'other' class
            label_column : str, column with labels
            Returns
            opt_sample : subset and remainder
        """
        other_classes = data[label_column].unique().tolist()
        len(other_classes)
        other_classes.remove(binary_class1)
        data_binary = data.copy()
        data_binary.loc[
            data_binary[label_column] == binary_class1, label_column
        ] = binary_class1
        data_binary.loc[
            data_binary[label_column].isin(other_classes), label_column
        ] = other_classes[0]
        return data_binary, other_classes

    def remap_keys_to_integers(self, class_size_dict):
        """
        Utility method to map category labels to integers using the same logic as used
        in model generator (engine.base.utils.remap_labels_to_integers).
            Parameters
            class_size_dict : dict, The keys are the labels in the data (field values are unused)
            Returns
            class_map : dict, Keys are data labels, field values are integers used in the KB engine
            reverse_map : dict, Keys are integers used in the KB engine, field values are the associated data labels
        """
        label_array = array(list(class_size_dict.keys()))
        if label_array.dtype == "int64":  # If labels are int64, sort by magnitude
            labels = sorted(set(label_array.astype(int)))
        elif label_array.dtype == "float64":  # If labels are int64, sort by magnitude
            labels = sorted(set(label_array.astype(float)))
        else:
            # If labels are characters, sort alphabetically
            labels = sorted(set(label_array))
        class_map = {}
        value = 1
        for item in labels:  # Set sorted values to ascending integers
            class_map[item] = value
            value += 1
        reverse_map = {}
        # Invert dict so that keys are field values and visa versa
        for k, v in dict.items(class_map):
            reverse_map[v] = k
        return class_map, reverse_map


class MetadataKFoldValidation(ValidationMethod):
    def __init__(self, config, data):
        super(MetadataKFoldValidation, self).__init__(config, data)
        self._metadata_name = config["metadata_name"]
        self._n_splits = config["number_of_folds"]

    def generate_validation(self, **kwargs):

        # Generate temporary indices from labels
        cv = GroupKFold(n_splits=self._n_splits)

        groups = self._data[self._metadata_name]

        y = self._data[self._label_column]
        X = np.zeros(len(y))

        for fold, (train_indices, validate_indices) in enumerate(
            cv.split(X, y, groups)
        ):

            train, validate, test = self.add_augmented_indices(
                self._original_indices[train_indices],
                self._original_indices[validate_indices],
                [],
                metadata_name=self._metadata_name,
            )

            self._sets.append(
                ValidationSet(
                    train=train,
                    validate=validate,
                    name=f"{fold}",
                )
            )


class MetadataAndLabelKFoldValidation(ValidationMethod):
    def __init__(self, config, data):
        super(MetadataAndLabelKFoldValidation, self).__init__(config, data)
        self._metadata_name = config["metadata_name"]
        self._n_splits = config["number_of_folds"]

    def generate_validation(self, **kwargs):

        # Generate temporary indices from labels
        cv = GroupAndLabelKFold(n_splits=self._n_splits)

        groups = self._data[self._metadata_name]
        y = self._data[self._label_column]
        X = np.zeros(len(y))

        for fold, (train_indices, validate_indices) in enumerate(
            cv.split(X, y, groups)
        ):

            train, validate, test = self.add_augmented_indices(
                self._original_indices[train_indices],
                self._original_indices[validate_indices],
                [],
                metadata_name=self._metadata_name,
                group_by_label_metadata=True,
            )

            self._sets.append(
                ValidationSet(
                    train=train,
                    validate=validate,
                    name=f"{fold}",
                )
            )


class GroupAndLabelKFold(_BaseKFold):
    """K-fold iterator variant with non-overlapping groups and label
    combination which also attempts. to evenly distribute the number of each
    class across each fold. This is similar to GroupKFold, where, you cannot
    have the same group in in multiple folds, but in this case you cannot
    have the same group and label combination across multiple folds.

    The main use case is for time series data where you may have a Subject
    group, where the subject performs several activities. If you build a model
    using a sliding window to segment data, you will end up with "Subject A"
    performing "action 1" many times. If you use a validation method that
    splits up "Subject A" performing "action 1" into different folds it can
    often result in data leakage and overfitting. If however, you build your
    validation set such that "Subject A" performing "action 1" is only in a
    single fold you can be more confident that your model is generalizing.
    This validation will also attempt to ensure you have a similar amount
    of "action 1s" across your folds.

    Parameters
    ----------
    n_splits : int, default=5
        Number of folds. Must be at least 2.

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.model_selection import GroupAndLabelKFold
    >>> groups = np.array([3,0,3,0,3,3,2,0,1])
    >>> y =      np.array([1,1,1,1,1,2,2,2,2])
    >>> X =      np.array([1,2,3,4,5,6,6,6,7])
    >>> group_label_kfold = GroupAndLabelKFold(n_splits=2)
    >>> group_label_kfold.get_n_splits(X, y, groups)
    2
    >>> for train_index, test_index in group_label_kfold.split(X, y, groups):
    ...     print("TRAIN:", train_index, "TEST:", test_index)
    ...     X_train, X_test = X[train_index], X[test_index]
    ...     y_train, y_test = y[train_index], y[test_index]
    ...     print(X_train, X_test, y_train, y_test)
    ...
        TRAIN: [1 3 6 7] TEST: [0 2 4 5 8]
        [2 4 6 6] [1 3 5 6 7] [1 1 2 2] [1 1 1 2 2]
        TRAIN: [0 2 4 5 8] TEST: [1 3 6 7]
        [1 3 5 6 7] [2 4 6 6] [1 1 1 2 2] [1 1 2 2]

    See also
    --------
    LeaveOneGroupOut
        For splitting the data according to explicit domain-specific
        stratification of the dataset.
    """

    def __init__(self, n_splits=5):
        super().__init__(n_splits, shuffle=False, random_state=None)

    def _iter_test_indices(self, X, y, groups):
        if groups is None:
            raise ValueError("The 'groups' parameter should not be None.")
        groups = check_array(groups, ensure_2d=False, dtype=None)

        unique_groups, groups = np.unique(groups, return_inverse=True)
        n_groups = len(unique_groups)

        if self.n_splits > n_groups:
            raise ValueError(
                "Cannot have number of splits n_splits=%d greater"
                " than the number of groups: %d." % (self.n_splits, n_groups)
            )

        unique_y = np.unique(y)

        label_to_fold = []
        for label in unique_y:
            # Weight labels by their number of occurrences
            tmp_groups = groups[y == label]

            n_samples_per_group = np.bincount(tmp_groups)

            # Distribute the most frequent labels first
            indices = np.argsort(n_samples_per_group)[::-1]
            n_samples_per_group = n_samples_per_group[indices]

            # Total weight of each fold
            n_samples_per_fold = np.zeros(self.n_splits)

            # Mapping from group index to fold index
            groups_in_fold = {x: [] for x in range(self.n_splits)}

            # Distribute samples, add the largest weight to the lightest fold
            for group_index, weight in enumerate(n_samples_per_group):
                lightest_fold = np.argmin(n_samples_per_fold)
                if weight:
                    n_samples_per_fold[lightest_fold] += weight
                    groups_in_fold[lightest_fold].append(indices[group_index])

            label_to_fold.append((label, groups_in_fold))

        for f in range(self.n_splits):
            indices = []
            for label, groups_in_fold in label_to_fold:
                label_indices = np.where(y == label)[0]
                group_indices = np.where(np.isin(groups, groups_in_fold[f]))[0]
                indices.extend(np.intersect1d(label_indices, group_indices))

            yield indices

    def split(self, X, y=None, groups=None):
        """Generate indices to split data into training and test set.
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data, where n_samples is the number of samples
            and n_features is the number of features.
        y : array-like, shape (n_samples,), optional
            The target variable for supervised learning problems.
        groups : array-like, with shape (n_samples,)
            Group labels for the samples used while splitting the dataset into
            train/test set.
        Yields
        ------
        train : ndarray
            The training set indices for that split.
        test : ndarray
            The testing set indices for that split.
        """
        return super().split(X, y, groups)
