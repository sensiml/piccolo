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

import api, { setAuthHeader, BaseAPIError, parseApiError } from "store/api";

import { push } from "connected-react-router";

import logger from "store/logger";
import TokenStorage from "services/TokenStorage";

import { ROUTES } from "routers";
import { AUTH_CLIENT_ID, AUTH_CLIENT_SECRET } from "config";
import { loadPlatforms } from "store/platforms/actions";
import { loadPipelineSeeds } from "store/pipelines/actions";
import { loadTransforms } from "store/transforms/actions";
import { loadTeamInfo } from "store/team/actions";
import { loadPlatformLogos } from "store/platformlogos/actions";

import { loadTeamSubscription } from "./loadTeamSubscription";

import { LOG_IN } from "./actionTypes";

const getSuccessRedicectPathName = (_state) => {
  return ROUTES.MAIN.HOME.path;
};

const getFormData = (data) => {
  // reduce to FormData
  return Object.entries(data).reduce((acc, [dataKey, dataVal]) => {
    acc.append(dataKey, dataVal);
    return acc;
  }, new FormData());
};

const setData = (accessToken, refreshToken) => async (dispatch) => {
  await TokenStorage.saveToken(accessToken);
  TokenStorage.saveRefreshToken(refreshToken);
  setAuthHeader(accessToken);

  await dispatch(loadTransforms());

  dispatch(loadPlatformLogos());
  dispatch(loadTeamSubscription());
  dispatch(loadTeamInfo());
  dispatch(loadPlatforms());
  dispatch(loadPipelineSeeds());
};

export const logIn =
  ({ email, password }) =>
  async (dispatch, getState) => {
    const state = getState();

    const reqData = {
      grant_type: "password",
      username: email,
      password,
      client_id: AUTH_CLIENT_ID,
      client_secret: AUTH_CLIENT_SECRET,
    };

    try {
      const response = await api.post("/oauth/token/", getFormData(reqData));
      if (response?.data?.access_token) {
        await dispatch({ type: LOG_IN, userId: email, teamInfo: undefined });
        await dispatch(setData(response.data.access_token, response.data.refresh_token));
        dispatch(
          push({
            pathname: getSuccessRedicectPathName(state),
            state: {
              isConfirmed: true,
            },
          }),
        );

        logger.logInfo("", `user ${email} logged in.`, null, "login");
      } else {
        logger.logError(email, "", "", "Login Error");
        throw new BaseAPIError(400, {
          message: "An error occurred while logging in. Please try again.",
        });
      }
    } catch (error) {
      if (error?.response?.status) {
        throw new BaseAPIError(error.response.status, error.response);
      } else {
        throw new BaseAPIError(500, {
          message: "An error occurred while logging in. Please try again.",
        });
      }
    }
  };

export const logInOauthCallback =
  ({ email, refreshToken, accessToken }) =>
  async (dispatch, getState) => {
    const state = getState();

    try {
      if (accessToken) {
        await dispatch({ type: LOG_IN, userId: email, teamInfo: undefined });
        await dispatch(setData(accessToken, refreshToken));
        dispatch(push({ pathname: getSuccessRedicectPathName(state) }));

        logger.logInfo("", `user ${email} logged in.`, null, "login");
      } else {
        logger.logError(email, "", "", "Login Error");
        throw new BaseAPIError(400, {
          message: "An error occurred while logging in. Please try again.",
        });
      }
    } catch (error) {
      parseApiError(error, "login oauth callback");
    }
  };
