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

import api, { throwParsedApiError } from "store/api";

import logger from "../logger";
import helper from "../helper";
import { FEATURE_ANALYSIS_LIST_LOADING } from "./actionTypes";

export const loadFeatureAnalysisList = (projectUUID, modelUUID) => async (dispatch) => {
  try {
    dispatch({ type: FEATURE_ANALYSIS_LIST_LOADING });
    const { data } = await api.get(`/project/${projectUUID}/featurefile-analysis/${modelUUID}/`);
    return data;
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(
        err,
      )} \n--projectUUID:${projectUUID}\n--featureFileUUID:${modelUUID}`,
      err,
      "loadFeatureVectorData",
    );
    throwParsedApiError(err, `Failed to loadFeatureAlalisies modelUUID: ${modelUUID}`);
  }
  return [];
};

export const generateFeatureAnalysis =
  (projectUUID, modelUUID, requestPayload) => async (dispatch) => {
    try {
      dispatch({ type: FEATURE_ANALYSIS_LIST_LOADING });
      const { data } = await api.post(
        `/project/${projectUUID}/featurefile-analysis/${modelUUID}/`,
        requestPayload,
        { headers: { ...api.headers }, "X-HTTP-Method-Override": "POST" },
      );
      return data;
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          err,
        )} \n--projectUUID:${projectUUID}\n--modelUUID:${modelUUID}`,
        err,
        "loadFeatureVectorData",
      );
      throwParsedApiError(err, `Failed to generateFeatureAnalysis modelUUID: ${modelUUID}`);
    }
    return [];
  };

export const loadFeatureAnalysisData = (projectUUID, featureFileUUID) => async (dispatch) => {
  try {
    dispatch({ type: FEATURE_ANALYSIS_LIST_LOADING });
    const { data } = await api.get(`/project/${projectUUID}/featurefile/${featureFileUUID}/json/`);
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
    throwParsedApiError(err, `Failed to loadFeatureAlalisies featureFileUUID: ${featureFileUUID}`);
  }
  return {};
};
