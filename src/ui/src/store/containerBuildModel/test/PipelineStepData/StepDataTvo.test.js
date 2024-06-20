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
import StepDataTvo from "../../domain/PipelineStepsDataFactory/StepDataTvo";
import { PIPELINE_STEP_TYPES } from "store/autoML/const";
import FORM_TYPES from "consts/FORM_TYPES";

const TVO_LIST = [
  PIPELINE_STEP_TYPES.CLASSIFIER,
  PIPELINE_STEP_TYPES.TRAINING_ALGORITHM,
  PIPELINE_STEP_TYPES.VALIDATION,
];

describe("StepDataTransform", () => {
  let store;
  let state;
  let pipelineSteps = [];
  store = setupMockStore();
  state = store.getState();
  pipelineSteps = state.autoML.pipelineHierarchyRules.data.filter(el => TVO_LIST.includes(el.type));

  pipelineSteps.forEach(step => {
    describe(`${step.type} ${step.subtype}`, () => {
      let transformDataClass;
      let inputData;
      transformDataClass = new StepDataTvo({
        state,
        type: step.type,
        subtype: step.subtype,
        id: step.id,
        queryName: "CDK_ALL_TYPES",
      });
      inputData = transformDataClass.getInputsData({
        transformList: step.transformList,
        excludeTransform: step.excludeTransform,
      });

      describe("Convert input contract types to dynamic form type", () => {

        it("first lvl should has fieldset array", () => {
          expect(inputData).toHaveProperty('fieldset');
        });
        inputData.fieldset.forEach(formElement => {
          it(`${formElement.name} has know type`, () => {
            expect(Object.values(FORM_TYPES)).toEqual(expect.arrayContaining([formElement.type]));
          });

          if ([FORM_TYPES.FORM_MULTI_SELECT_TYPE].includes(formElement.type)) {
            it(`${formElement.name} -- FORM_MULTI_SELECT_TYPE elements have options`, () => {
              expect(formElement?.options?.length > 0 || formElement?.isFormHidden).toBeTruthy();
            });
            it(`${formElement.name} -- FORM_MULTI_SELECT_TYPE elements have default values all options`, () => {
              expect(formElement?.options.map(el => el.value)).toEqual(expect.arrayContaining(formElement?.default));
            });
          }
          if ([FORM_TYPES.FORM_SELECT_TYPE].includes(formElement.type)) {
            it(`${formElement.name} -- FORM_SELECT_TYPE elements have options`, () => {
              expect(formElement?.options?.length > 0 || formElement?.isFormHidden).toBeTruthy();
            });
            it(`${formElement.name} -- FORM_MULTI_SELECT_TYPE elements contaon options`, () => {
              expect(formElement?.options.map(el => el.value)).toContain(formElement?.default);
            });
          }
        });
        
      });
    })
  });
});