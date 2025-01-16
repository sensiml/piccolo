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

/* eslint-disable array-callback-return */
/* eslint-disable no-use-before-define */
import api from "../api";
import helper from "../helper";
import {
  START_CLASSIFIER_RUN,
  END_CLASSIFIER_RUN,
  STOP_CLASSIFIER_RUN,
  STOPPED_CLASSIFIER_RUN,
  ADD_CLASSIFIER_TO_CACHE,
  CLEAR_CLASSIFIER_TO_CACHE,
} from "./actionTypes";

export const submitClassifier =
  (projectId, pipelineId, modelId, selectedCaptureSets, label, kbDescription) =>
  async (dispatch) => {
    try {
      dispatch({
        type: START_CLASSIFIER_RUN,
        status: "SUBMITTING",
        response: null,
      });
      if (
        !helper.isNullOrEmpty(projectId) &&
        !helper.isNullOrEmpty(pipelineId) &&
        !helper.isNullOrEmpty(modelId)
      ) {
        try {
          const captures = selectedCaptureSets
            .filter((sc) => sc.type === "capture")
            .map((sc) => sc?.name);
          const postData = {
            stop_step: false,
            platform: "emulator",
            compare_labels: label || false,
            segmenter: true,
            capture: captures,
            kb_description: kbDescription,
          };

          await api.post(
            `project/${projectId}/sandbox/${pipelineId}/knowledgepack/${modelId}/recognize_signal/`,
            postData,
          );
        } catch (err) {
          dispatch({
            type: END_CLASSIFIER_RUN,
            status: "ERROR",
            response: err.message,
          });
        }
      }
    } catch (error) {
      dispatch({
        type: END_CLASSIFIER_RUN,
        uuid: `Project:${projectId},Pipeline:${pipelineId},Model:${modelId}`,
        status: "ERROR",
        response: error.message,
      });
    }
  };

export const stopClassifierRun = (projectId, pipelineId, modelId) => async (dispatch) => {
  dispatch({
    type: STOP_CLASSIFIER_RUN,
    uuid: modelId,
    status: "STOPPING",
    response: null,
  });
  let dispatchObject = {};
  if (
    !helper.isNullOrEmpty(projectId) &&
    !helper.isNullOrEmpty(pipelineId) &&
    !helper.isNullOrEmpty(modelId)
  ) {
    try {
      await api.delete(
        `project/${projectId}/sandbox/${pipelineId}/knowledgepack/${modelId}/recognize_signal/`,
      );
      dispatchObject = {
        type: STOPPED_CLASSIFIER_RUN,
        uuid: modelId,
        status: "STOPPED",
        response: null,
      };
    } catch (err) {
      dispatchObject = {
        type: END_CLASSIFIER_RUN,
        uuid: modelId,
        status: "ERROR",
        response: err.message,
      };
    }
  }
  dispatch(dispatchObject);
  return dispatchObject;
};

export const clearClassifierCache = () => async (dispatch) => {
  dispatch({
    type: CLEAR_CLASSIFIER_TO_CACHE,
  });
};

const getResults = (pipelineId, modelId, selectedCaptureSets, session, responseBody) => {
  const retResults = {};
  Object.values(selectedCaptureSets).map((sc) => {
    retResults[sc.name] = {
      cacheKey: getCacheKey(pipelineId, modelId, sc.uuid),
      accuracy: {},
      captureUuid: sc.uuid,
      fileName: sc.name,
      results: [],
      ground_truth: [],
      confusion_matrices: {},
      sessions: [],
    };
  });

  if (responseBody.confusion_matrix) {
    Object.keys(responseBody.confusion_matrix).map((s) => {
      Object.keys(responseBody.confusion_matrix[s]).map((k) => {
        if (retResults[k]) {
          retResults[k].confusion_matrices[s] = responseBody.confusion_matrix[s][k];

          retResults[k].accuracy[s] = calculateAccuracy(responseBody.confusion_matrix[s][k]);
          retResults[k].sessions.push(s);
        }
      });
    });
  }

  if (responseBody.results) {
    responseBody.results.map((rb) => {
      if (retResults[rb.Capture]) {
        retResults[rb.Capture].results.push(rb);
      }
    });
  }
  if (responseBody.ground_truth) {
    responseBody.ground_truth.map((rb) => {
      if (retResults[rb.Capture]) {
        retResults[rb.Capture].ground_truth.push(rb);
      }
    });
  }
  return retResults;
};

const calculateAccuracy = (confusionMatrix) => {
  if (!confusionMatrix) return 0;
  let total = 0;
  let common = 0;
  Object.keys(confusionMatrix).map((parentKey) => {
    Object.keys(confusionMatrix[parentKey]).map((childKey) => {
      if (childKey !== "GroundTruth_Total") {
        total += confusionMatrix[parentKey][childKey];
      }
      if (parentKey === childKey || (childKey === "UNK" && parentKey.toLowerCase() === "unknown")) {
        common += confusionMatrix[parentKey][childKey];
      }
    });
  });
  return total !== 0 ? ((common / total) * 100).toFixed(2) : null;
};

const getCacheKey = (pipelineId, modelId, fileUUid) => {
  return `${pipelineId}-${modelId}-${fileUUid}`;
};

export const checkClassifierRunStatus =
  (projectId, pipelineId, modelId, selectedCaptureSets, session) => async (dispatch) => {
    const { data: responseBody } = await api.get(
      `project/${projectId}/sandbox/${pipelineId}/knowledgepack/${modelId}/recognize_signal/`,
    );
    let dispatchObject = {};
    if (responseBody && !responseBody.status) {
      const results = getResults(pipelineId, modelId, selectedCaptureSets, session, responseBody);
      const lastResult = results
        ? results[Object.keys(results)[Object.keys(results).length - 1]]
        : { uuid: "00000000-0000-0000-0000-000000000000", results: [] };
      dispatch({
        type: ADD_CLASSIFIER_TO_CACHE,
        classifierData: results,
      });
      dispatchObject = {
        type: START_CLASSIFIER_RUN,
        uuid: results.uuid,
        status: "SUCCESS",
        response: lastResult,
      };
    } else if (
      (responseBody && responseBody.status === "FAILURE") ||
      responseBody.status === "REVOKED"
    ) {
      dispatchObject = {
        type: END_CLASSIFIER_RUN,
        status: "ERROR",
        response: responseBody,
      };
    } else {
      dispatchObject = {
        type: START_CLASSIFIER_RUN,
        status: responseBody.status,
      };
    }
    dispatch(dispatchObject);
    return dispatchObject;
  };
