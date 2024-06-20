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

import api, { BaseAPIError, parseApiError } from "store/api";
import logger from "store/logger";
import helper from "store/helper";
import {
  ADD_UPDATE_QUERY,
  LOADING_QUERIES,
  STORE_QUERIES,
  STORE_SELECTED_QUERY,
  LOADING_QUERY,
  UNCAUGHT_ERROR_QUERY_LIST,
  UNCAUGHT_ERROR_QUERY_DATA,
  STORE_QUERY,
  DELETING_QUERY,
  QUERY_DELETED,
  LOADING_QUERY_FEATURE_STATS,
  STORE_QUERY_FEATURE_STATS,
  UNCAUGHT_ERROR_QUERY_FEATURE_STATS,
  RESET_QUERY_FEATURE_STATS,
  BUILD_QUERY_CACHE,
} from "../actionTypes";

import loadQueryCacheStatus from "./loadQueryCacheStatus";
import clearQueryCacheStatus from "./clearQueryCacheStatus";

export { loadQueryCacheStatus, clearQueryCacheStatus };

export const loadQueries = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_QUERIES });
  let queries = [];
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectId}/query/`);
      queries = helper.sortObjects(responseBody, "name");
      queries.forEach((element, index, theArray) => {
        // eslint-disable-next-line no-param-reassign
        theArray[index].task_status =
          element.task_status == null ? null : element.task_status.toUpperCase();
      });
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId}`,
        err,
        "loadQueries",
      );
      dispatch({ type: UNCAUGHT_ERROR_QUERY_LIST, error: err });
    }
  }
  dispatch({ type: STORE_QUERIES, queries });
};

export const addToQueryManualObj = (queryData) => async (dispatch, getState) => {
  const state = getState();
  const queries = state.queries?.queryList?.data || [];
  if (!queries.find((q) => q.name === queryData.name)) {
    queries.push(queryData);
  }
  return { type: STORE_QUERIES, queries };
};

export const deleteQuery = (projectId, queryId) => async (dispatch) => {
  dispatch({ type: DELETING_QUERY, uuid: queryId });
  let response = { status: "" };
  try {
    if (!helper.isNullOrEmpty(projectId) && !helper.isNullOrEmpty(queryId)) {
      await api.delete(`/project/${projectId}/query/${queryId}/`);
      dispatch({
        type: QUERY_DELETED,
        uuid: queryId,
      });
      response = { status: "success" };
    }
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId}, queryId:${queryId}`,
      err,
      "deleteQuery",
    );
    response = { status: "error", details: parseApiError(err, "Failed to delete query") };
  }
  return response;
};

export const setSelectedQuery = (queryId) => {
  return {
    type: STORE_SELECTED_QUERY,
    selectedQuery: queryId,
  };
};

const initilaizeQueryData = (queryData, responseBody) => {
  let resultQueryData = { ...queryData };
  if (responseBody && responseBody.uuid) {
    resultQueryData = {
      query: responseBody.uuid || "",
      name: responseBody.name || "",
      label: responseBody.label_column || "",
      session: responseBody.segmenter_id || "",
      metadata: responseBody.metadata_columns || [],
      metadata_filter: responseBody.metadata_filter,
      source: responseBody.columns || [],
      plot: "segment", // default plot selected
      summary_statistics: responseBody.summary_statistics || [],
      segment_statistics: {},
      cache: responseBody.cache || [],
      task_status: _.isEmpty(responseBody.task_status)
        ? null
        : responseBody.task_status.toUpperCase(),
    };
  }
  return { ...resultQueryData };
};

export const buildQueryCache = (projectId, queryId) => async (dispatch, getState) => {
  const state = getState();
  const queryList = state.queries?.queryList?.data || [];

  if (!projectId) {
    throw new Error("Provide projectId pamameter");
  }
  if (!queryId) {
    throw new Error("Provide queryId pamameter");
  }
  dispatch({ type: BUILD_QUERY_CACHE, queryList });

  try {
    await api.delete(`/project/${projectId}/query/${queryId}/cache/`);
    await api.post(`/project/${projectId}/query/${queryId}/cache/`);
    const response = await api.get(`/project/${projectId}/query/${queryId}/`);
    const queryIndex = queryList.findIndex((queryEl) => queryEl.uuid === queryId);

    if (queryIndex >= 0) {
      queryList[queryIndex] = { ...response.data };
    } else {
      queryList.push(response.data);
    }
    dispatch({ type: STORE_QUERIES, queries: queryList });
  } catch (error) {
    if (error?.response) {
      logger.logError(
        "",
        `${error.response?.config?.url} ${error.response?.data}`,
        error.response?.data,
        "postQueryCash",
      );
      throw new BaseAPIError(error.response?.status, error.response);
    } else {
      throw new BaseAPIError(500, "Could not send update request");
    }
  }
};

// eslint-disable-next-line consistent-return
export const addQueryStats = async (projectId, queryData) => {
  // eslint-disable-next-line no-param-reassign
  queryData.segmentsCharts = queryData.summary_statistics?.segments || {};

  // eslint-disable-next-line no-param-reassign
  queryData.samplesCharts = queryData.summary_statistics?.samples || {};

  if (queryData.summary_statistics?.samples) {
    return queryData;
  }

  try {
    const { data: responseBody } = await api.get(
      `/project/${projectId}/query/${queryData.query}/summary-statistics/`,
    );

    if (!_.isEmpty(responseBody)) {
      const { segments, samples } = responseBody;
      // eslint-disable-next-line no-param-reassign
      queryData.segmentsCharts = segments || {};
      // eslint-disable-next-line no-param-reassign
      queryData.samplesCharts = samples || {};
    }
    return queryData;
  } catch (err) {
    if (err.response && err.response.data) {
      // eslint-disable-next-line max-len
      const errorMsg = `${err.response.data.category} ${err.response.data.err}\n--project:${projectId} query:${queryData.query}`;
      logger.logError("", errorMsg, err, "addQueryStats");
      throw new BaseAPIError(errorMsg);
    }
  }

  return queryData;
};

export const loadQueryStatistic = (projectUUID, queryUUID) => async () => {
  let data = {};
  try {
    const respose = await api.get(`/project/${projectUUID}/query/${queryUUID}/summary-statistics/`);
    data = respose.data;
  } catch (err) {
    if (err.response && err.response.data) {
      // eslint-disable-next-line max-len
      const errorMsg = `${err.response.data.category} ${err.response.data.err}\n--project:${projectUUID} query:${queryUUID}`;
      logger.logError("", errorMsg, err, "addQueryStats");
      throw new BaseAPIError(errorMsg);
    }
  }
  return data;
};

const getHistogramSize = (data, nbins) => {
  const min = 0;
  const max = _.max(data);
  const size = max / nbins;

  return { size, max, min };
};

function histogram(data, min, max, size) {
  const bins = Math.ceil((max - min + 1) / size);

  const hist = new Array(bins).fill(0);
  const x = new Array(bins).fill(0);

  // eslint-disable-next-line no-restricted-syntax
  for (const item of data) {
    hist[Math.floor((item - min) / size)]++;
  }

  x[0] = Math.floor(size / 2);
  for (let i = 0; i < bins; i++) {
    x[i] = Math.floor(min + size / 2 + size * i);
  }

  return { x, histogram: hist };
}

// eslint-disable-next-line consistent-return
export const addQuerySegmentStats = async (projectId, queryData) => {
  try {
    const { data: responseBody } = await api.get(
      `/project/${projectId}/query/${queryData.query}/statistics/`,
    );

    if (!_.isEmpty(responseBody) && _.isArray(responseBody["Segment Length"])) {
      const nbins = 24;
      const histParams = getHistogramSize(responseBody["Segment Length"], nbins);
      const labels = responseBody[queryData.label] || [];

      // eslint-disable-next-line no-param-reassign
      queryData.segment_statistics = labels.reduce((acc, label) => {
        const values = responseBody["Segment Length"].filter(
          (_lenght, index) => labels[index] === label,
        );
        acc[label] = histogram(values, histParams.min, histParams.max, histParams.size);
        return acc;
      }, {});
    }

    return queryData;
  } catch (err) {
    if (err.response && err.response.data) {
      // eslint-disable-next-line max-len
      const errorMsg = `${err.response.data.category} ${err.response.data.err}\n--project:${projectId} query:${queryData.query}`;
      logger.logError("", errorMsg, err, "addQuerySegmentStats");

      throw new BaseAPIError(errorMsg);
    }
  }
};

export const resetFeatureStats = () => async (dispatch) => {
  dispatch({ type: RESET_QUERY_FEATURE_STATS });
};

export const loadQuerySegmentStatistic = (projectUUID, queryUUID) => async (_dispatch) => {
  try {
    const { data } = await api.get(`/project/${projectUUID}/query/${queryUUID}/statistics/`);
    return data;
  } catch (err) {
    if (err.response && err.response.data) {
      // eslint-disable-next-line max-len
      const errorMsg = `${err.response.data.category} ${err.response.data.err}\n--project:${projectUUID} query:${queryUUID}`;
      logger.logError("", errorMsg, err, "loadQuerySegmentStatistic");

      throw new BaseAPIError(errorMsg);
    }
  }
  return {};
};

export const loadFeatureStats = (projectId, queryId) => async (dispatch) => {
  const featureStats = { status: "success", msg: "", stats: {} };
  dispatch({ type: LOADING_QUERY_FEATURE_STATS });
  try {
    const { data: responseBody } = await api.get(
      `/project/${projectId}/query/${queryId}/featurestatistics/`,
    );
    if (responseBody.status) {
      if (responseBody.status === "FAILURE") {
        featureStats.status = "failed";
        featureStats.msg =
          responseBody.errors && responseBody.errors.length > 0
            ? responseBody.errors[0].name
            : "Failed Generating Statistics";
      } else {
        featureStats.status = "Running";
        featureStats.msg = "Feature Statistics are not ready, please try again in a few minutes.";
      }
    }
    featureStats.stats = responseBody;
    dispatch({
      type: STORE_QUERY_FEATURE_STATS,
      featureStatistics: featureStats,
    });
  } catch (err) {
    if (err.response && err.response.data) {
      const errorMsg = `${err.response.data.category}${err.response.data.err}`;
      logger.logError(
        "",
        `${errorMsg}\n--projectId:${projectId}, queryId:${queryId}`,
        err,
        "loadFeatureStats",
      );
      dispatch({
        type: UNCAUGHT_ERROR_QUERY_FEATURE_STATS,
        error: err,
      });
    }
  }
};

export const loadQuery =
  (projectId, queryId, loadStats = true) =>
  async (dispatch) => {
    let queryData = {
      query: "",
      name: "",
      session: "",
      label: "",
      metadata: [],
      source: [],
      plot: "",
      metadata_filter: "",
    };
    const status = { isSuccessFull: true, errorMessage: "" };
    dispatch({ type: LOADING_QUERY });
    if (!helper.isNullOrEmpty(projectId) && !helper.isNullOrEmpty(queryId)) {
      try {
        const { data: responseBody } = await api.get(`/project/${projectId}/query/${queryId}/`);
        queryData = initilaizeQueryData(queryData, responseBody);
        if (loadStats === true && queryData.task_status !== "FAILED") {
          await addQueryStats(projectId, queryData);
        }
        if (loadStats === true && queryData.task_status !== "FAILED") {
          await addQuerySegmentStats(projectId, queryData);
        }

        await dispatch(loadQueryCacheStatus(projectId, queryId));
      } catch (err) {
        logger.logError(
          "",
          `${helper.getResponseErrorDetails(
            err,
          )}\n--projectId:${projectId}, queryId:${queryId}, loadStats:${loadStats}`,
          err,
          "loadQuery",
        );
        status.isSuccessFull = false;
        status.errorMessage = err.message;
        dispatch({
          type: UNCAUGHT_ERROR_QUERY_DATA,
          error: err,
          queryDetails: queryData,
        });
        if (err.response && err.response.status === 403) {
          // eslint-disable-next-line no-throw-literal
          throw { error: { response: err.response } };
        }
        return status;
      }
    }
    dispatch(setSelectedQuery(queryId === undefined ? null : queryId));
    dispatch({
      type: STORE_QUERY,
      queryDetails: queryData,
    });
    return status;
  };

export const addOrUpdateQuery =
  (
    projectId,
    queryId,
    name,
    sourceColumns,
    metadataColumns,
    segmentId,
    metadataFilter,
    labelName,
  ) =>
  async (dispatch) => {
    const queryInfo = {
      name,
      columns: sourceColumns,
      metadata_columns: metadataColumns,
      metadata_filter: metadataFilter || "",
      segmenter_id: segmentId,
      label_column: labelName,
      combine_labels: null,
    };
    let queryData = {
      query: "",
      name: "",
      session: "",
      label: "",
      metadata: [],
      source: [],
      plot: "",
      metadata_filter: "",
    };

    const status = { isSuccessFull: true, errorMessage: "", newUuid: null };

    if (!helper.isNullOrEmpty(projectId)) {
      try {
        if (helper.isNullOrEmpty(queryId)) {
          const { data: responseBody } = await api.post(`/project/${projectId}/query/`, queryInfo);
          queryData = initilaizeQueryData(queryData, responseBody);
        } else {
          const { data: responseBody } = await api.put(
            `/project/${projectId}/query/${queryId}/`,
            queryInfo,
          );
          queryData = initilaizeQueryData(queryData, responseBody);
        }
        status.newUuid = queryData.query;
        await addQueryStats(projectId, queryData);
        dispatch({ type: STORE_SELECTED_QUERY, selectedQuery: queryData.query });

        if (queryData.task_status !== "FAILED") {
          await addQuerySegmentStats(projectId, queryData);
        }
        if (!helper.isNullOrEmpty(queryId)) {
          await dispatch(loadQueryCacheStatus(projectId, queryId));
        }
      } catch (err) {
        logger.logError(
          "",
          `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId},queryId:${queryId} `,
          err,
          "addOrUpdateQuery",
        );
        status.isSuccessFull = false;
        status.errorMessage = err.message;
        dispatch({ type: UNCAUGHT_ERROR_QUERY_DATA, error: err });
        if (err.response && err.response.status === 403) {
          // eslint-disable-next-line no-throw-literal
          throw { error: { response: err.response } };
        }
        return status;
      }
    }
    dispatch({ type: ADD_UPDATE_QUERY, queryDetails: queryData });
    return status;
  };
