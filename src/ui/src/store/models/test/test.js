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

import * as modelActions from "../actions";
import {
  LOADING_MODELS,
  STORE_MODELS,
  LOADING_MODEL,
  STORE_MODEL,
  STORE_SELECTED_MODEL,
  STARTING_MODEL_DOWNLOAD,
  STARTED_MODEL_DOWNLOAD,
  DOWNLOADING_MODEL,
  MODEL_DOWNLOAD_FAILED,
  MODEL_DOWNLOADED,
} from "../actionTypes";
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";
import "regenerator-runtime/runtime";
import mockAxios from "axios";

const mockStore = configureMockStore([thunk]);

describe("models actions", () => {
  let store;
  beforeEach(() => {
    store = mockStore({
      models: {},
    });
  });

  it("should fetch all models for a project & pipeline", async () => {
    //mock setup
    const expectedModels = [
      { name: "test1", uuid: "1ee09063-39bb-4b83-839f-4402b6e29b68" },
      { name: "test2", uuid: "6d52d44c-143b-46a3-b553-ac741b979b37" },
    ];
    const mockedResponse = Promise.resolve({ data: expectedModels });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const piplelineUuid = "49e803f7-e37d-4c1c-aed3-7e34cf26e52a";
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_MODELS,
      },
      {
        type: STORE_MODELS,
        models: expectedModels,
      },
    ];
    await modelActions.loadModels(projectUuid, piplelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when models request fails", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const piplelineUuid = "49e803f7-e37d-4c1c-aed3-7e34cf26e52a";

    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_MODELS,
      },
      {
        type: STORE_MODELS,
        models: [],
      },
    ];
    await modelActions.loadModels(projectUuid, piplelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should return no labels project is undefined", async () => {
    const projectUuid = undefined;
    const piplelineUuid = "49e803f7-e37d-4c1c-aed3-7e34cf26e52a";

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_MODELS,
      },
      {
        type: STORE_MODELS,
        models: [],
      },
    ];
    await modelActions.loadModels(projectUuid, piplelineUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should fetch selected model data for a model Id", async () => {
    //mock setup
    const expectedModel = {
      name: "test1",
      uuid: "1ee09063-39bb-4b83-839f-4402b6e29b68",
    };

    const mockedResponse = Promise.resolve({ data: expectedModel });
    const modelUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";

    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_MODEL,
      },
      {
        type: STORE_SELECTED_MODEL,
        selectedModel: expectedModel.uuid,
      },
      {
        type: STORE_MODEL,
        model: expectedModel,
      },
    ];
    await modelActions.loadModel(modelUuid, ["uuid", "name"])(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
    expect(dispatch.mock.calls[2][0]).toEqual(expectedActions[2]);
  });

  it("should log error when model data request fails", async () => {
    //mock setup
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const modelUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_MODEL,
      },
      {
        type: STORE_MODEL,
        model: {},
      },
    ];
    await modelActions.loadModel(modelUuid, [["name", "uuid"]])(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should return no model data when modelUuid is undefined", async () => {
    //mock setup
    const expectedModel = {
      name: "test1",
      uuid: "1ee09063-39bb-4b83-839f-4402b6e29b68",
    };

    const mockedResponse = Promise.resolve({ data: expectedModel });
    const modelUuid = undefined;

    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: STORE_MODEL,
        model: {},
      },
    ];
    await modelActions.loadModel(modelUuid, ["name", "uuid"])(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should submit download request", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = "4ad93ade-65a6-4d36-a711-92624e912bc5";

    let config = {
      target_platform: 99,
      test_data: undefined,
      debug: false,
      application: "Default",
      sample_rate: 100,
      output_options: ["serial"],
      kb_description: {
        AudioPipe_rank_4: {
          uuid: "4ad93ade-65a6-4d36-a711-92624e912bc5",
          results: {
            "1 ": "Report",
            "2 ": "Report",
            "3 ": "Report",
            "4 ": "Report",
            "5 ": "Report",
          },
          source: "c26b15ee-9018-415a-bb65-a327a3aec53a",
        },
      },
      debug_level: 1,
      profile: false,
      profile_iterations: 0,
      asynchronous: true,
    };
    const mockedResponse = Promise.resolve({ data: { task_state: "SUCCESS" } });
    mockAxios.post.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: STARTING_MODEL_DOWNLOAD,
      },
      {
        type: STARTED_MODEL_DOWNLOAD,
        pipelineUuid: pipelineUuid,
        modelUuid: modelUuid,
        message: "Submitting Download Request.",
      },
    ];

    await modelActions.submitDownloadRequest(
      projectUuid,
      pipelineUuid,
      modelUuid,
      "bin",
      config,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should not submit download request if model id is null", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = undefined;

    let config = {
      target_platform: 99,
      test_data: undefined,
      debug: false,
      application: "Default",
      sample_rate: 100,
      output_options: ["serial"],
      kb_description: {
        AudioPipe_rank_4: {
          uuid: "4ad93ade-65a6-4d36-a711-92624e912bc5",
          results: {
            "1 ": "Report",
            "2 ": "Report",
            "3 ": "Report",
            "4 ": "Report",
            "5 ": "Report",
          },
          source: "c26b15ee-9018-415a-bb65-a327a3aec53a",
        },
      },
      debug_level: 1,
      profile: false,
      profile_iterations: 0,
      asynchronous: true,
    };
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: STARTING_MODEL_DOWNLOAD,
      },
    ];

    await modelActions.submitDownloadRequest(
      projectUuid,
      pipelineUuid,
      modelUuid,
      "bin",
      config,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should log error when download submission fails", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = "4ad93ade-65a6-4d36-a711-92624e912bc5";

    let config = {};
    mockAxios.post
      .mockImplementation(() => {})
      .mockImplementationOnce(() => {
        throw new Error("Some Error");
      });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: STARTING_MODEL_DOWNLOAD,
      },
      {
        type: MODEL_DOWNLOAD_FAILED,
        pipelineUuid: pipelineUuid,
        modelUuid: modelUuid,
        message: "Submitting Download Request.",
        error: "Some Error",
        code: undefined,
        message: "Some Error",
        status: "FAILURE",
      },
    ];

    await modelActions.submitDownloadRequest(
      projectUuid,
      pipelineUuid,
      modelUuid,
      "bin",
      config,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should check download request status is pending", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = "4ad93ade-65a6-4d36-a711-92624e912bc5";
    const downloadType = "bin";
    const downloadFileName =
      "kp_4ad93ade-65a6-4d36-a711-92624e912bc5_x86_GCC_Generic_GCC_7.2.0_p.zip";
    const mockedResponse = Promise.resolve({ data: { task_state: "SENT" } });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: DOWNLOADING_MODEL,
        pipelineUuid: pipelineUuid,
        modelUuid: modelUuid,
        status: "RUNNING",
      },
    ];

    await modelActions.checkDownloadRequestStatus(
      projectUuid,
      pipelineUuid,
      modelUuid,
      downloadType,
      downloadFileName,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should not check download request status if model id is null", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = undefined;
    const downloadType = "bin";
    const downloadFileName =
      "kp_4ad93ade-65a6-4d36-a711-92624e912bc5_x86_GCC_Generic_GCC_7.2.0_p.zip";
    const dispatch = jest.fn();
    const getState = jest.fn();

    await modelActions.checkDownloadRequestStatus(
      projectUuid,
      pipelineUuid,
      modelUuid,
      downloadType,
      downloadFileName,
    )(dispatch, getState);

    expect(dispatch.mock.calls.length).toEqual(0);
  });

  it("should check download failed", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = "4ad93ade-65a6-4d36-a711-92624e912bc5";
    const downloadType = "bin";
    const downloadFileName =
      "kp_4ad93ade-65a6-4d36-a711-92624e912bc5_x86_GCC_Generic_GCC_7.2.0_p.zip";
    const mockedResponse = Promise.resolve({
      data: { task_state: "FAILURE", task_result: "Some Error" },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: MODEL_DOWNLOAD_FAILED,
        pipelineUuid: pipelineUuid,
        modelUuid: modelUuid,
        status: "FAILURE",
        error: "Some Error",
        message: "Some Error",
      },
    ];

    await modelActions.checkDownloadRequestStatus(
      projectUuid,
      pipelineUuid,
      modelUuid,
      downloadType,
      downloadFileName,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should check download with unknown status ", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = "4ad93ade-65a6-4d36-a711-92624e912bc5";
    const downloadType = "bin";
    const downloadFileName =
      "kp_4ad93ade-65a6-4d36-a711-92624e912bc5_x86_GCC_Generic_GCC_7.2.0_p.zip";
    const mockedResponse = Promise.resolve({
      data: { task_state: "UNKNOWN", task_result: "Some Error" },
    });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: MODEL_DOWNLOAD_FAILED,
        pipelineUuid: pipelineUuid,
        modelUuid: modelUuid,
        status: "FAILURE",
        error: "Some Error",
        message: "Some Error",
      },
    ];

    await modelActions.checkDownloadRequestStatus(
      projectUuid,
      pipelineUuid,
      modelUuid,
      downloadType,
      downloadFileName,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should check download request status is successful", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = "4ad93ade-65a6-4d36-a711-92624e912bc5";
    const downloadType = "bin";
    const downloadFileName =
      "kp_4ad93ade-65a6-4d36-a711-92624e912bc5_x86_GCC_Generic_GCC_7.2.0_p.zip";
    const expectedHeaders = {
      "Content-Disposition": "attachment; filename: test.zip",
    };
    const expectedData = "Some Blob";
    const mockedResponse = Promise.resolve({
      headers: expectedHeaders,
    });
    mockAxios.get
      .mockResolvedValue(mockedResponse)
      .mockResolvedValueOnce(mockedResponse)
      .mockResolvedValueOnce({ headers: expectedHeaders, data: expectedData });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: MODEL_DOWNLOADED,
        pipelineUuid: pipelineUuid,
        modelUuid: modelUuid,
        data: expectedData,
        headers: expectedHeaders,
        filename: "",
        status: "SUCCESS",
        message: "Download Completed.",
      },
    ];

    await modelActions.checkDownloadRequestStatus(
      projectUuid,
      pipelineUuid,
      modelUuid,
      downloadType,
      downloadFileName,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should log an error when download request fails", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const pipelineUuid = "7107b18c-5d6c-4f31-aa8e-b5727fec4c3c";
    const modelUuid = "4ad93ade-65a6-4d36-a711-92624e912bc5";
    const downloadType = "bin";
    const downloadFileName =
      "kp_4ad93ade-65a6-4d36-a711-92624e912bc5_x86_GCC_Generic_GCC_7.2.0_p.zip";
    mockAxios.get
      .mockImplementation(() => {})
      .mockImplementationOnce(() => {
        throw new Error("Some Error");
      });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: MODEL_DOWNLOAD_FAILED,
        pipelineUuid: pipelineUuid,
        modelUuid: modelUuid,
        status: "FAILURE",
        error: "Some Error",
        message: "Some Error",
      },
    ];

    await modelActions.checkDownloadRequestStatus(
      projectUuid,
      pipelineUuid,
      modelUuid,
      downloadType,
      downloadFileName,
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });
});
