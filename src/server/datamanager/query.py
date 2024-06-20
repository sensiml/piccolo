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

import binascii
import json
import logging
import os
import time
import wave
from copy import deepcopy

import datamanager.utils as utils
import numpy as np
from datamanager.datasegments import generate_segment_template
from datamanager.models import (
    Capture,
    CaptureLabelValue,
    CaptureMetadataValue,
    Label,
    Project,
    Query,
)
from datamanager.queryparser import VALUE_NOT_PRESENT, QueryParser
from datamanager.datastore import get_datastore, get_datastore_basedir
from datamanager.utils.file_reader import sanitize_fields
from django.conf import settings
from django.db import connection, transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import re_path as url
from drf_spectacular.utils import extend_schema, extend_schema_view
from logger.log_handler import LogHandler
from pandas import DataFrame, concat, read_csv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.urlpatterns import format_suffix_patterns

logger = LogHandler(logging.getLogger(__name__))

STATIC_METADATA_NAMES = ["capture_uuid", "segment_uuid"]


class QueryIsNotValidException(Exception):
    pass


def _check_parents(user, project_uuid):
    return Project.objects.with_user(user=user, uuid=project_uuid).exists()


def _locate_query(user, project_uuid, query_id=""):
    queries = Query.objects.with_user(user=user, project__uuid=project_uuid)
    return queries if query_id == "" else queries.get(uuid=query_id)


def _get_project(user, project_uuid):
    return Project.objects.with_user(user=user).get(uuid=project_uuid)


def query_to_df(cursor_id, query_type, session_id, query_string, query_params):
    logger.userlog(
        {
            "message": "Executing Query",
            "log_type": "{}ID".format(query_type),
            "UUID": session_id,
        }
    )

    """logger.debug(
        {
            "message": "Query String",
            "data": query_string,
            "log_type": "{}ID".format(query_type),
            "UUID": session_id,
        }
    )
    """

    logger.debug(
        {
            "message": "Query Params",
            "data": query_params,
            "log_type": "{}ID".format(query_type),
            "UUID": session_id,
        }
    )

    data_list = []
    start_time = time.time()

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(query_string, query_params)

        while True:
            cursor.execute("FETCH 100000 FROM cursor_{0}".format(cursor_id))
            results = cursor.fetchall()
            if not results:
                break

            data_list.append(
                DataFrame(
                    results, columns=[col[0] for col in cursor.description]
                ).fillna(VALUE_NOT_PRESENT)
            )

    execution_time = time.time()

    logger.userlog(
        {
            "message": "Data retrieved in {} sec".format(execution_time - start_time),
            "log_type": "{}ID".format(query_type),
            "UUID": session_id,
        }
    )

    if data_list:
        data = concat(data_list)
    else:
        data = DataFrame()

    if "segmentid" in data.columns:
        data["segmentid"] = data["segmentid"].astype(str)

    return data


def query_to_df_no_cursor(query_type, session_id, query_string, query_params):
    logger.userlog(
        {
            "message": "Executing Query",
            "log_type": "{}ID".format(query_type),
            "UUID": session_id,
        }
    )

    logger.debug(
        {
            "message": "Query Params",
            "data": query_params,
            "log_type": "{}ID".format(query_type),
            "UUID": session_id,
        }
    )

    start_time = time.time()

    with connection.cursor() as cursor:
        cursor.execute(query_string, query_params)

        results = cursor.fetchall()

        if len(results):
            data = DataFrame(
                results, columns=[col[0] for col in cursor.description]
            ).fillna(VALUE_NOT_PRESENT)
        else:
            data = DataFrame()

    execution_time = time.time()
    logger.userlog(
        {
            "message": "Data retrieved in {} sec".format(execution_time - start_time),
            "log_type": "{}ID".format(query_type),
            "UUID": session_id,
        }
    )

    if "segmentid" in data.columns:
        data["segmentid"] = data["segmentid"].astype(str)

    return data


def _make_query_map(schema, field="path"):
    """
    Searches a schema of type list or dictionary for dictionaries, possibly
    nested, that contain the search field and constructs a flat map of only
    those elements. It is set to search for the key 'path' by default.
    """
    query_map = []

    if isinstance(schema, list):
        for item in schema:
            if isinstance(item, dict) or isinstance(item, list):
                more_results = _make_query_map(item, field)
                for another_result in more_results:
                    query_map.append(another_result)
    elif isinstance(schema, dict):
        for key, value in schema.items():
            if key == field:
                query_map.append(schema)
            elif isinstance(value, dict) or isinstance(value, list):
                results = _make_query_map(value, field)
                for result in results:
                    query_map.append(result)

    return query_map


def _get_captures(user, project_uuid):
    return Capture.objects.with_user(user=user, project__uuid=project_uuid)


def _get_metadata_names(project):
    """Returns a list of all the unique metadata, eventmetadata, and eventlabel names associated with this project."""
    return set(
        [m.name for m in Label.objects.filter(project=project, metadata=True)]
        + STATIC_METADATA_NAMES
    )


def _get_label_names(project):
    """Returns a list of all the unique metadata, eventmetadata, and eventlabel names associated with events."""
    return set([m.name for m in Label.objects.filter(project=project, metadata=False)])


def _get_labelset(event_or_events, label_name):
    if type(event_or_events) == Capture:
        metadataset = CaptureLabelValue.objects.filter(
            capture=event_or_events, label__name=label_name, label__metadata=False
        )
    else:
        metadataset = CaptureLabelValue.objects.filter(
            capture__in=event_or_events, label__name=label_name, label__metadata=False
        )

    return metadataset


def _get_metadataset(event_or_events, metadata_name, metadata=True):
    if type(event_or_events) == Capture:
        metadataset = CaptureMetadataValue.objects.filter(
            capture=event_or_events, label__name=metadata_name, label__metadata=True
        )
    else:
        metadataset = CaptureMetadataValue.objects.filter(
            capture__in=event_or_events, label__name=metadata_name, label__metadata=True
        )
    for metadata in metadataset:
        if metadata.label.type == "integer":
            metadata.label_value.value = int(metadata.label_value.value)
        elif metadata.label.type == "float":
            metadata.label_value.value = float(metadata.label_value.value)

    return metadataset


def _get_labels(event_or_events, metadata_name):
    if type(event_or_events) == Capture:
        metadataset = CaptureLabelValue.objects.filter(
            capture=event_or_events, label__name=metadata_name, label__metadata=False
        )
    else:
        metadataset = CaptureLabelValue.objects.filter(
            capture__in=event_or_events,
            label__name=metadata_name,
            label__metadata=False,
        )

    return metadataset


def _validate_data_columns(column_names, schema):
    # Validate requested columns
    errors = []
    columns_in_schema = [c for c in schema] + ["SequenceID"]
    invalid_column_names = []
    for i, column in enumerate(column_names):
        if column not in columns_in_schema:
            invalid_column_names.append(i)
            column_names.pop(i)
            errors.append(
                "{0}: {1}".format(column, "Column not found in project schema")
            )
    return column_names, errors


def _get_row_memory_estimate(number_of_columns):
    return 8 * number_of_columns / 1e6


def get_capture_file(project_uuid: str, capture_file: str, ext: str) -> DataFrame:
    """
    Returns the capture as a dataframe

    Args:
        capture_name (str): name of capture

    """

    # TODO: DATASTORE Convert this to the datastore get_data
    datastore = get_datastore(folder=os.path.join("capture", str(project_uuid)))
    if datastore.is_remote:
        datastore.get("{}".format(os.path.basename(capture_file)), capture_file)

    if ext == ".csv":
        tmp_df = read_csv(capture_file, index_col="sequence")
    elif ext == ".wav":
        with wave.open(capture_file, "rb") as wave_reader:
            waveFrames = wave_reader.readframes(wave_reader.getnframes())
            waveData = np.fromstring(waveFrames, dtype=np.int16).reshape(
                (-1, wave_reader.getnchannels())
            )
            columns = [
                "channel_{}".format(i) for i in range(wave_reader.getnchannels())
            ]
            tmp_df = DataFrame(waveData, columns=columns).rename_axis(index="sequence")

    return tmp_df.rename(sanitize_fields(tmp_df.columns), axis=1)


def validate_query_capture_columns(query_columns, data_columns, capture):
    missing_columns = []
    for column in query_columns:
        if column not in data_columns:
            missing_columns.append(column)

    if missing_columns:
        raise ValueError(
            f"Sources *{', '.join(missing_columns)}* in query are not part of file {capture}."
        )


def query_driver_from_csv_to_datasegments(
    task_id, query_info, project_id, pipeline_id, exclude_metadata_value=None
):
    cached_df = None
    capture_index = "capture_file"
    query_data = []
    start_time = time.time()

    include_metadata = []
    for column in query_info["metadata"]:
        if exclude_metadata_value and column in exclude_metadata_value:
            continue
        include_metadata.append(column)

    for index, segment in enumerate(query_info["query_info"]):
        if cached_df != segment[capture_index]:
            capture_file_start_time = time.time()
            tmp_df = get_capture_file(
                project_uuid=project_id,
                capture_file=segment[capture_index],
                ext=segment["capture_format"],
            )

            validate_query_capture_columns(
                query_info["columns"],
                tmp_df.columns,
                os.path.basename(segment[capture_index]),
            )

            tmp_df = tmp_df[query_info["columns"]]

            logger.debug(
                {
                    "message": "CSV file {} retrieved in {} sec".format(
                        os.path.basename(segment[capture_index]),
                        time.time() - capture_file_start_time,
                    ),
                    "log_type": "PID",
                    "UUID": pipeline_id,
                    "task_id": task_id,
                    "project_uuid": project_id,
                }
            )

            cached_df = segment[capture_index]

        seg_dict = generate_segment_template()
        seg_dict["data"] = tmp_df.loc[
            segment["seg_start"] : segment["seg_end"]
        ].values.T.astype(np.int32)
        seg_dict["columns"] = tmp_df.columns.tolist()

        for column in include_metadata:
            seg_dict["metadata"][column] = segment[column]

        seg_dict["metadata"][query_info["label"]] = segment[query_info["label"]]

        seg_dict["metadata"]["segment_uuid"] = segment["segmentid"]

        seg_dict["metadata"]["SegmentID"] = query_info["segment_start"] + index
        seg_dict["statistics"]["length"] = segment["length"]

        if sum([x == 0 for x in seg_dict["data"].shape]) == 0:
            query_data.append(seg_dict)

    logger.userlog(
        {
            "message": "CSV Driver finished {} segments in {} sec".format(
                len(query_info["query_info"]), time.time() - start_time
            ),
            "log_type": "PID",
            "UUID": pipeline_id,
            "task_id": task_id,
            "project_uuid": project_id,
        }
    )

    return query_data


def partition_query(query):
    column_names = json.loads(query.columns)
    metadata_column_names = json.loads(query.metadata_columns)

    drop_capture_uuid = False
    if "capture_uuid" not in metadata_column_names:
        metadata_column_names.append("capture_uuid")
        drop_capture_uuid = True

    metadata_filter = query.metadata_filter

    row_memory_size = _get_row_memory_estimate(
        len(column_names) + len(metadata_column_names)
    )
    (column_names, errors) = _validate_data_columns(
        column_names, query.project.capture_sample_schema
    )
    query_parser = QueryParser(
        query.project,
        column_names,
        metadata_column_names,
        query.segmenter_id,
        query.label_column,
    )
    query_parser.parse(metadata_filter)

    query_string, query_params = query_parser.get_query_profile_string_with_cursor()

    profile_df = query_to_df(
        query_parser.cursor_id, "Q", query.uuid, query_string, query_params
    )

    #  Define partitions using the query profile
    group_template = {"memory_size": 0, "num_segments": 0, "segments": []}

    group_list = [deepcopy(group_template)]

    profile_groupby = profile_df.groupby("capture_id")

    for group_name, capture_group in profile_groupby:
        placed = False
        placed_index = None
        capture_group_num_segments = capture_group.shape[0]
        capture_group_memory_size = capture_group.length.sum() * row_memory_size
        for partition_index, partition in enumerate(group_list):
            if (
                not placed
                and partition["memory_size"] + capture_group_memory_size
                <= settings.SHARD_MEMORY_SPLIT_SIZE
                and partition["num_segments"] + capture_group_num_segments
                <= settings.SHARD_SEGMENT_SPLIT_SIZE
            ):
                placed = True
                placed_index = partition_index
                break

        if not placed:
            group_list.append(deepcopy(group_template))
            placed_index = -1
            # if row_memory_size >= settings.MAX_SHARD_MEMORY_SIZE:
            #    raise Exception("Cannot split the segment %s small enough to be processed.")

        group_list[placed_index]["memory_size"] += capture_group_memory_size
        group_list[placed_index]["num_segments"] += capture_group_num_segments
        group_list[placed_index]["segments"].extend(
            capture_group.to_dict(orient="records")
        )

    # Create capture_id filter for each partition.
    filter_list = [part["segments"] for part in group_list if part["segments"]]

    json.dump(filter_list, open("test2.json", "w"))

    return query_parser, filter_list, drop_capture_uuid


def make_statistics(
    captures, project, metadata_column_names=None, segmenter_id=None, events=True
):
    """Creates a data structure containing summary metadata statistics for each capture indicated.

    The argument metadata_column_names, when present, defines the metadata names to summarize. If it is not present,
    all metadata names will be used. For ranged metadata, the summary will consist of each possible name/value pair
    and the count of all metadata items with that combination. For non-ranged metadata, a single name/value pair is
    returned.
    """
    data = []
    label_columns = []
    if metadata_column_names is None:
        metadata_column_names = _get_metadata_names(project)

    metadata_columns = []

    # Determine the type of each metadata (simple or ranged)
    for metadata_column_name in metadata_column_names:
        _get_metadataset(captures, metadata_column_name)
        captures_with_metadata = Capture.objects.filter(
            capturemetadatavalue__label__name=metadata_column_name
        ).annotate(Count("capturemetadatavalue"))

        # If there is only one instance per file, treat as simple (a single column)
        instances_per_capture = [
            c.capturemetadatavalue__count for c in captures_with_metadata
        ]
        if instances_per_capture and max(instances_per_capture) <= 1:
            metadata_columns.append(metadata_column_name)

    label_column_names = _get_label_names(project)

    for label_column_name in label_column_names:
        if label_column_name == "SegmentID":
            continue
        labels = _get_labelset(captures, label_column_name)

        values = sorted(list(set([n.label_value.value for n in labels])))
        for value in values:
            label_columns.append({"name": str(label_column_name), "value": value})

    # Construct the file-level results
    for c in captures:
        file_object_data = {}
        file_object_data["event_labels"] = {}
        file_object_data["metadata"] = {}

        for metadata_column_name in metadata_columns:
            result = _get_metadataset(c, metadata_column_name)
            if result:
                file_object_data["metadata"][metadata_column_name] = result[
                    0
                ].label_value.value
            else:
                file_object_data["metadata"][metadata_column_name] = None

        if segmenter_id is not None:
            for column in label_columns:
                label_count = 0
                if column["name"] not in file_object_data["event_labels"]:
                    file_object_data["event_labels"][column["name"]] = []

                label_count = CaptureLabelValue.objects.filter(
                    capture=c,
                    label__name=column["name"],
                    label_value__value=str(column["value"]),
                    segmenter=segmenter_id,
                ).count()

                file_object_data["event_labels"][column["name"]].append(
                    {"value": column["value"], "count": label_count}
                )
        else:
            total_events = 0
            main_label_num = 0
            for column in label_columns:
                label_count = 0
                if column["name"] not in file_object_data["event_labels"]:
                    file_object_data["event_labels"][column["name"]] = []

                label_count = CaptureLabelValue.objects.filter(
                    capture=c,
                    label__name=column["name"],
                    label_value__value=str(column["value"]),
                ).count()

                if events:
                    file_object_data["event_labels"][column["name"]].append(
                        {"value": str(column["value"]), "count": label_count}
                    )
                else:
                    if file_object_data.get("main_label", None) is None:
                        file_object_data["main_label"] = None

                    if label_count > main_label_num:
                        main_label_num = label_count
                        file_object_data["main_label"] = str(column["value"])

                total_events += label_count

            file_object_data["total_event_count"] = total_events

        file_object_data["capture_name"] = c.name
        file_object_data["capture_uuid"] = c.uuid
        data.append(file_object_data)

    return data


def _get_project_statistics(user, project_uuid, query_id="", events=True):
    captures = _get_captures(user, project_uuid)
    project = _get_project(user, project_uuid)
    metadata_column_names = None
    segmenter_id = None

    return make_statistics(
        captures, project, metadata_column_names, segmenter_id, events=events
    )


def _get_query_segment_statistics(user, project_uuid, query_id, query=None):
    if query is None:
        query = _locate_query(user, project_uuid, query_id)
        if query.segment_info is not None:
            return query.segment_info

    label_column = query.label_column
    metadata_column_names = json.loads(query.metadata_columns)
    metadata_columns_no_label = [m for m in metadata_column_names if m != label_column]
    metadata_filter = query.metadata_filter
    segmenter_id = query.segmenter_id

    if not segmenter_id:
        raise QueryIsNotValidException(
            "The label session for this query has been deleted. Update the query with a new session to continue using it."
        )

    q = QueryParser(
        query.project,
        [],
        metadata_column_names,
        segmenter_id=segmenter_id,
        label=label_column,
    )

    q.parse(metadata_filter)

    query_string, query_params = q.get_query_stats_string_with_cursor()

    data = query_to_df(q.cursor_id, "Q", query_id, query_string, query_params)

    if data.shape[0] == 0:
        return []

    return (
        data.rename(columns={"capture": "Capture", "length": "Segment Length"})
        .sort_values(by=["Capture", "segstart", "Segment Length"])
        .to_dict(orient="list")
    )


def _compute_statistics(df_segment_info, label_column):
    return {
        "samples": df_segment_info.groupby(label_column)["Segment Length"]
        .sum()
        .to_dict(),
        "segments": {
            x[0]: int(x[1])
            for x in zip(
                df_segment_info.groupby(label_column).count().index,
                df_segment_info.groupby(label_column)["Segment Length"].count().values,
            )
        },
        "total_segments": df_segment_info.shape[0],
    }


def _get_query_summary_statistics(user, project_uuid, query_id, query=None):
    if query is None:
        query = _locate_query(user, project_uuid, query_id)
        if query.summary_statistics is not None:
            return query.summary_statistics

    df_segment_info = DataFrame(
        _get_query_segment_statistics(user, project_uuid, query_id, query=query)
    )

    if df_segment_info.shape[0] == 0:
        return None

    return _compute_statistics(df_segment_info, query.label_column)


def _check_query_cache_up_to_date(user, project_uuid, query_id):
    query = _locate_query(user, project_uuid, query_id)

    if query.segment_info is None:
        return {
            "message": "This query has not been cached.",
            "status": None,
            "build_status": query.task_status,
        }

    try:
        df_segment_info = _get_query_segment_statistics(
            user, project_uuid, query_id, query=query
        )
    except QueryIsNotValidException as errot_msg:
        # send to the api only known errors
        return {
            "message": str(errot_msg),
            "status": False,
            "build_status": "FAILED",
        }

    if df_segment_info == query.segment_info:
        return {
            "message": "The query cache is up to date with the project data.",
            "status": True,
            "build_status": query.task_status,
        }

    return {
        "message": "Project sensor data has changed since the last time this query was built. Rebuild your query if you want the latest changes reflected in your training data.",
        "status": False,
        "build_status": query.task_status,
    }


def query_data_describe(query, pipeline_id=None):
    """
    TODO: Implement this as part of the query creation
    """


@extend_schema_view(
    get=extend_schema(
        summary="Get detailed project statistics",
        description="Returns a dictionary containing summary metadata statistics for each capture in the project",
        tags=["project"],
    ),
)
@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def project_statistics_api(request, project_uuid):
    if request.method == "GET":
        try:
            get_events = request.data.get("events", True)
        except:
            get_events = True
        data = _get_project_statistics(request.user, project_uuid, events=get_events)

        return HttpResponse(data, content_type="application/json")


@extend_schema_view(
    get=extend_schema(
        summary="Get detailed query segment statistics",
        description="Returns a dictionary containing summary statistics about each segment in the query",
    ),
)
@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def query_segment_statistics_api(request, project_uuid, query_id):
    if request.method == "GET":
        data = utils._jsonify_output(
            _get_query_segment_statistics(request.user, project_uuid, query_id)
        )

        return HttpResponse(data, content_type="application/json")


@extend_schema_view(
    get=extend_schema(
        summary="Get detailed query statistics",
        description="Returns a dictionary containing summary statistics about the query",
    ),
)
@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def query_summary_statistics_api(request, project_uuid, query_id):
    if request.method == "GET":
        data = utils._jsonify_output(
            _get_query_summary_statistics(request.user, project_uuid, query_id)
        )

        return HttpResponse(data, content_type="application/json")


@extend_schema_view(
    get=extend_schema(
        summary="Checks if the cached query matches the current project",
        description="Returns information about the query cache being up to do date with the project",
    ),
)
@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def query_summary_cache_up_to_date(request, project_uuid, query_id):
    if request.method == "GET":
        data = utils._jsonify_output(
            _check_query_cache_up_to_date(request.user, project_uuid, query_id)
        )

        return HttpResponse(data, content_type="application/json")


@extend_schema_view(
    get=extend_schema(
        summary="Returns the data from the query cache by partion",
        description="Returns a .gz file containing the cached query data for the specified partition",
    ),
)
@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def query_data_api(request, project_uuid, query_id, partition_id=0):
    partition_id = int(partition_id)

    if request.method == "GET":
        query = _locate_query(request.user, project_uuid, query_id)

        if query.cache is None:
            raise Exception("Query cache has not been created yet.")
        if partition_id < 0:
            raise Exception("Must be greater than 0")
        if partition_id >= len(query.cache):
            raise Exception(
                "Partition {partition_id} does not exist".format(
                    partition_id=partition_id
                )
            )

        datastore = get_datastore(bucket=settings.AWS_S3_BUCKET)

        file_path = os.path.join(
            get_datastore_basedir(settings.SERVER_QUERY_ROOT),
            str(query_id),
            query.cache[partition_id][1],
        )

        # TODO: DATASTORE put this functionality into the datastore directly
        if datastore.is_remote:
            return redirect(datastore.get_url(file_path))
        else:
            with open(file_path, "rb") as f:
                returndata = binascii.hexlify(f.read())

            response = HttpResponse(str(returndata), content_type="application/gzip")
            response["Content-Disposition"] = 'attachment; filename="%s"' % query.name

            return response


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^project/(?P<project_uuid>[^/]+)/query/(?P<query_id>[^/]+)/data/(?P<partition_id>[^/]+)$",
            query_data_api,
            {},
            name="query-data",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/query/(?P<query_id>[^/]+)/statistics/$",
            query_segment_statistics_api,
            {},
            name="query-statistics",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/query/(?P<query_id>[^/]+)/cache-status/$",
            query_summary_cache_up_to_date,
            {},
            name="query-cache-status",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/query/(?P<query_id>[^/]+)/summary-statistics/$",
            query_summary_statistics_api,
            {},
            name="query-summary-statistics",
        ),
        url(
            r"^project/(?P<project_uuid>[^/]+)/statistics/$",
            project_statistics_api,
            {},
            name="project-statistics",
        ),
    ]
)
