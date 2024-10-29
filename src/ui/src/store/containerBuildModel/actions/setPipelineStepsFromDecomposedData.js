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

/* eslint-disable no-unused-vars */
/* eslint-disable import/no-cycle */
import { getUniqueId } from "utils";
import { PIPELINE_STEP_TYPES, AUTOML_STEP } from "store/autoML/const";

const setPipelineStepsFromDecomposedData =
  (decomposedPipelineSteps) => async (_dispatch, getState) => {
    /**
     * updateting decomposed or pipeline steps with hirerarchy rules instructions
     * @return {Array} selectedPipelineSteps - updated pipeline array
     */

    const state = getState();
    const sepectedPipeline = state.pipelines?.selectedPipeline;
    const pipelineHierarchyRules = state.autoML.pipelineHierarchyRules?.data;
    let selectedPipelineSteps = [];

    if (sepectedPipeline && pipelineHierarchyRules?.length) {
      selectedPipelineSteps = decomposedPipelineSteps
        // .filter((step) => step.name !== AUTOML_STEP.name)
        .map((stepObj) => {
          const pipelineHierarchyStep = pipelineHierarchyRules.find(
            (el) => el.name === stepObj.name || el.type === stepObj.name,
          );
          return {
            ...pipelineHierarchyStep,
            customName: stepObj.customName,
            data: stepObj.data,
            options: stepObj.options || {},
            id: getUniqueId(),
          };
        });

      // release not mondatory steps without data, keep either query or input_data
      selectedPipelineSteps = selectedPipelineSteps.filter((stepObj) => {
        if ([PIPELINE_STEP_TYPES.QUERY, PIPELINE_STEP_TYPES.INPUT_DATA].includes(stepObj.type)) {
          // show only with data
          if (decomposedPipelineSteps?.length) {
            return Boolean(stepObj.data);
          }
          // or query when decomposedPipelineSteps is empty
          return stepObj.type === PIPELINE_STEP_TYPES.QUERY;
        }
        // && stepObj.type === PIPELINE_STEP_TYPES.FEATURE_SELECTOR
        return Boolean(stepObj.data || stepObj.mandatory);
      });
    }

    return selectedPipelineSteps;
  };

export default setPipelineStepsFromDecomposedData;
