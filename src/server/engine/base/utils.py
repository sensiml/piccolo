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
import pandas as pd
from numpy import float32, float64, int64, ndarray

logger = logging.getLogger(__name__)

METRICS = [
    "sensitivity",
    "precision",
    "f1_score",
    "mean_squared_error",
    "median_absolute_error",
    "mean_absolute_error",
]
HAS_KEYS = {
    "sensitivity": True,
    "precision": True,
    "f1_score": True,
    "accuracy": False,
    "specificity": False,
    "mean_squared_error": True,
    "median_absolute_error": True,
    "mean_absolute_error": True,
}
AVG = "average"
CLASS_MODES = {0: "rbf", 1: "knn"}

from library.models import Transform


class ClassMapException(Exception):
    pass


def get_input_contract(name):
    return Transform.objects.get(name=name).input_contract


def check_valid_input(input_contract, config):
    if input_contract.get("handle_by_set", False) is True:
        return {}

    if input_contract["name"] in config:
        return {input_contract["name"]: config[input_contract["name"]]}

    else:
        return {input_contract["name"]: input_contract["default"]}
        raise Exception("No Input for paramter {}".format(input_contract["name"]))


def make_tvo_config(step, c, v, o):

    tvo_config = step.copy()
    tvo_config.update(
        {
            # Properties of the classifier
            "optimizer": o["name"],
            "classifier": c["name"],
            # Properties of the validation method
            "validation_method": v["name"],
            "group_columns": v["inputs"].get("group_columns", []),
            # Properties of the set container
            "outputs": step.get("outputs", "tvo.{0}.{1}.{2}".format(c, v, o)),
            "ignore_columns": step.get("ignore_columns", []),
        }
    )

    optimizer_contract = get_input_contract(tvo_config["optimizer"])
    classifier_contract = get_input_contract(tvo_config["classifier"])
    validation_contract = get_input_contract(tvo_config["validation_method"])

    for input_contract in optimizer_contract:
        tvo_config.update(check_valid_input(input_contract, o["inputs"]))

    for input_contract in validation_contract:
        tvo_config.update(check_valid_input(input_contract, v["inputs"]))

    for input_contract in classifier_contract:
        tvo_config.update(check_valid_input(input_contract, c["inputs"]))

    # Make sure group_columns includes important metadata columns
    if "metadata_name" in tvo_config:
        tvo_config["group_columns"] = list(
            set(tvo_config["group_columns"]).union(set([tvo_config["metadata_name"]]))
        )

    tvo_config.pop("classifiers", None)
    tvo_config.pop("optimizers", None)
    tvo_config.pop("validation_methods", None)

    return tvo_config


def get_config_values(config, field):
    """
    Searches a dictionary or list of dictionaries, such as a pipeline or
    model generation config, for the search field key and constructs a flat
    list of all the values found for that key.
    """
    value_list = []

    if isinstance(config, list):
        for item in config:
            if isinstance(item, dict) or isinstance(item, list):
                more_results = get_config_values(item, field)
                for another_result in more_results:
                    value_list.append(another_result)
    elif isinstance(config, dict):
        for key, value in config.items():
            if key == field:
                value_list.append(value)
            elif isinstance(value, dict) or isinstance(value, list):
                results = get_config_values(value, field)
                for result in results:
                    value_list.append(result)

    return value_list


def remap_labels_to_integers(step, input_data):
    if step["optimizers"][0]["inputs"].get("class_map", None):
        original_map = step["optimizers"][0]["inputs"].get("class_map")

    else:
        label_column = step["label_column"]
        if input_data[label_column].dtype == "int64":
            labels = sorted(set(input_data[label_column].astype(int)))
        elif input_data[label_column].dtype == "float64":
            labels = sorted(set(input_data[label_column].astype(float)))
        else:
            labels = sorted(set(input_data[label_column]))
        original_map = {}
        value = 1
        for item in labels:
            original_map[item] = value
            value += 1

    reverse_map = {}
    for k, v in dict.items(original_map):
        reverse_map[v] = k

    return (original_map, reverse_map)


def replace_labels_in_input_data(original_map, label_column, input_data):
    input_data[label_column] = input_data[label_column].map(original_map)
    return input_data


def return_labels_to_original_values(model_set_stats, reverse_map):
    """Converts labels embedded in one set of model metrics from simulator integers to string label names.
    This depends on a standard of key names.

    Args:
        model_set_stats (dict): Container for model statistics with a specific format. If any key names change
        or if the type/format of the value changes this function will have to be updated.
        {
            "f1_score": {...},
            "y_pred": {...},
            "precision": {...},
            "ConfusionMatrix": {...},
            ...
        }
        reverse_map (dict): A map from integer labels to string label names. Keys can be ints or strings but
        should represent the simulator integer categories.
        {1: "Kick", 2: "Jump", 3: "Run"}
        {"1": "Kick", "2": "Jump", "3": "Run"}
    """
    list_entries_to_convert = ["y_pred", "y_true"]
    dict_entries_to_convert = [
        "ActualCategoryCounts",
        "RecognizedCategoryCounts",
        "f1_score",
        "precision",
        "positive_predictive_rate",
        "sensitivity",
    ]
    nested_dict_entries_to_convert = ["ConfusionMatrix"]

    # Convert everything in the reverse_map to strings to ensure JSON compatibility and add UNK category
    rm = {str(k): str(v) for k, v in reverse_map.items()}
    rm["0"] = "UNK"

    # Lists
    for metric in list_entries_to_convert:
        if model_set_stats.get(metric, None):
            model_set_stats[metric] = [rm[str(k)] for k in model_set_stats[metric]]

    # Dictionaries
    for metric in dict_entries_to_convert:
        if model_set_stats.get(metric, None):
            model_set_stats[metric] = {
                (rm[str(k)] if str(k) in rm.keys() else str(k)): v
                for k, v in model_set_stats[metric].items()
            }

    # Nested Dictionaries
    for metric in nested_dict_entries_to_convert:
        if model_set_stats.get(metric, None):
            model_set_stats[metric] = {
                (rm[str(k)] if str(k) in rm.keys() else str(k)): {
                    (rm[str(x)] if str(x) in rm.keys() else str(x)): y
                    for x, y in v.items()
                }
                for k, v in model_set_stats[metric].items()
            }

    return model_set_stats


def avg_validation_metrics(validation):
    """strip out the validation metrics and return the average"""

    avg_metrics = {}
    for key in METRICS:
        if validation.get(key, None):
            if validation[key].get("average", None):
                avg_metrics[key] = validation[key]["average"]
            else:
                avg_metrics[key] = np.nanmean(list(validation[key].values()))

    return avg_metrics


def parse_key_index(keys):
    """parses the key to strip out individual components in a dictionary"""

    key_index = {}
    for key in keys.split(", "):
        key_index[key.split(" ")[0]] = key.split(" ")[1]

    return key_index


def get_metric_matrix(results, defaults=None):
    """generates a dataframe from the results metrics"""

    defaults = defaults or {}
    result_matrix = []
    for key in results["models"].keys():
        result_row = {}
        result_row.update(defaults)
        result_row.update(parse_key_index(key))
        result_row.update(
            avg_validation_metrics(results["models"][key]["metrics"]["validation"])
        )
        result_matrix.append(result_row)

    return pd.DataFrame(result_matrix)


def get_metric_matrix_stats(result_matrices, group_columns=None):
    """returns the aggregate averages of each result metric"""
    group_columns = group_columns or []
    metric_columns = [x for x in METRICS if x in result_matrices.columns]
    groups = result_matrices[metric_columns + group_columns].groupby(group_columns)

    df1 = groups.agg(np.nanmean).reset_index()
    df2 = groups.agg(np.nanstd).reset_index()
    df2.rename(
        columns={
            col: "{}_std".format(col)
            for col in [c for c in df1.columns if not c in group_columns]
        },
        inplace=True,
    )
    ret = pd.merge(df1, df2, on=group_columns)

    ret.fillna(value=0, inplace=True)

    return ret


def handle_array_formatting(t):
    """this is a way to properly parse the dataframe sensor column loaded from the cache"""

    # This needs to be handled when we write the cached file instead of here

    # replace unicoded handle in the string if they are there
    return t.split(",")


def traverse(obj, path=None, callback=None):
    if path is None:
        path = []

    if isinstance(obj, dict):
        value = {str(k): traverse(v, path + [k], callback) for k, v in obj.items()}
    elif isinstance(obj, list):
        value = [traverse(elem, path + [[]], callback) for elem in obj]
    # convert ndarrays to regular lists so we can traverse them
    elif isinstance(obj, ndarray):
        if obj.dtype == int64:
            new_obj = obj.astype(int).tolist()
        elif obj.dtype in [float64, float32]:
            new_obj = obj.astype(float).tolist()
        else:
            new_obj = obj.tolist()

        value = [traverse(elem, path + [[]], callback) for elem in new_obj]
    else:
        value = obj

    if callback is None:  # if a callback is provided, call it to get the new value
        return value
    else:
        return callback(value, path)


def clean_results(obj):
    # Not using path in this function so set to None
    def transform(value, path=None):
        if isinstance(value, int64):
            value = value.astype(int)
        elif isinstance(value, float64):
            value = value.astype(float)

        # Convert NaN to float for JSON serialization
        if isinstance(value, float) and np.isnan(value):
            return None

        return value

    return traverse(obj, callback=transform)


def to_libsvm(df, label, name):
    """
    take a dataframe of feature columns and ending in a label where each feature vector is a value
    between 0-256 and convert that to libsvm format of floats between -1 and 1
    """
    df_records = df[df.columns[:-1]].to_records(index=False)
    tmp = []
    for record in df_records:
        # scale the 0-256 to a float between -1 and 1
        tmp.append(
            map(
                lambda x, y: "{}:{:1.6f}".format(y + 1, x / 128 - 1.0),
                record,
                range(len(record)),
            )
        )
    df_svlib = pd.DataFrame(tmp)
    df_svlib.insert(0, label, df.reset_index(drop=True)[label].astype(int))
    df_svlib.to_csv(name, index=None, header=None, sep=" ")


def from_libsvm(filename):
    """
    take a file in libsvm format and convert it to a dataframe with the
    """
    M = []
    with open(filename, "r") as fid:
        for line in fid.readlines():
            split = line.split(" ")
            tmp = {
                feature.split(":")[0]: feature.split(":")[1] for feature in split[1:-1]
            }
            tmp["label"] = split[0]
            M.append(tmp)

    return pd.DataFrame(M)


def vector_package_to_df(vector_pacakge):
    M = []
    for record in vector_pacakge:
        tmp = {index + 1: value for index, value in enumerate(record["Vector"])}
        tmp["label"] = record["Category"]
        M.append(tmp)

    return pd.DataFrame(M), "label"
