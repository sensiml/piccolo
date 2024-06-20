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
from numpy.testing import assert_array_almost_equal
from pandas import DataFrame, concat

from library.core_functions_python.tr_threshold_crossing_filter import (
    tr_threshold_crossing_filter,
)


class TestThresholdCrossing:
    """Test Threshold Crossing filter."""

    @pytest.fixture(autouse=True)
    def setup(self):
        a = DataFrame(list(range(-5, 5)), columns=["A"])
        b = DataFrame(list(range(5, 15)), columns=["B"])
        self.data = concat([a, b], axis=1)
        self.data["Subject"] = 1

    def test_threshold_crossing_transform_one_group(self):
        """Apply threshold crossing filter to a test set that has a crossing."""
        filtered_data = tr_threshold_crossing_filter(self.data, ["Subject"], "A")
        assert_array_almost_equal(self.data, filtered_data)

    def test_threshold_crossing_transform_no_groups(self):
        """Apply threshold crossing filter to a test set that does not have a crossing."""
        try:
            tr_threshold_crossing_filter(self.data, ["Subject"], "B")
            assert False
        except Exception:
            assert True
