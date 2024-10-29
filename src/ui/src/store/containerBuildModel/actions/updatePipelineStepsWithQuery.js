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

import { selectPipelineSteps } from "store/containerBuildModel/selectors";
import { PIPELINE_STEP_TYPES, PARENT_KEY, TRANSFORM_TYPES } from "store/autoML/const";
import PipelineDataBuilderDefault from "store/containerBuildModel/domain/PipelineDataDefault";

import PipelineDataDecomposer from "../domain/PipelineDataDecomposer";
import setPipelineStepsFromDecomposedData from "./setPipelineStepsFromDecomposedData";

const IGNORED_MANDATORY_TYPES = [PIPELINE_STEP_TYPES.INPUT_DATA, PIPELINE_STEP_TYPES.QUERY];
// eslint-disable-next-line no-unused-vars
const IGNORED_TRANFORMS_FOR_SESSION = [
  TRANSFORM_TYPES.SENSOR_FILTER,
  TRANSFORM_TYPES.SENSOR_TRANSFORM,
  TRANSFORM_TYPES.AUGMENTATION,
];

const getDefaultOptions = (selectedPipelineSteps) => {
  const stepAutoMLParams = selectedPipelineSteps.find(
    (step) => step.type === PIPELINE_STEP_TYPES.AUTOML_PARAMS,
  );
  const stepClassifier = selectedPipelineSteps.find(
    (step) => step.type === PIPELINE_STEP_TYPES.CLASSIFIER,
  );

  return {
    isAutoMLOptimization: !stepAutoMLParams?.data?.disable_automl,
    selectedClassifier: stepClassifier?.customName || "",
  };
};

export const updatePipelineStepsWithQuery =
  (queryStep = {}, pipelineSteps) =>
  async (dispatch, getState) => {
    const state = getState();
    const decomposer = new PipelineDataDecomposer(state, {});
    const sessionPipelineSteps = decomposer.getSessionStepData(queryStep?.data?.name);
    const pipelineHierarchyRules = state.autoML.pipelineHierarchyRules?.data;
    let selectedPipelineSteps = _.isUndefined(pipelineSteps)
      ? selectPipelineSteps(state)
      : pipelineSteps;
    // methods

    const getDefaultPipelineSteps = () => {
      return new PipelineDataBuilderDefault(
        state,
        getDefaultOptions(selectedPipelineSteps),
        queryStep?.data?.name,
      ).getPipelineStepData();
    };

    const isUseSessionSteps = () => {
      // SESSION STEPS
      if (queryStep?.data?.use_session_preprocessor === undefined) {
        return true;
      }
      return queryStep?.data?.use_session_preprocessor;
    };

    const getStepObj = (step) => {
      return {
        ...pipelineHierarchyRules.find(
          (rule) => rule.name === step.name || rule.type === step.name,
        ),
        customName: step.customName,
        data: step.data,
        options: step.options || {},
      };
    };

    const insertStepByHierarchyRules = (step) => {
      // let pipelineSavedNextStepIndex = 0;
      let pipelineSavedNextStepIndex = selectedPipelineSteps.findIndex((pplStep) => {
        return _.includes(pplStep?.nextSteps, step.name);
      });

      const isNextStep = (savedStep) => {
        return (
          _.includes(savedStep?.nextSteps, step.name) ||
          _.includes(savedStep?.nextSteps, PARENT_KEY)
        );
      };

      const isIgnoreSessionTransform = (savedStep) => {
        // set before transforms
        return (
          !IGNORED_TRANFORMS_FOR_SESSION.includes(savedStep?.name) ||
          (IGNORED_TRANFORMS_FOR_SESSION.includes(savedStep?.name) &&
            savedStep?.options?.isSessionPreprocess)
        );
      };

      while (
        selectedPipelineSteps[pipelineSavedNextStepIndex] &&
        pipelineSavedNextStepIndex < selectedPipelineSteps.length &&
        isNextStep(selectedPipelineSteps[pipelineSavedNextStepIndex]) &&
        isIgnoreSessionTransform(selectedPipelineSteps[pipelineSavedNextStepIndex])
      ) {
        pipelineSavedNextStepIndex++;
      }
      selectedPipelineSteps = selectedPipelineSteps.reduce((acc, el, index) => {
        if (pipelineSavedNextStepIndex === index) {
          acc.push(getStepObj(step));
        }
        acc.push(el);
        return acc;
      }, []);
    };

    const rebuildSelectedPipelineSteps = (step, initialSelectedPipelineSteps) => {
      const pipelineSavedStepIndex = initialSelectedPipelineSteps.findIndex((pplStep) => {
        if (
          (step.name === pplStep.name || step.name === pplStep.type) &&
          !step?.options?.isSessionPreprocess
        ) {
          return true;
        }
        if (
          pplStep?.options?.uniqueName &&
          pplStep?.options?.uniqueName === step?.options?.uniqueName
        ) {
          return true;
        }
        return false;
      });

      if (pipelineSavedStepIndex >= 0) {
        // store step before ovewrite
        selectedPipelineSteps[pipelineSavedStepIndex] = getStepObj(step);
      } else {
        // looking for pipelineSteps
        // with nextStep prop that include decomposed pipeline to add at this place
        insertStepByHierarchyRules(step);
      }
    };

    const selectDefaultPipeline = async () => {
      /**
       * this method build default pipeline
       */
      // is columns have different values -> rebuild with default parameters
      const reviwedStepNames = selectedPipelineSteps
        .filter((step) => step?.options?.is_should_be_reviewed)
        .map((step) => step.name);
      const defautltPipelineSteps = getDefaultPipelineSteps().map((step) => {
        return {
          ...step,
          options: { is_should_be_reviewed: reviwedStepNames.includes(step.name) },
        };
      });

      // eslint-disable-next-line no-return-await
      return await dispatch(setPipelineStepsFromDecomposedData(defautltPipelineSteps));
    };

    const addMandatoryStepsToSelectedPipelineSteps = (initialSelectedPipelineSteps) => {
      /**
       * this method checks missed mandatory steps and set them to pipiline with default values
       * in case when a previus Query had session some steps like Segmenter may be delete
       */
      const notSessionPipelineSteps = selectedPipelineSteps.filter(
        (step) => !step?.options?.isSession,
      );
      const defautltPipelineSteps = getDefaultPipelineSteps();
      const mandatorySteps = pipelineHierarchyRules.filter(
        (el) =>
          el.mandatory &&
          !IGNORED_MANDATORY_TYPES.includes(el.type) &&
          !notSessionPipelineSteps.find((step) => step.name === el.name),
      );

      mandatorySteps.forEach((mandatoryStep) => {
        const defaultStepData = defautltPipelineSteps.find(
          (step) => step.name === mandatoryStep.name,
        );
        rebuildSelectedPipelineSteps(
          { ...mandatoryStep, ...defaultStepData },
          initialSelectedPipelineSteps,
        );
      });

      return selectedPipelineSteps.filter((step) => !step?.options?.isSession);
    };

    // logic

    if (queryStep?.options?.isChangedColumns) {
      selectedPipelineSteps = await selectDefaultPipeline();
    }

    selectedPipelineSteps = addMandatoryStepsToSelectedPipelineSteps([...selectedPipelineSteps]);
    if (_.isEmpty(sessionPipelineSteps) || !isUseSessionSteps()) {
      return selectedPipelineSteps;
    }

    const sessionTransformNames = sessionPipelineSteps.map((step) => step.customName) || [];

    selectedPipelineSteps = selectedPipelineSteps.filter(
      (step) =>
        !IGNORED_TRANFORMS_FOR_SESSION.includes(step.name) ||
        (IGNORED_TRANFORMS_FOR_SESSION.includes(step.name) &&
          !sessionTransformNames.includes(step.customName)),
    );

    sessionPipelineSteps.forEach((step) => {
      rebuildSelectedPipelineSteps(step, [...selectedPipelineSteps]);
    });

    return selectedPipelineSteps;
  };
