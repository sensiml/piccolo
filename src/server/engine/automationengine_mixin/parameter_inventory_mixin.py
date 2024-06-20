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

import logging


from engine.automationengine_mixin.parameter_optimizer_utils import get_inventory
from engine.automationengine_mixin.automationengine_exception import ValidationError


logger = logging.getLogger(__name__)


class ParameterInventoryMixin:
    def __init__(self):
        pass

    def get_the_parameter_inventory(self, feature_data=None):
        # Get the parameter inventory
        inventory = get_inventory()

        if self.param_allow_unknown:
            inventory = update_inventory_to_allow_unknown(inventory)

        if self.set_training_algorithm:
            inventory = update_training_algorithm(
                inventory, list(self.set_training_algorithm.keys())
            )

            inventory = update_training_algorithm_parameters(
                inventory, self.set_training_algorithm
            )

        # flat model with more then 2 class
        if (feature_data is not None) and (len(feature_data[self.label].unique()) > 2):
            inventory = remove_binary_optimizers_and_dependens(inventory)

        return inventory


def update_inventory_to_allow_unknown(inventory):
    # Remove all classifiers and optimizers except RBF related ones
    drop_list = inventory[inventory.allow_unknown == False].index.tolist()
    inventory = inventory.drop(drop_list).reset_index(drop=True)
    index = inventory[
        (inventory.function_name == "PME")
        & (inventory.variable_name == "classification_mode")
    ].index
    temp_list = inventory.loc[index, "variable_values"].values
    temp_list[0] = ["RBF"]
    inventory.loc[index, "variable_values"] = temp_list
    return inventory


def remove_binary_optimizers_and_dependens(inventory):
    drop_list = inventory[inventory.binary_classifiers == True].index.tolist()
    return inventory.drop(drop_list).reset_index(drop=True)


def validate_existence_of_algorithm_in_inventory(algorithm_list, inventory):
    # check the existence of the algorithm
    for algorithm in algorithm_list:
        if algorithm not in inventory.function_name.tolist():
            raise ValidationError(
                "ERROR: Please check the 'set_training_algorithm' parameters. '"
                + algorithm
                + "' algorithm is not found in AutoML inventory."
            )


def update_training_algorithm(inventory, set_training_algorithm):

    # check the existence of the algorithm
    validate_existence_of_algorithm_in_inventory(set_training_algorithm, inventory)

    # remove the optimizers and classifiers which are not in the list
    classifiers_optimizers_group = inventory[
        inventory.function_name.isin(set_training_algorithm)
    ].classifiers_optimizers_group.unique().tolist() + [0]
    new_inventory = inventory[
        inventory.classifiers_optimizers_group.isin(classifiers_optimizers_group)
    ]

    # remove the optimizer which use the same classifier but not in the list
    # i.e: Hierarchical Clustering with Neuron Optimization and RBF with Neuron Allocation Optimization
    optimizers = (
        new_inventory[new_inventory.pipeline_key == "optimizers"]
        .function_name.unique()
        .tolist()
    )
    optimizers_drop = list(set(optimizers) - set(set_training_algorithm))

    drop_index = new_inventory[
        new_inventory.function_name.isin(optimizers_drop)
    ].index.tolist()
    new_inventory = new_inventory.drop(drop_index).reset_index(drop=True)

    return new_inventory


def validate_existence_of_variable_in_function(inventory, algorithm, key):
    if (
        key
        not in inventory[inventory.function_name == algorithm].variable_name.to_list()
    ):
        raise ValidationError(
            "ERROR: Please check the 'set_training_algorithm' parameters. '"
            + key
            + "' variable is not member of '"
            + algorithm
            + "' algorithm."
        )


def update_training_algorithm_parameters(inventory, set_training_algorithm):

    drop_list = []
    for algorithm in set_training_algorithm.keys():
        for key in set_training_algorithm[algorithm].keys():

            validate_existence_of_variable_in_function(inventory, algorithm, key)

            item_index = inventory[
                (inventory.function_name == algorithm)
                & (inventory.variable_name == key)
            ].index.to_list()
            drop_list.extend(item_index)

            temp = list(inventory.loc[item_index].values[0])
            variable_values_index = inventory.columns.to_list().index("variable_values")

            # update variable values
            temp[variable_values_index] = set_training_algorithm[algorithm][key]
            inventory.loc[len(inventory)] = temp

    return inventory.drop(index=drop_list).reset_index(drop=True)
