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

import pytest
from oauth2_provider.models import AbstractApplication
import os
from io import BytesIO

from datamanager.models import Project
from oauthlib.oauth2 import LegacyApplicationClient
from requests import Request
from requests_oauthlib import OAuth2, OAuth2Session
from rest_framework import status
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError


def test_oauthlib(live_server):

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    project = Project.objects.create(name="test", team_id=1)

    username = "unittest@piccolo.com"
    password = "TinyML4Life"
    client_id = "f7J0QNKkKcIkHMpk5lvq0wGZtBEpw1YcJ8Bea9Pv"
    client_secret = "4OxQzkEnVc6OmTMKHgi77o8uFhEDz1QCuyKsNFm2Jo84r0TlGBXli0NrZ5uHTI769P3UurvDVB86awZkrEikCUJ7RM333BTS5oajO32BRwsNkPcOzA3JlBkPblvKM0l0"

    client = LegacyApplicationClient(client_id=client_id)
    session = OAuth2Session(client=client)

    token = session.fetch_token(
        token_url=live_server.url + "/oauth/token/",
        username=username,
        password=password,
        auth=(client_id, client_secret),
        verify=False,
    )
    req = Request(
        "post",
        live_server.url + "/project/{0}/capture/".format(project.uuid),
        data={"name": "TestFile"},
        files={"file": BytesIO(bytes(10))},
        auth=OAuth2(client=client),
    )

    assert token["token_type"] == "Bearer"
    assert token["access_token"] is not None


def test_oauthlib_bad_password(live_server):

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    project = Project.objects.create(name="test", team_id=1)

    username = "unittest@piccolo.com"
    password = "ready"
    client_id = "f7J0QNKkKcIkHMpk5lvq0wGZtBEpw1YcJ8Bea9Pv"
    client_secret = "4OxQzkEnVc6OmTMKHgi77o8uFhEDz1QCuyKsNFm2Jo84r0TlGBXli0NrZ5uHTI769P3UurvDVB86awZkrEikCUJ7RM333BTS5oajO32BRwsNkPcOzA3JlBkPblvKM0l0"

    client = LegacyApplicationClient(client_id=client_id)
    session = OAuth2Session(client=client)

    try:
        token = session.fetch_token(
            token_url=live_server.url + "/oauth/token/",
            username=username,
            password=password,
            auth=(client_id, client_secret),
            verify=False,
        )
    except InvalidGrantError:
        pass
