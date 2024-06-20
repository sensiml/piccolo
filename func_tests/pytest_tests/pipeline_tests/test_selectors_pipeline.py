# get_ipython().magic(u'matplotlib inline')
import os
import os.path
import sys

import numpy as np
import pandas as pd
import pytest


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


@pytest.fixture
def dsk_project_pipeline(dsk_random_project):
    client = dsk_random_project

    client.pipeline = "test pipline"

    client.pipeline.reset(delete_cache=False)
    df = client.datasets.load_activity_raw()
    client.upload_dataframe("test_data", df, force=True)

    return client


class PipelineFailedException(Exception):
    pass


def check_result(dsk, results):
    if results is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


def build_pipeline(dsk, params, pipeline_name="test", input_data="test_data"):
    dsk.pipeline = pipeline_name
    dsk.pipeline.reset()
    dsk.pipeline.set_input_data(
        input_data,
        group_columns=["Subject", "Class", "Rep"],
        label_column="Class",
        data_columns=["accelx", "accely", "accelz", "gyrox", "gyroy", "gyroz"],
    )

    # number of total feature generators: 8
    dsk.pipeline.add_feature_generator(
        [
            {
                "name": "MFCC",
                "params": {
                    "columns": ["accelx"],
                    "sample_rate": 10,
                    "cepstra_count": 3,
                },
            },
            {
                "name": "Downsample",
                "params": {"columns": ["accelx", "accely", "accelz"], "new_length": 3},
            },
            {
                "name": "MFCC",
                "params": {
                    "columns": ["accely"],
                    "sample_rate": 10,
                    "cepstra_count": 4,
                },
            },
            {
                "name": "Power Spectrum",
                "params": {
                    "columns": ["accelx"],
                    "number_of_bins": 5,
                    "window_type": "hanning",
                },
            },
            {
                "name": "Absolute Area",
                "params": {
                    "sample_rate": 10,
                    "columns": ["accelx", "accelz"],
                },
            },
        ]
    )

    dsk.pipeline.add_feature_selector(
        [{"name": "Feature Selector By Family", "params": params}]
    )

    return dsk


def generator_total_count(results):
    return len(
        set([int(col.split("_")[1]) for col in results.columns if "gen_" in col])
    )


def selected_generators_counts(status):
    df = status["feature_table"]
    generator_selected_counts = (
        df[["Generator", "GeneratorTrueIndex"]][df.Selected == True]
        .drop_duplicates()
        .groupby(["Generator"])["Generator"]
        .count()
        .to_dict()
    )

    generator_all_counts = (
        df[["Generator", "GeneratorTrueIndex"]]
        .drop_duplicates()
        .groupby(["Generator"])["Generator"]
        .count()
        .to_dict()
    )

    for key in generator_all_counts:
        if not key in generator_selected_counts:
            generator_selected_counts[key] = 0

    return generator_selected_counts


def test_sensor_average_pipeline(dsk_project_pipeline):
    ####################################################################
    # maximum number of generators has not been specified
    dsk = build_pipeline(
        dsk_project_pipeline,
        params={
            "max_number_generators": 4,
            "generators": [
                {"generator_names": "Downsample", "number": 2},
                {"generator_names": ["MFCC"], "number": 1},
            ],
        },
    )
    results, status = dsk.pipeline.execute()

    assert generator_total_count(results) == 4

    generator_counts = selected_generators_counts(status)
    assert generator_counts["Downsample"] == 2
    assert generator_counts["MFCC"] == 1
    assert (generator_counts["Absolute Area"] + generator_counts["Power Spectrum"]) == 1

    #####################################################################
    # max number of generators less than the number of all generators and larger than the sum of selected generators from the specified list

    dsk = build_pipeline(
        dsk_project_pipeline,
        params={
            "max_number_generators": 5,
            "random_seed": 1,
            "generators": [
                {"generator_names": "Downsample", "number": 2},
                {"generator_names": ["MFCC", "Power Spectrum"], "number": 2},
            ],
        },
    )
    results, status = dsk.pipeline.execute()
    assert generator_total_count(results) == 5

    generator_counts = selected_generators_counts(status)
    assert generator_counts["Downsample"] == 2
    assert (generator_counts["MFCC"] + generator_counts["Power Spectrum"]) == 2

    #####################################################################
    # maximum number of generators is less than the generated generators
    dsk = build_pipeline(
        dsk_project_pipeline,
        params={
            "max_number_generators": 4,
            "random_seed": 4,
        },
    )
    results, status = dsk.pipeline.execute()
    assert generator_total_count(results) == 4

    #####################################################################
    # maximum number of generators is larger than the generated generators
    dsk = build_pipeline(
        dsk_project_pipeline,
        params={
            "max_number_generators": 10,
        },
    )
    results, status = dsk.pipeline.execute()
    assert generator_total_count(results) == 8

    #####################################################################
    # no input parameter has been specified
    # note: default for max_number_generators is 5

    dsk = build_pipeline(dsk_project_pipeline, params={})
    results, status = dsk.pipeline.execute()
    assert generator_total_count(results) == 5
