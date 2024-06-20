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

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            assert (check_subdirs_empty(settings.SERVER_DATA_ROOT)) == True, (
                "root directory: " + settings.SERVER_DATA_ROOT + " not empty"
            )
            assert (check_subdirs_empty(settings.SERVER_CACHE_ROOT)) == True, (
                "root directory: " + settings.SERVER_CACHE_ROOT + " not empty"
            )
            assert (check_lib_empty(settings.KBLIB_ROOT)) == [], (
                "root directory: " + settings.KBLIB_ROOT + " not empty"
            )
        except AssertionError as e:
            raise CommandError(e)


def check_lib_empty(rootdir):
    return os.listdir(rootdir)


def check_subdirs_empty(rootdir):
    for dirpath, dirs, files in os.walk(rootdir):
        if files:
            return False
        else:
            return True
