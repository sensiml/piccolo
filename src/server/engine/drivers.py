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

import json
import sys
import time
import traceback
from collections import OrderedDict

import engine.base.cost_manager as cost_manager
import pandas as pd
from datamanager import utils
from datamanager.datasegments import DataSegments
from datamanager.models import Sandbox
from django.conf import settings
from django.core.exceptions import ValidationError
from engine.base.contractenforcer import ContractEnforcer
from engine.base.temp_table import TempVariableTable
from engine.base.utils import (
    logging,
    make_tvo_config,
    np,
    remap_labels_to_integers,
    replace_labels_in_input_data,
    return_labels_to_original_values,
)
from library.classifiers.classifiers import get_classifier
from library.model_generators.model_generators import (
    get_model_generator,
    validate_config,
)
from library.model_validation.validation_methods import get_validation_method
from library.core_functions.augmentation import is_augmented
from library.models import Transform
from logger.log_handler import LogHandler
from numpy import isnan
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class ExecutionError(Exception):
    pass


class FeatureGenerationError(Exception):
    pass


class NoFeaturesGeneratedError(Exception):
    pass


class TVOValidationError(Exception):
    pass


def segment_function_caller(
    input_data, step, team_id, project_id, pipeline_id, user_id, task_id, **kwargs
):
    # Contract enforcer checks input types against transform contract
    transform = Transform.objects.get(name=step["name"])
    contract_enforcer = ContractEnforcer(step, transform.input_contract, transform.name)
    args = contract_enforcer.enforce()

    # Load and call function
    func = utils.get_function(transform)
    output_contract = transform.output_contract
    results = func(input_data, **args)

    if isinstance(results, tuple):
        contract_enforcer.enforce_output(len(output_contract), len(results))
    else:
        contract_enforcer.enforce_output(len(output_contract), 1)
    if len(output_contract) == 1:
        results = {[t["name"] for t in output_contract][0]: results}
    else:
        results = dict(zip([t["name"] for t in output_contract], results))

    if "Seg_Begin" in results["output_data"][0]["metadata"]:
        result_output = [
            [int(seg["metadata"]["Seg_Begin"]), int(seg["metadata"]["Seg_End"])]
            for seg in results["output_data"]
        ]
    else:
        result_output = []

    return result_output, None


def function_caller(
    input_data, step, team_id, project_id, pipeline_id, user_id, task_id, **kwargs
):
    # Load Functions and retrieve data
    transform = Transform.objects.get(name=step["name"])
    func = utils.get_function(transform)

    # Contract enforcer checks input types against transform contract
    contract_enforcer = ContractEnforcer(step, transform.input_contract, transform.name)
    args = contract_enforcer.enforce()

    # Call Function
    results = func(input_data, **args)

    # Verify Output
    output_contract = transform.output_contract
    if isinstance(results, tuple):
        contract_enforcer.enforce_output(len(output_contract), len(results))
    else:
        contract_enforcer.enforce_output(len(output_contract), 1)
    if len(output_contract) == 1:
        results = {[t["name"] for t in output_contract][0]: results}
    else:
        results = dict(zip([t["name"] for t in output_contract], results))

    # Save results to temp variable
    for index, result in enumerate(results):
        contract_output = [t for t in output_contract if t["name"] == result][0]

        # Persistent variables will be saved to the temp variable, but will not be returned
        if "persist" in contract_output and contract_output["persist"]:
            temp_table = TempVariableTable(pipeline_id=pipeline_id)
            # Create a variable name based on the step output, for parallel compatibility

            step_id = ".".join(step["outputs"][0].split(".")[1:])
            persistent_output = {
                "step_type": step["type"],
                "function_name": step["name"],
                "parameter_name": contract_output["name"],
                "parameter_value": results[result],
            }

            temp_table.add_variable_temp(
                "persist.{0}.{1}".format(step_id, contract_output["name"]),
                data=persistent_output,
                overwrite=True,
            )

        # The non-persistent output will be saved to temp and returned
        else:
            result_output = results[result]

        return result_output, step.get("feature_table_value", None)

    return result_output, None


def get_function_from_database(function, pipeline_id):
    transform = Transform.objects.get(
        name=function["function_name"],
        library_pack__uuid=function["inputs"].get(
            "library_pack", settings.SENSIML_LIBRARY_PACK
        ),
    )

    if (
        transform.custom
        and transform.library_pack.team
        != Sandbox.objects.get(uuid=pipeline_id).project.team
    ):
        raise Exception("Function {} not found.".format(function.name))

    return transform


def feature_generation_driver(
    input_data, step, team_id, project_id, pipeline_id, user_id, task_id, **kwargs
):
    if len(input_data) == 0:
        raise Exception(
            "No data was passed to the feature generator step of the pipeline. This can happen if the window size for Windowing Segmentation is larger than your smallest labeled segments. Check the distributions of label sizes in this pipeline's dataset. If that is not the issue, check the previous steps in the pipeline to see if they might be filtering out the input data."
        )

    errors = []

    function_list = []
    generator_list = []

    for g, generator in enumerate(step["set"]):
        function = get_function_from_database(
            function=generator, pipeline_id=pipeline_id
        )

        function_list.append([function])

    # Track start time
    start_time = time.time()

    # Set up the list of functions and their costs
    for index, function_set in enumerate(function_list):
        for function in function_set:
            inputs = {}
            inputs["inputs"] = step["set"][index]["inputs"]

            # Update with params from the step, but only if they are in the input contract
            for item in [item["name"] for item in function.input_contract]:
                if item in step["inputs"].keys():
                    inputs["inputs"][item] = step["inputs"][item]

            generator_call = utils.get_function(function)

            contract_enforcer = ContractEnforcer(
                inputs, function.input_contract, function.name
            )
            args = contract_enforcer.enforce()

            # Add the generator function along with its arguments to a list
            generator_list.append(([generator_call, args], function))

    # When the flag is set, generate features only from the feature summary pipeline for recognition
    if "feature_summary" in step:
        # All FGs always have the same group columns
        result, feature_summary, errors = generate_features(
            pipeline_id,
            input_data,
            generator_list,
            errors,
            True,
            [s["outputs"] for s in step["set"]],
        )

        # Rename features in the DataFrame - relevant if feature selection was used
        current_feature_names = [f["Feature"] for f in feature_summary]
        correct_feature_names = [f["Feature"] for f in step["feature_summary"]]
        name_map = dict(zip(current_feature_names, correct_feature_names))
        result = result.rename(columns=name_map)

        return result, step["feature_summary"]

    # All FGs always have the same group columns
    results, feature_table, errors = generate_features(
        pipeline_id, input_data, generator_list, errors, True
    )

    end_time = time.time()

    total_secs = round(end_time - start_time)
    logger.userlog(
        {
            "message": "Feature Generation Summary",
            "data": {
                "number_of_generators": len(generator_list),
                "number_of_features": len(feature_table),
                "number_of_feature_vectors": len(results),
                "execution_time": total_secs,
            },
            "sandbox_uuid": pipeline_id,
            "project_uuid": project_id,
            "log_type": "PID",
            "task_id": task_id,
        }
    )

    if len(errors):
        logger.errorlog(
            {
                "message": "Feature Generator Errors",
                "data": errors,
                "UUID": pipeline_id,
                "log_type": "PID",
            }
        )

    if not len(feature_table):
        raise NoFeaturesGeneratedError(
            "No features were successfully generated. Make sure the pipeline is accurate "
            + "and consider adding more feature generators."
        )

    return results, feature_table


##########################################################
def augmentation_driver(
    input_data, step, team_id, project_id, pipeline_id, user_id, task_id, **kwargs
):
    if len(input_data) == 0:
        raise Exception("No data was passed to the augmenter function.")

    # adding pipeline external input parameters
    # such as "label_column", "group_column"and "passthrough_columns"
    step_inputs = step.get("inputs", {})
    unique_functions = set([st["function_name"] for st in step["set"]])
    if len(unique_functions) > 1 and "Random Crop" in unique_functions:
        raise ValidationError(
            "Cropping functions cannot be used in the same augmentation set with other augmentation functions to avoid dataset complications. Please dedicate a separate set for cropping functions."
        )

    output_data_set = []
    ignore_index = []
    force_remove_index = (
        []
    )  # when cropping the original segments are forcefully removed

    for g, augmenter in enumerate(step["set"]):
        function = get_function_from_database(
            function=augmenter, pipeline_id=pipeline_id
        )

        func = utils.get_function(function)
        contract_enforcer = ContractEnforcer(
            augmenter, function.input_contract, function.name
        )
        args = contract_enforcer.enforce()

        for k, v in step_inputs.items():
            args[k] = v

        # Call Function
        output_data, index, force_remove_originals = func(input_data, **args)

        output_data_set += output_data

        replace = augmenter["inputs"].get("replace", False)
        if replace:
            ignore_index += index
        if force_remove_originals:
            force_remove_index += index

    ignore_index = list(set(ignore_index))
    force_remove_index = list(set(force_remove_index))

    for ix, data in enumerate(input_data):
        if not ix in force_remove_index:
            if ix in ignore_index:
                # an original segment chosen for augmentation
                if "segment_uuid" in data["metadata"] and not is_augmented(
                    data["metadata"]["segment_uuid"]
                ):
                    output_data_set.append(
                        data
                    )  # always preserve the original segments
            else:
                output_data_set.append(data)  # if not ignored, add back to the set

    return output_data_set, None


##########################################################


def feature_selection_driver(
    input_data, step, team_id, project_id, pipeline_id, user_id, task_id, **kwargs
):
    label_column = step["inputs"].get("label_column", "")
    passthrough_columns = step["inputs"].get("passthrough_columns", [])
    if label_column not in passthrough_columns:
        passthrough_columns += [label_column]

    feature_columns = [
        col for col in input_data.columns if col not in passthrough_columns
    ]

    feature_table = step.pop(
        "feature_table_value", pd.DataFrame(feature_columns, columns=["Feature"])
    )

    # If specified, check for the presence of the label_column in the data
    if label_column and label_column not in input_data.columns:
        raise ExecutionError(
            "The label column {0} is not present in the"
            "feature selection step. Check the spelling and"
            " the preceding steps to make sure it is in the"
            " query and the group_columns property of the feature"
            " generation step.".format(label_column)
        )

    # Data cleansing - this needs to be reviewed and put into another module!
    # Drop columns with None values
    none_cols = [col for col in feature_columns if any(input_data[col]) is None]
    input_data.drop(none_cols, axis=1, inplace=True)
    input_data.fillna(0.0, inplace=True)

    feature_table["Selected"] = True
    feature_table["EliminatedBy"] = ""

    selected_data = input_data
    for selector in step["set"]:
        if "function_name" in selector:
            actual_function = Transform.objects.get(name=selector["function_name"])
        else:
            actual_function = Transform.objects.get(name=selector["name"])
        for inp in actual_function.input_contract:
            if inp["name"] in step["inputs"] and not selector["inputs"].get(
                inp["name"], None
            ):
                selector["inputs"][inp["name"]] = step["inputs"][inp["name"]]
        selector["inputs"]["passthrough_columns"] = passthrough_columns

        selector_call = utils.get_function(actual_function)

        contract_enforcer = ContractEnforcer(
            selector, actual_function.input_contract, actual_function.name
        )
        args = contract_enforcer.enforce()

        # append function specific args.
        args["input_data"] = selected_data
        args["feature_table"] = feature_table

        selected_data, unselected_features = selector_call(**args)

        eliminated = {}
        for feature in unselected_features:
            eliminated[feature] = actual_function.name

        for key in eliminated.keys():
            feature_table.loc[feature_table["Feature"] == key, "Selected"] = False
            feature_table.loc[
                feature_table["Feature"] == key, "EliminatedBy"
            ] = eliminated[key]

        num_feat = selected_data.shape[1] - len(passthrough_columns)
        if num_feat <= step["inputs"]["number_of_features"]:
            break

    return selected_data, feature_table


def feature_transform_caller(
    input_data, step, team_id, project_id, pipeline_id, user_id, task_id, **kwargs
):
    # Load Functions and retrieve data
    feature_table = step.pop("feature_table_value", None)

    transform = Transform.objects.get(name=step["name"])
    func = utils.get_function(transform)

    # Contract enforcer checks input types against transform contract
    contract_enforcer = ContractEnforcer(step, transform.input_contract, transform.name)
    args = contract_enforcer.enforce()

    # This is the first pass, we want to make all our feature transforms take/modify the feature table eventually
    if step["name"] == "Feature Cascade":
        results, feature_table = func(input_data, feature_table, **args)
    else:
        # Call Function
        results = func(input_data, **args)

    # Verify Output
    output_contract = transform.output_contract

    if isinstance(results, tuple):
        contract_enforcer.enforce_output(len(output_contract), len(results))
    else:
        contract_enforcer.enforce_output(len(output_contract), 1)
    if len(output_contract) == 1:
        results = {[t["name"] for t in output_contract][0]: results}
    else:
        results = OrderedDict(zip([t["name"] for t in output_contract], results))

    # Save results to temp variable
    for index, result in enumerate(results):
        contract_output = [t for t in output_contract if t["name"] == result][0]
        # Persistent variables will be saved to the temp variable, but will not be returned
        if "persist" in contract_output and contract_output["persist"]:
            temp_table = TempVariableTable(pipeline_id=pipeline_id)
            # Create a variable name based on the step output, for parallel compatibility
            step_id = ".".join(step["outputs"][0].split(".")[1:])
            persistent_output = {
                "step_type": step["type"],
                "function_name": step["name"],
                "parameter_name": contract_output["name"],
                "parameter_value": results[result],
            }
            temp_table.add_variable_temp(
                "persist.{0}.{1}".format(step_id, contract_output["name"]),
                data=persistent_output,
                overwrite=True,
            )

        # The non-persistent output will be saved to temp and returned
        else:
            result_output = results[result]

    return result_output, feature_table


def generate_features(
    pipeline_id, input_data, generator_list, errors, calc_features=False, outputs=None
):
    """Generates features and costs and accrues error messages.


    Feature - Feature Name
    Generator - Generator Name
    Category - Generator Category
    Generator Index - Index of Generator in Pipeline
    GeneratorTrueIndex - Index of Generator in KnowledgePack
    GeneratorFamilyIndex - Index of Feature within Generator Family
    ContextIndex - Index of Feature Generator within Context
    CascadeIndex - Index of Cascade
    GeneratorFamilyFeatures - Number of features created by this generator

    Context are windows of features that are fed into a model. Each context calculates all features
    Cascades are made up of contexts. Each context will compute the same features.
    Generator Family refers to generator that generates more than one feature (ie. Histgoram)


    """

    result = DataFrame()
    feature_table = []
    pad = 4
    generator_counter = 0
    feature_index = 0
    gen_incremented = 0

    for index, gen in enumerate(generator_list):
        generator_family_index = 0
        generator_call = gen[0][0]
        kwargs = gen[0][1]
        contract_num_inputs = gen[1].input_contract[1].get("num_columns", None)
        generator_family = gen[1].output_contract[0].get("family", False)
        kwargs.pop("input_data", None)
        kwargs["group_columns"] = list(input_data[0]["metadata"].keys())
        try:
            column_result = DataSegments(input_data).apply(generator_call, **kwargs)
        except Exception as e:
            column_result = None
            error = {
                "pid": pipeline_id,
                "step": "Feature Generation",
                "error": "FeatureGenerationError",
                "function_in_file": generator_call.__name__,
                "input_keys": list(kwargs.keys()),
                "message": "{} threw an exception so it was dropped".format(
                    gen[1].name
                ),
                "detail": str(e),
            }
            _, _, exc_traceback = sys.exc_info()
            debug_error = {"traceback": "\n".join(traceback.format_tb(exc_traceback))}
            debug_error.update(error)

            logger.error(
                {
                    "message": str(e),
                    "UUID": pipeline_id,
                    "log_type": "PID",
                    "data": debug_error,
                }
            )

            errors.append(error)

        if isinstance(column_result, DataFrame):
            prefix_columns = {}
            feature_names = [
                col
                for col in column_result.columns
                if col not in kwargs["group_columns"]
            ]

            # Remove any columns containing NaNs and log the error
            for col in feature_names:
                if isnan(column_result[col]).any():
                    column_result = column_result.drop(col, axis=1)
                    error = {
                        "step": "Feature Generation",
                        "error": "FeatureGenerationError",
                        "function_in_file": generator_call.__name__,
                        "input_keys": list(kwargs.keys()),
                        "message": "{} produced an incomplete result for feature {} so it was dropped".format(
                            gen[1].name, col
                        ),
                    }
                    logger.error(
                        {
                            "message": "Feature Generation Error",
                            "data": error,
                            "UUID": pipeline_id,
                            "log_type": "PID",
                        }
                    )
                    errors.append(error)

            sensor_combinations = set()

            if outputs:
                features_to_keep = [
                    n for i, n in enumerate(feature_names) if i in outputs[index]
                ]
                column_result = column_result[
                    kwargs["group_columns"] + features_to_keep
                ]

            # Multiple Sensors Multiple Features using different sensors combination
            for feature_name in feature_names:
                used_sensors = get_used_sensors(
                    feature_name, kwargs["columns"], contract_num_inputs
                )
                if used_sensors and not sensor_combinations.intersection(
                    set(used_sensors)
                ):
                    gen_incremented = index
                    sensor_combinations.add(used_sensors[0])
                    if len(sensor_combinations) >= 1:
                        generator_counter += 1
                if gen_incremented != index:
                    generator_counter += 1
                    gen_incremented = index
                prefix_columns[feature_name] = "gen_{1:0{0}}_{2}".format(
                    pad, generator_counter, feature_name
                )

            column_result.rename(columns=prefix_columns, inplace=True)

            if len(result):
                result = pd.merge(
                    result,
                    column_result,
                    on=kwargs["group_columns"],
                    left_index=False,
                    right_index=False,
                )
            else:
                result = column_result.reset_index(drop=True)

            generator_columns = [
                c for c in column_result.columns if c not in kwargs["group_columns"]
            ]

            generator_families = [int(col.split("_")[1]) for col in generator_columns]
            generator_family_features = {}
            for g_index in set(generator_families):
                generator_family_features[g_index] = generator_families.count(g_index)

            for col in generator_columns:
                feature_dict = {}
                feature_dict["Feature"] = col
                feature_dict["Generator"] = gen[1].name
                feature_dict["Category"] = gen[1].subtype
                feature_dict["GeneratorIndex"] = index
                feature_dict["GeneratorTrueIndex"] = int(col.split("_")[1])
                feature_dict["GeneratorFamilyIndex"] = generator_family_index
                feature_dict["ContextIndex"] = feature_index
                feature_dict["LibraryPack"] = kwargs.get(
                    "library_pack", settings.SENSIML_LIBRARY_PACK
                )
                feature_dict["GeneratorFamilyFeatures"] = generator_family_features[
                    int(col.split("_")[1])
                ]
                feature_index += 1
                if generator_family:
                    generator_family_index += 1

                # Determine the sensor names associated with the feature
                feature_dict["Sensors"] = get_used_sensors(
                    col, kwargs["columns"], contract_num_inputs
                )
                if not len(feature_dict["Sensors"]):
                    feature_dict["Sensors"] = kwargs["columns"]
                feature_dict["Sensors"] = ",".join(feature_dict["Sensors"])
                feature_table.append(feature_dict)

        else:
            for context in errors:
                context.update({"name": gen[1].name, "subtype": gen[1].subtype})
                logger.error(
                    {
                        "message": "Feature generator failed: {0}".format(gen[1].name),
                        "data": context,
                        "UUID": pipeline_id,
                        "log_type": "PID",
                    }
                )

    if "temp_group" in result.columns:
        result = result.drop("temp_group", axis=1)

    return result, feature_table, errors


def is_classification(tvo_config):
    if tvo_config.get("estimator_type") == "regression":
        return False

    if tvo_config["classifier"] == "Linear Regression":
        return False

    return True


def tvo_driver(
    input_data, step, team_id, project_id, pipeline_id, user_id, task_id, **kwargs
):
    """
    Driver for the train-validate-optimize step.

    Args:
        step (dict): A dictionary containing at least the following keys: input_data, label_column. \
                    May also contain appropriate values for the following keys: validation_methods, classifiers, \
                    optimizers, outputs, group_columns, ignore_column, run_non_optimized, number_of_neurons, number_of_folds, number_of_iterations
        pipeline_id (str): A unique id for the pipeline

    Raises:
        ExecutionError: Description
        TVOValidationError: Description

    Returns:
        The results from the TVO configuration
    """
    feature_table = step.pop("feature_table_value", None)

    # Assemble all possible configurations using the ranges supplied; provide defaults if necessary
    classifier = step.get("classifiers", None)
    validation_method = step.get("validation_methods", None)
    optimizer = step.get("optimizers", None)

    if classifier is None:
        raise TVOValidationError("No Classifier Specified")

    if validation_method is None:
        raise TVOValidationError("No Validation Method Specified")

    if optimizer is None:
        raise TVOValidationError("No Optimizer Specified")

    tvo_config = make_tvo_config(
        step, classifier[0], validation_method[0], optimizer[0]
    )

    # Make sure this is a valid configuration
    if validate_config(tvo_config) == False:
        raise TVOValidationError(
            "The selected combination of classifier: {}, \
                             validation_method: {} and optimizer: {} is not a\
                              valid tvo configuration is not valid.".format(
                classifier["name"], validation_method["name"], optimizer["name"]
            )
        )
    tvo_results = {}
    # tvo_results["input_data"] = json.dumps(input_data.to_dict(orient='list'))

    # Ensure that the label column is specified and present in the input data
    if step["label_column"] == "":
        raise ExecutionError("A label column is required for model generation.")
    elif step["label_column"] not in input_data.columns:
        raise ExecutionError(
            "The label column {0} is not present in the model generation step. \
                                Check the spelling and the preceding steps to make sure it is in the query,  \
                                the group_columns property of the feature generation step, and the passthrough_columns \
                                of the feature selection step.".format(
                step["label_column"]
            )
        )

    # Read features from the incoming table of selected features or if it's not available create the table
    feature_table, selected_features, feature_columns = get_selected_features(
        feature_table, pipeline_id
    )
    if not len(feature_table):
        feature_table, feature_columns = create_feature_table_from_tvo(
            step, input_data.columns.tolist()
        )

    tvo_config["feature_columns"] = feature_columns  # Ensure feature order

    logger.userlog(
        {
            "message": "TVO Data Size {}".format(input_data.shape),
            "sandbox_uuid": pipeline_id,
            "log_type": "PID",
            "task_id": task_id,
            "project_uuid": project_id,
        }
    )

    if is_classification(tvo_config):
        # Remap labels to increasing non-zero integers and replace them in the input data
        original_map, reverse_map = remap_labels_to_integers(step, input_data)
        input_data = replace_labels_in_input_data(
            original_map, step["label_column"], input_data
        )

        tvo_config["reverse_map"] = reverse_map
        tvo_config["class_map"] = original_map

    start_time = time.time()
    model_stats, _ = execute_tvo_config(
        tvo_config,
        input_data,
        team_id=team_id,
        project_id=project_id,
        pipeline_id=pipeline_id,
        save_model_parameters=kwargs.get("save_model_parameters", True),
    )

    if is_classification(tvo_config):
        for model in model_stats["models"]:
            for metric in ["train", "validation", "test"]:
                model_stats["models"][model]["metrics"][
                    metric
                ] = return_labels_to_original_values(
                    model_stats["models"][model]["metrics"][metric], reverse_map
                )

        tvo_results["class_map"] = reverse_map
    else:
        tvo_results["class_map"] = None

    model_stats["config"] = tvo_config
    tvo_results["model_stats"] = model_stats
    tvo_results["feature_table"] = json.dumps(
        feature_table.replace({np.nan: None}).to_dict(orient="list")
    )

    logger.userlog(
        {
            "message": "Training Time: {} DataShape: {} Optimizer: {}".format(
                time.time() - start_time, input_data.shape, step["optimizers"][0]
            ),
            "sandbox_uuid": pipeline_id,
            "log_type": "PID",
            "task_id": task_id,
            "project_uuid": project_id,
        }
    )

    return tvo_results, feature_table


def execute_tvo_config(
    config,
    input_data,
    team_id=None,
    project_id=None,
    pipeline_id=None,
    save_model_parameters=True,
):
    """Executes a TVO config on an input DataFrame.

    Stays outside the ExecutionEngine class for access by multiple concurrent
    processes called by the ExecutionEngine."""
    # Covering a limited number of optimizer/validation_methods/classifier permutations:
    validation_method = get_validation_method(config, input_data)
    classifier = get_classifier(config, save_model_parameters=save_model_parameters)
    model_generator = get_model_generator(
        config,
        classifier=classifier,
        validation_method=validation_method,
        team_id=team_id,
        project_id=project_id,
        pipeline_id=pipeline_id,
        save_model_parameters=save_model_parameters,
    )

    # Run the model generator and format the results
    model_generator.run()
    results = model_generator.get_results()

    execution_stats = {"status": "completed"}  # for now

    return results, execution_stats


def get_used_sensors(name, sensors, contract_num_inputs):
    used_sensors = []

    if contract_num_inputs == -1:
        return sensors

    for sensor in sensors:
        if sensor in name:
            used_sensors.append(sensor)

    return used_sensors


def get_selected_features(feature_table, pipeline_id):
    if feature_table is not None:
        if "Selected" in feature_table.columns:
            # The eliminated features will be of type string
            selected_features = cost_manager.get_active_features(feature_table)
        else:
            selected_features = feature_table
        feature_columns = selected_features["Feature"].tolist()
    else:
        logger.errorlog(
            {
                "message": "No valid feature stats were provided in the TVO step.",
                "UUID": pipeline_id,
                "log_type": "PID",
            }
        )
        return pd.DataFrame(), pd.DataFrame(), []

    return feature_table, selected_features, feature_columns


def create_feature_table_from_tvo(step, available_columns):
    implied_feature_columns = [
        c
        for c in available_columns
        if c
        not in (
            step["ignore_columns"]
            if "ignore_columns" in step and step["ignore_columns"]
            else []
        )
        and c != step.get("label_column", "")
    ]
    feature_table = pd.DataFrame(implied_feature_columns, columns=["Feature"])
    return feature_table, implied_feature_columns
