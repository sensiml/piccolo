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

/* eslint-disable prefer-const */
/* eslint-disable max-len */
/* eslint-disable no-unused-vars */
/* eslint-disable import/order */
/* eslint-disable-next-line max-len */
import _ from "lodash";
import fileDownload from "js-file-download";
import TokenStorage from "services/TokenStorage";
import api, { throwParsedApiError } from "store/api";
import { getFileExtension, CSVToJSON } from "utils";

import logger from "store/logger";
import helper from "store/helper";

import {
  STORE_CAPTURES,
  LOADING_CAPTURES,
  STORE_CAPTURES_STATISTICS,
  LOADING_CAPTURES_STATISTICS,
  CLEAR_CAPTURES_STATISTICS,
  LOADING_CAPTURE_SENSOR_DATA,
  SET_CAPTURE_SENSOR_DATA,
} from "./actionTypes";

// eslint-disable-next-line prefer-destructuring
const WaveFile = require("wavefile").WaveFile;

export const loadCaptures = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_CAPTURES });
  let captures = [];
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectId}/capture/`);
      captures = responseBody;
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectId}`,
        err,
        "loadCaptures",
      );
    }
  }
  dispatch({
    type: STORE_CAPTURES,
    captures,
  });
};

export const loadCapturesStatistics = (projectId, segmenterUUID) => async (dispatch) => {
  dispatch({ type: LOADING_CAPTURES_STATISTICS });
  let capturesStatistics = [];
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectId}/capture-stats/`, {
        params: { segmenter: segmenterUUID },
      });
      capturesStatistics = responseBody;
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)} \n--project:${projectId}`,
        err,
        "loadCapturesStatistics",
      );
    }
  }
  dispatch({
    type: STORE_CAPTURES_STATISTICS,
    capturesStatistics,
  });
};

export const updateCapturesStatisticsSegments =
  (captureUUID, segmentsCount) => async (dispatch, getState) => {
    const capturesStatistics = getState().capturesStatistics?.data || [];
    if (!_.isUndefined(segmentsCount)) {
      dispatch({
        type: STORE_CAPTURES_STATISTICS,
        capturesStatistics: capturesStatistics.map((capture) => {
          const updatedCapture = { ...capture };
          if (capture.uuid === captureUUID) {
            updatedCapture.total_events = segmentsCount;
          }
          return updatedCapture;
        }),
      });
    }
  };

export const clearCapturesStatistics = (projectId) => {
  return { type: CLEAR_CAPTURES_STATISTICS };
};

export const deleteCapture = (projectId, captureUUID) => async (dispatch) => {
  if (!helper.isNullOrEmpty(projectId) && !helper.isNullOrEmpty(captureUUID)) {
    try {
      await api.delete(`/project/${projectId}/capture/${captureUUID}/`);
      dispatch(loadCapturesStatistics(projectId));
    } catch (error) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(error)} \n--projectId:${projectId}`,
        error,
        "capture deleting",
      );
      throwParsedApiError(error, "capture deleting");
    }
  }
};

export const updateCapture =
  (projectUUID, captureUUID, data = {}) =>
  async () => {
    try {
      await api.patch(`/project/${projectUUID}/capture/${captureUUID}/`, { ...data });
    } catch (error) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(error)} \n--projectId:${projectUUID}`,
        error,
        "loadCaptures",
      );
      throwParsedApiError(error, "capture updating");
    }
  };

export const loadCapture =
  (projectUUID, captureUUID, captureFileName, isDownload = false) =>
  async (dispatch) => {
    const { baseURL, headers } = api.defaults;
    const fetchOptions = {
      method: "GET",
      mode: "cors",
      withCredentials: true,
      headers: { Authorization: `Bearer ${TokenStorage.getToken()}` },
      redirect: "follow",
    };
    let sensorData = [];
    let wavFile;

    dispatch({ type: LOADING_CAPTURE_SENSOR_DATA });

    const parseResponse = async (response) => {
      if (getFileExtension(captureFileName) === "csv") {
        const csvFile = await response.text();
        if (isDownload) {
          fileDownload(csvFile, captureFileName);
        } else {
          sensorData = CSVToJSON(csvFile);
        }
      } else if (getFileExtension(captureFileName) === "wav") {
        const bufferArray = await response.arrayBuffer();
        if (isDownload) {
          fileDownload(bufferArray, captureFileName);
        } else {
          wavFile = new WaveFile(new Uint8Array(bufferArray));
          const samles = wavFile.getSamples();
          sensorData = [
            Array.from(samles).map((value, index) => ({
              sequence: index,
              name: "channel_0",
              value,
            })),
          ];
        }
      }
    };

    try {
      const URL = `${baseURL}project/${projectUUID}/capture/${captureUUID}/file/local/`;
      const fileResponse = await fetch(URL, fetchOptions);

      // if (fileResponse.url !== URL) {
      //   // catch redirect from aws
      //   const awsFileResponse = await fetch(fileResponse.url, { method: "get" });
      //   await parseResponse(awsFileResponse);
      // } else {
      //   await parseResponse(fileResponse);
      // }
      await parseResponse(fileResponse);
    } catch (error) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(error)} \n--projectId:${projectUUID}`,
        error,
        "loadCaptures",
      );
      throwParsedApiError(error, "capture loading");
    }
    dispatch({ type: SET_CAPTURE_SENSOR_DATA, payload: [] });
    return [sensorData, wavFile];
  };

export const uploadCapture = (projectUUID, file, name) => async (dispatch) => {
  /**
   * @return: captureUUID
   */
  const formData = new FormData();
  let captureData = {};

  formData.append("name", name);
  formData.append("file", file);
  formData.append("asynchronous", true);

  try {
    captureData = await api.post(`/project/${projectUUID}/capture/`, formData, {
      "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    });
  } catch (error) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(error)} \n--projectId:${projectUUID}`,
      error,
      "loadCaptures",
    );
    throwParsedApiError(error, "capture uploading");
  }
  return captureData?.data?.uuid || "";
};
