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

import pandas as pd
from codegen.knowledgepack_model_graph_mixin import (
    column_transform,
    get_feature_scale_value,
    get_nearest_power_2_buffer,
    get_transform_parameters,
    reduce_context,
)

"""Test Codegen Utility Functions"""


def test_column_transform():

    column = "AABB"

    column_transform(column, "pipeline", 0)

    column_transform(column, "sensor", 0)

    column = "AABB-CC"

    column_transform(column, "pipeline", 1)

    column_transform(column, "sensor", 1)


def test_get_nearest_power_2_buffer():

    assert get_nearest_power_2_buffer(0) == 0
    assert get_nearest_power_2_buffer(1) == 2
    assert get_nearest_power_2_buffer(2) == 2
    assert get_nearest_power_2_buffer(3) == 4

    assert get_nearest_power_2_buffer(250) == 256
    assert get_nearest_power_2_buffer(256) == 256
    assert get_nearest_power_2_buffer(257) == 512


def test_reduce_context():
    test_data = [
        {
            "Category": "Rate of Change",
            "ContextIndex": 2,
            "EliminatedBy": "",
            "Feature": "gen_0003_AccelerometerZMeanCrossingRate",
            "Generator": "Mean Crossing Rate",
            "GeneratorFamilyFeatures": 1,
            "GeneratorFamilyIndex": 0,
            "GeneratorIndex": 0,
            "GeneratorTrueIndex": 3,
            "Sensors": ["AccelerometerZ"],
        },
        {
            "Category": "Transpose",
            "ContextIndex": 4,
            "EliminatedBy": "",
            "Feature": "gen_0004_AccelerometerX_signal_bin_000001",
            "Generator": "Transpose Signal",
            "GeneratorFamilyFeatures": 15,
            "GeneratorFamilyIndex": 1,
            "GeneratorIndex": 1,
            "GeneratorTrueIndex": 4,
            "Sensors": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        },
        {
            "Category": "Transpose",
            "ContextIndex": 5,
            "EliminatedBy": "",
            "Feature": "gen_0004_AccelerometerX_signal_bin_000002",
            "Generator": "Transpose Signal",
            "GeneratorFamilyFeatures": 15,
            "GeneratorFamilyIndex": 2,
            "GeneratorIndex": 1,
            "GeneratorTrueIndex": 4,
            "Sensors": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        },
        {
            "Category": "Transpose",
            "ContextIndex": 6,
            "EliminatedBy": "",
            "Feature": "gen_0004_AccelerometerX_signal_bin_000003",
            "Generator": "Transpose Signal",
            "GeneratorFamilyFeatures": 15,
            "GeneratorFamilyIndex": 3,
            "GeneratorIndex": 1,
            "GeneratorTrueIndex": 4,
            "Sensors": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        },
        {
            "Category": "Transpose",
            "ContextIndex": 7,
            "EliminatedBy": "",
            "Feature": "gen_0004_AccelerometerX_signal_bin_000004",
            "Generator": "Transpose Signal",
            "GeneratorFamilyFeatures": 15,
            "GeneratorFamilyIndex": 4,
            "GeneratorIndex": 1,
            "GeneratorTrueIndex": 4,
            "Sensors": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        },
        {
            "Category": "Transpose",
            "ContextIndex": 14,
            "EliminatedBy": "",
            "Feature": "gen_0004_AccelerometerZ_signal_bin_000001",
            "Generator": "Transpose Signal",
            "GeneratorFamilyFeatures": 15,
            "GeneratorFamilyIndex": 11,
            "GeneratorIndex": 1,
            "GeneratorTrueIndex": 4,
            "Sensors": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        },
        {
            "Category": "Transpose",
            "ContextIndex": 15,
            "EliminatedBy": "",
            "Feature": "gen_0004_AccelerometerZ_signal_bin_000002",
            "Generator": "Transpose Signal",
            "GeneratorFamilyFeatures": 15,
            "GeneratorFamilyIndex": 12,
            "GeneratorIndex": 1,
            "GeneratorTrueIndex": 4,
            "Sensors": ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        },
        {
            "Category": "Rate of Change",
            "ContextIndex": 18,
            "EliminatedBy": "",
            "Feature": "gen_0005_AccelerometerXZeroCrossingRate",
            "Generator": "Zero Crossing Rate",
            "GeneratorFamilyFeatures": 1,
            "GeneratorFamilyIndex": 0,
            "GeneratorIndex": 2,
            "GeneratorTrueIndex": 5,
            "Sensors": ["AccelerometerX"],
        },
        {
            "Category": "Rate of Change",
            "ContextIndex": 20,
            "EliminatedBy": "",
            "Feature": "gen_0007_AccelerometerZZeroCrossingRate",
            "Generator": "Zero Crossing Rate",
            "GeneratorFamilyFeatures": 1,
            "GeneratorFamilyIndex": 0,
            "GeneratorIndex": 2,
            "GeneratorTrueIndex": 7,
            "Sensors": ["AccelerometerZ"],
        },
    ]

    result = reduce_context(pd.DataFrame(test_data))

    expected_result = [0, 2, 3, 4, 5, 12, 13, 16, 17]

    assert result == expected_result


def test_reduce_context_with_cascade():
    test_data = [
        {
            "Feature": "gen_c0000_gen_0001_AccelerometerXminimum",
            "Sensors": ["AccelerometerX"],
            "Category": "Statistical",
            "Generator": "Minimum",
            "CascadeIndex": 0,
            "ContextIndex": 0,
            "EliminatedBy": None,
            "GeneratorIndex": 0,
            "GeneratorTrueIndex": 1,
            "GeneratorFamilyIndex": 0,
            "GeneratorFamilyFeatures": 1,
        },
        {
            "Feature": "gen_c0001_gen_0001_AccelerometerXminimum",
            "Sensors": ["AccelerometerX"],
            "Category": "Statistical",
            "Generator": "Minimum",
            "CascadeIndex": 1,
            "ContextIndex": 0,
            "EliminatedBy": None,
            "GeneratorIndex": 0,
            "GeneratorTrueIndex": 1,
            "GeneratorFamilyIndex": 0,
            "GeneratorFamilyFeatures": 1,
        },
        {
            "Feature": "gen_c0001_gen_0003_AccelerometerXmaximum",
            "Sensors": ["AccelerometerX"],
            "Category": "Statistical",
            "Generator": "Maximum",
            "CascadeIndex": 1,
            "ContextIndex": 2,
            "EliminatedBy": None,
            "GeneratorIndex": 2,
            "GeneratorTrueIndex": 3,
            "GeneratorFamilyIndex": 0,
            "GeneratorFamilyFeatures": 1,
        },
    ]

    result = reduce_context(pd.DataFrame(test_data))

    expected_result = [0, 2, 3]

    assert result == expected_result


def test_get_feature_scale_value():
    maximums = {"gen_c_00001_A": 20, "B": 10, "E": 0}
    assert 10.0 == get_feature_scale_value(maximums, "B")
    assert 10.0 == get_feature_scale_value(maximums, "gen_c0000_B")
    assert 20.0 == get_feature_scale_value(maximums, "gen_c_00001_A")
    assert 0.0 == get_feature_scale_value(maximums, "E")

    exception_raised = False
    try:
        get_feature_scale_value(maximums, "gen_c_00001_C")
    except:
        exception_raised = True

    assert exception_raised


def test_get_transform_parameters():

    tr_segment_strip_contracts = {
        "input_contract": [
            {"name": "input_data", "type": "DataFrame"},
            {"name": "group_columns", "type": "list", "element_type": "str"},
            {"name": "input_columns", "type": "list", "element_type": "str"},
            {
                "name": "type",
                "type": "str",
                "options": [
                    {"name": "mean"},
                    {"name": "min"},
                    {"name": "std"},
                    {"name": "median"},
                ],
                "c_param": 0,
                "c_param_mapping": {"min": 0, "mean": 1, "median": 3, "std": 2},
            },
            {
                "name": "threshold",
                "type": "int",
                "c_param": 1,
                "default": 5,
            },
            {
                "name": "lower",
                "type": "boolean",
                "c_param": 2,
                "default": True,
            },
            {
                "name": "is_training",
                "type": "boolean",
                "default": True,
            },
        ],
        "output_contract": [{"name": "df_out", "type": "DataFrame"}],
    }

    inputs = {
        "group_columns": [1, 2, 3],
        "type": "std",
        "lower": False,
        "threshold": 10,
        "is_training": True,
    }

    results = get_transform_parameters(
        inputs, tr_segment_strip_contracts["input_contract"]
    )

    expected_results = [
        {"value": 2, "name": "type", "index": 0},
        {"value": 10, "name": "threshold", "index": 1},
        {"value": False, "name": "lower", "index": 2},
    ]

    assert results == expected_results

    inputs_missing = {
        "group_columns": [1, 2, 3],
        "type": "std",
        "lower": False,
        "is_training": True,
    }

    results = get_transform_parameters(
        inputs_missing, tr_segment_strip_contracts["input_contract"]
    )

    print(results)
    expected_results = [
        {"value": 2, "name": "type", "index": 0},
        {"value": 5, "name": "threshold", "index": 1},
        {"value": False, "name": "lower", "index": 2},
    ]

    assert results == expected_results
