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

# coding=utf-8

from library.classifiers.pme import PME

MAX_AIF = 1000


def print_results(results, desired_responses=1):
    print("category", results[0].category)
    print("distance", results[0].distance)
    print("nid", results[0].pattern_id)


class TestPME:
    def test_learn_and_recognize_rbf_l1(self):
        pme = PME()

        pme.set_max_aif(MAX_AIF)

        pme.initialize_model(100, 2)

        pme._learn_vector(0, [0, 0], 1)
        result = pme.dump_model()
        assert result == [
            {"Vector": [0, 0], "Category": 1, "AIF": MAX_AIF, "Identifier": 0}
        ]

        pme._learn_vector(0, [50, 50], 4)
        result = pme.dump_model()

        assert result == [
            {"Vector": [0, 0], "Category": 1, "AIF": 100, "Identifier": 0},
            {"Vector": [50, 50], "Category": 4, "AIF": MAX_AIF, "Identifier": 1},
        ]

        pme._learn_vector(0, [100, 100], 3)
        result = pme.dump_model()
        assert result == [
            {"Vector": [0, 0], "Category": 1, "AIF": 100, "Identifier": 0},
            {"Vector": [50, 50], "Category": 4, "AIF": 100, "Identifier": 1},
            {"Vector": [100, 100], "Category": 3, "AIF": MAX_AIF, "Identifier": 2},
        ]

        pme._learn_vector(0, [25, 25], 4)
        result = pme.dump_model()

        assert result == [
            {"Vector": [0, 0], "Category": 1, "AIF": 50, "Identifier": 0},
            {"Vector": [50, 50], "Category": 4, "AIF": 50, "Identifier": 1},
            {"Vector": [100, 100], "Category": 3, "AIF": 150, "Identifier": 2},
            {"Vector": [25, 25], "Category": 4, "AIF": MAX_AIF, "Identifier": 3},
        ]

        print(result)

        vector = {"Vector": [250, 250], "Category": 3}

        results = pme._recognize_vector(0, vector["Vector"], 1)

        print_results(results)
        assert results[0].category == 4
        assert results[0].distance == 450
        assert results[0].pattern_id == 3

        vector = {"Vector": [100, 100], "Category": 3}

        results = pme._recognize_vector(0, vector["Vector"], 1)

        print_results(results)
        assert results[0].category == 3
        assert results[0].distance == 0
        assert results[0].pattern_id == 2

        vector = {"Vector": [0, 0], "Category": 1}

        results = pme._recognize_vector(0, vector["Vector"], 1)

        print_results(results)
        assert results[0].category == 1
        assert results[0].distance == 0
        assert results[0].pattern_id == 0

        vector = {"Vector": [50, 50], "Category": 4}

        print_results(results)
        assert results[0].category == 1
        assert results[0].distance == 0
        assert results[0].pattern_id == 0
