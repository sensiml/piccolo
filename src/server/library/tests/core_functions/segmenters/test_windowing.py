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

import numpy as np
import pandas as pd
from datamanager.datasegments import DataSegments, dataframe_to_datasegments
from library.core_functions.segmenters.sg_windowing import sg_windowing


class TestWindowingSegmenter:
    """Test windowing segmentation algorithm."""

    def test_windowing(self):
        params = {
            "group_columns": ["Label"],
            "delta": 100,
            "window_size": 100,
            "return_segment_index": True,
        }

        df = DataSegments(sg_windowing(build_test_data(), **params)).to_dataframe()

        seg_beg_end_list = parse_beg_end(df)

        ground_data = get_ground_data(
            range(0, 101, params["delta"]),
            range(params["window_size"], 101, params["delta"]),
        )

        assert ground_data == seg_beg_end_list

    def test_windowing_train_delta_large(self):
        params = {
            "group_columns": ["Label"],
            "delta": 100,
            "enable_train_delta": True,
            "train_delta": 50,
            "window_size": 25,
            "return_segment_index": True,
        }

        passed = False

        try:
            DataSegments(sg_windowing(build_test_data(), **params)).to_dataframe()
        except:
            passed = True

        assert passed

    def test_windowing_delta_small(self):
        params = {
            "group_columns": ["Label"],
            "delta": 5,
            "window_size": 10,
            "return_segment_index": True,
        }

        df = DataSegments(sg_windowing(build_test_data(), **params)).to_dataframe()

        seg_beg_end_list = parse_beg_end(df)

        ground_data = get_ground_data(
            range(0, 101 - params["window_size"], params["delta"]),
            range(params["window_size"], 101, params["delta"]),
        )

        assert ground_data == seg_beg_end_list

    def test_windowing_delta_small_data(self):
        params = {
            "group_columns": ["Label"],
            "delta": 5,
            "window_size": 10,
            "return_segment_index": False,
        }

        df = DataSegments(sg_windowing(build_test_data(), **params)).to_dataframe()

        window_data = []
        for i in range(0, len(df.AccelerometerX), 10):
            window_data.append(list(df.AccelerometerX.values[i : i + 10]))

        ground_data = [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            [10.0, 10.0, 10.0, 10.0, 10.0, 20.0, 20.0, 20.0, 20.0, 20.0],
            [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],
            [20.0, 20.0, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0, 30.0, 30.0],
            [30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0],
            [30.0, 30.0, 30.0, 30.0, 30.0, 40.0, 40.0, 40.0, 40.0, 40.0],
            [40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0],
            [40.0, 40.0, 40.0, 40.0, 40.0, 50.0, 50.0, 50.0, 50.0, 50.0],
            [50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
            [50.0, 50.0, 50.0, 50.0, 50.0, 60.0, 60.0, 60.0, 60.0, 60.0],
            [60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0],
            [60.0, 60.0, 60.0, 60.0, 60.0, 70.0, 70.0, 70.0, 70.0, 70.0],
            [70.0, 70.0, 70.0, 70.0, 70.0, 70.0, 70.0, 70.0, 70.0, 70.0],
            [70.0, 70.0, 70.0, 70.0, 70.0, 80.0, 80.0, 80.0, 80.0, 80.0],
            [80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0],
            [80.0, 80.0, 80.0, 80.0, 80.0, 90.0, 90.0, 90.0, 90.0, 90.0],
            [90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0],
        ]

        for i in range(len(ground_data)):
            assert ground_data[i] == window_data[i]


def build_test_data():
    df = pd.DataFrame()
    df["Label"] = "A"
    df["AccelerometerX"] = np.zeros(100)
    df["Label"] = "A"
    for i in range(0, 100, 10):
        df.AccelerometerX.loc[i : i + 10] = i

    return dataframe_to_datasegments(
        df, data_columns=["AccelerometerX"], group_columns=["Label"]
    )


def parse_beg_end(df):
    beg = df.Seg_Begin.unique()
    end = df.Seg_End.unique()
    M = []
    for i in range(len(beg)):
        M.append([beg[i], end[i]])
    return M


def get_ground_data(beg, end):
    return [list(a) for a in zip(beg, end)]
