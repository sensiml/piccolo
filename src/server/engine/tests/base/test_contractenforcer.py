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

from engine.base.contractenforcer import ContractEnforcer, ContractError


class TestContractEnforcer:
    """Unit tests for EventFile and EventFiles."""

    fixtures = ["datamanager.yml", "develop.yml"]

    @pytest.fixture(autouse=True)
    def setup(self):
        self._pipeline = {
            "name": "normalization",
            "type": "transform",
            "inputs": {
                "inputVector": "x",
                "minBound": "y",
                "maxBound": 3,
                "maxBound_float": 3.12,
                "maxBound_int": 1,
            },
            "outputs": ["temp.t1_data"],
        }
        self._json_contract = [
            {"name": "inputVector", "type": "str", "subtype": "numeric", "size_min": 2},
            {"name": "minBound", "type": "str", "default": 0.0},
            {"name": "maxBound", "type": "float", "default": 1.0},
            {"name": "maxBound_float", "type": "float", "default": 1.0},
            {"name": "maxBound_int", "type": "int", "default": 1.0},
        ]
        self._contractenforcer = None
        self._contractenforcer = ContractEnforcer(
            self._pipeline, self._json_contract, self._pipeline["name"]
        )

    def test_contractenforcer_create(self):
        assert self._contractenforcer is not None

    def test_contractenforcer_extract(self):
        assert len(self._contractenforcer._contract_types) == 5

    def test_contractenforcer_enforce_output(self):
        assert self._contractenforcer.enforce_output(1, 1) == True
        try:
            self._contractenforcer.enforce_output(1, 2)
            assert True == False  # Means that enforcement failed
        except ContractError:
            assert True == True

    def test_contractenforcer_enforce(self):
        assert self._contractenforcer.enforce() == {
            "inputVector": "x",
            "maxBound": 3,
            "minBound": "y",
            "maxBound_float": 3.12,
            "maxBound_int": 1,
        }
