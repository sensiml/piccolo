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
import os

# make sure local proxy is disabled.
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""


def pytest_addoption(parser):
    """pytest option used in basetest.py workarounds"""
    parser.addoption(
        "--django", action="store_true", help="Use django LiveServerTestCase"
    )
    parser.addoption("--corefunc", action="store_true", help="Run core function tests")


@pytest.fixture
def oauth(server):
    return {
        "username": "piccolo@sensiml.com",
        "password": "TinyML4Life",
        "client_id": "NaBajqUI3soGpb95sa3lmi1FhnepJsE4sBhGRzql",
        "client_secret": "UswBlm26Gjsw6VticjgBNbfkdVEDEainbe1KfmQJVasBoY7o92oP1NSrdR4xrQmvz8gDUkEuSDMm56ozdiZpG7rlvLqkkEgtRgV8JSslkmpGmH7JBxUP4dBH68b78l43",
        "insecure": True,
        "url": server,
        "auth_url": server + "oauth/",
    }


@pytest.fixture
def oauth_class(request, oauth):
    request.cls.oauth = oauth


@pytest.fixture(scope="module")
def server(request):
    """Returns server URL

    If using --django option, also loads default db fixtures
    """
    if request.config.getoption("--django"):
        from django.core.management import call_command

        live_server = request.getfixturevalue("live_server")
        request.getfixturevalue("django_db_setup")
        django_db_blocker = request.getfixturevalue("django_db_blocker")

        with django_db_blocker.unblock():
            call_command("loaddata", "datamanager", "develop")
            call_command("load_functions")

        return live_server.url + "/"
    else:
        return "http://localhost:8000/"


@pytest.fixture(autouse=True)
def _db_marker(request, server):
    """Checks for `live_db` marker only if --django option is used

    Use instead of `django_db` marker to maintain compat with non-liveserver test runs
    """
    if request.config.getoption("--django"):
        from pytest_django.plugin import validate_django_db

        marker = request.keywords.get("live_db", None)
        if marker:
            validate_django_db(marker)
            if marker.transaction:
                request.getfixturevalue("transactional_db")
            else:
                request.getfixturevalue("db")
