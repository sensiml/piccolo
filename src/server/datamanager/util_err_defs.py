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

from datetime import datetime

from rest_framework.exceptions import ParseError


class ErrorCategories:
    """Categories for error messages"""

    contract = "Contract Error: "
    fileOps = "File Operation Error: "
    schema = "Schema Error: "
    general = "General Error: "
    database = "Database Error: "
    project = "Project Error: "
    metadata = "Metadata Error: "
    eventlabel = "Event Label Error: "
    event = "Event Error: "
    sandbox = "Sandbox Error: "
    query = "Query Error: "
    feature = "Feature File Error: "
    function = "Function Error: "
    knowledgepack = "KnowledgePack Error: "


class ErrorDefaults:
    category_default = ErrorCategories.general
    err_default = "Unspecified Error has occurred."
    extra_default = "Occurred on " + str(datetime.now()) + ": "


class ContractDirection:
    """Direction for Contract related errors"""

    dir_input = "Input"
    dir_output = "Output"


class CodebookErrors:
    code_no_retrieve = "Unable to retrieve code information "
    code_not_found = "Could not find code with ID "
    code_not_saved = "Could not insert code "


class ContractErrors:
    type_mismatch = "Type Mismatch: "
    contract_parse_fail = "Contract Parsing Failure: "
    value_out_of_range = "Value Out of Range: "
    wrong_number_inputs = "Wrong number of inputs: "


class EventErrors:
    event_no_file = "Unable to find file for event "
    event_fil_info_rtrv_fail = "Unable to retrieve event file information "
    event_info_rtrv_fail = "Unable to retrieve event information "
    event_not_found = "Couldn't find event with ID "
    event_not_deleted = "Event not deleted: "


class FeatureErrors:
    feature_no_file = "Unable to find file for features "
    feature_fil_info_rtrv_fail = "Unable to retrieve feature file data "
    feature_info_rtrv_fail = "Unable to retrieve feature file information "
    feature_not_found = "Couldn't find feature file with ID "
    feature_not_deleted = "Feature file not deleted: "


class EventLabelErrors:
    label_not_found = "Unable to retrieve event label information "
    label_remove_err = "Error removing label "


class FileErrors:
    fil_no_write = "Could not write data "
    fil_no_read = "Could not read data "
    fil_no_open = "Could not open file "
    fil_not_found = "File not found "
    fil_inv_path = "Invalid path to object "
    fil_no_store = "Data could not be stored "
    fil_name_not_in_header = "File name not in HTTP header "
    fil_no_delete = "Error deleting file from disk "


class GeneralErrors:
    non_unique_id = "Object already exists, choose a different name \
for insertion (POST) or use update (PUT)."


class KnowledgePackErrors:
    kp_not_found = "Knowledgepack not found "
    kp_no_retrieve = "Unable to retrieve Knowledgepack information "
    kp_invalid_format = "Knowledgepack data is formatted incorrectly "
    kp_no_delete = "Knowledgepack not deleted: "
    kp_pipeline_fail = "Knowledgepack pipeline execution failure "
    kp_binary_fail = "Knowledgepack Binary generation failed."
    kp_sketch_fail = "Knowledgepack Sketch generation failed."


class MetaDataErrors:
    metadata_not_found = "Metadata could not be found for "
    metadata_no_retrv = "Metadata could not be retrieved "
    metadata_no_remove = "Metadata could not be removed "
    metadata_exists = "Metadata already exists. Use PUT to update "


class ProjectErrors:
    proj_not_found = "Project could not be found with ID "
    proj_data_format = "Project data format is incorrect "


class QueryErrors:
    query_invalid_format = "Query data is formatted incorrectly "
    query_not_found = "Query data could not be found for ID "
    query_no_retrieve = "Unable to retrieve query information "
    query_no_delete = "Query not deleted: "


class SandboxErrors:
    sandbox_no_retrieve = "Unable to retrieve sandbox information "
    sandbox_not_found = "Could not find sandbox with ID "
    sandbox_invalid_format = "Sandbox data is formatted incorrectly "
    sandbox_no_delete = "Sandbox not deleted: "
    sandbox_pipeline_fail = "Sandbox pipeline execution failure "
    sandbox_reco_fail = "Sandbox recognition failure "


class SchemaErrors:
    schema_not_found = "Could not find the schema "
    schema_incorrect = "Schema formatted incorrectly "
    schema_read_new = "Error reading new schema data "
    schema_no_retrieve = "Unable to retrieve schema information "
    schema_no_update = "Error updating type schema "


class FunctionErrors:
    function_no_file = "Unable to find file for function "
    function_fil_info_rtrv_fail = "Unable to retrieve function file information "
    function_info_rtrv_fail = "Unable to retrieve function information "
    function_not_found = "Could not find function with the given function_name "
    function_execute_failed = "Function execution failed "
    function_no_modify = "Function cannot be modified "


class AdminErrors(object):
    class ActivationNotFound(ParseError):
        default_detail = "Activation key is expired, or is invalid."
