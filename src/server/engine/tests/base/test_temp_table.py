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

from engine.base import temp_table


class TestTempVariableTable:
    """Unit tests for UtilError and UtilErrorEncoder creation."""

    fixtures = ["datamanager.yml", "develop.yml"]

    @pytest.fixture(autouse=True)
    def setup(self):
        self.tvars = temp_table.TempVariableTable()

    def test_add_get_var(self):
        """Verify we add dictionary items properly, and dont do duplicates
        without the proper tagging.
        """
        self.tvars.add_variable_temp("Variable1", data=5)
        self.tvars.add_variable_temp("Variable2", data=[5, 6, 7])

        assert self.tvars.get_variable_temp("Variable1") == 5
        assert self.tvars.get_variable_temp("temp.Variable2") == [5, 6, 7]
        assert self.tvars.get_variable_temp("Notintable") is None

        self.tvars.add_variable_temp("Variable1", data=9)
        assert self.tvars.get_variable_temp("Variable1") != 9

        self.tvars.add_variable_temp("overwrite.Variable1", 9)
        assert self.tvars.get_variable_temp("Variable1") == 9

        self.tvars.clean_up_temp()

    def test_rem_vars(self):
        self.tvars.add_variable_temp("Variable1", data=5)
        self.tvars.add_variable_temp("Variable2", data=[5, 6, 7])

        assert self.tvars.get_variable_temp("temp.Variable1") == 5
        assert self.tvars.get_variable_temp("Variable2") == [5, 6, 7]

        self.tvars.rem_variable_temp("Variable1")
        assert self.tvars.get_variable_temp("Variable1") is None
        self.tvars.clean_up_temp()

    def test_dict_add_remove(self):
        """Test addition with a dictionary, removal with list of keys"""
        dict_add = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        list_rem = ["two", "four"]
        dict_add2 = {
            "one": 5,
            "temp.two": 4,
            "temp.overwrite.three": 2,
            "four": 3,
            "overwrite.five": 1,
        }

        self.tvars.add_dictionary_temp(dict_add)
        assert self.tvars.get_variable_temp("one") == 1
        assert self.tvars.get_variable_temp("two") == 2
        assert self.tvars.get_variable_temp("three") == 3
        assert self.tvars.get_variable_temp("four") == 4
        assert self.tvars.get_variable_temp("five") == 5

        self.tvars.rem_temp_with_list(list_rem)

        assert self.tvars.get_variable_temp("two") is None
        assert self.tvars.get_variable_temp("four") is None

        assert self.tvars.get_variable_temp("one") == 1
        assert self.tvars.get_variable_temp("three") == 3
        assert self.tvars.get_variable_temp("five") == 5

        self.tvars.add_dictionary_temp(dict_add2)
        assert self.tvars.get_variable_temp("one") == 1
        assert self.tvars.get_variable_temp("two") == 4
        assert self.tvars.get_variable_temp("three") == 2
        assert self.tvars.get_variable_temp("four") == 3
        assert self.tvars.get_variable_temp("five") == 1
        self.tvars.clean_up_temp()
