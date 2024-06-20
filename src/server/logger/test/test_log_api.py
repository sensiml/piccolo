"""
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os
import json

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from logger.models import Log

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def log_data():
    data = {
        "loglevel": "CRITICAL",
        "username": "tdonkena",
        "application": "Web Client",
        "message": "Test Message",
        "stacktrace": "Some Stack Trace",
        "tag": "Login Error",
        "browser": "Chrome",
        "client_information": json.dumps({"OS": "WinXX"}),
    }

    return data


@pytest.fixture
def login_log_data_usage():
    data = [
        {
            "loglevel": "INFO",
            "username": "unittest@piccolo.com",
            "application": "Web Client",
            "message": "Test Message",
            "stacktrace": "Some Stack Trace",
            "tag": "Login",
            "client_information": json.dumps({"OS": "WinXX"}),
        },
        {
            "loglevel": "INFO",
            "username": "unittest@piccolo.com",
            "application": "Web Client",
            "message": "Test Message",
            "stacktrace": "Some Stack Trace",
            "tag": "Login",
            "client_information": json.dumps({"OS": "WinXX"}),
        },
        {
            "loglevel": "INFO",
            "username": "unittest@piccolo.com",
            "application": "Data Capture Lab - Windows",
            "message": "Test Message",
            "stacktrace": "Some Stack Trace",
            "tag": "Login",
            "client_information": "{}",
        },
        {
            "loglevel": "INFO",
            "username": "unittest@piccolo.com",
            "application": "Data Capture Lab - Windows",
            "message": "Test Message",
            "stacktrace": "Some Stack Trace",
            "tag": "Logout,Test",
            "client_information": json.dumps({"OS": "WinXX"}),
        },
    ]

    return data


def test_logger(authenticated_client, log_data):
    # Check that there are no log messages -- initial state
    assert Log.objects.count() == 0

    response = authenticated_client.post(reverse("log"), log_data)

    # validate that the status code is OK
    assert response.status_code == status.HTTP_201_CREATED

    # validate that there is one log message in the model
    assert Log.objects.count() == 1

    log = Log.objects.first()

    # validate that the log properties are as expected
    assert log.loglevel.name == log_data["loglevel"]
    assert log.username == log_data["username"]
    assert log.application.name == log_data["application"]
    assert log.message == log_data["message"]
    assert log.stacktrace == log_data["stacktrace"]
    # assert log.tag == log_data["tag"]
    assert log.client_information == json.loads(log_data["client_information"])

    with open(
        os.path.join(os.path.dirname(__file__), "../../client_logs.log"), "r"
    ) as fid:
        lines = fid.readlines()
        header_size = len("[07/Jul/2021 21:35:58] INFO [logger.serializers:81]")
        result = json.loads(lines[-1][header_size:])

    assert result["loglevel"] == log_data["loglevel"]
    assert result["log_type"] == "client_logs"
    assert result["username"] == log_data["username"]
    assert result["application"] == log_data["application"]
