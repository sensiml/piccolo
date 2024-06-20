import os
import random
import shutil

import pytest


def test_upload_project(ClientConnectionSession):

    client = ClientConnectionSession
    project_name = "Test_Project_UPLOAD"
    client.project = project_name
    client.project.delete()

    shutil.unpack_archive(
        os.path.join(os.path.dirname(__file__), "data", "Smart_Lock_IMU.zip"),
        os.path.join(os.path.dirname(__file__), "data"),
    )

    client.upload_project(
        project_name,
        os.path.join(
            os.path.dirname(__file__),
            "data",
            "Smart_Lock_IMU",
            "Smart_Lock_IMU.dclproj",
        ),
    )

    expected_captures = sorted(
        [
            "keyio_001.csv",
            "record_session_imu_10.csv",
            "record_session_imu_9.csv",
            "record_session_imu_8.csv",
            "record_session_imu_7.csv",
            "record_session_imu_6.csv",
            "record_session_imu_5.csv",
            "record_session_imu_4.csv",
            "record_session_imu_3.csv",
            "record_session_imu_2.csv",
            "record_session_imu_1.csv",
            "mixed_events_001.csv",
            "lock_004.csv",
            "lock_003.csv",
            "lock_002.csv",
            "lock_001.csv",
            "knocking_005.csv",
            "knocking_004.csv",
            "knocking_003.csv",
            "knocking_002.csv",
            "keyio_004.csv",
            "keyio_003.csv",
            "keyio_002.csv",
        ]
    )

    assert (
        sorted(client.list_captures(force=True).Name.values.tolist())
        == expected_captures
    )

    client.project.delete()
