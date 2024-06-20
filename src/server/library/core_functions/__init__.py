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

MIN_INT_16 = -32768
MAX_INT_16 = 32767
import numpy as np


def fix_overflow(input_data, col_indexes):
    for index in col_indexes:
        input_data[index][np.where(input_data[index] >= MAX_INT_16)] = MAX_INT_16
        input_data[index][np.where(input_data[index] <= MIN_INT_16)] = MIN_INT_16


def fix_rounding(input_data, col_indexes):
    input_data[col_indexes] = np.apply_along_axis(
        lambda x: (x + np.sign(x) * 0.5).astype(np.int32), 1, input_data[col_indexes]
    )


def c_round_array(input_data):
    np.apply_along_axis(
        lambda x: (x + np.sign(x) * 0.5).astype(np.int32), 1, col_indexes
    )


def c_round_value(value):
    return np.int32(value + np.sign(value) * 0.5)
