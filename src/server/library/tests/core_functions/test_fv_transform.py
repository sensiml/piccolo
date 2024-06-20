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



import time

import pytest
from library.core_functions.feature_transforms import min_max_scale
from pandas import DataFrame, read_csv


class TestMinMaxScale:
    """Test function."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a"""

        data_list = {
            "gen_0001_Ax_signal_bin_000000": {
                0: -100,
                1: -100,
                2: -100,
                3: -100,
                4: -100,
            },
            "gen_0001_Ax_signal_bin_000001": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0001_Ax_signal_bin_000002": {0: 100, 1: 100, 2: 100, 3: 100, 4: 100},
            "Label": {0: "ring", 1: "ring", 2: "ring", 3: "ring", 4: "ring"},
            "SegmentID": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }

        data_list_2 = {
            "gen_0001_Ax_signal_bin_000000": {
                0: -100,
                1: -100,
                2: -100,
                3: -100,
                4: -100,
            },
            "gen_0001_Ax_signal_bin_000001": {0: 0, 1: 100, 2: -100, 3: 100, 4: 200},
            "gen_0001_Ax_signal_bin_000002": {0: 100, 1: 100, 2: 100, 3: 100, 4: 100},
            "Label": {0: "ring", 1: "ring", 2: "ring", 3: "ring", 4: "ring"},
            "SegmentID": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }

        self.data = DataFrame(data_list)
        self.data_2 = DataFrame(data_list_2)

    def test_min_max_scale_with_feature_min_max_defaults(self):
        """Calling ttest feature selector function"""

        result, result_scale = min_max_scale(
            self.data,
            passthrough_columns=["Label", "SegmentID"],
            min_bound=0,
            max_bound=255,
            feature_min_max_defaults={"maximum": 200, "minimum": -200},
        )
        print(result.to_dict())

        expected_result = {
            "gen_0001_Ax_signal_bin_000000": {0: 63, 1: 63, 2: 63, 3: 63, 4: 63},
            "gen_0001_Ax_signal_bin_000001": {0: 127, 1: 127, 2: 127, 3: 127, 4: 127},
            "gen_0001_Ax_signal_bin_000002": {0: 191, 1: 191, 2: 191, 3: 191, 4: 191},
            "Label": {0: "ring", 1: "ring", 2: "ring", 3: "ring", 4: "ring"},
            "SegmentID": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }

        expected_result_scale = {
            "maximums": {
                "gen_0001_Ax_signal_bin_000000": 200,
                "gen_0001_Ax_signal_bin_000001": 200,
                "gen_0001_Ax_signal_bin_000002": 200,
            },
            "minimums": {
                "gen_0001_Ax_signal_bin_000000": -200,
                "gen_0001_Ax_signal_bin_000001": -200,
                "gen_0001_Ax_signal_bin_000002": -200,
            },
        }

        assert expected_result == result.to_dict()
        assert expected_result_scale == result_scale

    def test_min_max_scale(self):
        """Calling ttest feature selector function"""

        result, result_scale = min_max_scale(
            self.data_2,
            passthrough_columns=["Label", "SegmentID"],
            min_bound=0,
            max_bound=255,
        )

        expected_result = {
            "gen_0001_Ax_signal_bin_000000": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0001_Ax_signal_bin_000001": {0: 85, 1: 170, 2: 0, 3: 170, 4: 255},
            "gen_0001_Ax_signal_bin_000002": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "Label": {0: "ring", 1: "ring", 2: "ring", 3: "ring", 4: "ring"},
            "SegmentID": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }
        expected_result_scale = {
            "maximums": {
                "gen_0001_Ax_signal_bin_000000": -100.0,
                "gen_0001_Ax_signal_bin_000001": 200.0,
                "gen_0001_Ax_signal_bin_000002": 100.0,
            },
            "minimums": {
                "gen_0001_Ax_signal_bin_000000": -100.0,
                "gen_0001_Ax_signal_bin_000001": -100.0,
                "gen_0001_Ax_signal_bin_000002": 100.0,
            },
        }

        assert expected_result == result.to_dict()
        assert expected_result_scale == result_scale

    def test_min_max_scale_with_partial_paramters(self):
        """Calling ttest feature selector function"""

        result, result_scale = min_max_scale(
            self.data_2,
            passthrough_columns=["Label", "SegmentID"],
            min_bound=0,
            max_bound=255,
            feature_min_max_parameters={
                "maximums": {
                    "gen_0001_Ax_signal_bin_000000": 100.0,
                    "gen_0001_Ax_signal_bin_000002": 100.0,
                },
                "minimums": {
                    "gen_0001_Ax_signal_bin_000000": -100.0,
                    "gen_0001_Ax_signal_bin_000002": -100.0,
                },
            },
        )

        expected_result = {
            "gen_0001_Ax_signal_bin_000000": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0001_Ax_signal_bin_000001": {0: 85, 1: 170, 2: 0, 3: 170, 4: 255},
            "gen_0001_Ax_signal_bin_000002": {0: 255, 1: 255, 2: 255, 3: 255, 4: 255},
            "Label": {0: "ring", 1: "ring", 2: "ring", 3: "ring", 4: "ring"},
            "SegmentID": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }
        expected_result_scale = {
            "maximums": {
                "gen_0001_Ax_signal_bin_000000": 100.0,
                "gen_0001_Ax_signal_bin_000002": 100.0,
                "gen_0001_Ax_signal_bin_000001": 200.0,
            },
            "minimums": {
                "gen_0001_Ax_signal_bin_000000": -100.0,
                "gen_0001_Ax_signal_bin_000002": -100.0,
                "gen_0001_Ax_signal_bin_000001": -100.0,
            },
        }

        assert expected_result == result.to_dict()
        assert expected_result_scale == result_scale

    def test_min_max_scale_with_partial_paramters_and_defaults(self):
        """Calling ttest feature selector function"""

        result, result_scale = min_max_scale(
            self.data_2,
            passthrough_columns=["Label", "SegmentID"],
            min_bound=0,
            max_bound=255,
            feature_min_max_parameters={
                "maximums": {
                    "gen_0001_Ax_signal_bin_000000": 100.0,
                    "gen_0001_Ax_signal_bin_000002": 100.0,
                },
                "minimums": {
                    "gen_0001_Ax_signal_bin_000000": -100.0,
                    "gen_0001_Ax_signal_bin_000002": -100.0,
                },
            },
            feature_min_max_defaults={"minimum": -200, "maximum": 200},
        )

        print(result.values)

        expected_result = {
            "gen_0001_Ax_signal_bin_000000": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "gen_0001_Ax_signal_bin_000001": {0: 127, 1: 191, 2: 63, 3: 191, 4: 255},
            "gen_0001_Ax_signal_bin_000002": {0: 255, 1: 255, 2: 255, 3: 255, 4: 255},
            "Label": {0: "ring", 1: "ring", 2: "ring", 3: "ring", 4: "ring"},
            "SegmentID": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }

        expected_result_scale = {
            "maximums": {
                "gen_0001_Ax_signal_bin_000000": 100.0,
                "gen_0001_Ax_signal_bin_000002": 100.0,
                "gen_0001_Ax_signal_bin_000001": 200,
            },
            "minimums": {
                "gen_0001_Ax_signal_bin_000000": -100.0,
                "gen_0001_Ax_signal_bin_000002": -100.0,
                "gen_0001_Ax_signal_bin_000001": -200,
            },
        }

        assert expected_result == result.to_dict()
        assert expected_result_scale == result_scale

    @pytest.mark.skip("Only used for profiling")
    def test_min_max_scale_profile(self):
        """Calling ttest feature selector function"""

        csv_path = "CSV_PATH"

        start = time.time()

        df = read_csv(csv_path, sep="\t")
        print("read csv in ", time.time() - start)
        start = time.time()

        print("starting profiling")
        result, result_scale = min_max_scale(
            df,
            passthrough_columns=[
                "CascadeID",
                "Labels",
                "SegmentID",
                "capture_uuid",
                "segment_uuid",
            ],
            min_bound=0,
            max_bound=255,
            feature_min_max_defaults={"maximum": 500000.0, "minimum": -500000},
        )
        print("profiling finished ", time.time() - start)
