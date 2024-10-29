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
import i18n from "i18n";

import { store } from "store";
import { STATUSES } from "consts";

import {
  selectPipelineSteps,
  selectSelectedQueryObj,
  selectTranformSegmentColumns,
} from "store/containerBuildModel/selectors";
import { addToQueryManualObj } from "store/queries/actions";
import {
  updatePipeline,
  submitOptimizationRequest,
  checkOptimizationRunning,
  clearOptimizationLogs,
  clearOptimizationDetailedLogs,
  updateOptimizationLogs,
  runOptimization,
  killOptimizationRequest,
  loadPipeline,
  loadIterationMetrics,
  loadPipelineResults,
  setPipelineExecutionType,
} from "store/pipelines/actions";

import { optimizeProject } from "store/projects/actions";
import PipelineDataBuilderDefault from "store/containerBuildModel/domain/PipelineDataDefault";
import PipelineImportDecomposer from "store/containerBuildModel/domain/PipelineImportDecomposer";

import { getSelectedPipelineObj } from "store/pipelines/selectors";
import {
  STORE_PIPELINE_STEPS,
  STORE_PIPELINE_JSON,
  STORE_PIPELINE_VALIDATION_ERROR,
} from "store/containerBuildModel/actionTypes";
import { PIPELINE_STEP_TYPES, TVO_LIST } from "store/autoML/const";

import PipelineDataComposer from "../domain/PipelineDataComposer";
import setPipelineStepsFromDecomposedData from "./setPipelineStepsFromDecomposedData";
import getPipelineDecomposerClass from "./getPipelineDecomposerClass";

import { updatePipelineStepsWithQuery } from "./updatePipelineStepsWithQuery";
import { setLoadingPipelineSteps } from "./setLoadingPipelineSteps";
import { setAlertBuilder, clearAlertBuilder } from "./setAlertBuilder";
import { clearPipelineValidationError } from "./setPiepelineValidationError";

export { updatePipelineStepsWithQuery };
export { clearPipelinesteps } from "./clearPipelinesteps";

export { setLoadingPipelineSteps };
export { setAlertBuilder, clearAlertBuilder };
export { clearPipelineValidationError };

// eslint-disable-next-line max-len
export const buildPipelineJson =
  (selectedPipeline, selectedSteps, pipelineSettingsData = {}) =>
  async (dispatch) => {
    const state = store.getState();
    const selectedQueryData = selectSelectedQueryObj(state);
    const [featureTransformColumns, segmentColumns] = selectTranformSegmentColumns(state);

    const { pipelineList, autoMLSeed } = new PipelineDataComposer(
      selectedSteps,
      selectedQueryData,
      featureTransformColumns,
      segmentColumns,
    ).getPipelineData(pipelineSettingsData);
    dispatch({
      type: STORE_PIPELINE_JSON,
      payload: {
        [selectedPipeline]: { pipelineList, autoMLSeed },
      },
    });
  };

export const setPipelineStep =
  (pipelineId, pipelineSteps, pipelineSettings, isAutoML) => async (dispatch) => {
    dispatch({ type: STORE_PIPELINE_VALIDATION_ERROR, payload: "" });
    await dispatch({ type: STORE_PIPELINE_STEPS, payload: { [pipelineId]: [...pipelineSteps] } });
    const state = store.getState();
    const [featureTransformColumns, segmentColumns] = selectTranformSegmentColumns(state);

    const selectedQueryData = selectSelectedQueryObj(state);
    const pipelineObj = getSelectedPipelineObj(state);
    const selectedProject = state.projects?.selectedProject;
    const pipelineSettingsData = {
      ...(!_.isUndefined(pipelineSettings?.data) && pipelineSettings?.data),
      ...(!_.isUndefined(isAutoML) && { disable_automl: !isAutoML }),
    };
    const { pipelineList, autoMLSeed } = new PipelineDataComposer(
      pipelineSteps,
      selectedQueryData,
      featureTransformColumns,
      segmentColumns,
    ).getPipelineData(pipelineSettingsData);

    if (pipelineObj) {
      await dispatch(
        updatePipeline({
          projectUuid: selectedProject.uuid,
          pipelineUuid: pipelineId,
          pipelineSteps: pipelineList,
          autoMLSeed,
          pipelineName: pipelineObj.name,
          cacheEnabled: pipelineObj.cache_enabled,
          deviceConfig: pipelineObj.device_config,
        }),
      );
    }

    dispatch(buildPipelineJson(pipelineId, pipelineSteps, pipelineSettingsData));
  };

export const setPipelineDefaultSteps = (defaultOptions) => async (dispatch, getState) => {
  const state = getState();
  const selectedPipeline = state.pipelines?.selectedPipeline;

  let selectedPipelineSteps = selectPipelineSteps(state);
  let decomposedPipelineSteps = [];

  dispatch(setLoadingPipelineSteps(true, "Loading pipeline ..."));

  const [decomposer, isUpdatePipline = false] = getPipelineDecomposerClass(
    state,
    defaultOptions || {},
  );

  const pipelineSettings = decomposer.getAutoMLStep();
  decomposedPipelineSteps = decomposer.getPipelineStepData();
  // manually adds Input query from Input data

  if (!_.isEmpty(decomposer.reviewedStepsParams)) {
    let alertTitle = i18n.t("models:model-builder.alert-review-created-pipeline-title");
    let alertMessage = i18n.t("models:model-builder.alert-review-created-pipeline-message");
    if (decomposer instanceof PipelineImportDecomposer) {
      alertTitle = i18n.t("models:model-builder.alert-review-imported-pipeline-title");
      alertMessage = i18n.t("models:model-builder.alert-review-imported-pipeline-message");
    }
    dispatch(
      setAlertBuilder(alertMessage, {
        title: alertTitle,
        parameters: decomposer.reviewedStepsParams,
      }),
    );
  }

  if (decomposer.queryFromInputData) {
    dispatch(addToQueryManualObj(decomposer.queryFromInputData));
  }

  if (!_.isEmpty(decomposedPipelineSteps) && decomposer.isNeededToAddTVO) {
    const pipelineStepsWtTVO = decomposedPipelineSteps.filter(
      (step) => !TVO_LIST.includes(step.type),
    );
    const defaultTVOPipelineSteps = new PipelineDataBuilderDefault(
      state,
      defaultOptions,
    ).getPipelineTVOStepData();
    decomposedPipelineSteps = _.union(pipelineStepsWtTVO, defaultTVOPipelineSteps);
  }

  if (selectedPipeline && selectedPipelineSteps?.length !== decomposedPipelineSteps?.length) {
    // setPipelineStepsFromDecomposedData
    selectedPipelineSteps = await dispatch(
      setPipelineStepsFromDecomposedData(decomposedPipelineSteps),
    );
    // udapte with query session
    const queryStep = selectedPipelineSteps.find((step) => step.type === PIPELINE_STEP_TYPES.QUERY);

    if (queryStep) {
      selectedPipelineSteps = await dispatch(
        updatePipelineStepsWithQuery(
          {
            customName: queryStep.customName,
            data: {
              name: queryStep.customName,
              use_session_preprocessor: !_.isUndefined(defaultOptions?.isUseSessionPreprocessor)
                ? defaultOptions?.isUseSessionPreprocessor
                : queryStep?.data?.use_session_preprocessor,
            },
          },
          selectedPipelineSteps,
        ),
      );
    }
  }

  if (isUpdatePipline) {
    try {
      await dispatch(setPipelineStep(selectedPipeline, selectedPipelineSteps, pipelineSettings));
    } catch (err) {
      dispatch({ type: STORE_PIPELINE_VALIDATION_ERROR, payload: err.message });
    }
  } else {
    dispatch({
      type: STORE_PIPELINE_STEPS,
      payload: { [selectedPipeline]: [...selectedPipelineSteps] },
    });
    dispatch(buildPipelineJson(selectedPipeline, selectedPipelineSteps, pipelineSettings?.data));
  }

  dispatch(setLoadingPipelineSteps(false, ""));

  return [selectedPipelineSteps, pipelineSettings];
};

export const checkOptimizationStatus = (projectUUID, pipelineUUID) => async (dispatch) => {
  /**
   * check optimization status and store optimization logs
   */
  const isLauching = await dispatch(checkOptimizationRunning(projectUUID, pipelineUUID));
  dispatch(loadIterationMetrics(projectUUID, pipelineUUID));
  return isLauching;
};

export const loadPipelineBuilderData = (projectUUID, pipelineUUID) => async (dispatch) => {
  /**
   * loads additional data to render builder screen
   */
  dispatch(loadIterationMetrics(projectUUID, pipelineUUID));
};

export const loadDataAfterTraining =
  (projectUUID, pipelineUUID, labelKey = "Label") =>
  async (dispatch) => {
    /**
     * updates dependent data for new models
     */
    dispatch(loadPipelineResults(projectUUID, pipelineUUID, labelKey));
    dispatch(loadIterationMetrics(projectUUID, pipelineUUID));
    dispatch(loadPipeline(projectUUID, pipelineUUID));
  };

const getExecutionType = (executionType, isAutoML) => {
  let exType = "AUTOML";
  if (executionType === "pipeline") {
    exType = "FEATURE_EXTRACTOR";
  }
  if (executionType === "auto" && isAutoML) {
    exType = "CUSTOM";
  }
  return exType;
};

export const launchModelOptimization =
  (selectedSteps, pipelineSettings, executionType, isAutoML) => async (dispatch) => {
    const pipelineSettingsData = {
      ...(!_.isUndefined(pipelineSettings?.data) && pipelineSettings?.data),
      ...(!_.isUndefined(isAutoML) && { disable_automl: !isAutoML }),
    };
    const { autoMLSeed } = new PipelineDataComposer(selectedSteps).getPipelineData(
      pipelineSettingsData,
    );
    const state = store.getState();
    const selectedProject = state.projects?.selectedProject;
    const selectedPipeline = getSelectedPipelineObj(state);

    dispatch(setPipelineExecutionType(getExecutionType(executionType, isAutoML)));

    await dispatch(clearOptimizationLogs());
    await dispatch(clearOptimizationDetailedLogs());

    await dispatch(runOptimization());

    await dispatch(
      updateOptimizationLogs({
        status: STATUSES.INFO,
        message: "Optimizing Query...",
        isLauching: true,
      }),
    );

    await dispatch(optimizeProject(selectedProject.uuid));

    await dispatch(
      updateOptimizationLogs({
        status: STATUSES.INFO,
        message: "Query is optimized...",
        isLauching: true,
      }),
    );

    await dispatch(
      submitOptimizationRequest(selectedProject.uuid, selectedPipeline.uuid, {
        run_parallel: true,
        execution_type: executionType,
        auto_params: {
          seed: autoMLSeed.seed,
          params: { ...autoMLSeed.params },
        },
      }),
    );
  };

export const stopModelOptimization = (projectUUID, pipelineUUID) => async (dispatch) => {
  await dispatch(killOptimizationRequest(projectUUID, pipelineUUID));
};
