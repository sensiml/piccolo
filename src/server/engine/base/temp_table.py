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

import pickle
import re
from logging import getLogger
from uuid import uuid4

from django.conf import settings
from pandas import DataFrame
from redis import StrictRedis
import zlib

logger = getLogger(__name__)


def _variable_is_temp(inputs):
    """
    Check if string input has temp.<name> notation.
    Returns the regex match object if it does, None otherwise
    """
    temp_pattern = r"(temp\.)(?P<variable_name>[A-Za-z0-9\._-]+)"
    regexp = re.compile(temp_pattern)
    return regexp.match(inputs)


def _overwrite_variable(inputs):
    """
    Check if string input for writing to dictionary has overwrite.<name>
    notation.
    Returns Boolean value and key string.
    """
    overwrite_pattern = r"(overwrite\.)(?P<variable_name>[A-Za-z0-9\._-]+)"
    regexp = re.compile(overwrite_pattern)
    match = regexp.match(inputs)
    if match is not None:
        return True, match.group("variable_name")
    else:
        return False, inputs


class TempVariableTable(object):
    """A Class to communicate with the redis datastore"""

    def __init__(self, pipeline_id=None):
        if pipeline_id is None:
            self._id = "{}".format(uuid4())
        else:
            self._id = pipeline_id
        self._table = StrictRedis(settings.REDIS_ADDRESS)

    def set_variable_id(self, name):
        return "temp.{}.{}".format(self._id, name)

    def add_variable(self, name, data):
        if isinstance(data, DataFrame):
            self._table.set(
                self.set_variable_id(name), zlib.compress(pickle.dumps(data))
            )
        else:
            self._table.set(self.set_variable_id(name), pickle.dumps(data))

        self._table.set(self.set_variable_id(name) + ".type", type(data).__name__)

    def get_variable(self, name):
        data_type = self._table.get(self.set_variable_id(name) + ".type")

        if data_type == b"DataFrame":
            return pickle.loads(
                zlib.decompress(self._table.get(self.set_variable_id(name)))
            )

        return pickle.loads(self._table.get(self.set_variable_id(name)))

    def variable_exists(self, name):
        return self._table.exists(self.set_variable_id(name))

    def delete_variable(self, name):
        self._table.delete(self.set_variable_id(name))

    def search_keys(self, name):
        keys = self._table.keys(self.set_variable_id(name))
        return map(lambda x: x.decode("utf-8")[len(self._id) + 6 :], keys)

    def add_variable_temp(self, name, data=None, overwrite=False):
        """Add a variable to dictionary, if it's not already in it"""
        if isinstance(name, str):
            match = _variable_is_temp(name)
            if match is not None:
                # Variable was output with temp.(overwrite?).<name> syntax
                # Check if key should be overwritten.
                result, key = _overwrite_variable(match.group("variable_name"))
            else:
                # Variable was output without temp.(overwrite?).<name> syntax
                # Check if key should be overwritten.
                result, key = _overwrite_variable(name)

            if (result is False and self.variable_exists(key)) and not overwrite:
                logger.warning("Variable name already in table!")
            else:
                if result is True and self.variable_exists(key):
                    logger.warning("Variable name in table! Overwriting")
                self.add_variable(key, data)
        else:
            logger.warning("Need a name in string format!")

    def rem_variable_temp(self, name):
        """Remove variable from dictionary, if it exists"""
        if isinstance(name, str):
            match = _variable_is_temp(name)
            if match is not None:
                key = match.group("variable_name")
            else:
                key = name
            if not self.variable_exists(key):
                logger.warning("Variable " + key + " not in table!")
            else:
                self.delete_variable(key)
        else:
            logger.warning("Need a name in string format!")

    def get_variable_temp(self, name):
        """
        Attempt to parse temp.<name> scheme from name input. If the regular
        expression matches, look in the dictionary for data with matching key.
        If the expression does not match, check dictionary for key. Returns
        NoneType if key does not exist, data pointed to by value otherwise
        """
        name = str(name)
        match = _variable_is_temp(name)
        if match is not None:
            if not self.variable_exists(match.group("variable_name")):
                logger.warning(
                    "Variable with name {} not in table!".format(
                        match.group("variable_name")
                    )
                )
                return None
            else:
                return self.get_variable(match.group("variable_name"))
        else:
            if not self.variable_exists(name):
                logger.warning("Variable with name {} not in table!".format(name))
                return None
            else:
                return self.get_variable(name)

    def add_dictionary_temp(self, input_dict):
        """Add in dictionary of results to temp variables"""
        for key, value in input_dict.items():
            self.add_variable_temp(key, data=value)

    def rem_temp_with_list(self, input_list):
        """Remove list of keys from temp variables"""
        for key in input_list:
            self.rem_variable_temp(key)

    def get_persistent_variables(self, key_prefix="persist.*"):
        """Return list of temp variables with the key_prefix. The values
        and temp names are returned, although this type of variable is a
        dictionary that contains its own recognition-time variable name."""

        keys = self.search_keys(key_prefix)

        # filter out the type variables from the search
        keys = [key for key in keys if ".type" != key[-5:]]

        return map(lambda key: {"name": key, "value": self.get_variable(key)}, keys)

    def clean_up_temp(self):
        """Delete all the key values that have the id"""
        self.rem_temp_with_list(self.search_keys("*"))

    def clean_up_variables(self, name):
        """Delete all the key values that have the name"""
        match = _variable_is_temp(name)

        if match is not None:
            key = match.group("variable_name")
        else:
            key = name

        self.rem_temp_with_list(self.search_keys("{}*".format(key)))
