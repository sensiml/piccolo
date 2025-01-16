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

/* eslint-disable no-unused-vars */
import _ from "lodash";
import { selectedCaptureMetadataUUID } from "store/captureMetadata/selectors";

const getCaptureLabelsRequestData =
  (captureUUID, labelUUID, updatedLabelData, deletedLabels) => (state) => {
    /**
     * @params {Object} updatedLabelData
     * @params {Object} deletedLabels
     * @return - [requestDataToCreate, requestDataToUpdate, requestDataToDelete]
     */
    // const labelValuesToUpdate = state.captures.

    const getDataObj = (labelEl) => {
      return {
        capture: captureUUID,
        ...(!labelEl.isCreated && { uuid: labelEl.id }), // uuid only for updated
        label: labelUUID,
        label_value: labelEl.labelValueUUID,
        capture_sample_sequence_start: labelEl.start,
        capture_sample_sequence_end: labelEl.end,
      };
    };

    // labelEl.isCreated
    const requestDataToUpdate = [];
    const requestDataToCreate = [];
    let requestDataToDelete = [];

    requestDataToDelete = deletedLabels.filter((id) => !updatedLabelData[id]?.isCreated);

    _.values(updatedLabelData).forEach((labelEl) => {
      if (labelEl.isCreated && !deletedLabels.includes(labelEl.id)) {
        requestDataToCreate.push(getDataObj(labelEl));
      } else if (!labelEl.isCreated) {
        requestDataToUpdate.push(getDataObj(labelEl));
      }
    });

    return [requestDataToUpdate, requestDataToCreate, requestDataToDelete];
  };

export default getCaptureLabelsRequestData;
