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

/* eslint-disable no-console */
/* eslint-disable no-unused-vars */
import axios from "axios";
import { store } from "./index";
import helper from "./helper";

const ERROR = "ERROR";
const WARNING = "WARNING";
const INFO = "INFO";
const DEBUG = "DEBUG";

const _logToServer = async (loglevel, username, message, stacktrace, tag) => {
  if (!username) {
    const state = store.getState();
    // eslint-disable-next-line no-param-reassign
    username = state.auth && state.auth.userId ? state.auth.userId : username;
  }
  const reqData = {
    loglevel,
    username,
    application: "Web Client",
    message,
    stacktrace: Array.isArray(stacktrace) ? stacktrace.join(", ") : JSON.stringify(stacktrace),
    tag,
    browser: navigator.appName,
    client_information: JSON.stringify({
      browserName: navigator.appName,
      browserEngine: navigator.product,
      browserVersion1a: navigator.appVersion,
      browserVersion1b: navigator.userAgent,
      browserLanguage: navigator.language,
      browserOnline: navigator.onLine,
      browserPlatform: navigator.platform,
      sizeDocW: document.width,
      sizeDocH: document.height,
    }),
  };

  const loggerApi = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
    withCredentials: false,
    crossdomain: true,
    headers: {
      Authorization: `Api-Key ${process.env.REACT_APP_LOGGER_API_KEY}`,
    },
  });

  const esc = encodeURIComponent;
  const query = Object.keys(reqData)
    .map((k) => `${esc(k)}=${esc(reqData[k])}`)
    .join("&");

  try {
    await loggerApi.post("/log/", query);
  } catch (_err) {
    console.info(query);
  }
};

const logger = (() => {
  const logConsole = (username, message, stacktrace, tag) => {
    console.log(
      `message:${message}, stacktrace:${
        Array.isArray(stacktrace) ? stacktrace.join(", ") : stacktrace
      }`,
    );
  };

  const logError = (username, message, stacktrace, tag) => {
    _logToServer(ERROR, username, message, stacktrace, tag);
  };

  const logWarning = (username, message, stacktrace, tag) => {
    _logToServer(WARNING, username, message, stacktrace, tag);
  };

  const logInfo = (username, message, stacktrace, tag) => {
    _logToServer(INFO, username, message, stacktrace, tag);
  };

  const logDebug = (username, message, stacktrace, tag) => {
    _logToServer(DEBUG, username, message, stacktrace, tag);
  };

  return {
    logError,
    logWarning,
    logInfo,
    logDebug,
    logConsole,
  };
})();

export default logger;
