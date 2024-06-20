# get_ipython().magic(u'matplotlib inline')
import os
import os.path
import shutil
import sys

import numpy as np
import pandas as pd
import pytest


class KnowledgePackDownload(Exception):
    pass


def remove(path):
    """param <path> could either be relative or absolute."""
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


def utils_sml_runner(
    sml_runner,
    dsk,
    data_df,
    model_api="run_model",
    get_feature_vector=False,
    get_sensor_data=False,
    get_unscaled_feature_vector=False,
    kp=None,
):
    if kp is None:
        kp_list = dsk.pipeline.list_knowledgepacks()
        kp_uuid = kp_list.loc[0]["kp_uuid"]
        kp = dsk.get_knowledgepack(kp_uuid)

    os_type = sys.platform.lower()
    temp_folder = os.path.join(os.path.dirname(__file__), "tmp")

    del_tmp = False
    if not os.path.isdir(temp_folder):
        os.makedirs(temp_folder)
        del_tmp = True

    if "win" in os_type:
        platform_name = "Windows x86_64"
    else:  # linux darwin
        platform_name = "x86 GCC Generic"

    try:
        config = dsk.platforms_v2.get_platform_by_name(platform_name).get_config()
        kp_file = kp.download_library_v2(config=config, folder=temp_folder)[0]
        sml = sml_runner.SMLRunner(kp_file, class_map=kp.class_map)
        sml.init_model()
    except:
        raise KnowledgePackDownload

    # removing temporary files and folders
    if del_tmp:
        remove(temp_folder)
    else:
        remove(kp_file)

    rec_data = sml.recognize_capture(
        data_df,
        model_index=0,
        model_api=model_api,
        get_feature_vector=get_feature_vector,
        get_sensor_data=get_sensor_data,
        get_unscaled_feature_vector=get_unscaled_feature_vector,
    )

    return rec_data


@pytest.fixture
def sml_runner(request):
    decision = request.config.getoption("--rlocal")
    if decision.lower() in ("yes", "true", "y"):
        sys.path.insert(1, "../../../sensiml")
        sys.path.insert(1, "../../sensiml")
    from sensiml import sml_runner

    return sml_runner


def compare_features(df_e, df_c, tolerance=1):
    fv_e = np.array(df_e.FeatureVector.tolist())
    fv_c = df_c[[col for col in df_c.columns if "gen_" in col]].values

    assert fv_e.shape == fv_c.shape

    print((fv_e - fv_c) <= tolerance * fv_c.size)
    print(((fv_e - fv_c) <= tolerance * fv_c.size).sum())
    assert ((fv_e - fv_c) <= tolerance * fv_c.size).sum() == fv_c.size


def compare_classifications(df_e, df_c):
    r_e = df_e.ClassificationName.tolist()
    r_c = [x[0] if x else "Unknown" for x in df_c.MappedCategoryVector.tolist()]

    assert r_e == r_c


def get_train_data():
    df = pd.DataFrame()
    df["Axis_1"] = list(range(5, 201, 5))
    df["Axis_2"] = list(range(5, 201, 5))
    df["Label"] = "normal"
    return df


def get_test_data():
    df = pd.DataFrame()
    df["Axis_1"] = list(range(105, 251, 5))
    df["Axis_2"] = list(range(106, 252, 5))
    df["Label"] = "normal"

    return df


def get_train_data_1d():
    df = pd.DataFrame()
    df["Axis_1"] = list(range(5, 201, 5))
    df["Label"] = "normal"
    return df


def get_test_data_1d():
    df = pd.DataFrame()
    df["Axis_1"] = list(range(105, 251, 5))
    df["Label"] = "normal"

    return df


@pytest.fixture
def dsk_project_pipeline(dsk_random_project):
    client = dsk_random_project

    client.pipeline = "test pipline"

    # Upload training data
    client.upload_dataframe("train_file.csv", get_train_data(), force=True)

    # Upload testing data
    r = client.upload_dataframe("test_file.csv", get_test_data(), force=True)

    client.pipeline.reset()

    sensor_columns = ["Axis_1", "Axis_2"]

    client.pipeline.set_input_data(
        "train_file.csv",
        data_columns=sensor_columns,
        group_columns=["Label"],
        label_column="Label",
    )

    return client


@pytest.fixture
def dsk_project_pipeline_1d(dsk_random_project):
    client = dsk_random_project

    client.pipeline = "test pipline"

    # Upload training data
    client.upload_dataframe("train_file.csv", get_train_data_1d(), force=True)

    # Upload testing data
    r = client.upload_dataframe("test_file.csv", get_test_data_1d(), force=True)

    client.pipeline.reset()

    sensor_columns = ["Axis_1"]

    client.pipeline.set_input_data(
        "train_file.csv",
        data_columns=sensor_columns,
        group_columns=["Label"],
        label_column="Label",
    )

    return client


class PipelineFailedException(Exception):
    pass


def check_result(dsk, results):
    if results is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


def test_sensor_average_pipeline(dsk_project_pipeline):
    dsk = dsk_project_pipeline

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 3, "delta": 3, "train_delta": 3}
    )

    dsk.pipeline.add_transform(
        "Sensor Average", params={"input_columns": dsk.pipeline.data_columns}
    )

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Median", "params": {"columns": ["Axis_1", "Average_ST_0000"]}},
        ]
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_defaults": {"minimum": 0, "maximum": 255},
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 5,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 80},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()

    results.summarize()

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")

    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )

    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )
    compare_features(r, fv_c)
    compare_classifications(r, r_c)


def test_sensor_moving_average_with_downsample_streaming_pipeline(dsk_project_pipeline):
    dsk = dsk_project_pipeline

    dsk.pipeline.add_transform(
        "Moving Average Sensor Transform",
        params={"input_columns": ["Axis_1"], "filter_order": 2},
    )

    dsk.pipeline.add_transform(
        "Streaming Downsample",
        params={"input_columns": dsk.pipeline.data_columns, "filter_length": 2},
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 5, "delta": 5, "train_delta": 5}
    )

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Median", "params": {"columns": dsk.pipeline.data_columns}},
        ]
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_defaults": {"minimum": 0, "maximum": 255},
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 100},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()
    results.summarize()

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")

    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )

    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )

    assert r.shape[0] == 1
    assert fv_c.shape[0] == 3

    # these are not equal due to slightly different starting points for each of the features as the device has to fill the buffer before doing any computations
    # compare_features(r, fv_c)
    # compare_classifications(r, r_c)


def test_feature_cascade_pipeline(dsk_project_pipeline):
    dsk = dsk_project_pipeline

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 5, "delta": 5, "train_delta": 5}
    )

    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Linear Regression Stats",
                "params": {"columns": dsk.pipeline.data_columns},
            },
            {"name": "Median", "params": {"columns": dsk.pipeline.data_columns}},
        ]
    )

    dsk.pipeline.add_feature_selector(
        [
            {
                "name": "Custom Feature Selection By Index",
                "params": {"custom_feature_selection": {1: [0, 1], 2: [0]}},
            }
        ]
    )

    dsk.pipeline.add_transform(
        "Min Max Scale", params={"min_bound": 0, "max_bound": 255}
    )

    dsk.pipeline.add_transform(
        "Feature Cascade", params={"num_cascades": 2, "slide": False}
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 100},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()

    print(results)

    results.summarize()

    model = results.configurations[0].models[0]

    print("Emulator Test")

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")
    print(r)

    print("Extract Featurers Test")
    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )
    print(fv_c)

    print("Run Entire Pipeline Test")
    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )
    print(r_c)

    assert r.shape[0] == 3

    # TODO: These are not currently matching, but they are not incorrect (comes down)

    # compare_features(r, fv_c)
    # compare_classifications(r, r_c)


def test_feature_cascade_pipeline_slide_true(dsk_project_pipeline, sml_runner):
    dsk = dsk_project_pipeline

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 5, "delta": 5, "train_delta": 5}
    )

    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "Linear Regression Stats",
                "params": {"columns": dsk.pipeline.data_columns},
            },
            {"name": "Median", "params": {"columns": dsk.pipeline.data_columns}},
        ]
    )

    dsk.pipeline.add_feature_selector(
        [
            {
                "name": "Custom Feature Selection By Index",
                "params": {"custom_feature_selection": {1: [0, 1], 2: [0]}},
            }
        ]
    )

    dsk.pipeline.add_transform(
        "Min Max Scale", params={"min_bound": 0, "max_bound": 255}
    )

    dsk.pipeline.add_transform(
        "Feature Cascade",
        params={
            "num_cascades": 2,
            "slide": True,
            "training_slide": True,
            "training_delta": 1,
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 100},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()

    print(results)

    results.summarize()

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")

    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )

    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )

    assert r.shape[0] == 5

    # TODO: These are not currently matching, but they are not incorrect
    # compare_features(r, fv_c)
    # compare_classifications(r, r_c)


def test_sensor_moving_average_with_downsample_by_decimation_streaming_pipeline(
    dsk_project_pipeline, sml_runner
):
    dsk = dsk_project_pipeline

    dsk.pipeline.add_transform(
        "Moving Average Sensor Transform",
        params={"input_columns": ["Axis_1"], "filter_order": 2},
    )

    dsk.pipeline.add_transform(
        "Streaming Downsample by Decimation",
        params={"input_columns": dsk.pipeline.data_columns, "filter_length": 2},
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 5, "delta": 5, "train_delta": 5}
    )

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Median", "params": {"columns": dsk.pipeline.data_columns}},
        ]
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_defaults": {"minimum": 0, "maximum": 255},
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 100},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()

    print(results)

    results.summarize()

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")

    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )

    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )

    assert r.shape[0] == 2
    assert fv_c.shape[0] == 3

    # compare_features(r, fv_c)
    # compare_classifications(r, r_c)

    ## testing where the segments start/end
    for i in range(r.shape[0]):
        assert r.SegmentStart.values[i] == i * 10
        assert r.SegmentLength.values[i] == 10
        assert r.SegmentEnd.values[i] == i * 10 + 9


def test_downsample_by_decimation_streaming_pipeline(dsk_project_pipeline, sml_runner):
    dsk = dsk_project_pipeline

    dsk.pipeline.add_transform(
        "Streaming Downsample by Decimation",
        params={"input_columns": dsk.pipeline.data_columns, "filter_length": 2},
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 5, "delta": 5, "train_delta": 5}
    )

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Median", "params": {"columns": dsk.pipeline.data_columns}},
        ]
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_defaults": {"minimum": 0, "maximum": 255},
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 100},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()

    print(results)

    results.summarize()

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")

    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )

    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )

    assert r.shape[0] == 3
    assert fv_c.shape[0] == 3

    # compare_features(r, fv_c)
    # compare_classifications(r, r_c)

    ## testing where the segments start/end
    for i in range(r.shape[0]):
        assert r.SegmentStart.values[i] == i * 10
        assert r.SegmentLength.values[i] == 10
        assert r.SegmentEnd.values[i] == i * 10 + 9

    ##########################
    ### Testing sml_runner
    ##########################

    test_data = get_test_data()
    # dropping the label column
    test_data = test_data[test_data.columns[:-1]]

    rec_data = utils_sml_runner(
        sml_runner,
        dsk,
        test_data,
        get_feature_vector=True,
        get_sensor_data=True,
    )

    # number of recognized segments
    assert rec_data.shape[0] == 3

    fv = [130, 131]
    for i in range(rec_data.shape[0]):
        # testing where the segments start/end
        assert rec_data.capture_sample_sequence_start.values[i] == i * 10
        assert rec_data.capture_sample_sequence_end.values[i] == i * 10 + 9

        # ## testing feature vector, and sensor data
        assert rec_data["sensor_data_0"].iloc[i] == list(
            range(110 + i * 50, 155 + i * 50, 10)
        )
        assert rec_data["sensor_data_1"].iloc[i] == list(
            range(111 + i * 50, 156 + i * 50, 10)
        )
        assert rec_data["feature_vector"].iloc[i] == [x + 50 * i for x in fv]


######################################
def test_downsample_feature_cascade_pipeline(dsk_project_pipeline, sml_runner):
    dsk = dsk_project_pipeline

    dsk.pipeline.add_transform(
        "Moving Average Sensor Transform",
        params={"input_columns": ["Axis_1"], "filter_order": 2},
    )

    dsk.pipeline.add_transform(
        "Streaming Downsample by Decimation",
        params={"input_columns": dsk.pipeline.data_columns, "filter_length": 2},
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 3, "delta": 2, "train_delta": 2}
    )

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Median", "params": {"columns": dsk.pipeline.data_columns}},
        ]
    )

    dsk.pipeline.add_transform(
        "Feature Cascade",
        params={
            "num_cascades": 3,
            "slide": True,
            "training_slide": True,
            "training_delta": 1,
        },
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_defaults": {"minimum": 0, "maximum": 255},
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 100},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()

    print(results)

    results.summarize()

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")

    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )

    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )

    assert r.shape[0] == 4
    assert fv_c.shape[0] == 5

    # compare_features(r, fv_c)
    # compare_classifications(r, r_c)

    ## testing where the segments start/end
    for i in range(r.shape[0]):
        assert r.SegmentStart.values[i] == i * 4
        assert r.SegmentLength.values[i] == 14
        assert r.SegmentEnd.values[i] == i * 4 + 13

    ##########################
    ### Testing sml_runner
    # TODO
    # having both decimation and feature cascade
    # causes issues with segment star/end when running sml_runner
    ##########################

    # test_data = get_test_data()
    # test_data = test_data[test_data.columns[:-1]]

    # rec_data = utils_sml_runner(
    #     sml_runner,
    #     dsk,
    #     test_data,
    #     model_api="run_model_cascade_features",
    #     get_feature_vector=True,
    #     get_sensor_data=True,
    # )


######################################
def test_feature_cascade_pipeline_delta_3(dsk_project_pipeline, sml_runner):
    dsk = dsk_project_pipeline

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 5, "delta": 3, "train_delta": 3}
    )

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Median", "params": {"columns": dsk.pipeline.data_columns}},
        ]
    )

    dsk.pipeline.add_transform(
        "Feature Cascade",
        params={
            "num_cascades": 3,
            "slide": True,
            "training_slide": True,
            "training_delta": 1,
        },
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_defaults": {"minimum": 0, "maximum": 255},
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 100},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()

    print(results)

    results.summarize()

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")

    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )

    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )

    assert r.shape[0] == 7
    assert fv_c.shape[0] == 7

    compare_features(r, fv_c)
    compare_classifications(r, r_c)

    ## testing where the segments start/end
    for i in range(r.shape[0]):
        assert r.SegmentStart.values[i] == i * 3
        assert r.SegmentLength.values[i] == 11
        assert r.SegmentEnd.values[i] == i * 3 + 10

    ##########################
    ### Testing sml_runner
    ##########################

    test_data = get_test_data()
    # dropping the label column
    test_data = test_data[test_data.columns[:-1]]

    rec_data = utils_sml_runner(
        sml_runner,
        dsk,
        test_data,
        model_api="run_model_cascade_features",
        get_feature_vector=True,
        get_sensor_data=True,
    )

    # number of recognized segments
    assert rec_data.shape[0] == 7

    fv = [115, 116, 130, 131, 145, 146]
    for i in range(rec_data.shape[0]):
        # ## testing where the segments start/end
        assert rec_data.capture_sample_sequence_start.values[i] == i * 3
        assert rec_data.capture_sample_sequence_end.values[i] == i * 3 + 10

        # ## testing feature vector, and sensor data
        assert rec_data["sensor_data_0"].iloc[i] == list(
            range(135 + i * 15, 160 + i * 15, 5)
        )
        assert rec_data["sensor_data_1"].iloc[i] == list(
            range(136 + i * 15, 161 + i * 15, 5)
        )
        assert rec_data["feature_vector"].iloc[i] == [x + 15 * i for x in fv]


######################################
def test_feature_cascade_1d_pipeline(dsk_project_pipeline_1d, sml_runner):
    dsk = dsk_project_pipeline_1d

    dsk.pipeline.add_transform(
        "Windowing", params={"window_size": 5, "delta": 5, "train_delta": 5}
    )

    dsk.pipeline.add_feature_generator(
        [
            {"name": "Median", "params": {"columns": dsk.pipeline.data_columns}},
        ]
    )

    dsk.pipeline.add_transform(
        "Feature Cascade",
        params={
            "num_cascades": 2,
            "slide": True,
            "training_slide": True,
            "training_delta": 1,
        },
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={
            "min_bound": 0,
            "max_bound": 255,
            "feature_min_max_defaults": {"minimum": 0, "maximum": 255},
        },
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "number_of_neurons": 1,
        },
    )

    dsk.pipeline.set_classifier(
        "PME",
        params={"distance_mode": "L1", "classification_mode": "RBF", "max_aif": 100},
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    results, stats = dsk.pipeline.execute()

    print(results)

    results.summarize()

    model = results.configurations[0].models[0]

    r, s = model.knowledgepack.recognize_signal(datafile="test_file.csv")

    fv_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv", platform="cloud", stop_step=10
    )

    r_c, s_c = model.knowledgepack.recognize_signal(
        datafile="test_file.csv",
        platform="cloud",
    )

    assert r.shape[0] == 5
    assert fv_c.shape[0] == 5

    compare_features(r, fv_c)
    compare_classifications(r, r_c)

    ## testing where the segments start/end
    for i in range(r.shape[0]):
        assert r.SegmentStart.values[i] == i * 5
        assert r.SegmentLength.values[i] == 10
        assert r.SegmentEnd.values[i] == i * 5 + 9

    ##########################
    ### Testing sml_runner
    ##########################

    test_data = get_test_data_1d()
    # dropping the label column
    test_data = test_data[test_data.columns[:-1]]

    rec_data = utils_sml_runner(
        sml_runner,
        dsk,
        test_data,
        model_api="run_model_cascade_features",
        get_feature_vector=True,
        get_sensor_data=True,
    )

    # number of recognized segments
    assert rec_data.shape[0] == 5

    fv = [115, 140]
    for i in range(rec_data.shape[0]):
        # ## testing where the segments start/end
        assert rec_data.capture_sample_sequence_start.values[i] == i * 5
        assert rec_data.capture_sample_sequence_end.values[i] == i * 5 + 9

        # ## testing feature vector, and sensor data
        assert rec_data["sensor_data_0"].iloc[i] == list(
            range(130 + i * 25, 155 + i * 25, 5)
        )
        assert rec_data["feature_vector"].iloc[i] == [x + 25 * i for x in fv]

    kp = model.knowledgepack

    new_generators = [
        {
            "family": None,
            "inputs": {"columns": ["Axis_1"]},
            "num_outputs": 1,
            "function_name": "100th Percentile",
            "subtype": "Stats",
        },
        {
            "family": None,
            "inputs": {"columns": ["Axis_2"]},
            "num_outputs": 1,
            "function_name": "100th Percentile",
            "subtype": "Stats",
        },
    ]

    kp.add_feature_only_generators(new_generators)

    expected_feature_summary = [
        {
            "Feature": "gen_c0000_gen_0001_Axis_1Median",
            "Sensors": ["Axis_1"],
            "Category": "Statistical",
            "Generator": "Median",
            "LibraryPack": None,
            "CascadeIndex": 0,
            "ContextIndex": 0,
            "GeneratorIndex": 0,
            "GeneratorTrueIndex": 1,
            "GeneratorFamilyIndex": 0,
            "GeneratorFamilyFeatures": 1,
        },
        {
            "Feature": "agen_Axis_1100th_Percentile_1",
            "Sensors": ["Axis_1"],
            "Category": "Stats",
            "Generator": "100th Percentile",
            "LibraryPack": None,
            "ContextIndex": 1,
            "EliminatedBy": "GeneratorOnly",
            "GeneratorIndex": 1,
            "GeneratorTrueIndex": 2,
            "GeneratorFamilyIndex": 1,
            "GeneratorFamilyFeatures": 1,
            "CascadeIndex": 0,
        },
        {
            "Feature": "agen_Axis_2100th_Percentile_2",
            "Sensors": ["Axis_2"],
            "Category": "Stats",
            "Generator": "100th Percentile",
            "LibraryPack": None,
            "ContextIndex": 2,
            "EliminatedBy": "GeneratorOnly",
            "GeneratorIndex": 2,
            "GeneratorTrueIndex": 3,
            "GeneratorFamilyIndex": 1,
            "GeneratorFamilyFeatures": 1,
            "CascadeIndex": 0,
        },
        {
            "Feature": "gen_c0001_gen_0001_Axis_1Median",
            "Sensors": ["Axis_1"],
            "Category": "Statistical",
            "Generator": "Median",
            "LibraryPack": None,
            "CascadeIndex": 1,
            "ContextIndex": 0,
            "GeneratorIndex": 0,
            "GeneratorTrueIndex": 1,
            "GeneratorFamilyIndex": 0,
            "GeneratorFamilyFeatures": 1,
        },
        {
            "Feature": "agen_Name_Axis_1100th_Percentile_1",
            "Sensors": ["Axis_1"],
            "Category": "Stats",
            "Generator": "100th Percentile",
            "LibraryPack": None,
            "ContextIndex": 1,
            "EliminatedBy": "GeneratorOnly",
            "GeneratorIndex": 1,
            "GeneratorTrueIndex": 2,
            "GeneratorFamilyIndex": 1,
            "GeneratorFamilyFeatures": 1,
            "CascadeIndex": 1,
        },
        {
            "Feature": "agen_Name_Axis_2100th_Percentile_2",
            "Sensors": ["Axis_2"],
            "Category": "Stats",
            "Generator": "100th Percentile",
            "LibraryPack": None,
            "ContextIndex": 2,
            "EliminatedBy": "GeneratorOnly",
            "GeneratorIndex": 2,
            "GeneratorTrueIndex": 3,
            "GeneratorFamilyIndex": 1,
            "GeneratorFamilyFeatures": 1,
            "CascadeIndex": 1,
        },
    ]
    expected_feature_generator_set = {
        "set": [
            {
                "family": None,
                "inputs": {"columns": ["Axis_1"]},
                "outputs": [0],
                "function_name": "Median",
            },
            {
                "family": None,
                "inputs": {"columns": ["Axis_1"]},
                "num_outputs": 1,
                "function_name": "100th Percentile",
                "subtype": "Stats",
                "outputs": [0],
            },
            {
                "family": None,
                "inputs": {"columns": ["Axis_2"]},
                "num_outputs": 1,
                "function_name": "100th Percentile",
                "subtype": "Stats",
                "outputs": [0],
            },
        ],
        "name": "generator_set",
        "type": "generatorset",
        "inputs": {
            "input_data": "temp.Windowing0",
            "group_columns": ["Label", "SegmentID"],
        },
        "outputs": ["temp.generator_set0", "temp.features.generator_set0"],
    }

    assert kp.feature_summary == expected_feature_summary
    assert (
        kp.knowledgepack_summary["recognition_pipeline"][1]
        == expected_feature_generator_set
    )

    kp._name = "New Generators"
    kp._knowledgepack_summary["sensor_columns"] = ["Axis_1", "Axis_2"]
    kp._knowledgepack_summary["data_columns_ordered"] = ["AXIS_1", "AXIS_2"]

    new_kp = kp.create()

    rec_data = utils_sml_runner(
        sml_runner,
        dsk,
        test_data,
        model_api="run_model_cascade_features",
        get_feature_vector=True,
        get_sensor_data=True,
        get_unscaled_feature_vector=True,
        kp=new_kp,
    )

    assert len(rec_data["feature_vector"][0]) == 2
    assert len(rec_data["unscaled_feature_vector"][0]) == 6
