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

import helper from "store/helper";
import logger from "store/logger";

import { SEGMENTS_STORE } from "./actionTypes";

export const loadSegments = (projectUUID) => async (dispatch) => {
  try {
    const { data } = await api.get(`/project/${projectUUID}/label-relationship/`);
    dispatch({ type: SEGMENTS_STORE, payload: data });
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(err)} \n--projectUUID:${projectUUID}`,
      err,
      "loadFeatureVectorData",
    );
    throwParsedApiError(err, `Failed to loadSegments projectUUID: ${projectUUID}`);
  }
};
