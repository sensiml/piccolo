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

import numpy as np
from datamanager.datasegments import dataframe_to_datasegments
from library.core_functions.feature_generators.fg_stats import (
    fg_stats_linear_regression as stats_linear_regression,
)
from library.core_functions_python.feature_generators.fg_stats import (
    stats_linear_regression as scipy_stats_linear_regression,
)
from pandas import DataFrame


class TestStatsLinearRegression:
    """Test Histogram feature generators."""

    def setup(self):
        pass

    def test_stats_linear_regression(self):
        """Call the function and match to ground data."""

        # positive slope
        df = DataFrame()
        df["X"] = [i + 2 for i in range(10)]
        df["Y"] = [i for i in range(10)]
        df["Z"] = [1, 2, 3, 3, 5, 5, 7, 7, 9, 10]
        df["Subject"] = "A"

        data_segment = dataframe_to_datasegments(
            df, data_columns=["X", "Y", "Z"], group_columns=["Subject"]
        )[0]

        results = stats_linear_regression(data_segment, ["X", "Y", "Z"])

        expected_columns = [
            "XLinearRegressionSlope_0000",
            "XLinearRegressionIntercept_0001",
            "XLinearRegressionR_0002",
            "XLinearRegressionStdErr_0003",
            "YLinearRegressionSlope_0000",
            "YLinearRegressionIntercept_0001",
            "YLinearRegressionR_0002",
            "YLinearRegressionStdErr_0003",
            "ZLinearRegressionSlope_0000",
            "ZLinearRegressionIntercept_0001",
            "ZLinearRegressionR_0002",
            "ZLinearRegressionStdErr_0003",
        ]
        assert list(results.columns) == expected_columns

        expected_values = np.array(
            [
                1.0,
                2.0,
                1.0,
                0.0,
                1.0,
                0.0,
                1.0,
                0.0,
                0.982,
                0.782,
                0.987,
                0.056,
            ]
        )
        np.testing.assert_array_almost_equal(
            results.loc[0].values, expected_values, decimal=1
        )

        python_results = scipy_stats_linear_regression(df, ["X", "Y", "Z"])
        print(python_results.values)
        np.testing.assert_array_almost_equal(
            python_results.loc[0].values, results.loc[0].values, decimal=1
        )

        # negative slope
        df = DataFrame()
        df["X"] = [10 - i + 2 for i in range(10)]
        df["Y"] = [10 - i for i in range(10)]
        df["Z"] = [10, 8, 7, 7, 5, 5, 3, 3, 1, 0]

        df["Subject"] = "A"

        data_segment = dataframe_to_datasegments(
            df, data_columns=["X", "Y", "Z"], group_columns=["Subject"]
        )[0]

        results = stats_linear_regression(data_segment, ["X", "Y", "Z"])

        expected_columns = [
            "XLinearRegressionSlope_0000",
            "XLinearRegressionIntercept_0001",
            "XLinearRegressionR_0002",
            "XLinearRegressionStdErr_0003",
            "YLinearRegressionSlope_0000",
            "YLinearRegressionIntercept_0001",
            "YLinearRegressionR_0002",
            "YLinearRegressionStdErr_0003",
            "ZLinearRegressionSlope_0000",
            "ZLinearRegressionIntercept_0001",
            "ZLinearRegressionR_0002",
            "ZLinearRegressionStdErr_0003",
        ]
        assert list(results.columns) == expected_columns

        expected_values = np.array(
            [
                -1.0,
                12.0,
                -1.0,
                0.0,
                -1.0,
                10.0,
                -1.0,
                0.0,
                -1.036,
                9.564,
                -0.987,
                0.059,
            ]
        )
        np.testing.assert_array_almost_equal(
            results.loc[0].values, expected_values, decimal=1
        )

        python_results = scipy_stats_linear_regression(df, ["X", "Y", "Z"])

        np.testing.assert_array_almost_equal(
            python_results.loc[0].values, results.loc[0].values, decimal=1
        )
