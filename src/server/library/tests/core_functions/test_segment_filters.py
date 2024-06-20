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
from copy import deepcopy

import numpy as np
import pytest
from datamanager.datasegments import (
    DataSegments,
    dataframe_to_datasegments,
    datasegments_equal,
)
from library.core_functions.segment_filters import (
    sg_filter_energy_threshold,
    sg_filter_peak_ratio_energy_threshold,
    sg_filter_mse,
    sg_filter_threshold,
)
from pandas import DataFrame, read_csv

A = [
    0,
    100,
    1000,
    2000,
    1000,
    100,
    0,
    100,
    1000,
    2000,
]
B = [
    0,
    -100,
    -1000,
    -2000,
    -1000,
    -100,
    0,
    -100,
    -1000,
    -2000,
]
C = [
    0,
    -100,
    -1000,
    -2000,
    -1000,
    -100,
    0,
    100,
    1000,
    2000,
]


class TestSGFilterThreshold:
    """Test function segment filter threshold function"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a dataset"""

        segments = [[x] * len(A) for x in range(3)]
        flat_segments = [item for sublist in segments for item in sublist]

        self.data = dataframe_to_datasegments(
            DataFrame({"Ax": A + B + C, "SegmentID": flat_segments}),
            group_columns=["SegmentID"],
            data_columns=["Ax"],
        )
        self.input_columns = "Ax"
        self.group_columns = ["SegmentID"]

    def test_sg_filter_threshold_filter_all(self):
        # positive and negative values

        input_data = deepcopy(self.data)

        results = sg_filter_threshold(
            input_data,
            self.input_columns,
            self.group_columns,
            threshold=0,
            comparison=0,
        )

        assert len(results) == 0

        input_data = deepcopy(self.data)

        results = sg_filter_threshold(
            input_data,
            self.input_columns,
            self.group_columns,
            threshold=0,
            comparison=1,
        )
        assert len(results) == 0

    def test_sg_filter_threshold_none(self):

        input_data = deepcopy(self.data)

        results = sg_filter_threshold(
            input_data,
            self.input_columns,
            self.group_columns,
            threshold=3000,
            comparison=0,
        )
        datasegments_equal(results, self.data)

        results = sg_filter_threshold(
            input_data,
            self.input_columns,
            self.group_columns,
            threshold=-3000,
            comparison=1,
        )

        datasegments_equal(results, self.data)

    def test_sg_filter_threshold_some(self):

        input_data = deepcopy(self.data)

        results = DataSegments(
            sg_filter_threshold(
                input_data,
                self.input_columns,
                self.group_columns,
                threshold=2000,
                comparison=0,
            )
        ).to_dataframe()

        expected_results = DataFrame({"Ax": B, "SegmentID": [1] * len(B)})

        assert np.array_equal(results.values, expected_results.values)

        results = DataSegments(
            sg_filter_threshold(
                input_data,
                self.input_columns,
                self.group_columns,
                threshold=-2000,
                comparison=1,
            )
        ).to_dataframe()
        expected_results = DataFrame({"Ax": A, "SegmentID": [0] * len(A)})

        assert np.array_equal(results.values, expected_results.values)


class TestSGMSEFilter:
    """Test function segment filter threshold function"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a dataset"""

        segments = [[x] * len(A) for x in range(3)]
        flat_segments = [item for sublist in segments for item in sublist]

        self.data = dataframe_to_datasegments(
            DataFrame({"Ax": A + B + C, "SegmentID": flat_segments}),
            data_columns=["Ax"],
            group_columns=["SegmentID"],
        )
        self.input_columns = "Ax"
        self.group_columns = ["SegmentID"]

    def test_sg_filter_mse_all(self):
        # positive and negative values

        input_data = deepcopy(self.data)

        results = DataSegments(
            sg_filter_mse(
                input_data,
                self.input_columns,
                self.group_columns,
                MSE_target=100,
                MSE_threshold=1130000,
            )
        ).to_dataframe()

        expected_results = DataFrame(
            {"Ax": B + C, "SegmentID": ([1] * len(B)) + ([2] * len(C))}
        )

        assert np.array_equal(results.values, expected_results.values)


def test_sg_filter_energy_threshold():

    data = dataframe_to_datasegments(
        read_csv(
            os.path.join(
                os.path.dirname(__file__), "data", "sg_filter_threshold_test_data.csv"
            )
        ),
        group_columns=["SegmentID"],
        data_columns=["channel_0"],
    )

    results = (
        DataSegments(
            sg_filter_energy_threshold(
                data,
                "channel_0",
                group_columns=["SegmentID"],
                threshold=90,
            )
        )
        .to_dataframe()
        .SegmentID.unique()
        .tolist()
    )

    expected_results = [0, 2, 3]

    assert results == expected_results


def test_sg_filter_peak_ratio_energy_threshold():

    data = dataframe_to_datasegments(
        read_csv(
            os.path.join(
                os.path.dirname(__file__), "data", "sg_filter_threshold_test_data.csv"
            )
        ),
        group_columns=["SegmentID"],
        data_columns=["channel_0"],
    )

    results = (
        DataSegments(
            sg_filter_peak_ratio_energy_threshold(
                data,
                "channel_0",
                group_columns=["SegmentID"],
                upper_threshold=90,
                lower_threshold=20,
                peak_to_average_limit=20,
            )
        )
        .to_dataframe()
        .SegmentID.unique()
        .tolist()
    )

    expected_results = [0, 2, 3]
    assert results == expected_results

    results = (
        DataSegments(
            sg_filter_peak_ratio_energy_threshold(
                data,
                "channel_0",
                group_columns=["SegmentID"],
                upper_threshold=1000,
                lower_threshold=200,
                peak_to_average_limit=0,
            )
        )
        .to_dataframe()
        .SegmentID.unique()
        .tolist()
    )

    expected_results = [3]
    assert results == expected_results

    results = (
        DataSegments(
            sg_filter_peak_ratio_energy_threshold(
                data,
                "channel_0",
                group_columns=["SegmentID"],
                upper_threshold=1000,
                lower_threshold=50,
                peak_to_average_limit=1,
            )
        )
        .to_dataframe()
        .SegmentID.unique()
        .tolist()
    )

    expected_results = [0, 3]
    assert results == expected_results
