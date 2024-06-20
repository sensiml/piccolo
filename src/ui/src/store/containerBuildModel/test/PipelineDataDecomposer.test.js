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

import customPipelinesToDecompose from "./data/customPipelinesToDecompose";
import autoMLToDecompose from "./data/autoMLToDecompose";
import setupMockStore from "./setupStore";
import PipelineDataDecomposer from "../domain/PipelineDataDecomposer";
import { AUTOML, PIPELINE_STEP_TYPES } from "store/autoML/const";

const AUTOML_NAME = "Pipeline Settings";
const ExcludedNamesFromHirerarchyCheck = ["Input Data", AUTOML_NAME];

const AUTOML_CORRECT_PARSED_PARAMS = {
  reset: true,
  iterations: 5,
  tvo: true,
  selectorset: false,
  single_model: false,
  allow_unknown: false,
  disable_automl: true,
  hardware_target: {
    classifiers_sram: 312,
  },
  population_size: 119,
  set_selectorset: {
    "Information Gain": {},
  },
  "prediction_target(%)": {
    accuracy: 100,
  },
  set_training_algorithm: {
    "Hierarchical Clustering with Neuron Optimization": {},
  },
  hierarchical_multi_model: true,
};

describe("PipelineDataDecomposer.test", () => {
  const store = setupMockStore();
  const state = store.getState();
  const hierarchyRules = state.autoML.pipelineHierarchyRules.data;

  describe("Custom Pipelines", () => {
    const decomposer = new PipelineDataDecomposer(state, customPipelinesToDecompose);
    const pipelineSteps = decomposer.getPipelineStepData();
    describe("each step should has customName and name", () => {
      pipelineSteps.forEach((step) => {
        test(`test ${step.name}`, () => {
          expect(step.customName).not.toBeUndefined();
          expect(step.name).not.toBeUndefined();
        });
      });
    });
    describe("each step should has data", () => {
      pipelineSteps.forEach((step) => {
        test(`test ${step.name}`, () => {
          expect(step.data).not.toBeUndefined();
        });
      });
    });
    describe("Names in hirerarchy rules", () => {
      pipelineSteps.forEach((step) => {
        it(`${step.name}`, () => {
          const pipelineSavedSteps = hierarchyRules.find(
            (el) => el.name === step.name || el.type === step.name,
          );
          expect(pipelineSavedSteps).not.toBeUndefined();
        });
      });
    });
  });

  describe("AuloML", () => {
    const decomposer = new PipelineDataDecomposer(state, autoMLToDecompose);

    const pipelineSteps = decomposer.getPipelineStepData();
    const pipelineSettings = decomposer.getAutoMLStep();
    it("each step should has customName and name", () => {
      pipelineSteps.forEach((step) => {
        expect(step.customName).not.toBeUndefined();
        expect(step.name).not.toBeUndefined();
      });
    });
    it("each step should has data", () => {
      pipelineSteps.forEach((step) => {
        expect(step.data).not.toBeUndefined();
      });
    });
    describe("Names in hirerarchy rules", () => {
      pipelineSteps
        .filter((step) => !ExcludedNamesFromHirerarchyCheck.includes(step.name))
        .forEach((step) => {
          it(`${step.name}`, () => {
            const pipelineSavedSteps = hierarchyRules.find(
              (el) => el.name === step.name || el.type === step.name,
            );
            expect(pipelineSavedSteps).not.toBeUndefined();
          });
        });
    });
    describe("AutoML params", () => {
      expect(pipelineSettings.data).toMatchObject(AUTOML_CORRECT_PARSED_PARAMS);
    });
  });
});
