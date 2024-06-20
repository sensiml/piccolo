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


import math


import pytest
from library.core_functions.feature_generators.fg_frequency import (
    fg_frequency_harmonic_product_spectrum,
    fg_frequency_mfe,
    fg_frequency_peak_harmonic_product_spectrum,
    fg_frequency_power_spectrum,
)
from numpy import array, int16
from pandas import DataFrame

# fmt: off
data = {'data': array([[0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024]], dtype=int16),
        'columns': ['X'],
        'metadata': ['capture_uuid', 'segment_uuid', 'Labels', 'SegmentID'],
        'Labels': 'knocking',
        'segment_uuid': 'de50edbe-d8b7-4614-91da-72f1cfc02ab3',
        'SegmentID': 32475,
        'length': 8000
        }
# fmt: on


@pytest.mark.skip("segfault")
def test_fg_frequency_power_spectrum():
    expected = [
        34.413029,
        261.124451,
        753.245178,
        259.472137,
        755.474182,
        253.716339,
        757.474182,
        255.472137,
        755.000000,
        256.002014,
        753.031982,
        255.002014,
        757.000000,
        259.236053,
        757.433105,
        25.276249,
    ]

    """Call the function and match to ground data."""
    columns = ["X"]

    result = fg_frequency_power_spectrum(data, columns, "hanning", 16)

    assert type(DataFrame()) == type(result)

    assert [int(x) for x in expected] == result.values.astype(int).tolist()[0]


def test_fg_frequency_mfe():
    # fmt: off


    expected = [102336., 101943., 101581., 102738., 102976., 104083., 107427.,
        127885., 123949., 104367., 106126., 129376., 133437., 106142.,
        131855., 136643., 113349., 139423., 132547., 140732., 139241.,
        140372., 141620]
    # fmt: on

    """Call the function and match to ground data."""
    columns = ["X"]

    result = fg_frequency_mfe(data, columns, 23)

    assert type(DataFrame()) == type(result)

    assert [int(x) for x in expected] == result.values.astype(int).tolist()[0]


def test_fg_frequency_harmonic_product_spectrum():
    # fmt: off


    expected = [0.0, 72.0, 8.0, 8.0, 0.0, 1.0, 0.0, 4.0, 0.0, 2.0, 0.0, 13016.0, 0.0, 0.0, 0.0, 12.0, 0.0, 6.0, 0.0, 8.0, 0.0, 1628.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 4.0, 0.0, 19500.0, 110983867531264.0, 16270.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 0.0]
    # fmt: on

    """Call the function and match to ground data."""
    columns = ["X"]

    result = fg_frequency_harmonic_product_spectrum(data, columns, 5)

    assert type(DataFrame()) == type(result)

    assert expected == result.values.tolist()[0]


def test_fg_frequency_peak_harmonic_product_spectrum():
    # fmt: off
    expected = [32.0, 1907606528.0]
    # fmt: on

    """Call the function and match to ground data."""
    columns = ["X"]

    result = fg_frequency_peak_harmonic_product_spectrum(data, columns, 5)

    assert type(DataFrame()) == type(result)

    assert expected == result.values.tolist()[0]
