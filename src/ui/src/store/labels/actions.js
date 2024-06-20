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

import { getColorToDCLFormat } from "utils";

import api, { throwParsedApiError } from "store/api";
import logger from "store/logger";
import helper from "store/helper";
import { DEFALULT_LABEL } from "store/labels/domain";

import { STORE_LABELS, LOADING_LABELS, SET_SELECTED_LABEL } from "./actionTypes";

export const loadLabels = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_LABELS });
  let labels = [];
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectId}/label/`);
      labels = responseBody;
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectId}`,
        err,
        "loadLabels",
      );
    }
  }
  dispatch({ type: STORE_LABELS, labels });
};

export const setSelectedLabel = (selectedLabelUUID) => {
  return { type: SET_SELECTED_LABEL, selectedLabelUUID };
};

export const createDefaultLabel = (projectUUID) => async (dispatch) => {
  let newLabelUUID = "";
  if (!helper.isNullOrEmpty(projectUUID)) {
    const labelData = {
      name: DEFALULT_LABEL.name,
      metadata: false,
      type: "string",
      is_dropdown: "true",
    };
    try {
      const { data } = await api.post(`/project/${projectUUID}/label/`, labelData);
      newLabelUUID = data?.uuid;
      dispatch(loadLabels(projectUUID));
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
        err,
        "createLabel",
      );
    }
  }
  return newLabelUUID;
};

export const createLabelValue =
  (projectUUID, labelUUID, { value, color }) =>
  async (dispatch) => {
    let newLabelValueUUID = "";
    let _labelUUID = labelUUID;
    if (!helper.isNullOrEmpty(projectUUID)) {
      try {
        if (!_labelUUID) {
          dispatch({ type: LOADING_LABELS });
          _labelUUID = await dispatch(createDefaultLabel(projectUUID));
        }
        if (_labelUUID) {
          const response = await api.post(
            `/project/${projectUUID}/label/${_labelUUID}/labelvalue/`,
            {
              value,
              color: getColorToDCLFormat(color),
            },
          );
          await dispatch(loadLabels(projectUUID));
          newLabelValueUUID = response.data?.uuid || "";
        }
      } catch (err) {
        logger.logError(
          "",
          `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
          err,
          "createLabel",
        );
        throwParsedApiError(err, "createLabel");
      }
    }
    return newLabelValueUUID || "";
  };

export const updateLabelValue =
  (projectUUID, labelUUID, labelValueUUID, { value, color }) =>
  async (dispatch) => {
    if (!helper.isNullOrEmpty(projectUUID)) {
      try {
        await api.patch(
          `/project/${projectUUID}/label/${labelUUID}/labelvalue/${labelValueUUID}/`,
          {
            value,
            color: getColorToDCLFormat(color),
          },
        );
        await dispatch(loadLabels(projectUUID));
      } catch (err) {
        logger.logError(
          "",
          `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
          err,
          "updateLabelValue",
        );
        throwParsedApiError(err, "updateLabelValue");
      }
    }
  };

export const deleteLabelValue = (projectUUID, labelUUID, labelValueUUID) => async (dispatch) => {
  if (!helper.isNullOrEmpty(projectUUID)) {
    try {
      await api.delete(`/project/${projectUUID}/label/${labelUUID}/labelvalue/${labelValueUUID}/`);
      await dispatch(loadLabels(projectUUID));
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)} \n--projectId:${projectUUID}`,
        err,
        "createLabel",
      );
    }
  }
};
