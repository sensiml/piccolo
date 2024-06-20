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

import "regenerator-runtime/runtime";
import { CACHE_STATUSES } from "../const";
import * as queryActions from "../actions";
import {
  LOADING_QUERY,
  LOADING_QUERIES,
  STORE_SELECTED_QUERY,
  LOADING_QUERY_CACHE_STATUS,
  STORE_QUERY_CACHE_STATUS,
} from "../actionTypes";
import configureMockStore from "redux-mock-store";
import MockAdapter from "axios-mock-adapter";
import thunk from "redux-thunk";
import i18n from "i18n";
import api from "store/api";

// needs for MockAdapter
jest.unmock("axios");

const mockStore = configureMockStore([thunk]);

describe("loadQueryCacheStatus action", () => {
  let store;
  beforeEach(() => {
    store = mockStore({
      queries: {},
    });
  });
  const projectId = "1";
  const queryId = "2";

  const reponseQueryCaheDataUpToDate = {
    status: true,
    build_status: CACHE_STATUSES.CACHED,
    message: "UpToDate CACHED",
  };
  const reponseQueryCaheDataOutOfSync = {
    status: false,
    build_status: CACHE_STATUSES.CACHED,
    message: "OutOfSync CACHED",
  };
  const reponseQueryCaheDataNotBuilt = {
    status: false,
    build_status: null,
    message: "",
  };
  const reponseQueryCaheDataBuilding = {
    status: false,
    build_status: CACHE_STATUSES.BUILDING,
    message: "",
  };
  const reponseQueryCaheDataFailed = {
    status: false,
    build_status: CACHE_STATUSES.FAILED,
    message: "",
  };
  const reponseQueryCaheDataUnknow = {
    status: false,
    build_status: "Cached",
    message: "",
  };

  const responseCacheDataNotCached = {
    status: null,
    message: [],
    detail: null,
  };
  const responseCacheDataBuilding = {
    status: null,
    message: null,
    detail: null,
  };
  const responseCacheDataFailed = {
    status: null,
    message: null,
    detail: null,
  };

  const mockResponseAdapter = new MockAdapter(api);

  mockResponseAdapter
    // ut to date
    .onGet(`/project/${projectId}/query/${queryId}/cache-status/`)
    .replyOnce(200, reponseQueryCaheDataUpToDate)
    // out of sync
    .onGet(`/project/${projectId}/query/${queryId}/cache-status/`)
    .replyOnce(200, reponseQueryCaheDataOutOfSync)
    // not cached
    .onGet(`/project/${projectId}/query/${queryId}/cache-status/`)
    .replyOnce(200, reponseQueryCaheDataNotBuilt)
    .onGet(`/project/${projectId}/query/${queryId}/cache/`)
    .replyOnce(200, responseCacheDataNotCached)
    // building
    .onGet(`/project/${projectId}/query/${queryId}/cache-status/`)
    .replyOnce(200, reponseQueryCaheDataBuilding)
    .onGet(`/project/${projectId}/query/${queryId}/cache/`)
    .replyOnce(200, responseCacheDataBuilding)
    // failed
    .onGet(`/project/${projectId}/query/${queryId}/cache-status/`)
    .replyOnce(200, reponseQueryCaheDataFailed)
    .onGet(`/project/${projectId}/query/${queryId}/cache/`)
    .replyOnce(200, responseCacheDataFailed)
    // unknow status
    .onGet(`/project/${projectId}/query/${queryId}/cache-status/`)
    .replyOnce(200, reponseQueryCaheDataUnknow)
    .onGet(`/project/${projectId}/query/${queryId}/cache/`)
    .replyOnce(200, responseCacheDataFailed);

  it("should load up to date query", async () => {
    const expectedActions = [
      { type: LOADING_QUERY_CACHE_STATUS },
      {
        type: STORE_QUERY_CACHE_STATUS,
        payload: { data: reponseQueryCaheDataUpToDate, isFetching: false },
      },
    ];

    await store.dispatch(queryActions.loadQueryCacheStatus(projectId, queryId));

    expect(store.getActions()).toEqual(expectedActions);
  });

  it("should load out of sync query", async () => {
    const expectedActions = [
      { type: LOADING_QUERY_CACHE_STATUS },
      {
        type: STORE_QUERY_CACHE_STATUS,
        payload: { data: reponseQueryCaheDataOutOfSync, isFetching: false },
      },
    ];

    await store.dispatch(queryActions.loadQueryCacheStatus(projectId, queryId));

    expect(store.getActions()).toEqual(expectedActions);
  });

  it("should load not built data", async () => {
    const expectedActions = [
      { type: LOADING_QUERY_CACHE_STATUS },
      {
        type: STORE_QUERY_CACHE_STATUS,
        payload: {
          data: {
            ...reponseQueryCaheDataNotBuilt,
            message: i18n.t("queries:cache.no-cache"),
            build_status: CACHE_STATUSES.NOT_BUILT,
          },
          isFetching: false,
        },
      },
    ];

    await store.dispatch(queryActions.loadQueryCacheStatus(projectId, queryId));
    expect(store.getActions()).toEqual(expectedActions);
  });

  it("should load building", async () => {
    const expectedActions = [
      { type: LOADING_QUERY_CACHE_STATUS },
      {
        type: STORE_QUERY_CACHE_STATUS,
        payload: {
          data: {
            ...reponseQueryCaheDataBuilding,
            message: i18n.t("queries:cache.building-cache"),
            build_status: CACHE_STATUSES.BUILDING,
          },
          isFetching: false,
        },
      },
    ];

    await store.dispatch(queryActions.loadQueryCacheStatus(projectId, queryId));
    expect(store.getActions()).toEqual(expectedActions);
  });

  it("should load failed cache", async () => {
    const expectedActions = [
      { type: LOADING_QUERY_CACHE_STATUS },
      {
        type: STORE_QUERY_CACHE_STATUS,
        payload: {
          data: {
            ...reponseQueryCaheDataFailed,
            message: i18n.t("queries:cache.failed-building-cache"),
            build_status: CACHE_STATUSES.FAILED,
          },
          isFetching: false,
        },
      },
    ];

    await store.dispatch(queryActions.loadQueryCacheStatus(projectId, queryId));
    expect(store.getActions()).toEqual(expectedActions);
  });

  it("should load with unknow status", async () => {
    const expectedActions = [
      { type: LOADING_QUERY_CACHE_STATUS },
      {
        type: STORE_QUERY_CACHE_STATUS,
        payload: {
          data: {
            ...reponseQueryCaheDataUnknow,
            message: i18n.t("queries:cache.no-cache"),
            build_status: CACHE_STATUSES.NOT_BUILT,
          },
          isFetching: false,
        },
      },
    ];

    await store.dispatch(queryActions.loadQueryCacheStatus(projectId, queryId));
    expect(store.getActions()).toEqual(expectedActions);
  });

});
