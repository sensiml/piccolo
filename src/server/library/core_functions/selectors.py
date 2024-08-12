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

# -----------------------------------------------------------
# Feature selection based on correlation
# -----------------------------------------------------------
from typing import List, Optional, Tuple

import numpy as np
from library.core_functions.utils.fs_information_gain import (
    feature_selector_with_information_gain,
)
from library.core_functions.utils.utils import get_costs
from library.exceptions import InputParameterException
from numpy import (
    amax,
    argsort,
    corrcoef,
    delete,
    unique,
    where,
)
from pandas import DataFrame, concat
from scipy.stats import ttest_ind
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import RFE, SelectKBest, VarianceThreshold, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC


def add_index_by_generator(d, key, val):
    if key in d:
        if not val in d[key]:
            d[key].append(val)
    else:
        d[key] = [val]
    return d


def index_random_choice(index_list, n_select):

    unique_index = list(set(index_list))
    n_index = len(unique_index)

    if n_select > n_index:
        n_select = n_index

    return list(np.random.choice(unique_index, n_select, replace=False))


def add_index_by_generator(d, key, val):
    if key in d:
        if not val in d[key]:
            d[key].append(val)
    else:
        d[key] = [val]
    return d


def get_generator_index(df_features, generators):

    gen_dict = {}  # {generator_name : index name}
    gen_names = df_features.Generator.values
    gen_index = df_features.GeneratorTrueIndex.values

    remaining_generator_index = []
    selected_generator_index = []
    all_selected_generator_list = []

    selected_generators_items = [
        generator["generator_names"] for generator in generators
    ]

    for item in selected_generators_items:
        if isinstance(item, str):
            all_selected_generator_list += [item]
        elif isinstance(item, list):
            all_selected_generator_list += item

    for i, generator in enumerate(gen_names):
        gen_dict = add_index_by_generator(gen_dict, generator, gen_index[i])

        if not generator in all_selected_generator_list:
            remaining_generator_index += [gen_index[i]]

    remaining_generator_index = list(set(remaining_generator_index))

    for i, generator in enumerate(generators):
        generator_names = generator["generator_names"]
        if isinstance(generator_names, str) and generator_names in gen_dict:
            selected_generator_index += index_random_choice(
                gen_dict[generator_names], generator["number"]
            )
        elif isinstance(generator_names, list):
            gen_list = []
            for name in generator_names:
                if name in gen_dict:
                    gen_list += gen_dict[name]
            selected_generator_index += index_random_choice(
                gen_list, generator["number"]
            )

    return selected_generator_index, remaining_generator_index


def feature_selector_by_family(
    input_data: DataFrame,
    generators: list,
    max_number_generators: Optional[int] = 5,
    random_seed: Optional[int] = None,
    passthrough_columns: Optional[list] = None,
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    This is an unsupervised method of feature selection. The goal is to randomly select features from the specified
    feature generators until the maximum number of generators given as input is reached. If no specific generator is
    provided, all feature generators have an equal chance to be selected.

    Args:
        input_data (DataFrame): Input data to perform feature selection on.
        generators (List[Dict[str, Union[str, int]]]): A list of feature generators to select from. Each member of
            this list is a dictionary of this form:
            {"generator_names": [(str)] or (str), "number": (int)},
            where "generator_names" lists the name(s) of the generator(s) to select from, and "number" is the desired
            number of generators.
        max_number_generators (int): [Default 5] The maximum number of feature generators to keep.
        random_seed (int): [Optional] Random initialization seed.
        passthrough_columns (List[str]): [Optional] A list of columns to include in the output DataFrame in addition
            to the selected features.
        **kwargs: Additional keyword arguments to pass.

    Returns:
        Tuple[DataFrame, List[str]]: A tuple containing a DataFrame that includes the selected features and the
        passthrough columns and a list containing the unselected feature columns.

    Examples:
        >>> client.project  = <project_name>
        >>> client.pipeline = <piepline_name>
        >>> df = client.datasets.load_activity_raw()
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data',
                                     data_columns = ['accelx', 'accely', 'accelz', 'gyrox', 'gyroy', 'gyroz'],
                                     group_columns = ['Subject','Class', 'Rep'],
                                     label_column = 'Class')
        >>> client.pipeline.add_feature_generator([
                    {
                        "name": "MFCC",
                        "params": {
                            "columns": ["accelx"],
                            "sample_rate": 10,
                            "cepstra_count": 3,
                        },
                    },
                    {
                        "name": "Downsample",
                        "params": {"columns": ["accelx", "accely", "accelz"], "new_length": 3},
                    },
                    {
                        "name": "MFCC",
                        "params": {
                            "columns": ["accely"],
                            "sample_rate": 10,
                            "cepstra_count": 4,
                        },
                    },
                    {
                        "name": "Power Spectrum",
                        "params": {
                            "columns": ["accelx"],
                            "number_of_bins": 5,
                            "window_type": "hanning",
                        },
                    },
                    {
                        "name": "Absolute Area",
                        "params": {
                            "sample_rate": 10,
                            "columns": ["accelx", "accelz"],
                        },
                    },
                ])
        >>>
        >>> results, stats = client.pipeline.execute()

        >>> results.columns.tolist()
            # List of all features before the feature selection algorithm
            Out:
            ['gen_0001_accelxmfcc_000000',
            'gen_0001_accelxmfcc_000001',
            'gen_0001_accelxmfcc_000002',
            'Class',
            'Rep',
            'Subject',
            'gen_0002_accelxDownsample_0',
            'gen_0002_accelxDownsample_1',
            'gen_0002_accelxDownsample_2',
            'gen_0003_accelyDownsample_0',
            'gen_0003_accelyDownsample_1',
            'gen_0003_accelyDownsample_2',
            'gen_0004_accelzDownsample_0',
            'gen_0004_accelzDownsample_1',
            'gen_0004_accelzDownsample_2',
            'gen_0005_accelymfcc_000000',
            'gen_0005_accelymfcc_000001',
            'gen_0005_accelymfcc_000002',
            'gen_0005_accelymfcc_000003',
            'gen_0006_accelxPowerSpec_000000',
            'gen_0006_accelxPowerSpec_000001',
            'gen_0006_accelxPowerSpec_000002',
            'gen_0006_accelxPowerSpec_000003',
            'gen_0006_accelxPowerSpec_000004',
            'gen_0007_accelxAbsArea',
            'gen_0008_accelzAbsArea']

        Here, feature selector picks upto 5 feature generators, of which 2 could be from the "Downsample" generator
        and 2 of them could be either "MFCC" or "Power Spectrum" feature and the rest could be any other feature
        not listed in any of the "generator_names" lists.

        >>> client.pipeline.add_feature_selector([{"name": "Feature Selector By Family",
                                                "params":{
                                                    "max_number_generators": 5,
                                                    "seed": 1,
                                                    "generators":[
                                                    {
                                                        "generator_names": "Downsample",
                                                        "number": 2
                                                    },
                                                    {
                                                        "generator_names": ["MFCC", "Power Spectrum"],
                                                        "number": 2
                                                    }]
                                            }}])

        >>> results, stats = client.pipeline.execute()

        >>> results.columns.tolist()
            # List of all features after the feature selection algorithm
            # Because of the random nature of this selector function, the output might be
            # slightly different each time based on the chosen seed
            Out:
            ['Class',
            'Rep',
            'Subject',
            'gen_0003_accelyDownsample_0',
            'gen_0003_accelyDownsample_1',
            'gen_0003_accelyDownsample_2',
            'gen_0002_accelxDownsample_0',
            'gen_0002_accelxDownsample_1',
            'gen_0002_accelxDownsample_2',
            'gen_0005_accelymfcc_000000',
            'gen_0005_accelymfcc_000001',
            'gen_0005_accelymfcc_000002',
            'gen_0005_accelymfcc_000003',
            'gen_0001_accelxmfcc_000000',
            'gen_0001_accelxmfcc_000001',
            'gen_0001_accelxmfcc_000002',
            'gen_0008_accelzAbsArea']

    """

    if not random_seed is None:
        np.random.seed(random_seed)

    df_features = kwargs.get("feature_table")

    if max_number_generators is None and generators is None:
        return input_data, []

    if max_number_generators and max_number_generators > 0 and generators is None:
        random_chosen_generator_index = index_random_choice(
            df_features.GeneratorTrueIndex.values, max_number_generators
        )

    else:
        selected_generator_index, remaining_generator_index = get_generator_index(
            df_features, generators
        )

        if max_number_generators and max_number_generators > 0:
            if len(selected_generator_index) > max_number_generators:
                random_chosen_generator_index = index_random_choice(
                    selected_generator_index, max_number_generators
                )
            else:
                random_chosen_generator_index = (
                    selected_generator_index
                    + index_random_choice(
                        remaining_generator_index,
                        max_number_generators - len(selected_generator_index),
                    )
                )
        else:
            random_chosen_generator_index = selected_generator_index

    columns_to_keep = []
    for keep_group_index in random_chosen_generator_index:
        columns_to_keep += df_features.Feature[
            df_features.GeneratorTrueIndex == keep_group_index
        ].values.tolist()

    new_column_list = passthrough_columns + columns_to_keep
    unselected_features = list(set(input_data.columns).difference(set(new_column_list)))

    return input_data[new_column_list], unselected_features


feature_selector_by_family_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "max_number_generators",
            "type": "int",
            "default": 5,
            "range": [0, 24],
            "description": "Maximum number of feature generators to keep",
        },
        {
            "name": "generators",
            "type": "list",
            "element_type": "dict",
            "default": None,
            "description": "Number of generator groups to keep",
        },
        {
            "name": "random_seed",
            "type": "int",
            "default": None,
            "description": "seed to initialize the random state",
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "description": "List of non sensor columns",
            "handle_by_set": True,
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def custom_feature_selection(
    input_data: DataFrame,
    custom_feature_selection: list,
    passthrough_columns: list,
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    This is a feature selection method which allows custom feature selection. This takes a list of strings where each
    value is the feature name to keep.

    Args:
        input_data: DataFrame, input data
        custom_feature_selection: list, feature generator names to keep
        passthrough_columns: list, columns to pass through without modification
        **kwargs: additional keyword arguments

    Returns:
        tuple: tuple containing:
            selected_features: DataFrame, which includes selected features and the passthrough columns.
            unselected_features: list, unselected features
    """

    # parse the columns of the dataframe to get the features
    columns_to_select_from = [
        col for col in input_data.columns if col not in passthrough_columns
    ]

    columns_to_keep = [
        feature
        for feature in columns_to_select_from
        if feature in custom_feature_selection
    ]

    new_column_list = passthrough_columns + columns_to_keep
    unselected_features = list(set(input_data.columns).difference(set(new_column_list)))

    return input_data[new_column_list], unselected_features


custom_feature_selection_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "custom_feature_selection",
            "type": "list",
            "description": "List of features to keep",
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "description": "List of non sensor columns",
            "handle_by_set": True,
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def custom_feature_selection_by_index(
    input_data: DataFrame,
    custom_feature_selection: dict,
    passthrough_columns: list,
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    This is a feature selection method which allows custom feature selection. This takes a dictionary where the key is the
    feature generator number and the value is an array of the features for the feature generator to keep. All feature generators
    that are not added as keys in the dictionary will be dropped.

    Args:
        input_data (DataFrame): Input data to perform feature selection on.
        custom_feature_selection (dict): A dictionary of feature generators and their corresponding features to keep.
        passthrough_columns (list):  A list of columns to include in the output DataFrame in addition to the selected
            features.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Tuple[DataFrame, list]: A tuple containing the selected features and the passthrough columns as a DataFrame, and a list
        of unselected features.

    Example:

        .. code-block:: python

            client.pipeline.add_feature_selector([{'name': 'Custom Feature Selection By Index',
                                        'params': {"custom_feature_selection":
                                                {1: [0], 2:[0], 3:[1,2,3,4]},
                                        }}])

            # would select the features 0 from feature generator 1 and 2, and
            # features 1,2,3,4 from the generator feature generator 3.

    """

    # parse the columns of the dataframe to get the features
    columns_to_select_from = [
        col for col in input_data.columns if col not in passthrough_columns
    ]

    feature_table = kwargs.get("feature_table")

    columns_to_keep = []
    for genetor_index, generator_generator_indexes in custom_feature_selection.items():
        columns_to_keep.extend(
            feature_table[
                (feature_table["GeneratorTrueIndex"] == int(genetor_index))
                & (
                    feature_table["GeneratorFamilyIndex"].isin(
                        generator_generator_indexes
                    )
                )
            ].Feature.values.tolist()
        )

    if not columns_to_keep:
        raise Exception("No features were selected!")

    new_column_list = passthrough_columns + columns_to_keep
    unselected_features = list(set(input_data.columns).difference(set(new_column_list)))

    return input_data[new_column_list], unselected_features


custom_feature_selection_by_index_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "custom_feature_selection",
            "type": "dict",
            "description": "Describes which features to keep",
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "description": "List of non sensor columns",
            "handle_by_set": True,
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def check_number_of_classes(input_data, label_column):
    """
    Check number of classes for feature selector
    """
    if len(input_data[label_column].unique()) < 2:
        raise InputParameterException(
            "Error: Selected 'add_feature_selector' option needs samples of at least 2 classes in the data, but the data contains only one class: "
            + str(input_data[label_column].unique())
        )


def information_gain(
    input_data: DataFrame,
    label_column: str,
    feature_number: int = 2,
    passthrough_columns: Optional[list] = None,
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    This is a supervised feature selection algorithm that selects features based on Information Gain (one class vs other
    classes approaches).

    First, it calculates Information Gain (IG) for each class separately to all features then sort features based on IG
    scores, std and mean differences. Feature with higher IG is a better feature to differentiate the class from others. At the end, each feature
    has their own feature list.

    Args:
        input_data (DataFrame): Input data.
        label_column (str): The label column in the input_data.
        feature_number (int): [Default 2] Number of features to select for each class.
        passthrough_columns (list): [Optional] A list of columns to include in the output DataFrame in addition to
            the selected features.
        **kwargs: Additional keyword arguments.

    Returns:
        Tuple[DataFrame, list]: A tuple containing the selected features and the passthrough columns as a DataFrame, and a list
        of unselected features.

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
        # List of all features before the feature selection algorithm
        >>> results.columns.tolist()
            Out:
            [u'Class',
             u'Subject',
             u'gen_0001_accelx_0',
             u'gen_0001_accelx_1',
             u'gen_0001_accelx_2',
             u'gen_0001_accelx_3',
             u'gen_0001_accelx_4',
             u'gen_0002_accely_0',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_3',
             u'gen_0002_accely_4',
             u'gen_0003_accelz_0',
             u'gen_0003_accelz_1',
             u'gen_0003_accelz_2',
             u'gen_0003_accelz_3',
             u'gen_0003_accelz_4']

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', results, force=True,
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_selector([{'name':'Information Gain',
                                    'params':{"feature_number": 3}}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            Out:
                  Class Subject  gen_0001_accelx_0  gen_0001_accelx_1  gen_0001_accelx_2
            0  Crawling     s01         347.881775         372.258789         208.341858
            1  Crawling     s02         347.713013         224.231735          91.971481
            2  Crawling     s03         545.664429         503.276642         200.263031
            3   Running     s01         -21.588972         -23.511278         -16.322056
            4   Running     s02         422.405182         453.950897         431.893585
            5   Running     s03         350.105774         366.373627         360.777466
            6   Walking     s01         -10.362945         -46.967007           0.492386
            7   Walking     s02         375.751343         413.259460         374.443237
            8   Walking     s03         353.421906         317.618164         283.627502

    """

    # Sanity Checks
    check_number_of_classes(input_data, label_column)

    new_column_list = feature_selector_with_information_gain(
        input_data, label_column, feature_number, ignore_col=passthrough_columns
    )

    unselected_features = [
        col for col in input_data.columns if col not in new_column_list
    ]
    return input_data[new_column_list], unselected_features


information_gain_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "label_column",
            "type": "str",
            "description": "Name of the label column",
            "handle_by_set": True,
        },
        {
            "name": "feature_number",
            "type": "int",
            "default": 2,
            "description": "Number of features will be selected for each class",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def vt_select(
    input_data: DataFrame,
    threshold: float = 0.01,
    passthrough_columns: Optional[list] = None,
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    Feature selector that removes all low-variance features.

    This step is an unsupervised feature selection algorithm and looks only at the input features (X) and not the Labels
    or outputs (y). Select features whose variance exceeds the given threshold (default is set to 0.05). It should be
    applied prior to standardization.

    Args:
        input_data (DataFrame): Input data.
        threshold (float): [Default 0.01] Minimum variance threshold under which features should be eliminated.
        passthrough_columns (list): [Optional] A list of columns to include in the output DataFrame in addition to
            the selected features.

    Returns:
        tuple: tuple containing:
            selected_features (DataFrame): which includes selected features and the passthrough columns.
            unselected_features (list): unselected features

    Examples:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> client.pipeline.set_input_data('test_data', df, force=True,
                            data_columns = ['accelx', 'accely', 'accelz'],
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_generator([{'name':'Downsample',
                                     'params':{"columns": ['accelx','accely','accelz'],
                                               "new_length": 5 }}])
        >>> results, stats = client.pipeline.execute()
        # List of all features before the feature selection algorithm
        >>> results.columns.tolist()
            Out:
            [u'Class',
             u'Subject',
             u'gen_0001_accelx_0',
             u'gen_0001_accelx_1',
             u'gen_0001_accelx_2',
             u'gen_0001_accelx_3',
             u'gen_0001_accelx_4',
             u'gen_0002_accely_0',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_3',
             u'gen_0002_accely_4',
             u'gen_0003_accelz_0',
             u'gen_0003_accelz_1',
             u'gen_0003_accelz_2',
             u'gen_0003_accelz_3',
             u'gen_0003_accelz_4']

        >>> client.pipeline.add_feature_selector([{'name':'Variance Threshold',
                                    'params':{"threshold": 4513492.05}}])

        >>> results, stats = client.pipeline.execute()
        >>> print results
            Out:
            [u'Class',
             u'Subject',
             u'gen_0002_accely_0',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_3',
             u'gen_0002_accely_4']

    """

    df_out = DataFrame()
    feature_cols = [col for col in input_data.columns if col not in passthrough_columns]
    features = input_data[feature_cols]
    sel = VarianceThreshold(threshold=threshold)
    reduced_df = DataFrame(sel.fit_transform(features), index=input_data.index)
    df_out = concat([df_out, reduced_df], axis=1)
    selected_features = features.columns[sel.get_support(indices=True)].tolist()
    unselected_features = [
        col
        for col in input_data.columns
        if col not in selected_features + passthrough_columns
    ]
    df_out.columns = selected_features
    df_out[passthrough_columns] = input_data[passthrough_columns]
    return df_out, unselected_features


vt_select_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "threshold",
            "type": "float",
            "default": 0.01,
            "description": "Minimum variance threshold under which features should be eliminated (0 to ~)",
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "The set of columns the selector should ignore",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def rfe_select(
    input_data: DataFrame,
    label_column: str,
    method: str,
    number_of_features: int,
    passthrough_columns: Optional[list],
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    This is a supervised method of feature selection. The goal of recursive feature elimination (RFE) is to select
    features by recursively considering smaller and smaller sets of features. First, the estimator (`method`: 'Log R'
    or 'Linear SVC') is trained on the initial set of features and weights are assigned to each one of them. Then,
    features whose absolute weights are the smallest are pruned from the current set of features. That procedure is
    recursively repeated on the pruned set until the desired number of features `number_of_features` to select is
    eventually reached.

    Args:
        input_data (DataFrame): Input data to perform feature selection on.
        label_column (str): Name of the column containing the labels.
        method (str): The type of selection method. Two options available: 1) `Log R` and 2) `Linear SVC`. For
            `Log R`, the value of Inverse of regularization strength `C` is default to 1.0 and `penalty` is
            defaulted to `l1`. For `Linear SVC`, the default for `C` is 0.01, `penalty` is `l1` and `dual` is
            set to `False`.
        number_of_features (int): The number of features you would like the selector to reduce to.
        passthrough_columns (list): [Optional] A list of columns to include in the output DataFrame in addition to
            the selected features.

    Returns:
        tuple: A tuple containing:
            - DataFrame: A DataFrame that includes the selected features and the passthrough columns.
            - list: A list of unselected features.

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
        # # List of all features before the feature selection algorithm
        >>> results.columns.tolist()
            Out:
            [u'Class',
             u'Subject',
             u'gen_0001_accelx_0',
             u'gen_0001_accelx_1',
             u'gen_0001_accelx_2',
             u'gen_0001_accelx_3',
             u'gen_0001_accelx_4',
             u'gen_0002_accely_0',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_3',
             u'gen_0002_accely_4',
             u'gen_0003_accelz_0',
             u'gen_0003_accelz_1',
             u'gen_0003_accelz_2',
             u'gen_0003_accelz_3',
             u'gen_0003_accelz_4']

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', results, force=True,
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_selector([{'name':'Recursive Feature Elimination',
                                    'params':{"method": "Log R",
                                              "number_of_features": 3}}],
                                  params={'number_of_features':3})
        >>> results, stats = client.pipeline.execute()

        >>> print results
            Out:
                  Class Subject  gen_0001_accelx_2  gen_0003_accelz_1  gen_0003_accelz_4
            0  Crawling     s01         208.341858        3881.038330        3900.734863
            1  Crawling     s02          91.971481        3821.513428        3896.376221
            2  Crawling     s03         200.263031        3896.349121        3889.297119
            3   Running     s01         -16.322056         641.164185         605.192993
            4   Running     s02         431.893585         870.608459         846.671204
            5   Running     s03         360.777466         263.184052         234.177200
            6   Walking     s01           0.492386         559.139587         558.538086
            7   Walking     s02         374.443237         658.902710         669.394592
            8   Walking     s03         283.627502         -87.612816         -98.735649

    Notes:
        For more information on defaults of `Log R`, please see: http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html#sklearn.linear_model.LogisticRegression
        For `Linear SVC`, please see: http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html#sklearn.svm.LinearSVC

    """

    if input_data.shape[0] > 2000:

        raise ValueError(
            "Recursive Feature Elimination can only be used for data sets with less than 1000 samples. Try Information Gain for larger feature sets first then fine tune with RFE."
        )

    if input_data.shape[1] > 25:

        raise ValueError(
            "Recursive Feature Elimination can only be used for data sets with less than 25 Features. Try Information Gain for larger feature sets first then fine tune with RFE."
        )

    label_column = input_data[label_column]
    df_out = DataFrame()
    selected_features = []

    i_cols = [col for col in input_data.columns if col not in passthrough_columns]
    df_pre = input_data[i_cols]

    # Disabled, user must explicitly use transforms for normalization and scaling
    # df = DataFrame(scale(df_pre))
    # df.columns = df_pre.columns
    df = df_pre

    if method == "Log R":
        clf = LogisticRegression(
            C=1.0, penalty="l1", solver="liblinear", multi_class="auto"
        )
    elif method == "Linear SVC":
        clf = LinearSVC(C=0.01, penalty="l1", dual=False)
    # Couldn't get this method to work - it may be incompatible with RFE
    # elif (method == 'Random Log R'):
    #    clf = RandomizedLogisticRegression()

    sel = RFE(
        estimator=clf, n_features_to_select=number_of_features
    )  # setup the method
    X_new = sel.fit_transform(df, label_column)  # apply the method

    reduced_df = DataFrame(X_new, index=input_data.index)
    df_out = concat([df_out, reduced_df], axis=1)
    selected_features = df.columns[sel.get_support(indices=True)].tolist()
    unselected_features = [
        col
        for col in input_data.columns
        if col not in selected_features + passthrough_columns
    ]
    df_out.columns = selected_features
    df_out[passthrough_columns] = input_data[passthrough_columns]

    return df_out, unselected_features


rfe_select_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "method",
            "type": "str",
            "description": "Selection method",
            "default": "Log R",
            "options": [{"name": "Log R"}, {"name": "Linear SVC"}],
        },
        {
            "name": "number_of_features",
            "type": "int",
            "handle_by_set": False,
            "description": "The number of \
    features you would like the selector to reduce to",
            "default": 10,
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "The set of columns the selector should ignore",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def tree_select(
    input_data: DataFrame,
    label_column: str,
    number_of_features: int,
    passthrough_columns: Optional[list],
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    Select features using a supervised tree-based algorithm. This class implements a meta estimator that fits a number of randomized decision trees
    (a.k.a. extra-trees) on various sub-samples of the dataset and use averaging to improve the predictive accuracy and control overfitting.
    The default number of trees in the forest is set at 250, and the `random_state` to be 0. Please see notes for more information.

    Args:
        input_data (DataFrame): Input data.
        label_column (str): Label column of input data.
        number_of_features (int): The number of features you would like the selector to reduce to.
        passthrough_columns (list, optional): A list of columns to include in the output dataframe in addition to the selected features. Defaults to None.

    Returns:
        tuple: A tuple containing:
            - selected_features (DataFrame): DataFrame which includes selected features and the passthrough columns for each class.
            - unselected_features (list): A list of unselected features.

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
        # List of all features before the feature selection algorithm
        >>> results.columns.tolist()
            Out:
            [u'Class',
             u'Subject',
             u'gen_0001_accelx_0',
             u'gen_0001_accelx_1',
             u'gen_0001_accelx_2',
             u'gen_0001_accelx_3',
             u'gen_0001_accelx_4',
             u'gen_0002_accely_0',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_3',
             u'gen_0002_accely_4',
             u'gen_0003_accelz_0',
             u'gen_0003_accelz_1',
             u'gen_0003_accelz_2',
             u'gen_0003_accelz_3',
             u'gen_0003_accelz_4']

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', results, force=True,
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_selector([{'name':'Tree-based Selection', 'params':{ "number_of_features": 4 }}] )
        >>> results, stats = client.pipeline.execute()

        >>> print results
            Out:
                  Class Subject  gen_0002_accely_0  gen_0002_accely_1  gen_0002_accely_2  gen_0002_accely_3  gen_0002_accely_4  gen_0003_accelz_0  gen_0003_accelz_1  gen_0003_accelz_2  gen_0003_accelz_3  gen_0003_accelz_4
            0  Crawling     s01           1.669203           1.559860           1.526786           1.414068           1.413625           1.360500           1.368615           1.413445           1.426949           1.400083
            1  Crawling     s02           1.486925           1.418474           1.377726           1.414068           1.413625           1.360500           1.368615           1.388456           1.408576           1.397417
            2  Crawling     s03           1.035519           1.252789           1.332684           1.328587           1.324469           1.410274           1.414961           1.384032           1.345107           1.393088
            3   Running     s01          -0.700995          -0.678448          -0.706631          -0.674960          -0.713493          -0.572269          -0.600986          -0.582678          -0.560071          -0.615270
            4   Running     s02          -0.659030          -0.709012          -0.678594          -0.688869          -0.700753          -0.494247          -0.458891          -0.471897          -0.475010          -0.467597
            5   Running     s03          -0.712790          -0.713026          -0.740177          -0.728651          -0.733076          -0.836257          -0.835071          -0.868028          -0.855081          -0.842161
            6   Walking     s01          -0.701450          -0.714677          -0.692671          -0.716556          -0.696635          -0.652326          -0.651784          -0.640956          -0.655958          -0.643802
            7   Walking     s02          -0.698335          -0.689857          -0.696807          -0.702233          -0.682212          -0.551928          -0.590001          -0.570077          -0.558563          -0.576008
            8   Walking     s03          -0.719046          -0.726102          -0.722315          -0.727506          -0.712461          -1.077342          -1.052320          -1.052297          -1.075949          -1.045750

    Notes:
        For more information, please see: http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html

    """

    label_column = input_data[label_column]
    DataFrame()
    selected_features = []
    # list of all features
    i_cols = [col for col in input_data.columns if col not in passthrough_columns]
    df_pre = input_data[i_cols]

    # Disabled, user must explicitly use transforms for normalization and scaling
    # Normalize
    # df = DataFrame(scale(df_pre))
    # df.columns = df_pre.columns
    df = df_pre

    # Build a forest and compute the feature importances
    sel = ExtraTreesClassifier(n_estimators=250, random_state=0)  # setup the method
    sel.fit(df, label_column)  # apply the method

    # get the sorted indices
    importances = sel.feature_importances_
    indices = argsort(importances)[::-1]
    # select top number_of_features
    selected_features = df.columns[indices][:number_of_features].tolist()
    unselected_features = [
        col
        for col in input_data.columns
        if col not in selected_features + passthrough_columns
    ]

    return input_data[passthrough_columns + selected_features], unselected_features


tree_select_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "number_of_features",
            "type": "int",
            "handle_by_set": False,
            "description": "The number of features you would like the selector to reduce to",
            "default": 10,
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "The set of columns the selector should ignore",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def univariate_select(
    input_data: DataFrame,
    label_column: str,
    number_of_features: int,
    passthrough_columns: Optional[list] = None,
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    Univariate feature selection using ANOVA (Analysis of Variance) is a statistical method used to identify the most
    relevant features in a dataset by analyzing the variance between different groups. It is a supervised method of
    feature selection, which means that it requires labeled data.

    The ANOVA test calculates the F-value for each feature by comparing the variance within each class to the variance
    between classes. The higher the F-value, the more significant the feature is in differentiating between the classes.
    Univariate feature selection selects the top k features with the highest F-values, where k is a specified parameter.

    Args:
        input_data (DataFrame): Input data
        label_column (str): Label column name
        number_of_features (int): The number of features you would like the selector to reduce to.
        passthrough_columns (Optional[list], optional): List of columns to pass through. Defaults to None.

    Returns:
        tuple: Tuple containing:
            - DataFrame: DataFrame which includes selected features and the passthrough columns.
            - list: List of unselected features.

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
        # List of all features before the feature selection algorithm
        >>> results.columns.tolist()
            Out:
            [u'Class',
             u'Subject',
             u'gen_0001_accelx_0',
             u'gen_0001_accelx_1',
             u'gen_0001_accelx_2',
             u'gen_0001_accelx_3',
             u'gen_0001_accelx_4',
             u'gen_0002_accely_0',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_3',
             u'gen_0002_accely_4',
             u'gen_0003_accelz_0',
             u'gen_0003_accelz_1',
             u'gen_0003_accelz_2',
             u'gen_0003_accelz_3',
             u'gen_0003_accelz_4']

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', results, force=True,
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_selector([{'name':'Univariate Selection',
                            'params': {"number_of_features": 3 } }])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            Out:
                  Class Subject  gen_0002_accely_2  gen_0002_accely_3  gen_0002_accely_4
            0  Crawling     s01           1.526786           1.496120           1.500535
            1  Crawling     s02           1.377726           1.414068           1.413625
            2  Crawling     s03           1.332684           1.328587           1.324469
            3   Running     s01          -0.706631          -0.674960          -0.713493
            4   Running     s02          -0.678594          -0.688869          -0.700753
            5   Running     s03          -0.740177          -0.728651          -0.733076
            6   Walking     s01          -0.692671          -0.716556          -0.696635
            7   Walking     s02          -0.696807          -0.702233          -0.682212
            8   Walking     s03          -0.722315          -0.727506          -0.712461

    Notes:
        Please see the following for more information:
        http://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html
        http://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.f_classif.html#sklearn.feature_selection.f_classif

    """

    label_column = input_data[label_column]
    df_out = DataFrame()
    selected_features = []

    i_cols = [col for col in input_data.columns if col not in passthrough_columns]
    df_pre = input_data[i_cols]

    # Disabled, user must explicitly use transforms for normalization and scaling
    # Normalize
    # df = DataFrame(scale(df_pre))
    # df.columns = df_pre.columns
    df = df_pre
    if number_of_features > len(i_cols) - 1:
        number_of_features = "all"
    sel = SelectKBest(f_classif, k=number_of_features)  # set the method
    X_new = sel.fit_transform(df, label_column)  # apply the method
    reduced_df = DataFrame(X_new, index=input_data.index)
    df_out = concat([df_out, reduced_df], axis=1)
    selected_features = df.columns[sel.get_support(indices=True)].tolist()
    unselected_features = [
        col
        for col in input_data.columns
        if col not in selected_features + passthrough_columns
    ]
    df_out.columns = selected_features
    df_out[passthrough_columns] = input_data[passthrough_columns]

    return df_out, unselected_features


univariate_select_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "number_of_features",
            "type": "int",
            "handle_by_set": False,
            "description": "The number of \
    features you would like the selector to reduce to",
            "default": 1,
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "The set of columns the selector should ignore",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def correlation_select(
    input_data: DataFrame,
    threshold: float = 0.85,
    passthrough_columns: Optional[list] = None,
    **kwargs
) -> Tuple[DataFrame, list]:
    """
    Select features which do not highly correlate with each other. This method computes the correlation
    matrix between all features, and selects only those features which have a correlation coefficient
    with other selected features below the given threshold. This method can be useful in reducing the
    redundancy among selected features.

    Args:
        input_data (DataFrame): Input data
        threshold (float): The maximum allowed correlation coefficient between selected features.
            Features with higher correlation than this will be eliminated. Should be between 0 and 1.
            Default is 0.85.
        passthrough_columns (Optional[list]): List of columns to pass through. The selector will ignore
            these columns.

    Returns:
        tuple: Tuple containing:
            - DataFrame: DataFrame which includes selected features and the passthrough columns.
            - list: List of unselected features.
    """

    df_out = DataFrame()
    unselected_features = []

    numeric_columns = input_data.select_dtypes(include="number").columns
    i_cols = [
        col
        for col in input_data.columns
        if (col not in passthrough_columns and col in numeric_columns)
    ]
    df_pre = input_data[i_cols]

    # Scale
    # Disabled, user must explicitly use transforms for normalization and scaling
    # df = DataFrame(scale(df_pre))
    # df.columns = df_pre.columns
    df = df_pre

    cm = abs(corrcoef(df.T))  # Compute correlation coefficient matrix
    cm_t = threshold_clip(
        cm, threshmax=threshold, newval=-1
    )  # set to -1 the values > thresh

    # extract indices == -1
    del_idx = []
    for i in range(0, len(cm_t)):
        for j in range(i + 1, len(cm_t)):
            if cm_t[i, j] == -1:
                del_idx.append(j)

    if len(del_idx) > 0:  # if there are correlated features
        del_idx = unique(del_idx)  # find the unique ones
        cols = range(0, len(cm))
        selectCols = delete(cols, del_idx)  # delete them
        reduced_df = df_pre[
            selectCols
        ]  # extract data corresponding to selected columns
        df_out = concat([df_out, reduced_df], axis=1)
        selected_features = df_pre.columns[selectCols].tolist()
        unselected_features = [
            col
            for col in input_data.columns
            if col not in selected_features + passthrough_columns
        ]
        df_out.columns = selected_features
        df_out[passthrough_columns] = input_data[passthrough_columns]
    else:
        df_out = input_data

    return df_out, unselected_features


correlation_select_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "threshold",
            "type": "float",
            "description": "Maximum correlation \
    threshold over which features should be eliminated (0 to 1)",
            "default": 0.95,
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "The set of columns the selector should ignore",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def get_indices_to_drop_in_correlation_matrix(df, thresh):
    indices_to_drop = []
    while True:
        my_count = df.apply(lambda x: len(where(x >= thresh)[0]), axis=1)
        if (my_count == 0).all(axis=0):
            return indices_to_drop
        idx_to_drop = np.where(my_count == amax(my_count))[0]
        idx_to_drop = idx_to_drop.flatten()
        if len(idx_to_drop) > 1:
            t_sum = df.apply(np.sum, axis=1)
            to_fill_zero_idx = np.setdiff1d(t_sum.index, idx_to_drop)
            t_sum[to_fill_zero_idx] = 0
            idx_to_drop = np.where(t_sum == amax(t_sum))[0].flatten()
            if len(idx_to_drop) > 1:
                # pickup the first element if there is still a tie
                # we cannot drop more than one vector at a time
                temp = idx_to_drop[0]
                idx_to_drop = np.array([temp])

        df.iloc[idx_to_drop, :] = 0
        df.iloc[:, idx_to_drop] = 0
        indices_to_drop.extend(idx_to_drop.tolist())
    return indices_to_drop


def correlation_select_remove_most_corr_first(
    input_data: DataFrame,
    threshold: float = 0.85,
    passthrough_columns: Optional[List[str]] = None,
    feature_table: Optional[DataFrame] = None,
    median_sample_size: Optional[float] = None,
) -> Tuple[DataFrame, list]:
    """

    Correlation feature selection is an unsupervised feature selection algorithm that aims
    to select features based on their absolute correlation with the other features in the
    dataset. The algorithm begins by computing a pairwise correlation matrix of all the
    features. It then proceeds to identify a candidate feature for removal, which is the
    feature that correlates with the highest number of other features that have a correlation
    coefficient greater than the specified `threshold`. This process is repeated iteratively
    until there are no more features with a correlation coefficient higher than the threshold,
    or when there are no features left. The main objective is to remove the most correlated
    features first, which could help reduce multicollinearity issues and improve model performance.


    Args:
        input_data: DataFrame containing the input features
        threshold: float, default=0.85. Minimum correlation threshold over which
            features should be eliminated (0 to 1).
        passthrough_columns: Optional list of column names to be ignored by the selector.
        feature_table: Optional DataFrame that contains the correlation matrix
            of input features. If this argument is provided, the correlation matrix will
            not be calculated again.
        median_sample_size: Optional float value to use instead of median when a feature
            has no correlation with other features.

    Returns:
        Tuple[DataFrame, list]: A tuple containing the DataFrame with selected features
            and the list of removed features.

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
        # List of all features before the feature selection algorithm
        >>> results.columns.tolist()
            Out:
            [u'Class',
             u'Subject',
             u'gen_0001_accelx_0',
             u'gen_0001_accelx_1',
             u'gen_0001_accelx_2',
             u'gen_0001_accelx_3',
             u'gen_0001_accelx_4',
             u'gen_0002_accely_0',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_3',
             u'gen_0002_accely_4',
             u'gen_0003_accelz_0',
             u'gen_0003_accelz_1',
             u'gen_0003_accelz_2',
             u'gen_0003_accelz_3',
             u'gen_0003_accelz_4']

        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('test_data', results, force=True,
                            group_columns = ['Subject','Class'],
                            label_column = 'Class')
        >>> client.pipeline.add_feature_selector([{'name':'Correlation Threshold',
                                    'params':{ "threshold": 0.85 }}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            Out:
            [u'Class',
             u'Subject',
             u'gen_0001_accelx_2',
             u'gen_0001_accelx_4',
             u'gen_0002_accely_0']

    """

    if isinstance(feature_table, DataFrame) and median_sample_size:
        get_costs(feature_table, median_sample_size)

    numeric_columns = input_data.select_dtypes(include="number").columns
    i_cols = [
        col
        for col in input_data.columns
        if (col not in passthrough_columns and col in numeric_columns)
    ]

    df_pre = input_data[i_cols]
    # create correlation matrix
    cm_df = DataFrame(abs(corrcoef(df_pre.T)))
    np.fill_diagonal(cm_df.values, 0)
    # index of the features that will be removed
    del_idx = get_indices_to_drop_in_correlation_matrix(cm_df, threshold)

    if len(del_idx) > 0:  # if there are correlated features
        cols = range(cm_df.shape[0])
        selectCols = delete(cols, del_idx)  # delete them
        selected_features = df_pre.columns[selectCols].tolist()
        df_out = df_pre.loc[:, selected_features]
        unselected_features = df_pre.columns[del_idx].tolist()
        df_out[passthrough_columns] = input_data[passthrough_columns]
    else:
        df_out = input_data
        unselected_features = []

    return df_out, unselected_features


correlation_select_remove_most_corr_first_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "threshold",
            "type": "float",
            "description": "Maximum correlation \
    threshold over which features should be eliminated (0 to 1)",
            "default": 0.95,
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "The set of columns the selector should ignore",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def ttest_select(
    input_data: DataFrame,
    label_column: str,
    feature_number: int,
    passthrough_columns: Optional[List[str]],
    **kwargs
) -> Tuple[DataFrame, List[str]]:
    """
    This is a supervised feature selection algorithm that selects features based on a two-tailed t-test.
    It computes the p-values and selects the top-performing number of features for each class as defined by feature_number.
    It returns a reduced combined list of all the selected features.

    Args:
        input_data (DataFrame): Input data
        label_column (str): Column containing class labels
        feature_number (int): Number of features to select for each class
        passthrough_columns (Optional[List[str]]): List of columns that the selector should ignore

    Returns:
        Tuple[DataFrame, List[str]]: A tuple containing:
            - DataFrame: DataFrame which includes selected features and the passthrough columns.
            - List[str]: List of unselected features.

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
        # List of all features before the feature selection algorithm
        >>> results.columns.tolist()
            Out:
            [u'Class',
             u'Subject',
             u'gen_0001_accelx_0',
             u'gen_0001_accelx_1',
             u'gen_0001_accelx_2',
             u'gen_0001_accelx_3',
             u'gen_0001_accelx_4',
             u'gen_0002_accely_0',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_3',
             u'gen_0002_accely_4',
             u'gen_0003_accelz_0',
             u'gen_0003_accelz_1',
             u'gen_0003_accelz_2',
             u'gen_0003_accelz_3',
             u'gen_0003_accelz_4']

        >>> client.pipeline.add_feature_selector([{'name':'ttest Feature Selector',
                'params':{"feature_number": 2 }}])
        >>> results, stats = client.pipeline.execute()

        >>> print results
            Out:
             [u'Class',
             u'Subject',
             u'gen_0002_accely_1',
             u'gen_0002_accely_2',
             u'gen_0002_accely_4',
             u'gen_0003_accelz_1',
             u'gen_0003_accelz_4']

    """

    # Sanity Checks
    check_number_of_classes(input_data, label_column)

    features = [col for col in input_data.columns if col not in passthrough_columns]

    all_class = input_data[label_column].unique()
    best_features_list = []

    # for each clas find the best features
    for pv_class in all_class:
        other_class = list(set(all_class) - set(pv_class))
        temp_A = np.array(
            input_data[input_data[label_column].isin([pv_class])][features]
        )
        temp_L = np.array(
            input_data[input_data[label_column].isin(other_class)][features]
        )

        # NOTE: ttest raises warnings when two columns have the same value.
        # ie signal duration all have same window size. it will return nan
        t, p = ttest_ind(temp_A, temp_L, equal_var=False)

        # sort the p values and select the best features (NaN's are placed at the bottom)
        best_features = (
            DataFrame([p, features])
            .T.sort_values(by=[0], ascending=True)[1]
            .tolist()[:feature_number]
        )
        best_features_list.extend(best_features)

    best_features_list = list(np.unique(best_features_list))

    unselected_features = list(set(features) - set(best_features_list))

    return input_data[passthrough_columns + best_features_list], unselected_features


ttest_select_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "feature_number",
            "type": "int",
            "handle_by_set": False,
            "description": "The number of features you would like select for each class",
            "default": 1,
        },
        {
            "name": "passthrough_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "The set of columns the selector should ignore",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def threshold_clip(a, threshmin=None, threshmax=None, newval=0):
    a = np.array(a, copy=True)
    mask = np.zeros(a.shape, dtype=bool)
    if threshmin is not None:
        mask |= (a < threshmin).filled(False)

    if threshmax is not None:
        mask |= (a > threshmax).filled(False)

    a[mask] = newval
