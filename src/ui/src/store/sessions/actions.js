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

import api from "../api";
import logger from "../logger";
import helper from "../helper";
import { STORE_SESSIONS, LOADING_SESSIONS, SET_SELECTED_SESSION } from "./actionTypes";

export const loadSessions = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_SESSIONS });
  let sessions = [];
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectId}/segmenter/`);
      sessions = responseBody;
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId}`,
        err,
        "loadSessions",
      );
    }
  }
  dispatch({ type: STORE_SESSIONS, sessions });
};

export const createSession = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_SESSIONS });
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      await api.post(`/project/${projectId}/segmenter/`, {
        name: "Training Session",
        custom: true,
      });
      dispatch(loadSessions(projectId));
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId}`,
        err,
        "createSession",
      );
    }
  }
};

export const setSelectedSession = (selectedSessionUUID) => {
  return { type: SET_SELECTED_SESSION, selectedSessionUUID };
};
