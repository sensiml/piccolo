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

from engine.base import cost_manager
from library.models import Transform


class TesetCostManager:
    """Unit tests for cost management."""

    def setUp(self):
        self.support_params = {
            "kbtoplevel": {"sram": "0", "flash": "0", "num": 1, "stack": "76"},
            "another_function": {
                "sram": "248",
                "flash": "1250",
                "stack": "1000",
                "num": 1,
            },
            "median_sample_size": 12,
        }

        self.test_costs = {
            "test": {
                "latency": "12",
                "sram": "52",
                "flash": "632",
                "stack_dependencies": ["kbtoplevel"],
                "stack": "28",
                "function_type": "test",
                "function_id": None,
                "flash_dependencies": ["another_function"],
                "c_function_name": "qrk_functions",
            }
        }

    def test_stack_sum(self):
        """Stack costs from 'test' and 'kbtoplevel' and 'another_function' should be summed:
        28 + 76 1000 = 1104"""
        costs = cost_manager.calc_function_costs(
            "test", "", self.test_costs, self.support_params
        )
        assert 1104 == costs["stack"]

    def test_flash_sram_sum(self):
        """Flash costs from 'test' and 'another_function' should be summed: 632 + 1250 = 1882 (float is okay)
        SRAM costs from 'test' and 'another_function' should be summed: 52 + 248 = 300 (float is okay)
        """
        costs = cost_manager.calc_function_costs(
            "test", "", self.test_costs, self.support_params
        )
        assert 1882.0 == costs["flash"]
        assert 300.0 == costs["sram"]

    def test_latency(self):
        """Latency cost should be test's latency multiplied by 'median_sample_size': 12 * 12 = 144"""
        costs = cost_manager.calc_function_costs(
            "test", "", self.test_costs, self.support_params
        )
        assert 144 == costs["latency"]

    def test_latency_with_multiplier(self):
        """Latency cost should be test's latency multiplied by 'median_sample_size' multiplied by
        5: 12 * 12 * 5 = 720"""
        costs = cost_manager.calc_function_costs(
            "test", "", self.test_costs, self.support_params, latency_factor=5
        )
        assert 720 == costs["latency"]


class TestCostData:
    """Unit tests for cost data."""

    fixtures = ["cost_test.yml", "test_classifier_costs.yml"]

    @pytest.mark.django_db(transaction=True)
    def test_get_costs_from_database(self):
        """All core functions with a C version should include latency, flash, sram, and stack"""
        core_functions = Transform.objects.filter(has_c_version=True)
        for function in core_functions:
            costs = cost_manager.get_costs_from_database(function.name)
            for cost in ["latency", "flash", "sram", "stack"]:
                assert cost in costs.keys()

    @pytest.mark.django_db(transaction=True)
    def test_init_support_costs(self):
        """Check that support function cost initialization is correct"""
        parameters = cost_manager.init_support_costs()
        for function in parameters.keys():
            # Initial count of calling functions should be equal to 0
            assert 0 == parameters[function]["num"]
            # Costs should include flash, sram, and stack
            for cost in ["flash", "sram", "stack"]:
                assert cost in parameters[function].keys()
