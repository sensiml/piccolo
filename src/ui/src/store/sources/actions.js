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
import { STORE_SOURCES, LOADING_SOURCES } from "./actionTypes";

export const loadSources = (projectId) => async (dispatch) => {
  dispatch({ type: LOADING_SOURCES });
  let sourceValues = [];
  if (!helper.isNullOrEmpty(projectId)) {
    try {
      const { data: responseBody } = await api.get(`/project/${projectId}/`);

      if (responseBody && responseBody.capture_sample_schema) {
        sourceValues = Object.keys(responseBody.capture_sample_schema);
      }
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(err)}\n--projectId:${projectId}`,
        err,
        "loadSources",
      );
    }
  }
  dispatch({ type: STORE_SOURCES, sources: sourceValues });
};
