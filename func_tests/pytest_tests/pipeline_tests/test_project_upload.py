import os
import os.path
import time

import numpy as np
import pandas as pd
import pytest


def test_project_upload(ClientConnection):

    client = ClientConnection

    client.project = "test_dcli_upload"
    client.project.delete()

    client.upload_project_dcli(
        "test_dcli_upload",
        os.path.join(os.path.dirname(__file__), "data", "fan_demo", "Export.dcli"),
    )

    expected_captures = [
        "Blocked Flow 2021-04-26 15_29_33.csv",
        "Blocked Flow 2021-04-26 20_47_46.csv",
        "Fan Off 2021-04-26 15_27_02.csv",
        "Fan On 2021-04-26 15_25_35.csv",
        "Fan On 2021-04-26 15_48_58.csv",
        "Fan On 2021-04-27 08_26_42.csv",
        "TestCollection_Unknown.csv",
        "Unknown 2021-04-26 20_48_29.csv",
    ]

    assert sorted(client.list_captures(force=True).Name.values) == expected_captures

    expected_metadata_values = [
        "Connection",
        "Device",
        "Fan Type",
        "Mounted",
        "capture_uuid",
        "segment_uuid",
        "set",
    ]

    assert sorted(client.project.metadata_columns()) == expected_metadata_values

    client.project.delete()
