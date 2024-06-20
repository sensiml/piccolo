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

import pytest

from engine.base.calculate_statistics import StatsCalc, StatsCalcException


class TestStatsCalc:
    """Tests the statistics calculator object for binary and multi class confusion matrices,
    as the calculations differ between binary and multi class in some cases"""

    def assertEqual(self, a, b):
        assert a == b

    def assertIsInstance(self, a, b):
        assert isinstance(a, b)

    def assertAlmostEqual(self, a, b):
        assert abs(a - b) < 0.001

    @pytest.fixture(autouse=True)
    def setUp(self):
        """setting confusion matrix info and mapping y_true y_pred to confusion matrix values"""
        self._y_true_multi = [
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            3,
        ]
        self._y_pred_multi_no_ukn = [
            1,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            3,
            3,
            1,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            3,
            3,
        ]
        self._y_pred_multi_ukn = [
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            3,
            "UNK",
            "UNK",
            2,
            2,
            2,
            3,
            "UNK",
            3,
            3,
            3,
            "UNK",
            "UNK",
        ]

        self._y_true_binary = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
        self._y_pred_binary_no_ukn = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2]
        self._y_pred_binary_ukn = [
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            "UNK",
            "UNK",
            "UNK",
            1,
            2,
            2,
            "UNK",
            "UNK",
        ]

        self.bin_obj_no_ukn = StatsCalc(self._y_true_binary, self._y_pred_binary_no_ukn)
        self.bin_obj_ukn = StatsCalc(self._y_true_binary, self._y_pred_binary_ukn)
        self.multi_obj_no_ukn = StatsCalc(self._y_true_multi, self._y_pred_multi_no_ukn)
        self.multi_obj_ukn = StatsCalc(self._y_true_multi, self._y_pred_multi_ukn)

        self._desired_se_binary_no_ukn = {1: 60.00, 2: 80.00, "average": 70.00}
        self._desired_se_binary_ukn = {1: 50.00, 2: 40.00, "average": 45.00}
        self._desired_se_multi_no_ukn = {
            1: 60.0,
            2: 60.0,
            3: 100.0,
            "average": 73.333333333333343,
        }
        self._desired_se_multi_ukn = {
            1: 50.0,
            2: 60.0,
            3: 60.0,
            "average": 56.666666666666679,
        }

        self._desired_acc_binary_no_ukn = 66.6666666667
        self._desired_acc_binary_ukn = 46.666666666
        self._desired_acc_multi_no_ukn = 70.00
        self._desired_acc_multi_ukn = 55.00

        self._desired_pp_binary_no_ukn = {
            1: 85.714285714285708,
            2: 50.0,
            "average": 67.857142857142861,
        }
        self._desired_pp_binary_ukn = {
            1: 83.333333333333343,
            2: 50.0,
            "average": 66.666666666666671,
        }
        self._desired_pp_multi_no_ukn = {
            1: 85.714285714285708,
            2: 60.0,
            3: 62.5,
            "average": 69.404761904761912,
        }
        self._desired_pp_multi_ukn = {
            1: 100.0,
            2: 60.0,
            3: 60.0,
            "average": 73.333333333333343,
        }

        self._desired_f1_binary_no_ukn = {
            1: 70.588235294117638,
            2: 61.53846153846154,
            "average": 66.063348416289585,
        }
        self._desired_f1_binary_ukn = {
            1: 62.5,
            2: 44.44444444444445,
            "average": 53.472222222222229,
        }
        self._desired_f1_multi_no_ukn = {
            1: 70.588235294117638,
            2: 60.0,
            3: 76.923076923076934,
            "average": 69.170437405731505,
        }
        self._desired_f1_multi_ukn = {
            1: 66.666666666666657,
            2: 60.0,
            3: 60.0,
            "average": 62.222222222222221,
        }

        self._desired_prec_binary_no_ukn = {
            1: 85.714285714285708,
            2: 50.0,
            "average": 67.857142857142861,
        }
        self._desired_prec_binary_ukn = {
            1: 83.333333333333343,
            2: 50.0,
            "average": 66.666666666666671,
        }
        self._desired_prec_multi_no_ukn = {
            1: 85.714285714285708,
            2: 60.0,
            3: 62.5,
            "average": 69.404761904761912,
        }
        self._desired_prec_multi_ukn = {
            1: 100.0,
            2: 60.0,
            3: 60.0,
            "average": 73.333333333333343,
        }

        self._desired_spec_binary_no_ukn = 70.0
        self._desired_spec_binary_ukn = 69.047619047619037
        self._desired_spec_multi_no_ukn = 82.8347578348
        self._desired_spec_multi_ukn = 86.666666666666671

    def test_init_function(self):
        """Tests the __init__ function of StatsCalc to be sure appropriate exceptgions are raised for invalid args"""
        exception_raised = False
        try:
            StatsCalc(0, ["2"])
        except StatsCalcException:
            exception_raised = True
        assert exception_raised

        exception_raised = False

        try:
            StatsCalc(["2"], 0)
        except StatsCalcException:
            exception_raised = True

        assert exception_raised

        stats_ob = StatsCalc(self._y_true_multi, self._y_pred_multi_no_ukn)
        self.assertIsInstance(stats_ob, StatsCalc)
        stats_ob = StatsCalc(self._y_true_binary, self._y_pred_binary_no_ukn)
        self.assertIsInstance(stats_ob, StatsCalc)

    def test_accuracy_calc(self):
        """Tests the accuracy calculation for binary and multi class confusion matrices"""
        self.assertAlmostEqual(
            self._desired_acc_binary_no_ukn, self.bin_obj_no_ukn.calc_accuracy()
        )
        self.assertAlmostEqual(
            self._desired_acc_binary_ukn, self.bin_obj_ukn.calc_accuracy()
        )
        self.assertAlmostEqual(
            self._desired_acc_multi_no_ukn, self.multi_obj_no_ukn.calc_accuracy()
        )
        self.assertAlmostEqual(
            self._desired_acc_multi_ukn, self.multi_obj_ukn.calc_accuracy()
        )

    def test_sensitivity_calc(self):
        """Tests the average sensitivity calculation for binary and multi class confusion matrices"""
        for key in self._desired_se_binary_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_se_binary_no_ukn[key],
                self.bin_obj_no_ukn.calc_sensitivity()[key],
            )
            self.assertAlmostEqual(
                self._desired_se_binary_ukn[key],
                self.bin_obj_ukn.calc_sensitivity()[key],
            )
        for key in self._desired_se_multi_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_se_multi_no_ukn[key],
                self.multi_obj_no_ukn.calc_sensitivity()[key],
            )
            self.assertAlmostEqual(
                self._desired_se_multi_ukn[key],
                self.multi_obj_ukn.calc_sensitivity()[key],
            )

    def test_avg_pp_calc(self):
        """Tests the average positive predictivity calculation for binary and multi class confusion matrices"""
        for key in self._desired_pp_binary_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_pp_binary_no_ukn[key],
                self.bin_obj_no_ukn.calc_positive_predictive_rate()[key],
            )
            self.assertAlmostEqual(
                self._desired_pp_binary_ukn[key],
                self.bin_obj_ukn.calc_positive_predictive_rate()[key],
            )
        for key in self._desired_pp_multi_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_pp_multi_no_ukn[key],
                self.multi_obj_no_ukn.calc_positive_predictive_rate()[key],
            )
            self.assertAlmostEqual(
                self._desired_pp_multi_ukn[key],
                self.multi_obj_ukn.calc_positive_predictive_rate()[key],
            )

    @pytest.mark.skip("TO BE FIXED")
    def test_specificity_calc(self):
        """Tests the specificity calculation for binary and multi class confusion matrices"""
        self.assertAlmostEqual(
            self._desired_spec_binary_no_ukn, self.bin_obj_no_ukn.calc_specificity()
        )
        self.assertAlmostEqual(
            self._desired_spec_binary_ukn, self.bin_obj_ukn.calc_specificity()
        )
        assert (self.multi_obj_no_ukn.calc_specificity()) is None
        assert (self.multi_obj_ukn.calc_specificity()) is None

    def test_precision_calc(self):
        """Tests the precision calculation for binary and multi class confusion matrices"""
        for key in self._desired_prec_binary_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_prec_binary_no_ukn[key],
                self.bin_obj_no_ukn.calc_precision()[key],
            )
            self.assertAlmostEqual(
                self._desired_prec_binary_ukn[key],
                self.bin_obj_ukn.calc_precision()[key],
            )
        for key in self._desired_prec_multi_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_prec_multi_no_ukn[key],
                self.multi_obj_no_ukn.calc_precision()[key],
            )
            self.assertAlmostEqual(
                self._desired_prec_multi_ukn[key],
                self.multi_obj_ukn.calc_precision()[key],
            )

    def test_f1_score_calc(self):
        """Tests the f1 score calculation for binary and multi class confusion matrices"""
        for key in self._desired_f1_binary_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_f1_binary_no_ukn[key],
                self.bin_obj_no_ukn.calc_f1_score()[key],
            )
            self.assertAlmostEqual(
                self._desired_f1_binary_ukn[key], self.bin_obj_ukn.calc_f1_score()[key]
            )

        for key in self._desired_f1_multi_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_f1_multi_no_ukn[key],
                self.multi_obj_no_ukn.calc_f1_score()[key],
            )
            self.assertAlmostEqual(
                self._desired_f1_multi_ukn[key], self.multi_obj_ukn.calc_f1_score()[key]
            )

    @pytest.mark.skip("TO BE FIXED")
    def test_get_metric_set(self):
        """tests the get metric set functionality of the metrics library
        Performs all of the calculations at once, and ensures the metrics object has correctly assigned the results
        to an appropriate dictionary"""
        self.bin_obj_no_ukn.calc_all_metrics()
        self.bin_obj_ukn.calc_all_metrics()
        self.multi_obj_no_ukn.calc_all_metrics()
        self.multi_obj_ukn.calc_all_metrics()

        for key in self._desired_f1_binary_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_f1_binary_no_ukn[key], self.bin_obj_no_ukn.f1_score[key]
            )
            self.assertAlmostEqual(
                self._desired_f1_binary_ukn[key], self.bin_obj_ukn.f1_score[key]
            )

        for key in self._desired_f1_multi_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_f1_multi_no_ukn[key], self.multi_obj_no_ukn.f1_score[key]
            )
            self.assertAlmostEqual(
                self._desired_f1_multi_ukn[key], self.multi_obj_ukn.f1_score[key]
            )

        for key in self._desired_prec_binary_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_prec_binary_no_ukn[key],
                self.bin_obj_no_ukn.precision[key],
            )
            self.assertAlmostEqual(
                self._desired_prec_binary_ukn[key], self.bin_obj_ukn.precision[key]
            )

        for key in self._desired_prec_multi_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_prec_multi_no_ukn[key],
                self.multi_obj_no_ukn.precision[key],
            )
            self.assertAlmostEqual(
                self._desired_prec_multi_ukn[key], self.multi_obj_ukn.precision[key]
            )

        self.assertAlmostEqual(
            self._desired_spec_binary_no_ukn, self.bin_obj_no_ukn.specificity
        )
        self.assertAlmostEqual(
            self._desired_spec_binary_ukn, self.bin_obj_ukn.specificity
        )
        assert self.multi_obj_no_ukn.specificity
        assert self.multi_obj_ukn.specificity

        for key in self._desired_pp_binary_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_pp_binary_no_ukn[key],
                self.bin_obj_no_ukn.positive_predictive_rate[key],
            )
            self.assertAlmostEqual(
                self._desired_pp_binary_ukn[key],
                self.bin_obj_ukn.positive_predictive_rate[key],
            )

        for key in self._desired_pp_multi_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_pp_multi_no_ukn[key],
                self.multi_obj_no_ukn.positive_predictive_rate[key],
            )
            self.assertAlmostEqual(
                self._desired_pp_multi_ukn[key],
                self.multi_obj_ukn.positive_predictive_rate[key],
            )

        for key in self._desired_se_binary_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_se_binary_no_ukn[key],
                self.bin_obj_no_ukn.sensitivity[key],
            )
            self.assertAlmostEqual(
                self._desired_se_binary_ukn[key], self.bin_obj_ukn.sensitivity[key]
            )

        for key in self._desired_se_multi_no_ukn.keys():
            self.assertAlmostEqual(
                self._desired_se_multi_no_ukn[key],
                self.multi_obj_no_ukn.sensitivity[key],
            )
            self.assertAlmostEqual(
                self._desired_se_multi_ukn[key], self.multi_obj_ukn.sensitivity[key]
            )

        self.assertAlmostEqual(
            self._desired_acc_binary_no_ukn, self.bin_obj_no_ukn.accuracy
        )
        self.assertAlmostEqual(self._desired_acc_binary_ukn, self.bin_obj_ukn.accuracy)
        self.assertAlmostEqual(
            self._desired_acc_multi_no_ukn, self.multi_obj_no_ukn.accuracy
        )
        self.assertAlmostEqual(self._desired_acc_multi_ukn, self.multi_obj_ukn.accuracy)


def test_with_unknown():

    stats_obj = StatsCalc(
        [1, 1, 1, 0, 0, 0, 13, 13, 13],
        [1, 1, 1, 0, 0, 13, 13, 0, 0],
        class_map={"Unknown": 13, "label": 1},
    )

    stats_obj.calc_all_metrics()
    expected_metric = {1: 100.0, "average": 100.0}

    assert stats_obj.accuracy == 100
    assert stats_obj.sensitivity == expected_metric
    assert stats_obj.positive_predictive_rate == expected_metric
    assert stats_obj.f1_score == expected_metric
    assert stats_obj.precision == expected_metric
