import os
import sys

import pandas as pd
import pytest


class PipelineFailedException(Exception):
    pass


def check_result(dsk, results):
    if results is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")


@pytest.mark.parametrize(
    "validation_method",
    [
        "Split by Metadata Value",
        # "Leave-One-Subject-Out (1 column)",
        # "Leave-One-Subject-Out (2 columns)",
        "Stratified K-Fold Cross-Validation",
        "Recall",
        "Stratified Shuffle Split",
        "Stratified Metadata k-fold",
        "Metadata k-fold",
    ],
)
def test_ValidationMethods(validation_method, dsk_random_project, DataDir):
    dsk = dsk_random_project

    dsk.pipeline = "Test_Validate_Method_{}".format(validation_method)

    sensor_columns = dsk.project.columns()
    df = pd.read_csv(
        "{}/kbbasics/activities_combinedSignalsWithLabel_verysmall.csv".format(DataDir)
    )
    df["Phase"] = pd.Series([1, 2] * len(df))[0 : len(df)]

    df.head()

    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]

    filename = "activity_data_{}.csv".format(
        validation_method.replace(" ", "_").replace("-", "_")
    )
    dsk.upload_dataframe(filename, df, force=True)

    dsk.pipeline.reset()

    dsk.pipeline.set_input_data(
        filename,
        data_columns=sensor_columns,
        group_columns=["Class", "Subject", "Phase"],
        label_column="Class",
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
        function_defaults={"columns": sensor_columns},
    )

    dsk.pipeline.add_transform("Min Max Scale")

    results, stats = dsk.pipeline.execute()

    check_result(dsk, results)

    # results.head()

    SMO = "dsk.pipeline.set_validation_method('Split by Metadata Value', params={'number_of_folds':1, 'metadata_name':'Subject', 'training_values': ['U0{}'.format(str(x).zfill(2)) for x in range(5)], 'validation_values':['U0{}'.format(str(x).zfill(2)) for x in range(2, 4)]})"
    LOSO1 = "dsk.pipeline.set_validation_method('Leave-One-Subject-Out', params={'group_columns': ['Subject']})"
    LOSO2 = "dsk.pipeline.set_validation_method('Leave-One-Subject-Out', params={'group_columns': ['Subject', 'Phase']})"
    SKCV = "dsk.pipeline.set_validation_method('Stratified K-Fold Cross-Validation', params={'number_of_folds': 2})"
    RECALL = "dsk.pipeline.set_validation_method('Recall')"
    SSS = "dsk.pipeline.set_validation_method('Stratified Shuffle Split')"
    SMAL = "dsk.pipeline.set_validation_method('Stratified Metadata k-fold', params={'metadata_name': 'Subject', 'number_of_folds':2})"
    MAL = "dsk.pipeline.set_validation_method('Metadata k-fold', params={'metadata_name': 'Subject', 'number_of_folds':2})"

    HCNO = "dsk.pipeline.set_training_algorithm('Hierarchical Clustering with Neuron Optimization', params = {'number_of_neurons': 7})"
    RNAO = "dsk.pipeline.set_training_algorithm('RBF with Neuron Allocation Optimization', params = {'number_of_iterations': 3})"
    RNAL = "dsk.pipeline.set_training_algorithm('RBF with Neuron Allocation Limit')"
    LNA = "dsk.pipeline.set_training_algorithm('Load Model PME', params = {'neuron_array':[{u'AIF': 5, u'Category': 4, u'Context': 1, u'Identifier': 1, u'Vector': [175, 0, 253, 253, 62]},{u'AIF': 147, u'Category': 2, u'Context': 1, u'Identifier': 2, u'Vector': [24, 196, 0, 0, 128]},{u'AIF': 1, u'Category': 1, u'Context': 1, u'Identifier': 3, u'Vector': [114, 124, 63, 0, 63]},{u'AIF': 78, u'Category': 1, u'Context': 1, u'Identifier': 4, u'Vector': [124, 116, 254, 0, 2]},{u'AIF': 147, u'Category': 3, u'Context': 1, u'Identifier': 5, u'Vector': [211, 97, 254, 0, 65]},{u'AIF': 230, u'Category': 1, u'Context': 1, u'Identifier': 6, u'Vector': [60, 143, 0, 0, 3]},{u'AIF': 147, u'Category': 4, u'Context': 1, u'Identifier': 7, u'Vector': [176, 0, 254, 0, 0]}]})"

    algorithms = [HCNO, RNAO, RNAL, LNA]

    validationMethods = {
        "Split by Metadata Value": SMO,
        "Leave-One-Subject-Out (1 column)": LOSO1,
        "Leave-One-Subject-Out (2 columns)": LOSO2,
        "Stratified K-Fold Cross-Validation": SKCV,
        "Recall": RECALL,
        "Stratified Shuffle Split": SSS,
        "Stratified Metadata k-fold": SMAL,
        "Metadata k-fold": MAL,
    }

    algorithmText = [
        "Hierarchical Clustering with Neuron Optimization",
        "RBF with Neuron Allocation Optimization",
        "RBF with Neuron Allocation Limit",
        "Load Neuron Array",
    ]
    failed = 0
    validationLoop = 0
    algorithmLoop = 0
    print("Loop starts\n")

    validation = validationMethods[validation_method]

    algorithmLoop = 0
    for algo in algorithms:
        if validation == RECALL and algo == RNAL:
            print(
                "Ignored "
                + validation_method
                + " and  "
                + algorithmText[algorithmLoop]
                + "\n"
            )
            continue

        print(
            "Executing "
            + validation_method
            + " and  "
            + algorithmText[algorithmLoop]
            + "\n"
        )

        exec(validation)
        exec(algo)

        dsk.pipeline.set_classifier(
            "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
        )

        dsk.pipeline.set_tvo()
        results, stats = dsk.pipeline.execute()

        if stats is not None:
            # results.summarize()
            print("\nPipeline execution successful\n")
            # for model in results.configurations[0].models:
            # 	print '{} - Subject {}'.format(model._index, results.input_data.ix[model.validation_set, 'Subject'].unique()[0])
        else:
            failed = failed + 1
            print(
                "\nFailed to run pipeline for "
                + validation_method
                + " and "
                + algorithmText[algorithmLoop]
            )
            print(results)
            dsk.pipeline.stop_pipeline()
        algorithmLoop = algorithmLoop + 1

    print("Loop ends\n")
    assert failed == 0
