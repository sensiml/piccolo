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
import _ from "lodash";
import logger from "store/logger";
import helper from "store/helper";

import {
  LOADING_TEAM_INFO,
  STORE_TEAM_INFO,
  LOADING_ACCOUNT_API_KEYS,
  STORE_ACCOUNT_API_KEYS,
} from "./actionTypes";

export const loadTeamInfo = () => async (dispatch) => {
  dispatch({ type: LOADING_TEAM_INFO });
  let teamInfo = {};

  try {
    const { data } = await api.get("/team-info/");
    if (!_.isEmpty(data)) {
      teamInfo = data;
    }
  } catch (error) {
    logger.logError("", `${helper.getResponseErrorDetails(error)}\n`, error, "loadTeamInfo");
  }
  dispatch({ type: STORE_TEAM_INFO, payload: teamInfo });
};

export const loadAccountApiKeys = () => async (dispatch) => {
  dispatch({ type: LOADING_ACCOUNT_API_KEYS });
  let userApiKeys = [];

  try {
    const { data } = await api.get("/user-api-keys/");
    if (!_.isEmpty(data)) {
      userApiKeys = data;
    }
  } catch (error) {
    logger.logError("", `${helper.getResponseErrorDetails(error)}\n`, error, "loadAccountApiKeys");
    throwParsedApiError(error, "loadAccountApiKeys");
  }
  dispatch({ type: STORE_ACCOUNT_API_KEYS, payload: userApiKeys });
};

export const createAccountApiKey = (name) => async (dispatch) => {
  let apiKey = "";
  try {
    const { data } = await api.post("/user-api-keys/", { name });
    apiKey = data.api_key;
    dispatch(loadAccountApiKeys());
  } catch (error) {
    logger.logError("", `${helper.getResponseErrorDetails(error)}\n`, error, "loadAccountApiKeys");
    throwParsedApiError(error, "loadAccountApiKeys");
  }
  return apiKey;
};

export const deleteApiKey = (APIKeyUUID) => async (dispatch) => {
  try {
    await api.delete(`/user-api-key/${APIKeyUUID}/`);
    await dispatch(loadAccountApiKeys());
  } catch (error) {
    logger.logError("", `${helper.getResponseErrorDetails(error)}\n`, error, "deleteApiKey");
    throwParsedApiError(error, "deleteApiKey");
  }
};
