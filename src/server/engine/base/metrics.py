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

import inspect
import json
import warnings

import numpy as np
from numpy import NaN
from sklearn import metrics as met

UNC = "UNC"
UNK = "UNK"
AVG = "average"
UNK_UNC = [UNK, UNC]


def accuracy(y_true, y_pred, **kwargs):
    """calculates the accuracy given y_true and y_pred arrays. Uses locally defined calculations for binary class
    problems and scikit-learn.metrics.accuracy_score for multi-class problems

        Args:
            y_true (list): ground truth classification of each vector recognized
            y_pred (list): classification as predicted by a classifier

        Kwargs:
            Accepts any kwargs that scikit-learn.metrics.accuracy_score would accept, only applies those kwargs to
            multi-class problems

        Raises:
            RunTimeError: if y_true and y_pred are the wrong type or not of equal length

        Returns:
            accuracy (float): accuracy score given y_true and y_pred values

        Examples:
            >>> accuracy([1, 1, 1, 2, 2, 2], [1, 2, 1, 2, 1, 1])
            50.0
            >>> accuracy([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3])
            66.666666666666657
            >>> accuracy([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3], normalize=False)
            600"""

    if verify_truth_pred(y_true, y_pred):
        y_true, y_pred = scrub_unknowns(y_true, y_pred, unk_vals=UNK_UNC)
        if is_binary(y_true):  # if this is a binary problem
            temp_total = 0.0
            for i, item in enumerate(y_true):
                if (
                    y_true[i] == y_pred[i]
                ):  # for every correct classification, increment by 1
                    temp_total += 1

            # return 100 * correct classifications / number of elements in y_true
            return 100 * float(temp_total / len(y_true)) if len(y_true) > 0 else NaN

        else:  # if this is a multi-class problem
            temp = {"y_true": y_true, "y_pred": y_pred}
            temp.update(kwargs)
            z = {}
            z.update(kwargs)
            # check if scikit-learn/metrics.accuracy_score is callable given the kwargs supplied by user
            if is_callable_with_args(met.accuracy_score, temp) and z is not None:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    # calculate accuracy score with user defined kwargs
                    return 100 * met.accuracy_score(y_true, y_pred, **z)
            else:
                # If kwargs passed in by the user are not recognized by scikit-learn.metrics.accuracy_score,
                # warn the user and ignore user supplied values
                warnings.warn(
                    "metrics::accuracy() - kwargs were not recognized. They have been ignored."
                )
                return 100 * met.accuracy_score(y_true, y_pred)


def positive_predictive_rate(y_true, y_pred):
    """calculates the positive predictive rate given y_true and y_pred arrays. Calculations are done for each class.
    positive_predictive_rate = True Positive (TP) /(True Positive (TP) + False Positive (FP)), for each class

    Args:
        y_true (list): ground truth classification of each vector recognized
        y_pred (list): classification as predicted by a classifier

    Raises:
        RunTimeError: if y_true and y_pred are the wrong type or not of equal length

    Returns:
        positive_predictive_rate (dict): pp score given y_true and y_pred values for each class as well as average

    Examples:
        >>> positive_predictive_rate([1, 1, 1, 2, 2, 2], [1, 2, 1, 2, 1, 1])
        {1: 50, 2: 50, 'average': 50}
        >>> positive_predictive_rate([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3])
        {1: 50.0, 2: 50.0, 3: 100.0, 'average': 66.666666666666657}
        >>> positive_predictive_rate([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3], average=None)
        {1: 50.0, 2: 50.0, 3: 100.0, 'average': array([  50.,   50.,  100.])}
        >>> positive_predictive_rate([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
                                     [1, 1, 1, 1, 1, 2, 2, "UNK", "UNK", "UNK", 1, 2, 2, "UNK", "UNK"])
        {1: 83.333333333333343, 2: 50.0, 'average': 66.666666666666671}
        >>> positive_predictive_rate([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3],
                                     [1, 1, 1, 1, 1, 2, 2, 3, "UNK", "UNK", 2, 2, 2, 3, "UNK", 3, 3, 3, "UNK", "UNK"])
        {1: 100.0, 2: 60.0, 3: 60.0, 'average': 73.333333333333343}
    """

    return precision(y_true, y_pred)


def sensitivity(y_true, y_pred, **kwargs):
    """calculates the sensitivity given y_true and y_pred arrays.
    calculations are done for each class and for the entire y_true/y_pred

        Args:
            y_true (list): ground truth classification of each vector recognized
            y_pred (list): classification as predicted by a classifier

        Kwargs:
            Accepts any kwargs that scikit-learn.metrics.recall_score accepts
            Defaults:
                average: weighted
                pos_label: 1
                labels: set(y_true) + set(y_pred)

        Raises:
            RunTimeError: if y_true and y_pred are the wrong type or not of equal length

        Returns:
            sensitivity (dict): sensitivity score given y_true and y_pred values for each class as well as average

        Examples:
            >>> sensitivity([1, 1, 1, 2, 2, 2], [1, 2, 1, 2, 1, 1])
            {1: 66.66666666666666, 2: 33.33333333333333, 'average': 49.999999999999993}
            >>> sensitivity([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3])
            {1: 66.666666666666657, 2: 33.333333333333329, 3: 100.0, 'average': 66.666666666666657}
            >>> sensitivity([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3], average=None)
            {1: 66.666666666666657, 2: 33.333333333333329, 3: 100.0, 'average': array([  66.66666667, 33.33333333, 100. ])}

            >>> sensitivity([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
                                         [1, 1, 1, 1, 1, 2, 2, "UNK", "UNK", "UNK", 1, 2, 2, "UNK", "UNK"])
            {1: 50.0, 2: 40.0, 'average': 45.0}
            >>> sensitivity([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3],
                                         [1, 1, 1, 1, 1, 2, 2, 3, "UNK", "UNK", 2, 2, 2, 3, "UNK", 3, 3, 3, "UNK", "UNK"])
            {1: 50.0, 2: 60.0, 3: 60.0, 'average': 56.666666666666679}

    """

    return base_function(y_true, y_pred, met.recall_score, **kwargs)


def specificity(y_true, y_pred):
    """calculates the specificity given y_true and y_pred arrays
    specificity = (tn / (tn + fp))

    Args:
        y_true (list): ground truth classification of each vector recognized
        y_pred (list): classification as predicted by a classifier

    Kwargs:
        pos_label : label in the y_true array of the positive case

    Raises:
        RunTimeError: if y_true and y_pred are the wrong type or not of equal length
        RunTimeError: if pos_label cannot be found in y_true array

    Returns:
        specificity (float): specificity value given the y_true and y_pred arrays

    Examples:
        >>> specificity([1, 1, 1, 1, 2, 2, 2, 2], [1, 2, 2, 1, 2, 2, 2, 2])
        75.0
        >>> specificity([1, 1, 1, 1, 2, 2, 2, 2], [1, 1, 1, 1, 2, 1, 1, 2])
        75.0
        >>> specificity([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
                                     [1, 1, 1, 1, 1, 2, 2, "UNK", "UNK", "UNK", 1, 2, 2, "UNK", "UNK"])
        69.047619047619037
        >>> specificity([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3],
                                     [1, 1, 1, 1, 1, 2, 2, 3, "UNK", "UNK", 2, 2, 2, 3, "UNK", 3, 3, 3, "UNK", "UNK"])
        86.666666666666671
    """

    if verify_truth_pred(y_true, y_pred):
        y_true, y_pred, indicies_list = get_indicies_list(y_true, y_pred)

        confusion_matrix_array = met.confusion_matrix(y_true, y_pred)
        total = []
        total_tp = []

        for i in range(len(confusion_matrix_array)):
            tp = confusion_matrix_array[i][i]
            total_tp.append(tp)

        total_tp = sum(total_tp)

        for i in range(len(confusion_matrix_array)):
            tp = confusion_matrix_array[i][i]
            fp = sum(confusion_matrix_array[:, i]) - tp
            tn = total_tp - tp
            specificity_score = (
                100 * np.true_divide(tn, (tn + fp)) if ((tn + fp) > 0) else NaN
            )
            total.append(specificity_score)

        if 0 in y_pred:
            # ignore UNK
            return np.mean([total[i] for i in indicies_list])
        else:
            return np.mean(total)


def precision(y_true, y_pred, **kwargs):
    """
    calculates the precision given y_true and y_pred arrays.
    calculations are done for each class and for the entire y_true/y_pred
    precision = (tp / (tp + fp))

    Args:
        y_true (list): ground truth classification of each vector recognized
        y_pred (list): classification as predicted by a classifier

    Kwargs:
        Accepts any kwargs that scikit-learn.metrics.recall_score accepts
        Defaults:
            average: weighted
            pos_label: 1
            labels: set(y_true) + set(y_pred)

    Raises:
        RunTimeError: if y_true and y_pred are the wrong type or not of equal length

    Returns:
        precision (dict): precision score given y_true and y_pred values for each class as well as average

    Examples:
        >>> precision([1, 1, 1, 2, 2, 2], [1, 2, 1, 2, 1, 1])
        {1: 50, 2: 50, 'average': 50}
        >>> precision([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3])
        {1: 50.0, 2: 50.0, 3: 100.0, 'average': 66.666666666666657}
        >>> precision([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3], average=None)
        {1: 50.0, 2: 50.0, 3: 100.0, 'average': array([  50.,   50.,  100.])}
        >>> precision([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
                                     [1, 1, 1, 1, 1, 2, 2, "UNK", "UNK", "UNK", 1, 2, 2, "UNK", "UNK"])
        {1: 83.333333333333343, 2: 50.0, 'average': 66.666666666666671}
        >>> precision([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3],
                                     [1, 1, 1, 1, 1, 2, 2, 3, "UNK", "UNK", 2, 2, 2, 3, "UNK", 3, 3, 3, "UNK", "UNK"])
        {1: 100.0, 2: 60.0, 3: 60.0, 'average': 73.333333333333343}

    """

    return base_function(y_true, y_pred, met.precision_score, **kwargs)


def f1_score(y_true, y_pred, **kwargs):
    """calculates the f1_score given y_true and y_pred arrays.
    calculations are done for each class and for the entire y_true/y_pred
    2 * ((precision * sensitivity) / (precision + sensitivity))

    Args:
        y_true (list): ground truth classification of each vector recognized
        y_pred (list): classification as predicted by a classifier

    Kwargs:
        Accepts any kwargs that scikit-learn.metrics.recall_score accepts
        Defaults:
            average: weighted
            pos_label: 1
            labels: set(y_true) + set(y_pred)

    Raises:
        RunTimeError: if y_true and y_pred are the wrong type or not of equal length

    Returns:
        f1_score (dict): f1_score score given y_true and y_pred values for each class as well as average

    Examples:
        >>> f1_score([1, 1, 1, 2, 2, 2], [1, 2, 1, 2, 1, 1])
        {1: 57.142857142857153, 2: 40.0, 'average': 48.571428571428577}
        >>> f1_score([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3])
        {1: 57.142857142857153, 2: 40.0, 3: 100.0, 'average': 65.714285714285708}
        >>> f1_score([1, 1, 1, 2, 2, 2, 3, 3, 3], [1, 2, 1, 2, 1, 1, 3, 3, 3], average=None)
        {1: 57.142857142857153, 2: 40.0, 3: 100.0, 'average': array([  57.14285714,   40.        ,  100.        ])}
        >>> f1_score([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
                                     [1, 1, 1, 1, 1, 2, 2, "UNK", "UNK", "UNK", 1, 2, 2, "UNK", "UNK"])
        {1: 62.5, 2: 44.44444444444445, 'average': 53.472222222222229}
        >>> f1_score([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3],
                                     [1, 1, 1, 1, 1, 2, 2, 3, "UNK", "UNK", 2, 2, 2, 3, "UNK", 3, 3, 3, "UNK", "UNK"])
        {1: 66.666666666666657, 2: 60.0, 3: 60.0, 'average': 62.222222222222221}

    """

    return base_function(y_true, y_pred, met.f1_score, **kwargs)


def base_function(y_true, y_pred, metric_function, **kwargs):
    if verify_truth_pred(y_true, y_pred):
        y_true, y_pred, indicies_list = get_indicies_list(y_true, y_pred)

        ret = {}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            scores = 100 * metric_function(
                y_true, y_pred, average=None, labels=indicies_list
            )

        # Compute the scores for individual
        for i, v in enumerate(scores):
            ret[i + 1] = v

        if is_binary(y_true):
            # Since sklearn apply null hypothesis 2 class problem (it returns score only for the first class),
            # average score is computed separately by ignoring the label balance.
            ret[AVG] = np.mean(scores)

        else:

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                default_kwargs = {
                    "pos_label": 1,
                    "labels": indicies_list,
                    "average": "macro",
                    "sample_weight": None,
                }
                upd_kwargs = build_kwargs(default_kwargs, kwargs)
                temp = {"y_true": y_true, "y_pred": y_pred}
                temp.update(upd_kwargs)
                if (
                    is_callable_with_args(metric_function, temp)
                    and upd_kwargs is not None
                ):
                    ret[AVG] = 100 * metric_function(y_true, y_pred, **upd_kwargs)
                else:
                    ret[AVG] = 100 * metric_function(y_true, y_pred, **default_kwargs)
        return ret


def get_indicies_list(y_true, y_pred):
    ####### Don't change the order of following two lines #########
    # If there is a 'UNK', convert it to 0
    y_true, y_pred = scrub_unknowns(y_true, y_pred, unk_vals=UNK_UNC)
    # remove 0 that refers 'UNK' from the indices_list if it exist
    indicies_list = list(set(y_pred).union(set(y_true)) - set([0]))
    ##############################################################
    return y_true, y_pred, indicies_list


def get_metrics_set(data):
    """Builds a metrics result set identical to the metric results reported by knowledgebuilderengine
    Default Keys of return value : f1_score, precision, sensitivity, specificity, accuracy,
        positive_predictive_rate, ConfusionMatrix, y_true, y_pred

        Args:
            data (dict): contains
            y_true, (list)
            Y-pred, (list)

        Returns:
            result_set (dict): default keys listed above"""

    y_true = None
    y_pred = None

    if not isinstance(data, dict):
        data = json.loads(data)

    if "y_true" in data.keys():
        if isinstance(data["y_true"], list):
            y_true = data["y_true"]

    if "y_pred" in data.keys():
        if isinstance(data["y_pred"], list):
            y_pred = data["y_pred"]

    if y_true is not None and y_pred is not None:
        y_true, y_pred = scrub_unknowns(y_true, y_pred, unk_vals=UNK_UNC)

        defaults = {
            "f1_score": f1_score,
            "precision": precision,
            "sensitivity": sensitivity,
            "accuracy": accuracy,
            "positive_predictive_rate": positive_predictive_rate,
        }
        # "specificity": specificity this is not implemented in a way to provide useful information
        # also it is crashing for cases where there is a missing class for example 2 here
        #  [1, 1, 1, 3, 3, 4, 4, 4, 4]
        #  [1, 1, 1, 0, 3, 4, 4, 4, 4]

        ret = dict.fromkeys(defaults.keys(), None)

        ret["y_true"] = y_true
        ret["y_pred"] = y_pred

        for key in defaults.keys():
            ret[key] = defaults[key](y_true, y_pred)
    else:
        ret = None

    return ret


def get_tp_fp_tn_fn(y_true, y_pred, pos_label=1, neg_label=0):
    if pos_label not in y_true or len(set(y_true)) > 2:
        return NaN, NaN, NaN, NaN

    tp = float(
        len(
            [
                x
                for i, x in enumerate(y_true)
                if x == pos_label and y_pred[i] == pos_label
            ]
        )
    )
    tn = float(
        len(
            [
                x
                for i, x in enumerate(y_true)
                if x == neg_label and y_pred[i] == neg_label
            ]
        )
    )
    fp = float(
        len(
            [
                x
                for i, x in enumerate(y_true)
                if x == pos_label and y_pred[i] == neg_label
            ]
        )
    )
    fn = float(
        len(
            [
                x
                for i, x in enumerate(y_true)
                if x == neg_label and y_pred[i] == pos_label
            ]
        )
    )
    return tp, fp, tn, fn


def find_labels(y_true, y_pred):
    labels_found = set(y_true)
    labels_found.update(set(y_pred))
    labels_found = list(labels_found)
    return labels_found


def build_kwargs(default_kwargs, user_input_kwargs):
    upd_kwargs = default_kwargs.copy()
    upd_kwargs.update(user_input_kwargs)
    return upd_kwargs


def verify_truth_pred(y_true, y_pred):
    if not isinstance(y_true, list) or not isinstance(y_pred, list):
        raise RuntimeError(
            (
                "y_true and y_pred must be lists.\ngot y_true: %s\ny_pred: %s"
                % (str(type(y_true)), str(type(y_pred)))
            )
        )
    if not len(y_true) == len(y_pred):
        raise RuntimeError("y_true and y_pred lists must be the same length")
    return True


def scrub_unknowns(y_true, y_pred, unk_vals=None):

    if not isinstance(unk_vals, list):
        return y_true, y_pred

    y_true_ret = []
    y_pred_ret = []
    for i, item in enumerate(y_true):
        if item in unk_vals:
            y_true_ret.append(0)
        else:
            y_true_ret.append(item)
    for i, item in enumerate(y_pred):
        if item in unk_vals:
            y_pred_ret.append(0)
        else:
            y_pred_ret.append(item)
    return y_true_ret, y_pred_ret


def is_binary(y_true):
    return len(set(y_true)) == 2


def split_truth_pred_by_class(y_true, y_pred):
    classes_present = list(set(y_true))
    y_true_by_class = dict.fromkeys(classes_present, None)
    y_pred_by_class = dict.fromkeys(classes_present, None)
    for c in classes_present:
        indices = [i for i, x in enumerate(y_true) if x == c]
        y_true_by_class[c] = [y_true[i] for i in indices]
        y_pred_by_class[c] = [y_pred[i] for i in indices]
    return y_true_by_class, y_pred_by_class


def is_callable_with_args(func, arg_dict):
    return not missing_args(func, arg_dict) and not invalid_args(func, arg_dict)


def invalid_args(func, arg_dict):
    (
        args,
        varargs,
        varkw,
        defaults,
        kwonlyargs,
        kwonlydefaults,
        annotations,
    ) = inspect.getfullargspec(func)
    if varkw:
        return set()
    return set(arg_dict) - set(args)


def missing_args(func, arg_dict):
    return set(get_required_args(func)).difference(arg_dict)


def get_required_args(func):

    (
        args,
        varargs,
        varkw,
        defaults,
        kwonlyargs,
        kwonlydefaults,
        annotations,
    ) = inspect.getfullargspec(func)
    if defaults:
        args = args[: -len(defaults)]
    return args
