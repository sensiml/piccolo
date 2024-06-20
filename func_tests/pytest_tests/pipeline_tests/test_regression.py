# get_ipython().magic(u'matplotlib inline')
import os
import os.path
import sys

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def expected_results():
    return np.array(
        [
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
            1,
            2,
            2,
            1,
        ]
    )


@pytest.fixture
def dsk_project_pipeline(dsk_random_project):
    dsk = dsk_random_project

    dsk.pipeline = "test_binary_classification"
    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    window_size = 50
    num_classes = 2
    num_iterations = 20

    df = dsk.datasets.generate_harmonic_data(
        window_size=window_size,
        num_classes=num_classes,
        noise_scale=1,
        num_iterations=num_iterations,
    )
    for index, column in enumerate(sensor_columns):
        df[column] = dsk.datasets.generate_harmonic_data(
            window_size=window_size,
            num_classes=num_classes,
            noise_scale=1,
            scale_factor=(index + 1) * 10,
            num_iterations=num_iterations,
        )["Data"]
    df.drop("Data", axis=1, inplace=True)
    df["Subject"] = 0

    dsk.upload_dataframe("window_test", df, force=True)

    rmap = {1: 1, 2: 2, 3: 3}
    df["Label"] = df["Label"].apply(lambda x: rmap[x])

    dsk.pipeline.reset()

    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]

    dsk.pipeline.set_input_data(
        "window_test.csv",
        data_columns=sensor_columns,
        group_columns=["Subject", "Label"],
        label_column="Label",
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": window_size, "delta": window_size}
    )

    dsk.pipeline.add_feature_generator(
        [{"name": "Sum", "params": {"columns": sensor_columns}}]
    )

    dsk.pipeline.add_transform("Min Max Scale")

    dsk.pipeline.execute()

    return dsk


class PipelineFailedException(Exception):
    pass


def check_result(dsk, results):
    if results is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


def test_ordinary_least_squares_linear_regression(
    dsk_project_pipeline, expected_results
):
    dsk = dsk_project_pipeline

    dsk.pipeline.set_regression("Linear Regression", params={})

    dsk.pipeline.set_training_algorithm(
        "Ordinary Least Squares",
        params={
            "fit_intercept": True,
            "positive": False,
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="window_test.csv")

    assert r.shape == (40, 10)

    assert "Result" in r.columns


def test_l2_ridge_linear_regression(dsk_project_pipeline, expected_results):
    dsk = dsk_project_pipeline

    dsk.pipeline.set_regression("Linear Regression", params={})

    dsk.pipeline.set_training_algorithm(
        "L2 Ridge",
        params={
            "fit_intercept": True,
            "positive": False,
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="window_test.csv")

    assert r.shape == (40, 10)

    assert "Result" in r.columns


def test_l1_lasso_linear_regression(dsk_project_pipeline, expected_results):
    dsk = dsk_project_pipeline

    dsk.pipeline.set_regression("Linear Regression", params={})

    dsk.pipeline.set_training_algorithm(
        "L1 Lasso",
        params={
            "fit_intercept": True,
            "positive": False,
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="window_test.csv")

    print(r)

    assert r.shape == (40, 10)

    assert "Result" in r.columns
