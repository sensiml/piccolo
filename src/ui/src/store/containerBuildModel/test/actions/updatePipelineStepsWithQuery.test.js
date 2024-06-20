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

import setupMockStore from "../setupStore";
import StepDataFeatureGenerator from "../../domain/PipelineStepsDataFactory/StepDataFeatureGenerator";
import { PIPELINE_STEP_TYPES, TRANSFORM_TYPES } from "store/autoML/const";
import MockAdapter from "axios-mock-adapter";
import mockAxios from "axios";
import api, { setAuthHeader } from "store/api";
import {
  updatePipelineStepsWithQuery,
  setPipelineDefaultSteps,
  setPipelineStep,
} from "store/containerBuildModel/actions";
import mockQueryList from "store/queries/fixtures/mockQueryList";
import FORM_TYPES from "consts/FORM_TYPES";

const sessionStore = {
  data: [
    {
      id: 1,
      parent: null,
      name: "My Auto Session",
      function: null,
      parameters:
        '{"inputs":{"input_data":"","first_column_of_interest":"Magnitude_ST_0000","second_column_of_interest":"Magnitude_ST_0001","group_columns":[],"max_segment_length":169,"min_segment_length":68,"threshold_space_width":20,"first_vt_threshold":4464.99658,"first_threshold_space":"sum","first_comparison":"max","second_vt_threshold":1534.0509,"second_threshold_space":"sum","second_comparison":"min","drop_over":false,"return_segment_index":false},"type":"segmenter","name":"General Threshold Segmentation","uuid":"5d685c61-26d7-4298-b309-615732d7fb62","outputs":["temp.Segmenting0"]}',
      custom: false,
      preprocess:
        '{"0":{"name":"MagnitudeGxGyGz","actual_name":"Magnitude_ST_0000","params":{"name":"Magnitude","type":"transform","feature_table":null,"outputs":["temp.Preprocess0"],"inputs":{"input_columns":["GyroscopeX","GyroscopeY","GyroscopeZ"],"input_data":"temp.raw"}}},"1":{"name":"MagnitudeAxAyAz","actual_name":"Magnitude_ST_0001","params":{"name":"Magnitude","type":"transform","feature_table":null,"outputs":["temp.Preprocess1"],"inputs":{"input_columns":["AccelerometerX","AccelerometerY","AccelerometerZ"],"input_data":"temp.Preprocess0"}}}}',
      created_at: "2021-08-02T15:51:18.781128Z",
      last_modified: "2021-08-02T15:51:18.781151Z",
    },
    {
      id: 2,
      parent: null,
      name: "My Training Session",
      function: null,
      parameters: null,
      custom: true,
      preprocess: null,
      created_at: "2021-08-02T15:51:18.949821Z",
      last_modified: "2021-08-02T15:51:18.949841Z",
    },
  ],
  isFetching: false,
};

const addedTransform = {
  name: "Sensor Transform",
  customName: "Magnitude",
  nextSteps: ["Parent"],
  mandatory: false,
  type: "Transform",
  subtype: ["Sensor"],
  transformFilter: [
    {
      Type: "Transform",
      Subtype: "Sensor",
    },
  ],
  transformList: [],
  excludeTransform: [],
  limit: null,
  set: false,
  id: "1d6d82ec-3526-4b4d-81bf-e4de66f8dc70",
  data: {
    input_columns: ["GyroscopeX", "GyroscopeY", "GyroscopeZ"],
    input_data: "temp.raw",
    transform: "Magnitude",
  },
};

const addedUndeletedTransform = {
  name: "Sensor Transform",
  customName: "Second Derivative",
  nextSteps: ["Parent"],
  mandatory: false,
  type: "Transform",
  subtype: ["Sensor"],
  transformFilter: [
    {
      Type: "Transform",
      Subtype: "Sensor",
    },
  ],
  transformList: [],
  excludeTransform: [],
  limit: null,
  set: false,
  id: "1d6d82ec-3526-4b4d-81bf-e4de66f8dc70",
  data: {
    input_columns: ["GyroscopeX", "GyroscopeY", "GyroscopeZ"],
    input_data: "temp.raw",
    transform: "Second Derivative",
  },
};

const queryDataAuto = mockQueryList.data[0];
const queryDataManual = mockQueryList.data[1];

describe("Query updating", () => {
  let store;
  let state;
  let pipelineSteps = [];

  store = setupMockStore({ sessions: sessionStore });
  state = store.getState();
  let selectedPipelineStepsToKeep;

  // const mockedPipelineResponse = Promise.resolve({
  //   data: {},
  //   status: 200,
  // });

  // mockAxios.put.mockResolvedValue(mockedPipelineResponse);

  // state.containerBuildModel.pipelineStepData[state.pipelines.selectedPipeline]

  // isAutoMLOptimization
  const mockResponseAdapter = new MockAdapter(api);
  mockResponseAdapter
    // scope should be sent at one time with expired token reponse
    .onPut()
    .replyOnce(200, { data: {} });

  beforeAll(async () => {
    let selectedPieplineSteps =
      state.containerBuildModel.pipelineStepData[state.pipelines.selectedPipeline];

    selectedPieplineSteps.splice(1, 0, addedTransform);
    selectedPieplineSteps.splice(2, 0, addedUndeletedTransform);

    await store.dispatch(setPipelineStep(state.pipelines.selectedPipeline, selectedPieplineSteps));
    await store.dispatch(setPipelineDefaultSteps({ isAutoMLOptimization: true }));
  });

  it("should sessions steps with use_session_preprocessor is true", async () => {
    selectedPipelineStepsToKeep = await store.dispatch(
      updatePipelineStepsWithQuery(
        {
          customName: queryDataAuto.name,
          data: { name: queryDataAuto.name, use_session_preprocessor: true },
          options: { isChangedColumns: false },
        },
        true,
      ),
    );

    const sermenter = selectedPipelineStepsToKeep.find(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    const sermenterIndex = selectedPipelineStepsToKeep.findIndex(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    const sensorTransforms = selectedPipelineStepsToKeep.filter(
      (step) => step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM,
    );
    const sensorTransformIndex = selectedPipelineStepsToKeep.findIndex(
      (step) =>
        step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM &&
        step.customName === "Magnitude" &&
        step.options?.isSession,
    );

    expect(sermenter.customName).toEqual("General Threshold Segmentation");
    expect(sermenterIndex).toEqual(4);
    expect(sensorTransforms.length).toEqual(3); // 1 manual + 2 from session
    expect(sensorTransformIndex).toEqual(1); // session transforms shoub be at the top
  });

  it("should set default segmenter and remove all session steps", async () => {
    const selectedPipelineStepsToKeep = await store.dispatch(
      updatePipelineStepsWithQuery(
        {
          customName: queryDataAuto.name,
          data: { name: queryDataAuto.name, use_session_preprocessor: false },
          options: { isChangedColumns: false },
        },
        true,
      ),
    );

    const sermenter = selectedPipelineStepsToKeep.find(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    const sermenterIndex = selectedPipelineStepsToKeep.findIndex(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    const sensorTransformIndex = selectedPipelineStepsToKeep.findIndex(
      (step) => step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM,
    );
    const sensorTransforms = selectedPipelineStepsToKeep.filter(
      (step) => step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM,
    );

    expect(sermenter.customName).toEqual("Windowing");
    expect(sermenterIndex).toEqual(3);
    expect(sensorTransforms.length).toEqual(2); // only custom sensor transform
    expect(sensorTransformIndex).toEqual(1);
  });

  it("should first add session steps and remove after with different query", async () => {
    let selectedPipelineSteps = await store.dispatch(
      updatePipelineStepsWithQuery(
        {
          customName: queryDataAuto.name,
          data: { name: queryDataAuto.name, use_session_preprocessor: true },
          options: { isChangedColumns: false },
        },
        true,
      ),
    );

    const sermenter = selectedPipelineSteps.find(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    const sermenterIndex = selectedPipelineSteps.findIndex(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    const sensorTransformIndex = selectedPipelineSteps.findIndex(
      (step) =>
        step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM &&
        step.customName === "Magnitude" &&
        step.options?.isSession,
    );
    const sensorTransforms = selectedPipelineSteps.filter(
      (step) => step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM,
    );

    expect(sermenter.customName).toEqual("General Threshold Segmentation");
    expect(sermenterIndex).toEqual(4);
    expect(sensorTransforms.length).toEqual(3); // 1 manual + 2 from session
    expect(sensorTransformIndex).toEqual(1); // session transforms shoub be at the top

    state.containerBuildModel.pipelineStepData[state.pipelines.selectedPipeline] =
      selectedPipelineSteps;

    selectedPipelineSteps = await store.dispatch(
      updatePipelineStepsWithQuery(
        {
          customName: queryDataManual.name,
          data: { name: queryDataManual.name, use_session_preprocessor: true },
          options: { isChangedColumns: false },
        },
        true,
      ),
    );

    const sermenterManual = selectedPipelineSteps.find(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    const sermenterIndexManual = selectedPipelineSteps.findIndex(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    const sensorTransformIndexManual = selectedPipelineSteps.findIndex(
      (step) => step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM && !step.options?.isSession,
    );
    const sensorTransformsManual = selectedPipelineSteps.filter(
      (step) => step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM && !step.options?.isSession,
    );

    expect(sermenterManual.customName).toEqual("Windowing");
    expect(sermenterIndexManual).toEqual(2);
    expect(sensorTransformsManual.length).toEqual(1); // only custom sensor transform without magnitutes
    expect(sensorTransformIndexManual).toEqual(1);
  });
});
