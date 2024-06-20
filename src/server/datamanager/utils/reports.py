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

from library.models import PlatformDescriptionVersion2


def cost_report(device_config, cost_dict=None, neuron_array=None):
    """A printed tabular report of the device costs incurred by the KnowledgePack or Sandbox"""
    cost_columns = ["flash", "sram", "stack", "cycle_count", "latency"]
    cost_columns_display_names = ["FLASH", "SRAM", "Stack", "Cycles", "Latency"]
    cost_column_map = dict(zip(cost_columns, cost_columns_display_names))
    cost_units = ["(Bytes)", "(Bytes)", "(Bytes)", "(Ticks)", "(Microseconds)"]
    na_string = "0"
    not_specified_string = "Not specified"

    number_of_costs = len(cost_columns)
    report = ""

    def horizontal_line():
        return "-" * (45 + 17 * number_of_costs) + "\n"

    def val_or_string(dict, key, string):
        if key in dict and dict[key]:
            if 0 < float(dict[key]) < 2:
                return round(float(dict[key]), 1)
            else:
                return int(round(float(dict[key]), 0))
        else:
            return string

    def combine_or_string(summary, key, string, operation):
        items_to_sum = [x[key] for x in summary["pipeline"] if key in x and x[key]]
        for a in ["neurons", "sensors", "framework"]:
            if summary.get(a, False) and summary[a].get(key, False):
                items_to_sum.append(summary[a][key])
        if operation == "sum":
            return int(sum(items_to_sum)) if len(items_to_sum) else string
        elif operation == "max":
            return int(max(items_to_sum)) if len(items_to_sum) else string

    def add_max_for_display(list_to_display, positions):
        for pos in positions:
            list_to_display[pos] = "Max: {}".format(list_to_display[pos])
        return list_to_display

    def populate_cost_keys(columns, cost_dict, string):
        all_costs = {cost: string for cost in columns}
        all_costs.update(cost_dict)
        return all_costs

    try:
        budget = device_config["budget"]
    except:
        budget = None

    report += horizontal_line()
    format_columns = "{:45}" + "{:>17}" * number_of_costs
    report += "\n" + format_columns.format("", *cost_columns_display_names)
    report += "\n" + format_columns.format("", *cost_units)
    report += "\n" + horizontal_line()

    format_budget = "{:45}"
    for cost in cost_columns:
        format_budget += "{" + cost + ":>17}"

    platform = PlatformDescriptionVersion2.objects.filter(
        id=device_config["target_platform"]
    )
    if platform:
        platform_name = platform[0].platform + " " + platform[0].platform_version
    else:
        platform_name = ""

    if budget:
        full_budget = populate_cost_keys(cost_columns, budget, not_specified_string)
        report += "\n" + format_budget.format(
            "Budgets (" + platform_name + ")", **full_budget
        )
    else:
        report += "\n" + "There is no budget defined"

    if cost_dict.get("neurons", None):
        report += "\n" + "\n\nPattern Matching Engine Costs"
        report += "\n" + horizontal_line()
        array_costs = populate_cost_keys(cost_columns, cost_dict["neurons"], na_string)
        array_size = "Classifier 1: {} pattern{} x {} feature{}".format(
            len(neuron_array),
            "" if len(neuron_array) == 1 else "s",
            len(neuron_array[0]["Vector"]),
            "" if len(neuron_array[0]["Vector"]) == 1 else "s",
        )
        report += "\n" + format_budget.format(array_size, **array_costs)
        report += "\n" + horizontal_line()

    report += "\n" + "\n\nFeature Extraction Costs"
    report += "\n" + horizontal_line()
    step_format = "{:45}" + "{:>17}" * number_of_costs
    step_format_sub = "{:6}{:39}" + "{:>17}" * number_of_costs
    fe_subtotals = [0] * number_of_costs
    for i, step in enumerate(cost_dict["pipeline"]):
        costs = [val_or_string(step, cost, na_string) for cost in cost_columns]
        fe_subtotals_add = [
            a + (int(b) if b == "0" else b)
            for a, b in zip(fe_subtotals[:-1], costs[:-1])
        ]
        fe_subtotals_max = [
            max(a, (int(b) if b == "0" else b))
            for a, b in zip([fe_subtotals[-1]], [costs[-1]])
        ]
        fe_subtotals = fe_subtotals_add + fe_subtotals_max
        if step["type"] in ["transform", "segmenter"]:
            report += "\n" + step_format.format(
                " - {} ({})".format(step["name"], step["type"]), *costs
            )
        elif step["type"] == "generatorset":
            report += "\n" + step_format.format(
                " - {} ({})".format(step["name"], step["type"]),
                *["" for cost in cost_columns],
            )
            if step.get("per_generator_costs", None):
                for feature_generator in step["per_generator_costs"].keys():
                    report += "\n" + step_format_sub.format(
                        "",
                        "{} x {}".format(
                            step["per_generator_costs"][feature_generator][
                                "num_iterations"
                            ],
                            feature_generator,
                        ),
                        *[
                            val_or_string(
                                step["per_generator_costs"][feature_generator],
                                cost,
                                na_string,
                            )
                            for cost in cost_columns
                        ],
                    )
    report += "\n" + horizontal_line()

    format_fe_totals = "{:>45}" + "{:>17}" * number_of_costs

    report += "\n" + format_fe_totals.format(
        "Feature Extraction Subtotals:", *add_max_for_display(fe_subtotals, [-1])
    )

    if cost_dict.get("framework", None):
        report += "\n" + "\n\nFramework Costs"
        report += "\n" + horizontal_line()
        framework_costs = populate_cost_keys(
            cost_columns, cost_dict["framework"], na_string
        )
        framework_size = "Knowledge Pack Overhead"
        report += "\n" + format_budget.format(framework_size, **framework_costs)

    report += "\n" + horizontal_line()

    totals = {
        cost: combine_or_string(cost_dict, cost, na_string, "sum")
        for cost in cost_columns[:-1]
    }
    totals.update(
        {
            cost: combine_or_string(cost_dict, cost, na_string, "max")
            for cost in [cost_columns[-1]]
        }
    )
    cost_dict_minus_sensors = {k: v for k, v in cost_dict.items() if k != "sensors"}
    totals_minus_sensors = {
        cost: combine_or_string(cost_dict_minus_sensors, cost, na_string, "sum")
        for cost in cost_columns[:-1]
    }
    totals_minus_sensors.update(
        {
            cost: combine_or_string(cost_dict_minus_sensors, cost, na_string, "max")
            for cost in [cost_columns[-1]]
        }
    )
    format_totals = "{:>45}" + "{:>17}" * number_of_costs
    report += "\n" + format_totals.format(
        "Totals Excluding Sensor Costs:",
        *add_max_for_display(
            [totals_minus_sensors[cost] for cost in cost_columns], [-1]
        ),
    )

    if cost_dict.get("sensors", None):
        report += "\n" + "\n\nSensor Costs"
        report += "\n" + horizontal_line()
        sensor_costs = populate_cost_keys(cost_columns, cost_dict["sensors"], na_string)
        sensor_size = "Buffer Size: {} samples x {} sensor stream{}".format(
            cost_dict["sensors"]["max_segment_length"],
            cost_dict["sensors"]["number_of_sensors"],
            "" if cost_dict["sensors"]["number_of_sensors"] == 1 else "s",
        )
        report += "\n" + format_budget.format(sensor_size, **sensor_costs)

    report += "\n" + horizontal_line()

    report += "\n" + format_totals.format(
        "Totals Including Sensor Costs:",
        *add_max_for_display([totals[cost] for cost in cost_columns], [-1]),
    )

    report += "\n" + "\nWarnings:"
    report += "\n" + horizontal_line()
    over_budget = False
    if budget:
        full_budget = {cost: na_string for cost in cost_columns}
        full_budget.update(budget)
        for key in full_budget.keys():
            if (
                key in totals
                and totals[key] > full_budget[key]
                and full_budget[key] not in [na_string, not_specified_string]
            ):
                report += "\n" + "   {} {} exceeds budget for {} ({} available)".format(
                    totals[key], cost_column_map[key], platform_name, full_budget[key]
                )
                over_budget = True
    if not over_budget and cost_dict.get("neurons", None):
        report += "\n" + "   None"
    if cost_dict.get("neurons", None) is None:
        report += (
            "\n"
            + "   This table does not include the costs of the pattern matching engine or sensor buffer"
        )
        report += (
            "\n"
            + "   For a more complete picture, see the cost report of a Knowledge Pack"
        )
    report += "\n" + "\n"

    return report


def cost_resource_summary(cost_dict=None, processor=None, accelerator=None):

    if cost_dict is None:
        return ""

    if processor is None:
        speed_in_mhz = 80
        speed_in_hz = speed_in_mhz * 1000000
    else:
        speed_in_mhz = processor.clock_speed_mhz
        speed_in_hz = speed_in_mhz * 1000000

    summary_totals = {"sram": 0, "flash": 0, "stack": 0, "latency": 0, "cycle_count": 0}
    sensor_summary = cost_dict.get("sensors", None)
    max_seg_len = (
        sensor_summary.get("max_segment_length", 100)
        if sensor_summary is not None
        else 100
    )
    summary_totals["max_segment_length"] = max_seg_len
    summary_totals["clock_speed_mhz"] = speed_in_mhz

    def aggregate(totals, cost_dict):
        if cost_dict.get("per_generator_costs", None) is not None:
            cost_dict.pop("per_generator_costs")
        for cost in ["flash", "sram", "stack", "latency", "cycle_count"]:
            totals[cost] += int(cost_dict.get(cost, 0))

    for key, top_value in cost_dict.items():

        if key == "classifier" or key == "pme":
            if accelerator and top_value.get(accelerator):
                summary_totals["classifier_cycle_count"] = int(
                    top_value[accelerator]["summary"]["cpu_cycles"]
                )
            else:
                summary_totals["classifier_cycle_count"] = top_value.get(
                    "cycle_count", None
                )

        if type(top_value) is list:
            for inner_value in top_value:
                aggregate(summary_totals, inner_value)
        if type(top_value) is dict:
            aggregate(summary_totals, top_value)
    summary_totals["feature_cycle_count"] = summary_totals.pop("cycle_count")
    time_ms = round((summary_totals["feature_cycle_count"] / speed_in_hz) * 1000, 6)
    time_us = round((summary_totals["feature_cycle_count"] / speed_in_hz) * 1000000, 3)
    summary_totals["feature_time_us"] = time_us
    summary_totals["feature_time_ms"] = time_ms

    if summary_totals.get("classifier_cycle_count", None):
        time_ms = round(
            (summary_totals["classifier_cycle_count"] / speed_in_hz) * 1000, 6
        )
        time_us = round(
            (summary_totals["classifier_cycle_count"] / speed_in_hz) * 1000000, 3
        )
        summary_totals["classifier_time_us"] = time_us
        summary_totals["classifier_time_ms"] = time_ms

    summary_totals.pop("latency")
    return json.dumps(summary_totals)
