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

import _ from "lodash";

import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { FORM_TYPES } from "consts";
import { sortAlphabeticallyAsc } from "utils";

export const selectMetadata = (uuid) => (state) => {
  if (!_.isEmpty(state.metadata?.data)) {
    return state.metadata?.data.find((el) => el.uuid === uuid) || {};
  }
  return {};
};

export const selectedMetadataNames = (state) => {
  if (!_.isEmpty(state.metadata?.data)) {
    return state.metadata?.data.map((el) => el.name);
  }
  return [];
};

export const selectMetadataFormData = (state) => {
  if (!_.isEmpty(state.metadata?.data)) {
    return state.metadata?.data.map((el) => ({
      ...el,
      label_values: !_.isEmpty(el?.label_values)
        ? el.label_values.sort((a, b) => sortAlphabeticallyAsc(a.value, b.value))
        : [],
    }));
  }
  return [];
};

export const selectMetadataTableData = (state) => {
  if (!_.isEmpty(state.metadata?.data)) {
    return state.metadata?.data.map((el) => ({
      ...el,
      label_values: !_.isEmpty(el?.label_values)
        ? el.label_values.sort((a, b) => sortAlphabeticallyAsc(a.value, b.value))
        : [],
    }));
  }
  return [];
};

export const selectMetadataTableColumnData = (state) => {
  if (!_.isEmpty(state.metadata?.data)) {
    return state.metadata?.data
      .filter((metadata) => metadata?.metadata)
      .map((metadata) => ({
        title: metadata?.name,
        field: metadata?.name,
        lookup: _.isArray(metadata.label_values)
          ? metadata.label_values.reduce((acc, el) => {
              acc[el.value] = el.value;
              return acc;
            }, {})
          : [],
        formType: metadata.is_dropdown ? FORM_TYPES.FORM_SELECT_TYPE : FORM_TYPES.FORM_STRING_TYPE,
        sortable: true,
        filterable: true,
        type: ColumnType.Text,
      }));
  }
  return [];
};

export const selectedMetadataSampleRate = (state) => {
  if (selectedMetadataNames(state).includes("Sample Rate")) {
    const sampleRateObj = state.metadata?.data.find((el) => el.name === "Sample Rate");
    if (!_.isEmpty(sampleRateObj?.label_values)) {
      return _.toSafeInteger(sampleRateObj.label_values[0]?.value);
    }
    return null;
  }
  return null;
};
