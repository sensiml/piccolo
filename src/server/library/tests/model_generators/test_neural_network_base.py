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

import numpy as np
import pandas as pd
import pytest
from library.model_generators.neural_network_training_utils import (
    features_to_tensor_convert,
    get_one_hot,
)
from pandas import DataFrame

logger = logging.getLogger(__name__)

# fmt: off

@pytest.fixture
def data():
    train_data = DataFrame(
        [
            [80, 6, 1, 3, 9, 241, 253, 251, 253, 253, 253, 252, 2, 254, 253, 252, 252, 250, 245, 1, 2, 2, 1, 1, 1, 1, 1],
            [144, 3, 2, 4, 7, 248, 251, 252, 253, 252, 253, 252, 4, 253, 253, 253, 251, 251, 221, 2, 1, 1, 0, 0, 1, 2, 1],
            [67, 248, 252, 251, 247, 17, 4, 1, 2, 2, 1, 1, 252, 1, 1, 0, 3, 7, 31, 253, 254, 253, 253, 254, 253, 253, 2],
            [84, 248, 251, 250, 242, 13, 4, 0, 1, 0, 0, 1, 250, 0, 1, 2, 2, 5, 33, 253, 253, 253, 253, 253, 253, 253, 2],
        ]
    )

    train_data = train_data.T
    train_data.columns = ["gen_1", "gen_2", "gen_3", "gen_4"]
    labels = [1] * 13 + [2] * 14
    train_data["Label"] = labels

    return train_data


def test_get_one_hot():
    targets=np.array([1,2,3,4,1,2,3,4])
    nb_classes=5

    get_one_hot(targets, nb_classes)


def test_features_to_tensors():
    train_data = pd.read_csv(os.path.join(os.path.dirname(__file__),'data', 'features_to_tensors.csv'))
    class_map = {1: 1, 2: 2}

    x_values, y_values = features_to_tensor_convert(train_data, class_map)


    expected_y_values = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 0.0]]
    expected_x_values = [[251, 253, 253], [252, 253, 254], [2, 3, 2], [9, 3, 1], [6, 7, 1], [251, 252, 254], [251, 252, 253], [4, 1, 1], [252, 253, 253], [249, 252, 255], [8, 3, 2], [1, 4, 2], [11, 4, 1], [252, 255, 252], [8, 4, 0], [8, 0, 2], [8, 4, 2], [7, 5, 2], [252, 253, 253], [8, 2, 1], [4, 4, 1], [248, 251, 254], [247, 251, 252], [255, 251, 254], [252, 253, 254], [3, 0, 1], [7, 2, 2], [247, 252, 252], [249, 251, 254], [252, 253, 253], [3, 5, 0], [250, 252, 255]]
    assert expected_y_values == y_values.tolist()
    assert expected_x_values == x_values.tolist()
