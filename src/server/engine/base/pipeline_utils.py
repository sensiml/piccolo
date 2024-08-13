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

import ast
import copy
import json
import logging
import os
from copy import deepcopy
from os.path import basename
from typing import List, Tuple
from uuid import uuid4

import numpy as np
import pandas as pd
from datamanager import utils
from datamanager.datasegments import DataSegments, dataframe_to_datasegments
from datamanager.featurefile import _get_featurefile_name, _get_featurefile_datastore
from datamanager.models import (
    Capture,
    CaptureConfiguration,
    CaptureLabelValue,
    FeatureFile,
    KnowledgePack,
    LabelValue,
    Query,
    Segmenter,
)
from datamanager.datastore import get_datastore, get_datastore_basedir
from datamanager.utils.file_reader import WaveFileReader, sanitize_fields
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist
from library.core_functions import MAX_INT_16, MIN_INT_16
from library.models import Transform
from logger.log_handler import LogHandler
from pandas import DataFrame, concat, read_csv
from scipy.signal import decimate

logger = LogHandler(logging.getLogger(__name__))


class FeatureFileError(Exception):
    pass


class NoInputDataStreamsError(Exception):
    pass


class FeatureSummaryException(Exception):
    pass


class NoSegmentationAlgorithmException(Exception):
    pass


class PipelineMergeException(Exception):
    pass


def make_summary(data, filename):

    summary = {"filename": filename}

    if isinstance(data, DataFrame):
        summary["total_feature_vectors"] = data.shape[1]
        summary["distribution_feature_vectors"] = (
            None
            if "Label" not in data.columns
            else data.groupby("Label").size().to_dict()
        )
        summary["type"] = "dataframe"

    if isinstance(data, list):
        summary.update(DataSegments(data).summary())
        summary["type"] = "datasegments"

    if isinstance(data, dict):
        summary["type"] = "dict"

    if isinstance(data, int):
        summary["total"] = data
        summary["type"] = "datasegments"

    return summary


def get_type_index(pipeline, step_type):
    """Return the first occurence of a step of type step_type"""
    try:
        return [i for i, val in enumerate(pipeline) if val["type"] == step_type][0]
    except:
        return None


def get_max_segment_length(step):
    for length_param in ["max_gesture_length_s", "window_size", "max_segment_length"]:
        if step["inputs"].get(length_param, None):
            if length_param == "max_gesture_length_s":
                return step["inputs"][length_param] * step["inputs"]["sample_rate"]
            else:
                return step["inputs"][length_param]
    else:
        return None


def get_group_columns(pipeline, project_id):
    if pipeline[0]["type"] == "query":
        q = Query.objects.get(name=pipeline[0]["name"], project__uuid=project_id)
        return ast.literal_eval(q.metadata_columns)

    if pipeline[0]["type"] == "featurefile":
        return pipeline[0]["group_columns"]

    if pipeline[0]["type"] == "datafile":
        return pipeline[0]["group_columns"]

    raise Exception("Unable to identify group columns")


def get_data_columns(pipeline, project_id):
    if pipeline[0]["type"] == "query":
        q = Query.objects.get(name=pipeline[0]["name"], project__uuid=project_id)
        return ast.literal_eval(q.columns)

    if pipeline[0]["type"] == "featurefile":
        return pipeline[0]["data_columns"]

    if pipeline[0]["type"] == "datafile":
        return pipeline[0]["data_columns"]


def make_recognition_pipeline(
    project,
    pipeline_summary,
    transform_summary,
    query_summary,
    feature_summary,
    segmenter=True,
    capture_configuration=None,
    **kwargs,
):
    """Makes a pipeline for recognition from the given model generation pipeline.

    This is a static method so the code generation module can use it."""

    def update_inputs(generator, original_inputs, new_inputs):
        for input_list in new_inputs:
            if set(generator["Sensors"]).intersection(
                set(input_list["columns"])
            ) == set(generator["Sensors"]):
                original_inputs.update(
                    {
                        k: v
                        for k, v in input_list.items()
                        if k not in ("columns", "group_columns")
                    }
                )

        return original_inputs

    original_pipeline = deepcopy(pipeline_summary)

    check_for_full_pipeline(original_pipeline, query_summary)

    # Remove training specific steps from the pipeline
    recognition_pipeline = [
        step
        for step in original_pipeline
        if step["type"]
        not in (
            "query",
            "featurefile",
            "selectorset",
            "sampler",
            "tvo",
            "capturefile",
            "datafile",
        )
    ]

    # Decide which segmenter to use, if any. This is complicated because it has to work for both cloud recognition,
    # where it is possible to not start with segmentation, and code gen where it isn't. The rules are:
    #
    #   1. Modify the pipeline segmenter if there is a defined segmenter argument
    #   2. Remove the pipeline segmenter if the segmenter argument is set to False
    #   3. If there isn't a pipeline segmenter, use the segmenter argument if provided
    #   4. If there is no pipeline segmenter or segmenter argument, look for a global project segmenter and use it
    #
    seg_index = get_type_index(recognition_pipeline, "segmenter")

    query_segmenter = False
    num_preprocess = 0
    # todo: pipeline orders itself by type order.
    if query_summary and query_summary.get("segmenter", None):
        if isinstance(query_summary["segmenter"], int):
            segmenter_obj = Segmenter.objects.filter(project__uuid=project.uuid).get(
                id=query_summary.get("segmenter")
            )
            if segmenter_obj.parameters:
                query_segmenter = json.loads(segmenter_obj.parameters)
                query_segmenter["outputs"] = ["temp.segmenter0"]
                query_segmenter["type"] = "segmenter"
                if segmenter_obj.preprocess:
                    num_preprocess = len(json.loads(segmenter_obj.preprocess).keys())
        else:
            segmenter_obj = query_summary["segmenter"]
            if segmenter_obj.get("parameters"):
                query_segmenter = segmenter_obj["parameters"]
                query_segmenter["outputs"] = ["temp.segmenter0"]
                query_segmenter["type"] = "segmenter"
                if segmenter_obj["preprocess"]:
                    num_preprocess = len(segmenter_obj["preprocess"].keys())

    if seg_index is not None:
        if isinstance(segmenter, bool) and not segmenter:
            recognition_pipeline.remove(recognition_pipeline[seg_index])
        elif isinstance(segmenter, dict):
            recognition_pipeline[seg_index] = segmenter
    elif isinstance(segmenter, dict):
        recognition_pipeline = [segmenter] + recognition_pipeline
    elif query_segmenter:
        recognition_pipeline.insert(num_preprocess, query_segmenter)

    # update the segmenter
    for step in recognition_pipeline:
        if step["name"] == "Windowing":
            step["inputs"]["train_delta"] = 0

    if not len(recognition_pipeline):
        return [], [], []

    # Set the first input variable and stitch the pipeline back together.

    recognition_pipeline[0]["inputs"]["input_data"] = "temp.raw"

    recognition_pipeline = make_pipeline_linear(recognition_pipeline)

    if feature_summary:
        features = DataFrame(feature_summary)
        if "GeneratorIndex" in features.columns and "ContextIndex" in features.columns:
            features = features.sort_values(
                by=["GeneratorIndex", "ContextIndex"]
            ).to_dict(orient="records")
        else:
            raise FeatureSummaryException(
                "The pipeline does not have a valid feature summary."
            )
    else:
        raise FeatureSummaryException(
            "The pipeline does not have a valid feature summary."
        )

    # Modify the generator set
    fg_index = get_type_index(recognition_pipeline, "generatorset")
    if fg_index:
        generator_set = recognition_pipeline[fg_index]
        genset_temp = generator_set["set"]
        generator_set["set"] = []

        for feature in features:
            # Get the input parameters for the feature
            inputs = {"columns": feature["Sensors"]}
            # Subtypes are not supported, only individual generators specified by name
            individual_inputs = []
            for gen_index, gen_temp in enumerate(genset_temp):
                if (
                    "function_name" in gen_temp
                    and gen_temp["function_name"] == feature["Generator"]
                ):
                    if gen_index == feature["GeneratorIndex"]:
                        individual_inputs.append(gen_temp["inputs"])

            inputs = update_inputs(feature, inputs, individual_inputs)

            # Append FG if it is not already present and add output index
            generators = [
                (g["function_name"], g["inputs"]) for g in generator_set["set"]
            ]
            feature_suffix = feature["Feature"].split("_")[-1]
            feature_index = int(feature_suffix) if feature_suffix.isdigit() else 0
            if (feature["Generator"], inputs) in generators:
                generator_to_update = next(
                    index
                    for (index, gen) in enumerate(generators)
                    if gen[0] == feature["Generator"] and gen[1] == inputs
                )
                if (
                    feature_index
                    not in generator_set["set"][generator_to_update]["outputs"]
                ):
                    generator_set["set"][generator_to_update]["outputs"].append(
                        feature_index
                    )
            else:
                generator_set["set"].append(
                    {
                        "function_name": feature["Generator"],
                        "inputs": inputs,
                        "outputs": [feature_index],
                    }
                )
                generator_set["set"][-1]["family"] = is_generator_family(
                    feature["Generator"], feature.get("LibraryPack", None)
                )

    transform_parameters = transform_summary

    # Insert stored transform variables
    for i in recognition_pipeline:
        if i["type"] == "transform" and transform_parameters:
            for parameter in transform_parameters:
                if i["name"] == parameter.get("function_name", None):
                    i["inputs"][parameter["parameter_name"]] = parameter[
                        "parameter_value"
                    ]

    sensor_columns, data_columns_ordered = get_sensor_data_columns(
        original_pipeline,
        recognition_pipeline,
        query_summary,
        feature_summary,
        capture_configuration,
    )

    return recognition_pipeline, sensor_columns, data_columns_ordered


def parse_recognition_pipeline(pipeline):
    pipeline_json = {
        "Sensor Transforms": [],
        "Sensor Filters": [],
        "Segmenter": None,
        "Segment Transforms": [],
        "Feature Generators": None,
        "Feature Transforms": [],
    }

    for step in pipeline:
        if is_transform(step["name"], "Transform", "Sensor"):
            pipeline_json["Sensor Transforms"].append(step)
        if is_transform(step["name"], "Transform", "Sensor Filter"):
            pipeline_json["Sensor Filters"].append(step)
        if is_transform(step["name"], "Transform", "Segment"):
            pipeline_json["Segment Transforms"].append(step)
        if is_transform(step["name"], "Transform", "Segment Filter"):
            pipeline_json["Segment Transforms"].append(step)
        if is_transform(step["name"], "Segmenter"):
            pipeline_json["Segmenter"] = step
        if step["type"] == "generatorset":
            pipeline_json["Feature Generators"] = step
        if is_transform(step["name"], "Transform", "Feature Vector"):
            pipeline_json["Feature Transforms"].append(step)

    return pipeline_json


def get_num_feature_banks(pipeline_json):
    #####
    # Logic for legacy reasons
    # 1. cascade reset is True when slide is False
    # 2. cascade reset is False when slide is True
    # 3. cascade reset is None when num_feature_banks is 1

    cleaned_pipeline_json = copy.deepcopy(pipeline_json)
    cascade_index = 0
    num_feature_banks = 1
    cascade_transform = False
    cascade_reset = None

    for index, transform in enumerate(pipeline_json["Feature Transforms"]):
        if transform["name"] == "Feature Cascade":
            cascade_index = index
            num_feature_banks = transform["inputs"].get("num_cascades", 1)
            cascade_transform = True
            slide = transform["inputs"].get("slide", True)

            if slide:
                cascade_reset = False
            else:
                cascade_reset = True

    if cascade_transform:
        cleaned_pipeline_json["Feature Transforms"].pop(cascade_index)

    if num_feature_banks == 1:
        cascade_reset = None

    return cleaned_pipeline_json, num_feature_banks, cascade_reset


def flatten_pipeline_json(pipeline_json):
    pipeline = []

    for step in pipeline_json["Sensor Transforms"]:
        pipeline.append(step)
    for step in pipeline_json["Sensor Filters"]:
        pipeline.append(step)
    if pipeline_json.get("Segmenter", None):
        pipeline.append(pipeline_json["Segmenter"])
    for step in pipeline_json["Segment Transforms"]:
        pipeline.append(step)
    if pipeline_json.get("Feature Generators", None):
        pipeline.append(pipeline_json["Feature Generators"])
    for step in pipeline_json["Feature Transforms"]:
        pipeline.append(step)

    return pipeline


def merge_sensor_columns(pipeline_names, pipelines):
    """checks that all pipeliens in a group use the same sensor inputs"""
    sensor_columns = pipelines[pipeline_names[0]]["sensor_columns"]
    for pipeline_name in pipeline_names:
        if sensor_columns != pipelines[pipeline_name]["sensor_columns"]:
            raise PipelineMergeException(
                "All pipelines in a group must use the same sensor columns"
            )
    return sensor_columns


def merge_data_streaming(pipeline_names, pipelines):
    """merges the data sterawming steps from multiple pipelines removing
    duplicate, creates a map for data columns for all pipelines in a group"""

    map_data_columns = {}
    # sensor columns are correctly sorted. lets get data columns sorted in the
    # same way
    sensor_columns = [x.upper() for x in pipelines[pipeline_names[0]]["sensor_columns"]]
    for sensor_column in sensor_columns:
        for pipeline_name in pipeline_names:
            if (
                sensor_column.upper() in pipelines[pipeline_name]["data_columns"]
                and sensor_column not in map_data_columns.keys()
            ):
                map_data_columns[sensor_column] = len(map_data_columns.keys())

    data_streaming_steps = []
    map_model_data_columns = {}
    for pipeline_name in pipeline_names:
        count = 0
        map_model_data_columns[pipeline_name] = {}
        for data_column in pipelines[pipeline_name]["data_columns"]:
            if data_column not in sensor_columns:
                step = pipelines[pipeline_name]["pipeline_json"]["Sensor Transforms"][
                    count
                ]
                if step not in data_streaming_steps:
                    data_streaming_steps.append(step)
                    # This still needs to be addressed somehow
                    if data_column in map_data_columns.keys():
                        raise PipelineMergeException(
                            "pipeline has different transforms with same names"
                        )
                    map_data_columns[data_column] = len(map_data_columns.keys())
                count += 1

            map_model_data_columns[pipeline_name].update(
                {data_column: map_data_columns[data_column]}
            )

    return data_streaming_steps, map_data_columns, map_model_data_columns


def make_pipeline_linear(pipeline):
    """return a pipeline that has been stitched together"""

    for i, step in enumerate(pipeline[:-1]):
        if "inputs" in pipeline[i + 1]:
            pipeline[i + 1]["inputs"]["input_data"] = step["outputs"][0]

        if "input_data" in pipeline[i + 1]:
            pipeline[i + 1]["input_data"] = step["outputs"][0]

    for i, step in enumerate(pipeline[:-1]):
        if "feature_table" in pipeline[i + 1]:
            if pipeline[i + 1]["feature_table"] is not None:
                pipeline[i + 1]["feature_table"] = step["outputs"][1]

        if "inputs" in pipeline[i + 1] and "feature_table" in pipeline[i + 1]["inputs"]:
            if pipeline[i + 1]["inputs"]["feature_table"] is not None:
                pipeline[i + 1]["inputs"]["feature_table"] = step["outputs"][1]

    return pipeline


def clean_feature_cascade(feature_summary):
    """Strip the cascade header from feature generator as it is generated again by feature cascade"""
    tmp_feature_summary = copy.deepcopy(feature_summary)
    for feature in tmp_feature_summary:
        if feature["Feature"][:5] == "gen_c":
            feature["Feature"] = feature["Feature"][10:]

    return tmp_feature_summary


def get_max_vector_size(neuron_array):
    max_vector = 0
    for neuron in neuron_array:
        if len(neuron["Vector"]) > max_vector:
            max_vector = len(neuron["Vector"])

    return max_vector


def is_generator_family(function_name, library_pack):
    try:
        transform = Transform.objects.get(name=function_name, library_pack=library_pack)
    except DoesNotExist:
        return None

    output_contract = transform.output_contract
    return output_contract[0].get("family", None)


def is_sensor_transform(function_name):
    try:
        transform = Transform.objects.get(name=function_name)
    except DoesNotExist:
        return False

    if transform.type == "Transform" and transform.subtype == "Sensor":
        return transform
    return False


def is_transform(function_name, transform_type, transform_subtype=None):
    try:
        transform = Transform.objects.get(name=function_name)
    except DoesNotExist:
        return False

    if (
        transform_subtype
        and transform.type == transform_type
        and transform.subtype == transform_subtype
    ):
        return True

    elif transform.type == transform_type and transform_subtype is None:
        return True

    return False


def get_segment_step(pipeline):
    for index, step in enumerate(pipeline):
        if step.get("type", None) == "segmenter":
            return index

    raise NoSegmentationAlgorithmException("Pipeline requires a segmentation")


def check_for_full_pipeline(original_pipeline, query_summary):
    # Get the Sensor Columns form the Pipeline Information
    if original_pipeline[0].get("type", None) == "query":
        pass
    elif original_pipeline[0].get("type", None) == "featurefile":
        if not original_pipeline[0]["data_columns"]:
            raise FeatureFileError(
                "Data columns to use must be specified in the pipeline."
            )
    elif original_pipeline[0].get("type", None) == "datafile":
        if not original_pipeline[0]["data_columns"]:
            raise FeatureFileError(
                "Data columns to use must be specified in the pipeline."
            )
    else:
        raise NoInputDataStreamsError(
            "Recognition can only be performed on pipelines with "
            + "queries or data files as the first step."
        )


def parse_capture_configuration(capture_configuration):
    sensor_columns = []
    for sensor in capture_configuration.configuration["capture_sources"][0]["sensors"]:
        if sensor["type"].lower() == "microphone":
            sensor_columns += [
                "channel_" + str(x) for x in range(sensor["column_count"])
            ]
        else:
            if sensor["column_names"]:
                sensor_columns += [sensor["type"] + x for x in sensor["column_names"]]
            else:
                sensor_columns += [sensor["type"]]

    return sensor_columns


def get_sensor_data_columns(
    original_pipeline,
    recognition_pipeline,
    query_summary,
    feature_summary,
    capture_configuration,
):
    # Get the Sensor Columns form the Pipeline Information
    sensor_columns = []

    if isinstance(capture_configuration, CaptureConfiguration):
        sensor_columns = parse_capture_configuration(capture_configuration)

    if not sensor_columns:
        if original_pipeline[0].get("type", None) == "query":
            sensor_columns = json.loads(query_summary["columns"])

        elif original_pipeline[0].get("type", None) == "featurefile":
            if original_pipeline[0]["data_columns"]:
                sensor_columns = original_pipeline[0]["data_columns"]

        elif original_pipeline[0].get("type", None) == "datafile":
            if original_pipeline[0]["data_columns"]:
                sensor_columns = original_pipeline[0]["data_columns"]

        else:
            raise NoInputDataStreamsError(
                "Recognition can only be performed on pipelines with "
                + "queries or data files as the first step."
            )

    if not sensor_columns:
        raise Exception(
            "Sensor columns are not defined. Define sensor columns using a capture configuration or set to Custom."
        )

    # Find which sensor columns are used in the pipeline
    data_columns = []
    single_columns_names = [
        "axis_of_interest",
        "column_of_interest",
        "input_column",
        "first_column_of_interest",
        "second_column_of_interest",
    ]
    multi_columns_names = ["columns_of_interest", "input_columns"]

    # Only include data columns for segmenter
    segment_step = get_segment_step(recognition_pipeline)
    step = recognition_pipeline[segment_step]
    for multi_columns_name in multi_columns_names:
        if step["inputs"].get(multi_columns_name, None):
            for column in step["inputs"][multi_columns_name]:
                data_columns.append(column.upper())
    for single_column_name in single_columns_names:
        if step["inputs"].get(single_column_name, None):
            data_columns.append(step["inputs"][single_column_name].upper())

    # Find which sensor columns are used by feature generators
    for fg in feature_summary:
        for column in fg["Sensors"]:
            data_columns.append(column.upper())

    # Make sure the data columns are ordered correctly
    data_columns_ordered = []
    for column in sensor_columns:
        if (
            column.upper() in data_columns
            and column.upper() not in data_columns_ordered
        ):
            data_columns_ordered.append(column.upper())

    # Generate the ordered list of sensor transforms
    transform_number = 0
    for step in recognition_pipeline:
        sensor_transform = is_sensor_transform(step["name"])
        if sensor_transform:
            data_columns_ordered.append(
                "{0}_ST_{1}".format(
                    sensor_transform.output_contract[0]["name"].upper(),
                    str("{}".format(transform_number)).zfill(4),
                )
            )
            transform_number += 1

    return sensor_columns, data_columns_ordered


def get_project_metadata(project):
    label_values = LabelValue.objects.filter(label__project=project).values(
        "label__name", "value"
    )
    label_values_dict = {}
    for lv in label_values:
        if lv["label__name"] not in label_values_dict:
            label_values_dict[lv["label__name"]] = [lv["value"]]
        else:
            label_values_dict[lv["label__name"]].append(lv["value"])

    return label_values_dict


def return_auto_query(project, sensors, label):
    metadata = get_project_metadata(project).keys()
    metadata_filter = "[{}]".format(label)
    if "SegmentID" in metadata:
        metadata_filter += " AND [SegmentID]"

    (query, created) = Query.objects.get_or_create(
        project=project,
        name="auto_{}".format(project.uuid),
        columns=json.dumps(sensors),
        metadata_columns=json.dumps(metadata),
        metadata_filter=metadata_filter,
    )
    return query


def replace_columns(step, inputs, value):
    for input in inputs:
        if input in step and not step[input]:
            step[input] = value
        if "inputs" in step and input in step["inputs"] and not step["inputs"][input]:
            step["inputs"][input] = value
        if "set" in step:
            for i in range(len(step["set"])):
                step["set"][i] = replace_columns(step["set"][i], inputs, value)

    return step


def insert_column_params(pipeline, data_columns, group_columns, label):
    new_pipeline = deepcopy(pipeline)
    for step in new_pipeline:
        step = replace_columns(step, ["columns"], data_columns)
        step = replace_columns(step, ["input_columns"], data_columns)
        step = replace_columns(
            step,
            ["group_columns", "ignore_columns", "passthrough_columns"],
            group_columns,
        )
        step = replace_columns(step, ["label_column"], label)

    return new_pipeline


def substitute_inputs(pipeline, params):
    new_pipeline = deepcopy(pipeline)
    for step in new_pipeline:
        if "inputs" in step:
            for key in step["inputs"].keys():
                if key in params:
                    step["inputs"][key] = params[key]
        if "set" in step:
            for set_item in range(len(step["set"])):
                for key in step["set"][set_item]["inputs"].keys():
                    if key in params:
                        step["set"][set_item]["inputs"][key] = params[key]

    return new_pipeline


def get_featurefile(user, project_uuid, filename):
    featurefile = FeatureFile.objects.with_user(
        user=user, project__uuid=project_uuid
    ).get(name=filename)

    datastore = _get_featurefile_datastore(featurefile)

    data = datastore.get_data(_get_featurefile_name(featurefile))

    return data, featurefile.uuid


def copy_querydata(query, query_partition, pipeline_id):

    querydata_dir = get_datastore_basedir(settings.SERVER_QUERY_ROOT)
    root_dir = get_datastore_basedir(settings.SERVER_CACHE_ROOT)

    datastore = get_datastore(folder=f"{querydata_dir}/{query.uuid}")

    datastore.copy_to_folder(
        key=query_partition,
        new_key=query_partition,
        new_directory=f"{root_dir}/{pipeline_id}",
    )


def reindex_recognize_file(
    capture_sizes: List[dict], result_list: List[dict]
) -> List[dict]:
    """When a file is run through the emulator it loses its indexing and capture specifications, this adds it back"""
    cumulative_size = 0

    result = DataFrame(result_list)
    capture_sizes[0]["index_start"] = 0
    result["Capture"] = None

    for index, capture in enumerate(capture_sizes):
        if (result.SegmentEnd > capture["number_samples"] + cumulative_size).any():
            capture["index_end"] = result[
                result.SegmentEnd > capture["number_samples"] + cumulative_size
            ].index[0]
        else:
            capture["index_end"] = result.index[-1] + 1

        if index > 0:
            capture["index_start"] = capture_sizes[index - 1]["index_end"]

        cumulative_size += capture["number_samples"]

    cumulative_size = 0
    for index, capture in enumerate(capture_sizes):
        start = capture["index_start"]
        end = capture["index_end"]

        result.loc[start:end, "SegmentStart"] -= cumulative_size
        result.loc[start:end, "SegmentEnd"] -= cumulative_size
        cumulative_size += capture["number_samples"]
        result.loc[start:end, "Capture"] = capture["capture"]

    return [x for x in result.to_dict(orient="records") if x["SegmentStart"] >= 0]


def get_capturefile_sizes(project_uuid: str, filenames: List[str]) -> List[dict]:
    if not isinstance(filenames, list):
        filenames = [filenames]

    cfs = capturefile = Capture.objects.filter(
        project__uuid=project_uuid, name__in=filenames
    )

    capture_sizes = []
    for filename in filenames:
        cf = cfs.get(name=filename)
        capture_sizes.append({"capture": cf.name, "number_samples": cf.number_samples})

    return capture_sizes


def get_capturefiles(user, project_uuid: str, filenames: List[str]) -> DataFrame:
    """

    Args:
        user (user): user object
        project_uuid (str): Project UUID
        filenames (List[str]): List of captures to look up

    Returns:
        DataFrame: concatenated DataFrame combining all the capture files
    """

    M = []

    if not isinstance(filenames, list):
        filenames = [filenames]

    for filename in filenames:
        data, _, sample_rate = get_capturefile(user, project_uuid, filename)
        M.append(data)

    return concat(M).reset_index(drop=True), sample_rate


def get_capturefile(user, project_uuid: str, filename: str) -> Tuple:
    """Gets a capturefile

    Args:
        user (user): user object
        project_uuid (str): Project UUID
        filename (str): capture filename to look up

    Raises:
        Capture.DoesNotExist: Raised when capture is not found

    Returns:
        Tuple: (DataFrame, uuid)
    """

    try:
        capturefile = Capture.objects.with_user(
            user=user, project__uuid=project_uuid
        ).get(name=filename)
    except Capture.DoesNotExist:
        raise Capture.DoesNotExist(
            "Capture {filename} does not exist.".format(filename=filename)
        )

    return extract_capture(capturefile, project_uuid)


####################################################################################


def decimate_signal(signal, in_sample_rate: int, out_sample_rate: int, type_int=True):
    """ "
    Downsample the signal after applying an anti-aliasing filter.
    """

    if in_sample_rate < out_sample_rate:
        raise ValueError("Input sample rate must be larger than output sample rate !")

    if in_sample_rate % out_sample_rate != 0:
        raise ValueError(
            "Input sampling rat ({}) must be divisible by the output sampling ({}) rate !".format(
                in_sample_rate, out_sample_rate
            )
        )

    if in_sample_rate > out_sample_rate:
        decimation_factor = in_sample_rate // out_sample_rate
        signal = decimate(signal, decimation_factor)

    if type_int:
        signal = convert_int16(signal)

    return signal


def normalize_signal(signal, rolling=50000):
    df = pd.DataFrame(np.abs(signal), columns=["audio"])
    df = (
        df.rolling(rolling, center=True)
        .max()
        .rolling(rolling, center=True)
        .mean()
        .rolling(rolling, center=True)
        .mean()
        .rolling(rolling, center=True)
        .mean()
        .rolling(rolling, center=True)
        .mean()
    )

    mean = np.nanmean(df.audio.values)

    return signal / mean


def rand_sample(audio, length: int, margin: int = 0):
    """
    Randomly selecting a portion of the input audio signal.

    Inputs:
        audio: 1D audio signal
        length: size of the output signal
        margin: the size of signal margin on both ends which is ignored prior to the random selection
    """

    N = len(audio)

    if length < 0 or margin < 0:
        raise ValueError(
            "Both length ({}) and margin ({}) must not be negative !".format(
                length, margin
            )
        )

    if N <= 2 * margin:
        raise ValueError(
            "Signal size ({}) is smaller than 2*margin ({}) !".format(N, 2 * margin)
        )

    if N < 2 * margin + length:
        raise ValueError(
            "Signal size ({}) can not be smaller than 2*margin+length ({}) !".format(
                N, 2 * margin + length
            )
        )

    be = np.random.randint(margin, N - margin - length + 1)
    en = be + length
    sample = audio[be:en]

    return sample


def factor_max_sample(signal, factor: float = 1.0, maximum=None):
    if factor > 1:
        signal = factor * signal

    if maximum:
        if type(maximum) == int and maximum > 0:
            signal[signal > maximum] = maximum
            signal[signal < -maximum] = -maximum
        else:
            raise ValueError("Maximum value of the signal must be a positive integer !")

    return signal


def convert_int16(signal):
    signal[signal > MAX_INT_16] = MAX_INT_16
    signal[signal < MIN_INT_16] = MIN_INT_16

    return signal.astype("int16")


def extract_background_signal(
    background_data,
    background_factor: float = 1.0,
    back_max_level=None,
    normalize: bool = False,
):
    signal = 0
    for col in background_data.columns:
        signal += background_data[col].values

    if normalize:
        signal = normalize_signal(signal)

    return factor_max_sample(signal, maximum=back_max_level, factor=background_factor)


def get_background(
    background_data,
    back_max_level=0,
    background_factor=1,
    normalize=False,
    sample_rate: int = 0,
    back_sample_rate: int = 0,
):
    background_signal = extract_background_signal(
        background_data, background_factor, back_max_level, normalize
    )

    if sample_rate > 0 and back_sample_rate > 0:
        background_signal = decimate_signal(
            background_signal, back_sample_rate, sample_rate
        )
        factor_max_sample(background_signal, maximum=back_max_level, factor=1.0)

    data_frame = pd.DataFrame(convert_int16(background_signal), columns=["channel_0"])

    return data_frame


def add_background(
    data_frame,
    capture_sizes,
    background_data,
    back_max_level=0,
    background_factor=1,
    audio_max_level=0,
    audio_factor=1,
    seed=0,
    back_margin=0,
    normalize=False,
    sample_rate: int = 0,
    back_sample_rate: int = 0,
):
    np.random.seed(seed)

    sizes = [capture["number_samples"] for capture in capture_sizes]

    background_signal = extract_background_signal(
        background_data, background_factor, back_max_level, normalize
    )

    if sample_rate > 0 and back_sample_rate > 0:
        background_signal = decimate_signal(
            background_signal, back_sample_rate, sample_rate
        )

    audio_length = data_frame.shape[0]

    for col in data_frame.columns:
        noisy_data = np.zeros(audio_length)
        be = 0

        for i, size in enumerate(sizes):
            en = be + size
            audio_seg = audio_factor * data_frame.iloc[be:en][col].values

            if audio_max_level > 0:
                mx = np.max(audio_seg)
                audio_seg = (1.0 * audio_max_level * audio_seg) / mx

            background = rand_sample(background_signal, size, margin=back_margin)
            noisy_data[be:en] = audio_seg + background

            be += size

        data_frame[col] = convert_int16(noisy_data)


def get_backgroundfile(filename: str) -> Tuple:
    """Gets a capturefile

    Args:
        filename (str): capture filename to look up

    Raises:
        BackgroundCapture.DoesNotExist: Raised when background capture is not found

    Returns:
        Tuple: (DataFrame, uuid)
    """

    BackgroundPrjUUID = settings.BACKGROUND_CAPTURE_PROJECT_UUID

    try:
        backgroundcapture = Capture.objects.get(name=filename)
    except Capture.DoesNotExist:
        raise Capture.DoesNotExist(
            "BackgroundCapture {filename} does not exist.".format(filename=filename)
        )

    return extract_capture(backgroundcapture, BackgroundPrjUUID)


####################################################################################


def extract_capture(capture, project_uuid):
    datastore = get_datastore(folder=f"capture/{project_uuid}")
    datastore.get(basename(capture.file), capture.file)

    # TODO: DATASTORE Make all part of the get_data
    if capture.format == ".csv":
        data = read_csv(capture.file)
    if capture.format == ".wav":
        data = WaveFileReader(capture.file)._dataframe
    if "sequence" in data.columns:
        data = data.drop("sequence", axis=1)

    if capture.number_samples is None:
        capture.number_samples = data.shape[0]
        capture.save()

    if datastore.is_remote:
        datastore.delete_local_copy(capture.file)

    return (
        data.rename(sanitize_fields(data.columns), axis=1),
        str(capture.uuid),
        capture.set_sample_rate,
    )


####################################################################################
def get_capturefile_labels(
    project_uuid: str,
    filenames: List[str],
    label: str,
    class_map: dict = None,
) -> List[dict]:
    def map_label(label, class_map):
        if not class_map:
            return label

        if label in class_map:
            return class_map[label]

        return label

    if not isinstance(filenames, list):
        filenames = [filenames]

    clvs = CaptureLabelValue.objects.select_related("label_value", "segmenter").filter(
        project__uuid=project_uuid, label__name=label, capture__name__in=filenames
    )

    sequence_dict = dict()
    for clv in clvs:
        sequence_start = clv.capture.max_sequence - clv.capture.number_samples
        sequence_dict[clv.capture.name] = sequence_start if sequence_start > 0 else 0

    data_labels = [
        {
            "Capture": clv.capture.name,
            "Label_Value": map_label(clv.label_value.value, class_map),
            "SegmentStart": clv.capture_sample_sequence_start
            - sequence_dict[clv.capture.name],
            "SegmentEnd": clv.capture_sample_sequence_end
            - sequence_dict[clv.capture.name],
            "Session": clv.segmenter.name,
        }
        for clv in clvs
    ]

    return data_labels


def get_recognize_confusion_matrix(
    predicted: DataFrame, ground_truth: DataFrame, filenames: list, class_map: dict
) -> dict:
    def get_ground_truth(df, session, capture):
        return df[(df["Session"] == session) & (df["Capture"] == capture)].to_dict(
            orient="records"
        )

    def get_predicted(df, capture):
        return df[(df["Capture"] == capture)].to_dict(orient="records")

    if not isinstance(filenames, list):
        filenames = [filenames]

    class_map["0"] = "Unknown"

    # make sure everyting is a string
    class_map = {k: str(v) for k, v in class_map.items()}

    ytick_labels = [str(class_map[x]) for x in sorted(class_map, key=lambda x: int(x))]
    confusion_matrix = {}

    if "Session" not in ground_truth.columns:
        return confusion_matrix

    for session in ground_truth.Session.unique():
        confusion_matrix[session] = {}
        for capture in filenames:
            gt = get_ground_truth(ground_truth, session, capture)
            pred = get_predicted(predicted, capture)
            confusion_matrix[session][capture] = compute_confusion_matrix(
                pred, gt, ytick_labels
            )

    return confusion_matrix


def get_empty_confusion_matrix(ytick_labels):
    tmp = {label_value: 0 for label_value in ytick_labels}
    tmp["GroundTruth_Total"] = 0
    return {label_value: tmp for label_value in ytick_labels}


def compute_confusion_matrix(
    predicted: List[dict], ground_truth: List[dict], ytick_labels: list
) -> dict:
    from sklearn.metrics import confusion_matrix

    if not predicted or not ground_truth:
        return get_empty_confusion_matrix(ytick_labels)

    df_gt = DataFrame(
        [
            ""
            for _ in range(
                max(ground_truth[-1]["SegmentEnd"], predicted[-1]["SegmentEnd"]) + 1
            )
        ],
        columns=["class"],
    )

    for segment in ground_truth:
        df_gt.loc[segment["SegmentStart"] : segment["SegmentEnd"]] = segment[
            "Label_Value"
        ]

    for segment in predicted:
        segment["Label_Value"] = df_gt.loc[
            segment["SegmentStart"] : segment["SegmentEnd"]
        ]["class"].mode()[0]

    combined = DataFrame(predicted)

    combined = combined[combined.Label_Value != ""].reset_index(drop=True)

    # TODO: Discuss a better way to handle this situation,  for now I think the best method is to return confusion matrix
    # if not set(combined["Label_Value"].values) <= set(ytick_labels):
    #    return get_empty_confusion_matrix(ytick_labels)
    ytick_labels = list(
        set(combined["Label_Value"].values.astype(str)).union(set(ytick_labels))
    )

    cm_array = confusion_matrix(
        combined["Label_Value"].astype(str),
        combined["ClassificationName"].astype(str),
        labels=ytick_labels,
    )

    df_cm = DataFrame(cm_array, index=ytick_labels, columns=ytick_labels)

    out_dict = df_cm.T.to_dict()
    gt_labels = [x["Label_Value"] for x in ground_truth]

    for ground_truth_label, predicted_labels in out_dict.items():
        predicted_labels["GroundTruth_Total"] = gt_labels.count(ground_truth_label)

    return out_dict


def get_featurefile_folder_path(project):
    feature_file_root = get_datastore_basedir(settings.SERVER_FEATURE_FILE_ROOT)
    if settings.USE_S3_BUCKET:
        return os.path.join(feature_file_root, str(project.uuid))
    else:
        folder_path = os.path.join(feature_file_root, str(project.uuid))
        utils.ensure_path_exists(feature_file_root)
        utils.ensure_path_exists(folder_path)
        return folder_path


def get_cache_path(pipeline_id):
    cache_root = get_datastore_basedir(settings.SERVER_CACHE_ROOT)
    if settings.USE_S3_BUCKET:
        return os.path.join(cache_root, pipeline_id)
    else:
        cache_path = os.path.join(cache_root, pipeline_id)
        utils.ensure_path_exists(cache_root)
        utils.ensure_path_exists(cache_path)
        return cache_path


def save_cache_as_featurefile(project, pipeline_id, filename, fmt, label_column):
    folder_path = get_featurefile_folder_path(project)
    cache_path = get_cache_path(pipeline_id)

    file_uuid = uuid4()
    feature_file = FeatureFile(
        uuid=file_uuid,
        project=project,
        name=str(file_uuid),
        format=fmt,
        is_features=True,
        path=folder_path,
        version=2,
        label_column=label_column,
    )
    feature_file.save()

    source_file_name = "{}{}".format(filename, "" if filename.endswith(fmt) else fmt)

    datastore = get_datastore(folder=cache_path)
    datastore.copy_to_folder(
        source_file_name,
        f"{feature_file.uuid}{fmt}",
        folder_path,
    )

    return feature_file


def save_featurefile(project, data, ext):
    folder_path = get_featurefile_folder_path(project)
    file_uuid = uuid4()
    file_name = "{}{}".format(file_uuid, ext)

    feature_file = FeatureFile(
        uuid=file_uuid,
        project=project,
        name=str(file_uuid),
        is_features=True,
        format=ext,
        path=folder_path,
        version=2,
    )
    feature_file.save()

    datastore = get_datastore(folder=folder_path)
    datastore.save_data(data, file_name, fmt=ext)

    return feature_file


def get_modified_class_map(knowledgepack, kb_description=None):
    """For some pipelines the ground truth has been modified as part of the pipeline,
    this returns a mapping between the modified values and the modificatiosn
    """

    if (kb_description is None) or (len(kb_description.keys()) == 1):
        # Single model
        modified_class_map = {v: v for k, v in knowledgepack.class_map.items()}
        for step in knowledgepack.pipeline_summary:
            if "Combine Labels" == step.get("name", None):
                for new_label, labels in step["inputs"]["combine_labels"].items():
                    for label in labels:
                        modified_class_map[label] = new_label

    else:
        # hierarchical model
        modified_class_map = {}
        for node in kb_description:
            uuid = kb_description[node]["uuid"]
            temp_kp = KnowledgePack.objects.get(uuid=uuid)
            class_map = temp_kp.class_map
            for _, v in class_map.items():
                if "combined_label_" not in v:
                    modified_class_map[v] = v

    return modified_class_map


def get_max_segment_size(step):
    ways_we_define_buffers = [
        "max_gesture_length_s",
        "window_size",
        "max_segment_length",
        "max_window_size",
    ]

    axis_buffer_size = 0
    for way in ways_we_define_buffers:
        if step["inputs"].get(way, None):
            if way == "max_gesture_length_s":
                axis_buffer_size = step["inputs"].get(way) * step["inputs"].get(
                    "sample_rate"
                )
            else:
                axis_buffer_size = step["inputs"].get(way)

    return axis_buffer_size


def check_and_convert_datasegments(input_data, step):
    if isinstance(input_data, list):
        return input_data

    if step.get("set", None) and not step["name"] == "generator_set":
        return input_data
    elif step.get("optimizers", None):
        return input_data

    elif step["name"] == "generator_set":
        group_columns = [
            x for x in step["inputs"]["group_columns"] if x in input_data.columns
        ]
        data_columns = [x for x in input_data.columns if x not in group_columns]

        return dataframe_to_datasegments(
            input_data, group_columns=group_columns, data_columns=data_columns
        )

    transform = Transform.objects.get(name=step["name"])
    if transform.subtype in ["Segment Filter", "Segment", "Sensor"]:
        group_columns = [
            x for x in step["inputs"]["group_columns"] if x in input_data.columns
        ]
        data_columns = [x for x in input_data.columns if x not in group_columns]

        return dataframe_to_datasegments(
            input_data, group_columns=group_columns, data_columns=data_columns
        )

    return input_data


def generate_feature_table(step):
    feature_table = []
    for index, name in enumerate(step["feature_columns"]):
        name_split = name.split("_")
        try:
            generator_index = int(name_split[name_split.index("gen") + 1])
        except:
            generator_index = index
        feature_dict = {}
        feature_dict["Feature"] = name
        feature_dict["Generator"] = name
        feature_dict["Category"] = None
        feature_dict["GeneratorIndex"] = generator_index
        feature_dict["GeneratorTrueIndex"] = index
        feature_dict["GeneratorFamilyIndex"] = (
            0 if not (name_split[-1]).isdigit() else int(name_split[-1])
        )
        feature_dict["ContextIndex"] = 0
        feature_dict["LibraryPack"] = None

        feature_table.append(feature_dict)

    return DataFrame(feature_table)
