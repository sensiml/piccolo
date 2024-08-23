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
from numpy import array
from numpy.testing import assert_array_almost_equal
from pandas import DataFrame

from library.core_functions_python.sensor_transforms import (
    tr_first_derivative,
    tr_second_derivative,
)


class TestDerivative:
    """Test First and Second Derivative functions."""

    @pytest.fixture(autouse=True)
    def setup(self):

        data = DataFrame([], columns=["X", "Y", "Z"])
        data["X"] = [10, 101, 4, 55, 2, 2, 2, 24, 59, 122]
        data["Y"] = [10, 101, 4, 75, 2, 5, 2, 24, 59, 122]
        data["Z"] = [10, 101, 4, 55, 9, 2, 2, 4, 29, 122]
        self.data = data

    def test_first_derivative(self):
        """Computes derivative and tests that the result is a DataFrame with a new column."""
        derivative_data = tr_first_derivative(self.data, ["X", "Y", "Z"])
        expected = array([0, 91, -97, 51, -53, 0, 0, 22, 35, 63])

        assert type(DataFrame()) == type(derivative_data)
        assert "DerivFst_ST_0000" in derivative_data.columns
        assert_array_almost_equal(expected, derivative_data["DerivFst_ST_0000"])

    def test_second_derivative(self):
        """Computes second derivative and tests that the result is a DataFrame with a new column."""
        derivative_data = tr_second_derivative(self.data, ["X", "Y", "Z"])
        expected = array([0, 91, -188, 148, -104, 53, 0, 22, 13, 28]).astype(int)

        assert type(DataFrame()) == type(derivative_data)
        assert "DerivSec_ST_0000" in derivative_data.columns
        assert_array_almost_equal(expected, derivative_data["DerivSec_ST_0000"])
