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

import api, { throwParsedApiError } from "../api";
import logger from "../logger";
import helper from "../helper";
import { STORE_METADATA, LOADING_METADATA } from "./actionTypes";
// import { ConsoleBodySimpleView } from "components/LogsView";
// import ConsoleTab from "components/LogsView/ConsoleTab";

export const loadMetadata = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_METADATA });
  let metadata = [];
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectId}/metadata/`);
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
  dispatch({ type: STORE_METADATA, metadata });
};

export const createMetadata = (projectUUID, name, isDropdown) => async () => {
  if (!helper.isNullOrEmpty(projectUUID)) {
    try {
      const { data } = await api.post(`/project/${projectUUID}/metadata/`, {
        name,
        is_dropdown: isDropdown,
        type: "string",
        metadata: true,
      });
      return data;
    } catch (err) {
      logger.logError(
        "",
        err,
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
        "createMetadata",
      );
      throwParsedApiError(err, "createMetadata");
    }
  }
  return {};
};

export const updateMetadata = (projectUUID, metadataUUID, name, isDropdown) => async () => {
  if (!helper.isNullOrEmpty(projectUUID)) {
    try {
      await api.patch(`/project/${projectUUID}/metadata/${metadataUUID}/`, {
        name,
        is_dropdown: isDropdown,
        type: "string",
      });
    } catch (err) {
      logger.logError(
        "",
        err,
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
        "updateMetadata",
      );
      throwParsedApiError(err, "updateMetadata");
    }
  }
};

export const deleteMetadata = (projectUUID, metadataUUID) => async () => {
  if (!helper.isNullOrEmpty(projectUUID)) {
    try {
      await api.delete(`/project/${projectUUID}/metadata/${metadataUUID}/`);
    } catch (err) {
      logger.logError(
        "",
        err,
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
        "deleteMetadata",
      );
      throwParsedApiError(err, "deleteMetadata");
    }
  }
};

export const createMetadataValue = (projectUUID, metadataUUID, value) => async () => {
  let metadataValue = {};
  if (!helper.isNullOrEmpty(projectUUID)) {
    try {
      metadataValue = await api.post(
        `/project/${projectUUID}/metadata/${metadataUUID}/labelvalue/`,
        { value },
      );
    } catch (err) {
      logger.logError(
        "",
        err,
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
        "updateMetadataValue",
      );
      throwParsedApiError(err, "createMetadata");
    }
  }
  return metadataValue;
};

export const updateMetadataValue =
  (projectUUID, metadataUUID, metadataValueUUID, value) => async () => {
    if (!helper.isNullOrEmpty(projectUUID)) {
      try {
        await api.patch(
          `/project/${projectUUID}/metadata/${metadataUUID}/labelvalue/${metadataValueUUID}/`,
          { value },
        );
      } catch (err) {
        logger.logError(
          "",
          err,
          `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
          "updateMetadataValue",
        );
        throwParsedApiError(err, "createMetadata");
      }
    }
  };

export const deleteMetadataValue = (projectUUID, metadataUUID, metadataValueUUID) => async () => {
  if (!helper.isNullOrEmpty(projectUUID)) {
    try {
      await api.delete(
        `/project/${projectUUID}/metadata/${metadataUUID}/labelvalue/${metadataValueUUID}/`,
      );
    } catch (err) {
      logger.logError(
        "",
        err,
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
        "deleteMetadataValue",
      );
      throwParsedApiError(err, "createMetadata");
    }
  }
};
