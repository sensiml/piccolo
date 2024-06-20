import os
import pytest
import os.path
import pytest


class PipelineFailedException(Exception):
    pass


def check_result(dsk, results):
    if results is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


@pytest.mark.skip(reason="Currently broken/not updated in a while")
def test_model_generation_double_twist(ClientConnection, DataDir):
    dsk = ClientConnection
    project_name = "DoubelTwistFuncTest"

    prj = dsk.projects.get_project_by_name(project_name)

    if prj is not None:
        prj.delete()

    dsk.upload_project(
        project_name,
        dclprojpath="{}/projects/Chilkat Gesture Double Twist/Chilkat Gesture Double Twist.dclproj".format(
            DataDir
        ),
    )

    dsk.project = project_name
    dsk.pipeline = "double_twist_pipeline"

    segmenters = dsk.list_segmenters()
    segmenter_id = int(segmenters[segmenters["name"] == "Double"]["id"].values[0])

    query_name = "query_general"
    sensor_columns = list(dsk.project.columns())

    q = dsk.create_query(
        query_name,
        columns=sensor_columns,
        label_column="Gesture",
        segmenter=segmenter_id,
        metadata_columns=["Subject"],
        force=True,
    )

    dsk.pipeline.reset()
    dsk.pipeline.set_input_query(query_name)

    dsk.pipeline.add_transform(
        "Strip",
        params={
            "input_columns": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
            "type": "mean",
        },
    )

    dsk.pipeline.add_feature_generator(
        [{"name": "Downsample with Min Max Scaling", "params": {"new_length": 12}}],
        function_defaults={"columns": sensor_columns},
        params={"group_columns": ["Subject", "Gesture", "SegmentID"]},
    )

    dsk.pipeline.add_feature_selector(
        [
            {
                "name": "Information Gain",
                "params": {
                    "feature_number": 2,
                },
            }
        ],
        params={"number_of_features": 6},
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

    fg, s = dsk.pipeline.execute()

    assert fg.shape == (89, 9)

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )

    dsk.pipeline.set_training_algorithm(
        "Hierarchical Clustering with Neuron Optimization",
        params={"number_of_neurons": 25},
    )

    dsk.pipeline.set_tvo(
        {
            "label_column": "Gesture",
            "ignore_columns": ["Subject", "SegmentID"],
            "reserve_test_set": False,
            "validation_seed": 0,
        }
    )

    results, extra = dsk.pipeline.execute()

    check_result(dsk, results)

    model = results.configurations[0].models[0]

    rec_r, s = model.recognize_signal(capturefile="MarcG_S 2019-01-07 12_30_27.csv")

    r_c, s = model.recognize_signal(
        capturefile="MarcG_S 2019-01-07 12_30_27.csv", platform="cloud"
    )

    assert len(r_c) == len(rec_r)  # check for the same number of segments

    assert [x[0] for x in r_c["CategoryVector"].values] == list(
        rec_r["Classification"].values
    )  # check for the same classifications

    fv_c, s = model.recognize_signal(
        capturefile="MarcG_S 2019-01-07 12_30_27.csv", stop_step=4, platform="cloud"
    )

    # check for the feature vectors

    dsk.pipeline.delete_sandbox()
