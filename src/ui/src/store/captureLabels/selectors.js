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
import { selectDefaultSessionData } from "store/sessions/selectors";
import { selectDefaultLabelData } from "store/labels/selectors";
import { getColorByIndex } from "store/labels/domain";

export const selectCaptureLabels = (state) => (sessionUUID, labelUUID) => {
  if (!_.isEmpty(state.captureLabels?.data)) {
    const defaultSessionUUID = sessionUUID || _.toString(selectDefaultSessionData(state)?.id);
    const defaultLabelUUID = labelUUID || selectDefaultLabelData(state)?.uuid;

    const labelValuesHashMap = state.labels?.data.reduce((acc, label) => {
      if (!_.isEmpty(label?.label_values)) {
        label.label_values.forEach((labelValue, labelValueIndex) => {
          if (!_.isEmpty(labelValue)) {
            acc[labelValue.uuid] = { ...labelValue, labelValueIndex };
          }
        });
      }
      return acc;
    }, {});

    return state.captureLabels.data
      .filter(
        (el) => _.toString(el.segmenter) === defaultSessionUUID && el.label === defaultLabelUUID,
      )
      .sort((a, b) => a.capture_sample_sequence_start - b.capture_sample_sequence_end)
      .map((el, elIndex) => {
        const labelValue = labelValuesHashMap[el.label_value];

        return {
          start: el.capture_sample_sequence_start,
          end: el.capture_sample_sequence_end,
          color:
            getColorFromDCLFormat(labelValue.color) || getColorByIndex(labelValue.labelValueIndex),
          name: labelValuesHashMap[el.label_value]?.value || "",
          labelValueUUID: el.label_value,
          sequence: _.add(elIndex, 1),
          id: el?.uuid || _.uniqueId(),
        };
      });
  }
  return [];
};
