import pytest
import os
import pandas as pd
import datetime


class PipelineFailedException(Exception):
    pass


def check_result(dsk, r):
    if r is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


@pytest.mark.skip(reason="Currently broken/not updated in a while")
def test_knowledge_pack_download_subtype_calls(ClientConnection, DataDir):
    dsk = ClientConnection
    prj = dsk.projects.get_project_by_name("SubTypes_Calls_Project")
    if prj is not None:
        prj.delete()
    dsk.project = "SubTypes_Calls_Project"
    dsk.pipeline = "SubTypeCallsSandBox"

    df = pd.read_csv(
        "{}/kbbasics/activities_combinedSignalsWithLabel_tiny.csv".format(DataDir)
    )
    df = df.rename(columns={"Class": "Activity"})
    # df['GyroscopeX'] = df['AccelerometerX']
    # df['GyroscopeY'] = df['AccelerometerY']
    # df['GyroscopeZ'] = df['AccelerometerZ']
    # sensor_columns = ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ', 'GyroscopeX', 'GyroscopeY', 'GyroscopeZ']
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
            {"subtype_call": "Time", "params": {"sample_rate": 100}},
        ],
        function_defaults={"columns": sensor_columns},
    )

    dsk.pipeline.add_transform("Min Max Scale")

    dsk.pipeline.set_validation_method(
        "Stratified K-Fold Cross-Validation", params={"number_of_folds": 3}
    )
    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )
    dsk.pipeline.set_training_algorithm(
        "Hierarchical Clustering with Neuron Optimization",
        params={"number_of_neurons": 30, "cluster_method": "DLHC"},
    )
    dsk.pipeline.set_tvo({"validation_seed": 1})

    subtypes = [
        {"subtype_call": "Time", "params": {"sample_rate": 100}},
        {"subtype_call": "Rate of Change"},
        {"subtype_call": "Statistical"},
        {"subtype_call": "Energy"},
        {"subtype_call": "Amplitude", "params": {"smoothing_factor": 9}},
        {"subtype_call": "Column Fusion"},
        {"subtype_call": "Convolution"},
        {"subtype_call": "Frequency", "params": {"sample_rate": 100}},
    ]

    failed = []
    for subtype in subtypes:
        dsk.pipeline.add_feature_generator(
            [subtype],
            function_defaults={"columns": sensor_columns},
        )
        r, s = dsk.pipeline.execute()
        check_result(dsk, r)
        model = r.configurations[0].models[0].knowledgepack

        for platform in dsk.platforms:
            if platform is None:
                print("None Platform")
                break

            for debug_flag in [True]:
                config = platform.get_config(debug=debug_flag)

                if platform.can_build_binary:
                    print("\n##################################")
                    print(
                        "Platform:",
                        platform.platform,
                        "Board Name:",
                        platform.board_name,
                    )
                    print("Download binary, debug: {}".format(debug_flag))
                    print("###################################\n")
                    res = model.download_binary(config=config)
                    if res is False:
                        failed.append((subtype, platform.platform, config, "binary"))

                print("\n#################################")
                print(
                    "Platform:", platform.platform, "Board Name:", platform.board_name
                )
                print("Download Library debug: {}".format(debug_flag))
                print("####################################\n")
                # config["kb_description"] = {"CascadeTest2": {"uuid": "fa7c0057-3c7d-4f0e-a6b2-2b5c65ea349b", "results": {"1 ": "Report", "3 ": "Report", "2 ": "Report"}, "source": "Custom"}}
                res = model.download_library(config=config)

                if res is False:
                    failed.append((subtype, platform.platform, config, "library"))

    if failed:
        from json import dumps

        print(dumps(failed, indent=True))
        raise Exception("Not All Platforms Were able to be downloaded")
