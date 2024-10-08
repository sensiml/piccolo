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

from typing import Optional

VALIDATION_METHODS = {
    "name": "validation_methods",
    "type": "list",
    "element_type": "str",
    "handle_by_set": True,
    "options": [
        {"name": "Stratified K-Fold Cross-Validation"},
        {"name": "Stratified Shuffle Split"},
        {"name": "Set Sample Validation"},
        {"name": "Split by Metadata Value"},
        {"name": "Recall"},
        {"name": "Stratified Metadata k-fold"},
        {"name": "Metadata k-fold"},
        {"name": "Leave-One-Subject-Out"},
    ],
}


def k_fold_strat(number_of_folds):
    """
    A variation of k-fold which returns stratified folds: each set contains approximately the
    same percentage of samples of each target class as the complete set. In other words, for a
    data set consisting of total 100 samples with 40 samples from class 1 and 60 samples from
    class 2, for a stratified 2-fold scheme, each fold will consist of total 50 samples with 20
    samples from class 1 and 30 samples from class 2.

    Args:
        number_of_folds (int): the number of stratified folds to produce
        test_size (float): the percentage of data to hold out as a final test set
        shuffle (bool): Specifies whether or not to shuffle the data before performing the
            cross-fold validation splits.

    """

    return None


k_fold_strat_contracts = {
    "input_contract": [
        {"name": "number_of_folds", "type": "int", "default": 3, "range": [2, 5]},
        {"name": "test_size", "type": "float", "default": 0.0, "range": [0.0, 0.4]},
        {"name": "shuffle", "type": "bool", "default": True},
    ],
    "output_contract": [],
}


def metadata_and_label_k_fold(number_of_folds, metadata_name):
    """
    K-fold iterator variant with non-overlapping metadata/group and label
    combination which also attempts to evenly distribute the number of each
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
    of "action 1's" across your folds.


    Args:
        number_of_folds (int): the number of stratified folds to produce
        metadata_name (str): the metadata to group on for splitting data into folds.
    """

    return None


metadata_and_label_k_fold_contracts = {
    "input_contract": [
        {"name": "number_of_folds", "type": "int", "default": 3, "range": [2, 5]},
        {"name": "metadata_name", "type": "str", "default": ""},
    ],
    "output_contract": [],
}


def metadata_k_fold(number_of_folds, metadata_name):
    """
    K-fold iterator variant with non-overlapping metadata groups.
    The same group will not appear in two different folds (the number of
    distinct groups has to be at least equal to the number of folds).
    The folds are approximately balanced in the sense that the number of
    distinct groups is approximately the same in each fold.


    Args:
        number_of_folds (int): the number of stratified folds to produce
        metadata_name (str): the metadata to group on for splitting data into folds.
    """

    return None


metadata_k_fold_contracts = {
    "input_contract": [
        {"name": "number_of_folds", "type": "int", "default": 3, "range": [2, 5]},
        {"name": "metadata_name", "type": "str", "default": ""},
    ],
    "output_contract": [],
}


def stratified_shuffle_split(test_size, validation_size):
    """
    A validation scheme which splits the data set into training, validation, and (optionally)
    test sets based on the parameters provided, with similar distribution of labels (hence
    stratified).

    In other words, for a data set consisting of 100 samples in total with 40
    samples from class 1 and 60 samples from class 2, for stratified shuffle split with
    validation_size = 0.4, the validation set will consist of 40 samples with 16 samples from
    class 1 and 24 samples from class 2, and the training set will consist of 60 samples
    with 24 samples from class 1 and 36 samples from class 2.

    For each fold, training and validation data re-shuffle and split.

    Args:
        test_size (float): target percent of total size to use for testing
        validation_size (float): target percent of total size to use for validation
        number_of_folds (int): the number of stratified folds (iteration) to produce

    """

    return None


stratified_shuffle_split_contracts = {
    "input_contract": [
        {"name": "test_size", "type": "float", "default": 0.0, "range": [0.0, 0.4]},
        {
            "name": "validation_size",
            "type": "float",
            "default": 0.2,
            "range": [0.0, 0.4],
        },
        {"name": "number_of_folds", "type": "int", "default": 1, "range": [1, 5]},
    ],
    "output_contract": [],
}


def leave_one_subject_out(group_columns):
    """
    A cross-validation scheme which holds out the samples for all but one subject for testing
    in each fold. In other words, for a data set consisting of 10 subjects, each fold will
    consist of a training set from 9 subjects and test set from 1 subject; thus, in all, there
    will be 10 folds, one for each left out test subject.

    Args:
        group_columns (list[str]): list of column names that define the groups (subjects)
    """

    return None


leave_one_subject_out_contracts = {
    "input_contract": [
        {"type": "list", "name": "group_columns", "element_type": "str"},
        {"name": "test_size", "type": "float", "default": 0.0, "range": [0.0, 0.5]},
    ],
    "output_contract": [],
}


def set_sampler(
    set_mean,
    set_stdev,
    mean_limit,
    stdev_limit,
    retries,
    samples_per_class,
    norm,
    optimize_mean_std,
    binary_class1,
    validation_samples_per_class,
):
    """
    A validation scheme wherein the data set is divided into training and test sets based
    on two statistical parameters, mean and standard deviation. The user selects the number
    of events in each category and has the option to select the subset mean, standard deviation,
    number in the validation set and the acceptable limit in the number of retries of random selection
    from the original data set.


    Example:
     samples = {'Class 1':2500, "Class 2":2500}
     validation = {'Class 1':2000, "Class 2":2000}

     client.pipeline.set_validation_method({"name": "Set Sample Validation",
                                         "inputs": {"samples_per_class": samples,
                                                    "validation_samples_per_class": validation}})

    Args:
        data_set_mean (numpy.array[floats]): mean value of each feature in dataset
        data_set_stdev (numpy.array[floats]): standard deviation of each feature in dataset
        samples_per_class (dict): Number of members in subset for training, validation,
            and testing
        validation_samples_per_class (dict): Overrides the number of members in subset for
            validation if not empty
        mean_limit (numpy.array[floats]): minimum acceptable difference between mean of
            subset and data for any feature
        stdev_limit (numpy.array[floats]): minimum acceptable difference between standard
            deviation of subset and data for any feature
        retries (int): Number of attempts to find a subset with similar statistics
        norm (list[str]): ['Lsup','L1'] Distance norm for determining whether subset is
            within user defined limits
        optimize_mean_std (list[str]): ['both','mean'] Logic to use for optimizing subset.
            If 'mean', then only mean distance must be improved. If 'both', then both mean
            and stdev must improve.
        binary_class1 (str): Category name that will be the working class in set composition
    """

    return None


set_sampler_contracts = {
    "input_contract": [
        {"name": "set_mean", "type": "list", "default": []},
        {"name": "set_stdev", "type": "list", "default": []},
        {"name": "mean_limit", "type": "list", "default": []},
        {"name": "stdev_limit", "type": "list", "default": []},
        {"type": "int", "name": "retries", "default": 5, "range": [1, 25]},
        {"name": "samples_per_class", "type": "dict", "default": {}},
        {"name": "validation_samples_per_class", "type": "dict", "default": {}},
        {
            "type": "str",
            "name": "norm",
            "options": [{"name": "L1"}, {"name": "Lsup"}],
            "default": "L1",
        },
        {
            "type": "str",
            "name": "optimize_mean_std",
            "options": [{"name": "both"}, {"name": "mean"}],
            "default": "both",
        },
        {"type": "str", "name": "binary_class1"},
    ],
    "output_contract": [],
}


def split_by_metadata_value(metadata_name, training_values, validation_values):
    """
    A validation scheme wherein the data set is divided into training and test sets based
    on the metadata value. In other words, for a data set consisting of 100 samples with the
    metadata column set to 'train' for 60 samples, and 'test' for 40 samples, the training set
    will consist of 60 samples for which the metadata value is 'train' and the test set will
    consist of 40 samples for which the metadata value is 'test'.

    Args:
        metadata_name (str): name of the metadata column to use for splitting
        training_values (list[str]): list of values of the named column to select samples for
          training
        validation_values (list[str)): list of values of the named column to select samples for
          validation
    """

    return None


split_by_metadata_value_contracts = {
    "input_contract": [
        {
            "name": "metadata_name",
            "lookup_field": "metadata_name",
            "type": "str",
            "default": "Set",
        },
        {
            "name": "training_values",
            "lookup_field": "metadata_label_values",
            "type": "list",
            "element_type": "str",
            "default": ["Train"],
            "options": ["Train"],
        },
        {
            "name": "validation_values",
            "lookup_field": "metadata_label_values",
            "type": "list",
            "element_type": "str",
            "default": ["Validate"],
            "options": ["Validate", "Test"],
        },
    ],
    "output_contract": [],
}


def recall():
    """
    The simplest validation method, wherein the training set itself is used as the
    test set. In other words, for a data set consisting of 100 samples in total, both
    the training set and the test set consist of the same set of 100 samples.
    """

    return None


recall_contracts = {"input_contract": [], "output_contract": []}


def pme(distance_mode, classification_mode, max_aif, min_aif):
    """
    PME or pattern matching engine is a distance based classifier that is optimized for high performance
    on resource constrained devices. It computes the distances between an input vector and a database
    of stored patterns and returns a prediction based on the classification classifier settings.

    There are three distance metrics that can be computed L1, LSUP and DTW(Dynamic Time Warping).

    The are two classification criteria, RBF and KNN. For RBF every pattern in the database is given an influence
    field that the distance between it and the input vector must be less than in order to pattern to fire.
    KNN returns the category of pattern with the smallest computed distance bewteen it and the input vector.

    Args:
        distance_mode (str): L1, Lsup or DTW
        classification_mode (str):  RBF or KNN
        max_aif (int): the maximum value of the influence field
        min_aif (int): the minimum value of the influence field
        reserved_patterns (int): The number of patterns to reserve in the database in addition to the
         predefined patterns during training
        online_learning  (bool): To generate the code for online learning on the edge device
         this takes up additional SRAM, but can be used to tune the model at the edge.
        num_channels (int): the number of channels that are specified for calculations when DTW is used as
         the distance metric (default: 1).

    """

    return None


pme_contracts = {
    "input_contract": [
        {
            "name": "distance_mode",
            "type": "str",
            "options": [{"name": "L1"}, {"name": "Lsup"}, {"name": "DTW"}],
            "default": "L1",
        },
        {
            "name": "classification_mode",
            "type": "str",
            "options": [{"name": "RBF"}, {"name": "KNN"}],
            "default": "KNN",
            "description": "Set the classifier recognition mode. KNN mode will always return a result corresponding to the nearest neuron that fires. RBF will only return results that are within the influence field. If the feature vector does not fall within any of the influence fiels RBF will return Unknown or 0.",
        },
        {
            "name": "max_aif",
            "type": "int",
            "default": 400,
            "range": [1, 16384],
            "description": "The maximum size of the influence field for a pattern in the database. The influence field determines the distance from the center that it will activate.",
        },
        {
            "name": "min_aif",
            "type": "int",
            "default": 25,
            "range": [1, 16383],
            "description": "The minimum size of the influence field for a pattern in the database. Patterns will not be created with an influence field smaller than this number.",
        },
        {
            "name": "num_channels",
            "type": "int",
            "default": 1,
            "description": "the number of channels that are specified for calculations when DTW is used as the distance metric (default: 1)",
            "range": [1, 12],
        },
        {
            "name": "reserved_patterns",
            "type": "int",
            "default": 0,
            "description": "The number of patterns to reserve in the database in addition to the predefined patterns during training",
            "range": [0, 1000],
        },
        {"name": "reinforcement_learning", "type": "bool", "default": False},
    ],
    "output_contracts": [],
}


def vanilla_burlington(
    input_data,
    label_column,
    number_of_iterations,
    ignore_columns,
    classifiers,
    validation_methods,
    turbo,
    number_of_neurons,
    aggressive_neuron_creation,
    ranking_metric,
):
    """
    RBF with Neuron Allocation Optimization takes as input feature vectors, corresponding
    class labels, and desired number of iterations (or trials), and outputs a set of
    models. For each iteration the input vectors are randomly shuffled and presented to
    the PME classifier which either places the pattern as a neuron or does
    not. When a neuron is placed, an area of influence (AIF) is determined based on the
    neuron's proximity to other neurons in the model and their respective classes.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        number_of_iterations (int): the number of times to shuffle the training set;
        turbo (boolean): a flag that when True runs through the set of unplaced feature
            vectors repeatedly until no new neurons are placed (default is True)
        number_of_neurons (int): the maximum allowed number of neurons; when the
            model reaches this number, the algorithm will stop training
        aggressive_neuron_creation (bool): flag for placing neurons even if they are within
            the influence field of another neuron of the same category (default is False)
        ranking_metric (str): Method to score models by when evaluating best candidate.
            Options: [f1_score, sensitivity, accuracy]

    Returns:
        a set of models

    """

    return None


base_pme_training_input_contract = [
    {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
    {"name": "label_column", "type": "str", "handle_by_set": True},
    {
        "name": "remove_unknown",
        "type": "boolean",
        "default": False,
        "description": "If there is an Unknown label, remove that from the database of patterns prior to saving the model.",
    },
]

vanilla_burlington_contracts = {
    "input_contract": base_pme_training_input_contract
    + [
        {
            "name": "number_of_iterations",
            "type": "int",
            "default": 100,
            "range": [1, 1000],
            "description": "The number of times to shuffle the training set and rerun the algorithm.",
        },
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "PME"}],
        },
        {
            "name": "turbo",
            "type": "bool",
            "handle_by_set": False,
            "default": True,
            "description": "The algorithm will repeatedly runs through the set of unplaced feature vectors until no new neurons are created",
        },
        {
            "name": "ranking_metric",
            "type": "str",
            "handle_by_set": False,
            "default": "f1_score",
            "options": [
                {"name": "f1_score"},
                {"name": "accuracy"},
                {"name": "sensitivity"},
            ],
        },
        {
            "name": "number_of_neurons",
            "type": "int",
            "handle_by_set": False,
            "default": 128,
            "range": [1, 16384],
        },
        {
            "name": "aggressive_neuron_creation",
            "type": "bool",
            "default": True,
            "description": "The algorithm will place a pattern even if they are within the influence field of another pattern of the same category",
        },
        VALIDATION_METHODS,
    ],
    "output_contract": [],
}


def cluster_learn(
    input_data,
    label_column,
    number_of_neurons,
    linkage_method,
    centroid_calculation,
    flip,
    cluster_method,
    aif_method,
    singleton_aif,
    min_number_of_dominant_vector,
    max_number_of_weak_vector,
    ignore_columns,
    classifiers,
    validation_methods,
):
    """
    Hierarchical Clustering with Neuron Optimization takes as input feature vectors,
    corresponding class labels, and desired number of patterns, and outputs a model.

    Each pattern in a model consists of a centroid, its class label, and its area of influence
    (AIF). Each centroid is calculated as an average of objects in the cluster, each class
    label is the label of the majority class, and each AIF is the distance between the
    centroid and the farthest object in that cluster.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        number_of_neurons (int): the maximum number of output clusters (neurons) desired
        linkage_method (str): options are average, complete, ward, and single (default
            is average)
        centroid_calculation (str): options are robust, mean, and median (default is
            robust)
        flip (int): default is 1
        cluster_method (str): options are DLCH, DHC, and kmeans (default is DLHC)
        aif_method (str): options are min, max, robust, mean, median (default is max)
        singleton_aif (int): default is 0
        min_number_of_dominant_vector (int) : It is used for pruning. It defines min. number of
            vector for dominant class in the cluster.
        max_number_of_weak_vector(int) : It is used for pruning. It defines max. number of
            vector for weak class in the cluster.

    Returns:
        one or more models

    """

    return None


cluster_learn_contracts = {
    "input_contract": base_pme_training_input_contract
    + [
        {
            "name": "number_of_neurons",
            "type": "int",
            "handle_by_set": False,
            "default": 32,
            "range": [1, 16384],
        },
        {
            "name": "linkage_method",
            "type": "str",
            "handle_by_set": False,
            "options": [
                {"name": "average"},
                {"name": "complete"},
                {"name": "ward"},
                {"name": "single"},
            ],
            "default": "average",
        },
        {
            "name": "centroid_calculation",
            "type": "str",
            "handle_by_set": False,
            "options": [{"name": "robust"}, {"name": "mean"}, {"name": "median"}],
            "default": "robust",
        },
        {"name": "flip", "type": "int", "handle_by_set": False, "default": 1},
        {
            "name": "cluster_method",
            "type": "str",
            "handle_by_set": False,
            "options": [{"name": "DHC"}, {"name": "DLHC"}, {"name": "kmeans"}],
            "default": "kmeans",
        },
        {
            "name": "aif_method",
            "type": "str",
            "handle_by_set": False,
            "options": [
                {"name": "min"},
                {"name": "max"},
                {"name": "robust"},
                {"name": "mean"},
                {"name": "median"},
            ],
            "default": "max",
        },
        {"name": "singleton_aif", "type": "int", "handle_by_set": False, "default": 0},
        {
            "name": "min_number_of_dominant_vector",
            "type": "int",
            "handle_by_set": False,
            "default": 3,
            "range": [1, 20],
        },
        {
            "name": "max_number_of_weak_vector",
            "type": "int",
            "handle_by_set": False,
            "default": 1,
            "range": [1, 20],
        },
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "PME"}],
        },
        VALIDATION_METHODS,
    ],
    "output_contract": [],
}


def neuron_optimize(
    input_data,
    label_column,
    number_of_neurons,
    linkage_method,
    centroid_calculation,
    norm_order,
    flip,
    cluster_method,
    aif_method,
    singleton_aif,
    ignore_columns,
    classifiers,
    validation_methods,
):
    """
    Neuron Optimization performs an optimized grid search over KNN/RBF and the number of neurons for
    the parameters of Hierarchical Clustering with Neuron Optimization. Takes as input feature vectors,
    corresponding class labels and outputs a model.

    Each  pattern in a model consists of a centroid, its class label, and its area of influence (AIF).
    Each centroid is calculated as an average of objects in the cluster, each class label is the label
    of the majority class, and each AIF is the distance between the centroid and the farthest object
    in that cluster.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        neuron_range (list): the range of max neurons spaces to search over specified as [Min, Max]
        linkage_method (str): options are average, complete, ward, and single (default
            is average)
        centroid_calculation (str): options are robust, mean, and median (default is
            robust)
        flip (int): default is 1
        cluster_method (str): options are DLCH, DHC, and kmeans (default is DLHC)
        aif_method (str): options are min, max, robust, mean, median (default is max)
        singleton_aif (int): default is 0
        min_number_of_dominant_vector (int) : It is used for pruning. It defines min. number of
            vector for dominant class in the cluster.
        max_number_of_weak_vector(int) : It is used for pruning. It defines max. number of
            vector for weak class in the cluster.

    Returns:
        one or more models
    "description": "."}


    return None
    """


neuron_optimize_contracts = {
    "input_contract": base_pme_training_input_contract
    + [
        {
            "name": "neuron_range",
            "type": "list",
            "element_type": "int",
            "min_elements": 2,
            "max_elements": 2,
            "default": [5, 30],
            "range": [1, 128],
            "description": "The range of max neurons spaces to serach over specified as [Min, Max]",
        },
        {
            "name": "linkage_method",
            "type": "str",
            "handle_by_set": False,
            "options": [
                {"name": "average"},
                {"name": "complete"},
                {"name": "ward"},
                {"name": "single"},
            ],
            "default": "average",
        },
        {
            "name": "centroid_calculation",
            "type": "str",
            "handle_by_set": False,
            "options": [{"name": "robust"}, {"name": "mean"}, {"name": "median"}],
            "default": "robust",
        },
        {
            "name": "flip",
            "type": "int",
            "handle_by_set": False,
            "default": 1,
            "range": [1, 10],
        },
        {
            "name": "cluster_method",
            "type": "str",
            "handle_by_set": False,
            "options": [{"name": "DHC"}, {"name": "DLHC"}],
            "default": "DLHC",
        },
        {
            "name": "aif_method",
            "type": "str",
            "handle_by_set": False,
            "options": [
                {"name": "min"},
                {"name": "max"},
                {"name": "robust"},
                {"name": "mean"},
                {"name": "median"},
            ],
            "default": "max",
        },
        {"name": "singleton_aif", "type": "int", "handle_by_set": False, "default": 0},
        {
            "name": "min_number_of_dominant_vector",
            "type": "int",
            "handle_by_set": False,
            "default": 3,
            "range": [1, 100],
        },
        {
            "name": "max_number_of_weak_vector",
            "type": "int",
            "handle_by_set": False,
            "default": 1,
            "range": [1, 100],
        },
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "PME"}],
        },
        VALIDATION_METHODS,
    ],
    "output_contract": [],
}


def train_n_prune(
    input_data,
    label_column,
    chunk_size,
    inverse_relearn_frequency,
    max_neurons,
    ignore_columns,
    classifiers,
    validation_methods,
    aggressive_neuron_creation,
):
    """
    The Train and Prune algorithm takes as input feature vectors, corresponding class
    labels, and maximum desired number of neurons, and outputs a model.

    The training vectors are partitioned into subsets (chunks) and presented to the PME
    classifier which places neurons and determines areas of influence (AIFs). After each
    subset is learned, the neurons that fired the most on the validation set are retained
    and the others are removed (pruned) from the model. After a defined number of train and
    prune cycles, the complete retained set of neurons is then re-learned, which results in
    larger neuron AIFs. Train/prune/re-learn cycles continue to run on all of the remaining
    chunks, keeping the total number of neurons within the limit while giving preference to
    neurons that fire frequently.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        chunk_size (int): the number of training vectors in each chunk
        inverse_relearn_frequency (int): the number of chunks to train and prune between
         each re-learn phase
        max_neurons (int): the maximum allowed number of neurons
        aggressive_neuron_creation (bool): flag for placing neurons even if they are within
         the influence field of another neuron of the same category (default is False)

    Returns:
        a model

    """

    return None


train_n_prune_contracts = {
    "input_contract": base_pme_training_input_contract
    + [
        {
            "name": "chunk_size",
            "type": "int",
            "handle_by_set": False,
            "default": 20,
            "range": [1, 1000],
        },
        {
            "name": "inverse_relearn_frequency",
            "type": "int",
            "handle_by_set": False,
            "default": 5,
            "range": [1, 1000],
        },
        {
            "name": "max_neurons",
            "type": "int",
            "handle_by_set": False,
            "default": 64,
            "range": [1, 16384],
        },
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "PME"}],
        },
        {"name": "aggressive_neuron_creation", "type": "bool", "default": True},
        VALIDATION_METHODS,
    ],
    "output_contract": [],
}


def load_model_pme(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    validation_methods,
    neuron_array,
):
    """
    Load Neuron Array takes an input of feature vectors, corresponding class labels,
    and a neuron array to use for classification.  The neuron array is loaded and
    classification is performed.

    Note: This training algorithm does not perform optimizations on the provided neurons.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        neuron_array (list): A list of neurons to load into the hardware simulator.
        class_map (dict): class map for converting labels to neuron categories.

    Returns:
        a set of models

    """

    return None


load_model_pme_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "PME"}],
        },
        VALIDATION_METHODS,
        {
            "name": "neuron_array",
            "type": "list",
            "element_type": "dict",
            "handle_by_set": False,
            "default": [],
        },
        {"name": "class_map", "type": "dict", "handle_by_set": False, "default": {}},
    ],
    "output_contract": [],
}


def decision_tree_ensemble():
    """
    The decision tree ensemble classifier is an ensemble of decision trees that are evaluated against an input vector. Each
    decision tree in the ensemble provides a single prediction and the majority vote of all the trees is returned
    as the prediction for the ensemble.

    """

    return None


decision_tree_ensemble_contracts = {"input_contract": [], "output_contract": []}


def train_random_forest(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    validation_methods,
    n_estimators,
    max_depth,
):
    """
    Train an ensemble of decision tree classifiers using the random forest training algorithm. A random forest is
    a meta estimator that fits a number of decision tree classifiers on various sub-samples of the dataset and
    uses averaging to improve the predictive accuracy and control overfitting. The sub-sample size is always
    the same as the original input sample size but the samples are drawn with replacement

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        max_depth (int): The max depth to allow a decision tree to reach
        n_estimators (int): The number of decision trees to build.

    Returns:
        a set of models

    """

    return None


train_random_forest_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "Decision Tree Ensemble"}],
        },
        VALIDATION_METHODS,
        {"name": "max_depth", "type": "int", "handle_by_set": False, "default": 5},
        {"name": "n_estimators", "type": "int", "handle_by_set": False, "default": 25},
    ],
    "output_contract": [],
}


def bonsai():
    """
    Bonsai is a tree model for supervised learning tasks such as binary and multi-class classification,
    regression, ranking, etc. Bonsai learns a single, shallow, sparse tree with powerful predictors at
    internal and leaf nodes. This allows Bonsai to achieve state-of-the-art prediction accuracies
    while making predictions efficiently in microseconds to milliseconds (depending on processor speed)
    using models that fit in a few KB of memory.

    Bonsai was developed by Microsoft, for detailed information see the `ICML 2017 Paper <https://github.com/Microsoft/EdgeML/wiki/files/BonsaiPaper.pdf>`_.

    """

    return None


bonsai_contracts = {"input_contract": [], "output_contract": []}


def train_bonsai(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    validation_methods,
    projection_dimension,
    tree_depth,
    sigma,
):
    """
    Train a Bonsais Tree Classifier using backpropagation.

    For detailed information see the `ICML 2017 Paper <https://github.com/Microsoft/EdgeML/wiki/files/BonsaiPaper.pdf>`_

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        epochs (str): The number of training epochs to iterate over
        batch_size (float): The size of batches to use during training
        learning_rate (float): The learning rate for training optimization
        project_dimensions (int): The number of dimensions to project the input feature space into
        sigma (float): tunable hyperparameter
        reg_W (float): regularization for W matrix
        reg_V (float): regularization for V matrix
        reg_Theta (float): regularization for Theta matrix
        reg_Z (float): regularization for Z matrix
        sparse_V (float): sparcity factor for V matrix
        sparse_Theta (float): sparcity factor for Theta matrix
        sparse_W (float): sparcity factor for W matrix
        sparse_Z (float): sparcity factor fo Z matrix


    Returns:
        model parameters for a bonsai tree classifier

    """

    return None


train_bonsai_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "Bonsai"}],
        },
        VALIDATION_METHODS,
        {
            "name": "projection_dimension",
            "type": "int",
            "handle_by_set": False,
            "default": 10,
            "range": [1, 50],
        },
        {
            "name": "tree_depth",
            "type": "int",
            "handle_by_set": False,
            "default": 4,
            "range": [2, 10],
        },
        {
            "name": "sigma",
            "type": "float",
            "handle_by_set": False,
            "default": 1.0,
            "range": [0.001, 10.0],
        },
        {
            "name": "epochs",
            "type": "int",
            "handle_by_set": False,
            "default": 100,
            "range": [1, 2000],
        },
        {
            "name": "batch_size",
            "type": "int",
            "handle_by_set": False,
            "default": 25,
            "range": [1, 100],
        },
        {
            "name": "reg_W",
            "type": "float",
            "handle_by_set": False,
            "default": 0.001,
            "range": [0.0001, 1.0],
        },
        {
            "name": "reg_V",
            "type": "float",
            "handle_by_set": False,
            "default": 0.001,
            "range": [0.0001, 1.0],
        },
        {
            "name": "reg_Theta",
            "type": "float",
            "handle_by_set": False,
            "default": 0.001,
            "range": [0.0001, 1.0],
        },
        {
            "name": "reg_Z",
            "type": "float",
            "handle_by_set": False,
            "default": 0.0001,
            "range": [0.0001, 1.0],
        },
        {
            "name": "sparse_V",
            "type": "float",
            "handle_by_set": False,
            "default": 1,
            "range": [0.0, 1.0],
        },
        {
            "name": "sparse_Theta",
            "type": "float",
            "handle_by_set": False,
            "default": 1,
            "range": [0.0, 1.0],
        },
        {
            "name": "sparse_W",
            "type": "float",
            "handle_by_set": False,
            "default": 1,
            "range": [0.0, 1.0],
        },
        {
            "name": "sparse_Z",
            "type": "float",
            "handle_by_set": False,
            "default": 1,
            "range": [0.0, 1.0],
        },
        {
            "name": "learning_rate",
            "type": "int",
            "handle_by_set": False,
            "default": 0.001,
            "range": [0.0001, 0.1],
        },
    ],
    "output_contract": [],
}


def boosted_tree_ensemble():
    """
    The boosted tree ensemble classifier is an ensemble of decision trees that are evaluated against an input vector. Each
    decision tree in the ensemble provides a bias towards a predicted value and the sum overall all biases determines
    the final prediction.

    """

    return None


boosted_tree_ensemble_contracts = {"input_contract": [], "output_contract": []}


def train_gradient_boosting(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    validation_methods,
    n_estimators,
    max_depth,
):
    """
    Train an ensemble of boosted tree classifiers using the xGBoost training algorithm.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        max_depth (int): The max depth to allow a decision tree to reach
        n_estimators (int): The number of decision trees to build.

    Returns:
        a trained model

    """

    return None


train_gradient_boosting_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "Boosted Tree Ensemble"}],
        },
        VALIDATION_METHODS,
        {"name": "max_depth", "type": "int", "handle_by_set": False, "default": 5},
        {"name": "n_estimators", "type": "int", "handle_by_set": False, "default": 25},
    ],
    "output_contract": [],
}


def tensorflow_micro():
    """
    The Tensorflow Micro Classifier uses Tensorflow Lite for Microcontrollers, an inference engine
    from Google optimized run machine learning models on embedded devices.

    Tensorflow Lite for Microcontrollers supports a subset of all Tensorflow functions. For a full
    list see `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.

    For additional documentation on Tensorflow Lite for Microcontrollers see `here <https://www.tensorflow.org/lite/microcontrollers>`_.
    """

    return None


tensorflow_micro_contracts = {"input_contract": [], "output_contract": []}


def neural_network():
    """
    The Neural Network uses Tensorflow Lite for Microcontrollers, an inference engine
    from Google optimized run machine learning models on embedded devices.

    Tensorflow Lite for Microcontrollers supports a subset of all Tensorflow functions. For a full
    list see `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.

    For additional documentation on Tensorflow Lite for Microcontrollers see `here <https://www.tensorflow.org/lite/microcontrollers>`_.
    """

    return None


neural_network_contracts = {"input_contract": [], "output_contract": []}


def load_model_tensorflow_micro(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    validation_methods,
):
    """
    Provides the ability to upload a TensorFlow Lite flatbuffer to use as the final classifier step in a pipeline.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        model_parameters (int): The flatbuffer object of your TensorFlow micro model
        class_map (dict): class map for converting labels to output
        estimator_type (str): defines if this estimator performs regression or classification, defaults to classification
        threshold (float):  if no values are greater than the threshold, classify as Unknown
        train_history (dict): training history for this model
        model_json (dict): expects the model json file from the tensorflow api tf_model.to_json()


    Example:

        SensiML provides the ability to train and bring your own NN architecture to use as the classifier for your pipeline.
        This example starts from the point where you have created features using the SensiML Toolkit

            >>> x_train, x_test, x_validate, y_train, y_test, y_validate, class_map = \
            >>>     client.pipeline.features_to_tensor(fv_t, test=0.0, validate=.1)

        Tensorflow Lite Micro only supports a subset of the full tensorflow functions. For a full list of available functions
        see the `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.
        Use the Keras tensorflow API to create the NN graph.

            >>> from tensorflow.keras import layers
            >>> import tensorflow as tf
            >>> tf_model = tf.keras.Sequential()
            >>> tf_model.add(layers.Dense(12, activation='relu',kernel_regularizer='l1', input_shape=(x_train.shape[1],)))
            >>> tf_model.add(layers.Dropout(0.1))
            >>> tf_model.add(layers.Dense(8, activation='relu', input_shape=(x_train.shape[1],)))
            >>> tf_model.add(layers.Dropout(0.1))
            >>> tf_model.add(layers.Dense(y_train.shape[1], activation='softmax'))
            >>> tf_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            >>> tf_model.summary()
            >>> train_history = {'loss':[], 'val_loss':[], 'accuracy':[], 'val_accuracy':[]}

        Train the Tensorflow Model

            >>> epochs=100
            >>> batch_size=32
            >>> data  = tf.data.Dataset.from_tensor_slices((x_train, y_train))
            >>> shuffle_ds = data.shuffle(buffer_size=x_train.shape[0], reshuffle_each_iteration=True).batch(batch_size)
            >>> history = tf_model.fit( shuffle_ds, epochs=epochs, batch_size=batch_size, validation_data=(x_validate, y_validate), verbose=0)
            >>> for key in train_history:
            >>>     train_history[key].extend(history.history[key])
            >>> import sensiml.tensorflow.utils as sml_tf
            >>> sml_tf.plot_training_results(tf_model, train_history, x_train, y_train, x_validate, y_validate)

        Qunatize the Tensorflow Model

        *   The ```representative_dataset_generator()``` function is necessary to provide statistical information about your dataset in order to quantize the model weights appropriatley.
        *   The TFLiteConverter is used to convert a tensorflow model into a TensorFlow Lite model. The TensorFlow Lite model is stored as a `flatbuffer <https://google.github.io/flatbuffers/>`_ which allows us to easily store and access it on embedded systems.
        *   Quantizing the model allows TensorFlow Lite micro to take advantage of specialized instructions on cortex-M class processors using the `cmsis-nn <http://www.keil.com/pack/doc/cmsis/NN/html/index.html>`_ DSP library which gives another huge boost in performance.
        *   Quantizing the model can reduce size by up to 4x as 4 byte floats are converted to 1 byte ints in a number of places within the model.

            >>> import numpy as np
            >>> def representative_dataset_generator():
            >>>     for value in x_validate:
            >>>     # Each scalar value must be inside of a 2D array that is wrapped in a list
            >>>         yield [np.array(value, dtype=np.float32, ndmin=2)]
            >>>
            >>> converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)
            >>> converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]
            >>> converter.representative_dataset = representative_dataset_generator
            >>> tflite_model_quant = converter.convert()

        Uploading Trained TF Lite model to SensiML

            >>> class_map_tmp = {k:v+1 for k,v in class_map.items()} #increment by 1 as 0 corresponds to unknown
            >>> client.pipeline.set_training_algorithm("Load Model TensorFlow Lite for Microcontrollers",
            >>>                                     params={"model_parameters": {
            >>>                                             'tflite': sml_tf.convert_tf_lite(tflite_model_quant)},
            >>>                                             "class_map": class_map_tmp,
            >>>                                             "estimator_type": "classification",
            >>>                                             "threshold": 0.0,
            >>>                                             "train_history":train_history,
            >>>                                             "model_json": tf_model.to_json()
            >>>                                             })
            >>> client.pipeline.set_validation_method("Recall", params={})
            >>> client.pipeline.set_classifier("TensorFlow Lite for Microcontrollers", params={})
            >>> client.pipeline.set_tvo()
            >>> results, stats = client.pipeline.execute()
            >>>
            >>> results.summarize()

    """

    return None


load_model_tensorflow_micro_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "TensorFlow Lite for Microcontrollers"}],
        },
        VALIDATION_METHODS,
        {"name": "model_parameters", "type": "dict", "default": {"tflite": ""}},
        {
            "name": "estimator_type",
            "type": "str",
            "options": [{"name": "classification"}, {"name": "regression"}],
            "default": "classification",
        },
        {"name": "class_map", "type": "dict", "handle_by_set": False, "default": None},
        {"name": "threshold", "type": "float", "handle_by_set": False, "default": 0},
        {
            "name": "train_history",
            "type": "dict",
            "handle_by_set": False,
            "default": None,
        },
        {"name": "model_json", "type": "dict", "handle_by_set": False, "default": None},
        {
            "name": "input_type",
            "type": "str",
            "default": "int8",
            "options": [{"name": "int8"}],
            "description": "use int8 as input. Typically Accelerated OPS require int8.",
        },
    ],
    "output_contract": [],
}


DEFAULT_NN_TRAINING = [
    {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
    {"name": "label_column", "type": "str", "handle_by_set": True},
    {
        "name": "ignore_columns",
        "type": "list",
        "element_type": "str",
        "handle_by_set": True,
    },
    {
        "name": "classifiers",
        "type": "list",
        "element_type": "str",
        "handle_by_set": True,
        "options": [
            {"name": "TensorFlow Lite for Microcontrollers", "name": "Neural Network"}
        ],
    },
    {"name": "class_map", "type": "dict", "handle_by_set": True, "default": None},
    {
        "name": "epochs",
        "type": "int",
        "default": 5,
        "range": [1, 100],
    },
    {
        "name": "batch_size",
        "type": "int",
        "default": 32,
        "range": [8, 128],
    },
    {
        "name": "threshold",
        "type": "float",
        "default": 0.80,
        "range": [0.0, 1.0],
        "description": "Threshold value below which the classification will return Unknown.",
    },
    {
        "name": "early_stopping_threshold",
        "type": "float",
        "default": 0.80,
        "range": [0.5, 1.0],
        "description": "Early stopping threshold to stop training when the validation accuracy stops improving.",
    },
    {
        "name": "early_stopping_patience",
        "type": "int",
        "default": 2,
        "range": [0, 5],
        "description": "The number of epochs after the early stopping threshold was reached to continue training.",
    },
    {
        "name": "loss_function",
        "type": "str",
        "default": "categorical_crossentropy",
        "options": [
            {"name": "categorical_crossentropy"},
            {"name": "binary_crossentropy"},
            {"name": "poisson"},
            {"name": "kl_divergence"},
        ],
    },
    {
        "name": "learning_rate",
        "type": "float",
        "default": 0.01,
        "range": [0.0, 0.2],
        "description": "The learning rate to apply during training",
    },
    {
        "name": "tensorflow_optimizer",
        "type": "str",
        "default": "adam",
        "options": [{"name": "adam"}, {"name": "SGD"}],
    },
]


def QAT_contract(default=False):

    return [
        {
            "name": "quantization_aware_step",
            "type": "bool",
            "default": default,
            "description": "Apply Quantization Aware Training Step, a process that emulates quantization effects to preserve model performance during deployment on edge devices. This involves fine-tuning the model to mitigate potential performance loss when converting weights to lower bit representations during inference.",
        },
        {
            "name": "qaware_epochs",
            "type": "int",
            "default": 2,
            "range": [1, 32],
        },
        {
            "name": "qaware_batch_size",
            "type": "int",
            "default": 32,
            "range": [8, 128],
        },
        {
            "name": "qaware_learning_rate",
            "type": "float",
            "default": 0.001,
            "range": [0.0, 0.02],
            "description": "The learning rate to be applied during training within the quantization aware phase.",
        },
        {
            "name": "qaware_training_size_factor",
            "type": "float",
            "default": 0.7,
            "range": [0, 1],
            "description": "Fraction of the training sample size to be used in the quantization aware step.",
        },
        {
            "name": "metrics",
            "type": "str",
            "default": "accuracy",
            "options": [{"name": "accuracy"}],
            "description": "The metric reported during the training.",
        },
        {
            "name": "input_type",
            "type": "str",
            "default": "int8",
            "options": [{"name": "int8"}],
            "description": "use int8 as input. Typically Accelerated OPS require int8.",
        },
        {
            "name": "estimator_type",
            "type": "str",
            "default": "classification",
            "options": [{"name": "classification"}, {"name": "regression"}],
        },
    ]


def train_fully_connected_neural_network(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    estimator_type,
    class_map,
    threshold,
    dense_layers,
    batch_normalization,
    final_activation,
    iteration,
    learning_rate,
    batch_size,
    loss_function,
    tensorflow_optimizer,
    validation_methods,
):
    """
    Provides the ability to train a fully connected neural network model to use as the final classifier step in a pipeline.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        class_map (dict): optional, class map for converting labels to output
        estimator_type (str): defines if this estimator performs regression or classification, defaults to classification
        threshold (float):  if no values are greater than the threshold, classify as Unknown
        dense_layers (list): The size of each dense layer
        drop_out (float): The amount of dropout to use after each dense layer
        batch_normalization (bool): Use batch normalization
        final_activation (str): the final activation to use
        iteration (int): Maximum optimization attempt
        batch_size (int): The batch size to use during training
        metrics (str): the metric to use for reporting results
        learning_rate (float): The learning rate is a tuning parameter in an optimization algorithm that determines the step size at each iteration while moving toward a minimum of a loss function.
        batch_size (int): Refers to the number of training examples utilized in one iteration.
        loss_function (str): It is a function that determine how far the predicted values deviate from the actual values in the training data.
        tensorflow_optimizer (str): Optimization algorithms that is used to minimize loss function.


    Example:

        SensiML provides the ability to train NN architecture to use as the classifier for your pipeline.
        Tensorflow Lite Micro only supports a subset of the full tensorflow functions. For a full list of available functions
        see the `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.
        Use the Keras tensorflow API to create the NN graph.

        >>> client.project = 'Activity_Detection'
        >>> client.pipeline = 'tf_p1'

        >>> client.pipeline.stop_pipeline()

        >>> sensors = ['GyroscopeX', 'GyroscopeY', 'GyroscopeZ', 'AccelerometerX', 'AccelerometerY', 'AccelerometerZ']

        >>> client.pipeline.reset()

        >>> client.pipeline.set_input_query("Q1")

        >>> client.pipeline.add_transform("Windowing", params={"window_size":200,
                                        "delta":200,
                                        "train_delta":0})

        >>> client.pipeline.add_feature_generator([
                {'name':'MFCC', 'params':{"columns":sensors,"sample_rate":100, "cepstra_count":1}}
            ])

        >>> client.pipeline.add_transform("Min Max Scale")

        >>> client.pipeline.set_validation_method("Recall", params={})

        >>> client.pipeline.set_training_algorithm("Train Fully Connected Neural Network", params={
                                "estimator_type":"classification",
                                "class_map": None,
                                "threshold":0.0,
                                "dense_layers": [64,32,16,8],
                                "drop_out": 0.1,
                                "iterations": 5,
                                "learning_rate": 0.01,
                                "batch_size": 64,
                                "loss_function":"categorical_crossentropy",
                                "tensorflow_optimizer":"adam",
                                "batch_normalization": True,
                                "final_activation":"softmax,
            })

        >>> client.pipeline.set_classifier("TensorFlow Lite for Microcontrollers")

        >>> client.pipeline.set_tvo({'validation_seed':None})

        >>> results, stats = client.pipeline.execute()
        >>> results.summarize()

    """

    return None


train_fully_connected_neural_network_contracts = {
    "input_contract": [
        {
            "name": "dense_layers",
            "type": "list",
            "element_type": "int",
            "range": [1, 256],
            "default": [64, 32, 16, 8],
            "description": "The size of each dense layer",
        },
        {
            "name": "drop_out",
            "type": "float",
            "default": 0.1,
            "range": [0, 0.2],
            "description": "Apply dropout during training after each layer. The value here specifies how many neurons will be excluded at each layer.",
        },
        {
            "name": "batch_normalization",
            "type": "bool",
            "default": True,
            "description": "Apply batch normalization after each dense layer",
        },
        {
            "name": "final_activation",
            "type": "str",
            "default": "softmax",
            "options": [{"name": "softmax"}, {"name": "sigmoid"}],
            "description": "This is the activation of the final layer which is responsible for generating the classification.",
        },
        VALIDATION_METHODS,
    ]
    + DEFAULT_NN_TRAINING
    + QAT_contract(default=True),
    "output_contract": [],
}


###############################################


def train_temporal_convolutional_neural_network(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    estimator_type,
    class_map,
    threshold,
    dense_layers,
    batch_normalization,
    final_activation,
    iteration,
    learning_rate,
    batch_size,
    loss_function,
    tensorflow_optimizer,
    validation_methods,
    number_of_temporal_blocks,
    number_of_temporal_layers,
    number_of_convolutional_filters,
    kernel_size,
    residual_block,
    initial_dilation_rate,
    number_of_latest_temporal_features,
):
    """
    Implements a temporal convolutional neural network, consisting of several temporal blocks with various dilations.

    A Temporal Convolutional Neural Network (TCN) is designed for sequential data like time series or text. TCNs use "temporal blocks" with varying dilation rates to capture different time scales. Smaller rates focus on short-term patterns, while larger rates capture long-term dependencies. This diversity enables TCNs to model complex temporal relationships effectively, making them useful for tasks like speech recognition and forecasting.

    Note: To build a TCN model, pipeline should include a feature cascading block with cascade number larger than 1.

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels
        class_map (dict): optional, class map for converting labels to output
        estimator_type (str): defines if this estimator performs regression or classification, defaults to classification
        threshold (float):  if no values are greater than the threshold, classify as Unknown
        dense_layers (list): The size of each dense layer
        drop_out (float): The amount of dropout to use after each dense layer
        batch_normalization (bool): Use batch normalization
        final_activation (str): the final activation to use
        iteration (int): Maximum optimization attempt
        batch_size (int): The batch size to use during training
        metrics (str): the metric to use for reporting results
        learning_rate (float): The learning rate is a tuning parameter in an optimization algorithm that determines the step size at each iteration while moving toward a minimum of a loss function.
        batch_size (int): Refers to the number of training examples utilized in one iteration.
        loss_function (str): It is a function that determine how far the predicted values deviate from the actual values in the training data.
        tensorflow_optimizer (str): Optimization algorithms that is used to minimize loss function.
        number_of_temporal_blocks (int): Number of Temporal Blocks
        number_of_temporal_layers (int): Number of Temporal Layers within each block
        number_of_convolutional_filters (int): Number of Convolutional filters in each layer
        kernel_size (int): Size of the convolutional filters
        residual_block (boolean): Implementing residual blocks
        initial_dilation_rate (int): The dilation rate of the first temporal block, which is a power of two. The dilation rate of each subsequent block is twice as large as that of the preceding block
        number_of_latest_temporal_features (int): Number of the most relevant temporal components generated by the last temporal layer, i.e. how many of the most recent successive temporal features to be used with the fully connected component of the network to generate classifications. Set this to zero to use the entire temporal range of the output tensor

    """

    return None


train_temporal_convolutional_neural_network_contracts = {
    "input_contract": [
        {
            "name": "number_of_temporal_blocks",
            "type": "int",
            "default": 3,
            "description": "Number of Temporal Blocks.",
        },
        {
            "name": "number_of_temporal_layers",
            "type": "int",
            "default": 2,
            "description": "Number of Temporal Layers within each block.",
        },
        {
            "name": "number_of_convolutional_filters",
            "type": "int",
            "default": 8,
            "description": "Number of Convolutional filters in each layer.",
        },
        {
            "name": "kernel_size",
            "type": "int",
            "default": 3,
            "description": "Size of the convolutional filters.",
        },
        {
            "name": "residual_block",
            "type": "boolean",
            "default": True,
            "description": "Implementing residual blocks.",
        },
        {
            "name": "initial_dilation_rate",
            "type": "int",
            "default": 1,
            "description": "The dilation rate of the first temporal block, which is a power of two. The dilation rate of each subsequent block is twice as large as that of the preceding block.",
        },
        {
            "name": "number_of_latest_temporal_features",
            "type": "int",
            "default": 0,
            "description": "Number of the most relevant temporal components generated by the last temporal layer, i.e. how many of the most recent successive temporal features to be used with the fully connected component of the network to generate classifications. Set this to zero to use the entire temporal range of the output tensor.",
        },
        {
            "name": "dense_layers",
            "type": "list",
            "element_type": "int",
            "range": [1, 256],
            "default": [32, 16, 8],
            "description": "The size of dense layers.",
        },
        {
            "name": "drop_out",
            "type": "float",
            "default": 0.1,
            "range": [0, 0.2],
            "description": "Apply dropout during training after each layer. The value here specifies how many neurons will be excluded at each layer.",
        },
        {
            "name": "batch_normalization",
            "type": "bool",
            "default": True,
            "description": "Apply batch normalization after each dense layer",
        },
        {
            "name": "final_activation",
            "type": "str",
            "default": "softmax",
            "options": [{"name": "softmax"}, {"name": "sigmoid"}],
            "description": "This is the activation of the final layer which is responsible for generating the classification.",
        },
        {
            "name": "random_sparse_noise",
            "type": "bool",
            "default": False,
            "description": "Augmentation using additional bias on pixels chosen randomly.",
        },
        {
            "name": "random_bias_noise",
            "type": "bool",
            "default": False,
            "description": "Augmentation using additional random bias along row and/or columns.",
        },
        {
            "name": "random_frequency_mask",
            "type": "bool",
            "default": False,
            "description": "Augmentation by randomly masking features in rows. In the case of audio data, each row might represent a specific frequency.",
        },
        {
            "name": "random_time_mask",
            "type": "bool",
            "default": False,
            "description": "Augmentation by masking features at random time columns.",
        },
        VALIDATION_METHODS,
    ]
    + DEFAULT_NN_TRAINING
    + QAT_contract(default=False),
    "output_contract": [],
}
#######################################################


def train_iterate_neural_network(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    estimator_type,
    class_map,
    threshold,
    iteration,
    learning_rate,
    batch_size,
    loss_function,
    tensorflow_optimizer,
    validation_methods,
):
    """Provides the ability to continue training a TensorFlow model for further epochs."""

    return None


train_iterate_neural_network_contracts = {
    "input_contract": [
        {
            "name": "base_model",
            "type": "str",
        },
        VALIDATION_METHODS,
    ]
    + DEFAULT_NN_TRAINING
    + QAT_contract(default=False),
    "output_contract": [],
}


def train_transfer_learning_neural_network(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    estimator_type,
    class_map,
    threshold,
    iteration,
    learning_rate,
    batch_size,
    loss_function,
    tensorflow_optimizer,
    validation_methods,
    base_model,
    batch_normalization,
    dense_layers,
    early_stopping,
    drop_out,
    random_sparse_noise,
    random_bias_noise,
    random_frequency_mask,
    random_time_mask,
    auxiliary_augmentation,
    training_size_limit,
    validation_size_limit,
):
    """Apply transfer learning to a pre-trained TensorFlow model."""

    return None


train_transfer_learning_neural_network_contracts = {
    "input_contract": [
        {"name": "base_model", "type": "str", "element_type": "UUID"},
        {
            "name": "final_activation",
            "type": "str",
            "default": "softmax",
            "options": [{"name": "softmax"}, {"name": "sigmoid"}],
        },
        {
            "name": "dense_layers",
            "type": "list",
            "element_type": "int",
            "range": [1, 256],
            "default": [],
            "description": "The size of each dense layer. If dense layer is empty, the base models head will be used instead.",
        },
        {
            "name": "number_of_trainable_base_layer_blocks",
            "type": "int",
            "default": 9999,
            "description": "The number of last trainable groups of layers in the tail of the foundation model. Set to 0 to freeze all parameters of the base model during the training process. Although using non-zero values can help improve the network performance, be cautious as the trainability of many base layers might cause over-fitting. Using values larger than the number of base blocks results in all base layers becoming trainable.",
        },
        {
            "name": "training_size_limit",
            "type": "int",
            "default": 0,
            "range": [0, 50000],
            "description": "Maximum number of training samples per labels. At each training epoch, data is randomly resampled to have even distribution across all labels.",
        },
        {
            "name": "validation_size_limit",
            "type": "int",
            "default": 500,
            "range": [0, 50000],
            "description": "Maximum number of validation samples per labels. The validation sample is suggested to be at least as large as 20% of the training sample. At eah epoch, validation set is used to evaluate the early stopping condition.",
        },
        {
            "name": "batch_normalization",
            "type": "bool",
            "default": True,
            "description": "Apply batch normalization after each dense layer",
        },
        {
            "name": "drop_out",
            "type": "float",
            "default": 0.1,
            "range": [0, 0.2],
            "description": "Apply drop out after each dense layer",
        },
        {
            "name": "random_sparse_noise",
            "type": "bool",
            "default": False,
            "description": "Augmentation using additional bias on pixels chosen randomly.",
        },
        {
            "name": "random_bias_noise",
            "type": "bool",
            "default": False,
            "description": "Augmentation using additional random bias along row and/or columns.",
        },
        {
            "name": "random_frequency_mask",
            "type": "bool",
            "default": False,
            "description": "Augmentation by randomly masking features in rows. In the case of audio data, typically, each row represents a specific frequency.",
        },
        {
            "name": "random_time_mask",
            "type": "bool",
            "default": False,
            "description": "Augmentation by masking features at random time columns.",
        },
        {
            "name": "auxiliary_augmentation",
            "type": "bool",
            "default": False,
            "description": "Augmentation using auxiliary data.",
        },
        VALIDATION_METHODS,
    ]
    + DEFAULT_NN_TRAINING
    + QAT_contract(default=True),
    "output_contract": [],
}


def linear_regression():
    """
    Linear regression is a linear approach for modelling the relationship between a scalar response and one or more
    explanatory variables (also known as dependent and independent variables).
    """

    return None


linear_regression_contracts = {"input_contract": [], "output_contract": []}


def train_linear_regression_ols(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    validation_methods,
    fit_intercept: bool = True,
    positive: bool = True,
):
    """
    Ordinary least squares Linear Regression.

    Fits a linear model with coefficients w = (w1, …, wp)
    to minimize the residual sum of squares between the observed targets in the dataset,
    and the targets predicted by the linear approximation.

    Args:
        fit_intercept (bool): Whether to calculate the intercept for this model. If set to False,
         no intercept will be used in calculations (i.e. data is expected to be centered). default=True
        positive (bool): When set to True, forces the coefficients to be positive.
         This option is only supported for dense arrays. default=False

    Returns:
        Trained linear regression model

    """

    return None


train_linear_regression_ols_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "Linear Regression"}],
        },
        VALIDATION_METHODS,
        {
            "name": "fit_intercept",
            "type": "bool",
            "handle_by_set": False,
            "default": True,
        },
        {"name": "positive", "type": "bool", "handle_by_set": False, "default": False},
    ],
    "output_contract": [],
}


def train_linear_regression_l1_lasso(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    validation_methods,
    fit_intercept: bool = True,
    positive: bool = True,
    alpha: float = 0,
    tol: float = 1e-4,
    max_iter: int = 1000,
    random_state: Optional[int] = None,
):
    """
    Linear Model trained with L1 prior as regularizer (aka the Lasso).

    The optimization objective for Lasso is::

        (1 / (2 * n_samples)) * ||y - Xw||^2_2 + alpha * ||w||_1

    Technically the Lasso model is optimizing the same objective function as
    the Elastic Net with ``l1_ratio=1.0`` (no L2 penalty).

    See: Scikit Learn linear_model.Lasso training algorithm https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html
        for more information


    Parameters
    ----------
    alpha : float, default=1.0
        Constant that multiplies the L1 term, controlling regularization
        strength. `alpha` must be a non-negative float i.e. in `[0, inf)`.

        When `alpha = 0`, the objective is equivalent to ordinary least
        squares, solved by the :class:`LinearRegression` object. For numerical
        reasons, using `alpha = 0` with the `Lasso` object is not advised.
        Instead, you should use the :class:`LinearRegression` object.

    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model. If set
        to False, no intercept will be used in calculations
        (i.e. data is expected to be centered).

    max_iter : int, default=1000
        The maximum number of iterations.

    tol : float, default=1e-4
        The tolerance for the optimization: if the updates are
        smaller than ``tol``, the optimization code checks the
        dual gap for optimality and continues until it is smaller
        than ``tol``

    positive : bool, default=False
        When set to ``True``, forces the coefficients to be positive.

    random_state : int, RandomState instance, default=None
        The seed of the pseudo random number generator that selects a random
        feature to update. Used when ``selection`` == 'random'.
        Pass an int for reproducible output across multiple function calls.

    Returns:
        Trained linear regression model

    """


train_linear_regression_l1_lasso_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "Linear Regression"}],
        },
        VALIDATION_METHODS,
        {
            "name": "alpha",
            "type": "float",
            "handle_by_set": False,
            "default": 1.0,
            "range": [0, 1e10],
        },
        {
            "name": "fit_intercept",
            "type": "bool",
            "handle_by_set": False,
            "default": True,
        },
        {
            "name": "max_iter",
            "type": "int",
            "handle_by_set": False,
            "default": 100,
            "range": [1, 1e4],
        },
        {
            "name": "tol",
            "type": "float",
            "handle_by_set": False,
            "default": 1e-4,
            "range": [0, 1e3],
        },
        {"name": "positive", "type": "bool", "handle_by_set": False, "default": False},
        {
            "name": "random_state",
            "type": "int",
            "handle_by_set": False,
            "default": None,
        },
    ],
    "output_contract": [],
}


def train_linear_regression_l2_ridge(
    input_data,
    label_column,
    ignore_columns,
    classifiers,
    validation_methods,
    fit_intercept: bool = True,
    positive: bool = True,
    alpha: float = 0,
    tol: float = 1e-4,
    solver: str = "auto",
    max_iter: Optional[int] = None,
    random_state: Optional[int] = None,
):
    """Linear least squares with l2 regularization.

    Minimizes the objective function::

    ||y - Xw||^2_2 + alpha * ||w||^2_2

    This model solves a regression model where the loss function is
    the linear least squares function and regularization is given by
    the l2-norm. Also known as Ridge Regression or Tikhonov regularization.
    This estimator has built-in support for multi-variate regression
    (i.e., when y is a 2d-array of shape (n_samples, n_targets)).

    Read more at Scikit Learn linear_model.Ridge https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html

    Parameters
    ----------
    alpha :float, default=1.0
        Constant that multiplies the L2 term, controlling regularization
        strength. `alpha` must be a non-negative float i.e. in `[0, inf)`.

        When `alpha = 0`, the objective is equivalent to ordinary least
        squares, solved by the :class:`LinearRegression` object. For numerical
        reasons, using `alpha = 0` with the `Ridge` object is not advised.
        Instead, you should use the :class:`LinearRegression` object.
        
    fit_intercept : bool, default=True
        Whether to fit the intercept for this model. If set
        to false, no intercept will be used in calculations
        (i.e. ``X`` and ``y`` are expected to be centered).

    max_iter : int, default=None
        Maximum number of iterations for conjugate gradient solver.
        For 'sparse_cg' and 'lsqr' solvers, the default value is determined
        by scipy.sparse.linalg. For 'sag' solver, the default value is 1000.
        For 'lbfgs' solver, the default value is 15000.

    tol : float, default=1e-4
        The precision of the solution (`coef_`) is determined by `tol` which
        specifies a different convergence criterion for each solver:

        - 'svd': `tol` has no impact.

        - 'cholesky': `tol` has no impact.

        - 'sparse_cg': norm of residuals smaller than `tol`.

        - 'lsqr': `tol` is set as atol and btol of scipy.sparse.linalg.lsqr,
          which control the norm of the residual vector in terms of the norms of
          matrix and coefficients.

        - 'sag' and 'saga': relative change of coef smaller than `tol`.

        - 'lbfgs': maximum of the absolute (projected) gradient=max|residuals|
          smaller than `tol`.

    solver : {'auto', 'svd', 'cholesky', 'lsqr', 'sparse_cg', \
            'sag', 'saga', 'lbfgs'}, default='auto'
        Solver to use in the computational routines:

        - 'auto' chooses the solver automatically based on the type of data.

        - 'svd' uses a Singular Value Decomposition of X to compute the Ridge
          coefficients. It is the most stable solver, in particular more stable
          for singular matrices than 'cholesky' at the cost of being slower.

        - 'cholesky' uses the standard scipy.linalg.solve function to
          obtain a closed-form solution.

        - 'sparse_cg' uses the conjugate gradient solver as found in
          scipy.sparse.linalg.cg. As an iterative algorithm, this solver is
          more appropriate than 'cholesky' for large-scale data
          (possibility to set `tol` and `max_iter`).

        - 'lsqr' uses the dedicated regularized least-squares routine
          scipy.sparse.linalg.lsqr. It is the fastest and uses an iterative
          procedure.

        - 'sag' uses a Stochastic Average Gradient descent, and 'saga' uses
          its improved, unbiased version named SAGA. Both methods also use an
          iterative procedure, and are often faster than other solvers when
          both n_samples and n_features are large. Note that 'sag' and
          'saga' fast convergence is only guaranteed on features with
          approximately the same scale. You can preprocess the data with a
          scaler from sklearn.preprocessing.

        - 'lbfgs' uses L-BFGS-B algorithm implemented in
          `scipy.optimize.minimize`. It can be used only when `positive`
          is True.

        All solvers except 'svd' support both dense and sparse data. However, only
        'lsqr', 'sag', 'sparse_cg', and 'lbfgs' support sparse input when
        `fit_intercept` is True.

        .. versionadded:: 0.17
           Stochastic Average Gradient descent solver.
        .. versionadded:: 0.19
           SAGA solver.

    positive : bool, default=False
        When set to ``True``, forces the coefficients to be positive.
        Only 'lbfgs' solver is supported in this case.

    random_state : int, RandomState instance, default=None
        Used when ``solver`` == 'sag' or 'saga' to shuffle the data.
    """


train_linear_regression_l2_ridge_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "Linear Regression"}],
        },
        VALIDATION_METHODS,
        {
            "name": "alpha",
            "type": "float",
            "handle_by_set": False,
            "default": 1.0,
            "range": [0, 1e10],
        },
        {
            "name": "fit_intercept",
            "type": "bool",
            "handle_by_set": False,
            "default": True,
        },
        {
            "name": "max_iter",
            "type": "int",
            "handle_by_set": False,
            "default": None,
            "range": [1, 1e6],
        },
        {
            "name": "tol",
            "type": "float",
            "handle_by_set": False,
            "default": 1e-4,
            "range": [0, 1e3],
        },
        {
            "name": "solver",
            "type": "str",
            "default": "auto",
            "options": [
                {"name": "auto"},
                {"name": "svd"},
                {"name": "cholesky"},
                {"name": "sparse_cg"},
                {"name": "lsqr"},
                {"name": "sag"},
                {"name": "lbfgs"},
            ],
        },
        {"name": "positive", "type": "bool", "handle_by_set": False, "default": False},
        {
            "name": "random_state",
            "type": "int",
            "handle_by_set": False,
            "default": None,
        },
    ],
    "output_contract": [],
}
