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
import setPipelineDefaultStepsPipelineExpected from "../../test/data/setPipelineDefaultStepsPipelineExpected";
import pipelineToLoad from "../../test/data/setPipelineDefaultStepsPipeline";
import { PIPELINE_STEP_TYPES, TRANSFORM_TYPES } from "store/autoML/const";
import { setPipelineDefaultSteps } from "store/containerBuildModel/actions";
import mockQueryList from "store/queries/fixtures/mockQueryList";
import FORM_TYPES from "consts/FORM_TYPES";
import { getSelectedPipelineObj } from "store/pipelines/selectors";
import fs from "fs";

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

const queryList = [
  {
    uuid: "c4f3e6f6-0365-4cd6-9734-20e58929be1e",
    name: "Q1",
    columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
    label_column: "Label",
    metadata_columns: ["segment_uuid"],
    metadata_filter: "[Label] IN [Vertical,Stationary,Horizontal]",
    segmenter_id: 2,
    combine_labels: null,
    created_at: "2021-10-06T17:25:39.5063",
    capture_configurations: [],
    last_modified: "2021-11-30T23:36:57.404516Z",
    cache: [[39853, "c4f3e6f6-0365-4cd6-9734-20e58929be1e.0.gz"]],
    task_status: "CACHED",
    summary_statistics: {
      samples: {
        Vertical: 8830,
        Horizontal: 12239,
        Stationary: 18772,
      },
      segments: {
        Vertical: 3,
        Horizontal: 3,
        Stationary: 6,
      },
      total_segments: 12,
    },
    segmenter: 2,
  },
];

// replacedColumns,
// isUseSessionPreprocessor,

const START_LOADING_ACTION = {
  type: "SET_LOADING_PIPELINE_STEPS",
  payload: { isLoading: true, message: "Loading pipeline ..." },
};

const END_LOADING_ACTION = {
  type: "SET_LOADING_PIPELINE_STEPS",
  payload: { isLoading: false, message: "" },
};

let initialState = {
  sessions: sessionStore,
  queries: {
    queryList: { data: [...queryList] },
  },
  containerBuildModel: {
    pipelineStepData: {},
    pipelineJsonData: {},
    isAdvancedBuilding: true,
    isSelectScreenGridView: true,
    loadingPipelineSteps: {
      isLoading: false,
      message: "",
    },
    alertBuilder: {
      message: "",
      parameters: [],
      type: "info",
      header: "",
    },
  },
  pipelines: {
    selectedPipeline: pipelineToLoad.uuid,
    pipelineList: { data: [pipelineToLoad] },
    pipelineData: { data: pipelineToLoad, isFetching: false },
  },
};

describe("Query updating", () => {
  let store;
  let defaultOptions = {
    isAutoMLOptimization: false,
    selectedClassifier: "Bonsai",
    isUseSessionPreprocessor: true,
  };
  let selectedPipelineStepsToKeep;

  const checkActions = (actions, expectedPipeline) => {
    // type: 'SET_LOADING_PIPELINE_STEPS'
    expect(actions[0]).toEqual(START_LOADING_ACTION);
    // type: 'STORE_PIPELINE_STEPS'
    actions[1].payload[pipelineToLoad.uuid].forEach((step, index) => {
      expect({ ...step, id: "" }).toEqual({ ...expectedPipeline[index], id: "" });
    });
    // type: 'SET_LOADING_PIPELINE_STEPS'
    expect(actions[3]).toEqual(END_LOADING_ACTION);
  };

  describe("Full pipeline", () => {
    store = setupMockStore(initialState);
    test("should load basic pipeline to pipeline steps and pipeline json", async () => {
      await store.dispatch(setPipelineDefaultSteps(defaultOptions));
      const expectedPipeline = setPipelineDefaultStepsPipelineExpected;
      const actions = store.getActions();

      checkActions(actions, expectedPipeline);
      store.clearActions();
    });
  });
});
