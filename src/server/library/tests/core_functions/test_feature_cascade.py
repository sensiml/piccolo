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

import numpy as np
import pandas as pd
import pytest
from library.core_functions.feature_cascade import (
    FeatureCascadeException,
    feature_cascade,
)


def test_feature_cascade_slide_false():
    params = {
        "group_columns": ["Label", "SegmentID", "segment_uuid"],
        "num_cascades": 5,
        "training_slide": False,
    }

    df, feature_table = feature_cascade(build_test_data(), None, **params)

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(__file__), "data", "feature_cascade_slide_false.csv"
        )
    )
    features = [gen for gen in expected_results.columns if gen[:4] == "gen_"]
    expected_results[features] = expected_results[features].astype(np.float32)

    assert sorted(df.columns) == sorted(expected_results.columns)

    pd.testing.assert_frame_equal(df, expected_results[df.columns])


def test_feature_cascade_slide_true():
    params = {
        "group_columns": ["Label", "SegmentID", "segment_uuid"],
        "num_cascades": 5,
        "training_slide": True,
        "training_delta": 1,
    }

    df, feature_table = feature_cascade(build_test_data(), None, **params)

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(__file__), "data", "feature_cascade_slide_true.csv"
        )
    )

    features = [gen for gen in expected_results.columns if gen[:4] == "gen_"]
    expected_results[features] = expected_results[features].astype(np.float32)

    assert sorted(df.columns) == sorted(expected_results.columns)

    pd.testing.assert_frame_equal(df, expected_results[df.columns])


def test_feature_cascade_slide_true_delta_5():
    params = {
        "group_columns": ["Label", "SegmentID", "segment_uuid"],
        "num_cascades": 5,
        "training_slide": True,
        "training_delta": 5,
    }

    df, feature_table = feature_cascade(build_test_data(), None, **params)

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(__file__), "data", "feature_cascade_slide_true_delta_5.csv"
        )
    )

    features = [gen for gen in expected_results.columns if gen[:4] == "gen_"]
    expected_results[features] = expected_results[features].astype(np.float32)

    assert sorted(df.columns) == sorted(expected_results.columns)

    pd.testing.assert_frame_equal(df, expected_results[df.columns])


def test_feature_cascade_new_test():
    params = {
        "group_columns": ["Label", "SegmentID"],
        "num_cascades": 2,
        "slide": True,
        "training_slide": True,
        "training_delta": 1,
    }

    input_data = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "test_feature_cascade_data.csv")
    )

    df, feature_table = feature_cascade(input_data, None, **params)

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(__file__), "data", "test_feature_cascade_new_test.csv"
        )
    )

    features = [gen for gen in expected_results.columns if gen[:4] == "gen_"]
    expected_results[features] = expected_results[features].astype(np.float32)

    assert sorted(df.columns) == sorted(expected_results.columns)

    pd.testing.assert_frame_equal(df, expected_results[df.columns])


def test_feature_cascade_slide_true_delta_2():
    params = {
        "group_columns": ["Label", "SegmentID", "segment_uuid"],
        "num_cascades": 5,
        "training_slide": True,
        "training_delta": 2,
    }

    df, feature_table = feature_cascade(build_test_data(), None, **params)

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(__file__), "data", "feature_cascade_slide_true_delta_2.csv"
        )
    )

    features = [gen for gen in expected_results.columns if gen[:4] == "gen_"]
    expected_results[features] = expected_results[features].astype(np.float32)

    assert sorted(df.columns) == sorted(expected_results.columns)

    pd.testing.assert_frame_equal(df, expected_results[df.columns])


def test_feature_cascade_slide_true_single_metadata():
    params = {
        "group_columns": ["Label", "SegmentID"],
        "num_cascades": 5,
        "training_slide": True,
        "training_delta": 1,
    }
    test_data = build_test_data()
    test_data = test_data[test_data.segment_uuid == 19].drop("segment_uuid", axis=1)
    df, feature_table = feature_cascade(test_data, None, **params)

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(__file__),
            "data",
            "feature_cascade_slide_true_single_metadata.csv",
        )
    )
    features = [gen for gen in expected_results.columns if gen[:4] == "gen_"]
    expected_results[features] = expected_results[features].astype(np.float32)

    assert sorted(df.columns) == sorted(expected_results.columns)

    pd.testing.assert_frame_equal(df, expected_results[df.columns])


def test_feature_cascade_slide_true_dropped_middle():
    params = {
        "group_columns": ["Label", "SegmentID", "segment_uuid"],
        "num_cascades": 5,
        "training_slide": True,
        "training_delta": 1,
    }

    df = build_test_data(dtype=np.int32)

    df, feature_table = feature_cascade(
        df[df.SegmentID != 2].reset_index(drop=True), None, **params
    )

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(__file__),
            "data",
            "feature_cascade_slide_dropped_middle.csv",
        )
    )
    features = [gen for gen in expected_results.columns if gen[:4] == "gen_"]
    expected_results[features] = expected_results[features].astype(dtype=np.int32)

    assert sorted(df.columns) == sorted(expected_results.columns)

    pd.testing.assert_frame_equal(df, expected_results[df.columns])


def test_feature_cascade_too_large():
    params = {
        "group_columns": ["Label", "SegmentID", "segment_uuid"],
        "num_cascades": 11,
        "training_slide": True,
        "training_delta": 1,
    }

    df = build_test_data()

    raised_exception = False

    try:
        df, feature_table = feature_cascade(
            df[df.SegmentID != 2].reset_index(drop=True), None, **params
        )
    except FeatureCascadeException:
        raised_exception = True

    assert raised_exception


@pytest.mark.skip("used for profiling")
def test_feature_cascade_slide_true_profile():
    import time

    params = {
        "group_columns": ["Labels", "SegmentID", "segment_uuid", "capture_uuid"],
        "num_cascades": 5,
        "training_slide": True,
        "training_delta": 1,
    }

    # test_data = build_test_data(length=20, delta=20, num_features=20)

    test_data = pd.read_csv(
        "~/server_data/datamanager/pipelinecache/2fbf4863-c5b8-45e1-8e52-04050158f9b3/temp.generator_set0.data_0.csv.gz",
        sep="\t",
    )

    start = time.time()

    df, feature_table = feature_cascade(test_data, None, **params)

    expected_results = None
    runtime = time.time() - start
    print(runtime)

    assert sorted(df.columns) == sorted(expected_results.columns)

    pd.testing.assert_frame_equal(df, expected_results[df.columns])


def build_test_data(length=200, delta=10, num_features=2, dtype=np.float32):
    df = pd.DataFrame()
    df["Label"] = "A"
    for index in range(num_features):
        df["gen_{:0>4}".format(index + 1)] = np.zeros(length, dtype=dtype)
    df["Label"] = "A"
    df["SegmentID"] = np.zeros(length, dtype=int)
    df["segment_uuid"] = np.zeros(length, dtype=int)

    half_point = length // 2

    counter = 0
    for i in range(0, length, delta):
        df.segment_uuid.loc[i : i + delta] = counter
        for j in range(delta):
            df.SegmentID.loc[i + j] = j
        counter += 1

    for i in range(0, half_point, delta):
        for index in range(num_features):
            if index % 2 == 0:
                df["gen_{:0>4}".format(index + 1)].loc[i : i + delta] = i
            else:
                df["gen_{:0>4}".format(index + 1)].loc[i : i + delta] = -i

    for i in range(half_point, length, delta):
        for index in range(num_features):
            if index % 2 == 0:
                df["gen_{:0>4}".format(index + 1)].loc[i : i + delta] = i - half_point
            else:
                df["gen_{:0>4}".format(index + 1)].loc[i : i + delta] = -(
                    i - half_point
                )

    return df
