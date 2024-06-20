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

from engine.base import temp_counter


class TestTempCounterTable:
    """Unit tests for UtilError and UtilErrorEncoder creation."""

    fixtures = ["datamanager.yml", "develop.yml"]

    @pytest.fixture(autouse=True)
    def setup(self):
        self.tvars = temp_counter.TempCounter(hostname="test", prefix="test")
        self.tvars.delete()

    def test_increment_decriment_delete(self):
        for i in range(10):
            self.tvars.increment()

        result = self.tvars.decrement()

        expected_result = 9

        assert result == expected_result

        assert self.tvars.get() == expected_result

        self.tvars.delete()

        assert self.tvars.get() is None


class TestTempSet:
    """Unit tests for UtilError and UtilErrorEncoder creation."""

    fixtures = ["datamanager.yml", "develop.yml"]

    @pytest.fixture(autouse=True)
    def setup(self):
        self.tvars = temp_counter.TempSet(hostname="test", prefix="test")
        self.tvars.delete()

    def test_increment_decriment_delete(self):
        for i in range(10):
            self.tvars.set_add(str(i))

        result = self.tvars.set_remove("9")

        expected_result = 1

        assert result == expected_result

        assert self.tvars.get_length() == 9

        for i in range(10):
            self.tvars.set_remove(str(i))

        assert self.tvars.get() == set()
