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

import api from "store/api";
import logger from "store/logger";
import helper from "store/helper";
import { UPDATE_ITERATION_METRICS, CLEAR_ITERATION_METRICS } from "../actionTypes";

export const loadIterationMetrics = (projectUuid, pipelineUuid) => async (dispatch) => {
  try {
    const { data } = await api.get(
      `/project/${projectUuid}/sandbox/${pipelineUuid}/automl-iteration-metrics/`,
    );
    dispatch({ type: UPDATE_ITERATION_METRICS, payload: Array.isArray(data) ? data : [] });
  } catch (err) {
    logger.logError("", helper.getResponseErrorDetails(err), err, "loadIterationmetrics");
  }
};

export const clearIterationMetrics = () => {
  return { type: CLEAR_ITERATION_METRICS };
};
