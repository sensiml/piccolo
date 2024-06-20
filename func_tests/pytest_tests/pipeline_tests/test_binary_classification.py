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

    rmap = {1: "A", 2: "B"}
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


def test_binary_class_boosted_decision_tree(dsk_project_pipeline, expected_results):
    dsk = dsk_project_pipeline
    dsk.pipeline.set_classifier("Boosted Tree Ensemble", params={})
    dsk.pipeline.set_training_algorithm(
        "xGBoost", params={"max_depth": 2, "n_estimators": 100}
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="window_test.csv")

    print(r)

    assert np.array_equal(r.Classification.values, expected_results)


def test_binary_class_boosted_decision_tree_large_classes(
    dsk_project_pipeline, expected_results
):
    client = dsk_project_pipeline
    client.pipeline = "large_class"
    fv = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "large_training_data.csv")
    )
    client.upload_feature_dataframe("input_features.csv", fv)

    client.pipeline.reset(delete_cache=True)
    client.pipeline.set_input_features(
        "input_features.csv",
        feature_columns=[
            "gen_0001_accXmfcc_000001",
            "gen_0002_accYmfcc_000001",
            "gen_0003_accZmfcc_000000",
            "gen_0004_Magnitude_ST_0000mfcc_000001",
            "gen_0004_Magnitude_ST_0000mfcc_000002",
            "gen_0004_Magnitude_ST_0000mfcc_000004",
            "gen_0006_accYNegativeZeroCrossings",
            "gen_0007_accZNegativeZeroCrossings",
            "gen_0008_accXPositiveZeroCrossings",
            "gen_0016_Magnitude_ST_0000Sum",
            "gen_0018_Magnitude_ST_0000Variance",
            "gen_0019_accXLinearRegressionIntercept_0001",
            "gen_0019_accXLinearRegressionStdErr_0003",
            "gen_0023_accYmaximum",
            "gen_0025_accXminimum",
            "gen_0026_accYminimum",
        ],
        group_columns=["SegmentID", "add_label", "segment_uuid"],
        label_column="Label",
    )

    client.pipeline.set_validation_method(
        "Stratified K-Fold Cross-Validation", params={"number_of_folds": 3}
    )
    client.pipeline.set_classifier("Boosted Tree Ensemble", params={})
    client.pipeline.set_training_algorithm(
        "xGBoost",
        params={
            "max_depth": 5,
            "n_estimators": 80,
        },
    )
    client.pipeline.set_tvo()

    results, stats = client.pipeline.execute()

    assert results == {
        "status": "FAILURE",
        "message": "Status: Failed - Gradient Boosting currently only supports binary classification",
        "detail": {
            "step_index": 2,
            "step_type": "tvo",
            "step_name": "tvo",
            "total_steps": 2,
            "name": "tvo",
            "batch": "1",
        },
        "errors": [],
        "execution_type": "pipeline",
    }


def test_binary_class_random_forest(dsk_project_pipeline, expected_results):
    dsk = dsk_project_pipeline

    dsk.pipeline.set_classifier("Decision Tree Ensemble", params={})
    dsk.pipeline.set_training_algorithm(
        "Random Forest", params={"max_depth": 6, "n_estimators": 15}
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="window_test.csv")

    assert np.array_equal(r.Classification.values, expected_results)


def test_binary_class_bonsai(dsk_project_pipeline, expected_results):
    dsk = dsk_project_pipeline

    dsk.pipeline.set_classifier("Bonsai", params={})

    dsk.pipeline.set_training_algorithm(
        "Bonsai Tree Optimizer",
        params={
            "projection_dimension": 2,
            "tree_depth": 4,
            "sigma": 1.0,
            "epochs": 100,
            "batch_size": 5,
            "reg_W": 0.001,
            "reg_V": 0.001,
            "reg_Theta": 0.001,
            "reg_Z": 0.0001,
            "sparse_V": 1,
            "sparse_Theta": 1,
            "sparse_W": 1,
            "sparse_Z": 1,
            "learning_rate": 0.001,
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="window_test.csv")

    assert np.array_equal(r.Classification.values, expected_results)


def test_binary_class_pme(dsk_project_pipeline, expected_results):
    dsk = dsk_project_pipeline
    dsk.pipeline.set_classifier(
        "PME",
        params={
            "distance_mode": "L1",  # options: <L1/DTW>,
            "classification_mode": "RBF",  # options: <RBF/KNN>,
            "max_aif": 16384,
            "min_aif": 2,
            "reserved_patterns": 0,
            "reinforcement_learning": False,
        },
    )

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 100,
            "turbo": True,
            "number_of_neurons": 2,
            "aggressive_neuron_creation": True,
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="window_test.csv")

    assert np.array_equal(r.Classification.values, expected_results)
    assert len(r.OutputTensor.iloc[0]) == 4


def test_binary_class_fully_connected_nn(dsk_project_pipeline, expected_results):
    dsk = dsk_project_pipeline

    dsk.pipeline.set_classifier("TensorFlow Lite for Microcontrollers", params={})

    dsk.pipeline.set_training_algorithm(
        "Train Fully Connected Neural Network",
        params={
            "estimator_type": "classification",  # options: <classification/regression>,
            "dense_layers": [8],
            "drop_out": 0.1,
            "threshold": 0.0,
            "learning_rate": 0.01,
            "batch_size": 8,
            "loss_function": "categorical_crossentropy",  # options: <categorical_crossentropy>,
            "tensorflow_optimizer": "adam",  # options: <adam>,
            "final_activation": "softmax",  # options: <softmax>,
            "epochs": 100,
            "metrics": "accuracy",  # options: <accuracy>,
        },
    )

    dsk.pipeline.set_validation_method(
        "Stratified Shuffle Split",
        params={
            "test_size": 0.0,
            "validation_size": 0.2,
            "number_of_folds": 1,
        },
    )

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="window_test.csv")

    assert np.array_equal(r.Classification.values, expected_results)

    # below, we test for the presence of the output tensor
    # column in the table returned by recognize signal

    assert "OutputSize" in r.columns
    assert "OutputTensor" in r.columns

    n_class = len(model.knowledgepack.class_map)

    for size in r.OutputSize.values:
        assert size == n_class

    for tensor in r.OutputTensor.values:
        assert len(tensor) == n_class
