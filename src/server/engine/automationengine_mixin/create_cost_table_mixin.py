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
from copy import deepcopy

from engine.automationengine_mixin.parameter_optimizer_utils import get_step_id
from pandas import DataFrame

logger = logging.getLogger(__name__)


class CreateCostTableMixin:
    def __init__(self):
        pass

    def create_cost_table(self, population, results_tvo, iteration):
        error_flag = False
        summaries = []
        cost_table = DataFrame(population)

        for metric in ["flash", "sram", "stack", "latency", "cycle_count"]:
            cost_table[metric] = 0.0

        # Attach full pipeline
        cost_table["iteration"] = iteration
        cost_table["pipeline"] = ""

        # Process each configuration to get summaries and costs
        for index, result in enumerate(results_tvo):

            pipeline = deepcopy(self.static_pipeline)
            for step in self.ga_pipeline:
                pipeline.append(population[get_step_id(step)][index])

            cost_table.at[index, "pipeline"] = json.dumps(pipeline)

            class_map = result["class_map"]
            for metric in ["flash", "sram", "stack", "latency", "cycle_count"]:
                cost_table.at[index, metric] = 1e2

            summary, _ = self.create_pipeline_summary(
                cost_table.loc[index, "tvo"],
                result["model_stats"]["config"],
                class_map,
                json.loads(cost_table.loc[index, "pipeline"]),
                DataFrame(json.loads(result["feature_table"])),
            )

            summaries.append(summary)

            device_costs = {
                "flash": 0,
                "sram": 0,
                "stack": 0,
                "latency": 0,
                "cycle_count": 0,
            }

            # Gather metrics
            if summary:
                for key in summary["cost_summary"].keys():
                    if isinstance(summary["cost_summary"][key], dict):
                        device_costs = count_costs(
                            device_costs, summary["cost_summary"][key]
                        )
                    elif isinstance(summary["cost_summary"][key], list):
                        for step in summary["cost_summary"][key]:
                            device_costs = count_costs(device_costs, step)

                for metric in ["flash", "sram", "stack", "latency", "cycle_count"]:
                    cost_table.at[index, metric] = device_costs[metric]

            cost_table.at[index, "summary"] = json.dumps(summary)

        if error_flag:
            # if there is a error
            pv = None
            for i in range(len(summaries)):
                if summaries[i]:
                    pv = deepcopy(summaries[i])
                    break

            for i in range(len(summaries)):
                if not (summaries[i]):
                    summaries[i] = pv

        return cost_table, summaries


def count_costs(all_costs, item_costs):
    for metric in ["flash", "sram", "latency", "cycle_count"]:
        if item_costs.get(metric, 0):
            all_costs[metric] += item_costs[metric]
    if item_costs.get("stack", 0):
        all_costs["stack"] = max(all_costs["stack"], item_costs["stack"])

    return all_costs
