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

import { combineReducers } from "redux";
import { MESSAGE_TYPES } from "consts";
import {
  STORE_PIPELINE_STEPS,
  CLEAR_PIPELINE_STEPS,
  STORE_PIPELINE_JSON,
  CLEAR_PIPELINE_JSON,
  STORE_ALERT_BUILDER,
  CLEAR_ALERT_BUILDER,
  STORE_PIPELINE_VALIDATION_ERROR,
  CLEAR_PIPELINE_VALIDATION_ERROR,
  SET_IS_ADVANCED_BUILDING,
  SET_IS_SELECT_SCREEN_GRID_VIEW,
  SET_LOADING_PIPELINE_STEPS,
} from "./actionTypes";

/*
initialPipelineStep = {
  PipelineUUID: {
    ...pipelineData
  }
}
*/
const initialPipelineStepData = {};
const initialPipelineJsonData = {};

export const pipelineStepData = (state = initialPipelineStepData, action) => {
  const { type, payload } = action;
  switch (type) {
    case STORE_PIPELINE_STEPS:
      return { ...state, ...payload };
    case CLEAR_PIPELINE_STEPS:
      return initialPipelineStepData;
    default:
      return state;
  }
};

export const pipelineJsonData = (state = initialPipelineJsonData, action) => {
  const { type, payload } = action;
  switch (type) {
    case STORE_PIPELINE_JSON:
      return { ...state, ...payload };
    case CLEAR_PIPELINE_JSON:
      return initialPipelineJsonData;
    default:
      return state;
  }
};

export const isAdvancedBuilding = (state = false, action) => {
  const { type, payload } = action;
  switch (type) {
    case SET_IS_ADVANCED_BUILDING:
      return payload;
    default:
      return state;
  }
};

export const isSelectScreenGridView = (state = true, action) => {
  const { type, payload } = action;
  switch (type) {
    case SET_IS_SELECT_SCREEN_GRID_VIEW:
      return payload;
    default:
      return state;
  }
};

export const loadingPipelineSteps = (state = { isLoading: false, message: "" }, action) => {
  const { type, payload } = action;
  switch (type) {
    case SET_LOADING_PIPELINE_STEPS:
      return payload;
    default:
      return state;
  }
};

const initialAlertBuilderState = {
  message: "",
  parameters: [],
  type: MESSAGE_TYPES.INFO,
  header: "",
};

export const alertBuilder = (state = initialAlertBuilderState, action) => {
  const { type, payload } = action;
  switch (type) {
    case STORE_ALERT_BUILDER:
      return payload;
    case CLEAR_ALERT_BUILDER:
      return initialAlertBuilderState;
    default:
      return state;
  }
};

export const pipelineValidationError = (state = "", action) => {
  const { type, payload } = action;
  switch (type) {
    case STORE_PIPELINE_VALIDATION_ERROR:
      return payload;
    case CLEAR_PIPELINE_VALIDATION_ERROR:
      return "";
    default:
      return state;
  }
};

export default combineReducers({
  pipelineStepData,
  pipelineJsonData,
  isAdvancedBuilding,
  isSelectScreenGridView,
  loadingPipelineSteps,
  alertBuilder,
  pipelineValidationError,
});
