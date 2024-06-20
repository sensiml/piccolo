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

import { getColorFromDCLFormat } from "utils";

export const selectLabelValuesColors = (labelName) => (state) => {
  const label = state.labels?.data.find((el) => el.name === labelName);
  if (label && !_.isEmpty(label?.label_values)) {
    return label.label_values.reduce((acc, labelVal) => {
      acc[labelVal.value] = getColorFromDCLFormat(labelVal?.color);
      return acc;
    }, {});
  }
  return {};
};

export const selectLabelByName = (name) => (state) => {
  return state.labels?.data.find((el) => el.name === name);
};

export const selectLabelValuesByName = (name) => (state) => {
  const label = selectLabelByName(name)(state);
  if (label && !_.isEmpty(label?.label_values)) {
    return label.label_values.map((el) => el.value);
  }
  return [];
};

export const selectLabel = (labelUUID) => (state) => {
  return state.labels?.data.find((el) => el.uuid === labelUUID);
};

export const selectSelectedLabelData = (state) => {
  const selectedLabel = state.labels?.selectedLabelUUID;
  if (selectedLabel) {
    return state.labels?.data.find((el) => el.uuid === selectedLabel);
  }
  return undefined;
};

export const selectDefaultLabelData = (state, name = "Label") => {
  if (!_.isEmpty(state.labels?.data)) {
    let defaultLabel = state.labels?.data.find((el) => el.name === name);
    if (!defaultLabel && !_.isEmpty(state.labels?.data)) {
      defaultLabel = state.labels?.data[0];
    }
    return defaultLabel;
  }
  return {};
};

export const setSelectedLabelUUID = (state) => {
  const selectedLabel =
    selectLabel(state.labels?.selectedLabelUUID)(state) || selectDefaultLabelData(state);
  if (!_.isEmpty(selectedLabel)) {
    return selectedLabel.uuid;
  }
  return "";
};

export const selectLabelValues = (labelUUID) => (state) => {
  const label = selectLabel(labelUUID)(state) || selectDefaultLabelData(state);
  if (!_.isEmpty(label?.label_values)) {
    return label.label_values.map((el) => ({
      uuid: el.uuid,
      name: el.value,
      color: getColorFromDCLFormat(el.color),
    }));
  }
  return [];
};

export const selectLabelValuesHashMap = () => (state) => {
  if (!_.isEmpty(state.labels?.data)) {
    //
    return state.labels.data.reduce((acc, label) => {
      //
      if (!_.isEmpty(label?.label_values)) {
        label.label_values.forEach((el) => {
          acc[el.uuid] = {
            name: el.value,
            color: getColorFromDCLFormat(el.color),
          };
        });
        return acc;
      }
      return {};
    }, {});
  }
  return {};
};

export const selectLabelTableValues = () => (state) => {
  const labels = state.labels?.data;

  if (!_.isEmpty(labels)) {
    return labels.reduce((acc, label) => {
      if (!_.isEmpty(label.label_values)) {
        label.label_values.forEach((el) => {
          acc.push({
            label: label.name,
            labelUUID: label.uuid,
            uuid: el.uuid,
            name: el.value,
            created: el.created_at,
            updated: el.last_modified,
            color: getColorFromDCLFormat(el.color),
          });
        });
      }
      return acc;
    }, []);
  }
  return [];
};
