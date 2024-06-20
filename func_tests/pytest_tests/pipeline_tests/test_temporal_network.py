import os
import os.path
import shutil
import sys
from uuid import *

import numpy as np
import pandas as pd
import pytest
from rest_framework import status


class PipelineFailedException(Exception):
    pass


def remove(path):
    """param <path> could either be relative or absolute."""
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


def check_result(dsk, results):
    if results is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


@pytest.fixture
def client_project_pipeline(dsk_random_project):
    client = dsk_random_project

    client.pipeline = "temporal_network"

    data = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "kw_spotting_test_data.csv")
    )
    client.upload_dataframe("kw_spotting_test_data.csv", data, force=True)

    client.pipeline.set_input_data(
        "kw_spotting_test_data.csv",
        data_columns=["channel_0"],
        group_columns=["SegmentID", "segment_uuid", "Label"],
        label_column="Label",
    )

    client.pipeline.add_transform(
        "Windowing", params={"window_size": 480, "delta": 320, "train_delta": 0}
    )

    client.pipeline.add_feature_generator(
        [
            {
                "name": "MFCC",
                "params": {
                    "columns": ["channel_0"],
                    "sample_rate": 16000,
                    "cepstra_count": 23,
                },
            }
        ]
    )

    client.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "pad": 0,
            "feature_min_max_parameters": {},
            "feature_min_max_defaults": {"maximum": 200000, "minimum": -200000},
        },
    )

    client.pipeline.add_transform(
        "Feature Cascade",
        params={"num_cascades": 49, "slide": False, "training_slide": True},
    )

    client.pipeline.execute()

    return client


###########################################################
# testing the keyword spotting pipeline
# testing the knowledge pack with additional background data


def test_temporal_network(client_project_pipeline):
    client = client_project_pipeline

    client.pipeline.set_classifier("TensorFlow Lite for Microcontrollers", params={})

    client.pipeline.set_validation_method("Recall")

    client.pipeline.set_training_algorithm(
        "Train Temporal Convolutional Neural Network",
        params={
            "final_activation": "softmax",
            "dense_layers": [8],
            "training_size_limit": 5,
            "validation_size_limit": 5,
            "batch_normalization": True,
            "drop_out": 0.1,
            "random_sparse_noise": True,
            "random_bias_noise": True,
            "random_frequency_mask": True,
            "random_time_mask": True,
            "epochs": 5,
            "batch_size": 4,
            "threshold": 0.6,
            "early_stopping_threshold": 0.50,
            "early_stopping_patience": 1,
            "loss_function": "categorical_crossentropy",
            "learning_rate": 0.01,
            "tensorflow_optimizer": "adam",
            "metrics": "accuracy",
            "input_type": "int8",
            "estimator_type": "classification",
            "number_of_temporal_blocks": 3,
            "number_of_temporal_layers": 2,
            "number_of_convolutional_filters": 4,
            "kernel_size": 3,
            "residual_block": True,
            "initial_dilation_rate": 1,
            "number_of_latest_temporal_features": 5,
            "quantization_aware_step": False,
        },
    )

    client.pipeline.set_tvo({"validation_seed": 0})

    results, stats = client.pipeline.execute()

    print(results)
    check_result(client, results)

    assert stats["feature_table"].shape == (1127, 11)

    #### Test1: background noise ####
    model = results.configurations[0].models[0]

    out = model.knowledgepack.recognize_signal(
        test_plan={
            "background": "test_noise_rate16k_60sec.wav",
            "back_max_level": 450,
            "background_factor": 450,
            "sample_rate": 16000,
        }
    )

    assert len(out) == 2

    results = out[0]
    summary = out[1]

    class_map = model.knowledgepack.class_map
    classes = [v for k, v in class_map.items()]

    assert type(results) == pd.DataFrame

    N = results.shape[0]

    for i in range(N):
        assert len(results.FeatureVector.loc[i]) == 1127
        assert len(results.OutputTensor.loc[i]) == len(classes)

    for c, n in summary["summary"]["class_count"].items():
        assert c in classes
