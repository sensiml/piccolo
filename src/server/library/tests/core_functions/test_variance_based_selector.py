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
from pandas import DataFrame

from library.core_functions.selectors import vt_select


class TestCorrSelectMostCorr:
    """Test variance based feature selector and cost functions."""

    @pytest.fixture(autouse=True)
    def setup(self):

        df_dict = {
            u"gen_0002_accely_3": {
                0: 827.019165039,
                1: 646.515136719,
                2: 458.467132568,
                3: -3949.10766602,
                4: -3979.70678711,
                5: -4067.22119141,
                6: -4040.61425781,
                7: -4009.10400391,
                8: -4064.70361328,
            },
            u"gen_0002_accely_2": {
                0: 884.166137695,
                1: 554.7843017580001,
                2: 455.253967285,
                3: -4051.07397461,
                4: -3989.12011719,
                5: -4125.203125,
                6: -4020.22705078,
                7: -4029.36621094,
                8: -4085.73168945,
            },
            u"gen_0002_accely_1": {
                0: 862.607055664,
                1: 557.2834472659999,
                2: 199.48753356900002,
                3: -3971.01123047,
                4: -4037.01367188,
                5: -4045.68139648,
                6: -4049.24609375,
                7: -3995.64868164,
                8: -4073.91992188,
            },
            u"gen_0002_accely_0": {
                0: 1016.71246338,
                1: 628.616760254,
                2: -332.48980712900004,
                3: -4029.77441406,
                4: -3940.42431641,
                5: -4054.88745117,
                6: -4030.74365234,
                7: -4024.11083984,
                8: -4068.20825195,
            },
            u"gen_0002_accely_4": {
                0: 861.546325684,
                1: 668.117675781,
                2: 469.693878174,
                3: -4065.99243164,
                4: -4037.63842773,
                5: -4109.57568359,
                6: -4028.47338867,
                7: -3996.37304688,
                8: -4063.69702148,
            },
            u"gen_0003_accelz_3": {
                0: 3943.37377930,
                1: 3913.5703125,
                2: 3810.61669922,
                3: 720.220581055,
                4: 858.197814941,
                5: 241.68269348099997,
                6: 564.68145752,
                7: 722.66619873,
                8: -116.588783264,
            },
            u"gen_0003_accelz_2": {
                0: 3899.03515625,
                1: 3858.36181641,
                2: 3851.16088867,
                3: 650.028808594,
                4: 830.342407227,
                5: 185.57691955599998,
                6: 555.1726074219999,
                7: 670.53918457,
                8: -114.34980011,
            },
            u"gen_0003_accelz_1": {
                0: 3881.03833008,
                1: 3821.51342773,
                2: 3896.34912109,
                3: 641.16418457,
                4: 870.608459473,
                5: 263.18405151400003,
                6: 559.139587402,
                7: 658.902709961,
                8: -87.6128158569,
            },
            u"gen_0003_accelz_0": {
                0: 3977.54003906,
                1: 3889.81640625,
                2: 3972.05444336,
                3: 696.421081543,
                4: 825.3328857419999,
                5: 260.251373291,
                6: 564.148498535,
                7: 730.0297241210001,
                8: -138.078765869,
            },
            u"gen_0003_accelz_4": {
                0: 3900.73486328,
                1: 3896.3762206999995,
                2: 3889.29711914,
                3: 605.192993164,
                4: 846.671203613,
                5: 234.177200317,
                6: 558.538085938,
                7: 669.394592285,
                8: -98.73564910889999,
            },
            u"gen_0001_accelx_4": {
                0: 111.987220764,
                1: 323.65774536099997,
                2: 542.170043945,
                3: 16.7280693054,
                4: 432.530700684,
                5: 398.045318604,
                6: 18.2322330475,
                7: 391.77432251,
                8: 353.17089843800005,
            },
            u"gen_0001_accelx_3": {
                0: 153.923324585,
                1: 83.9857406616,
                2: 494.031738281,
                3: -40.6716804504,
                4: 469.537506104,
                5: 339.887359619,
                6: -16.1104068756,
                7: 385.25405883800005,
                8: 325.496673584,
            },
            u"gen_0001_accelx_2": {
                0: 208.34185791,
                1: 91.9714813232,
                2: 200.26303100599998,
                3: -16.3220558167,
                4: 431.893585205,
                5: 360.77746582,
                6: 0.492385774851,
                7: 374.443237305,
                8: 283.627502441,
            },
            u"gen_0001_accelx_1": {
                0: 372.25878906199995,
                1: 224.231735229,
                2: 503.27664184599996,
                3: -23.5112781525,
                4: 453.950897217,
                5: 366.373626709,
                6: -46.9670066833,
                7: 413.259460449,
                8: 317.618164062,
            },
            u"gen_0001_accelx_0": {
                0: 347.88177490199996,
                1: 347.713012695,
                2: 545.664428711,
                3: -21.5889720917,
                4: 422.405181885,
                5: 350.105773926,
                6: -10.362944602999999,
                7: 375.75134277300003,
                8: 353.421905518,
            },
        }

        self.df = DataFrame(df_dict)

    def test_variance_based_feature_selector(self):
        return_val, _ = vt_select(self.df, threshold=4513492.05, passthrough_columns=[])
        expected_result = [
            "gen_0002_accely_0",
            "gen_0002_accely_1",
            "gen_0002_accely_2",
            "gen_0002_accely_3",
            "gen_0002_accely_4",
        ]
        assert (
            sorted(return_val.columns.tolist()) == expected_result
        ), "test_variance_based_feature_selector failed to return expected results"
