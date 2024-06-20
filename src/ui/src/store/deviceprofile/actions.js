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
import {
  STORE_KNOWLEDGEPACK_PROFILE,
  CLEAR_KNOWLEDGEPACK_PROFILE,
  LOADING_KNOWLEDGEPACK_PROFILE,
} from "./actionTypes";

export const loadDeviceProfileInformation =
  (projectId, kpId, processorId, hardwareAccelerator) => async (dispatch) => {
    let deviceProfileInfo = {};

    const params = {};
    const hasProject = !helper.isNullOrEmpty(projectId);
    const hasKp = !helper.isNullOrEmpty(kpId);

    if (hasProject && hasKp) {
      dispatch({
        type: LOADING_KNOWLEDGEPACK_PROFILE,
      });
      const url = `/project/${projectId}/knowledgepack/${kpId}/report/resource_summary/`;

      if (!helper.isNullOrEmpty(processorId)) {
        params.processor = processorId;
      }
      if (!helper.isNullOrEmpty(hardwareAccelerator)) {
        params.accelerator = hardwareAccelerator;
      }
      try {
        const { data: responseBody } = await api.get(url, { params });
        deviceProfileInfo = JSON.parse(responseBody);
        dispatch({
          type: STORE_KNOWLEDGEPACK_PROFILE,
          deviceProfileInfo,
        });
      } catch (err) {
        logger.logError(
          "",
          `${helper.getResponseErrorDetails(
            err,
          )} \n--projectId: ${projectId} kpId: ${kpId} processorId:${processorId}`,
          err,
          "loadDeviceProfileInformation",
        );
        dispatch({
          type: CLEAR_KNOWLEDGEPACK_PROFILE,
        });
      }
    }
  };

export const clearDeviceProfileInformation = () => (dispatch) => {
  dispatch({ type: CLEAR_KNOWLEDGEPACK_PROFILE });
};
