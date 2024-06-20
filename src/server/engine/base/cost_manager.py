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
import logging
from ast import literal_eval

from datamanager.models import Query
from engine.base.pipeline_utils import get_max_segment_length, get_type_index
from engine.base.utils import get_config_values
from library.models import FunctionCost

from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


class AutomationError(Exception):
    pass


def init_support_costs():
    support_functions = FunctionCost.objects.all().values()
    parameters = {}

    for f in support_functions:
        parameters[f["c_function_name"]] = {
            k: v for k, v in f.items() if k in ["flash", "sram", "stack", "cycle_count"]
        }
        parameters[f["c_function_name"]]["num"] = 0

    return parameters


def get_support_costs(cost_data):
    # Populate parameters with static costs of support functions
    parameters = init_support_costs()

    # Count flash dependencies for each support function
    for core_function in cost_data.keys():
        for dependency in cost_data[core_function]["flash_dependencies"]:
            parameters[dependency]["num"] += 1

    return parameters


def get_active_features(feature_table):
    return feature_table[feature_table["Selected"].isin([True])].drop(
        "Selected", axis=1
    )


def insert_cost_parameters(cost_value, parameters):
    cost_function = str(cost_value)
    for key, value in parameters.items():
        if "_" + key in cost_function or key + "_" in cost_function:
            continue
        cost_function = cost_function.replace(key, str(value))
    return cost_function


def calc_function_costs(name, type, cost_data, cost_parameter_dict, latency_factor=1):
    costs = {"name": name, "type": type}
    number_of_features = cost_parameter_dict.get("num_features", 1)
    for cost in ["flash", "sram"]:
        # Take a proportionate share of support function costs they depend on
        costs[cost] = eval(
            insert_cost_parameters(cost_data[name][cost], cost_parameter_dict)
        )
        for support in cost_data[name]["flash_dependencies"]:
            costs[cost] += eval(
                insert_cost_parameters(
                    cost_parameter_dict[support][cost], cost_parameter_dict
                )
            ) / float(cost_parameter_dict[support]["num"])

    for cost in ["stack"]:
        # Takes the full summed value of the framework function costs they depend on
        costs[cost] = eval(
            insert_cost_parameters(cost_data[name][cost], cost_parameter_dict)
        )
        for fw_function in cost_data[name]["stack_dependencies"]:
            costs[cost] += eval(
                insert_cost_parameters(
                    cost_parameter_dict[fw_function][cost], cost_parameter_dict
                )
            )
        # Plus the maximum value of the support functions they depend on
        max_support = 0
        for support in cost_data[name]["flash_dependencies"]:
            max_support = max(max_support, (eval(cost_parameter_dict[support][cost])))
        costs[cost] += max_support

    for cost in ["latency"]:
        # Multiply by the sample rate and the input factor (e.g. number of iterations or input_streams)
        costs[cost] = (
            eval(insert_cost_parameters(cost_data[name][cost], cost_parameter_dict))
            * cost_parameter_dict.get("median_sample_size", 0)
            * float(latency_factor)
        )

    for cost in ["cycle_count"]:
        # Multiply by the sample rate and the input factor (e.g. number of iterations or input_streams)
        x_factor = (
            cost_parameter_dict.get("median_sample_size", 0)
            if name != "pme"
            else number_of_features
        )
        costs[cost] = (
            eval(insert_cost_parameters(cost_data[name][cost], cost_parameter_dict))
            * x_factor
        )
        # logger.debug(cost_data[name][cost])
    return costs


def get_costs_from_database(transform_name):
    try:
        costs = FunctionCost.objects.get(function__name=transform_name).__dict__
    except Exception:
        costs = {
            "flash": "0",
            "sram": "0",
            "stack": "0",
            "latency": "0",
            "cycle_count": "0",
            "flash_dependencies": [],
            "stack_dependencies": [],
        }

    return costs


def count_costs(feature_table, sample_size, number_of_ring_buffers, project, pipeline):
    # Get core function cost data out of the database and organize it
    settings = project.settings
    cost_data = {}
    counted_costs = []
    cost_output = {}
    number_of_features = 0
    if feature_table is not None:
        number_of_features = len(feature_table)
    if isinstance(settings, dict) and settings.get("segmenter", None):
        cost_data[settings["segmenter"]["name"]] = get_costs_from_database(
            settings["segmenter"]["name"]
        )

    for step in pipeline:
        if step["type"] in ["transform", "segmenter"]:
            cost_data[step["name"]] = get_costs_from_database(step["name"])
        elif step["type"] in ["generatorset"]:
            active_features = feature_table
            if "Selected" in feature_table.columns:
                active_features = get_active_features(active_features)
            number_of_features = len(active_features)
            for j, generator in active_features.iterrows():
                try:
                    cost_data[generator["Generator"]] = get_costs_from_database(
                        generator["Generator"]
                    )
                except Exception:
                    logger.debug(
                        {
                            "message": "Cost data not found for function {}".format(
                                generator
                            ),
                            "log_type": "datamanager",
                        }
                    )
    cost_parameter_dict = get_support_costs(cost_data)

    # Add number of features and median sample size
    cost_parameter_dict["num_features"] = number_of_features
    if sample_size and "median_sample_size" in sample_size:
        cost_parameter_dict["median_sample_size"] = sample_size["median_sample_size"]

    # In a second loop, get dynamic support function costs and calculate device costs
    # This needs to be done after support costs are counted over all relevant functions
    project_segmenter = isinstance(settings, dict) and settings.get("segmenter", False)
    if project_segmenter:
        seg_costs = calc_function_costs(
            settings["segmenter"]["name"], "segmenter", cost_data, cost_parameter_dict
        )
        counted_costs.append(seg_costs)

    for i, step in enumerate(pipeline):
        if step["type"] == "transform" or (
            step["type"] == "segmenter" and not project_segmenter
        ):
            pipeline_step = [s for s in pipeline if s["name"] == step["name"]][0]
            if pipeline_step["inputs"].get("input_columns", None):
                latency_factor = len(pipeline_step["inputs"].get("input_columns"))
            else:
                latency_factor = 1

            costs = calc_function_costs(
                step["name"],
                step["type"],
                cost_data,
                cost_parameter_dict,
                latency_factor=latency_factor,
            )
            counted_costs.append(costs)

        elif step["type"] in ["generatorset"]:
            gen_costs = calculate_feature_costs(
                active_features, cost_data, cost_parameter_dict
            )
            gen_costs.update({"name": step["name"], "type": step["type"]})
            counted_costs.append(gen_costs)

    # Get the buffer and framework costs - overwrites cost_parameter_dict so needs to happen last
    if sample_size:
        (
            cost_output["sensors"],
            cost_output["framework"],
        ) = calculate_buffer_framework_costs(
            project, pipeline, number_of_ring_buffers, sample_size, cost_parameter_dict
        )

    cost_output["pipeline"] = counted_costs

    return cost_output


def calculate_feature_costs(feature_table, cost_data, cost_parameter_dict):
    gen_costs = {
        "per_generator_costs": {},
        "flash": 0,
        "sram": 0,
        "latency": 0,
        "stack": 0,
        "cycle_count": 0,
    }

    feature_groups = feature_table.groupby(["Generator"])
    for generator, group in feature_groups:
        gen_costs["per_generator_costs"][generator] = {}
        num_iterations = len(group["Feature"].apply(lambda x: x.split("_")[1]).unique())
        costs = calc_function_costs(
            generator,
            "generator",
            cost_data,
            cost_parameter_dict,
            latency_factor=num_iterations,
        )
        gen_costs["per_generator_costs"][generator] = costs
        gen_costs["per_generator_costs"][generator]["num_iterations"] = num_iterations
        gen_costs["per_generator_costs"][generator]["num_features"] = len(group)

        # Adjust aggregates
        gen_costs["stack"] = max(
            gen_costs["stack"], gen_costs["per_generator_costs"][generator]["stack"]
        )
        for cost in ["flash", "sram", "latency", "cycle_count"]:
            gen_costs[cost] += gen_costs["per_generator_costs"][generator][cost]

    return gen_costs


def aggregate_costs(group, functions, parameters, cost_dict):
    for function in functions:
        function_costs = calc_function_costs(
            group, "", {group: function.__dict__}, parameters
        )
        for cost in ["flash", "sram", "stack", "latency", "cycle_count"]:
            # Note: summing stack works because it's required for the framework and the other groups only have 1 stack cost
            cost_dict[cost] += int(function_costs[cost])

    return cost_dict


def calculate_neuron_costs(model_parameters, num_features):
    parameters = init_support_costs()
    parameters["num_neurons"] = len(model_parameters)
    parameters["num_features"] = num_features

    pme_costs = {
        "flash": 0,
        "sram": 0,
        "stack": 0,
        "latency": 1,
        "cycle_count": 1,
    }  # Hard-coded to be non-zero

    pme_functions = FunctionCost.objects.filter(function_type="pme")
    pme_costs = aggregate_costs("pme", pme_functions, parameters, pme_costs)

    return pme_costs


def round_buffer_nearest_128(buffer_needed, nearest=128):
    """Round ring buffers to nearest 128 byte marker for accuracy"""
    rounded = nearest * round(buffer_needed / nearest)
    if rounded < buffer_needed:
        return rounded + nearest
    else:
        return rounded


def calculate_buffer_framework_costs(
    project, pipeline, number_of_ring_buffers, sample_size, parameters
):
    # Get the maximum segment length the way code gen does
    max_segment_length = 0
    if sample_size and "median_sample_size" in sample_size:
        max_segment_length = sample_size["median_sample_size"]
    seg_index = get_type_index(pipeline, "segmenter")
    if seg_index:
        max_segment_length = get_max_segment_length(pipeline[seg_index])

    # Get the number of sensor streams used by the pipeline
    num_sensor_streams = number_of_ring_buffers
    if not num_sensor_streams:
        num_sensor_streams = get_num_sensor_streams(project, pipeline)

    # Get the sample rate from the pipeline if it's there, otherwise assume it's 100
    # TODO: This should come from either the project or the the device_config, but the project doesn't hold
    # TODO: sample_rate yet and the kp doesn't exist when this is called, so this all needs refactoring
    values = get_config_values(pipeline, "sample_rate")
    if values:
        sample_rate = max(values)
    else:
        sample_rate = 100

    parameters["max_segment_length"] = max_segment_length
    parameters["num_sensor_streams"] = num_sensor_streams
    parameters["sample_rate"] = sample_rate

    # Calculate buffer costs
    buffer_costs = {
        "flash": 0,
        "sram": 0,
        "stack": 0,
        "latency": 0,
        "cycle_count": 0,
        "max_segment_length": max_segment_length,
        "number_of_sensors": num_sensor_streams,
    }

    buffer_functions = FunctionCost.objects.filter(function_type="buffer")
    buffer_function_costs = {}
    for f in buffer_functions:
        buffer_function_costs[f.c_function_name] = f.__dict__
        buffer_sram = eval(buffer_function_costs[f.c_function_name]["sram"])
        buffer_actual = round_buffer_nearest_128(buffer_sram)
        buffer_function_costs[f.c_function_name]["sram"] = buffer_actual

    parameters.update(get_support_costs(buffer_function_costs))
    buffer_costs = aggregate_costs("buffer", buffer_functions, parameters, buffer_costs)

    # Calculation framework costs
    framework_costs = {
        "flash": 0,
        "sram": 0,
        "stack": 0,
        "latency": 0,
        "cycle_count": 0,
    }
    framework_functions = FunctionCost.objects.filter(function_type="framework")
    framework_function_costs = {}
    for f in framework_functions:
        framework_function_costs[f.c_function_name] = f.__dict__

    parameters.update(get_support_costs(framework_function_costs))
    framework_costs = aggregate_costs(
        "framework", framework_functions, parameters, framework_costs
    )

    return buffer_costs, framework_costs


def get_num_sensor_streams(project, pipeline):
    if pipeline[0]["type"] == "query":
        query = Query.objects.get(project=project, name=pipeline[0]["name"])
        return len(
            [s for s in literal_eval(query.columns) if s in json.dumps(pipeline)]
        )
    elif pipeline[0]["type"] == "featurefile" and pipeline[0].get("data_columns", None):
        return len(pipeline[0]["data_columns"])
    else:
        return 0
