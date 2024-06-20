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

# pylint: disable=W0613,W0621
import pytest


@pytest.fixture
def loaddata(db):
    """Allows easy loading of django db fixtures for tests"""
    from django.core.management import call_command

    def _(*args):
        call_command("loaddata", *args)

    return _


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    """Automatically loads initial data for testing session

    See http://pytest-django.readthedocs.io/en/latest/database.html#std:fixture-django_db_setup
    for explanation.
    """
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command("loaddata", "application", "applicationapikeys", "loglevel")

    print("loaded stuff")
