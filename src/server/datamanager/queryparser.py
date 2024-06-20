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
import re
from uuid import uuid4

from datamanager.exceptions import QueryFormatError
from datamanager.models import Label, Segmenter

VALUE_NOT_PRESENT = "-1"
OPERATORS = ["=", ">", "<", ">=", "<=", "<>", "!=", "in", "IN"]

logger = logging.getLogger(__name__)

STATIC_METADATA_NAMES = ["capture_uuid", "segment_uuid"]


class InvalidParameterException(Exception):
    pass


class QueryParser(object):
    """Base class for metadata queries.

    Handles the logic of parsing and constructing a series of SQL query strings based on a filter string of the form:

        [label_descriptor_or_metadata_name] < [value] AND [label_2] <> [value2]

    where the standard SQL comparison operators are available (<> is 'not equal'). Symbol operators: =, <, >, >=, <=,
    <>, !=, in, IN.
    """

    def __init__(self, project, columns=[], metadata=[], segmenter_id=None, label=""):
        self._project_id = project.id
        self._matches = []
        self._columns = [col for col in columns if col != "SequenceID"]
        self._metadata = [m for m in metadata if m not in [label, "segment_uuid"]]
        self._label = label
        self._schema = project.capture_sample_schema
        self._labels = Label.objects.filter(project=project, metadata=False)
        self._metadataset = Label.objects.filter(project=project, metadata=True)
        self._parsed = False
        self._query = ""
        self._segment_uuid = ["segment_uuid"] if "segment_uuid" in metadata else []

        self._errors = []
        self.cursor_id = str(uuid4()).replace("-", "")

        # validate the segmenter id is part of this project
        if segmenter_id:
            segmenters = self._get_segmenters(segmenter_id, self._project_id)
            self._segmenter_ids = [segmenter.id for segmenter in segmenters]
            if len(self._segmenter_ids) == 0:
                raise InvalidParameterException("segmenter is not part of project")

        # Columns have been validated against the schema, we should probably sanitize them with a character whitelist too
        column_format = ', "{}"' * len(self._columns)
        column_format.format(*self._columns)

        self._select_string_columns = (
            ["capture_id", "seg_start", "seg_end"]
            + self._metadata
            + ["segment_uuid", self._label]
        )

        self._select_string = """ SELECT segments.capture_id, segments.seg_start, segments.seg_end, {METADATA COLUMNS} SegmentID, "{LABEL NAME}" FROM """

        self._select_decribe_string = """ SELECT {DATA DESCRIBE} FROM """

        self._select_segments = """(SELECT capture_id, capture_sample_sequence_start as seg_start, capture_sample_sequence_end as seg_end, label_value_id,
                                             clv.uuid as SegmentID, l.name as seg_label, lv.value as "{LABEL NAME}", clv.segmenter_id FROM datamanager_capturelabelvalue as clv
                                   LEFT JOIN datamanager_label as l on l.id = clv.label_id
                                   LEFT JOIN datamanager_labelvalue as lv on lv.id = clv.label_value_id
                                   WHERE clv.project_id= {PROJECT ID} AND l.name = '{LABEL NAME}' and clv.segmenter_id = {SEGMENTER ID} {LABEL SELECT}
                                   ) as segments
                                """

        self._select_summary = """SELECT CAPTURE, {METADATA COLUMNS} "{LABEL NAME}", Length, SegStart FROM
                                    (SELECT c.name as CAPTURE, capture_id,  clv.capture_sample_sequence_start as SegStart, (clv.capture_sample_sequence_end - clv.capture_sample_sequence_start + 1) as LENGTH,
                                            label_value_id, clv.uuid as seg_id, l.name, lv.value as "{LABEL NAME}",
                                            clv.uuid as SegmentID FROM datamanager_capturelabelvalue as clv
                                     LEFT JOIN datamanager_capture as c on c.id = clv.capture_id
                                     LEFT JOIN datamanager_label as l on l.id = clv.label_id
                                     LEFT JOIN datamanager_labelvalue as lv on lv.id = clv.label_value_id
                                     WHERE clv.project_id= {PROJECT ID} AND l.name = '{LABEL NAME}' and clv.segmenter_id = {SEGMENTER ID} {LABEL SELECT}
                                   ) as segments
                                """

        self._select_profile = """SELECT segments.capture_id, capture_file, capture_format, {METADATA COLUMNS} "{LABEL NAME}", SegmentID, seg_start, seg_end, Length FROM
                                    (SELECT capture_id, clv.capture_sample_sequence_end as seg_end, clv.capture_sample_sequence_start as seg_start, 
                                    (clv.capture_sample_sequence_end - clv.capture_sample_sequence_start + 1) as LENGTH,
                                            label_value_id, clv.uuid as seg_id, l.name, lv.value as "{LABEL NAME}",
                                            clv.uuid as SegmentID FROM datamanager_capturelabelvalue as clv
                                     LEFT JOIN datamanager_label as l on l.id = clv.label_id
                                     LEFT JOIN datamanager_labelvalue as lv on lv.id = clv.label_value_id
                                     WHERE clv.project_id= {PROJECT ID} AND l.name = '{LABEL NAME}' and clv.segmenter_id = {SEGMENTER ID} {LABEL SELECT}
                                   ) as segments
                                """

    @property
    def return_segment_uuid(self):
        return True if self._segment_uuid else False

    @property
    def matches(self):
        """A list of matches generated by the :func:`parse` method."""
        return self._matches

    @property
    def parsed(self):
        """An indication whether the :func:`parse` method has been executed."""
        return self._parsed

    @property
    def errors(self):
        """A list of errors generated by the :func:`parse` method."""
        return self._errors

    def get_query_string(self):
        """Returns a SQL string for capture sample and metadata selection.

        Constructs an SQL query string using the values extracted using the parse method.
        Uses the _select_string and _sub_select_string attributes and _where_clause_exists
        and _where_clause_comparison methods to construct the query, using INTERSECT to join
        the select statements. It then joins the requested metadata columns to the base query.

        Returns:
             The generated SQL query and list parameters for safe raw execution
        """
        assert self._parsed

        select_dict = {
            "LABEL NAME": self._label,
            "METADATA COLUMNS": (",".join(escape_strings(self._metadata)) + ",")
            if self._metadata
            else "",
        }

        query_string = self._select_string.format(**select_dict)

        segment_dict = {
            "PROJECT ID": self._project_id,
            "LABEL NAME": self._label,
            "SEGMENTER ID": self._segmenter_ids[0],
            "LABEL SELECT": self._get_metadata_select(self._label),
        }

        query_string += self._select_segments.format(**segment_dict)

        # Add metadata joins
        for index, metadata in enumerate(self._metadata):
            query_string += self.join_metadata(index, metadata)

        return query_string, self._metadata_params

    def get_query_capture_partitions_string(self, capture_partitions):
        """Returns a SQL string selecting segments"""
        assert self._parsed

        select_dict = {
            "LABEL NAME": self._label,
            "METADATA COLUMNS": (",".join(escape_strings(self._metadata)) + ",")
            if self._metadata
            else "",
        }

        query_string = self._select_string.format(**select_dict)

        segment_dict = {
            "PROJECT ID": self._project_id,
            "LABEL NAME": self._label,
            "SEGMENTER ID": self._segmenter_ids[0],
            "LABEL SELECT": self._get_metadata_select(self._label),
        }

        segment_dict["LABEL SELECT"] += " AND  capture_id IN ({})".format(
            ",".join(map(lambda x: str(x), capture_partitions))
        )
        query_string += self._select_segments.format(**segment_dict)

        # Add metadata joins
        for index, metadata in enumerate(self._metadata):
            query_string += self.join_metadata(index, metadata, no_filter=True)

        return query_string, self._metadata_params

    def get_query_profile_string(self):
        """Returns a SQL string for metadata group selection with sample counts.

        Constructs an SQL query string using the values extracted using the parse method.
        Uses the _select_string and _sub_select_string attributes and _where_clause_exists
        and _where_clause_comparison methods to construct the query, using INTERSECT to join
        the select statements. It then joins the requested metadata columns to the base query.

        Returns:
             The generated SQL query and list parameters for safe raw execution
        """
        assert self._parsed

        select_profile_dict = {
            "PROJECT ID": self._project_id,
            "LABEL NAME": self._label,
            "SEGMENTER ID": self._segmenter_ids[0],
            "LABEL SELECT": self._get_metadata_select(self._label),
            "METADATA COLUMNS": (",".join(escape_strings(self._metadata)) + ",")
            if self._metadata
            else "",
        }

        query_string = self._select_profile.format(**select_profile_dict)

        # Add metadata joins
        for index, metadata in enumerate(self._metadata):
            query_string += self.join_metadata(index, metadata)

        self.all_column_names = (
            ["capture_id", "SequenceID"]
            + self._columns
            + self._metadata
            + ["SegmentID", self._label]
            + self._segment_uuid
        )

        return query_string, self._metadata_params

    def get_query_stats_string(self):
        """Returns a SQL string for metadata group selection with sample counts.

        Constructs an SQL query string using the values extracted using the parse method.
        Uses the _select_string and _sub_select_string attributes and _where_clause_exists
        and _where_clause_comparison methods to construct the query, using INTERSECT to join
        the select statements. It then joins the requested metadata columns to the base query.

        Returns:
             The generated SQL query and list parameters for safe raw execution
        """
        assert self._parsed

        select_summary_dict = {
            "PROJECT ID": self._project_id,
            "LABEL NAME": self._label,
            "SEGMENTER ID": self._segmenter_ids[0],
            "LABEL SELECT": self._get_metadata_select(self._label),
            "METADATA COLUMNS": (",".join(escape_strings(self._metadata)) + ",")
            if self._metadata
            else "",
        }

        query_string = self._select_summary.format(**select_summary_dict)

        # Add metadata joins
        for index, metadata in enumerate(self._metadata):
            query_string += self.join_metadata(index, metadata)

        return query_string, self._metadata_params

    def _get_segmenters(self, segmenter_id, project_id):
        segmenter = Segmenter.objects.get(pk=segmenter_id, project__pk=project_id)
        children = Segmenter.objects.filter(parent=segmenter)
        segmenters = [segmenter]
        if len(children):
            segmenters += children

        return segmenters

    def get_query_string_with_cursor(self):
        (query_string, query_params) = self.get_query_string()
        return (
            "DECLARE cursor_{0} CURSOR FOR {1}".format(self.cursor_id, query_string),
            query_params,
        )

    def get_query_stats_string_with_cursor(self):
        (query_string, query_params) = self.get_query_stats_string()
        return (
            "DECLARE cursor_{0} CURSOR FOR {1}".format(self.cursor_id, query_string),
            query_params,
        )

    def get_query_profile_string_with_cursor(self):
        (query_string, query_params) = self.get_query_profile_string()
        return (
            "DECLARE cursor_{0} CURSOR FOR {1}".format(self.cursor_id, query_string),
            query_params,
        )

    def get_query_capture_partitions_string_with_cursor(self, capture_partitions):
        (query_string, query_params) = self.get_query_capture_partitions_string(
            capture_partitions
        )
        return (
            "DECLARE cursor_{0} CURSOR FOR {1}".format(self.cursor_id, query_string),
            query_params,
        )

    def get_query_size_string(self):
        """Returns a SQL string for query size calculation.

        Constructs an SQL query string using the values extracted using the parse method.
        Uses the _select_string and _sub_select_string attributes and _where_clause_exists
        and _where_clause_comparison methods to construct the query, using INTERSECT to join
        the select statements. It then counts the rows on the server side so minimal data is
        returned.

        Returns:
             The generated SQL query and list parameters for safe raw execution
        """

    def get_capture_query_string(self):
        """Returns a SQL string for capture selection (for query statistics call).

        Constructs an SQL query string using the values extracted during the parse method.
        Uses the _capture_select_string and _capture_sub_select_string attributes and
        _where_clause_exists and _where_clause_comparison methods to construct the query,
        using INTERSECT to join the select statements.

        Returns:
            The generated SQL query and list parameters for safe raw execution
        """

    def join_capture_uuid(self, index):
        metadata_dict = {
            "METADATA INDEX": index,
            "PROJECT ID": self._project_id,
            "METADATA SELECT": self._get_metadata_select("capture_uuid", "c.uuid"),
        }

        capture_uud_join = """ JOIN (SELECT c.id, c.uuid as capture_uuid, c.format as capture_format, c.file as capture_file FROM datamanager_capture as c
                                    WHERE c.project_id = {PROJECT ID} {METADATA SELECT})
                                    as md{METADATA INDEX} on md{METADATA INDEX}.id = segments.capture_id
                                """.format(
            **metadata_dict
        )

        return capture_uud_join

    def join_metadata(self, index, metadata_name, no_filter=False):

        if metadata_name == "capture_uuid":
            return self.join_capture_uuid(index)

        if metadata_name == "label_uuid":
            return ""

        metadata_type = self._metadataset.get(name=metadata_name).type

        if metadata_type == "integer":
            casted_value = "CAST(COALESCE(NULLIF(REGEXP_REPLACE(lv.value, '[^0-9]+', '', 'g'), ''), '0') AS INTEGER) as {METADATA NAME}"

        elif metadata_type == "float":
            casted_value = "CAST(COALESCE(NULLIF(REGEXP_REPLACE(lv.value, '[^0-9\.]+', '', 'g'), ''), '0') AS DOUBLE PRECISION) as {METADATA NAME}"
        else:
            casted_value = "lv.value as {METADATA NAME}"

        casted_value = casted_value.format(
            **{"METADATA NAME": '"{}"'.format(metadata_name)}
        )

        metadata_dict = {
            "METADATA SELECT": self._get_metadata_select(metadata_name),
            "CASTED VALUE": casted_value,
            "METADATA NAME": metadata_name,
            "METADATA INDEX": index,
            "PROJECT ID": self._project_id,
        }

        if no_filter:
            metadata_dict["METADATA SELECT"] = ""

        join_clause = """ JOIN (SELECT capture_id, label_value_id, clv.uuid, l.name, {CASTED VALUE} FROM datamanager_capturemetadatavalue as clv
                                    LEFT JOIN datamanager_label as l on l.id = clv.label_id
                                    LEFT JOIN datamanager_labelvalue as lv on lv.id = clv.label_value_id
                                    WHERE clv.project_id= {PROJECT ID} AND l.name = '{METADATA NAME}' {METADATA SELECT} )
                                    as md{METADATA INDEX} on md{METADATA INDEX}.capture_id = segments.capture_id
                                """.format(
            **metadata_dict
        )

        return join_clause

    def _get_metadata_select(self, metadata_name, column_name="lv.value"):

        metadata_filters = self._matches.get(metadata_name, [])

        metadata_select_string = ""

        for index, metadata in enumerate(metadata_filters):
            if metadata["symbol"] in ["in", "IN"]:
                metadata_select_string += "AND {} = ANY(%({}{})s)".format(
                    column_name, metadata_name, index
                )
            else:
                metadata_select_string += (
                    "AND "
                    + column_name
                    + " "
                    + metadata["symbol"]
                    + " %({}{})s".format(metadata_name, index)
                )
            self._metadata_params["{}{}".format(metadata_name, index)] = metadata[
                "value"
            ]

        return metadata_select_string

    def _check_number(self, value):
        try:
            float(value)
        except:
            raise QueryFormatError(
                "Cannot cast filter value to a number: {0}".format(value)
            )
        return True

    def _validate_match(self, match_dict):
        """Checks the filter condition format. Will either return True or throw a QueryFormatError."""
        # Verify the column name exists
        if (
            match_dict["key"]
            not in list(self._schema.keys())
            + [l.name for l in self._metadataset]
            + [l.name for l in self._labels]
            + STATIC_METADATA_NAMES
        ):
            raise QueryFormatError(
                "Column name not found in project: {0}".format(match_dict["key"])
            )
        # Verify the operator symbol is valid
        if "symbol" in match_dict and match_dict["symbol"] not in OPERATORS:
            raise QueryFormatError(
                "Cannot apply query filter with unknown operator: {0}".format(
                    match_dict["symbol"]
                )
            )
        # Verify numerical value(s)
        if "value" in match_dict:
            # Multiple values for the IN/in operator are comma separated
            values = match_dict["value"].split(",")
            values = [v.strip().rstrip() for v in values]
            if len(values) > 1 and match_dict["symbol"] not in ["in", "IN"]:
                raise QueryFormatError(
                    "List can only be applied filtered when using an IN operator"
                )
            for value in values:
                if match_dict["key"] in list(self._schema.keys()):
                    self._check_number(value)
                elif match_dict["key"] in [l.name for l in self._labels]:
                    if self._labels.get(name=match_dict["key"]).type in (
                        "integer",
                        "float",
                    ):
                        self._check_number(value)
            match_dict["value"] = values

        return True

    # This will work with AND and is compatible with all the logical operators supported by metadata_filter

    def parse(self, query):
        """
        Takes a filter string of the form:
        [metadata_name] < [value] AND [label_2] <> [value2]
        and extracts out:
            'metadata_name' and 'label_2' as keys,
            '<' and '<>' as symbols, and
            'value' and 'value2' as values
        These will be used by the _where_clause_exists and _where_clause_comparison methods to create SQL where clauses.
        :return: whether the filter string was successfully parsed using the approved format
        """
        returnvalue = True
        self._matches = {}
        self._query = query
        self._metadata_params = {}
        queries = query.split(" AND ")

        for i, q in enumerate([query for query in queries if len(query)]):
            # Should match queries like '[Subject] AND [Age < 40.0]' and '[Lack of Arm Swing (Extension)_LT] <> [0]'
            match = re.search(
                r"\[(?P<key>[0-9A-Za-z_\-\. \)\(]+)\]([ ]*(?P<symbol>[\>\=|\<\=|\=|\<\>|\>|\<|in|IN|!=]+)[ ]*\[(?P<value>.+)\])?",
                str(q),
            )
            if match is not None:
                match_dict = match.groupdict()
                # Symbol and value are optional, so the groups may not exist.
                if not match_dict["symbol"]:
                    match_dict.pop("symbol", None)
                    match_dict.pop("value", None)
                if self._validate_match(match_dict):
                    key = match_dict["key"]
                    if self._matches.get(key):
                        self._matches[key].append(match_dict)
                    else:
                        self._matches[key] = [match_dict]
                    returnvalue &= True
            else:
                logger.warn("No matches found in query.")
                if q:
                    self._errors.append(
                        'There was a problem parsing filter "{0}".'.format(q)
                    )
                returnvalue &= False
        self._parsed = returnvalue

        return self._matches


def escape_strings(values):
    if isinstance(values, list):
        return ['"{}"'.format(x) for x in values]

    if isinstance(values, str):
        return ['"{}"'.format(values)]
