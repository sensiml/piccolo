def activity_pipeline_sandbox(dsk, query_name):

    dsk.pipeline.reset()

    dsk.pipeline.set_input_query(query_name)

    dsk.pipeline.add_transform(
        "Scale Factor",
        params={"scale_factor": 4096.0, "input_column": "AccelerometerY"},
    )

    dsk.pipeline.add_transform(
        "Windowing", params={"group_column": ["Subject", "Activity"]}
    )

    dsk.pipeline.add_transform(
        "Segment Filter MSE",
        params={
            "input_column": "AccelerometerY",
            "group_column": ["Subject", "Activity", "window_id"],
        },
    )

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
        params={"group_columns": ["Subject", "Activity", "window_id"]},
        function_defaults={"columns": ["AccelerometerY"]},
    )

    dsk.pipeline.add_feature_selector(
        [{"name": "Recursive Feature Elimination", "params": {"method": "Log R"}}],
        params={
            "passthrough_columns": ["Subject", "Activity", "window_id"],
            "number_of_features": 8,
            "label_column": "Activity",
        },
    )

    dsk.pipeline.add_transform(
        "Min Max Scale",
        params={"passthrough_columns": ["Subject", "Activity", "window_id"]},
    )

    dsk.pipeline.set_validation_method(
        "Stratified K-Fold Cross-Validation", params={"number_of_folds": 5}
    )

    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )

    dsk.pipeline.set_training_algorithm(
        "Hierarchical Clustering with Neuron Optimization",
        params={"number_of_neurons": 7},
    )

    dsk.pipeline.set_tvo(
        {
            "label_column": "Activity",
            "ignore_columns": ["Subject", "window_id"],
            "reserve_test_set": False,
            "validation_seed": 0,
        }
    )
