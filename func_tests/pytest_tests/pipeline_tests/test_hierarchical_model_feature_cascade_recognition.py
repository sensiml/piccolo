# get_ipython().magic(u'matplotlib inline')
import os
import os.path
import sys

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def project_setup(dsk_random_project):
    dsk = dsk_random_project

    dsk.pipeline = "test_hierarchical_model"

    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    window_size = 200
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

    rmap = {1: "A", 2: "B", 3: "C"}
    df["Label"] = df["Label"].apply(lambda x: rmap[x])
    df.plot()

    test_file_names = []
    for i in range(5):
        df["Subject"] = i
        dsk.upload_dataframe("window_test_{}".format(i), df, force=True)
        test_file_names.append("window_test_{}.csv".format(i))

    return dsk, test_file_names


def run_pipelines(dsk, test_file_names, slide):
    dsk.pipeline.reset()

    dsk.pipeline.set_input_data(
        test_file_names,
        data_columns=["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        group_columns=["Subject", "Label"],
        label_column="Label",
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 50, "delta": 50, "train_delta": 0}
    )

    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Sum",
                "params": {
                    "columns": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
                },
            },
            {
                "name": "Absolute Sum",
                "params": {
                    "columns": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
                },
            },
        ]
    )

    dsk.pipeline.add_transform(
        "Feature Cascade", params={"num_cascades": 2, "slide": slide}
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "pad": 0,
            "feature_min_max_parameters": {},
        },
    )

    dsk.pipeline.add_transform(
        "Combine Labels",
        params={"combine_labels": {"combined_label_0": ["A", "B"], "C": ["C"]}},
    )

    dsk.pipeline.add_transform(
        "Sample By Metadata",
        params={"metadata_name": "Label", "metadata_values": ["combined_label_0", "C"]},
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={
            "distance_mode": "Lsup",
            "classification_mode": "KNN",
            "max_aif": 250,
            "min_aif": 20,
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={"number_of_iterations": 50, "number_of_neurons": 10},
    )

    dsk.pipeline.set_tvo({"validation_seed": 0})

    r, s = dsk.pipeline.execute()

    model = r.configurations[0].models[0]

    model.knowledgepack.save("parent")

    kp_parent = model.knowledgepack

    dsk.pipeline.reset()

    dsk.pipeline.set_input_data(
        test_file_names,
        data_columns=["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        group_columns=["Subject", "Label"],
        label_column="Label",
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 50, "delta": 50, "train_delta": 0}
    )

    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Sum",
                "params": {
                    "columns": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
                },
            },
            {
                "name": "Absolute Sum",
                "params": {
                    "columns": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
                },
            },
        ]
    )

    dsk.pipeline.add_transform(
        "Feature Cascade", params={"num_cascades": 2, "slide": slide}
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "pad": 0,
            "feature_min_max_parameters": {},
        },
    )

    dsk.pipeline.add_transform(
        "Sample By Metadata",
        params={"metadata_name": "Label", "metadata_values": ["A", "B"]},
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={
            "distance_mode": "Lsup",
            "classification_mode": "KNN",
            "max_aif": 250,
            "min_aif": 20,
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={"number_of_iterations": 50, "number_of_neurons": 10},
    )

    dsk.pipeline.set_tvo({"validation_seed": 0})

    r, s = dsk.pipeline.execute()

    print(r)

    model = r.configurations[0].models[0]

    model.knowledgepack.save("parent")

    kp_child = model.knowledgepack

    import copy

    report_map = copy.deepcopy(kp_parent.class_map)
    for k, v in report_map.items():
        if v == "combined_label_0":
            report_map[k] = "Child"
        else:
            report_map[k] = "Report"

    kb_description = {
        "Parent": {"uuid": kp_parent.uuid, "source": "Custom", "results": report_map},
        "Child": {
            "uuid": kp_child.uuid,
            "parent": "Parent",
            "results": {"1": "Report", "2": "Report"},
            "segmenter_from": "Parent",
        },
    }

    return kp_parent, kp_child, kb_description


def almost_equal(A, B, diff):
    count = 0
    for index, value in enumerate(A):
        if value != B[index]:
            count += 1

    if count > diff:
        return False

    return True


def test_hierarchical_model_feature_cascade_slide_codegeneration(project_setup):
    dsk, test_file_names = project_setup

    kp_parent, _, kp_description = run_pipelines(
        dsk, test_file_names=test_file_names, slide=False
    )

    rec, _ = kp_parent.recognize_signal(
        datafile="window_test_0.csv", kb_description=kp_description
    )

    assert rec.shape[0] == 30

    expected_classifications = [
        "A",
        "A",
        "B",
        "B",
        "C",
        "C",
        "C",
        "C",
        "B",
        "B",
        "A",
        "A",
        "A",
        "A",
        "B",
        "B",
        "C",
        "C",
        "C",
        "C",
        "B",
        "B",
        "A",
        "A",
        "A",
        "A",
        "B",
        "B",
        "C",
        "C",
    ]

    assert rec.ClassificationName.values.tolist() == expected_classifications

    expected_model_names = [
        "Child",
        "Child",
        "Child",
        "Child",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Parent",
        "Parent",
    ]

    assert rec.ModelName.values.tolist() == expected_model_names


def test_hierarchical_model_feature_cascade_reset_codegeneration(project_setup):
    dsk, test_file_names = project_setup

    kp_parent, _, kp_description = run_pipelines(
        dsk, test_file_names=test_file_names, slide=True
    )

    rec, _ = kp_parent.recognize_signal(
        datafile="window_test_0.csv", kb_description=kp_description
    )

    assert rec.shape[0] == 59

    expected_classifications = [
        "A",
        "A",
        "A",
        "A",
        "A",
        "B",
        "B",
        "B",
        "B",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "B",
        "B",
        "B",
        "B",
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "B",
        "B",
        "B",
        "B",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "B",
        "B",
        "B",
        "B",
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "B",
        "B",
        "B",
        "B",
        "C",
        "C",
        "C",
        "C",
    ]

    assert almost_equal(
        rec.ClassificationName.values.tolist(), expected_classifications, 10
    )

    expected_model_names = [
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Child",
        "Parent",
        "Parent",
        "Parent",
        "Parent",
    ]

    assert almost_equal(rec.ModelName.values.tolist(), expected_model_names, 10)
