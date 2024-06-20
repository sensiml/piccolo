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
  MODEL_FEATURE_VECTORS_LOADING,
  MODEL_FEATURE_VECTORS_STORE,
} from "./actionTypes";

const initialModelsState = { data: [], isFetching: false };

export const modelList = (state = initialModelsState, action) => {
  switch (action.type) {
    case LOADING_MODELS:
      return { data: [], isFetching: true };
    case STORE_MODELS:
      return { data: action.models, isFetching: false };
    default:
      return state;
  }
};

export const selectedModel = (state = "", action) => {
  switch (action.type) {
    case STORE_SELECTED_MODEL:
      return action.selectedModel;
    default:
      return state;
  }
};

const initialModelState = { data: [], isFetching: false };
export const modelData = (state = initialModelState, action) => {
  switch (action.type) {
    case LOADING_MODEL:
      return { data: [], isFetching: true };
    case STORE_MODEL:
      return { data: action.model, isFetching: false };
    case CLEAR_MODEL:
      return initialModelState;
    default:
      return state;
  }
};

const initialModelDowloadState = { isDownloading: false };
export const downloadStatus = (state = initialModelDowloadState, action) => {
  switch (action.type) {
    case STARTING_MODEL_DOWNLOAD:
      return { isDownloading: true };
    case STARTED_MODEL_DOWNLOAD:
      return { isDownloading: true };
    case DOWNLOADING_MODEL:
      return { isDownloading: true };
    case MODEL_DOWNLOADED:
      return { isDownloading: false };
    case MODEL_DOWNLOAD_FAILED:
      return { isDownloading: false };
    case CANCEL_MODEL_DOWNLOAD:
      return { isDownloading: false };
    default:
      return state;
  }
};

const initialFeatureVectorsState = { data: {}, featureFileUUID: "", isFetching: false };
const featureVectors = (state = initialFeatureVectorsState, action) => {
  const { type, payload } = action;
  switch (type) {
    case MODEL_FEATURE_VECTORS_LOADING:
      return { ...initialFeatureVectorsState, isFetching: true };
    case MODEL_FEATURE_VECTORS_STORE:
      return { data: payload.data, featureFileUUID: payload.featureFileUUID, isFetching: false };
    default:
      return state;
  }
};

export default combineReducers({
  selectedModel,
  modelList,
  modelData,
  featureVectors,
  downloadStatus,
});
