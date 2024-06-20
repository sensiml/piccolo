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

from copy import deepcopy
from typing import List, Optional

import numpy as np
from library.core_functions.utils.fs_meta_data_selection import MetaDataSelection
from library.core_functions.utils.utils import handle_group_columns
from numpy import abs as numpy_abs
from numpy import concatenate
from pandas import DataFrame, concat
from scipy import stats
from sklearn import svm
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.utils import resample


class InvalidateParameterException(Exception):
    pass


class SamplerError(Exception):
    pass


@handle_group_columns
def sample_metadata_max_pool(
    input_data: DataFrame, group_columns: List[str], metadata_name: str
) -> DataFrame:
    """
    For each group, perform max pooling on the specified metadata_name column
    and set the value of that metadata column to the maximum occurring value.

    Args:
        input_data (DataFrame): Input DataFrame.
        group_columns (list): Columns to group over.
        metadata_name (str): Name of the metadata column to use for sampling.

    Returns:
        DataFrame: The modified input_data DataFrame with metadata_name column being modified by max pooling.
    """
    if isinstance(input_data, DataFrame):
        input_data[metadata_name] = input_data[metadata_name].value_counts().idxmax()
    elif isinstance(input_data, list):
        raise Exception("Only supported for Feature Files")

    return input_data


sample_metadata_max_pool_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list"},
        {"name": "metadata_name", "type": "str"},
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def sample_by_metadata(
    input_data: DataFrame, metadata_name: str, metadata_values: List[str]
) -> DataFrame:
    """
    Select rows from the input DataFrame based on a metadata column. Rows
    that have a metadata value that is in the values list will be returned.

    Args:
        input_data (DataFrame): Input DataFrame.
        metadata_name (str): Name of the metadata column to use for sampling.
        metadata_values (list[str]): List of values of the named column for which to
            select rows of the input data.

    Returns:
        DataFrame: The input_data DataFrame containing only the rows for which the metadata value is
        in the accepted list.
    """

    if isinstance(input_data, DataFrame):
        indexes = [
            i
            for i in input_data.index
            if input_data.loc[i, metadata_name] in metadata_values
        ]
        return input_data.loc[indexes, :].reset_index(drop=True)
    elif isinstance(input_data, list):
        sampled_data = []

        for seg in input_data:
            if seg["metadata"][metadata_name] in metadata_values:
                sampled_data.append(seg)

        return sampled_data


sample_by_metadata_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "metadata_name", "type": "str"},
        {"name": "metadata_values", "type": "list", "element_type": "str"},
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def sample_combine_labels(
    input_data: DataFrame, label_column: str, combine_labels: dict
) -> DataFrame:
    """
    Select rows from the input DataFrame based on a metadata column. Rows that have
    a label value that is in the combined label list will be returned.

    Syntax:
        combine_labels = {'group1': ['label1', 'label2'], 'group2': ['label3', 'label4'],
                          'group3': ['group5']}

    Args:
        input_data (DataFrame): Input DataFrame.
        label_column (str): Label column name.
        combine_labels (dict): Map of label columns to combine.

    Returns:
        DataFrame: The input_data containing only the rows for which the label value is in
        the combined list.
    """

    invert_labels = {}
    for key, values in combine_labels.items():
        invert_labels.update({i: key for i in values})

    if isinstance(input_data, DataFrame):
        label_values = input_data[label_column].unique()
        invert_labels.update({k: k for k in label_values if k not in invert_labels})
        input_data[label_column] = input_data[label_column].map(invert_labels)

    elif isinstance(input_data, list):
        for seg in input_data:
            seg["metadata"][label_column] = invert_labels.get(
                seg["metadata"][label_column], seg["metadata"][label_column]
            )

    return input_data


sample_combine_labels_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {
            "name": "combine_labels",
            "type": "dict",
            "element_type": "list_str",
            "description": "Map of label columns to combine",
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def sample_autogroup_labels(
    input_data: DataFrame, label_column: str, combine_labels: dict
):
    """
    Finds the optimal grouping of labels such that all labels fall into two groups
    which are most separable in your feature space.

    Args:
        input_data (DataFrame): input DataFrame
            The DataFrame containing the input data.
        label_column (str): label column name
            The name of the column containing labels to be grouped.
        combine_labels (dict): map of label columns to combine
            A dictionary that maps label columns to be combined.

    Returns:
        DataFrame
            A new DataFrame containing only the rows for which the metadata value is
            in the accepted list.
    """

    md_obj = MetaDataSelection(input_data, label_column)
    combine_labels = md_obj.score_class_combination()

    map_labels = {}
    for label in input_data[label_column].unique():

        if label in combine_labels["Group1"]:
            map_labels[label] = combine_labels["Group1"]

        elif label in combine_labels["Group2"]:
            map_labels[label] = combine_labels["Group2"]

        else:
            raise Exception(label + " does not belong to any group.")

    input_data.loc[:, label_column] = input_data[label_column].map(map_labels)

    return input_data


sample_autogroup_labels_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {
            "name": "combine_labels",
            "type": "dict",
            "element_type": "list_str",
            "description": "Map of label columns to combine",
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def sample_zscore_filter(
    input_data: DataFrame,
    label_column: str,
    zscore_cutoff: int = 3,
    feature_threshold: int = 1,
    feature_columns: Optional[List[str]] = None,
    assign_unknown: bool = False,
) -> DataFrame:
    """
    A z-score filter is a way to standardize feature vectors by transforming each
    feature in the vector to have a mean of zero and a standard deviation of one.
    The z-score, or standard score, is a measure of how many standard deviations
    a data point is from the mean of the distribution.  This features that have
    z-score outside of a cutoff threshold are removed.

    Args:
        input_data (DataFrame): Input DataFrame.
        label_column (str): Label column name.
        zscore_cutoff (int): Cutoff for filtering features above z score.
        feature_threshold (int): The number of features in a feature vector that can be outside of
                                 the zscore_cutoff without removing the feature vector.
        feature_columns (list): List of features to filter by. If None, filters all.
        assign_unknown (bool): Assign unknown label to outliers.

    Returns:
        DataFrame: The filtered DataFrame containing only the rows for which the metadata value is in
                   the accepted list.

    Examples:
        >>> client.pipeline.reset(delete_cache=False)
        >>> df = client.datasets.load_activity_raw()
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_generator([{'name':'Downsample',
                                     'params':{"columns": ['accelx','accely','accelz'],
                                               "new_length": 5 }}])
        >>> results, stats = client.pipeline.execute()
        # List of all data indices before the filtering algorithm
        >>> results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5, 6, 7, 8]

        >>> client.pipeline.add_transform("Zscore Filter",
                           params={"zscore_cutoff": 3, "feature_threshold": 1})

        >>> results, stats = client.pipeline.execute()
        # List of all data indices after the filtering algorithm
        >>>results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5]

    """
    if zscore_cutoff <= 0:
        raise InvalidateParameterException("zscore_cutoff must be greater than 0")
    if not feature_columns:
        feature_columns = [column for column in input_data if column[:4] == "gen_"]

    # don't apply this to columns with std of 0 because it removes everything, let a feature selection
    # step take care of that
    std = input_data[feature_columns].describe().loc["std"]
    feature_columns = [col for col in std.index if std[col] != 0]

    indexes = []
    g = input_data.groupby(label_column)
    num_features = len(feature_columns)
    for key in g.groups:
        tmp = g.get_group(key)
        indexes.append(
            tmp[
                (
                    num_features
                    - (
                        numpy_abs(stats.zscore(tmp[feature_columns])) < zscore_cutoff
                    ).sum(axis=1)
                )
                < feature_threshold
            ].index
        )

    if assign_unknown:
        return change_outlier_to_unknown(input_data, concatenate(indexes), label_column)

    return input_data.iloc[concatenate(indexes)].reset_index(drop=True)


sample_zscore_filter_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {
            "name": "zscore_cutoff",
            "type": "int",
            "default": 3,
            "range": [1, 6],
            "display_name": "Z score Cutoff",
            "description": "Cutoff for to filter features above z score.",
        },
        {
            "name": "feature_threshold",
            "type": "int",
            "default": 1,
            "range": [1, 4],
            "display_name": "Feature Threshold",
            "description": "The number of features in a feature vector that can be outside of the zscore_cutoff without removing the feature vector.",
        },
        {
            "name": "feature_columns",
            "type": "list",
            "default": [],
            "display_name": "Feature Columns",
            "description": "List of features to filter by, if none filters all (default None).",
        },
        {
            "name": "assign_unknown",
            "type": "bool",
            "default": False,
            "display_name": "Assign Unknown",
            "description": "Assign unknown label to outliers.",
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def sigma_outliers_filtering(
    input_data: DataFrame,
    label_column: str,
    filtering_label: Optional[str] = None,
    feature_columns: Optional[List[str]] = None,
    sigma_threshold: float = 3.0,
    assign_unknown: bool = False,
) -> DataFrame:
    """
    A sigma outlier filter algorithm is a technique used to identify and remove
    outliers from feature vectors based on their deviation from the mean. In this
    algorithm, an outlier is defined as a data point that falls outside a certain
    number of standard deviations (sigma) from the mean of the distribution.



    Args:
        input_data (DataFrame): The feature set that is a result of either a generator_set or feature_selector.
        label_column (str): The label column name.
        filtering_label (str): List of classes that will be filtered. If it is not defined, all classes
                                       will be filtered.
        feature_columns (list of str): List of features. If it is not defined, it uses all features.
        sigma_threshold (float): Defines the ratio of outliers.
        assign_unknown (bool): Assigns an unknown label to outliers.

    Returns:
        DataFrame: The filtered DataFrame containing features without outliers and noise.

        Examples:

            .. code-block:: python

                client.pipeline.reset(delete_cache=False)
                df = client.datasets.load_activity_raw()
                client.pipeline.set_input_data('test_data', df, force=True,
                                data_columns = ['accelx', 'accely', 'accelz'],
                                group_columns = ['Subject','Class'],
                                label_column = 'Class')
                client.pipeline.add_feature_generator([{'name':'Downsample',
                                        'params':{"columns": ['accelx','accely','accelz'],
                                                "new_length": 5 }}])
                results, stats = client.pipeline.execute()
                # List of all data indices before the filtering algorithm
                results.index.tolist()
                # Out:
                # [0, 1, 2, 3, 4, 5, 6, 7, 8]

                client.pipeline.add_transform("Sigma Outliers Filtering",
                            params={ "sigma_threshold": 1.0 })

                results, stats = client.pipeline.execute()
                # List of all data indices after the filtering algorithm
                results.index.tolist()
                # Out:
                # [0, 1, 2, 3, 4, 5]

    """

    core_data_index = []
    if not (feature_columns):
        feature_columns = [i for i in input_data.columns.tolist() if ("gen_" == i[:4])]
    else:
        transfer_columns = [i for i in input_data.columns.tolist() if ("gen_" != i[:4])]
        input_data = input_data[transfer_columns + feature_columns]

    if not (filtering_label):
        filtering_label = np.unique(input_data[label_column])

    for label in filtering_label:
        class_input_data = input_data[(input_data[label_column] == label)][
            feature_columns
        ]
        mean_of_class_feature = np.mean(class_input_data).tolist()
        # to speed up computation, dataframe.corr propery is used
        # adding mean at the end of the dataframe
        mean_indx = int(max(class_input_data.index) + 1)
        class_input_data.loc[mean_indx] = mean_of_class_feature
        # create corr matrix
        df_temp = class_input_data.T.corr(method="pearson")
        # reading the mean_indx line that corrisponing correlation all vectors to mean
        class_input_data["Corr2mean"] = df_temp.loc[mean_indx].tolist()
        # remove mean_indx from the running_index
        class_input_data = class_input_data.drop(mean_indx)
        # # filter the outliers
        core_class_data_index = class_input_data[
            (np.mean(class_input_data["Corr2mean"]) - class_input_data["Corr2mean"])
            <= (np.std(class_input_data["Corr2mean"]) * sigma_threshold)
        ].index.tolist()
        core_data_index.append(core_class_data_index)

    flat_index = np.sort([i for class_list in core_data_index for i in class_list])

    if assign_unknown:
        return change_outlier_to_unknown(input_data, flat_index, label_column)

    return input_data.iloc[flat_index].reset_index(drop=True)


sigma_outliers_filtering_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {
            "name": "filtering_label",
            "type": "list",
            "default": [],
            "display_name": "Filtering Label",
            "description": "List of classes that will be filered. If it is not defined, all class will be filtered.",
        },
        {
            "name": "feature_columns",
            "type": "list",
            "default": [],
            "display_name": "Feature Columns",
            "description": "List of features. if it is not defined, it uses all features.",
        },
        {
            "name": "sigma_threshold",
            "type": "float",
            "default": 3.0,
            "range": [2, 4],
            "display_name": "Sigma Threshold",
            "description": "Define the ratio of outliers.",
        },
        {
            "name": "assign_unknown",
            "type": "bool",
            "default": False,
            "display_name": "Assign Unknown",
            "description": "Assign unknown label to outliers.",
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def change_outlier_to_unknown(input_data, flat_index, label_column):
    final_outliers = list(set(input_data.index.tolist()) - set(flat_index))
    input_data.loc[final_outliers, label_column] = "Unknown"
    return input_data


def filtering(
    input_data,
    clf,
    clf_name,
    filtering_label,
    feature_columns,
    outliers_fraction,
    label_column,
    assign_unknown=False,
):

    all_core_index = []

    if not (feature_columns):
        feature_columns = [i for i in input_data.columns.tolist() if ("gen_" == i[:4])]
    else:
        transfer_columns = [i for i in input_data.columns.tolist() if ("gen_" != i[:4])]
        input_data = input_data[transfer_columns + feature_columns]

    valid_labels = np.unique(input_data[label_column])

    if not (filtering_label):
        filtering_label = valid_labels

    filtering_label = list(filter(lambda x: x in valid_labels, filtering_label))
    non_filtered_labels = list(filter(lambda x: x not in filtering_label, valid_labels))

    for label_index in filtering_label:

        df_temp = deepcopy(
            input_data[input_data[label_column] == label_index].reset_index()
        )

        X = np.array(df_temp[feature_columns].fillna(0).astype("float64"))

        number_of_samples = len(X)

        if clf_name == "isolation_forest_filtering":
            clf = isolation_forest_filtering_sub_function(
                outliers_fraction, number_of_samples
            )

        if clf_name == "local_outlier_factor_filtering":
            clf.fit_predict(X)
            scores_pred = clf.negative_outlier_factor_
        else:
            clf.fit(X)
            scores_pred = clf.decision_function(X)
            clf.predict(X)

        threshold = stats.scoreatpercentile(scores_pred, 100 * outliers_fraction)
        outlier_index = [i for i, v in enumerate(scores_pred) if v >= threshold]
        # this is outlier_index
        df_core_index = df_temp.loc[outlier_index, "index"].values
        all_core_index.append(df_core_index)

    for label_index in non_filtered_labels:
        all_core_index.append(
            input_data[input_data[label_column] == label_index].index.values
        )

    flat_index = [i for indx in all_core_index for i in indx]

    if assign_unknown:
        return change_outlier_to_unknown(input_data, flat_index, label_column)

    filtered_data = input_data.iloc[flat_index].reset_index(drop=True)

    if filtered_data.shape[0] == 0:
        raise ValueError(
            "All data was filtered from this step. Adjust the parameters or remove the filtering function"
        )

    return filtered_data


def local_outlier_factor_filtering(
    input_data: DataFrame,
    label_column: str,
    filtering_label: Optional[str] = None,
    feature_columns: Optional[List[str]] = None,
    outliers_fraction: float = 0.05,
    number_of_neighbors: int = 50,
    norm: str = "L1",
    assign_unknown: bool = False,
):
    """
    The local outlier factor (LOF) to measure the local deviation of a given data point with respect
    to its neighbors by comparing their local density.

    The LOF algorithm is an unsupervised outlier detection method which computes the local density
    deviation of a given data point with respect to its neighbors. It considers as outlier samples
    that have a substantially lower density than their neighbors.

    Args:
        input_data: Dataframe, feature set that is results of generator_set or feature_selector
        label_column (str): Label column name.
        filtering_label: List<String>, List of classes. if it is not defined, it use all classes.
        feature_columns: List<String>, List of features. if it is not defined, it uses all features.
        outliers_fraction (float) : Define the ratio of outliers.
        number_of_neighbors (int) : Number of neighbors for a vector.
        norm (string) : Metric that will be used for the distance computation.
        assign_unknown (bool): Assign unknown label to outliers.

    Returns:
        DataFrame containing features without outliers and noise.

    Examples:
        >>> client.pipeline.reset(delete_cache=False)
        >>> df = client.datasets.load_activity_raw()
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_generator([{'name':'Downsample',
                                     'params':{"columns": ['accelx','accely','accelz'],
                                               "new_length": 5 }}])
        >>> results, stats = client.pipeline.execute()
        # List of all data indices before the filtering algorithm
        >>> results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5, 6, 7, 8]

        >>> client.pipeline.add_transform("Local Outlier Factor Filtering",
                           params={"outliers_fraction": 0.05,
                                    "number_of_neighbors": 5})

        >>> results, stats = client.pipeline.execute()
        # List of all data indices after the filtering algorithm
        >>>results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5]

    """

    if norm == "L1":
        norm = "cityblock"
    elif norm == "Lsup":
        norm = "chebyshev"
    else:
        raise Exception(
            "Err: This " + norm + " parameter is not defined in Analitic Studio."
        )

    # number_of_neighbors is bigger then data size, number_of_neighbors will be set to size of data
    if number_of_neighbors >= len(input_data):
        number_of_neighbors = len(input_data) - 2
        raise Exception(
            "Number_of_neighbors is bigger then the data size, number_of_neighbors will be set to size of data"
        )

    # "Local Outlier Factor"
    clf = LocalOutlierFactor(
        algorithm="auto",
        contamination=outliers_fraction,
        leaf_size=30,
        metric=norm,
        metric_params=None,
        n_jobs=1,
        n_neighbors=number_of_neighbors,
        p=2,
    )

    input_data = filtering(
        input_data,
        clf,
        "local_outlier_factor_filtering",
        filtering_label,
        feature_columns,
        outliers_fraction,
        label_column,
        assign_unknown,
    )
    return input_data


local_outlier_factor_filtering_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {
            "name": "filtering_label",
            "type": "list",
            "default": [],
            "display_name": "Filtering Label",
            "description": "List of classes.",
        },
        {
            "name": "feature_columns",
            "type": "list",
            "default": [],
            "display_name": "Feature Columns",
            "description": "List of features.",
        },
        {
            "name": "outliers_fraction",
            "type": "float",
            "default": 0.05,
            "range": [0.01, 1],
            "display_name": "Outliers Fraction",
            "description": "Define the ratio of outliers.",
        },
        {
            "name": "number_of_neighbors",
            "type": "int",
            "default": 50,
            "range": [5, 500],
            "display_name": "Number Of Neighbors",
            "description": "Number of neighbors for a vector.",
        },
        {
            "name": "norm",
            "type": "str",
            "default": "L1",
            "display_name": "Distance Norm",
            "description": "Metric that will be used for the distance computation.",
        },
        {
            "name": "assign_unknown",
            "type": "bool",
            "default": False,
            "display_name": "Assign Unknown",
            "description": "Assign unknown label to outliers.",
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def isolation_forest_filtering_sub_function(outliers_fraction, number_of_samples):
    # Isolation Forest
    return IsolationForest(
        bootstrap=False,
        contamination=outliers_fraction,
        max_features=1.0,
        max_samples=number_of_samples,
        n_estimators=100,
        n_jobs=1,
        random_state=np.random.RandomState(42),
        verbose=0,
    )


def isolation_forest_filtering(
    input_data: DataFrame,
    label_column: str,
    filtering_label: str = None,
    feature_columns: Optional[List[str]] = None,
    outliers_fraction: float = 0.05,
    assign_unknown: bool = False,
):
    """
    Isolation Forest Algorithm returns the anomaly score of each sample using the IsolationForest
    algorithm. The "Isolation Forest" isolates observations by randomly selecting a feature and
    then randomly selecting a split value between the maximum and minimum values of the selected
    feature.

    Args:
        input_data: Dataframe, feature set that is results of generator_set or feature_selector
        label_column (str): Label column name.
        filtering_label: List<String>, List of classes. if it is not defined, it use all classes.
        feature_columns: List<String>, List of features. if it is not defined, it uses all features.
        outliers_fraction (float) : Define the ratio of outliers.
        assign_unknown (bool): Assign unknown label to outliers.

    Returns:
        DataFrame containing features without outliers and noise.

    Examples:
        >>> client.pipeline.reset(delete_cache=False)
        >>> df = client.datasets.load_activity_raw()
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_generator([{'name':'Downsample',
                                     'params':{"columns": ['accelx','accely','accelz'],
                                               "new_length": 5 }}])
        >>> results, stats = client.pipeline.execute()
        # List of all data indices before the filtering algorithm
        >>> results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5, 6, 7, 8]

        >>> client.pipeline.add_transform("Isolation Forest Filtering",
                           params={ "outliers_fraction": 0.01})

        >>> results, stats = client.pipeline.execute()
        # List of all data indices after the filtering algorithm
        >>>results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5]


    """

    clf = None
    input_data = filtering(
        input_data,
        clf,
        "isolation_forest_filtering",
        filtering_label,
        feature_columns,
        outliers_fraction,
        label_column,
        assign_unknown=assign_unknown,
    )

    return input_data


isolation_forest_filtering_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {
            "name": "filtering_label",
            "type": "list",
            "default": [],
            "display_name": "Filtering Label",
            "description": "List of classes.",
        },
        {
            "name": "feature_columns",
            "type": "list",
            "default": [],
            "display_name": "Feature Columns",
            "description": "List of features.",
        },
        {
            "name": "outliers_fraction",
            "type": "float",
            "default": 0.05,
            "range": [0.01, 1],
            "display_name": "Outliers Fraction",
            "description": "Define the ratio of outliers.",
        },
        {
            "name": "assign_unknown",
            "type": "bool",
            "default": False,
            "display_name": "Assign Unknown",
            "description": "Assign unknown label to outliers.",
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def one_class_SVM_filtering(
    input_data: DataFrame,
    label_column: str,
    filtering_label: Optional[str] = None,
    feature_columns: Optional[str] = None,
    outliers_fraction: float = 0.05,
    kernel: str = "rbf",
    assign_unknown: bool = False,
):
    """
    Unsupervised Outlier Detection. Estimate the support of a high-dimensional distribution. The implementation is based on libsvm.

    Args:
        input_data: Dataframe, feature set that is results of generator_set or feature_selector
        label_column (str): Label column name.
        filtering_label: List<String>, List of classes. if it is not defined, it use all classes.
        feature_columns: List<String>, List of features. if it is not defined, it uses all features.
        outliers_fraction (float) : Define the ratio of outliers.
        kernel (str) : Specifies the kernel type to be used in the algorithm. It must be one of 'linear', 'poly', 'rbf', 'sigmoid'.
        assign_unknown (bool): Assign unknown label to outliers.

    Returns:
        DataFrame containing features without outliers and noise.

    Examples:
        >>> client.pipeline.reset(delete_cache=False)
        >>> df = client.datasets.load_activity_raw()
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_generator([{'name':'Downsample',
                                     'params':{"columns": ['accelx','accely','accelz'],
                                               "new_length": 5 }}])
        >>> results, stats = client.pipeline.execute()
        # List of all data indices before the filtering algorithm
        >>> results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5, 6, 7, 8]

        >>> client.pipeline.add_transform("One Class SVM filtering",
                           params={"outliers_fraction": 0.05})

        >>> results, stats = client.pipeline.execute()
        # List of all data indices after the filtering algorithm
        >>>results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5]

    """

    # OneClassSVM
    clf = svm.OneClassSVM(
        cache_size=200,
        coef0=0.0,
        degree=3,
        gamma=0.1,
        kernel=kernel,
        max_iter=-1,
        nu=0.95 * outliers_fraction + 0.05,
        shrinking=True,
        tol=0.001,
        verbose=False,
    )

    return filtering(
        input_data,
        clf,
        "one_class_SVM_filtering",
        filtering_label,
        feature_columns,
        outliers_fraction,
        label_column,
        assign_unknown,
    )


one_class_SVM_filtering_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {
            "name": "filtering_label",
            "type": "list",
            "default": [],
            "display_name": "Filtering Label",
            "description": "List of classes.",
        },
        {
            "name": "feature_columns",
            "type": "list",
            "default": [],
            "display_name": "Feature Columns",
            "description": "List of features.",
        },
        {
            "name": "outliers_fraction",
            "type": "float",
            "default": 0.05,
            "range": [0.01, 1],
            "display_name": "Outliers Fraction",
            "description": "Define the ratio of outliers.",
        },
        {
            "name": "kernel",
            "type": "str",
            "default": "rbf",
            "display_name": "Kernel",
            "description": "Specifies the kernel type to be used in the algorithm. It must be one of 'linear', 'poly', 'rbf', 'sigmoid'.",
        },
        {
            "name": "assign_unknown",
            "type": "bool",
            "default": False,
            "display_name": "Assign Unknown",
            "description": "Assign unknown label to outliers.",
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def robust_covariance_filtering(
    input_data: DataFrame,
    label_column: str,
    filtering_label: Optional[str] = None,
    feature_columns: Optional[str] = None,
    outliers_fraction: float = 0.05,
    assign_unknown: bool = False,
):
    """
    Unsupervised Outlier Detection. An object for detecting outliers in a Gaussian distributed dataset.

    Args:
        input_data: Dataframe, feature set that is results of generator_set or feature_selector
        label_column (str): Label column name.
        filtering_label: List<String>, List of classes. if it is not defined, it use all classes.
        feature_columns: List<String>, List of features. if it is not defined, it uses all features.
        outliers_fraction (float) : An upper bound on the fraction of training errors and a lower bound of the fraction of support vectors. Should be in the interval (0, 1]. By default 0.5 will be taken.
        assign_unknown (bool): Assign unknown label to outliers.

    Returns:
        DataFrame containing features without outliers and noise.

    Examples:
        >>> client.pipeline.reset(delete_cache=False)
        >>> df = client.datasets.load_activity_raw()
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_generator([{'name':'Downsample',
                                     'params':{"columns": ['accelx','accely','accelz'],
                                               "new_length": 5 }}])
        >>> results, stats = client.pipeline.execute()
        # List of all data indices before the filtering algorithm
        >>> results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5, 6, 7, 8]

        >>> client.pipeline.add_transform("Robust Covariance Filtering",
                           params={"outliers_fraction": 0.05})

        >>> results, stats = client.pipeline.execute()
        # List of all data indices after the filtering algorithm
        >>>results.index.tolist()
            Out:
            [0, 1, 2, 3, 4, 5]

    """
    # Robust covariance
    clf = EllipticEnvelope(
        assume_centered=False,
        contamination=outliers_fraction,
        random_state=None,
        store_precision=True,
        support_fraction=None,
    )

    return filtering(
        input_data,
        clf,
        "robust_covariance_filtering",
        filtering_label,
        feature_columns,
        outliers_fraction,
        label_column,
        assign_unknown,
    )


robust_covariance_filtering_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {
            "name": "filtering_label",
            "type": "list",
            "default": [],
            "display_name": "Filtering Label",
            "description": "List of classes.",
        },
        {
            "name": "feature_columns",
            "type": "list",
            "default": [],
            "display_name": "Feature Columns",
            "description": "List of features.",
        },
        {
            "name": "outliers_fraction",
            "type": "float",
            "default": 0.05,
            "range": [0.01, 1],
            "display_name": "Outliers Fraction",
            "description": "Define the ratio of outliers.",
        },
        {
            "name": "assign_unknown",
            "type": "bool",
            "default": False,
            "display_name": "Assign Unknown",
            "description": "Assign unknown label to outliers.",
        },
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    "costs": [
        {"name": "Bytes", "value": "0"},
        {"name": "RAM", "value": "0"},
        {"name": "Microseconds", "value": "0"},
    ],
}


def undersample_majority_classes(
    input_data: DataFrame,
    label_column: str,
    target_class_size: Optional[int] = None,
    maximum_samples_size_per_class: Optional[int] = None,
    seed: Optional[int] = None,
):
    """
    Create a balanced data set by undersampling the majority classes using random sampling without replacement.

    Args:
        input_data (DataFrame): input DataFrame
        label_column (str): The column to split against
        target_class_size (int): Specifies the size of the minimum class to use, if None we will use
         the min class size. If size is greater than min class size we use min class size (default: None)
        seed (int): Specifies a random seed to use for sampling
        maximum_samples_size_per_class(int): Specifies the size of the maximum class to use per class,

    Returns:
        DataFrame containing undersampled classes

    """

    df_g = input_data.groupby(label_column)

    if maximum_samples_size_per_class:
        max_samples_per_class = maximum_samples_size_per_class
    else:
        max_samples_per_class = df_g.size().min()

        if target_class_size and max_samples_per_class > target_class_size:
            max_samples_per_class = target_class_size

    M = []
    for key in df_g.groups.keys():
        temp_samples_per_class = max_samples_per_class
        if (
            maximum_samples_size_per_class
            and len(df_g.get_group(key)) <= max_samples_per_class
        ):
            temp_samples_per_class = len(df_g.get_group(key))

        M.append(
            resample(
                df_g.get_group(key),
                replace=False,
                n_samples=temp_samples_per_class,
                random_state=seed,
            )
        )

    return concat(M).sort_values(by=label_column).reset_index(drop=True)


undersample_majority_classes_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str"},
        {"name": "target_class_size", "type": "int", "default": None},
        {"name": "maximum_samples_size_per_class", "type": "int", "default": None},
        {"name": "seed", "type": "int", "default": None},
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}


def augment_pad_segment(
    input_data: DataFrame, group_columns: List[str], sequence_length: int, noise: int
):
    """
    Pad a segment so that its length is equal to a specific sequence length

    Args:
        input_data (DataFrame): input DataFrame
        group_columns (str): The column to group by against (should 283 SegmentID)
        sequence_length (int): Specifies the size of the minimum class to use, if None we will use
         the min class size. If size is greater than min class size we use min class size (default: None)
        noise_level (int): max amount of noise to add to augmentation
    Returns:
        DataFrame containing padded segments

    """

    if "SegmentID" not in group_columns and "SegmentID" in input_data.columns:
        group_columns += ["SegmentID"]

    df_g = input_data.groupby(group_columns)
    data_columns = [x for x in input_data.columns if x not in group_columns]

    M = []
    for key in df_g.groups.keys():
        tmp_df = df_g.get_group(key)[data_columns].astype(int)
        dim = tmp_df.shape[1]

        if len(tmp_df) < sequence_length:
            tmp_data = ((np.random.rand(sequence_length, dim) - 0.5) * noise).astype(
                int
            )
            tmp_data += (tmp_df.values[0] + tmp_df.values[-1]) // 2
            l = (len(tmp_data) - len(tmp_df)) // 2
            tmp_data[l : l + len(tmp_df)] = tmp_df.values

        else:
            tmp_data = tmp_df.values[:sequence_length]

        M.append(DataFrame(tmp_data, columns=data_columns))

        for index, value in enumerate(group_columns):
            M[-1][value] = key[index]

    return concat(M).reset_index(drop=True)


augment_pad_segment_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list"},
        {"name": "sequence_length", "type": "int"},
        {"name": "noise", "type": "int", "default": 0},
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}
