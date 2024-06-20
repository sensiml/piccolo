import os
import pandas as pd
import pytest
from six import string_types


imu_sensors = [
    "AccelerometerX",
    "AccelerometerY",
    "AccelerometerZ",
    "GyroscopeX",
    "GyroscopeY",
    "GyroscopeZ",
]

dogcommands_data = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "../auto_sense", "data/dogcommands.csv")
)

dogcommands_data.columns = imu_sensors + ["CaptureID", "Label"]


def init_imu_pipeline(dsk, data):

    dsk.upload_dataframe("dogcommand.csv", data, force=True)

    dsk.pipeline = "test_autosense_piepline"

    dsk.pipeline.reset()

    dsk.pipeline.set_input_data(
        "dogcommand.csv",
        data_columns=imu_sensors,
        group_columns=["Label", "CaptureID"],
        label_column="Label",
    )

    return dsk


def imu_model_builder_pipeline(dsk):

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Absolute Sum", "params": {"columns": imu_sensors}},
            {"name": "25th Percentile", "params": {"columns": imu_sensors}},
            {"name": "Zero Crossing Rate", "params": {"columns": imu_sensors}},
            {"name": "Average Energy", "params": {"columns": imu_sensors}},
            {"name": "Sum", "params": {"columns": imu_sensors}},
            {"name": "Mean", "params": {"columns": imu_sensors}},
        ]
    )

    dsk.pipeline.add_feature_selector(
        [{"name": "Information Gain", "params": {"feature_number": 2}}]
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={"min_bound": 0, "max_bound": 255, "feature_min_max_parameters": {}},
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={
            "distance_mode": "Lsup",
            "classification_mode": "KNN",
            "max_aif": 150,
            "min_aif": 80,
        },
    )

    dsk.pipeline.set_validation_method("Recall", params={})

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={"number_of_iterations": 1, "number_of_neurons": 25},
    )

    dsk.pipeline.set_tvo({"validation_seed": 0})

    return dsk


###########################################################################
# @pytest.mark.skip("Removing until can be reimplemented correctly")


def test_time_series_augmentation_1(dsk_random_project):

    dsk = init_imu_pipeline(dsk_random_project, dogcommands_data)

    dsk.pipeline.add_transform("Windowing", params={"window_size": 39, "delta": 39})

    r1, s1 = dsk.pipeline.execute()

    dsk.pipeline.add_augmentation(
        [
            {
                "name": "Add Noise",
                "params": {
                    "background_scale_range": [1, 5],
                    "fraction": 1,
                    "noise_types": ["pink", "white"],
                },
            },
            {
                "name": "Scale Amplitude",
                "params": {
                    "scale_range": [1, 5],
                    "fraction": 1,
                },
            },
            {
                "name": "Time Stretch",
                "params": {
                    "stretch_factor_range": [1, 1],
                    "fraction": 1,
                },
            },
            {
                "name": "Pitch Shift",
                "params": {
                    "shift_range": [0, 0],
                    "step_per_octave": 4,
                    "sample_rate": 100,
                    "fraction": 1,
                },
            },
        ],
    )

    r2, s2 = dsk.pipeline.execute(verbose=True)

    n_augmentation = 4
    assert r2.shape[0] == (1 + n_augmentation) * r1.shape[0]

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 30, "delta": 30}, overwrite=False
    )

    r3, s3 = dsk.pipeline.execute()

    assert r3.shape[0] / 30 == r2.shape[0] / 39

    dsk.pipeline.add_augmentation(
        [
            {
                "name": "Random Crop",
                "params": {
                    "crop_size": 15,
                    "overlap_factor": 1,
                },
            },
        ],
        overwrite=False,
    )

    r4, s4 = dsk.pipeline.execute()

    overlap_factor = 1
    n4_segments = r4.shape[0] / 15
    n3_segments = r3.shape[0] / 30
    assert n4_segments == (1 + overlap_factor) * (n3_segments * 30 / 15)

    dsk = imu_model_builder_pipeline(dsk)
    r, s = dsk.pipeline.execute()
    r.summarize()

    model = r.configurations[0].models[0]
    function_found = False
    for i in model.knowledgepack.pipeline_summary:
        if i["name"] == "augmentation_set":
            function_found = True
            break

    assert function_found


def test_time_series_augmentation_2(dsk_random_project):

    dsk = init_imu_pipeline(dsk_random_project, dogcommands_data[:30])

    dsk.pipeline.add_transform("Windowing", params={"window_size": 20, "delta": 20})

    # input: one segment of size 20
    dsk.pipeline.add_augmentation(
        [
            {
                "name": "Time Stretch",
                "params": {
                    "stretch_factor_range": [3, 3],
                    "fraction": 1,
                },
            },
        ],
        overwrite=False,
    )

    # input: one seg. of 20, one seg. of 60
    # seg of size 20 is passed unchanged
    # seg of size 60 is stretched by factor of 2 and passed
    dsk.pipeline.add_augmentation(
        [
            {
                "name": "Time Stretch",
                "params": {
                    "stretch_factor_range": [2, 2],
                    "fraction": 1,
                    "selected_segments_size_limit": [50, 1000],
                    "replace": True,
                },
            },
        ],
        overwrite=False,
    )
    # output: on seg of 20, and one seg of 60*2

    r1, s1 = dsk.pipeline.execute()

    assert r1.shape[0] == 140
