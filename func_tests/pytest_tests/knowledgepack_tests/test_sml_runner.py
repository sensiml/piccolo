import datetime
import json
import os
import random

import pandas as pd
import pytest
from utils import all_parameter_configuration, tensorflow_parameter_configuration


@pytest.fixture()
def imported_models(ClientConnectionSession):

    client = ClientConnectionSession
    project_name = "Test_Project_{}".format(random.randint(0, 10000))
    client.project = project_name

    from sensiml.datamanager.knowledgepack import KnowledgePack

    imported_models = []

    for model_type in ["tf", "pme", "dte", "bonsai"]:

        kp = KnowledgePack(client._connection, client.project.uuid)
        kp.initialize_from_dict(
            json.load(
                open(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                        "..",
                        "server",
                        "datamanager",
                        "tests",
                        "views",
                        "data",
                        f"export_{model_type}_model.json",
                    ),
                    "r",
                )
            )
        )
        kp._name = "test_model_" + model_type

        imported_models.append(kp.create())

    yield client, imported_models

    client.project.delete()


def test_sml_runner(imported_models):

    from sensiml.dclproj.datasegments import import_model_results
    from sensiml.sml_runner import SMLRunner

    client, imported_models = imported_models

    for model in imported_models:
        print("Testing", model.name)

        x86_config = client.platforms.get_platform_by_name(
            "x86 GCC Generic"
        ).get_config()

        kp_path, status = model.download_library_v2(config=x86_config)
        kp_path

        sml_runner = SMLRunner(kp_path)
        sml_runner.init_model()

        df_imu = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "data", "test_data.csv")
        )
        imu_results = sml_runner.recognize_capture(
            df_imu, model_index=0, get_output_tensor=True
        )

        imu_data_segments = import_model_results(
            imu_results, df_imu, "test_data", "default"
        )

        assert imu_data_segments
