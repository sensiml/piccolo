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

import { selectMetadata } from "store/metadata/selectors";

export const selectedCaptureMetadatas = (captureUUID) => (state) => {
  if (!_.isEmpty(state.captureMetadata?.data)) {
    return state.captureMetadata.data.filter((el) => el.capture === captureUUID);
  }
  return [];
};

export const selectedCaptureMetadataUUID = (captureUUID, labelUUID) => (state) => {
  if (!_.isEmpty(state.captureMetadata?.data)) {
    const captureMetadata = state.captureMetadata.data.find(
      (el) => el.capture === captureUUID && el.label === labelUUID,
    );
    return captureMetadata?.uuid || "";
  }
  return "";
};

export const selectedCaptureMetadataParameters = (captureUUID) => (state) => {
  if (!_.isEmpty(state.captureMetadata?.data)) {
    const captureMetadatas = state.captureMetadata.data.filter((el) => el.capture === captureUUID);
    return captureMetadatas.reduce((acc, captureMetadata) => {
      const metadata = selectMetadata(captureMetadata.label)(state);
      acc[metadata.name] =
        _.find(metadata.label_values, (el) => el.uuid === captureMetadata.label_value)?.value || "";
      return acc;
    }, {});
  }
  return {};
};
