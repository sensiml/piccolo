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

from django.conf import settings
from redis import StrictRedis


class TempBase(object):
    def __init__(self, hostname, prefix="active"):
        self._hostname = hostname
        self._prefix = prefix
        self._table = StrictRedis(settings.REDIS_ADDRESS)

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        self._hostname = value

    @property
    def name(self):
        return "{}.{}".format(self._prefix, self._hostname)

    def delete(self):
        return self._table.delete(self.name)


class TempCounter(TempBase):
    """A class to manage a counter in redis"""

    def increment(self):
        return self._table.incr(self.name)

    def decrement(self):
        return self._table.decr(self.name)

    def get(self):
        value = self._table.get(self.name)
        return None if value is None else int(value)


class TempSet(TempBase):
    """A class to manage a counter in redis"""

    def set_add(self, value):
        return self._table.sadd(self.name, value)

    def set_remove(self, value):
        return self._table.srem(self.name, value)

    def get(self):
        return self._table.smembers(self.name)

    def get_length(self):
        return self._table.scard(self.name)
