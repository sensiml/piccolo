/*
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
*/

const FORM_INT_TYPE = "int";
const FORM_INT_16T_TYPE = "int16_t";
const FORM_NUMERIC_TYPE = "numeric";
const FORM_STRING_TYPE = "str";
const FORM_FLOAT_TYPE = "float";
const FORM_BOOLEAN_TYPE = "boolean";
const FORM_BOOL_TYPE = "bool";
const FORM_SELECT_TYPE = "select";
const FORM_MULTI_SELECT_TYPE = "list";
const FORM_RANGE_INT_TYPE = "range_int";
const FORM_RANGE_FLOAT_TYPE = "range_float";
const FORM_RANGE_MIN_MAX_TYPE = "min_max_int";
const FORM_RANGE_NUMERIC_TYPE = "range_numeric";

const FORM_DICT_MULTISELECT_TYPE = "dict_list";
const FORM_DICT_MULTISELECT_STR_TYPE = "dict_list_str";
const FORM_DICT_EDITABLE_LIST_TYPE = "dict_editable_list";
const FORM_DICT_EDITABLE_LIST_STR_TYPE = "dict_editable_list_str";
const FORM_EDITABLE_LIST_INT_TYPE = "editable_list_int";
const FORM_EDITABLE_LIST_FLOAT_TYPE = "editable_list_float";
const FORM_EDITABLE_LIST_STR_TYPE = "editable_list_str";

const FORM_TYPES = {
  FORM_INT_TYPE,
  FORM_INT_16T_TYPE,
  FORM_FLOAT_TYPE,
  FORM_NUMERIC_TYPE,
  FORM_STRING_TYPE,
  FORM_BOOLEAN_TYPE,
  FORM_BOOL_TYPE,
  FORM_SELECT_TYPE,
  FORM_MULTI_SELECT_TYPE,
  FORM_RANGE_INT_TYPE,
  FORM_RANGE_FLOAT_TYPE,
  FORM_RANGE_MIN_MAX_TYPE,
  FORM_RANGE_NUMERIC_TYPE,

  FORM_DICT_MULTISELECT_TYPE,
  FORM_DICT_MULTISELECT_STR_TYPE,
  FORM_DICT_EDITABLE_LIST_TYPE,
  FORM_DICT_EDITABLE_LIST_STR_TYPE,
  FORM_EDITABLE_LIST_INT_TYPE,
  FORM_EDITABLE_LIST_FLOAT_TYPE,
  FORM_EDITABLE_LIST_STR_TYPE,
};

export const NUMERIC_ARR = [
  FORM_TYPES.FORM_INT_TYPE,
  FORM_TYPES.FORM_INT_16T_TYPE,
  FORM_TYPES.FORM_NUMERIC_TYPE,
  FORM_TYPES.FORM_FLOAT_TYPE,

  FORM_RANGE_INT_TYPE,
  FORM_RANGE_FLOAT_TYPE,
  FORM_RANGE_NUMERIC_TYPE,
];

export default FORM_TYPES;
