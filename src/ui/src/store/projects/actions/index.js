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

import axios from "axios";
import TokenStorage from "services/TokenStorage";

import api, { throwParsedApiError } from "store/api";
import logger from "store/logger";
import helper from "store/helper";

import { createLabelValue } from "store/labels/actions";
import { DEFALULT_LABEL } from "store/labels/domain";
import { createDefaultMetadata } from "store/metadata/actions";

import {
  DELETING_PROJECT,
  DELETED_PROJECT,
  LOADING_PROJECTS,
  LOADING_PROJECT_STATISTICS,
  STORE_PROJECT_STATISTICS,
  STORE_PROJECTS,
  STORE_LAST_SELECTED_PROJECT,
  STORE_SELECTED_PROJECT,
  OPTIMIZED_PROJECT,
  UPDATING_PROJECT,
  UPDATED_PROJECT,
} from "../actionTypes";

export { default as loadProjectSummaryData } from "./loadProjectSummaryData";
export { default as loadProjectData } from "./loadProjectData";
export { default as clearProjectSelectedData } from "./clearProjectSelectedData";

export const loadProjects = () => async (dispatch) => {
  dispatch({ type: LOADING_PROJECTS });
  let projects = [];
  try {
    const { data: responseBody } = await api.get("/project-summary/");
    projects = helper.sortObjects(responseBody, "created_at", false, "dsc");
  } catch (err) {
    logger.logError("", helper.getResponseErrorDetails(err), err, "loadProjects");
  }
  dispatch({ type: STORE_PROJECTS, projects });
};

export const deleteProject = (projectId) => async (dispatch) => {
  dispatch({ type: DELETING_PROJECT });
  let projects = [];
  try {
    await api.delete(`/project/${projectId}/`);
    const { data: responseBody } = await api.get("/project-summary/");
    projects = helper.sortObjects(responseBody, "created_at", false, "dsc");
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId}`,
      err,
      "deleteProject",
    );
    throw err;
  }
  dispatch({ type: DELETED_PROJECT, projects });
};

export const createProject = (name) => async (dispatch) => {
  try {
    const response = await api.post(`/project/`, { name });
    dispatch(loadProjects());
    dispatch(
      createLabelValue(response?.data?.uuid, undefined, {
        value: DEFALULT_LABEL.value,
        color: DEFALULT_LABEL.color,
      }),
    );
    dispatch(createDefaultMetadata(response?.data?.uuid));
  } catch (err) {
    logger.logError("", err, `${helper.getResponseErrorDetails(err)}}`, "createProject");
    throwParsedApiError(err, "createProject");
  }
};

export const updateProject = (project) => async (dispatch) => {
  dispatch({ type: UPDATING_PROJECT });
  const projectId = project.uuid;
  let errToThrow = null;

  try {
    api.put(`/project/${projectId}/`, project);
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId}`,
      err,
      "updateProject",
    );
    errToThrow = err;
  }
  let projects = [];
  try {
    const { data: responseBody } = await api.get("/project-summary/");
    projects = helper.sortObjects(responseBody, "name");
  } catch (err) {
    logger.logError("", helper.getResponseErrorDetails(err), err, "loadProjects");
  }

  dispatch({ type: UPDATED_PROJECT, projects });
  if (errToThrow) {
    throw errToThrow;
  }
};

export const uploadImage = (imageUrl, imageName, projectUUID, onUploadSuccess) => async () => {
  const block = imageUrl.split(";");

  // Get the content type of the image
  const contentType = block[0].split(":")[1]; // In this case "image/gif"

  // get the real base64 content of the file
  const realData = block[1].split(",")[1]; // In this case "R0lGODlhPQBEAPeoAJosM...."

  // Convert it to a blob to upload
  const blob = helper.b64toBlob(realData, contentType);

  const formData = new FormData();
  formData.append("file", blob);
  formData.append("name", imageName);

  const fileApi = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
    withCredentials: false,
    crossdomain: true,
    headers: {
      Authorization: `Bearer ${TokenStorage.getToken()}`,
      "Content-Type": "multipart/form-data",
    },
  });
  fileApi.post(`project/${projectUUID}/image/`, formData);
  onUploadSuccess();
};

export const loadProjectStatistics = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_PROJECT_STATISTICS });
  let statistics = [];
  try {
    const { data: responseBody } = await api.get(`/project/${projectId}/statistics/`);
    statistics = responseBody;
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId}`,
      err,
      "loadProjectStatistics",
    );
  }
  dispatch({ type: STORE_PROJECT_STATISTICS, statistics });
};

export const setSelectedProject = (project) => {
  return {
    type: STORE_SELECTED_PROJECT,
    selectedProject: project || {},
  };
};

export const setLastSelectedProject = (project, team, userId) => (dispatch) => {
  if (project && team && userId) {
    dispatch({
      type: STORE_LAST_SELECTED_PROJECT,
      selectedProject: { [`${team}-${userId}`]: project },
    });
  }
};

export const optimizeProject = (projectUuId) => async (dispatch) => {
  if (!helper.isNullOrEmpty(projectUuId)) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectUuId}/`);
      if (responseBody.optimized === false) {
        await api.post(`/project/${projectUuId}/profile/`);
      }
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)}\n--projectId:${projectUuId}`,
        err,
        "optimizeProject",
      );
      throw err;
    }
  }
  dispatch({ type: OPTIMIZED_PROJECT, uuid: projectUuId });
};
