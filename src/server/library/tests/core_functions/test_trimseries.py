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
from pandas import DataFrame

from library.core_functions_python.segment_transforms import trimseries


class TestTrim:
    """Test Trim function."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = DataFrame(
            {
                "Subject": {
                    0: 7,
                    1: 7,
                    2: 7,
                    3: 7,
                    14: 15,
                    15: 15,
                    16: 15,
                    17: 15,
                    28: 9,
                    29: 9,
                    30: 9,
                    31: 9,
                },
                "accelx": {
                    0: -1535,
                    1: -1535,
                    2: -1539,
                    3: -1532,
                    14: -1080,
                    15: -1075,
                    16: -1053,
                    17: -1050,
                    28: -2819,
                    29: -2817,
                    30: -2815,
                    31: -2821,
                },
                "accely": {
                    0: -3577,
                    1: -3580,
                    2: -3587,
                    3: -3595,
                    14: -3475,
                    15: -3456,
                    16: -3443,
                    17: -3433,
                    28: -27,
                    29: -21,
                    30: -16,
                    31: -18,
                },
                "accelz": {
                    0: 961,
                    1: 960,
                    2: 953,
                    3: 953,
                    14: 1790,
                    15: 1794,
                    16: 1796,
                    17: 1783,
                    28: 2989,
                    29: 2991,
                    30: 2992,
                    31: 3003,
                },
            }
        )

    def test_trim_transform(self):
        """Trims input to two samples per subject and tests that the result is a DataFrame with six rows."""
        trimmed_data = trimseries(self.data, 2, "Subject")
        assert type(DataFrame()) == type(trimmed_data)
        assert 6 == len(trimmed_data)
