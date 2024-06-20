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

import mockAxios from "axios";
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";
import "regenerator-runtime/runtime";

import * as pipelineActions from "./actions";
import {
  ADD_PIPELINE,
  UPDATING_PIPELINE,
  UPDATED_PIPELINE,
  STORE_SELECTED_PIPELINE,
  STORE_PIPELINES,
  LOADING_PIPELINES,
  LOADING_PIPELINE_SEEDS,
  LOADING_PIPELINES_RESULTS,
  STORE_PIPELINE_RESULTS,
  STORE_PIPELINE_SEEDS,
  SUBMITING_OPTIMIZATION_REQUEST,
  SUBMITED_OPTIMIZATION_REQUEST,
  FINISHED_OPTIMIZATION,
  RUNNING_OPTIMIZATION,
  FAILED_OPTIMIZATION,
  KILLING_OPTIMIZATION_REQUEST,
  KILLING_OPTIMIZATION_FAILED,
  OPTIMIZATION_REQUEST_KILLED,
} from "./actionTypes";

jest.mock("../../store/reducers.js");
const mockStore = configureMockStore([thunk]);

describe("pipelines actions", () => {
  let store;
  beforeEach(() => {
    store = mockStore({
      pipelines: {},
    });
  });

  it("should set selected pipeline", async () => {
    const expectedPipelineUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: STORE_SELECTED_PIPELINE,
      selectedPipeline: expectedPipelineUuid,
    };
    expect(pipelineActions.setSelectedPipeline(expectedPipelineUuid)).toEqual(expectedAction);
  });

  it("should log error when pipelines request fails", async () => {
    //mock setup
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINES,
      },
      {
        type: STORE_PIPELINES,
        pipelines: [],
      },
    ];
    await pipelineActions.loadPipelines(projectUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should return no pipelines if project id id not provided", async () => {
    const projectUuid = "";

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINES,
      },
      {
        type: STORE_PIPELINES,
        pipelines: [],
      },
    ];
    await pipelineActions.loadPipelines(projectUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should fetch all pipelines for a project", async () => {
    //mock setup
    const expectedPipelines = [{ name: "test1" }, { name: "test2" }];
    const mockedResponse = Promise.resolve({ data: expectedPipelines });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINES,
      },
      {
        type: STORE_PIPELINES,
        pipelines: expectedPipelines,
      },
    ];
    await pipelineActions.loadPipelines(projectUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when pipeline results request fails", async () => {
    //mock setup
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINES_RESULTS,
      },
      {
        type: STORE_PIPELINE_RESULTS,
        results: [],
      },
    ];
    await pipelineActions.loadPipelineResults(projectUuid, pipelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should not fecth pipeline results when pipelineUuid is not provided", async () => {
    const mockedResponse = Promise.resolve({
      data: null,
    });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINES_RESULTS,
      },
      {
        type: STORE_PIPELINE_RESULTS,
        results: [],
      },
    ];
    await pipelineActions.loadPipelineResults(projectUuid, pipelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should empty pipeline results when api response is undefined", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "";

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINES_RESULTS,
      },
      {
        type: STORE_PIPELINE_RESULTS,
        results: [],
      },
    ];
    await pipelineActions.loadPipelineResults(projectUuid, pipelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should fetch pipeline results for a project and pipeline", async () => {
    //mock setup
    const expectedResults = [{ name: "test1" }, { name: "test2" }];
    const mockedResponse = Promise.resolve({
      data: { extra: expectedResults },
    });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINES_RESULTS,
      },
      {
        type: STORE_PIPELINE_RESULTS,
        results: expectedResults,
      },
    ];
    await pipelineActions.loadPipelineResults(projectUuid, pipelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when pipeline seeds request fails", async () => {
    //mock setup
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINE_SEEDS,
      },
      {
        type: STORE_PIPELINE_SEEDS,
        seeds: [],
      },
    ];
    await pipelineActions.loadPipelineSeeds()(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should fetch all pipeline seeds", async () => {
    //mock setup
    const expectedSeeds = [{ name: "test1" }, { name: "test2" }];
    const mockedResponse = Promise.resolve({ data: expectedSeeds });

    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PIPELINE_SEEDS,
      },
      {
        type: STORE_PIPELINE_SEEDS,
        seeds: expectedSeeds,
      },
    ];
    await pipelineActions.loadPipelineSeeds()(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should add a pipeline", async () => {
    const expectedPipelineName = "Pipeline X";
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const expectedPipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";

    const mockedResponse = Promise.resolve({
      data: { uuid: expectedPipelineUuid },
    });
    mockAxios.post.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: ADD_PIPELINE,
      selectedPipeline: expectedPipelineUuid,
    };

    await pipelineActions.addPipeline(projectUuid, expectedPipelineName)(dispatch, getState);

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should return null when add a pipeline fails", async () => {
    const expectedPipelineName = "Pipeline X";
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";

    const mockedResponse = Promise.resolve({ data: {} });
    mockAxios.post.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: ADD_PIPELINE,
      selectedPipeline: "",
    };

    await pipelineActions.addPipeline(projectUuid, expectedPipelineName)(dispatch, getState);

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should return null on add a pipeline when project id is not set", async () => {
    const expectedPipelineName = "Pipeline X";
    const projectUuid = "";

    const mockedResponse = Promise.resolve({ data: {} });
    mockAxios.post.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: ADD_PIPELINE,
      selectedPipeline: "",
    };

    await pipelineActions.addPipeline(projectUuid, expectedPipelineName)(dispatch, getState);

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should return null when add a pipeline fails", async () => {
    const expectedPipelineName = "Pipeline X";
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    let expectedPipeline = {
      name: expectedPipelineName,
      pipeline: [],
      cache_enabled: "True",
      device_config: {
        target_platform: 0,
        build_flags: "",
        budget: [],
        debug: "False",
        sram_size: "",
        test_data: "",
        application: "",
        sample_rate: 100,
        kb_description: "",
      },
    };

    const mockedResponse = Promise.resolve({ data: { expectedPipeline } });
    mockAxios.post.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: ADD_PIPELINE,
      selectedPipeline: "",
    };

    await pipelineActions.addPipeline(projectUuid, expectedPipelineName)(dispatch, getState);

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should log error on add a pipeline", async () => {
    const expectedPipelineName = "Pipeline X";
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";

    mockAxios.post
      .mockImplementation(() => {})
      .mockImplementationOnce(() => {
        throw new Error("Some Error");
      });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: ADD_PIPELINE,
      selectedPipeline: "",
    };

    await pipelineActions.addPipeline(projectUuid, expectedPipelineName)(dispatch, getState);

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should update a pipeline", async () => {
    const pipelineName = "Pipeline X";
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const pipelineSteps = [{ name: "Q1", type: "query", outputs: ["temp.raw"] }];
    const cacheEnabled = true;
    const deviceConfig = {
      target_platform: 0,
      build_flags: "",
      budget: [],
      debug: "False",
      sram_size: "",
      test_data: "",
      application: "",
      sample_rate: 100,
      kb_description: "",
    };

    const mockedResponse = Promise.resolve({ data: { pipelineName } });
    mockAxios.put.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: UPDATING_PIPELINE,
        updatingPipeline: pipelineUuid,
      },
      {
        type: UPDATED_PIPELINE,
        updatedPipeline: pipelineUuid,
      },
    ];

    await pipelineActions.updatePipeline(
      projectUuid,
      pipelineUuid,
      pipelineName,
      pipelineSteps,
      cacheEnabled,
      deviceConfig,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when pipeline update fails", async () => {
    const pipelineName = "Pipeline X";
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const pipelineSteps = [{ name: "Q1", type: "query", outputs: ["temp.raw"] }];
    const cacheEnabled = true;
    const deviceConfig = {
      target_platform: 0,
      build_flags: "",
      budget: [],
      debug: "False",
      sram_size: "",
      test_data: "",
      application: "",
      sample_rate: 100,
      kb_description: "",
    };

    const dispatch = jest.fn();
    const getState = jest.fn();
    mockAxios.put
      .mockImplementation(() => {})
      .mockImplementationOnce(() => {
        throw new Error("Some Error");
      });

    const expectedActions = [
      {
        type: UPDATING_PIPELINE,
        updatingPipeline: pipelineUuid,
      },
    ];

    await pipelineActions.updatePipeline(
      projectUuid,
      pipelineUuid,
      pipelineName,
      pipelineSteps,
      cacheEnabled,
      deviceConfig,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should prepare pipeline for optimization request", async () => {
    const pipelineName = "Pipeline X";
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const pipelineSteps = [{ name: "Q1", type: "query", outputs: ["temp.raw"] }];
    const cacheEnabled = true;
    const deviceConfig = {
      target_platform: 0,
      build_flags: "",
      budget: [],
      debug: "False",
      sram_size: "",
      test_data: "",
      application: "",
      sample_rate: 100,
      kb_description: "",
    };

    const mockedResponse = Promise.resolve({ data: { pipelineName } });
    mockAxios.put.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: UPDATING_PIPELINE,
        updatingPipeline: pipelineUuid,
      },
      {
        type: UPDATED_PIPELINE,
        updatedPipeline: pipelineUuid,
      },
      {
        type: STORE_SELECTED_PIPELINE,
        selectedPipeline: pipelineUuid,
      },
      {
        type: UPDATING_PIPELINE,
        updatingPipeline: pipelineUuid,
      },
      {
        type: UPDATED_PIPELINE,
        updatedPipeline: pipelineUuid,
      },
      {
        type: STORE_SELECTED_PIPELINE,
        selectedPipeline: pipelineUuid,
      },
    ];

    await pipelineActions.preparePipeline(
      projectUuid,
      pipelineUuid,
      pipelineName,
      pipelineSteps,
      cacheEnabled,
      deviceConfig,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
    expect(dispatch.mock.calls[2][0]).toEqual(expectedActions[2]);
    expect(dispatch.mock.calls[3][0]).toEqual(expectedActions[3]);
  });

  it("should check optimization request status is pending", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const responseMessage =
      "Status: Pending, Time: 0.08, STEP: 1/3, NAME: generator_, TYPE: generators, BATCH: 1/1";
    //Status: Running, Time: 0.08, STEP: 2/3, NAME: generator_, TYPE: generators, BATCH: 1/1
    const mockedResponse = Promise.resolve({
      data: {
        status: "PENDING",
        message: responseMessage,
      },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: RUNNING_OPTIMIZATION,
      pipelineUuid: pipelineUuid,
      status: "RUNNING",
      message: responseMessage,
    };

    await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should check optimization request status is started", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const responseMessage =
      "Status: Running, Time: 0.08, STEP: 1/3, NAME: generator_, TYPE: generators, BATCH: 1/1";

    const mockedResponse = Promise.resolve({
      data: {
        status: "STARTED",
        message: responseMessage,
      },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: RUNNING_OPTIMIZATION,
      pipelineUuid: pipelineUuid,
      status: "RUNNING",
      message: responseMessage,
    };

    await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should check optimization request status is sent", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const responseMessage =
      "Status: Sent, Time: 0.08, STEP: 1/3, NAME: generator_, TYPE: generators, BATCH: 1/1";

    const mockedResponse = Promise.resolve({
      data: {
        status: "SENT",
        message: responseMessage,
      },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: RUNNING_OPTIMIZATION,
      pipelineUuid: pipelineUuid,
      status: "RUNNING",
      message: responseMessage,
    };

    await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should check optimization request status is not in known statuses", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const responseMessage = "Running Pipeline.";

    const mockedResponse = Promise.resolve({
      data: {
        status: "UNKNOWN_STATUS",
        message: responseMessage,
      },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: RUNNING_OPTIMIZATION,
      pipelineUuid: pipelineUuid,
      status: "RUNNING",
      message: responseMessage,
    };

    await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should check optimization request status with out a pipeline uuid", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "";

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {};

    let x = await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(x).toEqual(expectedAction);
  });

  it("should check optimization request status is failure", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const responseMessage = "Status: Pipeline Failed, Something was not set";

    const mockedResponse = Promise.resolve({
      data: {
        status: "FAILURE",
        message: responseMessage,
      },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: FAILED_OPTIMIZATION,
      pipelineUuid: pipelineUuid,
      status: "FAILURE",
      message: responseMessage,
    };

    await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should check optimization request status is revoked", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const responseMessage = "Status: Pipeline Failed, Something was not set";

    const mockedResponse = Promise.resolve({
      data: {
        status: "REVOKED",
        message: responseMessage,
      },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: FAILED_OPTIMIZATION,
      pipelineUuid: pipelineUuid,
      status: "FAILURE",
      message: responseMessage,
    };

    await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should check optimization request status on exception", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const responseMessage =
      "Encountered an error while checking optimization status, will retry status check in 5 seconds....";
    process.env.REACT_APP_ASYNC_CHECK_INTERVAL = "5000";
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: RUNNING_OPTIMIZATION,
      pipelineUuid: pipelineUuid,
      status: "RUNNING",
      message: responseMessage,
    };

    await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should check optimization request status is successful", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const responseMessage = "Automation Pipeline Completed.";

    const mockedResponse = Promise.resolve({
      data: {
        message: responseMessage,
      },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: FINISHED_OPTIMIZATION,
      pipelineUuid: pipelineUuid,
      status: "SUCCESS",
      message: responseMessage,
    };

    await pipelineActions.checkOptimizationRequestStatus(projectUuid, pipelineUuid)(
      dispatch,
      getState,
    );

    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should kill optimization request", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const mockedResponse = Promise.resolve({ data: "" });

    mockAxios.delete.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: KILLING_OPTIMIZATION_REQUEST,
        pipelineUuid: pipelineUuid,
        message: "Killing Pipeline Run",
      },
      {
        type: OPTIMIZATION_REQUEST_KILLED,
        pipelineUuid: pipelineUuid,
        message: "Killed Pipeline Run",
      },
    ];

    await pipelineActions.killOptimizationRequest(projectUuid, pipelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when kill optimization request fails", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";

    mockAxios.delete.mockImplementation(() => {
      throw new Error("Some Error");
    });

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: KILLING_OPTIMIZATION_REQUEST,
        pipelineUuid: pipelineUuid,
        message: "Killing Pipeline Run",
      },
      {
        type: KILLING_OPTIMIZATION_FAILED,
        pipelineUuid: pipelineUuid,
        message: "Error checking optimization request status.",
      },
    ];

    await pipelineActions.killOptimizationRequest(projectUuid, pipelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should ignore kill optimization request when pipeline is undefined", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "";
    const mockedResponse = Promise.resolve({ data: "" });

    mockAxios.delete.mockResolvedValue(mockedResponse);

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: KILLING_OPTIMIZATION_REQUEST,
        pipelineUuid: pipelineUuid,
        message: "Killing Pipeline Run",
      },
      {
        type: OPTIMIZATION_REQUEST_KILLED,
        pipelineUuid: pipelineUuid,
        message: "Killed Pipeline Run",
      },
    ];

    await pipelineActions.killOptimizationRequest(projectUuid, pipelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should submit optimization request", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    let autoParams = {
      search_steps: ["selectorset", "tvo"],
      iterations: 5,
      reset: true,
      population_size: 100,
      mutation_rate: 0.1,
      recreation_rate: 0.2,
      survivor_rate: 0.5,
      allow_unknown: false,
      validation_method: {
        name: "Stratified K-Fold Cross-Validation",
        inputs: {
          number_of_folds: 5,
          validation_size: 20 / 100,
          test_size: 0.0000000000000000001,
          metadata_name: "Label",
        },
      },
      balanced_data: false,
      demean_segments: false,
      outlier_filter: false,
      allow_hierarchical_model: false,
      "prediction_target(%)": { accuracy: 100 },
      hardware_target: { classifiers_sram: 32000 },
      combine_labels: null,
      group_columns: ["SegmentID", "Label"],
      data_columns: ["Col1", "Col2"],
      label_column: "Label",
    };
    const mockedResponse = Promise.resolve({ data: { pipelineUuid } });
    mockAxios.post.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: SUBMITING_OPTIMIZATION_REQUEST,
      },
      {
        type: SUBMITED_OPTIMIZATION_REQUEST,
        pipelineUuid: pipelineUuid,
        message: "Submitting Automation Pipeline Run.",
      },
    ];

    await pipelineActions.submitOptimizationRequest(
      projectUuid,
      pipelineUuid,
      autoParams,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when submit optimization fails", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    let autoParams = {};
    mockAxios.post
      .mockImplementation(() => {})
      .mockImplementationOnce(() => {
        throw new Error("Some Error");
      });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: SUBMITING_OPTIMIZATION_REQUEST,
      },
      {
        type: SUBMITED_OPTIMIZATION_REQUEST,
        pipelineUuid: pipelineUuid,
        message: "Submitting Automation Pipeline Run.",
      },
    ];

    await pipelineActions.submitOptimizationRequest(
      projectUuid,
      pipelineUuid,
      autoParams,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should not fail submit optimization if pipeline id is not provided", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "";
    let autoParams = {};
    mockAxios.post.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: SUBMITING_OPTIMIZATION_REQUEST,
      },
      {
        type: SUBMITED_OPTIMIZATION_REQUEST,
        pipelineUuid: pipelineUuid,
        message: "Submitting Automation Pipeline Run.",
      },
    ];

    await pipelineActions.submitOptimizationRequest(
      projectUuid,
      pipelineUuid,
      autoParams,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });
});
