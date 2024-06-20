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

import _ from "lodash";
import api from "store/api";
import i18n from "i18n";
import logger from "store/logger";

import {
  CLEAR_QUERY_CACHE_STATUS,
  LOADING_QUERY_CACHE_STATUS,
  STORE_QUERY_CACHE_STATUS,
} from "../actionTypes";
import { CACHE_STATUSES } from "../const";

export const loadQueryCacheStatus = (projectId, queryId) => async (dispatch) => {
  if (!projectId) {
    throw new Error("Provide projectId pamameter");
  }
  if (!queryId) {
    throw new Error("Provide queryId pamameter");
  }

  // eslint-disable-next-line no-unused-vars
  const getBuildStatus = (status) => {
    if (!status) {
      return CACHE_STATUSES.NOT_BUILT;
    }
    if (!_.values(CACHE_STATUSES).includes(status)) {
      // for unknow status
      return CACHE_STATUSES.NOT_BUILT;
    }
    return status;
  };

  const getBuildMessage = (buildStatus, buildMessage) => {
    /**
     * extract build message to show in priority
     */
    let message = buildMessage || "";

    if (_.isArray(buildMessage)) {
      message = _.join(buildMessage, ", ");
    }

    if (buildStatus === CACHE_STATUSES.CACHED) {
      return message;
    }
    if (buildStatus === CACHE_STATUSES.FAILED) {
      return message || i18n.t("queries:cache.failed-building-cache");
    }
    if (buildStatus === CACHE_STATUSES.NOT_BUILT) {
      return i18n.t("queries:cache.no-cache");
    }
    if (buildStatus === CACHE_STATUSES.BUILDING) {
      return i18n.t("queries:cache.building-cache");
    }
    return i18n.t("queries:cache.no-cache");
  };

  try {
    dispatch({ type: LOADING_QUERY_CACHE_STATUS });
    const { data: statusData } = await api.get(
      `/project/${projectId}/query/${queryId}/cache-status/`,
    );
    const buildStatus = getBuildStatus(statusData.build_status);

    let buildMessage = getBuildMessage(buildStatus, statusData?.message);

    if (buildStatus !== CACHE_STATUSES.CACHED) {
      const { data: buildCacheData } = await api.get(
        `/project/${projectId}/query/${queryId}/cache/`,
      );
      buildMessage = getBuildMessage(buildStatus, buildCacheData?.message);
    }

    dispatch({
      type: STORE_QUERY_CACHE_STATUS,
      payload: {
        data: { ...statusData, message: buildMessage, build_status: buildStatus },
        isFetching: false,
      },
    });
  } catch (error) {
    if (error?.response) {
      logger.logError(
        "",
        `${error.response?.config?.url} ${error.response?.data}`,
        error.response?.data,
        "postQueryCash",
      );
    }
    dispatch({
      type: CLEAR_QUERY_CACHE_STATUS,
    });
  }
};

export default loadQueryCacheStatus;
