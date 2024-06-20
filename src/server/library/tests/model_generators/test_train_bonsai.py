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
import logging
import os
from uuid import uuid4

import numpy as np
import pandas as pd
import pytest
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import get_model_generator
from library.model_generators.train_bonsai import (
    flatten_matrix,
    flatten_transpose_multi_matrix,
)
from library.model_validation.validation_methods import get_validation_method

assert_almost_equal = np.testing.assert_almost_equal


logger = logging.getLogger(__name__)


@pytest.mark.django_db
@pytest.mark.skip("takes to long")
def test_train_bonsai(loaddata):
    loaddata("test_classifier_costs")
    train_set = pd.read_csv(os.path.join("engine", "tests", "data", "Iris_train.csv"))

    train_set["label"] += 1

    test_set = pd.read_csv(os.path.join("engine", "tests", "data", "Iris_test.csv"))
    test_set["label"] += 1

    data = pd.concat([train_set, test_set], ignore_index=True)

    config = {
        "classifier": "Bonsai",
        "validation_method": "Recall",
        "optimizer": "Bonsai Tree Optimizer",
        "label_column": "label",
        "epochs": 1,
        "tree_depth": 2,
    }

    validation_method = get_validation_method(config, data)
    classifier = get_classifier(config)
    model_generator = get_model_generator(
        config,
        classifier=classifier,
        validation_method=validation_method,
        pipeline_id=str(uuid4()),
    )

    model_generator.run()

    results = model_generator.get_results()

    assert results["models"]["Fold 0"]["metrics"]["validation"]["accuracy"]


def test_flatten_matrix():
    input = np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]])

    result = flatten_matrix(input)

    expected_result = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]

    assert result == expected_result


def test_flatten_transpose_multi_matrix():

    input = np.array(
        [
            [11, 12, 13, 14],
            [21, 22, 23, 24],
            [31, 32, 33, 34],
            [41, 42, 43, 44],
            [51, 52, 53, 54],
            [61, 62, 63, 64],
        ]
    )

    result = flatten_transpose_multi_matrix(input, 2, 3)

    expected_result = [
        11,
        21,
        31,
        12,
        22,
        32,
        13,
        23,
        33,
        14,
        24,
        34,
        41,
        51,
        61,
        42,
        52,
        62,
        43,
        53,
        63,
        44,
        54,
        64,
    ]

    assert result == expected_result
