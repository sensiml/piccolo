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

import { FORM_TYPES } from "consts";
import { selectMetadataFormData } from "store/metadata/selectors";
import { selectedCaptureMetadatas } from "store/captureMetadata/selectors";
import { store } from "store";

import _ from "lodash";

const getCaptureMetadataFormData = (captureUUID) => {
  const state = store.getState();
  const metadataItems = selectMetadataFormData(state);
  const savedCaptureMetadata = selectedCaptureMetadatas(captureUUID)(state);

  const getDefaultCaptureMetadataUUID = (labelUUI) => {
    return savedCaptureMetadata.find((el) => el.label === labelUUI)?.label_value || "";
  };

  const getMetadataType = (isDropdown, metadataType) => {
    // some metadata types can be integer like Sample Rate
    if (isDropdown) {
      return FORM_TYPES.FORM_SELECT_TYPE;
    }
    if (metadataType === "integer" || metadataType === "int") {
      return FORM_TYPES.FORM_INT_TYPE;
    }
    // default to string
    return FORM_TYPES.FORM_STRING_TYPE;
  };

  const res = metadataItems
    .filter((el) => el?.metadata)
    .map((metadataItem) => {
      let defaultValueObj = !_.isEmpty(metadataItem.label_values)
        ? metadataItem.label_values.find(
            (el) => el.uuid === getDefaultCaptureMetadataUUID(metadataItem.uuid),
          )
        : {};

      if (_.isEmpty(defaultValueObj) && !_.isEmpty(metadataItem.label_values)) {
        defaultValueObj = _.first(metadataItem.label_values);
      }

      return {
        name: metadataItem.uuid,
        label: metadataItem.name,
        formType: getMetadataType(metadataItem.is_dropdown, metadataItem.type),
        defaultValue: metadataItem.is_dropdown
          ? defaultValueObj?.uuid || ""
          : defaultValueObj?.value || "",
        options: _.map(metadataItem?.label_values, (el) => ({
          name: el.value,
          value: el.uuid,
        })),
      };
    });
  return res;
};

export default getCaptureMetadataFormData;
