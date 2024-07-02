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


import os

from library.core_functions.selectors import correlation_select_remove_most_corr_first
from pandas import DataFrame, read_csv


class TestcorrSelectMostCorr:
    """Test Trim function."""

    def assertEqual(self, a, b):
        assert a == b

    def test_correlation_select_remove_most_corr_first(self):
        """calling the function"""

        self.data = read_csv(
            os.path.join(os.path.dirname(__file__), "data", "example_features.csv")
        )

        self.data["IgnoreThis"] = "twenty"

        odf, f_reject = correlation_select_remove_most_corr_first(
            self.data, 0.95, ["0", "1", "130"]
        )

        f_reject_expected = [
            "48",
            "45",
            "73",
            "47",
            "77",
            "80",
            "81",
            "39",
            "79",
            "49",
            "75",
            "51",
            "71",
            "43",
            "82",
            "46",
            "78",
            "44",
            "50",
            "83",
            "76",
            "67",
            "40",
            "55",
            "66",
            "70",
            "84",
            "72",
            "56",
            "36",
            "52",
            "38",
            "65",
            "69",
            "37",
            "63",
            "41",
            "58",
            "74",
            "53",
            "86",
            "42",
            "90",
            "68",
            "64",
            "59",
        ]

        self.assertEqual(type(DataFrame()), type(odf))
        self.assertEqual((275, 68), odf.shape)
        self.assertEqual(46, len(f_reject))
        self.assertEqual(f_reject_expected, f_reject)
