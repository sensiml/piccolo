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
import { store } from "store";
// eslint-disable-next-line import/no-extraneous-dependencies
import qs from "qs";

import { AUTH_CLIENT_ID, AUTH_CLIENT_SECRET } from "config";
import { RESET_APP } from "store/auth/actions/actionTypes";

export { default as BaseAPIError } from "./api.error.base";
export { default as throwParsedApiError } from "./throwParsedApiError";
export { default as parseApiError } from "./parseApiError";

export const refreshUrl = "/oauth/token/";

let isRefreshing = false;
let refreshSubscribers = [];

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  withCredentials: true,
  crossdomain: true,
  headers: {
    Authorization: `Bearer ${TokenStorage.getToken()}`,
  },
});

api.paramsSerializer = (params) => qs.stringify(params);

api.interceptors.request.use((config) => {
  if (!config.headers.Authorization || config.headers.Authorization.includes("null")) {
    // eslint-disable-next-line no-param-reassign
    config.headers.Authorization = `Bearer ${TokenStorage.getToken()}`;
  }
  return config;
});

const subscribeTokenRefresh = (cb) => {
  refreshSubscribers.push(cb);
};

const onRrefreshed = (token) => {
  refreshSubscribers.map((cb) => cb(token));
  refreshSubscribers = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 403) {
      if (error.config.url.includes("auth")) {
        // Refresh token has failed or auth endpoint return 401 => Logout the user
        store.dispatch({ type: RESET_APP });
        throw error;
      } else if (error.response?.data?.detail === "Authentication credentials were not provided.") {
        // refresh token
        try {
          const originalRequest = error.config;

          const retryOrigReq = new Promise((resolve) => {
            subscribeTokenRefresh((token) => {
              // replace the expired token and retry
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(api(originalRequest));
            });
          });

          if (!isRefreshing) {
            isRefreshing = true;
            const refreshToken = TokenStorage.getRefreshToken();
            const response = await api({
              method: "post",
              url: refreshUrl,
              params: {
                grant_type: "refresh_token",
                client_id: AUTH_CLIENT_ID,
                "client-secret": AUTH_CLIENT_SECRET,
                refresh_token: refreshToken,
              },
            });
            isRefreshing = false;

            await TokenStorage.saveToken(response.data.access_token);
            TokenStorage.saveRefreshToken(response.data.refresh_token);
            api.defaults.headers.common.Authorization = `Bearer ${response.data.access_token}`;

            onRrefreshed(response.data.access_token);
          }

          return retryOrigReq;
        } catch (e) {
          // Refresh has failed - reject the original request and logout
          store.dispatch({ type: RESET_APP });
          throw error;
        }
      }
    }
    // If error was not 401 just reject as is
    throw error;
  },
);

export const setAuthHeader = (accessToken) => {
  api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
};

export const resetAuthHeader = () => {
  api.defaults.headers.common.Authorization = undefined;
};

export default api;
