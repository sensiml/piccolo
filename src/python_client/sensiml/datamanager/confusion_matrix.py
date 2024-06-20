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

import pandas as pd
from random import randint
import numpy as np
from numpy import NaN
import operator

UNK = "UNK"
UNC = "UNC"
UNK_UNC = [UNK, UNC]
DF_COLUMNS = ["ClassIn", "UNK", "UNC", "Support", "Sens(%)"]
INSERTION_INDEX = 1
AVG = "average"
ACC = "accuracy"
SE = "sensitivity"
PP = "positive_predictive_rate"
SPEC = "specificity"
PREC = "precision"
F1 = "f1_score"
HAS_KEYS = {
    "f1_score": True,
    "accuracy": False,
    "sensitivity": True,
    "specificity": False,
    "positive_predictive_rate": True,
    "precision": True,
}
EXPECTED_KEYS = [
    "ConfusionMatrix",
    "f1_score",
    "accuracy",
    "sensitivity",
    "positive_predictive_rate",
    "precision",
    "specificity",
]
NEEDED_PROPS = [
    "confusion_matrix",
    "y_true",
    "y_pred",
    "f1_score",
    "accuracy",
    "sensitivity",
    "positive_predictive_rate",
    "precision",
    "specificity",
]


class ConfusionMatrixException(Exception):
    """Base exception for ConfusionMatrix and ConfusionMatrixList objects"""

    def __init__(self, e):
        self.e = e

    def __str__(self):
        return repr(self.e)


class ConfusionMatrix(object):
    """This object is a representation of a confusion matrix that contains properties for statistics that can be
    generated from a confusion matrix as well as a DataFrame representation for easy viewing"""

    def __init__(self, metrics_dict):
        """Initializes ConfusionMatrix object

        Args:
            metrics_dict (dict): dictionary of metrics values calculated by the server code when a test set
            is recognized against a model generating a confusion matrix

        Raise:
            ConfusionMatrixException: If arg is not correct type, or does not contain all needed keys returned by
            the server"""
        if not isinstance(metrics_dict, dict):
            raise ConfusionMatrixException(
                f"Expected a dictionary, instead got {str(type(metrics_dict))}"
            )
        keys_missing = []
        for key in EXPECTED_KEYS:
            if key not in metrics_dict.keys():
                keys_missing.append(key)
        if len(keys_missing) >= 1:
            raise ConfusionMatrixException(
                (
                    "Not all keys present in metrics dict, missing keys %s"
                    % str(keys_missing)
                )
            )
        # Init properties from metrics dict
        self._cm = metrics_dict["ConfusionMatrix"]
        self._accuracy = metrics_dict["accuracy"]
        self._sensitivity = metrics_dict["sensitivity"]
        self._positive_predictive_rate = metrics_dict["positive_predictive_rate"]
        self._precision = metrics_dict["precision"]
        self._specificity = metrics_dict["specificity"]
        self._f1_score = metrics_dict["f1_score"]
        # build DataFrame and determine se and pp by class rather than avg returned by server
        self._class_titles = None
        self._cm_data_frame = self._build_data_frame()

    def _order_columns(self, confusion_matrix):
        """Orders the columns such that the classes come first, then UNK and UNC."""
        columns = confusion_matrix.index.tolist() + ["UNK", "UNC"]
        return confusion_matrix[columns]

    def __str__(self):
        """Override string function to return the formatted string representation of the confusion matrix"""
        formatted_output = "CONFUSION MATRIX:\n"
        cell_width = 10
        decimal_points = 1

        cell_width_str = str(cell_width)
        decimal_points_str = str(decimal_points)
        cm = self._order_columns(pd.DataFrame.from_dict(self._cm).transpose())

        Unknown_UNK = 0  # how many Unknowns have been classified as UNK
        row_ix = None
        col_ix = None
        for j, c in enumerate(cm.columns.values):
            if c.lower() == "unknown":  # row
                row_ix = j
            if c == "UNK":  # column
                col_ix = j
        if row_ix and col_ix:
            Unknown_UNK = cm.iloc[row_ix, col_ix]

        row_format = ("{:>" + cell_width_str + "}") * (len(cm.columns) + 3) + "\n"
        columns = cm.columns.tolist() + ["Support", "Sens(%)"]
        formatted_output += row_format.format("", *columns)
        decimal_cell_format = "{0:." + decimal_points_str + "f}"
        for i, r in cm.iterrows():
            if i.lower() == "unknown":
                adjust = Unknown_UNK
            else:
                adjust = 0
            row = [decimal_cell_format.format(a) for a in r] + [
                decimal_cell_format.format(r.sum() - r["UNC"]),
                decimal_cell_format.format(
                    100 * (cm.loc[i, i] + adjust) / float(r.sum() - r["UNC"])
                ),
            ]
            formatted_output += row_format.format(i, *row)
        formatted_output += "\n"
        sum_row = cm.sum().tolist() + [sum(cm.sum().tolist()[:-1]), ""]
        formatted_output += row_format.format("Total", *sum_row) + "\n"

        pct_row_format = (
            "{:>"
            + cell_width_str
            + "}"
            + ("{:>" + cell_width_str + "." + decimal_points_str + "f}") * (len(cm))
            + ("{:>" + cell_width_str + "}") * 3
            + "{:>"
            + cell_width_str
            + "."
            + decimal_points_str
            + "f}"
            + "\n"
        )
        pp_row = (
            100 * np.array(cm).diagonal().astype(float) / cm.sum()[:-2].astype(float)
        )
        pp_row = pp_row.tolist()

        pp_row += [
            "",
            "",
            "Acc(%)",
            100.0
            * (sum(np.array(cm).diagonal()) + Unknown_UNK)
            / (sum(cm.sum()) - sum(cm["UNC"])),
        ]
        formatted_output += pct_row_format.format("PosPred(%)", *pp_row)

        return formatted_output

    def __html__(self):
        """Override string function to return the formatted string representation of the confusion matrix"""
        style = """<style>
                table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 90%;
                }

                th {
                border: 1px solid #040911;
                text-align: center;
                padding: 8px;
                background-color: #dddddd;
                }

                td {
                border: 1px solid #040911;
                text-align: center;
                padding: 8px;
                background-color: #f9f9f9;
                }

                </style>
                """

        formatted_output = '<table style="width:90%">'
        cell_width = 10
        decimal_points = 1

        cell_width_str = str(cell_width)
        str(decimal_points)
        cm = self._order_columns(pd.DataFrame.from_dict(self._cm).transpose())
        row_format = ("{:>" + cell_width_str + "}") * (len(cm.columns) + 3) + "\n"
        th = "<th>{}</th>"
        td = "<td>{}</td>"
        tr = "<tr>{}</tr>"
        columns = cm.columns.tolist() + ["Support", "Sens(%)"]
        formatted_output += tr.format("".join([th.format(x) for x in [""] + columns]))

        decimal_cell_format = "{0:.2f}"
        int_format_cell = "{0:.2f}"
        index = 0
        for i, r in cm.iterrows():
            row = th.format(columns[index])
            row += "".join([td.format(int_format_cell.format(x)) for x in r])
            row += td.format(int_format_cell.format(r.sum() - r["UNC"]))
            row += td.format(
                decimal_cell_format.format(
                    100 * cm.loc[i, i] / float(r.sum() - r["UNC"])
                )
            )
            index += 1

            formatted_output += tr.format(row)

        sum_row = cm.sum().tolist() + [sum(cm.sum().tolist()[:-1])]
        sum_row = [td.format(int_format_cell.format(x)) for x in sum_row] + [
            td.format("")
        ]
        sum_row = [th.format("Total")] + sum_row

        formatted_output += tr.format("".join(sum_row))

        pp_row = (
            100 * np.array(cm).diagonal().astype(float) / cm.sum()[:-2].astype(float)
        )

        pp_row = [td.format(decimal_cell_format.format(x)) for x in pp_row.tolist()]

        pp_row += [th.format(x) for x in ["", "", "Acc(%)"]]

        pp_row += [
            td.format(
                decimal_cell_format.format(
                    100.0
                    * sum(np.array(cm).diagonal())
                    / (sum(cm.sum()) - sum(cm["UNC"]))
                )
            )
        ]

        pp_row = [th.format("PosPred(%)")] + pp_row

        formatted_output += tr.format("".join(pp_row))

        formatted_output += "</table>"
        return style + formatted_output

    def __repr__(self):
        """Override repr function to return str value of object"""
        return str(self)

    @property
    def sensitivity(self):
        return self._sensitivity

    @property
    def positive_predictive_rate(self):
        return self._positive_predictive_rate

    @property
    def accuracy(self):
        return self._accuracy

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
    def confusion_matrix(self):
        return self._cm

    @property
    def confusion_matrix_data_frame(self):
        return self._cm_data_frame

    def se_by_class_name(self, class_name):
        """Returns the sensitivity of a given class in the confusion matrix

        Args:
            class_name (str): name of the class to return sensitivity of

        Returns:
            se_by_class: if class name exists in matrix return SE, else NaN"""
        return (
            self._sensitivity[class_name] if class_name in self._class_titles else NaN
        )

    def pp_by_class_name(self, class_name):
        """Returns the positive predictivity of a given class in the confusion matrix

        Args:
            class_name (str): name of the class to return positive predictivity of

        Returns:
            pp_by_class: if class name exists in matrix return PP, else NaN"""
        return (
            self._positive_predictive_rate[class_name]
            if class_name in self._class_titles
            else NaN
        )

    def _build_data_frame(self):
        """Builds a DataFrame from the dictionary representation of a confusion matrix returned by the server
        primarily for viewing purposes.

            Returns:
                cm_data_frame (pandas.DataFrame): DataFrame representation of dictionary confusion matrix"""
        self._class_titles = [x for x in self._cm.keys() if x not in UNK_UNC]
        self._class_titles.sort()
        row_index = 0
        df_cols = (
            ["ClassIn"] + self._class_titles + ["UNK", "UNC", "Support", "Sens(%)"]
        )
        ret = pd.DataFrame(columns=df_cols)
        support_total = 0.0
        for item in self._class_titles:
            c_vals = []
            for it in self._class_titles + [UNK]:
                c_vals.append(float(self._cm[item][it]))
            row_total = sum(c_vals)
            support_total += row_total
            c_vals.append(float(self._cm[item][UNC]))
            c_vals.append(row_total)
            if row_total == 0.0:
                c_vals.append(NaN)
            else:
                c_vals.append(float(self._cm[item][item] / row_total) * 100)
            n_row = [item] + c_vals
            ret.loc[row_index] = n_row
            row_index += 1
        n_row = ["UNK"] + ([0] * (len(ret.columns.tolist()) - 2)) + [NaN]
        ret.loc[row_index] = n_row
        row_index += 1
        pp_vals = []
        sum_vals = []
        for item in self._class_titles + [UNK]:
            col_total = 0.0
            if item == UNK:
                for un in self._class_titles:
                    col_total += self._cm[un][UNK]
                sum_vals.append(col_total)
            else:
                for it in self._class_titles:
                    col_total += self._cm[it][item]
                sum_vals.append(col_total)
            if item == UNK:
                pp_vals.append(NaN)
            else:
                if col_total > 0.0:
                    pp_vals.append(float(self._cm[item][item] / col_total) * 100)
                else:
                    pp_vals.append(NaN)
        n_row = ["Total"] + sum_vals + [sum(ret[UNC]), support_total, 0]
        ret.loc[row_index] = n_row
        row_index += 1
        temp_total = 0.0
        row_total = 0.0
        for item in self._class_titles:
            temp_total += self._cm[item][item]
            for it in self._class_titles + [UNK]:
                row_total += self._cm[item][it]
        acc = float(temp_total / row_total) * 100
        n_row = ["PosPred(%)"] + pp_vals + [0] + ["Acc(%)"] + [acc]
        ret.loc[row_index] = n_row
        self._class_titles.sort(reverse=True)
        return ret


class ConfusionMatrixList(ConfusionMatrix):
    """ConfusionMatrix list object represents a group of confusion matrices and is itself a confusion matrix.
    Enables investigation of child matrices to determine best model by the statistics of the confusion matrix"""

    def __init__(self, confusion_matrices):
        """Initializes ConfusionMatrixList object
        Args:
            confusion_matrices (dict): keys should be a way to identify each matrix, an index for example
            values are ConfusionMatrix objects

        Raises:
            ConfusionMatrixException: If arg are incorrect type, needs to be a dict of confusion matrices"""
        if isinstance(confusion_matrices, dict):
            for key, value in confusion_matrices.items():
                if not isinstance(value, ConfusionMatrix):
                    raise ConfusionMatrixException(
                        (
                            "Expected a ConfusionMatrix, instead got %s"
                            % str(type(value))
                        )
                    )
        else:
            raise ConfusionMatrixException(
                (
                    "Expected a dictionary, instead got %s"
                    % str(type(confusion_matrices))
                )
            )
        # compile child matrices, and average their statistics to generate this parent matrix
        self._confusion_matrices = confusion_matrices
        self._class_titles = self._inspect_confusion_matrix()
        compiled_metrics = self._average_child_metrics
        super(ConfusionMatrixList, self).__init__(compiled_metrics)
        self._sorted_matrices = [(k, v) for k, v in self._confusion_matrices.items()]

    def highest_avg_se_child(self):
        """Get key, and child matrix from dict with the highest average sensitivity

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the highest average sensitivity"""
        return self._query_children(operator.gt, SE, True)

    def highest_avg_pp_child(self):
        """Get key, and child matrix from dict with the highest average positive predictivity

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the highest average PP"""
        return self._query_children(operator.gt, PP, True)

    def highest_accuracy_child(self):
        """Get key, and child matrix from dict with the highest accuracy

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the highest accuracy"""
        return self._query_children(operator.gt, ACC, False)

    def highest_specificity_child(self):
        """Get key, and child matrix from dict with the highest specificity

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the highest specificity"""
        return self._query_children(operator.gt, SPEC, False)

    def highest_precision_child(self):
        """Get key, and child matrix from dict with the highest precision

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the highest precision"""
        return self._query_children(operator.gt, PREC, True)

    def highest_f1_score_child(self):
        """Get key, and child matrix from dict with the highest f1_score

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the highest f1_score"""
        return self._query_children(operator.gt, F1, True)

    def lowest_avg_se_child(self):
        """Get key, and child matrix from dict with the lowest average sensitivity

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the lowest average sensitivity"""
        return self._query_children(operator.lt, SE, True)

    def lowest_avg_pp_child(self):
        """Get key, and child matrix from dict with the lowest average positive predictivity

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the lowest average positive predictivity"""
        return self._query_children(operator.lt, PP, True)

    def lowest_accuracy_child(self):
        """Get key, and child matrix from dict with the lowest accuracy

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the lowest accuracy"""
        return self._query_children(operator.lt, ACC, False)

    def lowest_specificity_child(self):
        """Get key, and child matrix from dict with the lowest specificity

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the lowest specificity"""
        return self._query_children(operator.lt, SPEC, False)

    def lowest_precision_child(self):
        """Get key, and child matrix from dict with the lowest precision

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the lowest precision"""
        return self._query_children(operator.lt, PREC, True)

    def lowest_f1_score_child(self):
        """Get key, and child matrix from dict with the lowest f1_score

        Returns:
            key: key value provided in initialize dictionary pertaining to the confusion matrix
            confusion_matrix (ConfusionMatrix): The confusion matrix object with the lowest f1_score"""
        return self._query_children(operator.lt, F1, True)

    def head(self, length=5):
        """Returns the head of the list of confusion matrix objects, size specified

        Args:
            length (int): Number of values to return from confusion matrix list

        Returns:
            Head of size specified if all parameters are correct
            None if length is invalid
            Entire list if length is greater than the list size"""
        try:
            length = int(length)
        except ValueError:
            return None
        if length <= len(self._sorted_matrices):
            return self._sorted_matrices[0:length]
        else:
            return self._sorted_matrices

    def sort_by_metric(self, metric):
        """Sort the list of confusion matrices by a given metric
        Args:
            metric (str): The metric name to sort by, must be a property of the confusion matrix

        Returns:
            sorted_matrices (list): a list of index, object tuples after sorting is complete

        Raises:
            ConfusionMatrixException if metric value passed in is not recognized"""
        if metric not in EXPECTED_KEYS[1 : len(EXPECTED_KEYS)]:
            raise ConfusionMatrixException(
                (
                    "Metric %s is not a supported metric for sorting, use one of the following %s"
                    % (str(metric), str(EXPECTED_KEYS[1 : len(EXPECTED_KEYS)]))
                )
            )
        self._lambda_child_sort(metric, HAS_KEYS[metric])
        return self._sorted_matrices

    def _lambda_child_sort(self, metric, has_keys):
        """Uses lambda functions to sort the confusion matrix list by a given metric,
        or property of the child matrices. Sorting is done in place.

           Args:
               metric (str): the name of the metric to sort by
               has_keys (bool): If the metric to sort by is a dictionary value True, else False
        """
        temp = self._sorted_matrices
        # If the metric is a dictionary, sort by the average value
        if has_keys:
            temp = sorted(temp, key=lambda x: getattr(x[1], metric)[AVG], reverse=True)
        else:
            temp = sorted(temp, key=lambda x: getattr(x[1], metric), reverse=True)
        self._sorted_matrices = temp

    @property
    def _average_child_metrics(self):
        """averages the metrics of all of the children provided in order to build dict needed to init a ConfusionMatrix
        object

            Returns:
                metrics_dict (dict): averaged metrics dictionary from all children"""
        ret = dict.fromkeys(NEEDED_PROPS)
        y_true = []
        y_pred = []
        for key in ret.keys():
            if key == NEEDED_PROPS[1]:
                for k, cm in self._confusion_matrices.items():
                    y_true += getattr(cm, key)
                ret[key] = y_true
            elif key == NEEDED_PROPS[2]:
                for k, cm in self._confusion_matrices.items():
                    y_pred += getattr(cm, key)
                ret[key] = y_pred
            # create a list for each statistical measure, and append each CM's value
            elif key != NEEDED_PROPS[0]:
                for index, cm in self._confusion_matrices.items():
                    if isinstance(getattr(cm, key), dict):
                        if not isinstance(ret[key], dict):
                            ret[key] = dict.fromkeys(getattr(cm, key).keys())
                            for k in ret[key].keys():
                                ret[key][k] = []
                        for sub in ret[key].keys():
                            ret[key][sub].append(getattr(cm, key)[sub])
                    else:
                        if not isinstance(ret[key], list):
                            ret[key] = []
                        ret[key].append(getattr(cm, key))
            else:
                ret["ConfusionMatrix"] = self._sum_confusion_matrices()

        # After all of the statistical measures across all confusion matrices have been filled in, average them
        for to_avg in NEEDED_PROPS[3:]:
            if isinstance(ret[to_avg], dict):
                for k in ret[to_avg].keys():
                    ret[to_avg][k] = np.nanmean(ret[to_avg][k])
            else:
                ret[to_avg] = np.nanmean(ret[to_avg])
        return ret

    def _sum_confusion_matrices(self):
        """Sums all of the dictionary confusion matrices of children to create a top level combined confusion matrix

        Returns:
            confusion_matrix (dict): dictionary representation of a confusion matrix"""
        ret = dict.fromkeys(self._class_titles)
        for key in ret.keys():
            for item in self._class_titles + [UNK, UNC]:
                if not isinstance(ret[key], dict):
                    ret[key] = {}
                ret[key][item] = 0.0
        for index, conf in self._confusion_matrices.items():
            for item in self._class_titles:
                for it in self._class_titles + [UNK, UNC]:
                    ret[item][it] += float(conf.confusion_matrix[item][it])
        return ret

    def _inspect_confusion_matrix(self):
        """Inspects the child matrices given to the init function to determine the classes contained in them

        Returns:
            class_titles (list): list of class titles contained in the confusion matrix"""
        k = self._confusion_matrices.keys()
        random_matrix_index = randint(0, len(self._confusion_matrices) - 1)
        to_inspect = self._confusion_matrices[k[random_matrix_index]]
        class_titles = [
            x for x in to_inspect.confusion_matrix.keys() if x not in UNK_UNC
        ]
        assert len(class_titles) > 1
        class_titles.sort(reverse=True)
        return class_titles

    @staticmethod
    def _get_truth(val_a, opr, val_b):
        """returns the truth of two values and a boolean operator

        Returns:
            True if val_a operator val_b is True, Else False"""
        return opr(val_a, val_b)

    def _query_children(self, opr, prop, has_keys=False):
        """Iterates over children to find the child at the top of the list given the operator and property provided

        Example:
            If operator.gt and property f1_score are passed in, the index and confusion matrix with the highest
            f1_score will be returned

        Args:
            opr (operator): Must be a boolean operator
            prop (str): must be a property of the ConfusionMatrix object

        Returns:
            result (tuple): Tuple of length 2, index 0 == index of confusion matrix, index 1 == confusion matrix"""
        is_first = True
        ret = None
        for i, conf in self._confusion_matrices.items():
            if is_first:
                ret = (i, conf)
                is_first = False
            else:
                if not has_keys:
                    if self._get_truth(getattr(conf, prop), opr, getattr(ret[1], prop)):
                        ret = (i, conf)
                else:
                    if self._get_truth(
                        getattr(conf, prop)[AVG], opr, getattr(ret[1], prop)[AVG]
                    ):
                        ret = (i, conf)
        return ret
