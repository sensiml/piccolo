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

from engine.base import metrics as server_metrics

UNC = "UNC"
UNK = "UNK"
AVG = "average"
UNK_UNC = [UNK, UNC]


class StatsCalcException(Exception):
    """Base exception for StatsCalc object"""

    def __init__(self, e):
        self.e = e

    def __str__(self):
        return repr(self.e)


class StatsCalc(object):
    """StatsCalc object is a calculator/container for statistics that can be gleaned from a given confusion matrix.
    The functions provided can be called one at a time if you desire an individual statistic, or you can calculate them
    all at which point they will be stored as a property of the object for later use.
    """

    def __init__(
        self, y_true, y_pred, confusion_matrix=None, unknown=True, class_map=None
    ):
        """Initializes StatsCalc object

        Args:
            y_true (list): ground truth classification of each vector recognized
            y_pred (list): classifications as predicted by the model of y_true vectors
            confusion_matrix (dict): dictionary representation of confusion matrix, defaults to None
            unknown (bool): add 0 as a class to the class_titles even if it isn't in y_true

        Raises:
            StatsCalcException: If args are not the correct type

        """
        try:
            self._verify_args(y_true, y_pred)
        except StatsCalcException as e:
            raise StatsCalcException(str(e))
        self._confusion_matrix = confusion_matrix
        self._y_true = y_true
        self._y_pred = y_pred

        # treating the unknown labels the sae way as UNC and UNK
        if class_map:
            for l, c in class_map.items():
                if isinstance(l, str) and l.lower() == "unknown":
                    self._y_true = []
                    self._y_pred = []

                    for i, item in enumerate(y_true):
                        if item == c:
                            self._y_true.append(0)
                        else:
                            self._y_true.append(item)
                    for i, item in enumerate(y_pred):
                        if item == c:
                            self._y_pred.append(0)
                        else:
                            self._y_pred.append(item)
                    break

        if self._confusion_matrix is not None:
            self._class_titles = self._inspect_confusion_matrix()
        else:
            self._class_titles = list(set(self._y_true))
        # allows for binary classification in the event of unknown being the other class
        if unknown and 0 not in self._class_titles:
            self._class_titles.append(0)
        self._is_binary = len(self._class_titles) == 2
        # assuming positive class is index 0
        self._pos_class_name = self._class_titles[0]
        self._neg_class_name = (
            self._class_titles[1] if len(self._class_titles) > 1 else None
        )  # assuming negative class is index 1
        self._specificity = None
        self._precision = None
        self._accuracy = None
        self._sensitivity = None
        self._positive_predictive_rate = None
        self._f1_score = None
        self._average_over_folds = None
        if (
            self._is_binary
        ):  # if confusion matrix represents results from a binary model
            # acquire true pos/neg false pos/neg values
            self._tp, self._fp, self._tn, self._fn = server_metrics.get_tp_fp_tn_fn(
                self._y_true, self._y_pred, self._pos_class_name, self._neg_class_name
            )

    @property
    def accuracy(self):
        return self._accuracy

    @property
    def sensitivity(self):
        return self._sensitivity

    @property
    def positive_predictive_rate(self):
        return self._positive_predictive_rate

    @property
    def specificity(self):
        return self._specificity

    @property
    def precision(self):
        return self._precision

    @property
    def f1_score(self):
        return self._f1_score

    @property
    def y_true(self):
        return self._y_true

    @property
    def y_pred(self):
        return self._y_pred

    @property
    def average_over_folds(self):
        return self._average_over_folds

    @staticmethod
    def _verify_args(y_true, y_pred):
        """Verifies types of arguments passed to __init__ function of StatsCalc object

        Args:
            y_true (list): ground truth classification of each vector recognized
            y_pred (list): classifications as predicted by the model of y_pred vectors

        Raises:
            StatsCalcException: If args are not the correct type
        """
        if not isinstance(y_true, list):
            raise StatsCalcException(
                ("Expected a list for y_true values, got %s" % (str(type(y_true))))
            )
        if not isinstance(y_pred, list):
            raise StatsCalcException(
                ("Expected a list for y_pred values, got %s" % (str(type(y_pred))))
            )
        if not len(y_true) == len(y_pred):
            raise StatsCalcException("Length of y_true and y_pred must be equal")

    def _inspect_confusion_matrix(self):
        """Inspects confusion matrix passed to init of StatsCals to determine the classes represented

        Returns:
            list of classes represented in the confusion matrix
        """
        ret = {}
        for key in self._confusion_matrix.keys():
            ret[int(key)] = {}
            for k in self._confusion_matrix[key].keys():
                try:
                    temp = int(k)
                    ret[int(key)][temp] = self._confusion_matrix[key][k]
                except:
                    ret[int(key)][k] = self._confusion_matrix[key][k]
        self._confusion_matrix = ret
        return [int(x) for x in self._confusion_matrix.keys() if x not in UNK_UNC]

    def calc_accuracy(self):
        """calculates the accuracy of the confusion matrix supplied to __init__ function

        Returns:
            accuracy (dict): the accuracy of the confusion matrix, as well as the accuracy of each class
        """
        # If calculation has already been performed, return the value

        if self._accuracy is not None:
            return self._accuracy
        self._accuracy = server_metrics.accuracy(self._y_true, self._y_pred)
        return self._accuracy

    def calc_positive_predictive_rate(self):
        """Calculates the average positive predictive rate of all classes in the confusion matrix
        as well as the positive predictive rate for each class.
        Uses numpy.nanmean to avoid skewed results if a particular class does not have a PP value

            Returns:
                positive_predictive_rate (dict): positive predictive rate of each class as
                well as overall positive predictive rate
        """
        # If calculation has already been performed, return the value
        if self._positive_predictive_rate is not None:
            return self._positive_predictive_rate
        self._positive_predictive_rate = server_metrics.positive_predictive_rate(
            self._y_true, self._y_pred
        )
        return self._positive_predictive_rate

    def calc_sensitivity(self):
        """Calculates the average sensitivity of all classes in the confusion matrix as well
        as the sensitivity of each class.
        Uses numpy.nanmean to avoid skewed results if a particular class does not have a SE value

            Returns:
                average_se (dict): sensitivity of each class as well as the average sensitivity
        """
        # If calculation has already been performed, return the value
        if self._sensitivity is not None:
            return self._sensitivity
        self._sensitivity = server_metrics.sensitivity(self._y_true, self._y_pred)
        return self._sensitivity

    def calc_specificity(self):
        """calculates the specificity of the confusion matrix, if the matrix is binary

        Returns:
            If matrix is not binary, returns NaN
            If matrix is binary returns specificity
        """
        # If calculation has already been performed, return the value
        if self._specificity is not None:
            return self._specificity

        self._specificity = server_metrics.specificity(self._y_true, self._y_pred)
        return self._specificity

    def calc_precision(self):
        """Calculates the precision of the confusion matrix
        If the confusion matrix is binary calculates from tp, and fp values
        If the confusion matrix is not binary calculates from y_true and y_pred

            Returns:
                precision (dict): precision of the confusion matrix, and precision of each class
        """
        # If calculation has already been performed, return the value
        if self._precision is not None:
            return self._precision
        self._precision = server_metrics.precision(self._y_true, self._y_pred)
        return self._precision

    def calc_f1_score(self):
        """Calculates the f1 score of the confusion matrix (harmonic mean of precision and sensitivity)
        If the confusion matrix is binary, calculates from precision and average sensitivity values
        If the confusion matrix is not binary, calculates from the y_true and y_pred values

            Returns:
                f1_score (float): f1 score of the confusion matrix
        """
        # If calculation has already been performed, return the value
        if self._f1_score is not None:
            return self._f1_score
        self._f1_score = server_metrics.f1_score(self._y_true, self._y_pred)
        return self._f1_score

    def calc_all_metrics(self):
        """Calculates all available metrics for the confusion matrix supplied and
        stores the results in properties of StatsCalc object
        """

        metrics_set = server_metrics.get_metrics_set(
            {"y_true": self._y_true, "y_pred": self._y_pred}
        )

        for k in metrics_set.keys():
            if "_" + k in self.__dict__.keys():
                self.__dict__["_" + k] = metrics_set[k]
