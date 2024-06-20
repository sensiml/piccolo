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

import api, { throwParsedApiError } from "store/api";
import { selectCaptureUUIDs } from "store/captures/selectors";
import { selectMetadata } from "store/metadata/selectors";
import { createMetadataValue, loadMetadata } from "store/metadata/actions";

import logger from "../logger";
import helper from "../helper";

import getCaptureMetadataRequestData from "./domain/getCaptureMetadataRequestData";
import { LOADING_CAPTURES_METADATA, STORE_CAPTURES_METADATA } from "./actionTypes";

export const loadCapturesMetadata = (projectId) => async (dispatch, getState) => {
  const state = getState();
  const captureUUIDList = selectCaptureUUIDs(state);
  dispatch({ type: LOADING_CAPTURES_METADATA });
  await dispatch(loadMetadata(projectId));
  let metadata = [];

  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const { data: responseBody } = await api.post(
        `/project/${projectId}/capture-metadata-relationship/`,
        { capture_uuid_list: captureUUIDList },
      );
      metadata = responseBody;
    } catch (err) {
      logger.logError(
        "",
        err,
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectId}`,
        "loadMetadata",
      );
    }
  }
  dispatch({ type: STORE_CAPTURES_METADATA, metadata });
};

export const updateCapturesMetadata =
  (projectUUID, captureUUIDs, capturesMetadata) => async (dispatch, getState) => {
    /**
     * updating/creating capture metadata relationship
     * @projectUUID
     * @captureUUIDs
     * @capturesMetadata
     */
    const state = getState();
    const updatedCapturesMetadata = { ...capturesMetadata };

    // before update/create relationship
    // needs to create metadata values of metadata with dropdown false
    await Promise.all(
      _.entries(capturesMetadata).map(async ([metadataUUID, value]) => {
        const meatadataValues = selectMetadata(metadataUUID)(state)?.label_values || [];
        const metadataValueSelectedByUUID = meatadataValues.find((el) => el.uuid === value);
        if (!metadataValueSelectedByUUID && value) {
          // if not metadata values with uuid - it's metadata with text type
          const metadataValueSelectedByName = meatadataValues.find((el) => el.value === value);
          if (metadataValueSelectedByName) {
            updatedCapturesMetadata[metadataUUID] = metadataValueSelectedByName.uuid;
          } else {
            const createdMetadataValue = await dispatch(
              createMetadataValue(projectUUID, metadataUUID, value),
            );
            updatedCapturesMetadata[metadataUUID] = createdMetadataValue.data.uuid;
          }
        }
      }, []),
    );

    const [requestDataToUpdate, requestDataToCreate, requestDataToDelete] =
      getCaptureMetadataRequestData(state, captureUUIDs, updatedCapturesMetadata);
    if (!helper.isNullOrEmpty(projectUUID)) {
      try {
        if (!_.isEmpty(requestDataToUpdate)) {
          await api.put(`/project/${projectUUID}/metadata-relationship/`, requestDataToUpdate);
        }
        if (!_.isEmpty(requestDataToCreate)) {
          await api.post(`/project/${projectUUID}/metadata-relationship/`, requestDataToCreate);
        }
        if (!_.isEmpty(requestDataToDelete)) {
          await api.post(
            `v2/project/${projectUUID}/metadata-relationship/delete/`,
            requestDataToDelete,
          );
        }
      } catch (error) {
        logger.logError(
          "",
          error,
          `${helper.getResponseErrorDetails(error)} \n--projectId:${projectUUID}`,
          "loadMetadata",
        );
        throwParsedApiError(error, "capture metadata updating");
      }
    }
  };

export const deleteCapturesMetadata = (projectId, captureUUIDs) => async (dispatch) => {
  dispatch({ type: LOADING_CAPTURES_METADATA });
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      await api.post(`/v2/project/${projectId}/metadata-relationship/delete/`, [...captureUUIDs]);
      dispatch(loadCapturesMetadata(projectId));
    } catch (err) {
      logger.logError(
        "",
        err,
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectId}`,
        "loadMetadata",
      );
    }
  }
};
