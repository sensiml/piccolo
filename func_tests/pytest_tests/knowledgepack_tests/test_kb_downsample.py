import sys

import numpy as np
import pandas as pd
import pytest
from pandas import DataFrame


@pytest.mark.skip(reason="Currently broken/not updated in a while")
def test_streaming_downsample_kp(ClientConnection, DataDir):
    dsk = ClientConnection
    project_name = "Sample Debug Test"
    prj = dsk.projects.get_project_by_name(project_name)
    if prj is not None:
        prj.delete()
    dsk.project = project_name
    dsk.pipeline = "WindowingTest"

    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    window_size = 20
    num_classes = 3
    num_iterations = 5

    df = dsk.datasets.generate_step_data(
        window_size=window_size,
        num_classes=num_classes,
        noise_scale=1,
        num_iterations=num_iterations,
    )

    for index, column in enumerate(sensor_columns):
        df[column] = dsk.datasets.generate_step_data(
            window_size=window_size,
            num_classes=num_classes,
            noise_scale=1,
            scale_factor=(index + 1) * 10,
            num_iterations=num_iterations,
        )["Data"]
    df.drop("Data", axis=1, inplace=True)

    dsk.upload_dataframe("window_test", df, force=True)

    dsk.pipeline.reset()
    dsk.pipeline.set_input_data(
        "window_test",
        group_columns=["Label"],
        label_column="Label",
        data_columns=sensor_columns,
    )

    dsk.pipeline.add_transform(
        "Streaming Downsample",
        params={"input_columns": dsk.pipeline.data_columns, "filter_length": 4},
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": window_size // 4, "delta": window_size // 4}
    )

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Mean", "params": {"columns": sensor_columns}},
        ]
    )

    dsk.pipeline.add_transform("Min Max Scale")

    r, s = dsk.pipeline.execute()

    assert len(r) == 15

    r, s = dsk.pipeline.data(1)
    assert DataFrame(r).shape[0] == 75

    r, s = dsk.pipeline.data(2)
    assert DataFrame(r).shape[0] == 75

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_classifier("PME", params={"max_aif": 45, "min_aif": 1})

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={"number_of_iterations": 1, "number_of_neurons": 3},
    )

    dsk.pipeline.set_tvo({"validation_seed": 0})

    results, stats = dsk.pipeline.execute(describe=False)

    model = results.configurations[0].models[0]

    dsk.upload_dataframe("test_data.csv", df[sensor_columns], force=True)

    r_em = model.knowledgepack.recognize_signal(
        datafile="test_data.csv", platform="emulator"
    )

    r2 = model.knowledgepack.recognize_signal(
        datafile="test_data.csv", stop_step=4, platform="cloud"
    )

    def checkEqual(L1, L2):
        return len(L1) == len(L2) and L1 == L2

    for i in range(len(r_em[0])):
        assert checkEqual(list(r2[0].T[i].values[:3]), r_em[0]["FeatureVector"][i])
