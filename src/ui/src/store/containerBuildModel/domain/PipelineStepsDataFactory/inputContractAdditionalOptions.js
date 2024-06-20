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

/*
is_ignored - totaly igrore
is_hidden - hide from user, but use with default value
lookup - to handle dynamic options

query_columns" columns at query
query_metadata_columns - metadata columns at query
query_label_column - label_column at query
query_combine_labels - combine_labels at query
label_values - label_values at labels
metadata_names - list of names from metadata array
metadata_label_values - list of values from metadata object
*/

export const QUERY_COLUMNS = "query_columns";
export const QUERY_METADATA_COLUMNS = "query_metadata_columns";
export const QUERY_LABEL_COLUMN = "query_label_column";
export const QUERY_COMBINE_COLUMNS = "query_combine_labels";
export const LABEL_VALUES = "label_values";
export const FILTERING_LABEL_VALUES = "metadata_label_values";
export const METADATA_NAMES = "metadata_names";
export const METADATA_LABEL_VALUES = "metadata_label_values";
export const SAMPLE_RATE = "sample_rate";

export const constContracts = {
  QUERY_COLUMNS,
  QUERY_METADATA_COLUMNS,
  QUERY_LABEL_COLUMN,
  QUERY_COMBINE_COLUMNS,
  LABEL_VALUES,
  FILTERING_LABEL_VALUES,
  METADATA_NAMES,
  METADATA_LABEL_VALUES,
  SAMPLE_RATE,
};

export default {
  // default value
  // segmenter
  window_size: {
    defaultLookup: SAMPLE_RATE,
  },
  delta: {
    defaultLookup: SAMPLE_RATE,
  },
  train_delta: {
    default_use_param: false,
  },
  // tranform
  input_data: {
    is_ignored: true,
  },
  feature_min_max_parameters: {
    is_hidden: true,
    default: {},
  },
  feature_min_max_defaults: {
    default_use_param: false,
  },
  feature_pca_components: {
    lookup: "????",
    is_hidden: true,
    is_ignored: true, // tmp
  },
  coefficients: {
    lookup: "????",
    is_hidden: true,
    is_ignored: true, // tmp
  },
  query_columns: {
    lookup: "query_columns",
  },
  input_columns: {
    lookup: "query_columns",
  },
  input_column: {
    lookup: "query_columns",
  },
  group_columns: {
    lookup: "query_metadata_columns",
    is_hidden: true,
  },
  passthrough_columns: {
    lookup: "query_metadata_columns",
    is_hidden: true,
  },
  column_of_interest: {
    lookup: "query_columns",
  },
  columns_of_interest: {
    lookup: "query_columns",
  },
  first_column_of_interest: {
    lookup: "query_columns",
  },
  second_column_of_interest: {
    lookup: "query_columns",
  },
  // augmentration && feature selector
  label_column: {
    lookup: "query_label_column",
    is_hidden: true,
  },
  target_labels: {
    lookup: FILTERING_LABEL_VALUES,
  },
  target_sensors: {
    lookup: "query_columns",
  },
  // sampler
  combine_labels: {
    lookup: FILTERING_LABEL_VALUES,
  },
  filtering_label: {
    lookup: FILTERING_LABEL_VALUES,
  },
  feature_columns: {
    lookup: "????",
    is_hidden: true,
  },
  metadata_name: {
    lookup: "metadata_names",
  },
  metadata_values: {
    lookup: FILTERING_LABEL_VALUES,
  },
  // feature generator
  columns: {
    lookup: "query_columns",
  },
  pre_specified_bins: {
    lookup: "????",
    is_ignored: true, // tmp
  },
  // optimizer
  ignore_columns: {
    lookup: "query_columns",
  },
  // sampler
};
