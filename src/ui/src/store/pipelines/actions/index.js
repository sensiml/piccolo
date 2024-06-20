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
import axios from "axios";
import api, { throwParsedApiError, parseApiError } from "store/api";
import logger from "store/logger";
import helper from "store/helper";
import fileDownload from "js-file-download";
import { PIPELINE_CONSTS } from "consts";
import { v4 as uuidv4 } from "uuid";
import { store } from "store";
import { ASYNC_CECK_INTERVAL } from "config";
import { getPipelineObj } from "store/pipelines/selectors";

import {
  ADD_PIPELINE,
  UPDATING_PIPELINE,
  UPDATED_PIPELINE,
  STORE_SELECTED_PIPELINE,
  STORE_PIPELINES,
  LOADING_PIPELINES,
  LOADING_PIPELINE_SEEDS,
  STORE_PIPELINE_SEEDS,
  LOADING_PIPELINES_RESULTS,
  STORE_PIPELINE_RESULTS,
  CLEAR_PIPELINE_RESULTS,
  SUBMITING_OPTIMIZATION_REQUEST,
  SUBMITED_OPTIMIZATION_REQUEST,
  FINISHED_OPTIMIZATION,
  RUNNING_OPTIMIZATION,
  FAILED_OPTIMIZATION,
  KILLING_OPTIMIZATION_REQUEST,
  KILLING_OPTIMIZATION_FAILED,
  OPTIMIZATION_REQUEST_KILLED,
  OPTIMIZATION_REQUEST_NOT_STARTED,
  CLEAR_OPTIMIZATION_REQUEST_STATUS,
  DELETING_PIPELINE,
  PIPELINE_DELETED,
  UPDATE_OPTIMIATION_LOGS,
  CLEAR_OPTIMIATION_LOGS,
  UPDATE_OPTIMIATION_DETAILED_LOGS,
  CLEAR_OPTIMIATION_DETAILED_LOGS,
  STORE_PIPELINE_STATUS,
  LOADING_PIPELINE_DATA,
  STORE_PIPELINE_DATA,
} from "../actionTypes";
import {
  MESSAGE_STATUS,
  API_RUNNING_STATUS,
  API_ERROR_STATUS,
  API_TERMINATTED_STATUS,
} from "../status";

import { clearIterationMetrics } from "./loadIterationMetrics";

export { loadIterationMetrics } from "./loadIterationMetrics";

export const setRunningStatus = (responseBody) => async (dispatch) => {
  let logPayload = {};
  let isLauching = true;
  dispatch({
    type: STORE_PIPELINE_STATUS,
    payload: { status: responseBody?.status, ...responseBody.detail },
  });

  if (responseBody?.status === "SUCCESS" && !responseBody.message) {
    dispatch({ type: FINISHED_OPTIMIZATION });
    logPayload = {
      status: MESSAGE_STATUS.SUCCESS,
      message: "Automation Pipeline Completed.",
    };
    isLauching = false;
  } else if (!responseBody?.status && !responseBody.message) {
    dispatch({ type: OPTIMIZATION_REQUEST_NOT_STARTED });
    logPayload = {
      status: MESSAGE_STATUS.NOT_STARTED,
      message: responseBody.message,
    };
    isLauching = false;
  } else if (API_RUNNING_STATUS.includes(responseBody?.status)) {
    dispatch({ type: RUNNING_OPTIMIZATION });
    logPayload = {
      status: MESSAGE_STATUS.INFO,
      message: responseBody?.message,
    };
  } else if (API_ERROR_STATUS.includes(responseBody?.status)) {
    dispatch({ type: FAILED_OPTIMIZATION });
    logPayload = {
      status: MESSAGE_STATUS.ERROR,
      message: responseBody?.message,
    };
    isLauching = false;
  } else if (API_TERMINATTED_STATUS.includes(responseBody?.status)) {
    dispatch({ type: OPTIMIZATION_REQUEST_KILLED });
    logPayload = {
      status: MESSAGE_STATUS.WARNING,
      message: responseBody?.message,
    };
    isLauching = false;
  } else {
    dispatch({ type: RUNNING_OPTIMIZATION });
    logPayload = {
      status: MESSAGE_STATUS.INFO,
      message: "Running Pipeline.",
    };
  }

  // eslint-disable-next-line no-use-before-define
  dispatch(updateOptimizationLogs({ ...logPayload, isLauching }));
  return isLauching;
};

export const clearPipelineStatus = () => (dispatch) => {
  dispatch({
    type: STORE_PIPELINE_STATUS,
    payload: {},
  });
};

export const setSelectedPipeline = (pipelineUuId) => {
  return {
    type: STORE_SELECTED_PIPELINE,
    selectedPipeline: pipelineUuId,
  };
};

export const updateOptimizationLogs =
  ({ status, message }) =>
  async (dispatch) => {
    const state = store.getState();
    const logs = state?.pipelines?.optimizationLogs || [];

    if (logs.findIndex((logEl) => logEl.message === message) === -1) {
      dispatch({
        type: UPDATE_OPTIMIATION_LOGS,
        payload: [...logs, { status, message }],
      });
    }
  };

export const clearOptimizationLogs = () => async (dispatch) => {
  dispatch({ type: CLEAR_OPTIMIATION_LOGS });
  dispatch({ type: CLEAR_OPTIMIZATION_REQUEST_STATUS });
};

export const updateOptimizationDetailedLogs = (sourceArray, timestamp) => async (dispatch) => {
  const state = store.getState();
  const { logs } = state?.pipelines?.optimizationDetailedLogs;
  // eslint-disable-next-line max-len
  const { message: lastMessage, timestamp: lastLogTimestamp } = logs[logs.length - 1] || {}; // last log

  let targetArray = [];
  let startIndex = 0;

  startIndex = sourceArray.findIndex(
    (log) => log?.message === lastMessage || log?.timestamp === lastLogTimestamp,
  );

  if (startIndex !== -1) {
    targetArray = sourceArray.slice(startIndex).map((el) => ({ ...el, logid: uuidv4() }));
  } else {
    targetArray = sourceArray.map((el) => ({ ...el, logid: uuidv4() }));
  }

  await dispatch({
    type: UPDATE_OPTIMIATION_DETAILED_LOGS,
    payload: { logs: [...logs, ...targetArray], lastTimeStamp: timestamp },
  });
};

export const clearOptimizationDetailedLogs = () => {
  return {
    type: CLEAR_OPTIMIATION_DETAILED_LOGS,
  };
};

export const loadPipelines = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_PIPELINES });
  let pipelines = [];
  if (projectId) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectId}/sandbox/`, {
        params: {
          fields: [
            "name",
            "uuid",
            "created_at",
            "last_modified",
            "cpu_clock_time",
            "active",
            "pipeline",
            "hyper_params",
          ],
        },
      });
      pipelines = helper.sortObjects(responseBody, "name", true);
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)} \n -- projectId:${projectId}`,
        err,
        "loadPipelines",
      );
    }
  }
  dispatch({ type: STORE_PIPELINES, pipelines });
};

export const loadPipeline = (projectUUID, pipelineUUID) => async (dispatch) => {
  dispatch({ type: LOADING_PIPELINE_DATA });
  try {
    const { data } = await api.get(`/project/${projectUUID}/sandbox/${pipelineUUID}/`);
    dispatch({ type: STORE_PIPELINE_DATA, payload: data });
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(err)} \n -- projectId`,
      err,
      "loadPipelines",
    );
  }
};

export const clearPipeline = () => (dispatch) => {
  dispatch({ type: STORE_PIPELINE_DATA, payload: {} });
};

export const loadPipelineSeeds = () => async (dispatch) => {
  dispatch({ type: LOADING_PIPELINE_SEEDS });
  let seeds = [];
  try {
    const { data: responseBody } = await api.get("/seed/v2/");
    seeds = responseBody;
  } catch (err) {
    logger.logError("", helper.getResponseErrorDetails(err), err, "loadPipelineSeeds");
  }

  dispatch({ type: STORE_PIPELINE_SEEDS, seeds });
};

export const updatePipeline =
  ({
    projectUuid,
    pipelineUuid,
    pipelineName,
    pipelineSteps,
    autoMLSeed,
    cacheEnabled,
    deviceConfig,
  }) =>
  async (dispatch) => {
    if (helper.isNullOrEmpty(pipelineUuid)) return;

    try {
      dispatch({
        type: UPDATING_PIPELINE,
        updatingPipeline: pipelineUuid,
      });
      const sandboxInfo = {
        ...(pipelineName && { name: pipelineName }),
        ...(pipelineSteps && { pipeline: pipelineSteps }),
        ...(autoMLSeed && { hyper_params: autoMLSeed }),
        ...(cacheEnabled && { cache_enabled: cacheEnabled }),
        ...(deviceConfig && { device_config: deviceConfig }),
      };

      const response = await api.put(
        `project/${projectUuid}/sandbox/${pipelineUuid}/`,
        sandboxInfo,
      );
      dispatch({ type: UPDATED_PIPELINE, updatedPipeline: pipelineUuid });
      dispatch({ type: STORE_PIPELINE_DATA, payload: response?.data });
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          err,
        )} \n--projectId:${projectUuid},pipelineUuid:${pipelineUuid}`,
        err,
        "updatePipeline",
      );
      throwParsedApiError(err, "Failed to update pipeline");
    }
    dispatch({ type: STORE_SELECTED_PIPELINE, selectedPipeline: pipelineUuid });
  };

export const deletePipeline = (projectId, pipelineUuid) => async (dispatch) => {
  dispatch({ type: DELETING_PIPELINE, uuid: pipelineUuid });
  let response = { status: "" };
  try {
    if (!helper.isNullOrEmpty(projectId) && !helper.isNullOrEmpty(pipelineUuid)) {
      await api.delete(`/project/${projectId}/sandbox/${pipelineUuid}/`);
      dispatch({
        type: PIPELINE_DELETED,
        uuid: pipelineUuid,
      });
      response = { status: "success" };
    }
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(
        err,
      )}\n--projectId:${projectId},pipelineUuid:${pipelineUuid}`,
      err,
      "deletePipeline",
    );
    response = {
      status: "error",
      details: parseApiError(err, `Failed to delete pipeline ${pipelineUuid}`).message,
    };
  }
  return response;
};

export const checkPipelineIsRunning = (projectUuid, pipelineUuid) => async () => {
  try {
    if (helper.isNullOrEmpty(pipelineUuid)) return;

    const { data: responseBody } = await api.get(
      `project/${projectUuid}/sandbox-async/${pipelineUuid}/`,
    );
    // eslint-disable-next-line consistent-return
    return responseBody && responseBody.status && API_RUNNING_STATUS.includes(responseBody.status);
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(
        err,
      )}\n--projectId:${projectUuid},pipelineUuid:${pipelineUuid}`,
      err,
      "checkPipelineIsRunning",
    );
  }
  // eslint-disable-next-line consistent-return
  return false;
};

export const loadPipelineResults = (projectUuid, pipelineUuid) => async (dispatch) => {
  dispatch({ type: LOADING_PIPELINES_RESULTS });
  let isRunning = false;
  let results = {};

  try {
    const { data: responseBody } = await api.get(
      `project/${projectUuid}/sandbox-async/${pipelineUuid}/`,
    );
    isRunning = await dispatch(setRunningStatus(responseBody));
    if (responseBody) {
      if (responseBody.fitness_summary) {
        results = responseBody.fitness_summary;
      }
      if (!results.name) {
        results.name = results.knowledgepack;
      }
      if (!_.isEmpty(responseBody?.results?.configurations)) {
        results.name = _.keys(responseBody?.results?.configurations);
      }
    }
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(
        err,
      )}\n--projectId:${projectUuid},pipelineUuid:${pipelineUuid}`,
      err,
      "loadPipelineResults",
    );
  }

  dispatch({ type: STORE_PIPELINE_RESULTS, results });

  return isRunning;
};

export const clearPipelineResults = () => async (dispatch) => {
  dispatch({ type: CLEAR_PIPELINE_RESULTS });
};

export const runOptimization = () => {
  return { type: RUNNING_OPTIMIZATION };
};

export const submitOptimizationRequest =
  (projectUuid, pipelineUuid, autoParams) => async (dispatch) => {
    dispatch({ type: SUBMITING_OPTIMIZATION_REQUEST });
    if (!helper.isNullOrEmpty(projectUuid) && !helper.isNullOrEmpty(pipelineUuid)) {
      try {
        const response = await api.post(
          `project/${projectUuid}/sandbox-async/${pipelineUuid}/`,
          autoParams,
        );
        dispatch(clearIterationMetrics());
        dispatch({ type: SUBMITED_OPTIMIZATION_REQUEST });
        dispatch({ type: STORE_PIPELINE_STATUS, payload: response?.data?.detail });
        if (response?.data?.message) {
          dispatch(
            updateOptimizationLogs({
              status: MESSAGE_STATUS.INFO,
              message: response?.data?.message,
              isLauching: true,
            }),
          );
        }
        if (response?.data?.cpu_credit) {
          dispatch(
            updateOptimizationLogs({
              status: MESSAGE_STATUS.INFO,
              message: response?.data?.cpu_credit,
              isLauching: true,
            }),
          );
        }
      } catch (error) {
        const parsedError = parseApiError(error, "submitOptimizationRequest");
        await dispatch(setRunningStatus({ status: "FAILURE", message: parsedError.message }));

        logger.logError(
          "",
          `${helper.getResponseErrorDetails(
            error,
          )}\n--projectId:${projectUuid},pipelineUuid:${pipelineUuid}`,
          error,
          "submitOptimizationRequest",
        );
        throw parsedError;
      }
    }
  };

export const checkOptimizationRunningDetailed = (pipelineUuid) => async (dispatch) => {
  const detailedLogApi = axios.create({
    baseURL: process.env.REACT_APP_PIPELINE_RUN_LOG_API_URL,
    withCredentials: false,
    crossdomain: true,
    headers: {
      "X-Api-Key": process.env.REACT_APP_PIPELINE_RUN_LOG_API_KEY,
    },
  });
  const state = store.getState();
  const { lastTimeStamp } = state?.pipelines?.optimizationDetailedLogs;

  try {
    const { data: responseBody } = await detailedLogApi.get("/pipeline-run-log/", {
      params: { id: pipelineUuid, start_time_utc: lastTimeStamp },
    });
    if (responseBody?.results) {
      await dispatch(
        updateOptimizationDetailedLogs(responseBody?.results || [], responseBody?.timestamp),
      );
    }
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(
        err,
      )}\n--checkOptimizationRequestDetailedStatus--pipelineUuid:${pipelineUuid}`,
      err,
      "checkOptimizationRequestDetailedStatus",
    );
  }
};

export const checkOptimizationRunning = (projectUuid, pipelineUuid) => async (dispatch) => {
  let isLauching = true;

  if (projectUuid && pipelineUuid) {
    try {
      const { data } = await api.get(`project/${projectUuid}/sandbox-async/${pipelineUuid}/`);
      isLauching = await dispatch(setRunningStatus(data));
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          err,
        )}\n--projectId:${projectUuid},pipelineUuid:${pipelineUuid}`,
        err,
        "checkOptimizationRequestStatus",
      );

      const logPayload = {
        status: MESSAGE_STATUS.WARNING,
        // eslint-disable-next-line max-len
        message: `Encountered an error while checking optimization status, will retry status check in ${
          ASYNC_CECK_INTERVAL / 1000
        } seconds....`,
      };
      dispatch(updateOptimizationLogs({ ...logPayload, isLauching }));
    }
  }
  return isLauching;
};

export const killOptimizationRequest = (projectUuid, pipelineUuid) => async (dispatch) => {
  dispatch({ type: KILLING_OPTIMIZATION_REQUEST });
  dispatch(
    updateOptimizationLogs({
      status: MESSAGE_STATUS.WARNING,
      message: "Terminating running pipeline",
      isLauching: false,
    }),
  );

  if (!helper.isNullOrEmpty(projectUuid) && !helper.isNullOrEmpty(pipelineUuid)) {
    try {
      await api.delete(`project/${projectUuid}/sandbox-async/${pipelineUuid}/`);
      dispatch(
        updateOptimizationLogs({
          status: MESSAGE_STATUS.WARNING,
          message: "Pipeline was terminated.",
          isLauching: false,
        }),
      );
      dispatch({ type: OPTIMIZATION_REQUEST_KILLED });
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          err,
        )}\n--projectId:${projectUuid},pipelineUuid:${pipelineUuid}`,
        err,
        "killOptimizationRequest",
      );
      dispatch({
        type: KILLING_OPTIMIZATION_FAILED,
        pipelineUuid,
        message: "Error checking optimization request status.",
      });
    }
  }
};

export const addPipeline = (projectId, name) => async (dispatch) => {
  let pipelineUuid = "";
  let response = { status: "", details: pipelineUuid };
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const newSandbox = {
        name,
        pipeline: [],
        cache_enabled: "True",
        device_config: {
          target_platform: 0,
          build_flags: "",
          budget: [],
          debug: "False",
          sram_size: "",
          test_data: "",
          application: "",
          sample_rate: 100,
          kb_description: "",
        },
      };
      const { data } = await api.post(`/project/${projectId}/sandbox/`, newSandbox);
      await dispatch(loadPipelines(projectId));
      if (!_.isEmpty(data)) {
        pipelineUuid = data.uuid;
        await dispatch(setSelectedPipeline(pipelineUuid));
      }
      response = { isSuccess: true, details: pipelineUuid };
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId},pipelineName:${name}`,
        err,
        "addPipeline",
      );
      response = { isSuccess: false, details: _.join(err.response?.data?.data, "_") };
    }
  }
  await dispatch({ type: ADD_PIPELINE, selectedPipeline: pipelineUuid });
  return response;
};

const { DOWNLOAD_TYPES } = PIPELINE_CONSTS;
const EXTENTION_HASHMAP = {
  [DOWNLOAD_TYPES.PYTHON]: "py",
  [DOWNLOAD_TYPES.IPYNB]: "ipynb",
  [DOWNLOAD_TYPES.JSON]: "json",
};

const getPipelineJSON = (pipelineData) => {
  // eslint-disable-next-line camelcase
  const { pipeline = [], hyper_params = {} } = pipelineData;
  return JSON.stringify({ pipeline, hyper_params });
};

const getExtention = (downloadType) => {
  return EXTENTION_HASHMAP[downloadType];
};

export const exportPipeline =
  (projectUUID, pipelineUUID, downloadType = "python") =>
  async (_dispatch, getState) => {
    const state = getState();
    const pipeline = getPipelineObj(pipelineUUID)(state);

    if (downloadType === DOWNLOAD_TYPES.JSON) {
      const data = getPipelineJSON(pipeline);
      fileDownload(data, `${pipeline.name}.${getExtention(downloadType)}`);
    } else {
      try {
        const { data } = await api.get(
          `/project/${projectUUID}/sandbox/${pipelineUUID}/${downloadType}/`,
          { responseType: "blob" },
        );
        fileDownload(data, `${pipeline.name}.${getExtention(downloadType)}`);
      } catch (error) {
        logger.logError(
          "",
          `${helper.getResponseErrorDetails(error)} \n--projectId:${projectUUID}`,
          error,
          "loadCaptures",
        );
        throwParsedApiError(error, `download pipeline with ${downloadType} type`);
      }
    }
  };

export const downloadPipelineStepCache =
  (projectUUID, pipelineUUID, index, indexPage, pipelineName, stepName) => async () => {
    try {
      const { data } = await api.get(`/project/${projectUUID}/sandbox/${pipelineUUID}/data/`, {
        params: { pipeline_step: index, page_index: indexPage },
      });
      if (data?.results) {
        // remove all extentions
        fileDownload(
          JSON.stringify(data.results),
          `${pipelineName}.${stepName}.cache.${indexPage}.json`,
        );
      }
    } catch (error) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          error,
        )} \n--download pipeline cache data of ${pipelineUUID}`,
        error,
        "downloadPipelineStepCache",
      );
      throwParsedApiError(error, `download pipeline cache data of ${pipelineUUID}`);
    }
  };
