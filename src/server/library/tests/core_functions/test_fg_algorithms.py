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

import time

from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.fg_algorithms import (
    run_feature_generator_c_multiple_columns_sandboxed,
    run_feature_generator_c_sandboxed,
)
from pandas import DataFrame


def sleep_function(
    in_array, out_array, params, num_params, num_cols, num_rows, num_results
):
    time.sleep(params[0])
    return


def test_run_feature_generator_c_sandboxed():

    data = DataFrame(
        {
            "X": [1] * 5 + [2] * 10 + [3] * 15 + [4] * 20,
            "Y": [1] * 20 + [2] * 15 + [3] * 10 + [4] * 5,
        },
        columns=["X", "Y"],
    )
    data["Subject"] = "A"

    data = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["Subject"]
    )[0]

    columns = ["X"]

    sleep_time = 1
    res = run_feature_generator_c_sandboxed(
        data, columns, ["test_output"], [sleep_time], sleep_function
    )
    print(res)

    sleep_time = 5
    failed = False
    try:
        res = run_feature_generator_c_sandboxed(
            data, columns, ["test_output"], [sleep_time], sleep_function
        )
    except:
        failed = True

    assert failed


def test_run_feature_generator_c_multiple_columns_sandboxed():

    data = DataFrame(
        {
            "X": [1] * 5 + [2] * 10 + [3] * 15 + [4] * 20,
            "Y": [1] * 20 + [2] * 15 + [3] * 10 + [4] * 5,
        },
        columns=["X", "Y"],
    )
    data["Subject"] = "A"
    columns = ["X", "Y"]

    data = dataframe_to_datasegments(
        data, data_columns=["X", "Y"], group_columns=["Subject"]
    )[0]

    sleep_time = 1
    res = run_feature_generator_c_multiple_columns_sandboxed(
        data, columns, ["test_output"], [sleep_time], sleep_function
    )
    print(res)

    sleep_time = 5
    failed = False
    try:
        res = run_feature_generator_c_multiple_columns_sandboxed(
            data, columns, ["test_output"], [sleep_time], sleep_function
        )
    except:
        failed = True

    assert failed
