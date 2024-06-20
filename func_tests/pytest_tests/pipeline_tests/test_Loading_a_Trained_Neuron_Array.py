import os

import pandas as pd
import pytest

# Creating the connection with the server


def test_LoadTrainedNeuron(dsk_random_project, DataDir):
    dsk = dsk_random_project
    dsk.pipeline = "Activity_Pipeline"

    sensor_columns = dsk.project.columns()
    df = pd.read_csv(
        "{}/kbbasics/activities_combinedSignalsWithLabel_medium.csv".format(DataDir)
    )
    df["Subject"] = df["Subject"].apply(lambda x: int(x[1:]))
    df.head()
    assert (df.shape) == (210522, 5)

    neuron_array = [
        {
            u"AIF": 1,
            u"Category": 2,
            u"Context": 1,
            u"Identifier": 1,
            u"Vector": [0, 0, 0, 0, 0, 124, 0, 0],
        },
        {
            u"AIF": 1,
            u"Category": 2,
            u"Context": 1,
            u"Identifier": 2,
            u"Vector": [166, 31, 172, 138, 93, 31, 254, 35],
        },
        {
            u"AIF": 143,
            u"Category": 3,
            u"Context": 1,
            u"Identifier": 3,
            u"Vector": [246, 232, 243, 68, 241, 156, 72, 16],
        },
        {
            u"AIF": 1,
            u"Category": 3,
            u"Context": 1,
            u"Identifier": 4,
            u"Vector": [134, 171, 163, 42, 167, 114, 19, 254],
        },
        {
            u"AIF": 349,
            u"Category": 4,
            u"Context": 1,
            u"Identifier": 5,
            u"Vector": [118, 165, 147, 184, 156, 191, 2, 0],
        },
        {
            u"AIF": 449,
            u"Category": 1,
            u"Context": 1,
            u"Identifier": 6,
            u"Vector": [97, 78, 107, 43, 92, 106, 56, 4],
        },
        {
            u"AIF": 354,
            u"Category": 4,
            u"Context": 1,
            u"Identifier": 7,
            u"Vector": [131, 184, 165, 53, 174, 128, 2, 3],
        },
    ]

    dsk.upload_dataframe("activity_data", df, force=True)

    dsk.pipeline.reset()
    dsk.pipeline.set_columns(
        data_columns=["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        group_columns=["Activity", "Subject"],
        label_column="Activity",
    )

    dsk.pipeline.set_input_data(
        "activity_data.csv",
        data_columns=["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        group_columns=["Activity", "Subject"],
        label_column="Activity",
    )

    dsk.pipeline.add_transform("Windowing")

    dsk.pipeline.add_feature_generator(
        [
            "Mean",
            "Standard Deviation",
            "Skewness",
            "Kurtosis",
            "25th Percentile",
            "75th Percentile",
            "100th Percentile",
            "Zero Crossing Rate",
        ],
        function_defaults={"columns": [u"AccelerometerY"]},
    )

    dsk.pipeline.add_feature_selector(
        [{"name": "Recursive Feature Elimination", "params": {"method": "Log R"}}],
        params={"number_of_features": 8},
    )

    dsk.pipeline.add_transform("Min Max Scale")

    dsk.pipeline.set_training_algorithm(
        "Load Model PME", params={"neuron_array": neuron_array}
    )

    dsk.pipeline.set_validation_method("Recall")

    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )

    dsk.pipeline.set_tvo()

    results, stats = dsk.pipeline.execute()

    results.summarize()
    model = results.configurations[0].models[0]
    assert model.neurons == neuron_array

    feature_file = dsk.get_featurefile(model.knowledgepack._feature_file_uuid)
    response = feature_file.compute_analysis(analysis_type="UMAP")

    assert response.status_code == 200
    response = feature_file.compute_analysis(analysis_type="PCA")
    assert response.status_code == 200
    response = feature_file.compute_analysis(analysis_type="TSNE")
    assert response.status_code == 200

    feature_file_analyzed_list = feature_file.list_analysis()

    feature_file_analyzed = dsk.get_featurefile(feature_file_analyzed_list[0]["uuid"])

    analyzed_data = feature_file_analyzed.download_json()

    print("TODO: check this data is formatted correctl")
