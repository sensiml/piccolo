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

/* eslint-disable camelcase */
/* eslint-disable no-restricted-syntax */
import i18n from "i18n";
import _ from "lodash";
import fileDownload from "js-file-download";

import api, { BaseAPIError, throwParsedApiError } from "store/api";

import "regenerator-runtime/runtime";
import logger from "../logger";
import helper from "../helper";
import {
  LOADING_MODELS,
  STORE_MODELS,
  LOADING_MODEL,
  STORE_MODEL,
  CLEAR_MODEL,
  STORE_SELECTED_MODEL,
  STARTING_MODEL_DOWNLOAD,
  STARTED_MODEL_DOWNLOAD,
  DOWNLOADING_MODEL,
  MODEL_DOWNLOAD_FAILED,
  MODEL_DOWNLOADED,
  CANCEL_MODEL_DOWNLOAD,
  RENAMING_MODEL,
  RENAMED_MODEL,
  MODEL_FEATURE_VECTORS_LOADING,
  MODEL_FEATURE_VECTORS_STORE,
} from "./actionTypes";

import { selecteModelData } from "./selectors";

let cancelDownload = false;

export const loadModels = (projectId, pipelineId) => async (dispatch) => {
  await dispatch({ type: LOADING_MODELS });
  let models = [];

  if (!helper.isNullOrEmpty(projectId) && !helper.isNullOrEmpty(pipelineId)) {
    try {
      const { data: responseBody } = await api.get(
        `/project/${projectId}/sandbox/${pipelineId}/knowledgepack/`,
      );
      models = helper.sortObjects(responseBody, "name");
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          err,
        )} \n--projectId:${projectId},pipelineId:${pipelineId} `,
        err,
        `models-loadModels`,
      );
    }
  }
  await dispatch({ type: STORE_MODELS, models });
  return models;
};

export const deleteModel = (modelUUID) => async (_dispatch) => {
  // await dispatch({ type: LOADING_MODELS });

  if (!helper.isNullOrEmpty(modelUUID)) {
    try {
      await api.delete(`/knowledgepack/${modelUUID}/`);
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)} \n , modelUUID:${modelUUID} `,
        err,
        `model-delete`,
      );
      throwParsedApiError(err, `Failed to delete model ${modelUUID}`);
    }
  }
};

export const setSelectedModel = (modelUuId) => {
  return {
    type: STORE_SELECTED_MODEL,
    selectedModel: modelUuId,
  };
};

export const loadModel =
  (modelUuId, fields = []) =>
  async (dispatch, getState) => {
    const state = getState();
    const cachedModelFields = _.keys(selecteModelData(state));
    const filteredFields = fields.filter((field) => !cachedModelFields.includes(field));

    let model = {};
    if (!helper.isNullOrEmpty(modelUuId) && !_.isEmpty(filteredFields)) {
      dispatch({ type: LOADING_MODEL });

      try {
        const { data: responseBody } = await api.get(`/knowledgepack/${modelUuId}/`, {
          params: {
            fields: filteredFields,
          },
        });
        model = { ...selecteModelData(state), ...responseBody };

        dispatch(setSelectedModel(model?.uuid || ""));

        // For Hierachical models, if a parent model
        // is being downloaded, download all child model with it
        if (model && model.knowledgepack_description) {
          model.child_models = [];
          for (const modelName of Object.keys(model.knowledgepack_description)) {
            const childModelUuid = model.knowledgepack_description[modelName].uuid;
            // eslint-disable-next-line no-continue
            if (childModelUuid === modelUuId) continue;
            try {
              // eslint-disable-next-line no-await-in-loop
              const { data: childModel } = await api.get(`/knowledgepack/${childModelUuid}/`);
              model.child_models.push({
                uuid: childModelUuid,
                name: modelName,
                data: childModel,
              });
            } catch (err) {
              logger.logError(
                "",
                `${helper.getResponseErrorDetails(
                  err,
                )} \n--Hierachical Models childModelUuid:${childModelUuid}`,
                err,
                "loadModel",
              );
            }
          }
        }
      } catch (err) {
        logger.logError(
          "",
          `${helper.getResponseErrorDetails(err)} \n--modelUuId:${modelUuId}`,
          err,
          "loadModel",
        );
        if (err.response) {
          throw new BaseAPIError(err.response?.status, err.response);
        }
        dispatch({ type: STORE_MODEL, model });
      }
    }
    if (!_.isEmpty(filteredFields)) {
      dispatch({ type: STORE_MODEL, model });
    }
  };

export const renameModel = (projectId, pipelineId, modelId, kps_to_rename) => async (dispatch) => {
  let newName = "";
  dispatch({ type: RENAMING_MODEL, uuid: modelId });
  let response = { status: "" };
  if (kps_to_rename && kps_to_rename.length > 0) {
    if (!helper.isNullOrEmpty(modelId)) {
      try {
        // eslint-disable-next-line guard-for-in
        for (const kp_to_rename in kps_to_rename) {
          const nestetModelId = kps_to_rename[kp_to_rename].uuid;
          newName = kps_to_rename[kp_to_rename].newName;
          // eslint-disable-next-line no-await-in-loop
          await api.put(`project/${projectId}/knowledgepack/${nestetModelId}/`, {
            name: _.snakeCase(newName),
          });
        }
        dispatch({
          type: RENAMED_MODEL,
          uuid: modelId,
        });
        response = { status: "success" };
        await dispatch(loadModels(projectId, pipelineId));
      } catch (err) {
        const errorResponse = helper.getResponseErrorDetails(err);
        logger.logError(
          "",
          // eslint-disable-next-line max-len
          `${errorResponse} \n--projectId:${projectId},pipelineId:${pipelineId},modelId:${modelId},newName:${newName}`,
          err,
          "renameModel",
        );
        const errMsg =
          err.response?.status === 403
            ? "Your account does not have permission to rename the Knowledge Pack."
            : err.response?.status === 404
            ? i18n.t("models:model-selected-does-not-exist")
            : errorResponse;
        response = { status: "error", details: errMsg };
      }
    }
  }
  return response;
};

export const clearModel = () => (dispatch) => {
  dispatch(setSelectedModel(""));
  dispatch({ type: CLEAR_MODEL });
};

export const cancelDownloadRequest = () => {
  cancelDownload = true;
  return { type: CANCEL_MODEL_DOWNLOAD };
};

export const submitDownloadRequest =
  (projectUuid, pipelineUuid, modelUuid, downloadType, config) => async (dispatch) => {
    dispatch({ type: STARTING_MODEL_DOWNLOAD });

    let dispatchObject = {};
    const isValidParams = () => {
      if (!projectUuid) dispatchObject = { error: i18n.t("models:download.error-select-project") };
      if (!modelUuid) dispatchObject = { error: i18n.t("models:download.error-select-model") };
      if (!downloadType) dispatchObject = { error: i18n.t("models:download.error-select-format") };
      return Boolean(!dispatchObject.error);
    };

    try {
      if (!isValidParams()) {
        // throw an error which will be cathec bellow and dispatch to redux
        throw Error(dispatchObject.error);
      }

      const send_config = config;
      send_config.target_processor = config?.target_processor?.uuid;
      await api.post(
        // eslint-disable-next-line max-len
        `project/${projectUuid}/knowledgepack/${modelUuid}/generate_${downloadType}/v2`,
        send_config,
      );
      dispatchObject = {
        type: STARTED_MODEL_DOWNLOAD,
        pipelineUuid,
        modelUuid,
        message: "Submitting Download Request.",
      };
    } catch (err) {
      const errorMessage = helper.getResponseErrorDetails(err);
      logger.logError(
        "",
        // eslint-disable-next-line max-len
        `${errorMessage}\n--projectId:${projectUuid},pipelineId:${pipelineUuid},modelId:${modelUuid},downloadType:${downloadType}/v2`,
        err,
        "submitDownloadRequest",
      );

      dispatchObject = {
        type: MODEL_DOWNLOAD_FAILED,
        pipelineUuid,
        modelUuid,
        code: err?.response?.status,
        status: "FAILURE",
        error: errorMessage,
        message: errorMessage,
      };
    }
    dispatch(dispatchObject);
    return dispatchObject;
  };

export const checkDownloadRequestStatus =
  (projectUuid, pipelineUuid, modelUuid, downloadType) => async (dispatch) => {
    let dispatchObject = {};
    if (cancelDownload === true) {
      cancelDownload = false;
      dispatchObject = {
        type: CANCEL_MODEL_DOWNLOAD,
        pipelineUuid,
        modelUuid,
        status: "CANCELED",
      };
      dispatch(dispatchObject);
      return dispatchObject;
    }
    if (!helper.isNullOrEmpty(modelUuid)) {
      try {
        // eslint-disable-next-line max-len
        const url = `project/${projectUuid}/knowledgepack/${modelUuid}/generate_${downloadType}/v2`;
        const response = await api.get(url);
        if (response.data && response.data.task_state && response.data.task_state === "SENT") {
          dispatchObject = {
            type: DOWNLOADING_MODEL,
            pipelineUuid,
            modelUuid,
            status: "RUNNING",
            code: response?.status,
          };
        } else if (
          response.data &&
          response.data.task_state &&
          response.data.task_state === "FAILURE"
        ) {
          dispatchObject = {
            type: MODEL_DOWNLOAD_FAILED,
            pipelineUuid,
            modelUuid,
            status: "FAILURE",
            code: response?.status,
            error: response.data.task_result,
            message: response.data.task_result,
          };
        } else if (response && response.headers) {
          const resp = await api.get(url, { responseType: "blob" });
          let filename = "";
          const disposition = response.headers["content-disposition"];
          if (disposition && disposition.indexOf("attachment") !== -1) {
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(disposition);

            if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, "");
          }

          dispatchObject = {
            type: MODEL_DOWNLOADED,
            pipelineUuid,
            modelUuid,
            data: resp.data,
            headers: resp.headers,
            filename,
            code: response?.status,
            status: "SUCCESS",
            message: "Download Completed.",
          };
        } else {
          dispatchObject = {
            type: MODEL_DOWNLOAD_FAILED,
            pipelineUuid,
            modelUuid,
            status: "FAILURE",
            code: response?.status,
            error: response.data.task_result,
            message: response.data.task_result,
          };
        }
      } catch (err) {
        const errorMessage = helper.getResponseErrorDetails(err);
        logger.logError(
          "",
          // eslint-disable-next-line max-len
          `${errorMessage}\n--projectId:${projectUuid},pipelineId:${pipelineUuid},modelId:${modelUuid},downloadType:${downloadType}`,
          err,
          "checkDownloadRequestStatus",
        );
        dispatchObject = {
          type: MODEL_DOWNLOAD_FAILED,
          pipelineUuid,
          modelUuid,
          status: "FAILURE",
          code: err?.response?.status,
          error: errorMessage,
          message: errorMessage,
        };
      }
      dispatch(dispatchObject);
    }
    return dispatchObject;
  };

// eslint-disable-next-line consistent-return
export const loadDownloadLogs = (modelUuid) => async () => {
  try {
    const response = await api.get(`knowledgepack/${modelUuid}/build-logs/`, {
      responseType: "text",
    });
    if (response.data) {
      fileDownload(response.data, `${modelUuid}_build.log`);
    }
  } catch (error) {
    const errorMessage = helper.getResponseErrorDetails(error);
    return { errorMessage };
  }
};

export const loadFeatureVectorData = (projectUUID, featureFileUUID) => async (dispatch) => {
  try {
    dispatch({ type: MODEL_FEATURE_VECTORS_LOADING });
    const { data } = await api.get(`/project/${projectUUID}/featurefile/${featureFileUUID}/json/`);
    dispatch({ type: MODEL_FEATURE_VECTORS_STORE, payload: { data, featureFileUUID } });
    return data;
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(
        err,
      )} \n--projectUUID:${projectUUID}\n--featureFileUUID:${featureFileUUID}`,
      err,
      "loadFeatureVectorData",
    );
    throwParsedApiError(err, `Failed to loadFeatureVectorData featureFileUUID: ${featureFileUUID}`);
  }
  return {};
};
