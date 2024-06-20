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
import PipelineDataBuilderDefault from "../domain/PipelineDataDefault";
import defaultDataAutoML from "./data/defaultDataAutoML";
import defaultDataCustomClassifier from "./data/defaultDataCustomClassifier";
import setupMockStore from "./setupStore";

describe("PipelineDataDefault.test", () => {
  const store = setupMockStore();
  const state = store.getState();
  const queryName = "CDK_ALL_TYPES";

  it("Default classifier with AutoML", () => {
    const defaultOptions = {
      isAutoMLOptimization: true,
    };

    const PipelineSteps = new PipelineDataBuilderDefault(state, defaultOptions, queryName);
    const defaultPipelineSettings = PipelineSteps.getAutoMLStep();
    const defaultPipelineSteps = PipelineSteps.getPipelineStepData();

    const stepToEqual = [...defaultDataAutoML];
    stepToEqual.shift();

    // const pipelineSettings = defaultDataAutoML.shift();
    expect(defaultPipelineSettings).toEqual(defaultDataAutoML[0]);
    expect(defaultPipelineSteps).toEqual(stepToEqual);
  });

  it("Custom TF Micro classifier with AutoML", () => {
    const defaultOptions = {
      isAutoMLOptimization: false,
      selectedClassifier: "TensorFlow Lite for Microcontrollers",
    };

    const PipelineSteps = new PipelineDataBuilderDefault(state, defaultOptions, queryName);
    const defaultPipelineSettings = PipelineSteps.getAutoMLStep();
    const defaultPipelineSteps = PipelineSteps.getPipelineStepData();

    const stepToEqual = [...defaultDataCustomClassifier];
    stepToEqual.shift();

    const pipelineSettings = defaultDataCustomClassifier.shift();
    expect(defaultPipelineSettings).toEqual(pipelineSettings);
    expect(defaultPipelineSteps).toEqual(stepToEqual);
  });
});
