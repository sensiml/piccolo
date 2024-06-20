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

import numpy as np
from datamanager.datasegments import DataSegments
from engine.base.cost_manager import (
    calculate_feature_costs,
    get_costs_from_database,
    get_support_costs,
)
from pandas import DataFrame, concat

logger = logging.getLogger(__name__)


class SmoothingFactorException(Exception):
    pass


def handle_group_columns(func):
    """Decorator for grouping by a set of columns.

    func: the function that is wrapped
    modify_metadata (list): a list containing any new metadata this specific wrapped function adds

    input should be args which is input data
    followed by kwargs dict

    Groups input frame, applies the wrapped function to each group, and then concatenates
    the results into a single output DataFrame."""

    def func_wrapper(*args, **kwargs):

        group_columns = kwargs.get("group_columns", None)
        input_data = args[0]

        if isinstance(input_data, DataFrame):
            if group_columns:
                list_for_concatenation = []
                grouped = args[0].groupby(group_columns, sort=False, as_index=False)
                for name, group in grouped:
                    tmp_df = group.reset_index(drop=True)
                    list_for_concatenation.append(func(tmp_df, **kwargs))

                df = concat(list_for_concatenation)

            else:
                df = func(args[0], **kwargs)

            return df.reset_index(drop=True)

        else:
            datasegments = DataSegments(input_data)
            new_datasegments = []

            for segment in datasegments.iter_dataframe():
                new_datasegments.extend(func(segment, **kwargs))

            return new_datasegments

    setattr(func_wrapper, "__doc__", func.__doc__)

    return func_wrapper


def ma_filter(data, smoothing_factor=3):
    len_data = len(data)
    ma_filtered = np.zeros(len_data - smoothing_factor + 1)
    for i in range(smoothing_factor, len_data + 1):
        ma_filtered[i - smoothing_factor] = data[i - smoothing_factor : i].mean()
    return ma_filtered


def transform_column_name(transform_header, input_columns, current_column_names):

    transform_number = 0
    for name in current_column_names:
        parsed = name.split("_")
        if len(parsed) == 3:
            if parsed[1] == "ST":
                transform_number += 1

    transform_number = str("{0}".format(transform_number)).zfill(4)

    column_name = "{0}_ST_{1}".format(transform_header, transform_number)

    return column_name


def get_costs(feature_table, median_sample_size):
    cost_data = {}
    for j, generator in feature_table.iterrows():
        try:
            cost_data[generator["Generator"]] = get_costs_from_database(
                generator["Generator"]
            )
        except Exception:
            pass

            # Assemble cost parameter dictionary
    cost_parameter_dict = get_support_costs(cost_data)
    cost_parameter_dict["num_features"] = len(feature_table)
    cost_parameter_dict["median_sample_size"] = median_sample_size

    costs = calculate_feature_costs(feature_table, cost_data, cost_parameter_dict)[
        "per_generator_costs"
    ]

    # For per-generator latency divide by num_iterations
    for generator in costs:
        costs[generator]["latency"] = int(
            round(costs[generator]["latency"] / costs[generator]["num_iterations"])
        )

    items = ["latency", "sram", "flash", "stack", "num_features", "num_iterations"]

    return {key: {item: value[item] for item in items} for key, value in costs.items()}
