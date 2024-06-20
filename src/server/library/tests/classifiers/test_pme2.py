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

﻿import pytest
import os

from library.classifiers.pme import (
    PME,
)


def print_results(results, desired_responses=1):
    print("category", results[0].category)
    print("distance", results[0].distance)
    print("nid", results[0].pattern_id)


class TestPME2:
    """Unit tests for KBEngine."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.file_path = os.path.join(
            os.path.dirname(__file__), "TrainTestData_LOASE_scheme1_int.csv"
        )
        self.engine = PME()

        self.engine.initialize_model(2056, 128)

        self.vectors = [
            {
                "Category": "1",
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Vector": [
                    108,
                    105,
                    103,
                    100,
                    96,
                    91,
                    89,
                    87,
                    83,
                    81,
                    80,
                    80,
                    80,
                    81,
                    81,
                    82,
                    95,
                    123,
                    97,
                    87,
                    77,
                    66,
                    61,
                    66,
                    70,
                    81,
                    95,
                    100,
                    104,
                    113,
                    122,
                    126,
                    129,
                    133,
                    136,
                    138,
                    139,
                    141,
                    142,
                    143,
                    143,
                    143,
                    143,
                    143,
                    143,
                    145,
                    148,
                    150,
                    149,
                    148,
                    142,
                    135,
                    133,
                    131,
                    128,
                    127,
                    127,
                    128,
                    130,
                    134,
                    136,
                    138,
                    142,
                    146,
                    147,
                    148,
                    148,
                    147,
                    146,
                    146,
                    145,
                    146,
                    147,
                    147,
                    149,
                    153,
                    152,
                    152,
                    148,
                    143,
                    139,
                    141,
                    143,
                    148,
                    153,
                    156,
                    160,
                    166,
                    170,
                    170,
                    170,
                    167,
                    162,
                    160,
                    157,
                    152,
                    147,
                    144,
                    142,
                    139,
                    135,
                    134,
                    133,
                    131,
                    128,
                    127,
                    126,
                    124,
                    123,
                    122,
                    122,
                    123,
                    124,
                    125,
                    125,
                    126,
                    125,
                    123,
                    122,
                    121,
                    118,
                    115,
                    113,
                    111,
                    108,
                ],
                "DesiredResponses": 1,
            },
            {
                "Category": "2",
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Vector": [
                    110,
                    105,
                    102,
                    100,
                    97,
                    94,
                    93,
                    92,
                    89,
                    87,
                    85,
                    84,
                    83,
                    81,
                    78,
                    77,
                    76,
                    75,
                    76,
                    73,
                    70,
                    63,
                    61,
                    63,
                    66,
                    69,
                    72,
                    73,
                    74,
                    75,
                    78,
                    83,
                    85,
                    88,
                    94,
                    101,
                    104,
                    107,
                    112,
                    115,
                    119,
                    120,
                    122,
                    126,
                    130,
                    131,
                    132,
                    133,
                    134,
                    135,
                    135,
                    136,
                    136,
                    137,
                    138,
                    141,
                    142,
                    143,
                    144,
                    144,
                    146,
                    147,
                    148,
                    149,
                    151,
                    152,
                    152,
                    152,
                    153,
                    153,
                    154,
                    154,
                    154,
                    155,
                    158,
                    161,
                    163,
                    161,
                    154,
                    152,
                    150,
                    153,
                    157,
                    159,
                    160,
                    162,
                    164,
                    165,
                    165,
                    164,
                    163,
                    161,
                    159,
                    158,
                    156,
                    156,
                    156,
                    156,
                    156,
                    157,
                    157,
                    158,
                    158,
                    157,
                    157,
                    156,
                    155,
                    154,
                    152,
                    151,
                    150,
                    147,
                    143,
                    142,
                    140,
                    138,
                    136,
                    133,
                    131,
                    130,
                    126,
                    121,
                    119,
                    116,
                    111,
                ],
                "DesiredResponses": 1,
            },
        ]

    # test_rbf_knn_learning - tests that rbf and knn classifications are different and
    # working correct for a small subset of neurons
    # params - none
    # returns - nothing
    def test_rbf_knn_learning(self):
        rbf_knn_vectors = [
            {
                "Category": "1",
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Uncertain": [],
                "Vector": [
                    108,
                    105,
                    103,
                    100,
                    96,
                    91,
                    89,
                    87,
                    83,
                    81,
                    80,
                    80,
                    80,
                    81,
                    81,
                    82,
                    95,
                    123,
                    97,
                    87,
                    77,
                    66,
                    61,
                    66,
                    70,
                    81,
                    95,
                    100,
                    104,
                    113,
                    122,
                    126,
                    129,
                    133,
                    136,
                    138,
                    139,
                    141,
                    142,
                    143,
                    143,
                    143,
                    143,
                    143,
                    143,
                    145,
                    148,
                    150,
                    149,
                    148,
                    142,
                    135,
                    133,
                    131,
                    128,
                    127,
                    127,
                    128,
                    130,
                    134,
                    136,
                    138,
                    142,
                    146,
                    147,
                    148,
                    148,
                    147,
                    146,
                    146,
                    145,
                    146,
                    147,
                    147,
                    149,
                    153,
                    152,
                    152,
                    148,
                    143,
                    139,
                    141,
                    143,
                    148,
                    153,
                    156,
                    160,
                    166,
                    170,
                    170,
                    170,
                    167,
                    162,
                    160,
                    157,
                    152,
                    147,
                    144,
                    142,
                    139,
                    135,
                    134,
                    133,
                    131,
                    128,
                    127,
                    126,
                    124,
                    123,
                    122,
                    122,
                    123,
                    124,
                    125,
                    125,
                    126,
                    125,
                    123,
                    122,
                    121,
                    118,
                    115,
                    113,
                    111,
                    108,
                ],
                "DesiredResponses": 1,
            },
            {
                "Category": "1",
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Uncertain": [],
                "Vector": [
                    110,
                    105,
                    102,
                    100,
                    97,
                    94,
                    93,
                    92,
                    89,
                    87,
                    85,
                    84,
                    83,
                    81,
                    78,
                    77,
                    76,
                    75,
                    76,
                    73,
                    70,
                    63,
                    61,
                    63,
                    66,
                    69,
                    72,
                    73,
                    74,
                    75,
                    78,
                    83,
                    85,
                    88,
                    94,
                    101,
                    104,
                    107,
                    112,
                    115,
                    119,
                    120,
                    122,
                    126,
                    130,
                    131,
                    132,
                    133,
                    134,
                    135,
                    135,
                    136,
                    136,
                    137,
                    138,
                    141,
                    142,
                    143,
                    144,
                    144,
                    146,
                    147,
                    148,
                    149,
                    151,
                    152,
                    152,
                    152,
                    153,
                    153,
                    154,
                    154,
                    154,
                    155,
                    158,
                    161,
                    163,
                    161,
                    154,
                    152,
                    150,
                    153,
                    157,
                    159,
                    160,
                    162,
                    164,
                    165,
                    165,
                    164,
                    163,
                    161,
                    159,
                    158,
                    156,
                    156,
                    156,
                    156,
                    156,
                    157,
                    157,
                    158,
                    158,
                    157,
                    157,
                    156,
                    155,
                    154,
                    152,
                    151,
                    150,
                    147,
                    143,
                    142,
                    140,
                    138,
                    136,
                    133,
                    131,
                    130,
                    126,
                    121,
                    119,
                    116,
                    111,
                ],
                "DesiredResponses": 1,
            },
        ]

        expected_rbf_neuron_count = 2
        expected_knn_neuron_count = 1

        # Learn the local vectors with RBF, should produce two neurons
        self.engine.set_classification_mode(self.engine.CLASSIF_MODE_RBF)
        self.engine.set_min_aif(self.engine.MIN_MIN_AIF)
        self.engine.set_max_aif(self.engine.MIN_MIN_AIF + 10)
        self.engine.learn_vectors(rbf_knn_vectors)
        assert expected_rbf_neuron_count == self.engine.get_number_patterns()

        # recognize the vectors with RBF. Should be 100% result with no
        # uncertainty
        stats = self.engine.recognize_vectors(rbf_knn_vectors)
        assert 100 == stats["ProperClassificationPercent"]
        # self.assertEqual(False, rbf_knn_vectors[0]["Uncertain"])
        # self.assertEqual(False, rbf_knn_vectors[1]["Uncertain"])

        # recognize the vectors with KNN. Should also be 100% result with no
        # uncertainty
        self.engine.set_classification_mode(self.engine.CLASSIF_MODE_KNN)
        stats = self.engine.recognize_vectors(rbf_knn_vectors)
        assert 100 == stats["ProperClassificationPercent"]
        # self.assertEqual(False, rbf_knn_vectors[0]["Uncertain"])
        # self.assertEqual(False, rbf_knn_vectors[1]["Uncertain"])

        # reset the neurons, set up for KNN, and learn the vectors, should
        # produce one neuron
        print(self.engine.get_number_patterns())
        self.engine._reset_pme_database()
        print(self.engine.get_number_patterns())
        self.engine.set_classification_mode(self.engine.CLASSIF_MODE_KNN)
        self.engine.set_min_aif(self.engine.MIN_MIN_AIF)
        self.engine.set_max_aif(self.engine.MIN_MIN_AIF + 10)
        self.engine.learn_vectors(rbf_knn_vectors)
        assert expected_knn_neuron_count == self.engine.get_number_patterns()

        # Recognize the two vectors with KNN. Stats should return 100% with no
        # uncertainty
        stats = self.engine.recognize_vectors(rbf_knn_vectors)
        assert 100 == stats["ProperClassificationPercent"]
        # self.assertEqual(False, rbf_knn_vectors[0]["Uncertain"])
        # self.assertEqual(False, rbf_knn_vectors[1]["Uncertain"])

        # Recognize the two vectors with RBF. Stats should return 50% with no
        # uncertainty
        self.engine.set_classification_mode(self.engine.CLASSIF_MODE_RBF)
        stats = self.engine.recognize_vectors(rbf_knn_vectors)
        assert 50 == stats["ProperClassificationPercent"]
        # self.assertEqual(False, rbf_knn_vectors[0]["Uncertain"])
        # self.assertEqual(False, rbf_knn_vectors[1]["Uncertain"])

    # test_learn_and_recognize_vectors - tests that writing two vectors can be recognized
    # params - none
    # returns - nothing
    def test_learn_and_recognize_vectors(self):
        testContext = 0
        self.engine.learn_vectors(self.vectors)
        stats = self.engine.recognize_vectors(self.vectors)  # Should be 100%
        assert 100 == stats["ProperClassificationPercent"]

        # Now do exception testing. Need a slightly different set of vectors.
        learn_and_recognize_vectors = [
            {
                "Category": 1,
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Vector": [1, 253],
                "DesiredResponses": 1,
            },
            {
                "Category": 1,
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Vector": [253, 7],
                "DesiredResponses": 1,
            },
        ]

        self.engine.initialize_model(5, 128)

        # good and and exception and warning categories and contexts
        good_categroy = 1

        # learn_vector: A good category followed by one that causes an
        # exception.
        assert 1 == self.engine._learn_vector(
            testContext, learn_and_recognize_vectors[0]["Vector"], good_categroy
        )

    # test_read_neurons - tests that writing two vectors will produce expected neurons
    # params - none
    # returns - nothing
    def test_read_model(self):
        self.engine.learn_vectors(self.vectors)
        model_parameters = self.engine.dump_model()
        assert 1697 == model_parameters[0]["AIF"]
        assert [108, 105, 103, 100, 96, 91] == model_parameters[0]["Vector"][0:6]
        assert 2 == model_parameters[1]["Category"]

    # test_neurons_used - tests to ensure that learning two vectors produces two neurons
    # params - none
    # returns - nothing
    def test_neurons_used(self):
        expectedNeuronCount = 2
        self.engine.learn_vectors(self.vectors)
        assert expectedNeuronCount == self.engine.get_number_patterns()

    # test_C_engine_init - tests the setting of the HW distance modes
    # params - none
    # returns - nothing
    def test_C_engine_init(self):
        assert 0 == self.engine.initialize_model(128, 128)

        failed = False
        try:
            assert 0 == self.engine.initialize_model(128, 2049)
        except:
            failed = True

        assert failed

    # test_setGetDistanceMode - tests the setting of the HW distance modes
    # params - none
    # returns - nothing
    @pytest.mark.skip(
        "depricate support of curie emulation for device register setting"
    )
    def test_setGetDistanceMode(self):

        distanceModeBadMode1 = -2
        distanceModeBadMode2 = 7
        testDistModeVals = [
            [self.engine.DIST_MODE_LSUP, self.engine.DIST_MODE_LSUP],
            [self.engine.DIST_MODE_L1, self.engine.DIST_MODE_L1],
            [self.engine.DIST_MODE_LSUP, self.engine.DIST_MODE_LSUP],
            [distanceModeBadMode1, self.engine.DIST_MODE_L1],
            [self.engine.DIST_MODE_LSUP, self.engine.DIST_MODE_LSUP],
            [distanceModeBadMode2, self.engine.DIST_MODE_L1],
            [self.engine.DIST_MODE_LSUP, self.engine.DIST_MODE_LSUP],
            [self.engine.DIST_MODE_L1, self.engine.DIST_MODE_L1],
            [self.engine.DIST_MODE_LSUP, self.engine.DIST_MODE_LSUP],
        ]
        for i in range(0, len(testDistModeVals)):
            self.engine.set_distance_mode(testDistModeVals[i][0])
            value = self.engine.get_distance_mode()
            assert value == testDistModeVals[i][1]

    # test_setGetClassifcationMode - tests the setting of the HW classification modes
    # params - none
    # returns - nothing
    @pytest.mark.skip(
        "depricate support of curie emulation for device register setting"
    )
    def test_setGetClassifcationMode(self):
        classificationBadMode1 = -2
        classificationBadMode2 = 7
        testClassifModeVals = [
            [self.engine.CLASSIF_MODE_KNN, self.engine.CLASSIF_MODE_KNN],
            [self.engine.CLASSIF_MODE_RBF, self.engine.CLASSIF_MODE_RBF],
            [self.engine.CLASSIF_MODE_KNN, self.engine.CLASSIF_MODE_KNN],
            [classificationBadMode1, self.engine.CLASSIF_MODE_RBF],
            [self.engine.CLASSIF_MODE_KNN, self.engine.CLASSIF_MODE_KNN],
            [classificationBadMode2, self.engine.CLASSIF_MODE_RBF],
            [self.engine.CLASSIF_MODE_KNN, self.engine.CLASSIF_MODE_KNN],
            [self.engine.CLASSIF_MODE_RBF, self.engine.CLASSIF_MODE_RBF],
            [self.engine.CLASSIF_MODE_KNN, self.engine.CLASSIF_MODE_KNN],
        ]
        for i in range(0, len(testClassifModeVals)):
            self.engine.set_classification_mode(testClassifModeVals[i][0])
            value = self.engine.get_classification_mode()
            assert value == testClassifModeVals[i][1]

    # test_setGetIFs - tests the setting of the min and max AIF values
    # params - none
    # returns - nothing
    @pytest.mark.skip(
        "depricate support of curie emulation for device register setting"
    )
    def test_setGetIFs(self):
        validMinOrMax1 = 5
        validMinOrMax2 = 199
        validMinOrMax3 = 0x2002
        minOrMaxToHigh = 0x4999
        testMinVals = [
            [validMinOrMax1, validMinOrMax1],
            [minOrMaxToHigh, self.engine.MAX_MIN_AIF],
            [0, self.engine.MIN_MIN_AIF],
            [self.engine.MIN_MIN_AIF - 1, self.engine.MIN_MIN_AIF],
            [self.engine.MIN_MIN_AIF, self.engine.MIN_MIN_AIF],
            [validMinOrMax3, validMinOrMax3],
            [self.engine.MIN_MIN_AIF + 1, self.engine.MIN_MIN_AIF + 1],
            [validMinOrMax2, validMinOrMax2],
            [self.engine.MAX_MIN_AIF - 1, self.engine.MAX_MIN_AIF - 1],
            [self.engine.MAX_MIN_AIF, self.engine.MAX_MIN_AIF],
            [self.engine.MIN_MAX_AIF, self.engine.MIN_MAX_AIF],
            [self.engine.MAX_MIN_AIF + 1, self.engine.MAX_MIN_AIF],
            [self.engine.MAX_MAX_AIF, self.engine.MAX_MIN_AIF],
        ]

        for i in range(0, len(testMinVals)):
            self.engine.set_min_aif(testMinVals[i][0])
            value = self.engine.get_min_aif()
            assert value == testMinVals[i][1]

        testMaxVals = [
            [validMinOrMax1, validMinOrMax1],
            [minOrMaxToHigh, self.engine.MAX_MAX_AIF],
            [0, self.engine.MIN_MAX_AIF],
            [self.engine.MIN_MIN_AIF - 1, self.engine.MIN_MAX_AIF],
            [self.engine.MIN_MAX_AIF, self.engine.MIN_MAX_AIF],
            [validMinOrMax3, validMinOrMax3],
            [self.engine.MIN_MAX_AIF + 1, self.engine.MIN_MAX_AIF + 1],
            [validMinOrMax2, validMinOrMax2],
            [self.engine.MAX_MAX_AIF - 1, self.engine.MAX_MAX_AIF - 1],
            [self.engine.MAX_MAX_AIF, self.engine.MAX_MAX_AIF],
            [self.engine.MAX_MIN_AIF, self.engine.MAX_MIN_AIF],
            [self.engine.MAX_MAX_AIF + 1, self.engine.MAX_MAX_AIF],
            [self.engine.MIN_MIN_AIF, self.engine.MIN_MAX_AIF],
        ]
        for i in range(0, len(testMaxVals)):
            self.engine.set_max_aif(testMaxVals[i][0])
            value = self.engine.get_max_aif()
            assert value == testMaxVals[i][1]

    # test_write_neurons - tests that writing two neurons can be read back without error
    # params - none
    # returns - nothing
    def test_write_neurons(self, num_neurons=255):
        TEST_CAT_1 = 1
        neurons = []

        for i in range(num_neurons):
            neurons.append(
                {
                    "Category": TEST_CAT_1,
                    "Identifier": i,
                    "Vector": [
                        108,
                        105,
                        103,
                        100,
                        96,
                        91,
                        89,
                        87,
                        83,
                        81,
                        80,
                        80,
                        80,
                        81,
                        81,
                        82,
                        95,
                        123,
                        97,
                        87,
                        77,
                        66,
                        61,
                        66,
                        70,
                        81,
                        95,
                        100,
                        104,
                        113,
                        122,
                        126,
                        129,
                        133,
                        136,
                        138,
                        139,
                        141,
                        142,
                        143,
                        143,
                        143,
                        143,
                        143,
                        143,
                        145,
                        148,
                        150,
                        149,
                        148,
                        142,
                        135,
                        133,
                        131,
                        128,
                        127,
                        127,
                        128,
                        130,
                        134,
                        136,
                        138,
                        142,
                        146,
                        147,
                        148,
                        148,
                        147,
                        146,
                        146,
                        145,
                        146,
                        147,
                        147,
                        149,
                        153,
                        152,
                        152,
                        148,
                        143,
                        139,
                        141,
                        143,
                        148,
                        153,
                        156,
                        160,
                        166,
                        170,
                        170,
                        170,
                        167,
                        162,
                        160,
                        157,
                        152,
                        147,
                        144,
                        142,
                        139,
                        135,
                        134,
                        133,
                        131,
                        128,
                        127,
                        126,
                        124,
                        123,
                        122,
                        122,
                        123,
                        124,
                        125,
                        125,
                        126,
                        125,
                        123,
                        122,
                        121,
                        118,
                        115,
                        113,
                        111,
                        108,
                        0,
                        0,
                        0,
                    ],
                    "AIF": 1697,
                }
            )

        self.engine.load_model(neurons)
        assert len(neurons) == len(self.engine.dump_model())
        results = self.engine.dump_model()
        for i, neuron in enumerate(results):
            assert neuron["Vector"] == neurons[i]["Vector"]
            assert neuron["Category"] == neurons[i]["Category"]
            assert neuron["AIF"] == neurons[i]["AIF"]

    def test_write_neurons_large(self):
        self.engine.initialize_model(2056, 128)
        self.test_write_neurons(num_neurons=1)
        self.test_write_neurons(num_neurons=2)
        self.test_write_neurons(num_neurons=128)
        self.test_write_neurons(num_neurons=256)
        self.test_write_neurons(num_neurons=512)
        self.test_write_neurons(num_neurons=1024)
        self.test_write_neurons(num_neurons=2056)

    @pytest.mark.skip("Not currently supported")
    def test_degenerated_neuron_response(self):
        # Test that the control function works
        prevset = self.engine.set_degen_reporting(1)
        assert prevset == 0
        prevset = self.engine.set_degen_reporting(0)
        assert prevset == 1

        # Learn the local vectors with RBF, should produce two neurons
        test_context = 1
        test_vectors = [
            {
                "Category": 1,
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Vector": [1, 1],
                "DesiredResponses": 1,
            },
            {
                "Category": 1,
                "CategoryVector": [],
                "NIDVector": [],
                "DistanceVector": [],
                "Vector": [1, 2],
                "DesiredResponses": 1,
            },
        ]

        # init the neuron network
        self.engine.initialize_model(128, 128)
        self.engine.set_classification_mode(self.engine.CLASSIF_MODE_RBF)
        self.engine.set_min_aif(5)
        self.engine.set_max_aif(10)
        self.engine.learn_vector(test_context, test_vectors[0]["Vector"], 1)
        self.engine.learn_vector(test_context, test_vectors[1]["Vector"], 2)

        # check that both were learned seperately
        assert 2 == self.engine.get_neuron_count()

        # recognize a neuron and check that the 'degen' bit is set
        prevset = self.engine.set_degen_reporting(1)
        self.engine.recognize_vector(
            test_context,
            test_vectors[0]["Vector"],
            test_vectors[0]["DesiredResponses"],
            test_vectors[0]["DistanceVector"],
            test_vectors[0]["CategoryVector"],
            test_vectors[0]["NIDVector"],
        )
        assert test_vectors[0]["CategoryVector"][0] > 32767

        # Now test again with degenerated reporting disabled
        self.engine.set_degen_reporting(0)

        # recognize a neuron and check that the 'degen' bit is not set
        self.engine.recognize_vector(
            test_context,
            test_vectors[0]["Vector"],
            test_vectors[0]["DesiredResponses"],
            test_vectors[0]["DistanceVector"],
            test_vectors[0]["CategoryVector"],
            test_vectors[0]["NIDVector"],
        )
        assert test_vectors[0]["CategoryVector"][0] <= 32767

    @pytest.mark.django_db
    def test_compute_cost(self, loaddata):
        loaddata("test_classifier_costs")
        self.engine = PME()
        num_neurons = len(self.vectors)
        num_features = len(self.vectors[0]["Vector"])
        total_flash_size = 124 + (num_neurons * num_features) + (15 * num_neurons)
        expected_costs = {
            "flash": total_flash_size,
            "sram": 120,
            "stack": 0,
            "cycle_count": 1100 * num_features,
        }
        cost = self.engine.compute_cost(self.vectors)
        assert type(cost) == type(dict())
        for key in expected_costs.keys():
            assert cost[key] == expected_costs[key]
