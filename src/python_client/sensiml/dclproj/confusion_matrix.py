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

import copy
import itertools

from pandas import DataFrame
from tabulate import tabulate


class ConfusionMatrix(object):
    """A class used to create, store, and display a confusion matrix based on predicted segments and ground truth segments and compare against other confusion matrices
    Attributes:
        prediction_dict (dict): A dictionary of dictionaries that contains the confusion matrix prediction counts
        matrix (list): A formatted list of lists containing the confusion matrix data to be displayed
        model (str, optional): Name of model used to make prediction files (model being tested). Defaults to "".
        model_session (str, optional): Name of session that predcition files are labeled in. Defaults to "".
        gt_session (str, optional): Name of session that ground truth files are labeled in. Defaults to "".
        overlap_percent (float, optional): Percentage of overlap between predicted segment and real segment in order for the prediction to be considered over that even. Defaults to 50.0.
    Methods:
        compare_confusion_matrices(confusion_matrix_b)
            Compare this matrix to another and return matrix where every value is the difference in the values at the same [i][j] index in matrix a and matrix b
        display(matrix_to_display=None)
            Prints a tabulated ConfusionMatrix (prints self.matrix if no matrix is entered)
    """

    __BLACK = "\033[1;30m"
    __RED = "\033[1;31m"
    __GREEN = "\033[1;32m"
    __YELLOW = "\033[1;33m"
    prediction_dict = {}
    matrix = []
    model_session = ""
    gt_session = ""
    model = ""
    __predicted_segments = []
    __ground_truth_segments = []
    overlap_percent = 50.0

    def __init__(
        self,
        pred_segments: list,
        gt_segments: list,
        model_name: str = "",
        pred_session_name: str = "",
        gt_session_name: str = "",
        overlap_percent: float = 50.0,
    ):
        """Creates a Confusion Matrix object based on the given predicted segments and ground truth segments
        Args:
            pred_segments (list): list of (or single) datasegments or dataframe objects from prediction files to create confusion matrix from
            gt_segments (list): list of (or single) datasegments or dataframe objects from ground truth files to create confusion matrix from
            model_name (str, optional): Name of model used to make prediction files (model being tested). Defaults to "".
            pred_session_name (str, optional): Name of session that predcition files are labeled in. Defaults to "".
            gt_session_name (str, optional): Name of session that ground truth files are labeled in. Defaults to "".
            overlap_percent (float, optional): Percentage of overlap between predicted segment and real segment in order for the prediction to be considered over that even. Defaults to 50.0.
        """
        self.overlap_percent = overlap_percent
        self.model_session = pred_session_name
        self.gt_session = gt_session_name
        self.model = model_name
        pred_segments = copy.deepcopy(pred_segments)
        gt_segments = copy.deepcopy(gt_segments)
        if not isinstance(pred_segments, list):
            pred_segments = [pred_segments]
        if not isinstance(gt_segments, list):
            gt_segments = [gt_segments]
        for i in range(0, len(pred_segments)):
            if not isinstance(pred_segments[i], DataFrame):
                pred_segments[i] = pred_segments[i].to_dataframe()
        for i in range(0, len(gt_segments)):
            if not isinstance(gt_segments[i], DataFrame):
                gt_segments[i] = gt_segments[i].to_dataframe()

        self.matrix = self.__compare_predictions(pred_segments, gt_segments)
        self.__ground_truth_segments = gt_segments
        self.__predicted_segments = pred_segments

    def __repr__(self):
        self.display()
        return ""

    def __str__(self):
        self.display()
        return ""

    def __get_segment_list(self, segments_df: DataFrame) -> list:
        """take segments dataframe and returns a list of dictionaries, where each dictionary belongs to a different segment, with key names value, start, and end
        Args:
            segments_df (DataFrame): dataframe of segments converted from DataSegments object
        Returns:
            list: list of dictionaries containing condensed segment information
        """
        segments_df = segments_df.rename(
            columns={
                "label_value": "value",
                "capture_sample_sequence_start": "start",
                "capture_sample_sequence_end": "end",
            }
        )
        segment_list = segments_df.to_dict("records")
        return segment_list

    def __get_percent(self, numerator: int, denominator: int) -> float:
        """calculate percents rounded to the hundredths place while accounting for 0/0
        Args:
            numerator (int): numerator of the fraction corresponding to the percentage
            denominator (int): denominator of the fraction corresponding to the percentage
        Returns:
            float: the percent rounded to the hundredths place corresponding to (100*numerator/denominator) (or 0 in the case of 0/0)
        """
        return (
            round(100 * numerator / denominator, 2) if denominator and numerator else 0
        )

    def __calculate_overlap_percent(
        self, start_1: int, start_2: int, end_1: int, end_2: int
    ) -> float:
        """calculate how much of label_2 [start_2, end_2] is covered by label_1 [start_1, end_1] as a percent
        using the formula: 100*(min(end_1, end_2) - max(start_1, start_2))/(length_label_2)
        Args:
            start_1 (int): start value of label 1 (usually the prediction label)
            start_2 (int): start value of label 2 (usually the real label)
            end_1 (int): end value of label 1 (usually the prediction label)
            end_2 (int): start value of label 2 (usually the real label)
        Returns:
            float: the percent of label_2 that label_1 covers
        """
        # calculate overlap between labels
        label_overlap = min(end_1, end_2) - max(start_1, start_2)
        # calculate length of label 2
        range_of_label_2 = end_2 - start_2
        # return overlap percent
        return self.__get_percent(label_overlap, range_of_label_2)

    def __get_rc_list(
        self,
        pred_segment_list: list,
        real_segment_list: list,
        is_col_list: bool = False,
    ) -> list:
        """build the list of all labels found in the segment lists and add the names of the totals and % true positives
        column/row names based on whether a column name list or row name list is asked for
        Args:
            pred_segment_list (list): list of segments predicted by model
            real_segment_list (list): list of ground truth/ manually labeled segments
            is_col_list (bool, optional): boolean indicating whether to return a list of column names or row names. Defaults to False.
        Returns:
            list: list of the row or column names based on the segment labels in the predicted and real segment lists
        """

        events = [" "]
        for all_segment_set in list(
            itertools.zip_longest(pred_segment_list, real_segment_list)
        ):
            segment_set_all = [x for x in all_segment_set if not x == None]
            for segment_set in segment_set_all:
                for segment in segment_set:
                    label = segment["value"]
                    if events.count(label) == 0:
                        events.append(label)
        events.sort()
        events.append("UNK")
        if not is_col_list:
            events.extend(["Total", "Pos_Pred(%)"])
        else:
            events.extend(["Support", "Sense %"])
        return events

    def __build_matrix_comparison_frame(self, conf_matrix: list) -> list:
        """build a list of lists that copies column and row names from the inputed matrix
        Args:
            conf_matrix (list): confusion matrix to copy row and col names from
        Returns:
            list: list of lists where the 1st row are the column names and each successive row starts with the proper row names (no inner values)
        """
        tmp = [conf_matrix[0]]
        for name in tmp[0]:
            name = ConfusionMatrix.__BLACK + name
        for i in range(1, len(conf_matrix)):
            tmp.append([ConfusionMatrix.__BLACK + conf_matrix[i][0]])
        return tmp

    def __get_default_matrix_alignment(self, num_cols: int) -> list:
        """return list of "default" alignment, where the first column is left justified and all other columns are right justified
        Args:
            num_cols (int): number of columns in matrix
        Returns:
            list: list of "default" alignment, where the first column is left justified and all other columns are right justified
        """
        align_list = ["left"]
        for i in range(1, num_cols):
            align_list.append("right")
        return align_list

    def __insert_horizontal_line_table(
        self, table: list, pos: int, alignment: list
    ) -> list:

        """add a horizontal breaker line into a table
        Args:
            table (list): table in the form of a list of lists
            pos (int): row index for the line to be inserted at
            alignment (list): list of column alignments for tabulate format
        Returns:
            list: list of lists identical to the inputed list of lists with an inputed horizontal line row at index "pos"
        """
        tabulated = tabulate(table, colalign=alignment)
        newline_ind = tabulated.index("\n")
        line_breaker = tabulated[0:newline_ind]
        breaker = line_breaker.split()
        table.insert(pos, breaker)
        return table

    def __get_sum_row(self, pred_cts: dict, event: str, col_names: list) -> int:
        """calculate the sum of the numerical elements in a given row
        Args:
            pred_cts (dict): dictionary containing all predictions made and how they map to the actual labels
            event (str): name of the event row that you want to find the sum total of
            col_names (list): list of the column names to iterate over
        Returns:
            int: sum total of items in the event row
        """
        sum = 0
        for x in range(1, len(col_names) - 2):
            sum += pred_cts[col_names[x]][event]
        return sum

    def __get_sum_col(self, pred_cts: dict, event: str, row_names: list) -> int:
        """calculate the sum of the numerical elements in a given column
        Args:
            pred_cts (dict): dictionary containing all predictions made and how they map to the actual labels
            event (str): name of the event column that you want to find the sum total of
            row_names (list): list of the row names to iterate over
        Returns:
            int: sum total of items in the event column
        """
        sum = 0
        for x in range(1, len(row_names) - 2):
            sum += pred_cts[event][row_names[x]]
        return sum

    def __build_pred_dict(self, row_names: list, col_names: list) -> dict:
        """build a dictionary of dictionaries using the row names as the outer key set and the column names as the keys in each inner dictionary
        Args:
            row_names (list): list of the row names
            col_names (list): list of the column names
        Returns:
            dict: dictionary of dictionaries using the row names as the outer key set and the column names as the keys in each inner dictionary
        """
        tmp_dict = {}
        for i in range(1, len(row_names) - 2):
            tmp_dict[row_names[i]] = {}
            for j in range(1, len(col_names) - 2):
                tmp_dict[row_names[i]][col_names[j]] = 0
        return tmp_dict

    def __build_event_dict(self, row_names: list) -> dict:
        """build dictionary with keys as the different events (given in the row names list)
        Args:
            row_names (list): list of the row names
        Returns:
            dict: dictionary with keys as the different events (given in the row names list)
        """
        tmp_dict = {}
        for i in range(1, len(row_names) - 2):
            tmp_dict[row_names[i]] = 0
        return tmp_dict

    def __fill_sum_dict(
        self, pred_cts: dict, row_names: list, col_names: list, sum_type: str
    ) -> dict:
        """fill a dictionary with "row sums" or "column sums" (totals & supports)
        Args:
            pred_cts (dict): dictionary containing all predictions made and how they map to the actual labels
            row_names (list): list of the row names
            col_names (list): list of the column names
            sum_type (str): string indicating whether the dictionary should contain the row sums (support) or column sums (total)
        Returns:
            dict: dictionary containing "row sums" or "column sums" (totals & supports) where the keys are the row/col names
        """
        event_dict = self.__build_event_dict(row_names)
        for i in range(1, len(row_names) - 2):
            if sum_type == "r":
                event_dict[row_names[i]] = self.__get_sum_row(
                    pred_cts, row_names[i], col_names
                )
            else:
                event_dict[row_names[i]] = self.__get_sum_col(
                    pred_cts, row_names[i], row_names
                )
        return event_dict

    def __fill_percent_dict(
        self,
        pred_cts: dict,
        row_sums: dict,
        col_sums: dict,
        row_names: list,
        sum_type: str,
    ) -> dict:
        """fill a dictionary with "sense%" or "pos pred %"
        Args:
            pred_cts (dict): dictionary containing all predictions made and how they map to the actual labels
            row_sums (dict): list of the row sums
            col_sums (dict): list of the column sums
            row_names (list): list of the row names
            sum_type (str): list of the column names
        Returns:
        dict : dictionary containing the "sense%" or "pos pred %" where the keys are the row/col names
        """
        perc_dict = self.__build_event_dict(row_names)
        for i in range(1, len(row_names) - 2):
            if sum_type == "s":
                perc_dict[row_names[i]] = self.__get_percent(
                    pred_cts[row_names[i]][row_names[i]], row_sums[row_names[i]]
                )
            else:
                perc_dict[row_names[i]] = self.__get_percent(
                    pred_cts[row_names[i]][row_names[i]], col_sums[row_names[i]]
                )
        return perc_dict

    def __fill_prediction_dict(
        self, pred_segments: list, ground_truth_segments: list, pred_cts: dict
    ) -> dict:
        """fill a dictionary of dictionaries where the outer keys are the actual events and the inner keys are
        what they are predicted as (all labels that overlap with less than 40% of a real label are counted as UNK)
        Args:
            pred_segments (list): list of segments from prediction file
            ground_truth_segments (list): list of segments from manually labeled file
            pred_cts (dict): Empty dictionary of dictionaries with event keys
        Returns:
            dict: dictionary of dictionaries where the outer keys are the actual events and the inner keys are what they
                are predicted as with the inner values are the counts of each label
        """
        # Loop over all predicted segments
        for pdictionary in pred_segments:
            # Loop over real segments to find all real segements that the predicted segment overlaps with
            # (discard predictions that overlap w/ nothing)
            num_overlaps = 0
            for adictionary in ground_truth_segments:
                if len(adictionary) == 0:
                    break
                # If the next real segment begins after the predicted one ends then there will be no more overlapping segments
                if adictionary["start"] > pdictionary["end"]:
                    break
                # If the next real segment ends before the predicted one starts then it won't overlap so we should skip it
                if adictionary["end"] < pdictionary["start"]:
                    continue
                overlap = self.__calculate_overlap_percent(
                    pdictionary["start"],
                    adictionary["start"],
                    pdictionary["end"],
                    adictionary["end"],
                )
                # Keep track of what the prediction was and how it compared to the actual label IF it is over the overlap threshold
                if overlap >= self.overlap_percent:
                    pred_cts[pdictionary["value"]][adictionary["value"]] += 1
                    num_overlaps += 1
            if num_overlaps == 0:
                pred_cts[pdictionary["value"]]["UNK"] += 1

        # Count number of real segments that were left unlabeled in predictions
        for adictionary in ground_truth_segments:
            num_overlaps = 0
            for pdictionary in pred_segments:
                if pdictionary["start"] > adictionary["end"]:
                    break
                if pdictionary["end"] < adictionary["start"]:
                    continue
                num_overlaps += 1
            if num_overlaps == 0:
                pred_cts["UNK"][adictionary["value"]] += 1
        return pred_cts

    # Method to build the confusion matrix
    def __build_conf_matrix(
        self,
        pred_cts: dict,
        row_names: list,
        col_names: list,
        row_sum_dict: dict,
        col_sum_dict: dict,
        sense_dict: dict,
        pospred_dict: dict,
        sum_total: int,
    ) -> list:

        """list of lists containing the confusion matrix data
        Args:
            pred_cts (dict): Dictionary containing the segment prediction data
            row_names (list): List of the confusion matrix row names
            col_names (list): List of the confusion matrix col names
            row_sum_dict (dict): Dictionary containing the sums of each row
            col_sum_dict (dict): Dictionary containing the sums of each col
            sense_dict (dict): Dictionary containing the sensitivity for each row
            pospred_dict (dict): Dictionary containing the positive prediction % for each col
            sum_total (int): Sum total of all predictions made
        Returns:
            list: build and format confusion matrix
        """
        conf_matrix = []
        conf_matrix.append(col_names)
        corr_sum = 0
        for x in range(1, len(row_names) - 2):
            label = row_names[x]
            l = [label]
            for y in range(1, len(row_names) - 2):
                if x == y:
                    corr_sum += pred_cts[row_names[y]][label]
                    l.append(
                        ConfusionMatrix.__GREEN + str(pred_cts[row_names[y]][label])
                    )
                else:
                    l.append(ConfusionMatrix.__RED + str(pred_cts[row_names[y]][label]))
            l.append(ConfusionMatrix.__BLACK + str(row_sum_dict[label]))
            l.append(ConfusionMatrix.__BLACK + str(sense_dict[label]))
            conf_matrix.append(l)
        l = ["Total"]
        l.extend(list(col_sum_dict.values()))
        l.append(sum_total)
        conf_matrix.append(l)
        l = ["Pos_Pred(%)"]
        l.extend(list(pospred_dict.values()))
        l.extend(["Acc(%)", self.__get_percent(corr_sum, sum_total)])
        conf_matrix.append(l)

        return conf_matrix

    def __compare_predictions(
        self, pred_segments: list, ground_truth_segments: list
    ) -> list:

        """compare segments from predicted file(s) and ground truth file(s) and return a confusion matrix from the results. The number of prediction files and ground truth files MUST match.
        Args:
            pred_segments (list): list of segments from prediction file each set of segments in dataframe format
            ground_truth_segments (list): list of segments from manually labeled file each set of segments in dataframe format
        Returns:
            list: list: a list of lists with the confusion matrix data
        """
        if len(pred_segments) != len(ground_truth_segments):
            raise Exception(
                "The number of prediction files and ground truth files do not currently match."
            )
        for i in range(0, len(pred_segments)):
            pred_segments[i] = self.__get_segment_list(pred_segments[i])
            ground_truth_segments[i] = self.__get_segment_list(ground_truth_segments[i])
        row_names = self.__get_rc_list(
            pred_segments,
            ground_truth_segments,
            is_col_list=False,
        )
        col_names = self.__get_rc_list(
            pred_segments,
            ground_truth_segments,
            is_col_list=True,
        )
        # Count of labels in capture file labeled by model
        pred_cts = self.__build_pred_dict(row_names, col_names)
        for index in range(0, len(pred_segments)):
            pred_cts = self.__fill_prediction_dict(
                pred_segments[index], ground_truth_segments[index], pred_cts
            )
        self.prediction_dict = copy.deepcopy(pred_cts)
        # Get row sums
        row_sum_dict = self.__fill_sum_dict(pred_cts, row_names, col_names, "r")
        # Get col sums
        col_sum_dict = self.__fill_sum_dict(pred_cts, row_names, col_names, "c")
        # Get total sum
        sum_total = sum(row_sum_dict.values())
        # Get sense %s
        sense_dict = self.__fill_percent_dict(
            pred_cts, row_sum_dict, col_sum_dict, row_names, "s"
        )
        # Get positive prediction %s
        pospred_dict = self.__fill_percent_dict(
            pred_cts, row_sum_dict, col_sum_dict, row_names, "p"
        )

        confusion_matrix = self.__build_conf_matrix(
            pred_cts,
            row_names,
            col_names,
            row_sum_dict,
            col_sum_dict,
            sense_dict,
            pospred_dict,
            sum_total,
        )

        return confusion_matrix

    def __print_confusion_matrix(
        self,
        row_names: list = None,
        col_names: list = None,
        colalign: list = None,
    ) -> None:
        """prints a confusion matrix with prediction session name and model name as title using the given segments and alignment
        Args:
            row_names (list, optional): list of row names. Defaults to None.
            col_names (list, optional): list of column names. Defaults to None.
            colalign (list, optional): list of alignments. Defaults to None.
        """
        self.__ground_truth_segments
        self.__predicted_segments
        print(ConfusionMatrix.__BLACK + "Pred Session: " + self.model_session)
        print("Model: " + self.model)
        if row_names == None:
            row_names = self.__get_rc_list(
                self.__predicted_segments,
                self.__ground_truth_segments,
                is_col_list=False,
            )
        if col_names == None:
            col_names = self.__get_rc_list(
                self.__predicted_segments,
                self.__ground_truth_segments,
                is_col_list=True,
            )
        if colalign == None:
            colalign = self.__get_default_matrix_alignment(len(col_names))
        self.matrix = self.__insert_horizontal_line_table(
            self.matrix, len(self.matrix) - 2, colalign
        )
        print(tabulate(self.matrix, colalign=colalign))

    def compare_confusion_matrices(
        self,
        conf_matrix_b: list,
    ) -> list:
        """compare this matrix to another and create matrix where every value is the difference in the values at the same [i][j] index in matrix a and matrix b
        Args:
            conf_matrix_b (list): confusion matrix to set as the theoretically worse matrix (generally entered as other.matrix where other is a different ConfusionMatrix object)
        Returns:
            list: matrix where every value is the difference in the values at the same [i][j] index in matrix a and matrix b
                (values where a[i][j] > b[i][j] are colored GREEN and values where a[i][j] < b[i][j] are colored RED)
        """

        colalign = ["left"]
        for i in range(1, len(self.matrix[0])):
            colalign.append("right")
        tmp = self.__build_matrix_comparison_frame(self.matrix)
        for i in range(1, len(self.matrix)):
            for j in range(1, len(self.matrix[i])):
                a = (
                    str(self.matrix[i][j])
                    .replace(ConfusionMatrix.__BLACK, "")
                    .replace(ConfusionMatrix.__GREEN, "")
                    .replace(ConfusionMatrix.__RED, "")
                )
                b = (
                    str(conf_matrix_b[i][j])
                    .replace(ConfusionMatrix.__BLACK, "")
                    .replace(ConfusionMatrix.__GREEN, "")
                    .replace(ConfusionMatrix.__RED, "")
                )
                if a.replace(".", "").isdecimal() and b.replace(".", "").isdecimal():
                    num = float(a) - float(b)
                    if (num).is_integer():
                        num = int(num)
                    if num != 0 and (
                        i == len(self.matrix) - 2 or j == len(self.matrix) - 2
                    ):
                        tmp[i].append(ConfusionMatrix.__YELLOW + str(round(num, 2)))
                    elif num > 0 and (
                        (i == j)
                        or (i == len(self.matrix) - 1 or j == len(self.matrix) - 1)
                    ):
                        tmp[i].append(
                            ConfusionMatrix.__GREEN + "+" + str(round(num, 2))
                        )
                    elif num < 0 and (
                        i != j
                        and (i != len(self.matrix) - 1 and j != len(self.matrix) - 1)
                    ):
                        tmp[i].append(ConfusionMatrix.__GREEN + str(round(num, 2)))
                    elif num == 0:
                        tmp[i].append(ConfusionMatrix.__BLACK + str(round(num, 2)))
                    elif num > 0:
                        tmp[i].append(ConfusionMatrix.__RED + "+" + str(round(num, 2)))
                    else:
                        tmp[i].append(
                            ConfusionMatrix.__RED + "-" + str(abs(round(num, 2)))
                        )

                else:
                    tmp[i].append(ConfusionMatrix.__BLACK + a)
        return tmp

    def display(self, matrix_to_display=None):
        """Displays a tabulated ConfusionMatrix
        Args:
            matrix_to_display (ConfusionMatrix, optional): _description_. Defaults to None, in which case self will be displayed.
        """
        if matrix_to_display != None:
            num_cols = len(matrix_to_display[0])
            colalign = self.__get_default_matrix_alignment(num_cols)
            print(tabulate(matrix_to_display, colalign=colalign))
        else:
            self.__print_confusion_matrix()
