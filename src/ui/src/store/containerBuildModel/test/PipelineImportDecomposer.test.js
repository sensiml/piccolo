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
import setupMockStore from "./setupStore";

import importedPipelineBase from "./data/importedPipelineBase";
import importedPipelineBaseExpected from "./data/importedPipelineBaseExpected";
import importedPipelineLessSensorExpected from "./data/importedPipelineLessSensorExpected";
import importedPipelineSameSensorsExpected from "./data/importedPipelineSameSensorsExpected";

import PipelineImportDecomposer from "../domain/PipelineImportDecomposer";
import { ConsoleBodySimpleView } from "components/LogsView";

const AUTOML_NAME = "Pipeline Settings";
const ExcludedNamesFromHirerarchyCheck = ["Input Data", AUTOML_NAME];

const qoueryList = [
  {
    uuid: "1",
    name: "TEST_BASE_QUERY",
    columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
    label_column: "Label",
    metadata_columns: ["segment_uuid"],
    metadata_filter: "[Label] IN [Jab,Hook,Cross]",
    segmenter_id: 1,
    combine_labels: null,
    created_at: "2020-09-12T23:46:48.9057",
    capture_configurations: [],
    last_modified: "2020-09-13T20:43:33.390853Z",
    segmenter: 1,
  },
  {
    uuid: "2",
    name: "TEST_BASE_QUERY_2",
    columns: ["AccelerometerX", "AccelerometerY"],
    label_column: "Label",
    metadata_columns: ["segment_uuid"],
    metadata_filter: "[Label] IN [Jab,Hook,Cross]",
    segmenter_id: 1,
    combine_labels: null,
    created_at: "2020-09-12T23:46:48.9057",
    capture_configurations: [],
    last_modified: "2020-09-13T20:43:33.390853Z",
    segmenter: 1,
  },
  {
    uuid: "1",
    name: "TEST_BASE_QUERY_SAME_SENSORS",
    columns: ["AccX", "AccY", "AccZ"],
    label_column: "Label",
    metadata_columns: ["segment_uuid"],
    metadata_filter: "[Label] IN [Jab,Hook,Cross]",
    segmenter_id: 1,
    combine_labels: null,
    created_at: "2020-09-12T23:46:48.9057",
    capture_configurations: [],
    last_modified: "2020-09-13T20:43:33.390853Z",
    segmenter: 1,
  },
];

describe("PipelineImportDecomposer.test", () => {
  const store = setupMockStore({
    queries: {
      queryList: { data: [...qoueryList] },
    },
  });
  const state = store.getState();
  const queryName = "TEST_BASE_QUERY";

  test("regular pipeline with replacement for all columns", () => {
    const defaultOptions = {
      pipelineJson: importedPipelineBase,
      replacedColumns: { AccX: "AccelerometerX", AccY: "AccelerometerY", AccZ: "AccelerometerZ" },
      isUseSessionPreprocessor: true,
    };
    const decomposer = new PipelineImportDecomposer(
      state,
      importedPipelineBase,
      queryName,
      defaultOptions,
    );
    const decomposedPipelineSteps = decomposer.getPipelineStepData();
    const decomposedPipelineSettings = decomposer.getAutoMLStep();

    expect(decomposedPipelineSteps).toEqual(importedPipelineBaseExpected.pipeline);
    expect(decomposedPipelineSettings).toEqual(importedPipelineBaseExpected.pipelineSettings);
  });

  test("regular pipeline with replacement for all columns wt Query", () => {
    const defaultOptions = {
      replacedColumns: { AccX: "AccelerometerX", AccY: "AccelerometerY", AccZ: "AccelerometerZ" },
      isUseSessionPreprocessor: true,
    };
    const pipelineToImport = { ...importedPipelineBase };
    pipelineToImport.pipeline = importedPipelineBase.pipeline.slice(1);
    const decomposer = new PipelineImportDecomposer(
      state,
      pipelineToImport,
      queryName,
      defaultOptions,
    );
    const decomposedPipelineSteps = decomposer.getPipelineStepData();
    const decomposedPipelineSettings = decomposer.getAutoMLStep();
    expect(decomposedPipelineSteps).toEqual(importedPipelineBaseExpected.pipeline);
    expect(decomposedPipelineSettings).toEqual(importedPipelineBaseExpected.pipelineSettings);
  });

  test("regular pipeline with replacement for all columns wt Query", () => {
    const defaultOptions = {
      replacedColumns: { AccX: "AccelerometerX", AccY: "AccelerometerY", AccZ: "AccelerometerZ" },
      isUseSessionPreprocessor: false,
    };
    const pipelineToImport = { ...importedPipelineBase };
    const importrtedPipleineToExpect = importedPipelineBaseExpected;
    importrtedPipleineToExpect.pipeline[0].data.use_session_preprocessor = false;

    pipelineToImport.pipeline = importedPipelineBase.pipeline.slice(1);

    const decomposer = new PipelineImportDecomposer(
      state,
      pipelineToImport,
      queryName,
      defaultOptions,
    );
    const decomposedPipelineSteps = decomposer.getPipelineStepData();
    const decomposedPipelineSettings = decomposer.getAutoMLStep();
    expect(decomposedPipelineSteps).toEqual(importrtedPipleineToExpect.pipeline);
    expect(decomposedPipelineSettings).toEqual(importrtedPipleineToExpect.pipelineSettings);
  });

  test("regular pipeline with replacement for all columns wt replaced columns", () => {
    const defaultOptions = {};
    const pipelineToImport = { ...importedPipelineBase };

    const decomposer = new PipelineImportDecomposer(
      state,
      pipelineToImport,
      "TEST_BASE_QUERY_SAME_SENSORS",
      defaultOptions,
    );
    const decomposedPipelineSteps = decomposer.getPipelineStepData();
    const decomposedPipelineSettings = decomposer.getAutoMLStep();
    expect(decomposedPipelineSteps).toEqual(importedPipelineSameSensorsExpected.pipeline);
    expect(decomposedPipelineSettings).toEqual(
      importedPipelineSameSensorsExpected.pipelineSettings,
    );
  });

  test("regular pipeline with replacement for less columns", () => {
    const defaultOptions = {
      replacedColumns: { AccX: "AccelerometerX", AccY: "AccelerometerY" },
      use_session_preprocessor: true,
    };
    const decomposer = new PipelineImportDecomposer(
      state,
      importedPipelineBase,
      "TEST_BASE_QUERY_2",
      defaultOptions,
    );
    const decomposedPipelineSteps = decomposer.getPipelineStepData();
    const exptectedPipeline = [...importedPipelineLessSensorExpected.pipeline];
    exptectedPipeline[0].options.descriptionParameters.uuid = "2";
    expect(decomposedPipelineSteps).toEqual(exptectedPipeline);
  });
});
