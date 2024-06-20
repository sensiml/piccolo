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

/* eslint-disable */
//TODO: need to refactor and add new tests
import * as classifierActions from "./actions";
import { START_CLASSIFIER_RUN, END_CLASSIFIER_RUN, ADD_CLASSIFIER_TO_CACHE } from "./actionTypes";
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";
import "regenerator-runtime/runtime";
import mockAxios from "axios";

jest.mock("../../store/reducers.js");
const mockStore = configureMockStore([thunk]);

describe("classifier actions", () => {
  let store;
  beforeEach(() => {
    store = mockStore({
      pipelines: {},
    });
  });

  it("should start a classifier run with success", async () => {
    const expectedProjectId = "81cefa53-22c5-4af7-bcbe-33b7d9936c17";
    const expectedPipelineId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedModelId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const mockedResponse = Promise.resolve({ data: "" });
    const expectedRecognitionFileData = {
      uuid: "73e6b86b-3b86-45fa-a3f4-02feb9112515",
      type: "captures",
      name: "testfile.csv",
      kb_description: [],
    };
    mockAxios.post.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: START_CLASSIFIER_RUN,
        status: "SUBMITTING",
        response: null,
      },
    ];

    await classifierActions.submitClassifier(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      expectedRecognitionFileData,
    )(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should stop a classifier run post with errors", async () => {
    const expectedProjectId = "81cefa53-22c5-4af7-bcbe-33b7d9936c17";
    const expectedPipelineId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedModelId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const expectedRecognitionFileData = {
      type: "captures",
      name: "testfile.csv",
      kb_description: [],
    };

    mockAxios.post.mockImplementation(() => {
      throw new Error("Some Error");
    });

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: START_CLASSIFIER_RUN,
        uuid: expectedRecognitionFileData.uuid,
        status: "SUBMITTING",
        response: null,
      },
      {
        type: END_CLASSIFIER_RUN,
        status: "ERROR",
        response: "Some Error",
      },
    ];

    await classifierActions.submitClassifier(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      [],
      [],
      expectedRecognitionFileData,
    )(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should ignore a classifier run if projectId is undefined", async () => {
    const expectedProjectId = undefined;
    const expectedPipelineId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedModelId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const expectedRecognitionFileData = {
      type: "captures",
      name: "testfile.csv",
      kb_description: [],
    };
    const mockedResponse = Promise.resolve({ data: "" });
    mockAxios.post.mockResolvedValue(mockedResponse);

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: START_CLASSIFIER_RUN,
        uuid: expectedRecognitionFileData.uuid,
        status: "SUBMITTING",
        response: null,
      },
    ];

    await classifierActions.submitClassifier(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      expectedRecognitionFileData,
    )(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should ignore a classifier run if pipeline is undefined", async () => {
    const expectedProjectId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedPipelineId = undefined;
    const expectedModelId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const expectedRecognitionFileData = {
      type: "captures",
      name: "testfile.csv",
      kb_description: [],
    };
    const mockedResponse = Promise.resolve({ data: "" });
    mockAxios.post.mockResolvedValue(mockedResponse);

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: START_CLASSIFIER_RUN,
        uuid: expectedRecognitionFileData.uuid,
        status: "SUBMITTING",
        response: null,
      },
    ];

    await classifierActions.submitClassifier(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      expectedRecognitionFileData,
    )(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should ignore a classifier run if model is undefined", async () => {
    const expectedProjectId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedPipelineId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const expectedModelId = undefined;
    const expectedRecognitionFileData = {
      type: "captures",
      name: "testfile.csv",
      kb_description: [],
    };
    const mockedResponse = Promise.resolve({ data: "" });
    mockAxios.post.mockResolvedValue(mockedResponse);

    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: START_CLASSIFIER_RUN,
        uuid: expectedRecognitionFileData.uuid,
        status: "SUBMITTING",
        response: null,
      },
    ];

    await classifierActions.submitClassifier(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      expectedRecognitionFileData,
    )(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should stop a classifier run with errors", async () => {
    const expectedProjectId = "81cefa53-22c5-4af7-bcbe-33b7d9936c17";
    const expectedPipelineId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedModelId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const mockedResponse = Promise.resolve({ data: "" });
    mockAxios.post.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        response: null,
        status: "SUBMITTING",
        type: START_CLASSIFIER_RUN,
      },
      {
        type: END_CLASSIFIER_RUN,
        status: "ERROR",
      },
    ];

    await classifierActions.submitClassifier(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      null,
    )(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0].type).toEqual(expectedActions[1].type);
    expect(dispatch.mock.calls[1][0].status).toEqual(expectedActions[1].status);
  });

  it("should check classifier run status finished without errors", async () => {
    const expectedProjectId = "81cefa53-22c5-4af7-bcbe-33b7d9936c17";
    const expectedPipelineId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedModelId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const expectedRecognitionFileData = {
      type: "captures",
      name: "testfile.csv",
      kb_description: [],
    };
    const expectedResult = [
      {
        Classification: 1,
        ClassificationName: "Block",
        FeatureVector: [
          36, 119, 181, 254, 177, 112, 154, 185, 175, 0, 45, 39, 185, 255, 140, 113, 112, 94, 2, 0,
        ],
        ModelName: "0",
        SegmentEnd: 2047,
        SegmentID: 0,
        SegmentLength: 2048,
        SegmentStart: 0,
        Capture: "testfile.csv",
      },
      {
        Classification: 3,
        ClassificationName: "Normal",
        FeatureVector: [
          15, 86, 183, 198, 115, 255, 123, 27, 122, 97, 68, 104, 195, 254, 96, 179, 32, 163, 50, 34,
        ],
        ModelName: "0",
        SegmentEnd: 6143,
        SegmentID: 2,
        SegmentLength: 2048,
        SegmentStart: 4096,
        Capture: "testfile.csv",
      },
      {
        Classification: 2,
        ClassificationName: "Idle",
        FeatureVector: [
          0, 70, 33, 65, 62, 52, 197, 148, 200, 245, 0, 61, 8, 112, 92, 254, 209, 51, 0, 208,
        ],
        ModelName: "0",
        SegmentEnd: 38911,
        SegmentID: 18,
        SegmentLength: 2048,
        SegmentStart: 36864,
        Capture: "testfile.csv",
      },
    ];
    const expectedGroundTruth = [
      {
        Capture: "testfile.csv",
        Label_Value: "Normal",
        SegmentStart: 592,
        SegmentEnd: 500019,
        Session: "Manual",
      },
    ];
    const expectedConfusionMatrix = {
      unknown: {
        unknown: 0,
        Block: 0,
        Idle: 0,
        Normal: 0,
      },
      Block: {
        unknown: 0,
        Block: 0,
        Idle: 0,
        Normal: 40,
      },
      Idle: {
        unknown: 0,
        Block: 0,
        Idle: 0,
        Normal: 23,
      },
      Normal: {
        unknown: 0,
        Block: 0,
        Idle: 0,
        Normal: 181,
      },
    };
    const expectedResponseBody = {
      results: expectedResult,
      ground_truth: expectedGroundTruth,
      confusion_matrix: {
        Manual: {
          "testfile.csv": expectedConfusionMatrix,
        },
      },
    };
    const mockedResponse = Promise.resolve({ data: expectedResponseBody });

    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: ADD_CLASSIFIER_TO_CACHE,
        classifierData: {
          "testfile.csv": {
            accuracy: { Manual: "74.18" },
            cacheKey:
              "6cd35463-d372-48ec-b62d-0e4197aad53d-63ad0103-060d-4b8a-8958-e6e48349ca3d-undefined",
            captureUuid: undefined,
            fileName: "testfile.csv",
            results: expectedResult,
            ground_truth: expectedGroundTruth,
            sessions: ["Manual"],
            confusion_matrices: { Manual: expectedConfusionMatrix },
          },
        },
      },
      {
        response: {
          accuracy: { Manual: "74.18" },
          cacheKey:
            "6cd35463-d372-48ec-b62d-0e4197aad53d-63ad0103-060d-4b8a-8958-e6e48349ca3d-undefined",
          captureUuid: undefined,
          fileName: "testfile.csv",
          results: expectedResult,
          ground_truth: expectedGroundTruth,
          sessions: ["Manual"],
          confusion_matrices: { Manual: expectedConfusionMatrix },
        },
        type: START_CLASSIFIER_RUN,
        status: "SUCCESS",
        uuid: undefined,
      },
    ];

    await classifierActions.checkClassifierRunStatus(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      [{ type: "capture", name: "testfile.csv" }],
      "Manual",
    )(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should check classifier run status not finished without errors", async () => {
    const expectedProjectId = "81cefa53-22c5-4af7-bcbe-33b7d9936c17";
    const expectedPipelineId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedModelId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const expectedRecognitionFileData = {
      type: "captures",
      name: "testfile.csv",
      kb_description: [],
    };

    const expectedResponseBody = { status: "RUNNING" };
    const mockedResponse = Promise.resolve({ data: expectedResponseBody });

    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: START_CLASSIFIER_RUN,
        uuid: expectedRecognitionFileData.uuid,
        status: expectedResponseBody.status,
      },
    ];

    await classifierActions.checkClassifierRunStatus(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      expectedRecognitionFileData,
    )(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });

  it("should check classifier run status with errors", async () => {
    const expectedProjectId = "81cefa53-22c5-4af7-bcbe-33b7d9936c17";
    const expectedPipelineId = "6cd35463-d372-48ec-b62d-0e4197aad53d";
    const expectedModelId = "63ad0103-060d-4b8a-8958-e6e48349ca3d";
    const expectedRecognitionFileData = {
      type: "captures",
      name: "testfile.csv",
      kb_description: [],
    };

    const expectedResponseBody = { status: "FAILURE" };
    const mockedResponse = Promise.resolve({ data: expectedResponseBody });

    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: END_CLASSIFIER_RUN,
        uuid: expectedRecognitionFileData.uuid,
        status: "ERROR",
        response: expectedResponseBody,
      },
    ];

    await classifierActions.checkClassifierRunStatus(
      expectedProjectId,
      expectedPipelineId,
      expectedModelId,
      expectedRecognitionFileData,
    )(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
  });
});
