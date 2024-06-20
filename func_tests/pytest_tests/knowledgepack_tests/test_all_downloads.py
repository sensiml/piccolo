import datetime
import json
import os

import pandas as pd
import pytest
from utils import all_parameter_configuration, tensorflow_parameter_configuration


class PipelineFailedException(Exception):
    pass


@pytest.fixture(scope="session")
def capture_configs():
    capture_configs = {
        "QuickLogic QuickFeather": {
            "name": "QuickLogic QuickFeather",
            "version": 3,
            "plugin_uuid": "9d870c8f-bbbc-4186-a9c0-6701c08715ed",
            "protocol_uuid": "6f8bee3d-8f21-49ea-9401-dbe251e2848e",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "MC3635",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 1229804865,
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "units": None,
                                    "value": 20,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": True,
                        }
                    ],
                    "sample_rate": 105,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
        "STMicroelectronics SensorTile": {
            "name": "STMicroelectronics SensorTile",
            "version": 3,
            "plugin_uuid": "fb5f18c1-1ee6-4e2a-97ba-0c1cecb50f67",
            "protocol_uuid": "4523cec5-030a-4d2b-9401-03a15078d830",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 0,
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "units": None,
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": False,
                        }
                    ],
                    "sample_rate": 104,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": False,
        },
        "STMicroelectronics SensorTile.Box": {
            "name": "STMicroelectronics SensorTile.Box",
            "version": 3,
            "plugin_uuid": "36dbf5f1-d9d4-4462-8fa8-04a8c9211595",
            "protocol_uuid": "6f8bee3d-8f21-49ea-9401-dbe251e2848e",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 1229804865,
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "units": None,
                                    "value": 40,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": True,
                        }
                    ],
                    "sample_rate": 104,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
        "Silicon Labs Thunderboard Sense 2": {
            "name": "Silicon Labs Thunderboard Sense 2",
            "version": 3,
            "plugin_uuid": "aa2f7757-3c8e-45c8-b0f4-bad9fbcc1b86",
            "protocol_uuid": "dc607a63-84a6-411b-aedb-77f294fd76ef",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 0,
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "units": None,
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": False,
                        }
                    ],
                    "sample_rate": 102,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": False,
        },
        "Nordic Thingy": {
            "name": "Nordic Thingy",
            "version": 3,
            "plugin_uuid": "b242f464-d42d-4455-85f4-bdb84ac55783",
            "protocol_uuid": "323ad8af-294c-491c-89e9-465274b249fd",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 0,
                            "parameters": [],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": False,
                        }
                    ],
                    "sample_rate": 100,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": False,
        },
        "SAMD21 ML Evaluation Kit": {
            "version": 3,
            "name": "SAMD21 ML Evaluation Kit",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "plugin_uuid": "4a915608-c5ca-4813-890c-7d20f6e7c283",
            "capture_sources": [
                {
                    "name": "Motion (BMI160)",
                    "part": "BMI160",
                    "sample_rate": 100,
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804865,
                            "can_live_stream": True,
                        },
                        {
                            "type": "Gyroscope",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 125,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804871,
                            "can_live_stream": True,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
        "AVR128DA48 Curiosity Nano Evaluation Kit": {
            "version": 3,
            "name": "AVR128DA48 Curiosity Nano Evaluation Kit",
            "protocol_uuid": "c7f361c2-858f-4d51-b8fa-e31d09df10f8",
            "plugin_uuid": "67a70c76-1247-4db7-b143-1ed3e374de8c",
            "capture_sources": [
                {
                    "name": "Motion (BMI160)",
                    "part": "BMI160",
                    "sample_rate": 100,
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804865,
                            "can_live_stream": True,
                        },
                        {
                            "type": "Gyroscope",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 125,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804871,
                            "can_live_stream": True,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
        "PIC-IoT WG Development Board": {
            "version": 3,
            "name": "PIC-IoT WG Development Board",
            "protocol_uuid": "c7f361c2-858f-4d51-b8fa-e31d09df10f8",
            "plugin_uuid": "67a10c76-1247-4db7-b142-1ed3e374de8c",
            "capture_sources": [
                {
                    "name": "Motion (BMI160)",
                    "part": "BMI160",
                    "sample_rate": 100,
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804865,
                            "can_live_stream": True,
                        },
                        {
                            "type": "Gyroscope",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 125,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804871,
                            "can_live_stream": True,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
        "onsemi RSL10 Sense": {
            "version": 3,
            "name": "onsemi RSL10 Sense",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "plugin_uuid": "4a915608-c5ca-4813-890c-7d20f6e7c283",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "BHI160",
                    "sample_rate": 100,
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804865,
                            "can_live_stream": True,
                        },
                        {
                            "type": "Gyroscope",
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "value": 2000,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804871,
                            "can_live_stream": True,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
        "Infineon CY8CKIT-062S2-43012": {
            "version": 3,
            "name": "Infineon CY8CKIT-062S2-43012",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "plugin_uuid": "4a915608-c5ca-4813-890c-7d20f6e7c283",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sample_rate": 100,
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804865,
                            "can_live_stream": True,
                        },
                        {
                            "type": "Gyroscope",
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804871,
                            "can_live_stream": True,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
        "Arduino Nicla Sense ME": {
            "version": 3,
            "name": "Arduino Nicla Sense ME",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "plugin_uuid": "4a915608-c5ca-4813-890c-7d20f6e7c283",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sample_rate": 100,
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804865,
                            "can_live_stream": True,
                        },
                        {
                            "type": "Gyroscope",
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "sensor_id": 1229804871,
                            "can_live_stream": True,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
        "Silicon Labs xG24 Dev Kit": {
            "name": "Silicon Labs xG24 Dev Kit",
            "version": 3,
            "plugin_uuid": "aa2f7757-3c8e-45c8-b0f4-bad9fbcc1b86",
            "protocol_uuid": "dc607a63-84a6-411b-aedb-77f294fd76ef",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 0,
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "units": None,
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": False,
                        }
                    ],
                    "sample_rate": 102,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": False,
        },
    }

    return capture_configs


""""QuickLogic S3AI Merced": {
            "name": "QuickAI",
            "version": 3,
            "plugin_uuid": "b9463999-4a28-4eb0-a057-24ca5ec31c48",
            "protocol_uuid": "50460e2c-d673-464a-8a02-6b307e14a1a6",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 0,
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "units": None,
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 3,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": False,
                        }
                    ],
                    "sample_rate": 104,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": False,
        },
        "QuickLogic S3AI Chilkat": {
            "name": "Chilkat",
            "version": 3,
            "plugin_uuid": "885c73cc-f474-4176-9fa6-ed9739ec491d",
            "protocol_uuid": "91821a6e-32a0-4433-add8-eb623276b0d0",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "Default",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 0,
                            "parameters": [
                                {
                                    "name": "Sensor Range",
                                    "units": None,
                                    "value": 2,
                                    "num_bytes": 1,
                                }
                            ],
                            "column_count": 1,
                            "column_names": ["X", "Y", "Z"],
                            "can_live_stream": False,
                        }
                    ],
                    "sample_rate": 100,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": False,
        },
        """


@pytest.fixture(scope="session")
def capture_config_audio():
    capture_configs = {
        "Silicon Labs xG24 Dev Kit": {
            "version": 3,
            "name": "Silicon Labs xG24 Dev Kit",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "plugin_uuid": "4a915628-c5ca-4813-890c-7d20f6e7c283",
            "capture_sources": [
                {
                    "name": "Audio",
                    "sample_rate": 16000,
                    "sensors": [
                        {
                            "type": "Microchone",
                            "column_count": 1,
                            "column_names": ["0"],
                            "sensor_id": 1229804865,
                            "can_live_stream": True,
                        },
                    ],
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
        },
    }

    return capture_configs


@pytest.fixture(scope="session")
def dsk_model(ClientConnectionSession, DataDir, capture_configs):
    import random
    import time

    import pandas as pd

    start = time.time()
    print("Starting model building!")

    dsk = ClientConnectionSession
    project_name = f"IntegrationTestIMU{random.randint(0, 10000)}"
    prj = dsk.projects.get_project_by_name(project_name)

    # Delete the project if it exists
    if prj is not None:
        prj.delete()

    dsk.project = project_name
    dsk.pipeline = "TestPipeline"

    t0 = time.time()
    print("Creating Capture Configuration")

    for k, v in capture_configs.items():
        cc = dsk.project.capture_configurations.create_capture_configuration(
            name=k, configuration=v
        )
        capture_configs[k]["created_uuid"] = cc.uuid

    print("Finished Creating Capture Configuration in", time.time() - t0)

    df = pd.read_csv(
        "{}/kbbasics/activities_combinedSignalsWithLabel_tiny.csv".format(DataDir)
    )
    df = df.rename(columns={"Class": "Activity"})
    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    df.head()

    dsk.pipeline.set_columns(data_columns=sensor_columns)

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
        ["Mean", "Standard Deviation"], function_defaults={"columns": sensor_columns}
    )

    dsk.pipeline.add_transform("Min Max Scale")

    dsk.pipeline.set_validation_method("Recall")
    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "turbo": True,
            "number_of_neurons": 100,
            "aggressive_neuron_creation": True,
        },
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    r, s = dsk.pipeline.execute()

    print(r)
    print(s)

    print("MODEL BUILDING TOOK", time.time() - start)

    try:
        assert check_result(dsk, r)
        model = r.configurations[0].models[0].knowledgepack
    except:
        dsk.project.delete()
        raise Exception(r)

    yield dsk, model, capture_configs

    try:
        dsk.project.delete()
    except:
        pass


@pytest.fixture(scope="session")
def dsk_model_audio(ClientConnectionSession, DataDir, capture_config_audio):
    import random

    import pandas as pd

    dsk = ClientConnectionSession
    project_name = "IntegrationTest_Audio{}".format(random.randint(0, 10000))
    prj = dsk.projects.get_project_by_name(project_name)

    # Delete the project if it exists
    if prj is not None:
        prj.delete()

    dsk.project = project_name
    dsk.pipeline = "TestPipeline"

    for k, v in capture_config_audio.items():
        cc = dsk.project.capture_configurations.create_capture_configuration(
            name=k, configuration=v
        )
        capture_config_audio[k]["created_uuid"] = cc.uuid

    df = pd.read_csv(
        "{}/kbbasics/activities_combinedSignalsWithLabel_tiny.csv".format(DataDir)
    )
    df = df.rename(columns={"Class": "Activity", "AccelerometerX": "Microphone0"}).drop(
        ["AccelerometerY", "AccelerometerZ"], axis=1
    )
    df.head()
    sensor_columns = ["Microphone0"]

    dsk.pipeline.set_columns(data_columns=sensor_columns)

    dsk.upload_dataframe("audio_dataframe", df, force=True)

    dsk.pipeline.reset()
    dsk.pipeline.set_input_data(
        "audio_dataframe.csv",
        data_columns=sensor_columns,
        group_columns=["Subject", "Activity"],
        label_column="Activity",
    )  # , force=True)

    dsk.pipeline.add_transform("Windowing", params={"window_size": 200, "delta": 200})

    dsk.pipeline.add_feature_generator(
        ["Mean", "Standard Deviation"], function_defaults={"columns": sensor_columns}
    )

    dsk.pipeline.add_transform("Min Max Scale")

    dsk.pipeline.set_validation_method("Recall")
    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )

    dsk.pipeline.set_training_algorithm(
        "RBF with Neuron Allocation Optimization",
        params={
            "number_of_iterations": 1,
            "turbo": True,
            "number_of_neurons": 100,
            "aggressive_neuron_creation": True,
        },
    )

    dsk.pipeline.set_tvo({"validation_seed": 1})

    r, s = dsk.pipeline.execute()

    print(r)
    print(s)

    try:
        assert check_result(dsk, r)
        model = r.configurations[0].models[0].knowledgepack
    except:
        dsk.project.delete()
        raise Exception(r)

    yield dsk, model, capture_config_audio

    try:
        dsk.project.delete()
    except:
        pass


@pytest.fixture(scope="session")
def dsk_tf_model(ClientConnectionSession, DataDir, capture_configs):
    import random

    import pandas as pd

    dsk = ClientConnectionSession
    project_name = f"Test_Project_{random.randint(0, 10000)}"
    prj = dsk.projects.get_project_by_name(project_name)

    # Delete the project if it exists
    if prj is not None:
        prj.delete()

    dsk.project = project_name

    dsk.pipeline = "TestPipeline"

    for k, v in capture_configs.items():
        cc = dsk.project.capture_configurations.create_capture_configuration(
            name=k, configuration=v
        )
        capture_configs[k]["created_uuid"] = cc.uuid

    df = pd.read_csv(
        "{}/kbbasics/activities_combinedSignalsWithLabel_tiny.csv".format(DataDir)
    )
    df = df.rename(columns={"Class": "Activity"})
    df["Activity"] = df["Activity"].map({0: "A", 1: "B", 2: "C", 3: "E", 4: "F"})
    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    print(df.head())

    ss = dsk.upload_dataframe("activities_data.csv", df, force=True)
    dsk.pipeline.reset()

    dsk.pipeline.set_input_data(
        "activities_data.csv",
        data_columns=sensor_columns,
        group_columns=["Subject", "Activity"],
        label_column="Activity",
    )  # , force=True)

    dsk.pipeline.add_transform("Windowing", params={"window_size": 200, "delta": 200})

    dsk.pipeline.add_feature_generator(
        [{"subtype_call": "Time", "params": {"sample_rate": 100}}],
        function_defaults={"columns": sensor_columns},
    )

    dsk.pipeline.add_transform("Min Max Scale")

    fv, s = dsk.pipeline.execute()

    print(fv)

    (
        x_train,
        x_test,
        x_validate,
        y_train,
        y_test,
        y_validate,
        class_map,
    ) = dsk.pipeline.features_to_tensor(fv, test=0.0, validate=0.1)

    import tensorflow as tf
    from tensorflow.keras import layers

    tf_model = tf.keras.Sequential()

    tf_model.add(
        layers.Dense(
            12,
            activation="relu",
            kernel_regularizer="l1",
            input_shape=(x_train.shape[1],),
        )
    )
    tf_model.add(layers.Dropout(0.1))
    tf_model.add(layers.Dense(8, activation="relu", input_shape=(x_train.shape[1],)))
    tf_model.add(layers.Dropout(0.1))
    tf_model.add(layers.Dense(y_train.shape[1], activation="softmax"))

    # Compile the model using a standard optimizer and loss function for regression
    tf_model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    tf_model.summary()
    train_history = {"loss": [], "val_loss": [], "accuracy": [], "val_accuracy": []}

    import sensiml.tensorflow.utils as sml_tf

    num_iterations = 1
    epochs = 100
    batch_size = 32

    data = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    shuffle_ds = data.shuffle(
        buffer_size=x_train.shape[0], reshuffle_each_iteration=True
    ).batch(batch_size)

    for i in range(num_iterations):
        history = tf_model.fit(
            shuffle_ds,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(x_validate, y_validate),
            verbose=0,
        )

    for key in train_history:
        train_history[key].extend(history.history[key])

    import numpy as np

    def representative_dataset_generator():
        for value in x_validate:
            # Each scalar value must be inside of a 2D array that is wrapped in a list
            yield [np.array(value, dtype=np.float32, ndmin=2)]

    # Unquantized Model
    converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)
    tflite_model_full = converter.convert()
    print("Full Model Size", len(tflite_model_full))

    # Quantized Model
    converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.representative_dataset = representative_dataset_generator
    tflite_model_quant = converter.convert()

    print("Quantized Model Size", len(tflite_model_quant))

    class_map_tmp = {
        k: v + 1 for k, v in class_map.items()
    }  # increment by 1 as 0 corresponds to unknown

    dsk.pipeline.set_training_algorithm(
        "Load Model TensorFlow Lite for Microcontrollers",
        params={
            "model_parameters": {"tflite": sml_tf.convert_tf_lite(tflite_model_full)},
            "class_map": class_map_tmp,
            "estimator_type": "classification",
            "threshold": 0.0,
            "train_history": train_history,
            "model_json": tf_model.to_json(),
        },
    )

    dsk.pipeline.set_validation_method("Recall", params={})

    dsk.pipeline.set_classifier("TensorFlow Lite for Microcontrollers", params={})

    dsk.pipeline.set_tvo()

    results, stats = dsk.pipeline.execute()

    model = results.configurations[0].models[0].knowledgepack

    yield dsk, model, capture_configs

    try:
        dsk.project.delete()
    except:
        pass


def check_result(dsk, r):
    if r is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")

        return False

    return True


def check_success_failure(success, failed):
    if failed:
        failed_string = ""
        success_string = ""
        for f in failed:
            if f[3] == "library":
                print("LIBRARY FAILED PLATFORMS")
                print(f)
                failed_string += "library, "

        for s in success:
            if s[3] == "library":
                print("LIBRARY SUCCESS PLATFORMS")
                print(s)

                success_string += "library, "

        for f in failed:
            if f[3] == "binary":
                print("BINARY FAILED PLATFORMS")
                print(f)
                failed_string += "binary,  "

        for s in success:
            if s[3] == "binary":
                print("BINARY SUCCESS PLATFORMS")
                print(s)
                success_string += "binary,  "

        for f in failed:
            if f[3] == "binary_profile":
                print("BINARY PROFILE FAILED PLATFORMS")
                print(f)
                failed_string += "binary_profile,  "

        for s in success:
            if s[3] == "binary_profile":
                print("BINARY PROFILE SUCCESS PLATFORMS")
                print(s)
                success_string += "binary_profile,  "

        for f in failed:
            if f[3] == "library_profile":
                print("LIBRARY PROFILE FAILED PLATFORMS")
                print(f)
                failed_string += "library_profile,  "

        for s in success:
            if s[3] == "library_profile":
                print("LIBRARY PROFILE SUCCESS PLATFORMS")
                print(s)
                success_string += "library_profile,  "

        for f in failed:
            if f[3] == "source":
                print("SOURCE PROFILE FAILED PLATFORMS")
                print(f)
                failed_string += "source,  "

        for s in success:
            if s[3] == "source":
                print("SOURCE PROFILE SUCCESS PLATFORMS")
                print(s)
                success_string += "source,  "

        result_string = "failed: " + failed_string + "  success:" + success_string

        raise Exception(
            "Ran {num_run} failed {num_failed} - {result_string}".format(
                num_run=len(success) + len(failed),
                num_failed=len(failed),
                result_string=result_string,
            )
        )


def print_summary(config, download_type):
    print("\n##################################")
    print("Download {}, debug: {}".format(download_type, config["debug"]))
    print(
        "Platform:",
        config["platform.name"],
        "Processor Name:",
        config["processor.display_name"],
        "Compiler:",
        "{} {}".format(config["compiler.name"], config["compiler.compiler_version"]),
        "Application: ",
        config["application"],
        "Profiling:",
        config["processor.profiling_enabled"],
    )

    print("###################################\n")


def validate_results(res, config, path_or_err, download_type, success, failed):
    if res is False:
        print(config["platform.name"], res, path_or_err)
        if "Knowledge Pack will not fit" in path_or_err:
            # this is an ok error to have even though the download failed
            success.append(
                (config["platform.name"], path_or_err, config, download_type)
            )
        else:
            failed.append((config["platform.name"], path_or_err, config, download_type))

    else:
        success.append((config["platform.name"], path_or_err, config, download_type))

    return success, failed


@pytest.mark.parametrize("index,config", *all_parameter_configuration)
@pytest.mark.parametrize(
    "build_type",
    ["library", "binary", "source"],  # , "library_profile", "binary_profile"]
)
def test_all_downloads_v2_parallel(index, config, dsk_model, build_type):
    dsk, model, capture_configs = dsk_model

    failed = []
    success = []

    config["debug"] = True

    config["kb_description"] = {"TestModel": {"uuid": model.uuid, "source": "Custom"}}

    if config["platform.name"] in capture_configs.keys():
        config["kb_description"]["TestModel"]["source"] = capture_configs[
            config["platform.name"]
        ]["created_uuid"]

    if build_type == "binary" and config["platform.can_build_binary"]:
        print_summary(config, "binary")

        path_or_err, res = model.download_binary_v2(config=config)
        print("DOWNLOAD BINARY RESPONSE:", path_or_err)

        success, failed = validate_results(
            res, config, path_or_err, "binary", success, failed
        )

    elif (
        build_type == "binary_profile"
        and config["platform.can_build_binary"]
        and config["processor.profiling_enabled"]
    ):
        print_summary(config, "binary_profile")
        config["profile"] = True
        config["profile_iterations"] = 10
        path_or_err, res = model.download_binary_v2(config=config)
        print("response_profile", path_or_err)
        success, failed = validate_results(
            res, config, path_or_err, "binary_profile", success, failed
        )
        config["profile"] = False

    elif build_type == "library":
        print_summary(config, "library")
        path_or_err, res = model.download_library_v2(config=config)

        print("DOWNLOAD LIBRARY RESPONSE:", path_or_err)

        success, failed = validate_results(
            res, config, path_or_err, "library", success, failed
        )

    elif build_type == "library_profile" and config["processor.profiling_enabled"]:
        print_summary(config, "library_profile")
        config["profile"] = True
        config["profile_iterations"] = 10
        path_or_err, res = model.download_library_v2(config=config)
        success, failed = validate_results(
            res, config, path_or_err, "library_profile", success, failed
        )
    elif build_type == "source":
        print_summary(config, "source")

        path_or_err, res = model.download_source_v2(config=config)
        print("response_source", path_or_err)

        success, failed = validate_results(
            res, config, path_or_err, "source", success, failed
        )

    else:
        return

    if res is False:
        print(path_or_err)
        save_str = (
            build_type
            + "_"
            + config["platform.name"]
            + "_"
            + config["compiler.name"]
            + "_"
            + config["compiler.compiler_version"]
            + "_"
            + config["processor.display_name"]
            + "_platform_version_"
            + config["selected_platform_version"]
            + "_application_"
            + config["application"]
            + ".test_all_downloads_v2.log"
        )

        model.get_build_log(save_as=save_str.replace(" ", "_").replace("/", "_"))

    check_success_failure(success, failed)


@pytest.mark.parametrize("b_parameters", tensorflow_parameter_configuration)
def test_all_downloads_v2_tf_micro_parallel(b_parameters, dsk_tf_model):
    dsk, model, capture_configs = dsk_tf_model

    index = b_parameters[0]
    config = b_parameters[1]

    failed = []
    success = []

    config["kb_description"] = {"TestModel": {"uuid": model.uuid, "source": "Custom"}}

    if config["platform.name"] in capture_configs.keys():
        config["kb_description"]["TestModel"]["source"] = capture_configs[
            config["platform.name"]
        ]["created_uuid"]

    print_summary(config, "library")
    path_or_err, res = model.download_library_v2(config=config)

    if res is False:
        print(path_or_err)
        save_str = (
            "tf_micro_"
            + "_"
            + config["platform.name"]
            + "_"
            + config["compiler.name"]
            + "_"
            + config["compiler.compiler_version"]
            + "_"
            + config["processor.display_name"]
            + "_platform_version_"
            + config["selected_platform_version"]
            + "_application_"
            + config["application"]
            + ".log"
        )

        model.get_build_log(save_as=save_str.replace(" ", "_").replace("/", "_"))

    validate_results(res, config, path_or_err, "library", success, failed)

    check_success_failure(success, failed)
