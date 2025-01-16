import os
from os.path import dirname, join

import numpy as np
import pandas as pd
import pytest
from numpy import array_equal
from numpy.testing import assert_array_almost_equal
from pandas.util.testing import assert_frame_equal as pd_assert_frame_equal


@pytest.fixture
def accx_accy_2_group_data():
    df = pd.DataFrame(
        [
            [
                5393,
                -6310,
            ],
            [13675, -7920],
            [18572, -10815],
            [5039, -18178],
            [4882, -3419],
            [5842, -11819],
            [9514, -19908],
            [14003, -10131],
            [5951, -4927],
            [17153, -8763],
            [
                5393,
                -6310,
            ],
            [13675, -7920],
            [18572, -10815],
            [5039, -18178],
            [4882, -3419],
            [5842, -11819],
            [9514, -19908],
            [14003, -10131],
            [5951, -4927],
            [17153, -8763],
            [-2000, 0],
            [-1500, 0],
            [-1000, 0],
            [-500, 0],
            [0, 0],
            [500, 0],
            [1000, 0],
            [1500, 0],
            [2000, 0],
            [2500, 0],
            [32768, -32768],
            [32768, -32768],
            [32768, -32768],
            [32768, -32768],
            [32768, -32768],
            [32768, -32768],
            [32768, -32768],
            [32768, -32768],
            [32768, -32768],
            [32768, -32768],
        ],
        columns=["accelx", "accely"],
    )
    df["Subject"] = "s01"
    df["Rep"] = [0] * 10 + [1] * 10 + [2] * 10 + [3] * 10

    return df


def load_ground_data(filename):
    module_path = dirname(__file__)
    return pd.read_csv(join(module_path, "data", filename))


def assert_frame_equal(df1, df2, decimal=2, scaling=None):
    """Modifies the data frames so that their column names match before testing for equality"""

    if sorted(df1.columns) != sorted(df2.columns):
        print(df1.columns)
        print(df2.columns)
        raise Exception("Columns are not the same")

    float_columns = df1.dtypes[df1.dtypes == "float64"].index.to_list()
    for column in float_columns:
        if scaling:
            assert_array_almost_equal(
                df1[column].astype(float) / scaling,
                df2[column].astype(float) / scaling,
                decimal=decimal,
            )
        else:
            assert_array_almost_equal(df1[column], df2[column], decimal=decimal)

    columns = [x for x in df1.columns if x not in float_columns]

    if not columns:
        return

    if not df1[columns].equals(df2[columns]):
        print("DATA FRAME 1")
        print(df1.values)
        print("DATA FRAME 2")
        print(df2.values)
        raise Exception("Data Frame results are not equal")


def test_dsk_pipeline_data(dsk_proj):
    dsk = dsk_proj
    df = dsk.datasets.load_activity_raw_toy()
    dsk.upload_dataframe(
        "test_data",
        df,
        force=True,
    )
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
        label_column="Class",
    )
    dsk.pipeline.add_transform(
        "Windowing",
        params={
            "group_columns": ["Subject", "Class", "Rep"],
            "window_size": 5,
            "delta": 5,
        },
    )
    results, stats = dsk.pipeline.execute()
    data, stats = dsk.pipeline.data(pipeline_step=1)

    assert_frame_equal(results, pd.DataFrame(data))

    expected_datasegment = [
        {
            "columns": ["accelx", "accely", "accelz"],
            "metadata": {
                "Class": "Crawling",
                "Rep": 1,
                "Subject": "s01",
                "SegmentID": 0,
            },
            "statistics": {},
            "data": [
                [377, 357, 333, 340, 372],
                [569, 594, 638, 678, 708],
                [4019, 4051, 4049, 4053, 4051],
            ],
        },
        {
            "columns": ["accelx", "accely", "accelz"],
            "metadata": {
                "Class": "Crawling",
                "Rep": 1,
                "Subject": "s01",
                "SegmentID": 1,
            },
            "statistics": {},
            "data": [
                [410, 450, 492, 518, 528],
                [733, 733, 696, 677, 695],
                [4028, 3988, 3947, 3943, 3988],
            ],
        },
        {
            "columns": ["accelx", "accely", "accelz"],
            "metadata": {
                "Class": "Running",
                "Rep": 1,
                "Subject": "s01",
                "SegmentID": 0,
            },
            "statistics": {},
            "data": [
                [-44, -47, -43, -40, -48],
                [-3971, -3982, -3973, -3973, -3978],
                [843, 836, 832, 834, 844],
            ],
        },
        {
            "columns": ["accelx", "accely", "accelz"],
            "metadata": {
                "Class": "Running",
                "Rep": 1,
                "Subject": "s01",
                "SegmentID": 1,
            },
            "statistics": {},
            "data": [
                [-52, -64, -64, -66, -62],
                [-3993, -3984, -3966, -3971, -3988],
                [842, 821, 813, 826, 827],
            ],
        },
    ]
    data, stats = dsk.pipeline.get_cached_data(pipeline_step=1)

    assert expected_datasegment == data


def test_sg_windowing(dsk_proj):
    dsk = dsk_proj
    df = dsk.datasets.load_activity_raw_toy()
    dsk.pipeline.reset(delete_cache=True)
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.set_input_data(
        ["test_data.csv"],
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
        label_column="Class",
    )
    dsk.pipeline.add_transform(
        "Windowing",
        params={
            "group_columns": ["Subject", "Class", "Rep"],
            "window_size": 5,
            "delta": 5,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("load_gesture_raw_toy_results.csv")
    assert_frame_equal(
        results,
        df[["Class", "Rep", "SegmentID", "Subject", "accelx", "accely", "accelz"]],
    )


def test_fg_transpose_signal(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [
            [3, 3],
            [4, 5],
            [5, 7],
            [4, 6],
            [3, 1],
            [3, 1],
            [4, 3],
            [5, 5],
            [4, 7],
            [3, 6],
        ],
        columns=["accelx", "accely"],
    )
    df["Subject"] = 1
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["accelx", "accely"], group_columns=["Subject"]
    )
    dsk.pipeline.add_feature_generator(
        ["Transpose Signal"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely"], "cutoff": 3},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_transpose_signal_result.csv")
    assert (results.values[0] == df.values[0]).all()


def test_no_data_columns(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [
            [3, 3],
            [4, 5],
            [5, 7],
            [4, 6],
            [3, 1],
            [3, 1],
            [4, 3],
            [5, 5],
            [4, 7],
            [3, 6],
        ],
        columns=["accelx", "accely"],
    )
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data("test_data.csv", data_columns=["accelx", "accely"])

    results, stats = dsk.pipeline.execute()

    assert results["status"] == "FAILURE"


def test_fg_interleave_signal(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [
            [3, 3],
            [4, 5],
            [5, 7],
            [4, 6],
            [3, 1],
            [3, 1],
            [4, 3],
            [5, 5],
            [4, 7],
            [3, 6],
        ],
        columns=["accelx", "accely"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["accelx", "accely"], group_columns=["Subject"]
    )
    dsk.pipeline.add_feature_generator(
        ["Interleave Signal"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely"], "cutoff": 3},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_interleave_signal_results.csv")
    assert_frame_equal(results, df)


def test_fg_interleave_signal_delta_pad(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [
            [3, 3],
            [4, 5],
            [5, 7],
            [4, 6],
            [3, 1],
            [3, 1],
            [4, 3],
            [5, 5],
            [4, 7],
            [3, 6],
        ],
        columns=["accelx", "accely"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["accelx", "accely"], group_columns=["Subject"]
    )
    dsk.pipeline.add_feature_generator(
        ["Interleave Signal"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely"], "cutoff": 6, "delta": 2},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_interleave_signal_delta_pad_results.csv")
    assert_frame_equal(results, df)


def test_fg_histogram_single_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 50})
    # fmt: off
    df['accelx'] = [1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["accelx"], group_columns=["Subject"]
    )
    dsk.pipeline.add_feature_generator(
        ["Histogram"],
        params={"group_columns": ["Subject"]},
        function_defaults={
            "columns": ["accelx"],
            "number_of_bins": 10,
            "range_left": -5,
            "range_right": 5,
            "scaling_factor": 255,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_histogram_single_col_result.csv")

    assert_frame_equal(results, df)


def test_fg_histogram_multiple_columns(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 50})
    # fmt: off
    df['accelx'] = [1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4]
    df['accely'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["accelx", "accely"], group_columns=["Subject"]
    )
    dsk.pipeline.add_feature_generator(
        ["Histogram"],
        params={"group_columns": ["Subject"]},
        function_defaults={
            "columns": ["accelx", "accely"],
            "number_of_bins": 10,
            "range_left": -5,
            "range_right": 5,
            "scaling_factor": 255,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_histogram_multiple_cols_result.csv")
    assert_frame_equal(results, df)


def test_fg_histogram_auto_range_single_columns(dsk_proj):
    dsk = dsk_proj
    M = []
    for i in range(-5, 5):
        M.extend([i * 10] * 192)

    df = pd.DataFrame({"accelx": M})
    df["Subject"] = 1

    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["accelx"], group_columns=["Subject"]
    )
    dsk.pipeline.add_feature_generator(
        ["Histogram Auto Scale Range"],
        params={"group_columns": ["Subject"]},
        function_defaults={
            "columns": ["accelx"],
            "number_of_bins": 10,
            "scaling_factor": 255,
        },
    )

    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_histogram_auto_range_single_col_result.csv")
    assert_frame_equal(results, df)


def test_fg_histogram_auto_range_multiple_columns(dsk_proj):
    dsk = dsk_proj

    M = []
    for i in range(-5, 5):
        M.extend([i * 10] * 192)

    df = pd.DataFrame({"accelx": M})
    df["accely"] = M
    df["Subject"] = 1

    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["accelx", "accely"], group_columns=["Subject"]
    )
    dsk.pipeline.add_feature_generator(
        ["Histogram Auto Scale Range"],
        params={"group_columns": ["Subject"]},
        function_defaults={
            "columns": ["accelx", "accely"],
            "number_of_bins": 10,
            "scaling_factor": 255,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_histogram_auto_range_multiple_cols_result.csv")
    assert_frame_equal(results, df)


def test_streaming_downsampler(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [
            [3, 3],
            [4, 5],
            [5, 7],
            [4, 6],
            [3, 1],
            [3, 1],
            [4, 3],
            [5, 5],
            [4, 7],
            [3, 6],
        ],
        columns=["accelx", "accely"],
    )
    df["Subject"] = 1
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["accelx", "accely"], group_columns=["Subject"]
    )
    dsk.pipeline.add_transform(
        "Streaming Downsample",
        params={
            "group_columns": ["Subject"],
            "input_columns": ["accelx", "accely"],
            "filter_length": 3,
        },
    )
    results, stats = dsk.pipeline.execute()

    # import os
    # results.to_csv(os.path.join(os.path.dirname(__file__), "data/streaming_downsampling_result.csv"), index=None)

    df = load_ground_data("streaming_downsampling_result.csv")
    assert_frame_equal(results, df)


def test_tr_scale_min_max_scale(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["feature1", "feature2", "feature3"],
    )
    df["Subject"] = "s01"
    df["Label"] = "A"
    dsk.upload_feature_dataframe(
        "test_features",
        df,
        force=True,
    )
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_features(
        "test_features.csv",
        feature_columns=["feature1", "feature2", "feature3"],
        group_columns=["Subject", "Label"],
        label_column="Label",
    )
    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "passthrough_columns": ["Subject", "Label"],
            "min_bound": 0,
            "max_bound": 255,
        },
    )
    results, stats = dsk.pipeline.execute()
    columns = results.columns

    df = load_ground_data("tr_scale_min_max_scale_result.csv")[columns]

    assert_frame_equal(results, df)


def test_tr_scale_min_max_scale_param(dsk_proj):
    dsk = dsk_proj
    min_max_param = {
        "maximums": {"feature1": 30, "feature2": 100, "feature3": 500},
        "minimums": {"feature1": 0, "feature2": 0, "feature3": -100},
    }
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["feature1", "feature2", "feature3"],
    )
    df["Subject"] = "s01"
    dsk.upload_feature_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_features(
        "test_data.csv",
        feature_columns=["feature1", "feature2", "feature3"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "passthrough_columns": ["Subject"],
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_parameters": min_max_param,
        },
    )

    results, stats = dsk.pipeline.execute()
    columns = results.columns

    # import os
    # results.to_csv(os.path.join(os.path.dirname(__file__), "data/tr_scale_min_max_scale_param_result.csv"), index=None)

    df = load_ground_data("tr_scale_min_max_scale_param_result.csv")[columns]
    assert_frame_equal(results, df)


def test_tr_scale_min_max_scale_param_partial(dsk_proj):
    dsk = dsk_proj
    min_max_param = {
        "maximums": {
            "feature1": 30,
            "feature2": 100,
        },
        "minimums": {
            "feature1": 0,
            "feature2": 0,
        },
    }
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["feature1", "feature2", "feature3"],
    )
    df["Subject"] = "s01"
    dsk.upload_feature_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_features(
        "test_data.csv",
        feature_columns=["feature1", "feature2", "feature3"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "passthrough_columns": ["Subject"],
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_parameters": min_max_param,
        },
    )
    results, stats = dsk.pipeline.execute()
    columns = results.columns

    import os

    # results.to_csv(os.path.join(os.path.dirname(__file__), "data/tr_scale_min_max_scale_param_partial_result.csv"), index=None)

    df = load_ground_data("tr_scale_min_max_scale_param_partial_result.csv")[columns]
    assert_frame_equal(results, df)


@pytest.mark.skip(reason="Not using kbclient")
def tr_scale_normalize(dsk_proj):
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["feature1", "feature2", "feature3"],
    )
    df["Subject"] = "s01"
    df["Rep"] = [0] * 5 + [1] * 5
    normalize = dsk.get_function(self.tr_scale_normalize)
    normalize(df, ["Subject", "Rep"], [], "abs_max", "columns")


class TestSegmentTransforms:
    def test_tr_segment_verticle_scale(self, dsk_proj):
        dsk = dsk_proj
        # fmt: off
        Ax = [0,100, 1000, 2000, 1000, 100, 0, 100, 1000, 2000]
        Ay = [0, -100, -1000, -2000, -1000, -100, 0, -100, -1000, -2000]
        Az = [0, -100, -1000, -2000, -1000, -100, 0, 100, 1000, 2000]
        Gz = [0, -100, -1000, -2000, -1000, -100, 0, 100, 1000, 2000]
        # fmt: on
        df = pd.DataFrame(Ax, columns=["Ax"])
        df["Ay"] = Ay
        df["Az"] = Az
        df["Gz"] = Gz
        df["Subject"] = 0

        dsk.upload_dataframe("test_data", df, force=True)
        dsk.pipeline.reset(delete_cache=True)
        dsk.pipeline.set_input_data(
            "test_data.csv",
            data_columns=["Ax", "Ay", "Az", "Gz"],
            group_columns=["Subject"],
        )
        dsk.pipeline.add_transform(
            "Vertical AutoScale Segment", params={"input_columns": ["Ax", "Ay", "Az"]}
        )
        results, stats = dsk.pipeline.execute()

        expected = load_ground_data("test_segment_verticle_scale_results.csv")
        assert_frame_equal(results, expected)

    def test_tr_segment_strip_mean(self, dsk_proj, accx_accy_2_group_data):
        dsk = dsk_proj
        df = accx_accy_2_group_data
        dsk.upload_dataframe("test_data", df, force=True)
        dsk.pipeline.reset(delete_cache=True)
        dsk.pipeline.set_input_data(
            "test_data.csv",
            data_columns=["accelx", "accely"],
            group_columns=["Subject", "Rep"],
        )
        dsk.pipeline.add_transform(
            "Strip",
            params={
                "group_columns": ["Subject", "Rep"],
                "input_columns": ["accelx", "accely"],
                "type": "mean",
            },
        )
        results, stats = dsk.pipeline.execute()
        df = load_ground_data("tr_segment_strip_mean_result.csv")

        assert_frame_equal(results, df)

    def test_tr_segment_strip_median(self, dsk_proj, accx_accy_2_group_data):
        dsk = dsk_proj
        df = accx_accy_2_group_data
        dsk.upload_dataframe("test_data", df, force=True)
        dsk.pipeline.reset(delete_cache=True)
        dsk.pipeline.set_input_data(
            "test_data.csv",
            data_columns=["accelx", "accely"],
            group_columns=["Subject", "Rep"],
        )
        dsk.pipeline.add_transform(
            "Strip",
            params={
                "group_columns": ["Subject", "Rep"],
                "input_columns": ["accelx", "accely"],
                "type": "median",
            },
        )
        results, stats = dsk.pipeline.execute()

        expected = load_ground_data("tr_segment_strip_median_result.csv")

        assert_frame_equal(results, expected)

    def test_tr_segment_normalize_mean(self, dsk_proj, accx_accy_2_group_data):
        dsk = dsk_proj
        df = accx_accy_2_group_data

        dsk.upload_dataframe("test_data", df, force=True)
        dsk.pipeline.reset(delete_cache=True)
        dsk.pipeline.set_input_data(
            "test_data.csv",
            data_columns=["accelx", "accely"],
            group_columns=["Subject", "Rep"],
        )
        dsk.pipeline.add_transform(
            "Normalize Segment",
            params={
                "group_columns": ["Subject", "Rep"],
                "input_columns": ["accelx", "accely"],
                "mode": "mean",
            },
        )
        results, stats = dsk.pipeline.execute()

        expected = load_ground_data("tr_segment_normalize_mean.csv")

        assert_frame_equal(results, expected)

    def test_tr_segment_normalize_median(self, dsk_proj, accx_accy_2_group_data):
        dsk = dsk_proj
        df = accx_accy_2_group_data
        dsk.upload_dataframe("test_data", df, force=True)
        dsk.pipeline.reset(delete_cache=True)
        dsk.pipeline.set_input_data(
            "test_data.csv",
            data_columns=["accelx", "accely"],
            group_columns=["Subject", "Rep"],
        )
        dsk.pipeline.add_transform(
            "Normalize Segment",
            params={
                "group_columns": ["Subject", "Rep"],
                "input_columns": ["accelx", "accely"],
                "mode": "median",
            },
        )
        results, stats = dsk.pipeline.execute()

        df = load_ground_data("tr_segment_normalize_median.csv")

        assert_frame_equal(results, df)

    def test_tr_segment_normalize_none(self, dsk_proj, accx_accy_2_group_data):
        dsk = dsk_proj
        df = accx_accy_2_group_data
        dsk.upload_dataframe("test_data", df, force=True)
        dsk.pipeline.reset(delete_cache=True)
        dsk.pipeline.set_input_data(
            "test_data.csv",
            data_columns=["accelx", "accely"],
            group_columns=["Subject", "Rep"],
        )
        dsk.pipeline.add_transform(
            "Normalize Segment",
            params={
                "group_columns": ["Subject", "Rep"],
                "input_columns": ["accelx", "accely"],
                "mode": "none",
            },
        )
        results, stats = dsk.pipeline.execute()

        df = load_ground_data("tr_segment_normalize_none.csv")

        assert_frame_equal(results, df)

    def test_tr_segment_scale_factor(self, dsk_proj, accx_accy_2_group_data):
        dsk = dsk_proj
        df = accx_accy_2_group_data
        dsk.upload_dataframe("test_data", df, force=True)
        dsk.pipeline.reset(delete_cache=True)
        dsk.pipeline.set_input_data(
            "test_data.csv",
            data_columns=["accelx", "accely"],
            group_columns=["Subject", "Rep"],
        )

        dsk.pipeline.add_transform(
            "Scale Factor",
            params={
                "group_columns": ["Subject", "Rep"],
                "input_columns": ["accelx", "accely"],
                "mode": "scalar",
                "scale_factor": 0.5,
            },
        )
        results, stats = dsk.pipeline.execute()

        expected = load_ground_data("tr_segment_scale_factor_half.csv")

        assert_frame_equal(results[expected.columns], expected)


def test_fg_stats_generate_minimum(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Minimum"],
        params={"group_columns": ["Subject"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_minimum_results.csv")
    assert_frame_equal(results, df)


def test_fg_stats_generate_maximum(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Maximum"],
        params={"group_columns": ["Subject"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_maximum_results.csv")
    assert_frame_equal(results, df)


def test_fg_stats_pct100(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["100th Percentile"],
        params={"group_columns": ["Subject"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_pct100_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_pct025(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["25th Percentile"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_pct025_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_pct075(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["75th Percentile"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_pct075_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_iqr(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Interquartile Range"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_iqr_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_kurtosis(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Kurtosis"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_kurtosis_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_mean(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Mean"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_mean_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_sum(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Sum"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_sum_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_variance(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Variance"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_variance_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_median(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Median"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_median_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_skewness(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Skewness"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_skewness_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_stdev(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Standard Deviation"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_stdev_result.csv")
    assert_frame_equal(results, df)


def test_fg_rate_of_change_mean_crossing_rate(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [1] * 20}
    )
    # fmt: off
    df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Mean Crossing Rate"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_rate_of_change_mean_crossing_rate_result.csv")

    assert_frame_equal(results, df)


def test_fg_rate_of_change_mean_difference(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [1] * 20}
    )
    # fmt: off
    df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Mean Difference"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_rate_of_change_mean_difference_result.csv")
    assert_frame_equal(results, df)


def test_fg_rate_of_change_second_sigma_crossing_rate(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [1] * 20}
    )
    # fmt: off
    df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Second Sigma Crossing Rate"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_rate_of_change_second_sigma_crossing_rate_result.csv")
    assert_frame_equal(results, df)


def test_fg_rate_of_change_sigma_crossing_rate(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [1] * 20}
    )
    # fmt: off
    df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Sigma Crossing Rate"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_rate_of_change_sigma_crossing_rate_result.csv")
    assert_frame_equal(results, df)


def test_fg_rate_of_change_zero_crossing_rate(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [1] * 20}
    )
    # fmt: off
    df['accelx'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Zero Crossing Rate"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_rate_of_change_zero_crossing_rate_result.csv")
    assert_frame_equal(results, df)


def test_fg_frequency_dominant_frequency(dsk_proj):
    dsk = dsk_proj
    df = dsk.datasets.generate_harmonic_data(
        window_size=512, num_classes=2, num_iterations=1, harmonic_nodes=[2, 4]
    )
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Label"],
        label_column="Label",
        data_columns=["Data"],
    )
    dsk.pipeline.add_feature_generator(
        ["Dominant Frequency"],
        params={"group_columns": ["Label"]},
        function_defaults={"columns": ["Data"], "sample_rate": 512},
    )

    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_frequency_dominant_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_frequency_harmonic_product_spectrum(dsk_proj):
    dsk = dsk_proj
    df = dsk.datasets.generate_harmonic_data(
        window_size=512,
        num_classes=2,
        num_iterations=1,
        harmonic_nodes=[2, 4],
        noise_scale=0,
    )
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Label"],
        label_column="Label",
        data_columns=["Data"],
    )
    dsk.pipeline.add_feature_generator(
        ["Harmonic Product Spectrum"],
        params={"group_columns": ["Label"]},
        function_defaults={"columns": ["Data"], "harmonic_coefficients": 5},
    )

    results, stats = dsk.pipeline.execute()

    # results.to_csv("python_core_functions/data/fg_frequency_harmonic_product_spectrum_result.csv", index=None)
    df = load_ground_data("fg_frequency_harmonic_product_spectrum_result.csv")
    assert_frame_equal(results, df)


def test_fg_frequency_peak_harmonic_product_spectrum(dsk_proj):
    dsk = dsk_proj
    df = dsk.datasets.generate_harmonic_data(
        window_size=512,
        num_classes=2,
        num_iterations=1,
        harmonic_nodes=[2, 4],
        noise_scale=0,
    )
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Label"],
        label_column="Label",
        data_columns=["Data"],
    )
    dsk.pipeline.add_feature_generator(
        ["Peak Harmonic Product Spectrum"],
        params={"group_columns": ["Label"]},
        function_defaults={"columns": ["Data"], "harmonic_coefficients": 5},
    )

    results, stats = dsk.pipeline.execute()

    # results.to_csv("python_core_functions/data/fg_frequency_peak_harmonic_product_spectrum_result.csv", index=None)

    df = load_ground_data("fg_frequency_peak_harmonic_product_spectrum_result.csv")
    assert_frame_equal(results, df)


def test_fg_frequency_spectral_entropy(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {
            "Subject": ["s01"] * 512,
            "Class": ["Crawling"] * 512,
            "Rep": [0] * 256 + [1] * 256,
        }
    )
    # fmt: off
    df['accelx'] = [-3, -7, -11, 0, -6, 42, 22, 40, -18, 18, 15, -33, -28, -50, -15, 13, -30, 71, -34, 5, -6, -15, 34, -14, 12, 6, -22, 34, -14, -1, 48, -31, -26, -41, 46, -52, 37, -22, 37, 15, 52, 65, -16, 70, 45, 22, -3, -61, 80, 14, 35, 31, -15, -46, 47, -29, -6, 11, -15, 15, 48, 45, 26, -9, -56, 5, -2, -11, -22, -14, 18, -26, 3, -17, 21, -2, -18, -17, 3, -22, 44, -12, -2, 29, -13, 19, 0, -39, -26, 7, -28, -2, 50, 6, -4, -11, 10, 27, -25, 42, 1, 12, -20, -14, -8, 46, 43, -45, 25, -49, 65, -2, -57, -18, -13, 19, -36, -5, -8, 12, -28, -28, -13, 10, -4, -26, 10, 31, -27, -9, -18, -16, -12, -19, 9, -6, 16, 2, -27, -19, -19, 64, -19, -22, -21, -14, 13, 22, 41, 15, -19, 52, 42, 18, -8, -44, -13, 9, -16, 3, -4, 26, -37, -28, -19, 2, -29, 8, -25, -19, 15, -61, -21, -44, 0, -20, 19, 36, -34, 17, -20, 0, -47, 5, -8, -40, -36, 9, 31, 12, -1, 11, -12, 28, 44, 0, -27, -23, 37, 18, 38, 19, -32, 52, -6, -9, -12, 0, 68, 12, -23, -2, -48, 23, -8, -16, -28, -12, -23, -26, -17, -23, 47, -53, -16, 21, -11, -4, 14, 25, -18, 16, 12, -21, -23, -2, 28, -18, -10, -34, 1, 12, -1, -9, 21, 28, -23, 54, -5, 9, 17, -18, -8, 14, -9, -45, -41, 22, 16, -14, 28, -1, -57, -5, 6, 14, 31, 8, 22, 35, -28, -49, -10, 25, 2, 5, -9, 17, 7, 62, 22, 29, 22, -14, -30, -14, -2, 4, -51, -3, -16, 11, 9, -31, -8, -17, 9, 13, -77, -15, -34, -25, 21, -11, -13, -46, 31, -19, -18, 12, -2, -64, 55, 6, -7, -13, 33, -1, 17, -21, 21, 16, -13, 23, 16, -1, -7, 8, 20, -9, 30, -4, -46, -4, 4, 15, -47, -16, 25, -12, -18, 29, -28, -26, 14, -15, 26, -16, 7, -10, -26, 18, -7, 46, -25, 13, -30, -18, 9, 6, 29, -10, -26, -31, -14, -27, -43, 18, 4, -19, 26, -61, -22, 11, -18, -15, -14, 1, -25, 19, -40, 11, -32, -21, -18, -41, -41, 18, -28, 10, 5, 50, 28, 36, -3, 7, 67, -74, 0, 41, -65, 21, 1, -26, -25, 6, 40, -2, 14, -12, 1, 9, -15, -2, -43, 15, -1, -23, -38, -10, 36, -35, 3, -4, 46, -2, 0, 34, -6, 32, -40, -1, -7, -14, 31, 23, -9, 1, -18, 9, -6, -7, 4, 6, -18, 17, 0, -13, -56, 10, -19, -10, 54, 13, -16, 25, 3, 20, 12, 28, -16, 4, 29, -6, -33, -7, 2, -2, 60, 4, -8, 14, -11, 11, -13, 14, -18, -9, -9, 8, 50, -30, 35, 35, 9, 29, -43, -9, 6, 14, 54, -16, -30, 22, -23, 27, -19, 44, -38, -1, -46, -83, 10, 18, -10, -31, -52, 19, 14, 13, 19, -15]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Spectral Entropy"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "sample_rate": 10},
    )
    results, stats = dsk.pipeline.execute()
    df = load_ground_data("fg_frequency_spectral_entropy_result.csv")
    assert_frame_equal(results, df)


def test_fg_shape_amplitude_difference_high_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Difference of Peak to Peak of High Frequency between two halves"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "smoothing_factor": 1},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_amplitude_difference_high_frequency_result.csv")

    assert_frame_equal(results, df)


def test_fg_shape_amplitude_global_p2p_high_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Global Peak to Peak of High Frequency"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "smoothing_factor": 2},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_amplitude_global_p2p_high_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_shape_amplitude_global_p2p_low_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Global Peak to Peak of Low Frequency"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "smoothing_factor": 2},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_amplitude_global_p2p_low_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_shape_amplitude_max_p2p_half_high_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Max Peak to Peak of first half of High Frequency"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "smoothing_factor": 1},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_amplitude_max_p2p_half_high_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_shape_amplitude_p2p(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Global Peak to Peak"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_amplitude_p2p_result.csv")
    assert_frame_equal(results, df)


def test_fg_shape_amplitude_min_max_sum(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Global Min Max Sum"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_amplitude_min_max_sum_result.csv")
    assert_frame_equal(results, df)


def test_fg_shape_amplitude_ratio_high_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Ratio of Peak to Peak of High Frequency between two halves"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "smoothing_factor": 1},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_amplitude_ratio_high_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_time_pct_time_over_second_sigma(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Percent Time Over Second Sigma"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "sample_rate": 5},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_time_pct_time_over_second_sigma_result.csv")
    assert_frame_equal(results, df)


def test_fg_time_pct_time_over_sigma(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Percent Time Over Sigma"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "sample_rate": 5},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_time_pct_time_over_sigma_result.csv")
    assert_frame_equal(results, df)


def test_fg_time_pct_time_over_zero(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Percent Time Over Zero"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "sample_rate": 5},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_time_pct_time_over_zero_result.csv")
    assert_frame_equal(results, df)


def test_fg_time_signal_duration(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Duration of the Signal"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "sample_rate": 5},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_time_signal_duration_result.csv")
    assert_frame_equal(results, df)


def test_fg_area_absolute_area(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Absolute Area"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "sample_rate": 10},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_area_absolute_area_result.csv")
    assert_frame_equal(results, df)


def test_fg_area_absolute_area_high_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Absolute Area of High Frequency"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={
            "columns": ["accelx"],
            "sample_rate": 10.0,
            "smoothing_factor": 2,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_area_absolute_area_high_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_area_absolute_area_low_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Absolute Area of Low Frequency"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={
            "columns": ["accelx"],
            "sample_rate": 10.0,
            "smoothing_factor": 2,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_area_absolute_area_low_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_area_absolute_area_spectrum(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 512, "Class": ["Crawling"] * 512, "Rep": [0] * 512}
    )
    # fmt: off
    df['accelx'] = [-3, -7, -11, 0, -6, 42, 22, 40, -18, 18, 15, -33, -28, -50, -15, 13, -30, 71, -34, 5, -6, -15, 34, -14, 12, 6, -22, 34, -14, -1, 48, -31, -26, -41, 46, -52, 37, -22, 37, 15, 52, 65, -16, 70, 45, 22, -3, -61, 80, 14, 35, 31, -15, -46, 47, -29, -6, 11, -15, 15, 48, 45, 26, -9, -56, 5, -2, -11, -22, -14, 18, -26, 3, -17, 21, -2, -18, -17, 3, -22, 44, -12, -2, 29, -13, 19, 0, -39, -26, 7, -28, -2, 50, 6, -4, -11, 10, 27, -25, 42, 1, 12, -20, -14, -8, 46, 43, -45, 25, -49, 65, -2, -57, -18, -13, 19, -36, -5, -8, 12, -28, -28, -13, 10, -4, -26, 10, 31, -27, -9, -18, -16, -12, -19, 9, -6, 16, 2, -27, -19, -19, 64, -19, -22, -21, -14, 13, 22, 41, 15, -19, 52, 42, 18, -8, -44, -13, 9, -16, 3, -4, 26, -37, -28, -19, 2, -29, 8, -25, -19, 15, -61, -21, -44, 0, -20, 19, 36, -34, 17, -20, 0, -47, 5, -8, -40, -36, 9, 31, 12, -1, 11, -12, 28, 44, 0, -27, -23, 37, 18, 38, 19, -32, 52, -6, -9, -12, 0, 68, 12, -23, -2, -48, 23, -8, -16, -28, -12, -23, -26, -17, -23, 47, -53, -16, 21, -11, -4, 14, 25, -18, 16, 12, -21, -23, -2, 28, -18, -10, -34, 1, 12, -1, -9, 21, 28, -23, 54, -5, 9, 17, -18, -8, 14, -9, -45, -41, 22, 16, -14, 28, -1, -57, -5, 6, 14, 31, 8, 22, 35, -28, -49, -10, 25, 2, 5, -9, 17, 7, 62, 22, 29, 22, -14, -30, -14, -2, 4, -51, -3, -16, 11, 9, -31, -8, -17, 9, 13, -77, -15, -34, -25, 21, -11, -13, -46, 31, -19, -18, 12, -2, -64, 55, 6, -7, -13, 33, -1, 17, -21, 21, 16, -13, 23, 16, -1, -7, 8, 20, -9, 30, -4, -46, -4, 4, 15, -47, -16, 25, -12, -18, 29, -28, -26, 14, -15, 26, -16, 7, -10, -26, 18, -7, 46, -25, 13, -30, -18, 9, 6, 29, -10, -26, -31, -14, -27, -43, 18, 4, -19, 26, -61, -22, 11, -18, -15, -14, 1, -25, 19, -40, 11, -32, -21, -18, -41, -41, 18, -28, 10, 5, 50, 28, 36, -3, 7, 67, -74, 0, 41, -65, 21, 1, -26, -25, 6, 40, -2, 14, -12, 1, 9, -15, -2, -43, 15, -1, -23, -38, -10, 36, -35, 3, -4, 46, -2, 0, 34, -6, 32, -40, -1, -7, -14, 31, 23, -9, 1, -18, 9, -6, -7, 4, 6, -18, 17, 0, -13, -56, 10, -19, -10, 54, 13, -16, 25, 3, 20, 12, 28, -16, 4, 29, -6, -33, -7, 2, -2, 60, 4, -8, 14, -11, 11, -13, 14, -18, -9, -9, 8, 50, -30, 35, 35, 9, 29, -43, -9, 6, 14, 54, -16, -30, 22, -23, 27, -19, 44, -38, -1, -46, -83, 10, 18, -10, -31, -52, 19, 14, 13, 19, -15]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Absolute Area of Spectrum"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={
            "columns": ["accelx"],
            "sample_rate": 100,
            "smoothing_factor": 2,
        },
    )
    results, stats = dsk.pipeline.execute()
    df = load_ground_data("fg_area_absolute_area_spectrum_result.csv")
    assert_frame_equal(results, df)


def test_fg_area_total_area(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    df["accelx"] = [
        1,
        -2,
        -3,
        1,
        2,
        5,
        2,
        -2,
        -3,
        -1,
        1,
        -3,
        -4,
        1,
        2,
        6,
        2,
        -3,
        -2,
        -1,
    ]
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Total Area"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"], "sample_rate": 10.0},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_area_total_area_result.csv")
    assert_frame_equal(results, df)


def test_fg_area_total_area_high_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Total Area of High Frequency"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={
            "columns": ["accelx"],
            "sample_rate": 10.0,
            "smoothing_factor": 2,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_area_total_area_high_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_area_total_area_low_frequency(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Total Area of Low Frequency"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={
            "columns": ["accelx"],
            "sample_rate": 10.0,
            "smoothing_factor": 2,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_area_total_area_low_frequency_result.csv")
    assert_frame_equal(results, df)


def test_fg_energy_average_energy_y_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Average Energy"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accely"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_energy_average_energy_result_y.csv")
    assert_frame_equal(results, df)


def test_fg_energy_average_energy_all_columns(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Average Energy"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_energy_average_energy_result_all.csv")
    assert_frame_equal(results, df)


def test_fg_energy_p2p(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Global Peak to Peak"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_energy_p2p_result.csv")
    assert_frame_equal(results, df)


def test_fg_energy_total_energy_y_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Total Energy"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accely"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_energy_total_energy_result_y.csv")
    assert_frame_equal(results, df)


def test_fg_energy_total_energy_all_columns(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Total Energy"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_energy_total_energy_result_all.csv")
    assert_frame_equal(results, df)


def test_fg_energy_average_demeaned_energy_single_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Average Demeaned Energy"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_energy_average_demeaned_energy_result_single_col.csv")
    assert_frame_equal(results, df)


def test_fg_energy_average_demeaned_energy_all_columns(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Average Demeaned Energy"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_energy_average_demeaned_energy_result_all.csv")
    assert_frame_equal(results, df)


def test_fg_physical_variance_movement_intensity_all_columns(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Variance of Movement Intensity"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_physical_variance_movement_intensity_result.csv")
    assert_frame_equal(results, df)


def test_fg_physical_variance_movement_intensity_single_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Variance of Movement Intensity"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data(
        "fg_physical_variance_movement_intensity_result_single_col.csv"
    )
    assert_frame_equal(results, df)


def test_fg_physical_average_signal_magnitude_area_all_columns(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 8, "Class": ["Crawling"] * 8, "Rep": [0] * 8}
    )
    # fmt: off
    df['accelx'] = [ 2, 2, 2, 2, 2, 2, 2, 2,]
    df['accely'] = [-2, -2, -2, -2, -2, -2, -2, -2,]
    df['accelz'] = [32000, 32000, 32000, 32000, 32000, 32000, -32000, -32000]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Average Signal Magnitude Area"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_physical_average_signal_magnitude_area_result.csv")
    assert_frame_equal(results, df)


def test_fg_physical_average_signal_magnitude_area_single_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 8, "Class": ["Crawling"] * 8, "Rep": [0] * 8}
    )
    # fmt: off
    df['accelx'] = [ 2, 2, 2, 2, 2, 2, 2, 2,]
    df['accely'] = [-2, -2, -2, -2, -2, -2, -2, -2,]
    df['accelz'] = [32000, 32000, 32000, 32000, 32000, 32000, -32000, -32000]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Average Signal Magnitude Area"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelz"]},
    )
    results, stats = dsk.pipeline.execute()
    print(results)

    df = load_ground_data(
        "fg_physical_average_signal_magnitude_area_result_single_col.csv"
    )
    assert_frame_equal(results, df)


def test_fg_physical_average_movement_intensity_all_columns(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 8 + [1] * 12}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Average of Movement Intensity"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_physical_average_movement_intensity_result.csv")
    assert_frame_equal(results, df)


def test_fg_physical_average_movement_intensity_single_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [0] * 20}
    )
    # fmt: off
    df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
    df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject", "Class", "Rep"],
    )
    dsk.pipeline.add_feature_generator(
        ["Average of Movement Intensity"],
        params={"group_columns": ["Subject", "Class", "Rep"]},
        function_defaults={"columns": ["accelx"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data(
        "fg_physical_average_movement_intensity_result_single_col.csv"
    )
    assert_frame_equal(results, df)


def test_fg_stats_abs_mean(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Absolute Mean"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_abs_mean_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_abs_sum(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],
        columns=["accelx", "accely", "accelz"],
    )
    df["Subject"] = "A"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["accelx", "accely", "accelz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_feature_generator(
        ["Absolute Sum"],
        params={"group_columns": []},
        function_defaults={"columns": ["accelx", "accely", "accelz"]},
    )
    results, stats = dsk.pipeline.execute()


@pytest.mark.skip(reason="dev function")
def test_tr_filter_extreme_values(dsk_proj):
    # test using global min and max
    dsk = dsk_proj
    df = pd.DataFrame(
        [
            [-100, -200, -300],
            [3, 7, 8],
            [0, 6, 90],
            [-2, 8, 7],
            [8, 9, 6],
            [8, 9, 6],
            [100, 200, 300],
        ],
        columns=["feature1", "feature2", "feature3"],
    )
    df["Subject"] = "s01"

    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data("test_data.csv")
    dsk.pipeline.add_transform(
        "Filter Extreme Values",
        params={
            "input_columns": ["feature1", "feature2", "feature3"],
            "min_bound": -100,
            "max_bound": 100,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("tr_filter_extreme_values_result.csv")
    assert_frame_equal(results, df)

    # test using signal_min_max_params
    dsk.pipeline.reset(delete_cache=True)
    df = pd.DataFrame(
        [
            [-100, -200, -300],
            [3, 7, 8],
            [0, 6, 90],
            [-2, 8, 7],
            [8, 9, 6],
            [8, 9, 6],
            [100, 200, 300],
        ],
        columns=["feature1", "feature2", "feature3"],
    )
    df["Subject"] = "s01"
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.set_input_data("test_data.csv")
    min_max_param = {
        "maximums": {"feature1": 400, "feature2": 90, "feature3": 500},
        "minimums": {"feature1": 0, "feature2": 0, "feature3": -100},
    }
    dsk.pipeline.add_transform(
        "Filter Extreme Values",
        params={
            "input_columns": ["feature1", "feature2", "feature3"],
            "min_bound": -100,
            "max_bound": 100,
            "signal_min_max_parameters": min_max_param,
        },
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("tr_filter_extreme_values_result2.csv")
    assert_frame_equal(results, df)


@pytest.mark.skip("dev server only and not working")
def test_sensor_transform_first_derivative(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {
            "GyrSqrtSum": {
                0: 10,
                1: 101,
                2: 4,
                3: 55,
                4: 2,
                5: 2,
                6: 2,
                7: 24,
                8: 59,
                9: 122,
            }
        }
    )
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data("test_data.csv")
    dsk.pipeline.add_transform(
        "First Derivative", params={"input_columns": ["GyrSqrtSum"]}
    )

    results, stats = dsk.pipeline.execute()
    df = load_ground_data("tr_shft_first_derivative_result.csv")
    assert_frame_equal(results, df)


@pytest.mark.skip("dev server only and not working")
def test_sensor_transform_second_derivative(dsk_proj):
    dsk = dsk_proj

    df = pd.DataFrame(
        {
            "GyrSqrtSum": {
                0: 10,
                1: 101,
                2: 4,
                3: 55,
                4: 2,
                5: 2,
                6: 2,
                7: 24,
                8: 59,
                9: 122,
            }
        }
    )
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data("test_data.csv")
    dsk.pipeline.add_transform(
        "Second Derivative", params={"input_columns": ["GyrSqrtSum"]}
    )

    results, stats = dsk.pipeline.execute()
    df = load_ground_data("tr_shft_second_derivative_result.csv")
    assert_frame_equal(results, df)


def test_fg_frequency_mfcc(dsk_proj):
    dsk = dsk_proj

    # fmt: off
    df = pd.DataFrame([
            -182,   -438,   -322,   -281,     31,    155,    217,    483,
              365,    301,    230,    -98,   -139,   -317,   -430,   -476,
             -437,   -160,     73,    323,    439,    516,    533,    411,
              229,    -35,   -313,   -481,   -571,   -493,   -395,   -200,
               56,    316,    493,    578,    549,    438,    258,     42,
             -140,   -258,   -408,   -331,   -123,    -26,    657,   1123,
              775,    146,   -545,  -1229,  -1541,  -1611,  -1589,  -1144,
             -334,   1235,   2563,   2793,   2910,   2029,   1308,     16,
            -1642,  -2727,  -3632,  -3295,  -2588,  -1678,   -767,    718,
             2068,   2795,   2764,   2421,   1694,   1199,   1147,    260,
             -942,  -1182,  -1586,  -2146,  -2216,  -2451,  -2051,   -545,
              860,   2074,   2648,   2331,   2011,   1454,    641,   -143,
             -667,   -880,  -1388,  -1323,  -2002,  -2588,  -1511,  -1116,
              290,   1340,   2237,   2521,   3108,   3002,   1055,   -217,
            -1969,  -2490,  -1761,  -1172,  -1170,   -993,   -958,   -848,
             -199,   -119,    128,    736,   1599,   2354,   2713,   1748,
             1330,    226,  -1421,  -1713,  -2705,  -2204,  -1422,   -788,
             -275,   -279,    611,    762,    922,   1582,    810,   1363,
             1663,   1209,    722,    188,   -587,  -1332,  -1916,  -2434,
            -2172,  -1235,    329,    883,   1006,   1022,    581,    118,
               20,    256,    883,   2079,   2902,   2310,    627,  -1460,
            -3323,  -3613,  -2854,  -2469,  -1496,   -722,   -142,   -102,
               12,   1029,   2622,   4740,   5309,   4194,   2033,   -950,
            -2209,  -3602,  -4201,  -3532,  -3356,  -1117,    132,    383,
              413,    621,    704,   2285,   3377,   1970,   1383,    222,
            -1291,   -382,   -407,   -944,    149,   -626,     36,     36,
             -832,  -1673,  -2119,  -1414,   -421,   1694,   1908,   2021,
             1206,    -64,  -1708,  -1498,  -2032,  -1014,   1863,   3398,
             4627,   4459,   2161,  -1813,  -3295,  -6010,  -4838,  -2045,
             -584,   1724,   2465,    883,   -228,   -367,   -990,    690,
             1445,   1920,   1793,   1945,    243,   -959,  -1923,  -4019,
            -3107,  -2108,    -44,   1940,   3051,   2210,   1947,    492,
             -954,   -805,  -1142,   1094,   1563,   2285,   2051,    105,
            -1559,  -3343,  -3745,  -3167,  -1030,    534,   2030,   1665,
             1152,    -21,    597,   1355,   1532,   2667,   1484,    766,
             -696,  -1577,  -2906,  -2606,  -3348,  -2433,  -1788,   -715,
              595,   1664,   2034,   1579,   2544,   2686,   4353,   4018,
             2558,   -663,  -4283,  -6753,  -6390,  -4616,  -1874,   1151,
             1893,   2450,   2642,   1886,   2450,   3416,   2016,   1428,
               50,  -1924,  -2640,  -1942,  -2961,  -1628,  -1712,  -1250,
               55,    342,   1096,    951,   1603,   1615,   2883,   2789,
             2053,   -173,  -2210,  -3895,  -4108,  -3198,  -1747,   -632,
             1425,   2070,   2322,   3741,   2562,   3502,   4130,   2713,
              -78,  -2356,  -7037, -10287,  -6810,  -1096,    611,  -1001,
              799,   5226,   9356,   7405,   4192,    761,   -512,   1120,
             -515,  -4228, -11073, -10278,  -1708,    792,   -970,   -119,
             1996,   7492,   9687,   6640,   1964,   -943,   1065,   -107,
            -3868, -10121,  -9652,  -3354,   -313,     87,   -827,    264,
             3104,   7663,   8414,   6518,   1874,  -1103,   1236,   -884,
            -5323,  -8274,  -6716,  -5337,  -1392,    795,   -822,   3469], dtype='int16', columns = ["mic"])
    # fmt: on

    df["Class"] = "barking"
    df["SegmentID"] = 0
    df["Subject"] = 197243
    dsk.upload_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data",
        data_columns=["mic"],
        group_columns=["Subject", "Class", "SegmentID"],
        label_column="Class",
    )

    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "MFCC",
                "params": {
                    "columns": ["mic"],
                    "group_columns": ["Subject", "Class", "SegmentID"],
                    "sample_rate": 16000,
                    "cepstra_count": 23,
                },
            }
        ]
    )
    results, stats = dsk.pipeline.execute()

    # print results
    df = load_ground_data("fg_mfcc_result.csv")
    # print df
    assert_frame_equal(results, df, scaling=100000)


def test_fg_frequency_mfe(dsk_proj):
    dsk = dsk_proj

    # fmt: off
    df = pd.DataFrame([
            -182,   -438,   -322,   -281,     31,    155,    217,    483,
              365,    301,    230,    -98,   -139,   -317,   -430,   -476,
             -437,   -160,     73,    323,    439,    516,    533,    411,
              229,    -35,   -313,   -481,   -571,   -493,   -395,   -200,
               56,    316,    493,    578,    549,    438,    258,     42,
             -140,   -258,   -408,   -331,   -123,    -26,    657,   1123,
              775,    146,   -545,  -1229,  -1541,  -1611,  -1589,  -1144,
             -334,   1235,   2563,   2793,   2910,   2029,   1308,     16,
            -1642,  -2727,  -3632,  -3295,  -2588,  -1678,   -767,    718,
             2068,   2795,   2764,   2421,   1694,   1199,   1147,    260,
             -942,  -1182,  -1586,  -2146,  -2216,  -2451,  -2051,   -545,
              860,   2074,   2648,   2331,   2011,   1454,    641,   -143,
             -667,   -880,  -1388,  -1323,  -2002,  -2588,  -1511,  -1116,
              290,   1340,   2237,   2521,   3108,   3002,   1055,   -217,
            -1969,  -2490,  -1761,  -1172,  -1170,   -993,   -958,   -848,
             -199,   -119,    128,    736,   1599,   2354,   2713,   1748,
             1330,    226,  -1421,  -1713,  -2705,  -2204,  -1422,   -788,
             -275,   -279,    611,    762,    922,   1582,    810,   1363,
             1663,   1209,    722,    188,   -587,  -1332,  -1916,  -2434,
            -2172,  -1235,    329,    883,   1006,   1022,    581,    118,
               20,    256,    883,   2079,   2902,   2310,    627,  -1460,
            -3323,  -3613,  -2854,  -2469,  -1496,   -722,   -142,   -102,
               12,   1029,   2622,   4740,   5309,   4194,   2033,   -950,
            -2209,  -3602,  -4201,  -3532,  -3356,  -1117,    132,    383,
              413,    621,    704,   2285,   3377,   1970,   1383,    222,
            -1291,   -382,   -407,   -944,    149,   -626,     36,     36,
             -832,  -1673,  -2119,  -1414,   -421,   1694,   1908,   2021,
             1206,    -64,  -1708,  -1498,  -2032,  -1014,   1863,   3398,
             4627,   4459,   2161,  -1813,  -3295,  -6010,  -4838,  -2045,
             -584,   1724,   2465,    883,   -228,   -367,   -990,    690,
             1445,   1920,   1793,   1945,    243,   -959,  -1923,  -4019,
            -3107,  -2108,    -44,   1940,   3051,   2210,   1947,    492,
             -954,   -805,  -1142,   1094,   1563,   2285,   2051,    105,
            -1559,  -3343,  -3745,  -3167,  -1030,    534,   2030,   1665,
             1152,    -21,    597,   1355,   1532,   2667,   1484,    766,
             -696,  -1577,  -2906,  -2606,  -3348,  -2433,  -1788,   -715,
              595,   1664,   2034,   1579,   2544,   2686,   4353,   4018,
             2558,   -663,  -4283,  -6753,  -6390,  -4616,  -1874,   1151,
             1893,   2450,   2642,   1886,   2450,   3416,   2016,   1428,
               50,  -1924,  -2640,  -1942,  -2961,  -1628,  -1712,  -1250,
               55,    342,   1096,    951,   1603,   1615,   2883,   2789,
             2053,   -173,  -2210,  -3895,  -4108,  -3198,  -1747,   -632,
             1425,   2070,   2322,   3741,   2562,   3502,   4130,   2713,
              -78,  -2356,  -7037, -10287,  -6810,  -1096,    611,  -1001,
              799,   5226,   9356,   7405,   4192,    761,   -512,   1120,
             -515,  -4228, -11073, -10278,  -1708,    792,   -970,   -119,
             1996,   7492,   9687,   6640,   1964,   -943,   1065,   -107,
            -3868, -10121,  -9652,  -3354,   -313,     87,   -827,    264,
             3104,   7663,   8414,   6518,   1874,  -1103,   1236,   -884,
            -5323,  -8274,  -6716,  -5337,  -1392,    795,   -822,   3469], dtype='int16', columns = ["mic"])
    # fmt: on

    df["Class"] = "barking"
    df["SegmentID"] = 0
    df["Subject"] = 197243
    dsk.upload_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data",
        data_columns=["mic"],
        group_columns=["Subject", "Class", "SegmentID"],
        label_column="Class",
    )

    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "MFE",
                "params": {
                    "columns": ["mic"],
                    "group_columns": ["Subject", "Class", "SegmentID"],
                    "num_filters": 23,
                },
            }
        ]
    )
    results, stats = dsk.pipeline.execute()

    # print results
    df = load_ground_data("fg_mfe_result.csv")
    # print df
    assert_frame_equal(results, df, scaling=100000)


def test_fg_frequency_power_spectrum(dsk_proj):
    dsk = dsk_proj

    # fmt: off
    df = pd.DataFrame([0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024], dtype='int16', columns = ["mic"])
    # fmt: on

    df["Class"] = "barking"
    df["SegmentID"] = 0
    df["Subject"] = 197243
    dsk.upload_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data",
        data_columns=["mic"],
        group_columns=["Subject", "Class", "SegmentID"],
        label_column="Class",
    )

    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Power Spectrum",
                "params": {
                    "columns": ["mic"],
                    "group_columns": ["Subject", "Class", "SegmentID"],
                    "number_of_bins": 16,
                    "window_type": "hanning",
                },
            }
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_frequency_power_spectrum_result.csv")
    # print df
    assert_frame_equal(results, df, scaling=1000)


def test_fg_sampling_downsample_avg_with_normalization(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        [
            [3, -1000],
            [4, -1000],
            [5, 0],
            [4, 0],
            [3, 1000],
            [3, 1000],
            [4, 2000],
            [5, 2000],
            [4, 5000],
            [3, 5000],
        ],
        columns=["accelx", "accely"],
    )
    df["Subject"] = 1
    dsk.upload_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data", group_columns=["Subject"], data_columns=["accelx", "accely"]
    )
    dsk.pipeline.add_feature_generator(
        ["Downsample Average with Normalization"],
        function_defaults={"columns": ["accelx", "accely"], "new_length": 5},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_convolution_avg_result.csv")
    assert_frame_equal(results, df)


def test_sampler_combine_labels(dsk_proj):
    dsk = dsk_proj

    df = pd.DataFrame(
        [
            [-3, 6, 5, "A"],
            [3, 7, 8, "B"],
            [0, 6, 3, "C"],
            [-2, 8, 7, "C"],
            [2, 9, 6, "D"],
        ],
        columns=["feature1", "feature2", "feature3", "label"],
    )
    df["Subject"] = 1
    dsk.upload_feature_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_features(
        "test_data",
        feature_columns=["feature1", "feature2", "feature3"],
        group_columns=["Subject", "label"],
        label_column="label",
    )
    dsk.pipeline.add_transform(
        "Combine Labels",
        params={"combine_labels": {"Group1": ["A", "B"], "Group2": ["C"]}},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("sampler_combine_labels_result.csv")
    assert_frame_equal(results, df)


@pytest.mark.skip("not supported for sensor data at this point")
def test_sampler_max_metadata(dsk_proj):
    dsk = dsk_proj
    # fmt: off
    expected_results_cat = [1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1]
    # fmt: on
    window_size = 50
    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    df = create_ground_data(dsk, sensor_columns, window_size, 3, 50)
    dsk.upload_dataframe("window_test.csv", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "window_test.csv",
        group_columns=["Subject"],
        label_column="Label",
        data_columns=sensor_columns,
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": window_size, "delta": window_size // 5}
    )

    dsk.pipeline.add_transform(
        "Resampling by Majority Vote", params={"metadata_name": "Label"}
    )

    r, s = dsk.pipeline.execute()

    g = r.groupby(["Subject", "SegmentID"])

    M = []
    for i in range(746):
        tmp_df = g.get_group((0, i))
        assert tmp_df["Label"].value_counts().shape[0] == 1

    for index, result in enumerate(expected_results_cat):
        tmp_df = g.get_group((0, index))
        assert tmp_df["Label"].value_counts().index[0] == result


def test_fg_cross_column_mean_crossing_rate(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 20, "Class": ["Crawling"] * 20, "Rep": [1] * 20}
    )
    df["accelx"] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    df["accely"] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Rep", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely"],
    )
    dsk.pipeline.add_feature_generator(
        ["Cross Column Mean Crossing Rate"],
        function_defaults={"columns": ["accelx", "accely"]},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_cross_column_mean_crossing_rate_result.csv")
    assert_frame_equal(results, df)


def test_fg_cross_column_median_difference(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 10, "Class": ["Crawling"] * 10, "Rep": [1] * 10}
    )
    # fmt: off
    df['accelx'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,]
    df['accely'] = [10, 10, 10, 10, 10, 20, 20, 20, 20, 20]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Rep", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Two Column Median Difference",
                "params": {"columns": ["accelx", "accely"]},
            },
            {
                "name": "Two Column Median Difference",
                "params": {"columns": ["accely", "accelx"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()
    df = load_ground_data("fg_cross_column_median_difference_result.csv")
    assert_frame_equal(results, df)


def test_fg_cross_column_peak_location_difference(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 10, "Class": ["Crawling"] * 10, "Rep": [1] * 10}
    )
    # fmt: off
    df['accelx'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,]
    df['accely'] = [10, 10, 10, 10, 10, 20, 20, 20, 20, 20]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Rep", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Two Column Peak Location Difference",
                "params": {"columns": ["accelx", "accely"]},
            },
            {
                "name": "Two Column Peak Location Difference",
                "params": {"columns": ["accely", "accelx"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_cross_column_peak_location_difference_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_linear_regression(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 12, "Class": ["Crawling"] * 12})
    # fmt: off
    df["X"] = [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110,]
    df["Y"] = [ 0, 10, 20, 30, 40, 50, 60, 50, 40, 30, 20, 10,]
    df["Z"] = [-30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000]
    # fmt: on

    dsk.upload_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Class"],
        label_column="Class",
        data_columns=["X", "Y", "Z"],
    )
    dsk.pipeline.add_feature_generator(
        [{"name": "Linear Regression Stats", "params": {"columns": ["X", "Y", "Z"]}}]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_linear_regression_results.csv")
    assert_frame_equal(results, df)


def test_fg_shape_median_difference(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 12, "Class": ["Crawling"] * 12})
    # fmt: off
    df["X"] = [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110,]
    df["Y"] = [ 0, 10, 20, 30, 40, 50, 60, 50, 40, 30, 20, 10,]
    df["Z"] = [-30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000]
    # fmt: on

    dsk.upload_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Class"],
        label_column="Class",
        data_columns=["X", "Y", "Z"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Shape Median Difference",
                "params": {"columns": ["X", "Y", "Z"], "center_ratio": 0.25},
            }
        ]
    )

    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_median_difference_results.csv")
    assert_frame_equal(results, df)


def test_fg_shape_absolute_median_difference(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 12, "Class": ["Crawling"] * 12})
    # fmt: off
    df["X"] = [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110,]
    df["Y"] = [ 0, 10, 20, 30, 40, 50, 60, 50, 40, 30, 20, 10,]
    df["Z"] = [-30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Class"],
        label_column="Class",
        data_columns=["X", "Y", "Z"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Shape Absolute Median Difference",
                "params": {"columns": ["X", "Y", "Z"], "center_ratio": 0.25},
            }
        ]
    )

    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_shape_absolute_median_differencen_results.csv")
    assert_frame_equal(results, df)


def test_fg_stats_zero_crossings(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 12, "Class": ["Crawling"] * 12})
    # fmt: off
    df['accelx'] =   [-300, -100, 0, 100, 300, 100, 0, -100, -300, -100, 0, 100]
    df['accely'] = [-5000, -9000, 0, 9000, 5000, -5000, -9000, 0, 9000, 5000, -5000, -9000]
    df['accelz'] = [-30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely", "accelz"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Zero Crossings",
                "params": {"columns": ["accelx", "accely", "accelz"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_zero_crossings_result.csv")
    assert_frame_equal(results, df)


def test_fg_cross_column_min_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 12, "Class": ["Crawling"] * 12})
    # fmt: off
    df['accelx'] =   [-300, -100, 0, 100, 300, 100, 0, -100, -300, -100, 0, 100]
    df['accely'] = [-5000, -9000, 0, 9000, 5000, -5000, -9000, 0, 9000, 5000, -5000, -9000]
    df['accelz'] = [-30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely", "accelz"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Min Column",
                "params": {"columns": ["accelx", "accely", "accelz"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_cross_min_column_result.csv")
    assert_frame_equal(results, df)


def test_fg_cross_column_max_column(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 12, "Class": ["Crawling"] * 12})
    # fmt: off
    df['accelx'] =   [-300, -100, 0, 100, 300, 100, 0, -100, -300, -100, 0, 100]
    df['accely'] = [-5000, -9000, 0, 9000, 5000, 32001, -9000, 0, 9000, 5000, -5000, -9000]
    df['accelz'] = [-30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely", "accelz"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Max Column",
                "params": {"columns": ["accelx", "accely", "accelz"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_cross_max_column_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_positive_zero_crossings(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 12, "Class": ["Crawling"] * 12})
    # fmt: off
    df['accelx'] =   [-300, -100, 0, 100, 300, 100, 0, -100, -300, -100, 0, 100]
    df['accely'] = [-5000, -9000, 0, 9000, 5000, -5000, -9000, 0, 9000, 5000, -5000, -9000]
    df['accelz'] = [-30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely", "accelz"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Positive Zero Crossings",
                "params": {"columns": ["accelx", "accely", "accelz"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_positive_zero_crossings_result.csv")
    assert_frame_equal(results, df)


def test_fg_stats_negative_zero_crossings(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame({"Subject": ["s01"] * 12, "Class": ["Crawling"] * 12})
    # fmt: off
    df['accelx'] =   [-300, -100, 0, 100, 300, 100, 0, -100, -300, -100, 0, 100]
    df['accely'] = [-5000, -9000, 0, 9000, 5000, -5000, -9000, 0, 9000, 5000, -5000, -9000]
    df['accelz'] = [-30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely", "accelz"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Negative Zero Crossings",
                "params": {"columns": ["accelx", "accely", "accelz"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_stats_negative_zero_crossings_result.csv")
    assert_frame_equal(results, df)


def test_fg_cross_column_peak_location_difference(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 10, "Class": ["Crawling"] * 10, "Rep": [1] * 10}
    )
    # fmt: off
    df['accelx'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,]
    df['accely'] = [10, 10, 10, 10, 10, 20, 20, 20, 20, 20]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Rep", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Two Column Peak Location Difference",
                "params": {"columns": ["accelx", "accely"]},
            },
            {
                "name": "Two Column Peak Location Difference",
                "params": {"columns": ["accely", "accelx"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_cross_column_peak_location_difference_result.csv")
    assert_frame_equal(results, df)


def test_fg_cross_column_peak_location_difference(dsk_proj):
    dsk = dsk_proj
    df = pd.DataFrame(
        {"Subject": ["s01"] * 10, "Class": ["Crawling"] * 10, "Rep": [1] * 10}
    )
    # fmt: off
    df['accelx'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,]
    df['accely'] = [10, 10, 10, 10, 10, 20, 20, 20, 20, 20]
    # fmt: on
    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        group_columns=["Subject", "Rep", "Class"],
        label_column="Class",
        data_columns=["accelx", "accely"],
    )
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Two Column Peak Location Difference",
                "params": {"columns": ["accelx", "accely"]},
            },
            {
                "name": "Two Column Peak Location Difference",
                "params": {"columns": ["accely", "accelx"]},
            },
        ]
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("fg_cross_column_peak_location_difference_result.csv")
    assert_frame_equal(results, df)


@pytest.mark.skip(reason="Training directly from features is not currently supported")
def test_pme_hierarchical_cluster(dsk_proj):
    dsk = dsk_proj
    df = load_ground_data("pme_hierarchical_cluster_test.csv")
    df = df.astype("int")

    sensorcolumns = ["X", "Y", "Z"]
    labelcolumn = "label"
    groupcolumns = ["SegmentID", "label", "subject"]
    classification_mode = "KNN"
    distance_mode = "L1"
    number_of_neurons = 128

    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=sensorcolumns,
        group_columns=groupcolumns,
        label_column=labelcolumn,
    )
    dsk.pipeline.set_validation_method("Recall")
    dsk.pipeline.set_classifier(
        "PME",
        params={
            "classification_mode": classification_mode,
            "distance_mode": distance_mode,
        },
    )
    dsk.pipeline.set_training_algorithm(
        "Hierarchical Clustering with Neuron Optimization",
        params={"number_of_neurons": number_of_neurons, "cluster_method": "kmeans"},
    )
    dsk.pipeline.set_tvo({"validation_seed": 0})
    results, stats = dsk.pipeline.execute()

    model = results.configurations[0].models[0]
    cm = model.confusion_matrix_stats
    assert (
        cm["validation"].confusion_matrix_data_frame["Sens(%)"].values[-1] > 40
    ), "kmean clustring perform less than expected Acc: <= 50 !!!"


@pytest.mark.skip(reason="dev function")
def test_tr_segment_horizontal_scale(dsk_proj):
    dsk = dsk_proj
    # fmt: off
    Ax = [0,100, 1000, 2000, 1000, 100, 0, 100, 1000, 2000]
    Ay = [0, -100, -1000, -2000, -1000, -100, 0, -100, -1000, -2000]
    Az = [0, -100, -1000, -2000, -1000, -100, 0, 100, 1000, 2000]
    Gz = [0, -100, -1000, -2000, -1000, -100, 0, 100, 1000, 2000]
    # fmt: on
    df = pd.DataFrame(Ax, columns=["Ax"])
    df["Ay"] = Ay
    df["Az"] = Az
    df["Gz"] = Gz
    df["Subject"] = 0

    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["Ax", "Ay", "Az", "Gz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_transform(
        "Horizontal Scale Segment",
        params={"input_columns": ["Ax", "Ay", "Az"], "new_length": 20},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("test_horizontal_scale_nlength20.csv")
    assert_frame_equal(results, df)

    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv",
        data_columns=["Ax", "Ay", "Az", "Gz"],
        group_columns=["Subject"],
    )
    dsk.pipeline.add_transform(
        "Horizontal Scale Segment",
        params={"input_columns": ["Ax", "Ay", "Az"], "new_length": 5},
    )
    results, stats = dsk.pipeline.execute()

    df = load_ground_data("test_horizontal_scale_nlength5.csv")
    assert_frame_equal(results, df)


@pytest.mark.skip(reason="dev function")
def test_tr_feature_average(dsk_proj):
    dsk = dsk_proj
    M = []
    M.append(
        pd.DataFrame(
            np.array([list(range(5)), [1] * 5, [1] * 5, list(range(5)), [1] * 5]).T,
            columns=["gen_01_A", "gen_02_B", "Label", "SegmentID", "capture_id"],
        )
    )
    M.append(
        pd.DataFrame(
            np.array([list(range(5)), [1] * 5, [2] * 5, list(range(5)), [2] * 5]).T,
            columns=["gen_01_A", "gen_02_B", "Label", "SegmentID", "capture_id"],
        )
    )
    df = pd.concat(M).reset_index(drop=True)

    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", group_columns=["Label", "capture_id", "SegmentID"]
    )
    dsk.pipeline.add_transform(
        "Feature Average",
        params={
            "group_columns": ["Label", "SegmentID", "capture_id"],
            "num_cascades": 2,
            "stride": 2,
        },
    )
    results, stats = dsk.pipeline.execute()

    expected_results = pd.DataFrame(
        {
            "Label": {0: 1, 1: 1, 2: 2, 3: 2},
            "SegmentID": {0: 0, 1: 2, 2: 0, 3: 2},
            "capture_id": {0: 1, 1: 1, 2: 2, 3: 2},
            "gen_01_A": {0: 0.5, 1: 2.5, 2: 0.5, 3: 2.5},
            "gen_02_B": {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0},
        }
    )

    assert_frame_equal(results, expected_results)


def test_sg_filter_threshold(dsk_proj):
    dsk = dsk_proj

    A = [0, 100, 1000, 2000, 1000, 100, 0, 100, 1000, 2000]
    B = [0, -100, -1000, -2000, -1000, -100, 0, -100, -1000, -2000]
    segments = [[x] * len(A) for x in range(2)]
    flat_segments = [item for sublist in segments for item in sublist]

    df = pd.DataFrame({"Ax": A + B, "SegmentID": flat_segments})

    dsk.upload_dataframe("test_data", df, force=True)
    dsk.pipeline.reset(delete_cache=True)
    dsk.pipeline.set_input_data(
        "test_data.csv", data_columns=["Ax"], group_columns=["SegmentID"]
    )
    dsk.pipeline.add_transform(
        "Segment Filter Threshold",
        params={"input_column": "Ax", "threshold": 1, "comparison": 0},
    )
    results, stats = dsk.pipeline.execute()

    expected_results = pd.DataFrame({"Ax": B, "SegmentID": [1] * len(B)})
    assert_frame_equal(results, expected_results)


def create_ground_data(
    dsk, sensor_columns, window_size=50, num_classes=3, num_iterations=50
):
    df = dsk.datasets.generate_step_data(
        window_size=window_size,
        num_classes=num_classes,
        noise_scale=5,
        num_iterations=num_iterations,
    )
    for index, column in enumerate(sensor_columns):
        df[column] = dsk.datasets.generate_step_data(
            window_size=window_size,
            num_classes=num_classes,
            noise_scale=5,
            scale_factor=index * 10,
            num_iterations=num_iterations,
        )["Data"]
    df.drop("Data", axis=1, inplace=True)
    df["Subject"] = 0

    return df
