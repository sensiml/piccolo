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

import json

import pytest

from datamanager.sandbox import Sandbox
from engine.base.cache_manager import CacheManager


class TestCacheManager:
    """Unit tests for the CacheManager."""

    fixtures = ["datamanager.yml", "develop.yml"]

    @pytest.fixture(autouse=True)
    @pytest.mark.django_db(transaction=True)
    def setUp(self):
        self._sandbox = Sandbox(name="test")
        self.step1 = {
            "inputs": {
                "group_columns": ["Filename", "Subject", "Activity", "ActivityName"],
                "input_data": "temp.raw",
                "number_of_times": 1,
                "sample_size": 128,
            },
            "outputs": ["temp.feat", "temp.featstats"],
            "set": [
                {"function_name": "Mean", "inputs": {"columns": ["AccelerometerY"]}},
                {
                    "function_name": "Standard Deviation",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "Skewness",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "Kurtosis",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "25th Percentile",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "75th Percentile",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "100th Percentile",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
                {
                    "function_name": "Zero Crossing Rate",
                    "inputs": {"columns": ["AccelerometerY"]},
                },
            ],
            "type": "generatorset",
        }
        self.step2 = {
            "inputs": {
                "cost_function": "sum",
                "feature_table": "temp.featstats",
                "input_data": "temp.feat",
                "label_column": "ActivityName",
                "number_of_features": 5,
                "passthrough_columns": ["Filename", "Subject", "Activity"],
                "remove_columns": [],
            },
            "outputs": ["temp.selected", "temp.selstats"],
            "refinement": {},
            "set": [
                {
                    "function_name": "Recursive Feature Elimination",
                    "inputs": {"method": "Log R"},
                }
            ],
            "type": "selectorset",
        }
        self.step3 = {
            "inputs": {
                "input_data": "temp.selected",
                "max_bound": 254,
                "min_bound": 0,
                "passthrough_columns": [
                    "Filename",
                    "Subject",
                    "Activity",
                    "ActivityName",
                ],
            },
            "name": "Min Max Scale",
            "outputs": ["temp.scaled"],
            "type": "transform",
        }

        pipeline = [self.step1, self.step2, self.step3]

        self._sandbox.pipeline = json.dumps(pipeline)

        self._sandbox.cache = {
            "pipeline": pipeline[0:2],
            "data": {
                "temp.feat": "",
                "temp.featstats": "",
                "temp.selected": "",
                "temp.selstats": "",
                "temp.scaled": "",
            },
            "errors": ["error1", "error2"],
        }
        self._sandbox.save()
        self._test_cache = CacheManager(self._sandbox, pipeline)

    @pytest.mark.django_db(transaction=True)
    def test_write_cache_list(self):

        assert self._test_cache._cache_is_present()

        assert ["error1", "error2"] == self._test_cache.get_cache_list("errors")

        list_of_dicts = [
            {"name": "set1", "value": ["error_1", "error_2"]},
            {"name": "set2", "value": ["error3", "error4", "error5"]},
        ]
        self._test_cache.write_cache_list(list_of_dicts, "errors")

        # Get the stored list and assert that it is correct
        test_result = self._test_cache.get_cache_list("errors")
        assert ["error_1", "error_2", "error3", "error4", "error5"] == test_result

    @pytest.mark.skip(
        reason="Method changed and cannot be unit tested anymore because the file path or s3 key must exist"
    )
    def test_cache_manager_validate_step_true(self):
        assert self._test_cache.step_has_valid_cache(0, self.step1)
        assert self._test_cache.step_has_valid_cache(1, self.step2)

    @pytest.mark.skip(
        reason="Method changed and cannot be unit tested anymore because the file path or s3 key must exist"
    )
    def test_cache_manager_validate_step_false(self):
        assert not self._test_cache.step_has_valid_cache(2, self.step3)
        modified_step = self.step2
        modified_step["inputs"]["number_of_features"] = 6
        assert not self._test_cache.step_has_valid_cache(1, modified_step)
