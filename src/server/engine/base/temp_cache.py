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

from datamanager import utils
from datamanager.datastore import get_datastore, get_datastore_basedir
from django.conf import settings
from pandas import DataFrame


class TempCache(object):
    def __init__(self, pipeline_id, bucket=None):

        if bucket:
            self._bucket = bucket
        else:
            self._bucket = get_datastore_basedir(settings.SERVER_CACHE_ROOT)

        self._pipeline_id = pipeline_id

        self._datastore = get_datastore(folder=self._bucket)

        utils.ensure_path_exists(self._bucket)

        utils.ensure_path_exists(os.path.join(self._bucket, pipeline_id))

    def set_variable_path_id(self, name):
        if self._datastore.is_remote:
            return f"{self._pipeline_id}/{name}"

        return os.path.join(self._bucket, self._pipeline_id, name)

    def get_file(self, summary):
        """Gets data from the cache corresponding to a particular named variable."""

        if not summary:
            return None

        if isinstance(summary, dict):
            filename = summary.get("filename")
        elif isinstance(summary, str):
            filename = summary

        return self._datastore.get_data(self.set_variable_path_id(filename))

    def write_file(self, data, filename):

        if isinstance(data, DataFrame):
            fmt = ".csv.gz"
            filename += fmt

        elif isinstance(data, dict):
            fmt = ".json"
            filename += fmt

        elif isinstance(data, list):
            fmt = ".pkl"
            filename += fmt

        else:
            raise Exception(
                "Data type {} cannot be written to the cache".format(type(data))
            )

        self._datastore.save_data(data, self.set_variable_path_id(filename), fmt)

        return filename
