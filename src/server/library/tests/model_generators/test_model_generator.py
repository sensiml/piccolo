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

import logging

import pytest
from library.model_generators import model_generator
from pandas import DataFrame

logger = logging.getLogger(__name__)


@pytest.fixture
def data():
    return DataFrame(
        [
            [249, 253, 253, 1],
            [251, 253, 253, 1],
            [253, 253, 254, 1],
            [254, 254, 254, 1],
            [254, 254, 253, 1],
            [254, 254, 252, 1],
            [253, 253, 252, 1],
            [250, 252, 252, 1],
            [252, 253, 252, 1],
            [251, 252, 253, 1],
            [250, 252, 253, 1],
            [253, 252, 252, 1],
            [252, 252, 253, 1],
            [250, 252, 252, 1],
            [254, 254, 252, 1],
            [253, 254, 252, 1],
            [253, 254, 252, 1],
            [1, 2, 1, 2],
            [2, 3, 1, 2],
            [0, 3, 1, 2],
            [0, 0, 1, 2],
            [7, 1, 0, 2],
            [8, 0, 1, 2],
            [8, 0, 0, 2],
            [7, 0, 1, 2],
            [5, 1, 1, 2],
            [5, 2, 1, 2],
            [5, 4, 1, 2],
            [5, 4, 0, 2],
            [6, 2, 0, 2],
            [7, 2, 0, 2],
            [8, 0, 0, 2],
            [10, 0, 1, 2],
            [10, 0, 1, 2],
            [85, 89, 86, 3],
            [84, 90, 87, 3],
            [81, 88, 86, 3],
            [80, 88, 87, 3],
            [79, 87, 89, 3],
            [81, 86, 88, 3],
            [84, 85, 88, 3],
            [88, 86, 87, 3],
            [89, 86, 86, 3],
            [90, 86, 87, 3],
            [90, 88, 87, 3],
            [88, 87, 88, 3],
            [85, 89, 87, 3],
            [84, 89, 87, 3],
            [83, 88, 87, 3],
            [86, 88, 87, 3],
            [91, 88, 88, 3],
        ],
        columns=[
            "gen_0001_AccelerometerXSum",
            "gen_0002_AccelerometerYSum",
            "gen_0003_AccelerometerZSum",
            "Label",
        ],
    )


class TestModelGenerator:
    def setup_model(self, data):
        return data

    def test_compute_feature_stats(self, data):
        feature_stats = model_generator.compute_feature_stats(data)

        expected_result = {
            "gen_0001_AccelerometerXSum": {
                1: {
                    "count": 17.0,
                    "mean": 252.12,
                    "std": 1.65,
                    "min": 249.0,
                    "4.5%": 249.72,
                    "25%": 251.0,
                    "50%": 253.0,
                    "75%": 253.0,
                    "95.5%": 254.0,
                    "max": 254.0,
                    "median": 253.0,
                    "outlier": [249],
                },
                2: {
                    "count": 17.0,
                    "mean": 5.53,
                    "std": 3.16,
                    "min": 0.0,
                    "4.5%": 0.0,
                    "25%": 5.0,
                    "50%": 6.0,
                    "75%": 8.0,
                    "95.5%": 10.0,
                    "max": 10.0,
                    "median": 6.0,
                    "outlier": [],
                },
                3: {
                    "count": 17.0,
                    "mean": 85.18,
                    "std": 3.71,
                    "min": 79.0,
                    "4.5%": 79.72,
                    "25%": 83.0,
                    "50%": 85.0,
                    "75%": 88.0,
                    "95.5%": 90.28,
                    "max": 91.0,
                    "median": 85.0,
                    "outlier": [79, 91],
                },
            },
            "gen_0002_AccelerometerYSum": {
                1: {
                    "count": 17.0,
                    "mean": 253.0,
                    "std": 0.87,
                    "min": 252.0,
                    "4.5%": 252.0,
                    "25%": 252.0,
                    "50%": 253.0,
                    "75%": 254.0,
                    "95.5%": 254.0,
                    "max": 254.0,
                    "median": 253.0,
                    "outlier": [],
                },
                2: {
                    "count": 17.0,
                    "mean": 1.41,
                    "std": 1.46,
                    "min": 0.0,
                    "4.5%": 0.0,
                    "25%": 0.0,
                    "50%": 1.0,
                    "75%": 2.0,
                    "95.5%": 4.0,
                    "max": 4.0,
                    "median": 1.0,
                    "outlier": [],
                },
                3: {
                    "count": 17.0,
                    "mean": 87.53,
                    "std": 1.37,
                    "min": 85.0,
                    "4.5%": 85.72,
                    "25%": 86.0,
                    "50%": 88.0,
                    "75%": 88.0,
                    "95.5%": 89.28,
                    "max": 90.0,
                    "median": 88.0,
                    "outlier": [85, 90],
                },
            },
            "gen_0003_AccelerometerZSum": {
                1: {
                    "count": 17.0,
                    "mean": 252.59,
                    "std": 0.71,
                    "min": 252.0,
                    "4.5%": 252.0,
                    "25%": 252.0,
                    "50%": 252.0,
                    "75%": 253.0,
                    "95.5%": 254.0,
                    "max": 254.0,
                    "median": 252.0,
                    "outlier": [],
                },
                2: {
                    "count": 17.0,
                    "mean": 0.65,
                    "std": 0.49,
                    "min": 0.0,
                    "4.5%": 0.0,
                    "25%": 0.0,
                    "50%": 1.0,
                    "75%": 1.0,
                    "95.5%": 1.0,
                    "max": 1.0,
                    "median": 1.0,
                    "outlier": [],
                },
                3: {
                    "count": 17.0,
                    "mean": 87.18,
                    "std": 0.81,
                    "min": 86.0,
                    "4.5%": 86.0,
                    "25%": 87.0,
                    "50%": 87.0,
                    "75%": 88.0,
                    "95.5%": 88.28,
                    "max": 89.0,
                    "median": 87.0,
                    "outlier": [89],
                },
            },
        }

        print(feature_stats)

        assert feature_stats == expected_result
