import datetime
import os

import pandas as pd
import pytest


class PipelineFailedException(Exception):
    pass


def check_result(dsk, r):
    if r is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


@pytest.mark.parametrize(
    "subtype",
    [
        "Time",
        "Rate of Change",
        "Statistical",
        "Energy",
        "Amplitude",
        "Column Fusion",
        "Frequency",
    ],
)
def test_subtype_calls(subtype, dsk_random_project, DataDir):
    dsk = dsk_random_project
    dsk.pipeline = "SubType_{}".format(subtype)

    df = pd.read_csv(
        "{}/kbbasics/activities_combinedSignalsWithLabel_tiny.csv".format(DataDir)
    )
    df = df.rename(columns={"Class": "Activity"})

    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    df.head()

    dsk.pipeline.set_columns(
        data_columns=sensor_columns,
    )

    dsk.upload_dataframe("grid_dataframe1", df, force=True)

    dsk.pipeline.reset()
    dsk.pipeline.set_input_data(
        "grid_dataframe1.csv",
        data_columns=sensor_columns,
        group_columns=["Subject", "Activity"],
        label_column="Activity",
    )  # , force=True)

    dsk.pipeline.add_transform("Windowing", params={"window_size": 200, "delta": 200})

    dsk.pipeline.add_feature_generator(
        [
            {
                "subtype_call": subtype,
                "params": {"sample_rate": 100, "smoothing_factor": 9},
            }
        ],
        function_defaults={"columns": sensor_columns},
    )

    dsk.pipeline.add_transform("Min Max Scale")

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={"number_of_iterations": 1, "number_of_neurons": 20},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    r, s = dsk.pipeline.execute()
    check_result(dsk, r)

    print(dsk.pipeline.name)
    print(dsk.project.name)
    model = r.configurations[0].models[0].knowledgepack
    print(model.uuid)

    res, stat = model.recognize_signal(datafile="grid_dataframe1.csv")

    if not isinstance(res, pd.DataFrame):
        print(res)
        raise Exception("Subtype {} Failed".format(subtype))
