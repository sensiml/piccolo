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
import time
from sensiml.render import BaseRenderer
from typing import Optional, Any, Callable, Tuple
import requests
from pandas import DataFrame
from requests import Response

from typing import Union

logger = logging.getLogger(__name__)


def data_response(response_json: Union[list, str]):
    """handle response with data from server"""
    data = response_json.get("data", None)
    if data:
        if isinstance(data, list):
            print(f"Reason : {data[0].replace('DETAIL', 'Details')}")
        elif data:
            print(f"Reason : {data}")


def detail_response(response_json: dict, renderer: Optional[BaseRenderer] = None):
    """handle responses with detail (typically a server trace) form server"""
    detail = response_json.get("detail", None)
    if detail:
        if renderer:
            renderer.render(detail)
        print(detail)


def category_response_error(
    reason_json: dict, status, renderer: Optional[BaseRenderer] = None
):
    """Handles errors related to category responses from the knowledge base server (server).

    This function takes a JSON dictionary containing error details, an HTTP status code,
    and an optional renderer object. It constructs an error message based on the provided
    information and performs the following actions:

    - Formats an error message string with details from the JSON data, including:
        - HTTP status code
        - Category (if present in the JSON)
        - Error reason (if present in the JSON)
        - Additional details (if present in the JSON under the "extra" key)
    - If a renderer object is provided, it calls the renderer's `render` method
      to potentially format the message for a specific output (e.g., logging, UI).
    - Prints the formatted message to the console.

    Args:
        reason_json: A dictionary containing error details from the server response.
        status: The HTTP status code of the error response.
        renderer: An optional renderer object for custom message formatting (default: None).

    Returns:
        None
    """

    msg = (
        f"HTTPError {status} : {reason_json.get('category', None)}\n"
        + f"Reason : {reason_json.get('err', None)}\n"
        + f"Details : {reason_json.get('extra', None)}"
    )

    if renderer:
        renderer.render(msg)

    print(msg)


def read_response_json_data(
    response: Response, renderer: Optional[BaseRenderer] = None
):
    """Parse response from the server and print resopnse to terminal or option via a custom Rendere"""
    try:
        # If there is a json response we read it here
        response_json = response.json()
        if renderer:
            renderer.render(f"HTTPError: {response.status_code}")
        print(f"\n\nHTTPError: {response.status_code}")

        data_response(response_json)
        detail_response(response_json, renderer)
    except:
        pass

    try:
        # if there is a json in the reason we read it here
        category_response_error(
            json.loads(response.reason), response.status_code, renderer
        )
    except:
        pass


def check_server_response(
    response: Response, is_octet: bool = False, renderer: Optional[BaseRenderer] = None
) -> Any:
    """Check server response messages to see if they're JSON or not. If JSON,
    check whether or not an error or errors were returned.
    """
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        read_response_json_data(response, renderer)
        raise

    if is_octet:
        return response, False

    try:
        data = response.json()
    except (ValueError, KeyError):
        # Response was not JSON. Return content for now.
        return response.content, True

    return data, False


def check_pipeline_status(
    response_data: dict, parse_results: Callable, silent: bool = False, **kwargs
):
    """Read the response for a pipeline sandbox from the server

    Args:
        response_data (dictionary): rthe body of the response from the server
        parse_results (function): a function that will parse the result upon success
        silent (bool, False): silence the Pending and Started messages
        **kwargs : contains arguments to pass through to parse_results function
    """
    # If there are server errors, show them
    if response_data.get("errors") and len(response_data["errors"]):
        for error in response_data["errors"]:
            if error.get("detail"):
                logger.warning("{error}: {message} ({detail})".format(**error))
            else:
                logger.warning("{error}: {message}".format(**error))

    # If there is a status, the pipeline is Pending, Not Running, Failed, or in the Queue
    status = response_data.get("status", "SUCCESS")
    if status in ["PENDING", "STARTED", "SENT"]:
        if not silent:
            print(response_data.get("message", None))
            print(response_data.get("detail", None))
        return None, response_data.get("message", None)
    elif status in ["FAILURE", "REVOKED"]:
        print(response_data.get("message", None))
        print(response_data.get("detail", None))
        return response_data, None
    elif status in [None]:
        return response_data, None

    return parse_results(response_data, **kwargs)


def wait_for_pipeline_result(
    requester: object,
    lock: bool = True,
    silent: bool = True,
    wait_time: int = 15,
    skip_printing: int = 4,
    renderer: Optional[BaseRenderer] = None,
    **kwargs,
) -> Any:
    """
    This function will continuously polll a single pipeline for peridoically every **wait_time** until the
    pipeline finishes executing. It will print out status reports every time it polls for results. When it
    finishes it will parse the final result into the appropriate format.
    """
    count = 0
    start = time.time()

    results = requester.retrieve(silent=silent, **kwargs)
    if results[0] is not None:
        lock = False

    while lock:
        time.sleep(wait_time)
        results = requester.retrieve(silent=True, **kwargs)
        if results[0] is None:
            if renderer:
                renderer.render(results[1])
            if count % skip_printing == 0:
                print("")
                print(results[1], end="")
                print(" ", end="")
            else:
                print(".", end="")
            count += 1
        else:
            lock = False

    if isinstance(results[0], dict) and results[0].get("status") is None:
        msg = "No results stored"
    else:
        execution_time = time.time() - start
        msg = f"\n\nResults Retrieved. Wall Time: {int(execution_time / 60)} min. {int(execution_time % 60)} sec."

    if renderer:
        renderer.render(msg)

    print(msg)

    return results


def make_statistics_table(response_data: dict) -> Tuple[DataFrame, bool]:  # type: ignore
    error_report = None
    data = DataFrame(response_data)

    if "event_labels" in data.columns:
        labels_dict = {}
        labels = json.loads(data["event_labels"].to_json(orient="records"))
        data = data.drop("event_labels", 1)
        for label in labels:
            for name, info in label.items():
                for values in info:
                    column_name = f"{name}: {values['value']}"
                    if column_name not in labels_dict:
                        labels_dict[column_name] = []
                    labels_dict[column_name].append(values["count"])
        for column_name, column_values in labels_dict.items():
            data[column_name] = column_values

    if "metadata" in data.columns:
        meatadata_dict = {}
        meatadata_set = json.loads(data["metadata"].to_json(orient="records"))
        data = data.drop("metadata", 1)
        for metadata in meatadata_set:
            for name, value in metadata.items():
                if name not in meatadata_dict:
                    meatadata_dict[name] = []
                meatadata_dict[name].append(value)
        for column_name, column_values in meatadata_dict.items():
            data[column_name] = column_values

    # Post-processing to get numeric index
    data["sample"] = data.index.astype(int)
    data = data.set_index("sample")
    data.index.names = [None]
    data = data.sort_index(axis=0)
    cols = data.columns.tolist()
    if "id" in cols:
        data = data[["id"] + [c for c in cols if c != "id"]]

    return data.sort_index(axis=0), error_report


def make_cost_report(
    device_config: dict,
    cost_dict: Optional[dict] = None,
    neuron_array: Optional[DataFrame] = None,
):
    """A printed tabular report of the device costs incurred by the KnowledgePack or Sandbox"""
    cost_columns = ["Bytes", "RAM", "Microseconds", "Stack"]
    cost_columns_display_names = ["Flash", "SRAM", "Latency", "Stack"]
    cost_units = ["(Bytes)", "(Bytes)", "(Microseconds)", "(Bytes)"]
    na_string = "0"
    not_specified_string = "Not specified"

    number_of_costs = len(cost_columns)

    def horizontal_line():
        print("-" * (45 + 17 * number_of_costs))

    def val_or_string(dict, key, string):
        if key in dict and dict[key]:
            if 0 < float(dict[key]) < 1:
                return round(float(dict[key]), 1)
            else:
                return int(float(dict[key]))
        else:
            return string

    def sum_or_string(summary, key, string):
        items_to_sum = [x[key] for x in summary["pipeline"] if key in x and x[key]]
        for a in ["neurons", "sensors"]:
            if summary.get(a, False) and summary[a].get(key, False):
                items_to_sum.append(summary[a][key])
        return int(sum(items_to_sum)) if len(items_to_sum) else string

    def populate_cost_keys(columns, cost_dict, string):
        all_costs = {cost: string for cost in columns}
        all_costs.update(cost_dict)
        return all_costs

    try:
        budget = device_config["budget"]
    except:
        budget = None

    horizontal_line()
    format_columns = "{:45}" + "{:>17}" * number_of_costs
    print(format_columns.format("", *cost_columns_display_names))
    print(format_columns.format("", *cost_units))
    horizontal_line()

    format_budget = "{:45}"
    for cost in cost_columns:
        format_budget += "{" + cost + ":>17}"

    if budget:
        full_budget = populate_cost_keys(cost_columns, budget, not_specified_string)
        print(
            format_budget.format(
                "Budgets ("
                + device_config["target_platform"]
                + " "
                + device_config["platform_version"]
                + ")",
                **full_budget,
            )
        )
    else:
        print("There is no budget defined")

    if cost_dict.get("neurons", None):
        print("\n\nPattern Matching Engine Costs")
        horizontal_line()
        array_costs = populate_cost_keys(cost_columns, cost_dict["neurons"], na_string)
        array_size = "Classifier 1: {} neurons x {} features".format(
            len(neuron_array), len(neuron_array[0]["Vector"])
        )
        print(format_budget.format(array_size, **array_costs))
        horizontal_line()

    print("\n\nFeature Extraction Costs")
    horizontal_line()
    step_format = "{:45}" + "{:>17}" * number_of_costs
    step_format_sub = "{:6}{:39}" + "{:>17}" * number_of_costs
    fe_subtotals = [0] * number_of_costs
    for i, step in enumerate(cost_dict["pipeline"]):
        costs = [val_or_string(step, cost, na_string) for cost in cost_columns]
        fe_subtotals = [
            a + (int(b) if b == "0" else b) for a, b in zip(fe_subtotals, costs)
        ]
        if step["type"] in ["transform", "segmenter"]:
            print(
                step_format.format(
                    " - {} ({})".format(step["name"], step["type"]), *costs
                )
            )
        elif step["type"] == "generatorset":
            print(
                step_format.format(
                    " - {} ({})".format(step["name"], step["type"]),
                    *["" for cost in cost_columns],
                )
            )
            if step.get("per_generator_costs", None):
                for feature_generator in step["per_generator_costs"].keys():
                    print(
                        step_format_sub.format(
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
                    )
    horizontal_line()

    format_fe_totals = "{:>45}" + "{:>17}" * number_of_costs
    print(format_fe_totals.format("Feature Extraction Subtotals:", *fe_subtotals))

    if cost_dict.get("framework", None):
        print("\n\nFramework Costs")
        horizontal_line()
        framework_costs = populate_cost_keys(
            cost_columns, cost_dict["framework"], na_string
        )
        framework_size = "Knowledge Pack Overhead"
        print(format_budget.format(framework_size, **framework_costs))

    horizontal_line()

    totals = {cost: sum_or_string(cost_dict, cost, na_string) for cost in cost_columns}
    cost_dict_minus_sensors = {k: v for k, v in cost_dict.items() if k != "sensors"}
    totals_minus_sensors = {
        cost: sum_or_string(cost_dict_minus_sensors, cost, na_string)
        for cost in cost_columns
    }
    format_totals = "{:>45}" + "{:>17}" * number_of_costs
    print(
        format_totals.format(
            "Totals Excluding Sensor Costs:",
            *[totals_minus_sensors[cost] for cost in cost_columns],
        )
    )

    if cost_dict.get("sensors", None):
        print("\n\nSensor Costs")
        horizontal_line()
        sensor_costs = populate_cost_keys(cost_columns, cost_dict["sensors"], na_string)
        sensor_size = "Buffer Size: {} samples x {} sensor streams".format(
            cost_dict["sensors"]["max_segment_length"],
            cost_dict["sensors"]["number_of_sensors"],
        )
        print(format_budget.format(sensor_size, **sensor_costs))

    horizontal_line()

    print(
        format_totals.format(
            "Totals Including Sensor Costs:", *[totals[cost] for cost in cost_columns]
        )
    )

    print("\nWarnings:")
    horizontal_line()
    over_budget = False
    if budget:
        full_budget = {cost: na_string for cost in cost_columns}
        full_budget.update(budget)
        for key in full_budget.keys():
            if totals[key] > full_budget[key] and full_budget[key] not in [
                na_string,
                not_specified_string,
            ]:
                print(
                    "   {} {} exceeds budget for {} {} ({} available)".format(
                        totals[key],
                        key,
                        device_config["target_platform"],
                        device_config["platform_version"],
                        full_budget[key],
                    )
                )
                over_budget = True
    if not over_budget and cost_dict.get("neurons", None):
        print("   None")
    if cost_dict.get("neurons", None) is None:
        print(
            "   This table does not include the costs of the neuron array or sensor buffer"
        )
        print("   For a more complete picture, see the cost report of a Knowledge Pack")
    print("\n")
