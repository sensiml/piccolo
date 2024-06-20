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
  ADD_UPDATE_QUERY,
  UNCAUGHT_ERROR_QUERY_LIST,
  UNCAUGHT_ERROR_QUERY_DATA,
  STORE_QUERIES,
  STORE_QUERY,
} from "../actionTypes";
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";
import mockAxios from "axios";

const mockStore = configureMockStore([thunk]);

const responseSummaryStatisticValidData = {
  samples: {
    Drop: 237,
    Hold: 644,
    Take: 467,
    Stand: 436,
  },
  segments: {
    Drop: 4,
    Hold: 1,
    Take: 5,
    Stand: 5,
  },
  total_segments: 15,
};

describe("query actions", () => {
  let store;
  beforeEach(() => {
    store = mockStore({
      queries: {},
    });
  });

  it("should log error if fetch queries fails", async () => {
    //mock setup
    const expectedError = "Some Error";
    mockAxios.get.mockImplementation(() => {
      throw expectedError;
    });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      { type: LOADING_QUERIES },
      {
        type: UNCAUGHT_ERROR_QUERY_LIST,
        error: expectedError,
      },
      {
        type: STORE_QUERIES,
        queries: [],
      },
    ];

    await queryActions.loadQueries(projectUuid)(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
    expect(dispatch.mock.calls[2][0]).toEqual(expectedActions[2]);
  });

  it("should skip fetch queries if project id is not provided", async () => {
    const projectUuid = "";
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      { type: LOADING_QUERIES },
      {
        type: STORE_QUERIES,
        queries: [],
      },
    ];

    await queryActions.loadQueries(projectUuid)(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should skip fetch queries if project id is not provided", async () => {
    const projectUuid = "";
    const queryUuid = "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8";
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      { type: LOADING_QUERY },
      { type: STORE_SELECTED_QUERY, selectedQuery: queryUuid },
      {
        type: STORE_QUERY,
        queryDetails: {
          label: "",
          metadata: [],
          metadata_filter: "",
          name: "",
          plot: "",
          query: "",
          session: "",
          source: [],
          task_status: null,
        },
      },
    ];

    await queryActions.loadQuery(projectUuid, queryUuid)(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when loading the selected query fails", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const queryUuid = "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8";

    const expectedError = "Some Error";
    mockAxios.get.mockImplementation(() => {
      throw expectedError;
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      { type: LOADING_QUERY },
      {
        type: UNCAUGHT_ERROR_QUERY_DATA,
        queryDetails: {
          query: "",
          name: "",
          session: "",
          label: "",
          metadata: [],
          source: [],
          plot: "",
          metadata_filter: "",
        },
        error: expectedError,
      },
    ];

    let y = await queryActions.loadQuery(projectUuid, queryUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should add queryDetails for the selected query", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const queryUuid = "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8";
    const queryData = {
      query: queryUuid,
      label: "Fan_State",
      segmentsCharts: [],
      samplesCharts: [],
    };
    const responseData = [
      {
        Capture: "audio_001_blocked.csv",
        Fan: "AC",
        Fan_State: "Block",
        "Segment Length": 496991,
      },
      {
        Capture: "audio_001_Idle.csv",
        Fan: "AC",
        Fan_State: "Idle",
        "Segment Length": 499426,
      },
      {
        Capture: "audio_001_Normal.csv",
        Fan: "AC",
        Fan_State: "Normal",
        "Segment Length": 499427,
      },
      {
        Capture: "audio_002_blocked.csv",
        Fan: "AC",
        Fan_State: "Block",
        "Segment Length": 498301,
      },
      {
        Capture: "audio_002_Idle.csv",
        Fan: "AC",
        Fan_State: "Idle",
        "Segment Length": 498492,
      },
      {
        Capture: "audio_002_Normal.csv",
        Fan: "AC",
        Fan_State: "Normal",
        "Segment Length": 498615,
      },
      {
        Capture: "audio_003_blocked.csv",
        Fan: "AC",
        Fan_State: "Block",
        "Segment Length": 499887,
      },
      {
        Capture: "audio_003_Idle.csv",
        Fan: "AC",
        Fan_State: "Idle",
        "Segment Length": 499753,
      },
      {
        Capture: "audio_003_Normal.csv",
        Fan: "AC",
        Fan_State: "Normal",
        "Segment Length": 495367,
      },
      {
        Capture: "audio_004_blocked.csv",
        Fan: "AC",
        Fan_State: "Block",
        "Segment Length": 498106,
      },
    ];
    //{ Block: 4, Idle: 3, Normal: 3 },
    //{ Block: 1993285, Idle: 1497671, Normal: 1493409 },
    const expectedQueyData = {
      label: "Fan_State",
      query: "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8",
      samplesCharts: [],
      segmentsCharts: [],
    };
    const mockedResponse = Promise.resolve({ data: responseData });
    mockAxios.get.mockResolvedValue(mockedResponse);

    let actualQueryData = await queryActions.addQueryStats(projectUuid, queryData);
    expect(actualQueryData.label).toEqual(expectedQueyData.label);
    expect(actualQueryData.query).toEqual(expectedQueyData.query);
  });

  it("should load the selected query", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const queryUuid = "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8";

    const responseData = {
      uuid: queryUuid,
      name: "Q1",
      columns: [
        "AccelerometerX",
        "AccelerometerY",
        "AccelerometerZ",
        "GyroscopeX",
        "GyroscopeY",
        "GyroscopeZ",
      ],
      cache: [[1799, "d3ee6435-cf6f-4d79-b23d-4914689779c6.0.gz"]],
      label_column: "Lifting",
      metadata_columns: ["id"],
      metadata_filter: "[columnx]='y'",
      segmenter_id: "XYZ",
      combine_labels: null,
      created_at: "2019-10-30T05:04:29.9215",
      last_modified: "2019-12-09T23:36:46.260539Z",
      segmenter: null,
      task_status: null,
    };

    const expectedQueryData = {
      query: responseData.uuid,
      name: responseData.name,
      session: responseData.segmenter_id,
      label: responseData.label_column,
      cache: responseData.cache,
      metadata: responseData.metadata_columns,
      source: responseData.columns,
      plot: "segment",
      metadata_filter: responseData.metadata_filter,
      samplesCharts: responseSummaryStatisticValidData.samples,
      segmentsCharts: responseSummaryStatisticValidData.segments,
      summary_statistics: [],
      segment_statistics: {},
      task_status: null,
    };

    const reponseQueryCaheData = {
      status: true,
      build_status: CACHE_STATUSES.CACHED,
      message: "",
    };

    const expectedQueryCacheData = {
      data: reponseQueryCaheData,
      isFetching: false,
    };

    const mockedQueryResponse = Promise.resolve({ data: responseData });
    const mockedSummaryStatisticResponse = Promise.resolve({
      data: responseSummaryStatisticValidData,
    });
    const mockedQueryCacheData = Promise.resolve({ data: reponseQueryCaheData });

    mockAxios.get.mockImplementation((url) => {
      switch (url) {
        case `/project/${projectUuid}/query/${queryUuid}/`:
          return mockedQueryResponse;
        case `/project/${projectUuid}/query/${queryUuid}/summary-statistics/`:
          return mockedSummaryStatisticResponse;
        case `/project/${projectUuid}/query/${queryUuid}/cache-status/`:
          return mockedQueryCacheData;
        case `/project/${projectUuid}/query/${queryUuid}/cache/`:
          return mockedQueryCacheData;
        default:
          return mockedQueryResponse;
      }
    });

    const expectedActions = [
      { type: LOADING_QUERY },
      { type: LOADING_QUERY_CACHE_STATUS },
      {
        type: STORE_QUERY_CACHE_STATUS,
        payload: expectedQueryCacheData,
      },
      {
        type: STORE_SELECTED_QUERY,
        selectedQuery: queryUuid,
      },
      {
        type: STORE_QUERY,
        queryDetails: expectedQueryData,
      },
    ];

    await store.dispatch(queryActions.loadQuery(projectUuid, queryUuid));
    expect(store.getActions()).toEqual(expectedActions);
  });

  it("should fetch all queries", async () => {
    //mock setup
    const expectedQueries = [{ name: "test1" }, { name: "test2" }];
    const mockedResponse = Promise.resolve({ data: expectedQueries });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: STORE_QUERIES,
      queries: expectedQueries,
    };
    await queryActions.loadQueries(projectUuid)(dispatch, getState);
    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should add a query", async () => {
    const expectedQueryName = "Query X";
    const columns = ["AccelerometerX"];
    const metadataColumns = ["id"];
    const metadataFilter = "[columnx]='y'";
    const segmenterId = "XYZ";
    const labelColumn = "Lifting";
    const comnineLabels = null;
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const queryUuid = "";
    const cache = [];
    const task_status = null;

    let responseData = {
      name: expectedQueryName,
      columns: columns,
      metadata_columns: metadataColumns,
      metadata_filter: metadataFilter,
      segmenter_id: segmenterId,
      label_column: labelColumn,
      combine_labels: comnineLabels,
      uuid: "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8",
      cache,
      task_status: null,
    };

    const mockedResponse = Promise.resolve({
      data: responseData,
    });

    mockAxios.post.mockResolvedValue(mockedResponse);
    mockAxios.get.mockResolvedValue({ data: responseSummaryStatisticValidData });

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        selectedQuery: "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8",
        type: STORE_SELECTED_QUERY,
      },
      {
        queryDetails: {
          label: "Lifting",
          metadata: ["id"],
          metadata_filter: "[columnx]='y'",
          name: "Query X",
          plot: "segment",
          query: "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8",
          samplesCharts: responseSummaryStatisticValidData.samples,
          segmentsCharts: responseSummaryStatisticValidData.segments,
          session: "XYZ",
          source: ["AccelerometerX"],
          cache,
          summary_statistics: [],
          segment_statistics: {},
          task_status: null,
        },
        type: ADD_UPDATE_QUERY,
      },
    ];

    let x = await queryActions.addOrUpdateQuery(
      projectUuid,
      queryUuid,
      expectedQueryName,
      columns,
      metadataColumns,
      segmenterId,
      labelColumn,
      "Label Name",
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should add a query with null metadata", async () => {
    const expectedQueryName = "Query X";
    const columns = ["AccelerometerX"];
    const metadataColumns = ["id"];
    const metadataFilter = undefined;
    const segmenterId = "XYZ";
    const labelColumn = "Lifting";
    const comnineLabels = null;
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const queryUuid = "";

    let responseData = {
      name: expectedQueryName,
      cache: [[1799, "d3ee6435-cf6f-4d79-b23d-4914689779c6.0.gz"]],
      columns: columns,
      metadata_columns: metadataColumns,
      metadata_filter: "",
      segmenter_id: segmenterId,
      label_column: labelColumn,
      combine_labels: comnineLabels,
      uuid: "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8",
    };

    const mockedResponse = Promise.resolve({
      data: responseData,
    });

    mockAxios.post.mockResolvedValue(mockedResponse);
    mockAxios.get.mockResolvedValue({ data: responseSummaryStatisticValidData });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        selectedQuery: "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8",
        type: STORE_SELECTED_QUERY,
      },
      {
        queryDetails: {
          label: "Lifting",
          metadata: ["id"],
          metadata_filter: "",
          name: "Query X",
          plot: "segment",
          query: "8cc74759-4f4c-4a03-bdf8-1f20445a9ed8",
          session: "XYZ",
          source: ["AccelerometerX"],
          cache: responseData.cache,
          samplesCharts: responseSummaryStatisticValidData.samples,
          segmentsCharts: responseSummaryStatisticValidData.segments,
          summary_statistics: [],
          segment_statistics: {},
          task_status: null,
        },
        type: ADD_UPDATE_QUERY,
      },
    ];

    let x = await queryActions.addOrUpdateQuery(
      projectUuid,
      queryUuid,
      expectedQueryName,
      columns,
      metadataColumns,
      segmenterId,
      metadataFilter,
      labelColumn,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should update a query", async () => {
    const expectedQueryName = "Query X";
    const columns = ["AccelerometerX"];
    const metadataColumns = ["id"];
    const metadataFilter = "[columnx]='y'";
    const segmenterId = "XYZ";
    const labelColumn = "Lifting";
    const comnineLabels = null;
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const queryUuid = "0cb528dd-def5-46a9-8432-243378362e19";

    let expectedQuery = {
      uuid: queryUuid,
      name: expectedQueryName,
      columns: columns,
      metadata_columns: metadataColumns,
      metadata_filter: metadataFilter,
      segmenter_id: segmenterId,
      label_column: labelColumn,
      combine_labels: comnineLabels,
    };

    const mockedResponse = Promise.resolve({ data: { expectedQuery } });
    mockAxios.put.mockResolvedValue(mockedResponse);
    mockAxios.get.mockResolvedValue({ data: responseSummaryStatisticValidData });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        selectedQuery: "",
        type: STORE_SELECTED_QUERY,
      },
      {
        queryDetails: {
          label: "",
          metadata: [],
          metadata_filter: "",
          name: "",
          plot: "",
          query: "",
          samplesCharts: responseSummaryStatisticValidData.samples,
          segmentsCharts: responseSummaryStatisticValidData.segments,
          session: "",
          source: [],
        },
        type: ADD_UPDATE_QUERY,
      },
    ];

    let x = await queryActions.addOrUpdateQuery(
      projectUuid,
      queryUuid,
      expectedQueryName,
      columns,
      metadataColumns,
      segmenterId,
      metadataFilter,
      labelColumn,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[2][0]).toEqual(expectedActions[1]);
  });

  it("should log error when add/update query fails", async () => {
    const expectedQueryName = "Query X";
    const columns = ["AccelerometerX"];
    const metadataColumns = ["id"];
    const segmenterId = "XYZ";
    const labelColumn = "Lifting";
    const metadataFilter = "";
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const queryUuid = "0cb528dd-def5-46a9-8432-243378362e19";

    const expectedError = "Some Error";
    mockAxios.put.mockImplementation(() => {
      throw expectedError;
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        error: "Some Error",
        type: UNCAUGHT_ERROR_QUERY_DATA,
      },
    ];

    let x = await queryActions.addOrUpdateQuery(
      projectUuid,
      queryUuid,
      expectedQueryName,
      columns,
      metadataColumns,
      segmenterId,
      metadataFilter,
      labelColumn,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should skip add/update query if project id not provided", async () => {
    const expectedQueryName = "Query X";
    const columns = ["AccelerometerX"];
    const metadataColumns = ["id"];
    const metadataFilter = "";
    const segmenterId = "XYZ";
    const labelColumn = "Lifting";
    const projectUuid = "";
    const queryUuid = "0cb528dd-def5-46a9-8432-243378362e19";

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        queryDetails: {
          query: "",
          name: "",
          session: "",
          label: "",
          metadata: [],
          source: [],
          plot: "",
          metadata_filter: "",
        },
        type: ADD_UPDATE_QUERY,
      },
    ];

    let x = await queryActions.addOrUpdateQuery(
      projectUuid,
      queryUuid,
      expectedQueryName,
      columns,
      metadataColumns,
      segmenterId,
      metadataFilter,
      labelColumn,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should set the selected query in the store", async () => {
    let expectedUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const expectedAction = {
      type: STORE_SELECTED_QUERY,
      selectedQuery: expectedUuid,
    };
    expect(queryActions.setSelectedQuery(expectedUuid)).toEqual(expectedAction);
  });
});
