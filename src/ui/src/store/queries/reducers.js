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

import { combineReducers } from "redux";
import {
  ADD_UPDATE_QUERY,
  LOADING_QUERIES,
  STORE_QUERIES,
  STORE_SELECTED_QUERY,
  LOADING_QUERY,
  STORE_QUERY,
  LOADING_QUERY_CACHE_STATUS,
  STORE_QUERY_CACHE_STATUS,
  CLEAR_QUERY_CACHE_STATUS,
  UNCAUGHT_ERROR_QUERY_DATA,
  UNCAUGHT_ERROR_QUERY_LIST,
  LOADING_QUERY_FEATURE_STATS,
  STORE_QUERY_FEATURE_STATS,
  UNCAUGHT_ERROR_QUERY_FEATURE_STATS,
  RESET_QUERY_FEATURE_STATS,
} from "./actionTypes";

const initialQueryListState = { data: [], isFetching: false };
export function queryList(state = initialQueryListState, action) {
  switch (action.type) {
    case LOADING_QUERIES:
      return { data: [], error: undefined, isFetching: true };
    case STORE_QUERIES:
      return { data: action.queries, error: undefined, isFetching: false };
    case UNCAUGHT_ERROR_QUERY_LIST:
      // eslint-disable-next-line no-throw-literal
      throw { data: undefined, error: action.error, isFetching: false };
    default:
      return state;
  }
}

const initialQueryDataState = {
  query: "",
  name: "",
  session: "",
  label: "",
  metadata: [],
  source: [],
  plot: "",
  metadata_filter: "",
  task_status: null,
  query_partition: null,
  summary_statistics: null,
};

export function queryData(state = initialQueryDataState, action) {
  switch (action.type) {
    case LOADING_QUERY:
      return {
        data: initialQueryDataState,
        error: undefined,
        isFetching: true,
      };
    case STORE_QUERY:
      return { data: action.queryDetails, error: undefined, isFetching: false };
    case ADD_UPDATE_QUERY:
      return { data: action.queryDetails, error: undefined, isFetching: false };
    case UNCAUGHT_ERROR_QUERY_DATA:
      return {
        data: action.queryDetails,
        error: action.error,
        isFetching: false,
      };
    default:
      return state;
  }
}

const initialSelectedQueryState = "";
export function selectedQuery(state = initialSelectedQueryState, action) {
  switch (action.type) {
    case STORE_SELECTED_QUERY:
      return action.selectedQuery;
    default:
      return state;
  }
}

const initialQueryFeatureStats = {};

export function queryFeatureStats(
  state = { data: initialQueryFeatureStats, isFetching: false },
  action,
) {
  switch (action.type) {
    case LOADING_QUERY_FEATURE_STATS:
      return {
        data: initialQueryFeatureStats,
        error: undefined,
        isFetching: true,
      };
    case STORE_QUERY_FEATURE_STATS:
      return {
        data: action.featureStatistics,
        error: undefined,
        isFetching: false,
      };
    case UNCAUGHT_ERROR_QUERY_FEATURE_STATS:
      return {
        data: initialQueryDataState,
        error: action.error,
        isFetching: false,
      };
    case RESET_QUERY_FEATURE_STATS:
      return {
        data: initialQueryFeatureStats,
        error: undefined,
        isFetching: false,
      };
    default:
      return state;
  }
}

const initialCacheQueryStatus = { data: {}, isFetching: false };

export const queryCacheStatus = (state = initialCacheQueryStatus, action) => {
  const { type, payload } = action;
  switch (type) {
    case LOADING_QUERY_CACHE_STATUS:
      return { ...state, isFetching: true };
    case CLEAR_QUERY_CACHE_STATUS:
      return initialCacheQueryStatus;
    case STORE_QUERY_CACHE_STATUS:
      return { ...state, ...payload };
    default:
      return state;
  }
};

export default combineReducers({
  queryData,
  queryList,
  selectedQuery,
  queryFeatureStats,
  queryCacheStatus,
});
