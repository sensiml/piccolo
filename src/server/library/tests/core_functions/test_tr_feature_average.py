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
import pandas as pd

from library.core_functions_python.feature_transforms import tr_feature_average


class TestTrFeatureAverage:
    """Test windowing segmentation algorithm."""

    def test_tr_feature_average(self):

        params = {
            "group_columns": ["Label", "SegmentID", "capture_id"],
            "num_cascades": 2,
            "stride": 2,
        }

        M = []
        M.append(
            pd.DataFrame(
                np.array([list(range(5)), [1] * 5, [1] * 5, list(range(5)), [1] * 5]).T,
                columns=["gen_01_A", "gen_02_B", "Label", "SegmentID", "capture_id"],
            )
        )
        M.append(
            pd.DataFrame(
                np.array([list(range(5)), [1] * 5, [2] * 5, list(range(5)), [2] * 5]).T,
                columns=["gen_01_A", "gen_02_B", "Label", "SegmentID", "capture_id"],
            )
        )
        df = pd.concat(M).reset_index(drop=True)

        df = tr_feature_average(df, **params)

        expected_results = pd.DataFrame(
            {
                "Label": {0: 1, 1: 1, 2: 2, 3: 2},
                "SegmentID": {0: 0, 1: 2, 2: 0, 3: 2},
                "capture_id": {0: 1, 1: 1, 2: 2, 3: 2},
                "gen_01_A": {0: 0.5, 1: 2.5, 2: 0.5, 3: 2.5},
                "gen_02_B": {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0},
            }
        )

        assert df.equals(expected_results)
