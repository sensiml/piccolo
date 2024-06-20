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

import copy
import json
import logging
import random

import numpy as np
import pandas as pd
from django.forms.models import model_to_dict
from engine.base.contractenforcer import ContractEnforcer
from library.models import ParameterInventory, Transform
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))

model_stat_list_tuple = [
    "accuracy",
    "f1_score",
    "sensitivity",
    "precision",
    "positive_predictive_rate",
    "specificity",
    "features",
    "classifiers_sram",
]


# stat list in fitness_values(dataframe)
model_stat_list = [
    "accuracy",
    "f1_score",
    "sensitivity",
    "positive_predictive_rate",
    "features",
    "classifiers_sram",
]

# cost variables
cost_list = ["flash", "sram", "stack", "latency"]


fitness_values_temp_columns = model_stat_list + cost_list


def get_inventory():
    inventory = ParameterInventory.objects.all()

    inventory_dict = [model_to_dict(v) for v in inventory]

    for item in inventory_dict:
        item["variable_values"] = (
            None
            if item["variable_values"] is None
            else json.loads(item["variable_values"])
        )

    return pd.DataFrame(inventory_dict)


def get_libraries(step):
    if step["type"] in ["transform", "segmenter", "sampler"]:
        return ["transform"]
    elif step["type"] == "selectorset":
        return ["selectorset"]
    elif step["type"] == "tvo":
        return ["optimizers", "classifiers", "validation_methods"]
    else:
        return []


def get_step_id(step):
    if step["type"] in ["segmenter", "transform", "sampler"]:
        return step["name"]
    else:
        return step["type"]


def define_auto_params_weight_parm(fitness_preferences):
    weight_and_scale = pd.DataFrame([], columns=["weight", "min", "max", "rev"])
    weight_and_scale.loc[:] = 0
    weight_and_scale.loc["accuracy"] = [
        fitness_preferences.get("accuracy", 1),
        0,
        100,
        0,
    ]
    weight_and_scale.loc["f1_score"] = [
        fitness_preferences.get("f1_score", 0),
        0,
        100,
        0,
    ]
    weight_and_scale.loc["sensitivity"] = [
        fitness_preferences.get("sensitivity", 0.7),
        0,
        100,
        0,
    ]
    weight_and_scale.loc["positive_predictive_rate"] = [
        fitness_preferences.get("positive_predictive_rate", 0),
        0,
        100,
        0,
    ]
    weight_and_scale.loc["features"] = [
        fitness_preferences.get("features", 0.2),
        1,
        128,
        1,
    ]
    weight_and_scale.loc["classifiers_sram"] = [
        fitness_preferences.get("classifiers_sram", 0.3),
        1,
        32768,
        1,
    ]
    weight_and_scale.loc["flash"] = [fitness_preferences.get("flash", 0), 1, 40000, 1]
    weight_and_scale.loc["stack"] = [fitness_preferences.get("stack", 0), 1, 350, 1]
    weight_and_scale.loc["latency"] = [
        fitness_preferences.get("latency", 0),
        1,
        1e8,
        1,
    ]  # TODO: check this
    weight_and_scale.loc["sram"] = [fitness_preferences.get("sram", 0), 1, 4685, 1]

    return weight_and_scale


def recreation(
    new_generation,
    inventory,
    recreation_list,
    library_list,
    search_pipeline,
    validation_method,
    add_unsupervised_selectors=False,
):
    # this function creates new population\s for defined index (mutation recreation_list).
    # It uses the same logic with creating initial population
    if recreation_list:
        for list_index in recreation_list:
            for step in search_pipeline:
                new_generation.at[list_index, get_step_id(step)] = copy.deepcopy(step)

                # Recreation of feature selector
                if step["type"] == "selectorset" and "selectorset" in library_list:
                    new_generation.loc[list_index, "selectorset"][
                        "set"
                    ] = define_parameters(
                        sandbox_variable="selectorset",
                        inventory=inventory,
                        add_unsupervised_selectors=add_unsupervised_selectors,
                    )
                # Recreation of tvo steps
                elif step["type"] == "tvo":
                    if "optimizers" in library_list:
                        new_generation.loc[list_index, "tvo"][
                            "optimizers"
                        ] = define_parameters(
                            sandbox_variable="optimizers",
                            inventory=inventory,
                        )

                    optimizer = new_generation.loc[list_index, "tvo"]["optimizers"][0][
                        "name"
                    ]
                    if "classifiers" in library_list:
                        new_generation.loc[list_index, "tvo"][
                            "classifiers"
                        ] = define_parameters(
                            sandbox_variable="classifiers",
                            optimizer=optimizer,
                            inventory=inventory,
                        )

                    if "validation_methods" in library_list:
                        new_generation.loc[list_index, "tvo"][
                            "validation_methods"
                        ] = read_validation_algorithms(validation_method)

                """
                # TODO: transforms don't work yet
                elif step["type"] == "transform" and "transform" in library_list:

                    new_generation.loc[list_index, step["name"]] = [
                        prepare_random_population_steps_transform(
                            step,
                            inventory,
                            copy.deepcopy(
                                new_generation[step["name"]][0]["inputs"]["input_data"]
                            ),
                            new_generation.loc[list_index, "outputs"][1],
                            list_index,
                        )
                    ]
                """

    return new_generation


def create_classifiers_index_list(fitness_values, cross_over_survivors_list):
    # it creates index list for each classification group
    classifiers_list = list(
        np.unique([i["name"] for i in fitness_values["classifiers"]])
    )
    classifiers_index_list = []
    for c in classifiers_list:
        c_temp = []
        for i in fitness_values.loc[cross_over_survivors_list, "classifiers"].index:
            if c == fitness_values.loc[i, "classifiers"]["name"]:
                c_temp.append(i)

        classifiers_index_list.append(c_temp)

    return classifiers_index_list


def create_cross_over_list(classifiers_index_list, cross_over_survivors_list):
    # create cross_over_list from correct classifiers_index_list
    cross_over_list = random.sample(cross_over_survivors_list, 1)
    for i in classifiers_index_list:
        if cross_over_list[0] in i:
            target_list = list(set(i) - set(cross_over_list))
            if len(target_list) > 0:
                cross_over_list.extend(random.sample(target_list, 1))
            else:
                cross_over_list.extend(cross_over_list)

            break

    return cross_over_list


def cross_over(
    fitness_values,
    weight_and_scale,
    library_list,
    mutation_list,
    recreation_list,
    top_threshold,
):
    # This function takes two survivors and create a new population by using cross_over method.
    # define the index numbers for the results of cross over

    cross_over_next_gen_list = list(
        set(fitness_values.index[top_threshold:]) - set(mutation_list + recreation_list)
    )
    # survivors will be used for cross over process
    cross_over_survivors_list = fitness_values.index[:top_threshold].tolist()

    classifiers_index_list = create_classifiers_index_list(
        fitness_values, cross_over_survivors_list
    )

    if len(cross_over_survivors_list) > 1:
        for list_index in cross_over_next_gen_list:
            # pick 2 survivors for new item
            cross_over_list = create_cross_over_list(
                classifiers_index_list, cross_over_survivors_list
            )

            for library in library_list:
                fitness_values.at[list_index, library] = fitness_values.loc[
                    cross_over_list[0], library
                ]

            fitness_values.loc[
                list_index, weight_and_scale.index.tolist() + ["fitness"]
            ] = 0

            for lib in library_list:
                # for each lib item randomly pick a winner and update the template with winner
                winner = random.choice(cross_over_list)
                fitness_values.at[list_index, lib] = copy.deepcopy(
                    fitness_values.loc[winner, lib]
                )

    return fitness_values


def fix_extremes(value, allowed_values):
    if value > max(allowed_values):
        return max(allowed_values)
    elif value < min(allowed_values):
        return min(allowed_values)
    else:
        return value


def variables_name_list_for_mutation(library, new_generation, list_index):
    # this is sub-function of mutation, pick random variable names which will be mutated
    if library == "transform":
        algorithm = new_generation.loc[list_index, library]["name"]
        variables_name_list = []
    elif library == "selectorset":
        algorithm = new_generation.loc[list_index, library]["set"][0]["function_name"]
        keys = new_generation.loc[list_index, library]["set"][0]["inputs"].keys()
        if len(keys) > 2:
            variables_name_list = random.sample(keys, 2)
        else:
            variables_name_list = keys
    elif library == "validation_methods":
        algorithm = new_generation.loc[list_index, library]["name"]
        variables_name_list = []
    else:
        algorithm = new_generation.loc[list_index, library]["name"]
        variables_name_list = [
            x
            for x in new_generation.loc[list_index, library]["inputs"].keys()
            if x not in "class_map"
        ]

        if len(variables_name_list) > 2:
            variables_name_list = random.sample(variables_name_list, 2)

    return variables_name_list, algorithm


def is_set(step):
    if step.get("set"):
        return True
    return False


def get_variable_type(inventory, algorithm, variable_name):
    return inventory[
        (inventory["function_name"] == algorithm)
        & (inventory["variable_name"] == variable_name)
    ]["variable_type"].tolist()[0]


def get_variable_list(inventory, algorithm, variable_name):
    return inventory[
        (inventory["function_name"] == algorithm)
        & (inventory["variable_name"] == variable_name)
    ]["variable_values"].tolist()[0]


def apply_mutation(
    library, variables_name_list, algorithm, inventory, new_generation, list_index
):
    # if value is numeric, multiply it with defined range 0.5 ~ 2
    # if value is string, randomly select a parameter from inventory
    for variable_name in variables_name_list:
        if variable_name not in inventory["variable_name"].values:
            continue

        variable_type = get_variable_type(inventory, algorithm, variable_name)

        mutated_value = None

        variable_list = get_variable_list(inventory, algorithm, variable_name)

        if variable_type == None:
            continue
        elif variable_type == "str":
            mutated_value = random.choice(variable_list).strip()
        elif variable_type in ["int", "float"]:
            if is_set(new_generation.loc[list_index, library]):
                mutated_value = float(
                    new_generation.loc[list_index, library]["set"][-1]["inputs"][
                        variable_name
                    ]
                )
            else:
                mutated_value = float(
                    new_generation.loc[list_index, library]["inputs"][variable_name]
                )

            mutated_value *= random.choice(
                [0.5, 0.6, 0.7, 0.8, 0.9, 1.2, 1.4, 1.6, 1.8, 2]
            )

            mutated_value = fix_extremes(
                mutated_value, [float(x) for x in variable_list]
            )

            if variable_type == "int":
                mutated_value = int(mutated_value)
            else:
                mutated_value = float(mutated_value)

        else:
            raise Exception("Invalid variable type for mutation.")

        if is_set(new_generation.loc[list_index, library]):
            new_generation.loc[list_index, library]["set"][-1]["inputs"][
                variable_name
            ] = mutated_value
        else:
            new_generation.loc[list_index, library]["inputs"][
                variable_name
            ] = mutated_value

    return new_generation


def mutation(new_generation, inventory, mutation_list_orj, mutation_list, library_list):
    # This function apply mutation to mutation_list based on mutation_list_orj
    if mutation_list:
        # create template for mutation lists based on mutation_list_orj
        for list_index in range(len(mutation_list)):
            for library in library_list:
                new_generation.at[mutation_list[list_index], library] = copy.deepcopy(
                    new_generation.loc[mutation_list_orj[list_index], library]
                )

        for list_index in mutation_list:
            for library in library_list:
                if new_generation.loc[list_index, library]["inputs"] != {}:
                    # pick variable names that will be mutated
                    variables_name_list, algorithm = variables_name_list_for_mutation(
                        library, new_generation, list_index
                    )
                    # apply mutation for "variables_name_list" in the "algorithm"
                    new_generation = apply_mutation(
                        library,
                        variables_name_list,
                        algorithm,
                        inventory,
                        new_generation,
                        list_index,
                    )

    return new_generation


def normalize_classifiers_sram(val, min_val):
    """
    This is a spatial normalization for classifier sram value.
    It return score 0~1 if value is less then targetted classifier sram value.
    Therefore, in given range it naturalize the weight of sram. If classifier
    sram is greater than targetted sram, val is linearly normalized.
    """
    if isinstance(val, pd.Series):
        val = val.values[0]

    if (val - min_val) <= 1:
        val = 1 - (min_val - val) / min_val
    else:
        val = val - min_val

    return val


def comp_fitness_score_indv(weight_and_scale, scores):
    # Normalize each fitness value based weight_and_scale
    fitness_score_list = []
    for stat in weight_and_scale.index:
        weight = weight_and_scale.loc[stat, "weight"]
        max_val = weight_and_scale.loc[stat, "max"]
        min_val = weight_and_scale.loc[stat, "min"]
        val = scores[stat]

        if weight_and_scale.loc[stat, "rev"]:
            if stat == "classifiers_sram":
                val = normalize_classifiers_sram(val, min_val)

            fitness_score_list.append(weight * (1 - (val / float(max_val - min_val))))
        else:
            fitness_score_list.append(weight * val / float(max_val - min_val))

    return sum(fitness_score_list)


def read_metrics_cost(stat, model, classifier):
    if stat == "features":
        score = model["metrics"]["validation"]["FeaturesPerVector"]
    elif stat == "classifiers_sram":
        score = model["model_size"]
    else:
        score = model["metrics"]["validation"][stat]

    if score is None:
        score = 0

    if isinstance(score, dict):
        score = score.get("average")

    return score


def compute_avg_metric_scores(models, classifier):
    score_dict = {x: [] for x in model_stat_list_tuple}

    for _, model in models.items():
        for stat in model_stat_list_tuple:
            score_dict[stat].append(read_metrics_cost(stat, model, classifier))

    for stat in model_stat_list_tuple:
        score_dict[stat + "_std"] = np.std(score_dict[stat])
        score_dict[stat] = np.mean(score_dict[stat])

    return score_dict


def compute_fitness_values_for_population(fitness_values, models, weight_and_scale):
    classifier = fitness_values["classifiers"]["name"]
    cost_dict = {cost: fitness_values[cost] for cost in cost_list}
    score_dict = compute_avg_metric_scores(models, classifier)
    score_dict["AvgConfusionMatrix"] = compute_average_confusion_matrix(models)
    score_dict["AllConfusionMatrix"] = combine_confusion_matrices(models)
    score_dict["TrainingMetrics"] = combine_training_matrics(models)
    cost_dict.update(score_dict)
    score_dict["fitness"] = comp_fitness_score_indv(weight_and_scale, cost_dict)

    return score_dict


def compute_average_confusion_matrix(models):
    initial_key = list(models.keys())[0]
    number_folds = len(list(models.keys()))

    confusion_matrix_average = (
        pd.DataFrame(models[initial_key]["metrics"]["validation"]["ConfusionMatrix"])
        * 0
    )

    for fold in models.keys():
        confusion_matrix_average += pd.DataFrame(
            models[fold]["metrics"]["validation"]["ConfusionMatrix"]
        )

    return (confusion_matrix_average / number_folds).to_dict()


def combine_confusion_matrices(models):
    confusion_matrix_metrics = {}

    for fold in models.keys():
        confusion_matrix_metrics[fold] = {}
        confusion_matrix_metrics[fold]["validation"] = models[fold]["metrics"][
            "validation"
        ]["ConfusionMatrix"]
        confusion_matrix_metrics[fold]["train"] = models[fold]["metrics"]["train"][
            "ConfusionMatrix"
        ]

    return confusion_matrix_metrics


def combine_training_matrics(models):
    training_metrics = {}

    for fold in models.keys():
        training_metrics[fold] = models[fold]["training_metrics"]

    return training_metrics


def assign_fitness_values(
    population_models, fitness_values, weight_and_scale, reset_index=True
):
    fitness_values_iteration = []

    for population_index in fitness_values.index:
        tmp_fitness_score = compute_fitness_values_for_population(
            fitness_values.loc[population_index],
            population_models[population_index]["model_stats"]["models"],
            weight_and_scale,
        )

        fitness_values_iteration.append(tmp_fitness_score)

    fitness_value_scores = pd.DataFrame(fitness_values_iteration)

    fitness_values = pd.concat([fitness_values, fitness_value_scores], axis=1)

    if reset_index:
        return fitness_values.sort_values(by="fitness", ascending=False).reset_index(
            drop=True
        )
    else:
        return fitness_values


def read_validation_algorithms(validation_method):
    if isinstance(validation_method, list):
        validation_method = validation_method[0]

    if isinstance(validation_method, str):
        if validation_method == "Recall":
            return [{"inputs": {}, "name": "Recall"}]
        else:
            return [
                {
                    "inputs": {
                        "number_of_folds": 3,
                        "test_size": 0.0,
                        "validation_size": 0.2,
                    },
                    "name": "Stratified Shuffle Split",
                }
            ]

    elif isinstance(validation_method, dict):
        transform = Transform.objects.get(name=validation_method["name"])

        # webapp can't send 0 as a float so we have to convert it here
        if validation_method["inputs"].get("test_size", None) is not None:
            validation_method["inputs"]["test_size"] = float(
                validation_method["inputs"]["test_size"]
            )

        contract_enforcer = ContractEnforcer(
            validation_method, transform.input_contract, transform.name
        )

        contract_enforcer.enforce()

        return [contract_enforcer._validated_step]


def read_classifiers_algorithms(optimizer, inventory):
    group_list = inventory[
        inventory.function_name == optimizer
    ].classifiers_optimizers_group.unique()
    classifiers_list = (
        inventory[
            (inventory.pipeline_key == "classifiers")
            & (inventory.classifiers_optimizers_group.isin(group_list))
        ]
        .function_name.unique()
        .tolist()
    )

    return classifiers_list


def read_algorithms(sandbox_variable, optimizer, inventory):
    # read all algorithms for desired sandbox_variable(library)
    algorithms_list = np.unique(
        inventory[inventory["pipeline_key"] == sandbox_variable]["function_name"]
    ).tolist()

    # This is a place holder for selection of optimizer algorithms
    if sandbox_variable == "optimizers":
        # So far, we can use all optimizer algorithms
        pass

    # Select classifier algorithm for relevant optimizer
    elif sandbox_variable == "classifiers":
        algorithms_list = read_classifiers_algorithms(optimizer, inventory)

    return random.choice(algorithms_list)


def create_parameter_dictionary(inventory, param_list, algorithm):
    param_dict = {}

    for param in param_list:
        if param is None:
            return {}

        variable_options = inventory[
            (inventory["function_name"] == algorithm)
            & (inventory["variable_name"] == param)
        ]["variable_values"].tolist()[0]

        param_dict[param] = random.choice(variable_options)

    return param_dict


def define_parameters(
    inventory=None,
    sandbox_variable="optimizers",
    optimizer=None,
    add_unsupervised_selectors=False,
):
    """
    This function select the algorithm for the sandbox_variable which is a library. And create
    the parameters for selected algorithm
    """

    # Select the algorithm for desired sandbox library
    algorithm = read_algorithms(sandbox_variable, optimizer, inventory)

    # Read the parameters of selected algorithm
    param_list = inventory[inventory["function_name"] == algorithm][
        "variable_name"
    ].tolist()

    # Create parameters for selected algorithm
    param_dict = create_parameter_dictionary(inventory, param_list, algorithm)

    if sandbox_variable == "selectorset":
        unsupervised_selectors = [
            {
                "inputs": {"threshold": 0.95},
                "function_name": "Correlation Threshold",
            },
            {
                "inputs": {"threshold": 0.05},
                "function_name": "Variance Threshold",
            },
        ]
        if add_unsupervised_selectors:
            final_parameters = unsupervised_selectors + [
                {"inputs": param_dict, "function_name": algorithm}
            ]
        else:
            final_parameters = [{"inputs": param_dict, "function_name": algorithm}]

    else:
        final_parameters = [{"inputs": param_dict, "name": algorithm}]

    return final_parameters


def run_ga_functions(
    fitted_population,
    library_list,
    mutation_list_orj,
    mutation_list,
    recreation_list,
    top_threshold,
    weight_and_scale,
    inventory,
    search_pipeline,
    validation_method,
    add_unsupervised_selectors=False,
):
    # Run core genetic algorithm functions
    new_generation = cross_over(
        fitted_population,
        weight_and_scale,
        library_list,
        mutation_list,
        recreation_list,
        top_threshold,
    )

    new_generation = mutation(
        new_generation, inventory, mutation_list_orj, mutation_list, library_list
    )

    new_generation = recreation(
        new_generation,
        inventory,
        recreation_list,
        library_list,
        search_pipeline,
        validation_method,
        add_unsupervised_selectors=add_unsupervised_selectors,
    )

    return new_generation


def create_genetic_step(step, iteration, index, map_inputs, previous_outputs):
    """Create a genetic algorithm step and replace the input and cost table with a
       reference to the index.

    Args:
        step (dict): A pipeline step
        index (int): Index of the current step
        map_inputs (bool): input mapping should generally not be done for the first genetic step,
           but should be done for subsequent genetic steps

    Returns:
        dict: A grid point pipeline step.
    """
    temp_step = copy.deepcopy(step)

    if map_inputs:
        # Map the input data
        if "inputs" in temp_step and "input_data" in temp_step["inputs"]:
            temp_step["inputs"]["input_data"] = previous_outputs[index][1]
        elif step.get("input_data", None):
            temp_step["input_data"] = previous_outputs[index][1]

        # Map the feature table
        if step.get("inputs", None) and step["inputs"].get("feature_table", None):
            temp_step["inputs"]["feature_table"] = get_feature_table_name(
                step["inputs"]["feature_table"], previous_outputs[index][1]
            )
        elif step.get("feature_table", None):
            temp_step["feature_table"] = get_feature_table_name(
                step["feature_table"], previous_outputs[index][1]
            )

    temp_step["outputs"] = get_output_temp_name(step["outputs"], iteration, index)

    return temp_step


def get_feature_table_name(name, mapped_data_output):
    """
    feature table name format

        temp.features.<name_of_step>.<iteration>.<index>

    mapped_data_name has format

        temp.<name_of_step>.<iteration>.<index>.csv.gz

    sets the feature table input to the same iteration and index as the mapped_data_name

    """

    if isinstance(mapped_data_output, dict):
        filename = mapped_data_output["filename"]
    elif isinstance(mapped_data_output, str):
        filename = mapped_data_output

    iteration = filename.split(".")[2]
    index = filename.split(".")[3]

    return ".".join(name.split(".")[:3]) + ".{}.{}".format(iteration, index)


def get_output_temp_name(outputs, iteration, index):
    """
    output name format

        temp.features.<name_of_step> or temp.features.<name_of_step>.<iteration>.<index>

    temp output name format has format

        temp.name_of_feature.<name_of_step>.<iteration>.<index>

    """

    if has_iteration_indexes(outputs):
        return [
            ".".join(x.split(".")[:-2]) + ".{}.{}".format(iteration, index)
            for x in outputs
        ]

    return [x + ".{}.{}".format(iteration, index) for x in outputs]


def has_iteration_indexes(outputs):
    if len(outputs[0].split(".")) > 2:
        return True

    return False
