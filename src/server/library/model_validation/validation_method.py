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
from abc import abstractmethod

from numpy import array, ndarray, zeros
from numpy.random import RandomState
from pandas import DataFrame
from sklearn.model_selection import StratifiedShuffleSplit

from library.core_functions.augmentation import is_augmented, np, similar_root_uuid
from library.classifiers.classifier import Classifier

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


class ValidationSet(object):
    """A set of row indices corresponding to training, validation, and possibly testing feature vectors.
    Optionally, can be given a string name.

    Indices are kept as ndarrays for maximum efficiency."""

    def __init__(self, train=[], validate=[], test=[], name=""):
        self._train = train if isinstance(train, ndarray) else array(train)
        self._validate = validate if isinstance(validate, ndarray) else array(validate)
        self._test = test if isinstance(test, ndarray) else array(test)
        self._name = name

    @property
    def train(self):
        return self._train

    @property
    def test(self):
        return self._test

    @property
    def validate(self):
        return self._validate

    @property
    def name(self):
        return self._name


def is_original(data):

    assert isinstance(data, DataFrame)

    if "segment_uuid" in data.columns.values:
        return data.apply(lambda row: not is_augmented(row["segment_uuid"]), axis=1)
    else:
        return data.apply(lambda row: True, axis=1)


class ValidationMethod(object):
    """
    The base class for all validation methods used during train-validate-optimize steps.
    Subclasses should implement the integer method generate_validation() to provide specificity.
    Subclasses should NOT sort or otherwise re-order the rows as provided to the constructor.
    Subclasses may also use customized __init__ constructors to use configuration parameters, but must invoke
    this base class constructor at the start of their custom constructors.
    Internally, the dataframe columns are re-indexed into features + group_columns + label to facilitate slicing.
    If any feature column names are provided, these columns will be given highest priority in the re-indexing.
    """

    @classmethod
    def sort_columns(
        cls, column_names, label_column, unused=[], group_columns=[], feature_columns=[]
    ):
        """
        Re-index the data for validation:
           - remove unused columns (as provided by parameter)
           - initial column(s) reserved for priority features (provided as parameter)
           - use 'group_columns' parameter to identify columns used for groups
           - last column is reserved for label
        Columns are returned in [{features}, {groups}, {label}] order
        :return: a re-ordered list of column_names and the list of feature column labels (in priority order)
        """
        remaining_features = list(
            filter(
                lambda col: col != str(label_column)
                and col not in unused
                and col not in feature_columns
                and col not in group_columns,
                column_names,
            )
        )
        available_features = list(
            filter(lambda col: col in column_names, feature_columns)
        )
        new_columns = (
            available_features + remaining_features + group_columns + [label_column]
        )
        all_features = available_features + remaining_features
        return [str(x) for x in new_columns], [str(x) for x in all_features]

    def __init__(self, config, data):
        """
        Performs common validation tasks, like re-indexing columns into [feature_columns, group_columns, label_column]
        and grouping by cycle column.  Also sets members _labels and _features, used for extracting train and test
        vectors.
        :param config: a Train-Validate-Optimize configuration dictionary
        :param data: a feature dataframe
        """

        assert isinstance(data, DataFrame)

        ignore_columns = config.get("ignore_columns", [])
        self._uuid_list = None
        if "segment_uuid" in data.columns.values:
            self._uuid_list = data["segment_uuid"].values
            if not "segment_uuid" in ignore_columns:
                ignore_columns += ["segment_uuid"]

        new_columns, self._features = ValidationMethod.sort_columns(
            data.columns,
            label_column=config["label_column"],  # mandatory
            unused=ignore_columns,  # optional
            group_columns=config.get("group_columns", []),  # optional
            feature_columns=config.get("feature_columns", []),  # optional
        )
        self._config = config

        #############################################
        # NOTE bool_orig_segment (list): True for original, false for augmented
        # _all__data (DataFrame): Includes original and augmented
        # data (DataFrame): includes original segments

        bool_orig_segment = is_original(data)

        self._all_data = data.reindex(columns=new_columns, copy=True)
        self._augmented_indices = data[~bool_orig_segment].index.values

        self._original_indices = data[bool_orig_segment].index.values
        self._data = self._all_data[bool_orig_segment].reset_index(drop=True)
        #############################################

        self._group_columns = config.get("group_columns", [])
        assert isinstance(self._group_columns, list)
        # _grouped is a pandas GroupBy object
        self._grouped = (
            self._data.groupby(self._group_columns) if self._group_columns else None
        )
        self._label_column = str(config["label_column"])
        self._is_generated = False
        self._sets = []
        self._sets_iterator = iter(self._sets)
        self._current_set = ValidationSet()
        self._random_seed = config.get("validation_seed", None)
        self._permutation = (
            RandomState(int(self._random_seed)).permutation
            if self._random_seed
            else RandomState().permutation
        )

        self._test_size = config.get("test_size", 0.0)
        self._validation_size = config.get("validation_size", 0.2)
        self._number_of_folds = config.get("number_of_folds", 1)

    def add_augmented_indices(
        self,
        train_indx,
        validate_indx,
        test_indx,
        metadata_name=None,
        group_columns=None,
        group_key=None,
        group_by_label_metadata=False,
    ):
        """
        Adding augmented data indices to the training indices. This functions removes the augmented counterparts of the original segments already picked by the validation/testing sets.

        Parameters
        ----------
        train_indx : training indices (only original segments)
        validate_indx : validation indices (only original segments)
        test_indx : testing indices (only original segments)
        metadata_name (optional, str) : the name of the metadata column used for splitting data into training/validation sets (used by MetadataKFoldValidation)
        group_columns (optional, [str]) : the list metadata columns using which data is grouped and splitted (used in LeaveOneGroupOutValidation)
        group_key (optional, str) : grouping key generated in LeaveOneGroupOutValidation class
        group_by_label_metadata (optional, boolean) : if True, data is splitted based on unique groups generated by pairs of label and metadata (used in MetadataAndLabelKFoldValidation)

        Output: updated training, validation and testing indices.
        ----------
        augmented_train_indx
        validate_indx
        test_indx

        """

        # do NOT add augmented data to the training set, if NO augmented data is presented
        if self._uuid_list is None:
            return train_indx, validate_indx, test_indx

        n = len(self._augmented_indices)
        keep = [True] * n

        for j, aug_indx in enumerate(self._augmented_indices):

            for kx in validate_indx:
                if similar_root_uuid(self._uuid_list[aug_indx], self._uuid_list[kx]):
                    keep[j] = False
                    break

            if keep[j]:
                for kx in test_indx:
                    if similar_root_uuid(
                        self._uuid_list[aug_indx], self._uuid_list[kx]
                    ):
                        keep[j] = False
                        break

        augmented_train_indx = np.concatenate(
            (self._augmented_indices[keep], train_indx)
        )

        if metadata_name and len(augmented_train_indx) > 1:
            groups = set(self._all_data.iloc[validate_indx][metadata_name].values)
            trim = self._all_data.iloc[augmented_train_indx].apply(
                lambda row: not row[metadata_name] in groups, axis=1
            )
            augmented_train_indx = augmented_train_indx[trim]

        if group_by_label_metadata and len(augmented_train_indx) > 1:
            groups = set(
                self._all_data.iloc[validate_indx][
                    [metadata_name, self._label_column]
                ].apply(lambda row: "/".join([str(r) for r in row]), axis=1)
            )
            trim = self._all_data.iloc[augmented_train_indx][
                [metadata_name, self._label_column]
            ].apply(lambda row: "/".join([str(r) for r in row]) != group_key, axis=1)
            augmented_train_indx = augmented_train_indx[trim]

        if group_columns and group_key and len(augmented_train_indx) > 1:
            trim = self._all_data.iloc[augmented_train_indx][group_columns].apply(
                lambda row: "/".join([str(r) for r in row]) != group_key, axis=1
            )
            augmented_train_indx = augmented_train_indx[trim]

        return augmented_train_indx, validate_indx, test_indx

    # Read-only properties

    @property
    def label_column(self):
        return self._label_column

    @property
    def feature_columns(self):
        return self._features

    @property
    def group_columns(self):
        return self._group_columns

    # current validation-set read-only properties
    @property
    def test_indices(self):
        """
        :return: the indices corresponding to the test grouping for the current validation set
        """
        return self._current_set.test

    @property
    def train_indices(self):
        """
        :return: the indices corresponding to the training grouping for the current validation set
        """
        return self._current_set.train

    @property
    def validate_indices(self):
        """
        :return: the indices corresponding to the validation grouping for the current validation set
        """
        return self._current_set.validate

    @property
    def name(self):
        """
        :return: the name of the current validation set
        """
        return self._current_set.name

    @property
    def is_generated(self):
        """
        :return: whether the instance has generated train-validation-test sets or not
        """
        return self._is_generated

    @property
    def number_of_sets(self):
        return len(self._sets)

    def preprocess_data(self, classifier, **kwargs):
        """
        Pre-processes the feature data suitable for the given classifier
        :param classifier: the classifier used for learning/recognizing features
        :param kwargs: parameters passed on to the classifier's preprocess method
        """
        assert isinstance(classifier, Classifier)

        self._all_data = classifier.preprocess(
            len(self.feature_columns), self._all_data, **kwargs
        )

    @abstractmethod
    def generate_validation(self, **kwargs):
        """
        Constructs the sets of train-validate-test groupings.  Subclasses should override this method
        and set _is_generated accordingly.
        :return: How many sets of train-validate-test groupings were created.
        """

    def next_validation(self, number_of_features=0):
        """
        Returns the dataframes corresponding to the next validation set.
        Raises a StopIteration exception if there are no further validation sets.
        May be overridden by subclasses, but must update self._current_set.
        Also, indices in self._current_set should refer to the row ordering provided at _init_().
        :param num_features: the number of features to include in the dataframe, not including the label/classifier column.
        :return: at least two dataframes, first for training, second for validating. A third dataframe (test) may be empty. \
        Only feature vectors and the classifier(s) are included-- grouping is handled by the ValidationMethod instance.
        """

        if not number_of_features:
            number_of_features = len(self.feature_columns)
        columns_to_return = list(range(number_of_features)) + [-1]
        self._current_set = next(self._sets_iterator)
        train_data = self._all_data.iloc[self._current_set.train, columns_to_return]
        validate_data = self._all_data.iloc[
            self._current_set.validate, columns_to_return
        ]
        test_data = self._all_data.iloc[self._current_set.test, columns_to_return]
        return train_data, validate_data, test_data

    def recall_data(self, number_of_features=0):
        if not number_of_features:
            number_of_features = len(self.feature_columns)
        columns_to_return = list(range(number_of_features)) + [-1]
        train_data = self._all_data.iloc[:, columns_to_return]
        validate_data = self._all_data.iloc[:, columns_to_return]
        test_data = self._all_data.iloc[:, columns_to_return]
        return train_data, validate_data, test_data

    def get_test_set_args(self):

        if self._test_size == 0:
            return False, {}

        test_set_args = {"test_size": self._test_size}

        return True, test_set_args

        # return reserve_test, test_set_args

    def reserve_test_set(self, reserve_test, **kwargs):
        """
        A common method to reserve a stratified subset of feature data for model selection after model tuning.
        Subclasses may override this method, provided that the returned Series excludes the returned test indices.
        :param reserve_test: whether to reserve a set of test data or not
        :param kwargs: arguments to pass to sklearn's StratifiedShuffleSplit (e.g. test_size, random_seed)
        :return: The reduced set of labels for training-validation as a Series
        """
        if reserve_test:
            y = self._data[self._label_column]
            X = zeros(len(y))

            cv = StratifiedShuffleSplit(n_splits=1, **kwargs)

            new_indicies, test_indices = next(cv.split(X, y))
        else:
            test_indices = []
            new_indicies = self._data.index

        return new_indicies, test_indices

    def permute_current_set(self, number_of_features=0):
        """ Creates a permutation of the current data sets.
        :return: at least two dataframes, first for training, second for validating.  A third dataframe(test) may be empty. \
        Only feature vectors and classifier are returned; grouping is handled by the ValidationMethod instance.
        """
        if not number_of_features:
            number_of_features = len(self.feature_columns)
        assert number_of_features <= len(self.feature_columns)
        columns_to_return = self._all_data.columns[
            list(range(number_of_features)) + [-1]
        ]
        permutation_set = ValidationSet(*(self.permute_indices()))
        train_data = self._all_data.loc[permutation_set.train, columns_to_return]
        validate_data = self._all_data.loc[permutation_set.validate, columns_to_return]
        test_data = self._all_data.loc[permutation_set.test, columns_to_return]
        return train_data, validate_data, test_data

    def permute_indices(self):
        """ Creates a permutation of the indices for the current data sets.  Useful for when preprocessing has been \
        performed on the original data sets.
        :return: re-ordered lists of train, validate, and test indices.
        """
        return (
            self._permutation(self._current_set.train),
            self._permutation(self._current_set.validate),
            self._permutation(self._current_set.test),
        )
