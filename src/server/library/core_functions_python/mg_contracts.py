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

VALIDATION_METHODS = {
    "name": "validation_methods",
    "type": "list",
    "element_type": "str",
    "handle_by_set": True,
    "options": [
        {"name": "Stratified K-Fold Cross-Validation"},
        {"name": "Leave-One-Subject-Out"},
        {"name": "Stratified Shuffle Split"},
    ],
}


def train_tinn(
    input_data, label_column, ignore_columns, classifiers, validation_methods
):
    """
    Trains a Neural Network classifier with 1 hidden layer

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels

    Returns:
        a set of models

    """

    return None


train_tinn_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "NN 1-layer"}],
        },
        VALIDATION_METHODS,
        {"name": "iterations", "type": "int", "handle_by_set": False, "default": 100},
        {
            "name": "learning_rate",
            "type": "int",
            "handle_by_set": False,
            "default": 0.01,
        },
    ],
    "output_contract": [],
}


def tinn(num_hidden_layer, online_learning):
    """
    Neural Network classifier with a single hidden layer

    Args:
        num_hidden_layer (int): the number of hidden neurons in the hidden layer of the NN
        online_learning (bool): To generate the code for online learning on the edge device
            this takes up additional SRAM, but can be used to tune the model at the edge when ground truth
            is available.

    """

    return None


tinn_contracts = {
    "input_contract": [
        {"name": "num_hidden_layer", "type": "int", "default": 32},
        {"name": "online_learning", "type": "bool", "default": False},
    ],
    "output_contract": [],
}


def train_nlnn(
    input_data, label_column, ignore_columns, classifiers, validation_methods
):
    """
    Trains a Neural Network classifier with 1 hidden layer

    Args:
        input_data (DataFrame): input feature vectors with a label column
        label_column (str): the name of the column in input_data containing labels

    Returns:
        a set of models

    """

    return None


train_nlnn_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame", "handle_by_set": True},
        {"name": "label_column", "type": "str", "handle_by_set": True},
        {
            "name": "ignore_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
        },
        {
            "name": "classifiers",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [{"name": "NN n-layer"}],
        },
        {
            "name": "validation_methods",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "options": [
                {"name": "Stratified K-Fold Cross-Validation"},
                {"name": "Leave-One-Subject-Out"},
                {"name": "Stratified Shuffle Split"},
            ],
        },
        {"name": "iterations", "type": "int", "handle_by_set": False, "default": 100},
        {
            "name": "learning_rate",
            "type": "int",
            "handle_by_set": False,
            "default": 0.01,
        },
        {"name": "batch_size", "type": "int", "handle_by_set": False, "default": 10},
    ],
    "output_contract": [],
}


def nlnn(num_hidden_layer, online_learning):
    """
    Neural Network classifier with a single hidden layer

    Args:
        num_hidden_layer (int): the number of hidden neurons in the hidden layer of the NN
        online_learning (bool): To generate the code for online learning on the edge device
            this takes up additional SRAM, but can be used to tune the model at the edge when ground truth
            is available.

    """

    return None


nlnn_contracts = {
    "input_contract": [{"name": "num_hidden_layer", "type": "int", "default": 32}],
    "output_contract": [],
}
