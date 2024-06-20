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



# pylint: disable=W0201

import pytest

import codegen.knowledgepack_model_graph_mixin as kp_cg

pytestmark = pytest.mark.django_db  # All tests use db


class TestUtilityFunctions:
    """Test Codegen Utility Functions"""

    def test_get_model_groups(self):

        kp_description = {
            0: {"uuid": "test0", "parent": None},
            1: {"uuid": "test1", "parent": None},
            2: {"uuid": "test2", "parent": 0},
        }
        result = kp_cg.get_model_group(kp_description)

        expected_result = [[0, 2], [1]]

        assert result == expected_result
