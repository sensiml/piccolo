import os
import os.path

import numpy as np
import pandas as pd
import pytest


class PipelineFailedException(Exception):
    pass


def check_result(dsk, results):
    if results is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


def test_cascade_windowing(dsk_random_project):
    dsk = dsk_random_project

    dsk.pipeline = "Test Pipeline"

    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    window_size = 80

    df = pd.read_csv(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "data/test_cascade_windowing_input_data.csv",
        )
    )

    dsk.upload_dataframe("window_test.csv", df, force=True)

    dsk.pipeline.reset()

    dsk.pipeline.set_input_data(
        "window_test.csv",
        group_columns=["Subject", "Label"],
        label_column="Label",
        data_columns=sensor_columns,
    )

    dsk.pipeline.add_transform(
        "Windowing Threshold Segmentation",
        params={
            "column_of_interest": "AccelerometerX",
            "window_size": window_size,
            "vt_threshold": 1.0,
            "threshold_space_width": 25,
            "threshold_space": "std",
            "return_segment_index": False,
        },
    )

    df_segment_id, s = dsk.pipeline.execute()

    df_segment_id["segment_uuid"] = df_segment_id.SegmentID
    df_segment_id = df_segment_id.drop(["SegmentID"], axis=1)
    assert df_segment_id.shape == (960, 6)

    dsk.upload_dataframe("window_segments", df_segment_id, force=True)

    dsk.pipeline.reset()
    num_cascades = 4

    dsk.pipeline.set_input_data(
        "window_segments.csv",
        group_columns=["Subject", "Label", "segment_uuid"],
        label_column="Label",
        data_columns=sensor_columns,
    )

    dsk.pipeline.add_transform(
        "Windowing",
        params={
            "window_size": window_size // num_cascades,
            "delta": window_size // num_cascades,
        },
    )

    df_cascade_segment_id, s = dsk.pipeline.execute()

    assert df_cascade_segment_id.shape == (960, 7)

    dsk.pipeline.add_feature_generator(
        [{"name": "Mean", "params": {"columns": sensor_columns[1:]}}]
    )

    dsk.pipeline.add_transform(
        "Feature Cascade", params={"num_cascades": num_cascades, "slide": False}
    )

    dsk.pipeline.add_transform("Min Max Scale")

    results, stats = dsk.pipeline.execute()

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={"number_of_iterations": 50, "number_of_neurons": 10},
    )

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()
    model = results.configurations[0].models[0]

    r, s = model.recognize_signal(datafile="window_test.csv", platform="emulator")

    """
    r.to_csv(        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "data/test_cascade_windowing_slide_false.csv",
    ),index=None)
    """

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "data/test_cascade_windowing_slide_false.csv",
        )
    )

    assert r.shape == expected_results.shape

    dsk.pipeline.add_transform(
        "Feature Cascade",
        params={
            "num_cascades": num_cascades,
            "slide": True,
            "group_columns": ["Label", "SegmentID", "Subject", "segment_uuid"],
        },
    )
    results, stats = dsk.pipeline.execute()
    model = results.configurations[0].models[0]

    r, s = model.recognize_signal(datafile="window_test.csv", platform="emulator")

    """r.to_csv(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "data/test_cascade_windowing_slide_true.csv"
    ),index=None)"""

    expected_results = pd.read_csv(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "data/test_cascade_windowing_slide_true.csv",
        )
    )

    assert r.shape == expected_results.shape
