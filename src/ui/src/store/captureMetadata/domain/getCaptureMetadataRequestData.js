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
import { selectedCaptureMetadataUUID } from "store/captureMetadata/selectors";

const getCaptureMetadataFormData = (state, captureUUIDs, capturesMetadata) => {
  /**
   * @return - [requestDataToUpdate, requestDataToCreate, requestDataToDelete]
   */
  const requestDataToUpdate = [];
  const requestDataToCreate = [];
  const requestDataToDelete = [];

  _.forEach(captureUUIDs, (captureUUID) => {
    _.entries(capturesMetadata).forEach(([labelUUID, labelValueUUID]) => {
      const updateUUID = selectedCaptureMetadataUUID(captureUUID, labelUUID)(state);
      const requestData = {
        capture: captureUUID,
        label: labelUUID,
        label_value: labelValueUUID,
      };
      if (updateUUID && labelValueUUID) {
        requestDataToUpdate.push({
          ...requestData,
          uuid: updateUUID,
        });
      } else if (updateUUID) {
        requestDataToDelete.push(updateUUID);
      } else if (labelValueUUID) {
        requestDataToCreate.push(requestData);
      }
    });
  });
  return [requestDataToUpdate, requestDataToCreate, requestDataToDelete];
};

export default getCaptureMetadataFormData;
