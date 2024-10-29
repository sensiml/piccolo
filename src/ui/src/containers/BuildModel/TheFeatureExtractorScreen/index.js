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
import { connect } from "react-redux";
import { loadPipelinesHierarchyRules } from "store/autoML/actions";
import {
  setPipelineStep,
  setPipelineDefaultSteps,
  updatePipelineStepsWithQuery,
  launchModelOptimization,
  checkOptimizationStatus,
  loadPipelineBuilderData,
  loadDataAfterTraining,
  stopModelOptimization,
  clearAlertBuilder,
  clearPipelineValidationError,
} from "store/containerBuildModel/actions";
import {
  clearOptimizationLogs,
  clearPipelineResults,
  clearPipelineStatus,
  loadPipelineResults,
  clearPipeline,
  downloadPipelineStepCache,
  loadPipeline,
  setSelectedPipeline,
  exportPipeline,
  getPipelineStepFeatureStats,
} from "store/pipelines/actions";

import {
  loadQueryCacheStatus,
  clearQueryCacheStatus,
  buildQueryCache,
  loadQueryStatistic,
} from "store/queries/actions";

import { selectedQueryData } from "store/containerBuildModel/selectors";
import { selectPipelineStepDescription } from "store/autoML/selectors";

import getPipelineStepDataClass from "store/containerBuildModel/domain/PipelineStepsDataFactory";
import TheFeatureExtractorScreen from "./TheFeatureExtractorScreen";
import { selectLabelValuesColors, selectLabelValuesByName } from "store/labels/selectors";

const mapStateToProps = (state) => {
  return {
    alertBuilder: state.containerBuildModel?.alertBuilder || {},
    pipelineValidationError: state.containerBuildModel?.pipelineValidationError,
    defaultOptions: state.router?.location?.state,
    pipelineHierarchyRules: state.autoML.pipelineHierarchyRules?.data,
    transforms: state.transforms?.data,
    selectedPipeline: state.pipelines?.selectedPipeline,
    pipelineData: state.pipelines?.pipelineData?.data || {},
    selectedProjectObj: state.projects?.selectedProject || {},
    navBarIsOpen: state?.common?.values?.navBarIsOpen,
    getQueryData: (queryName) => selectedQueryData(state, queryName),
    getPipelineStepDataClass: (params) => getPipelineStepDataClass({ ...params, state }),
    getPipelineStepDescription: selectPipelineStepDescription,

    queryCacheStatusData: state.queries?.queryCacheStatus?.data,
    optimizationLogs: state.pipelines.optimizationLogs || [],
    pipelineRunningStatus: state.pipelines.pipelineRunningStatus || "",
    pipelineStatus: state.pipelines?.pipelineStatus.data,
    pipelineResults: state.pipelines?.pipelineResults?.data,
    pipelineResultsIsFetching: state.pipelines?.pipelineResults?.isFetching,

    selectLabelValuesColors: (labelName) => selectLabelValuesColors(labelName || "Label")(state),
    selectLabelValuesByName: (labelName) => selectLabelValuesByName(labelName || "Label")(state),

    queryStatistic: state.queries?.queryStatistic?.data || {},
    queryList: state.queries?.queryList?.data || [],
  };
};

const mapDispatchToProps = {
  clearAlertBuilder,
  clearPipelineValidationError,
  clearOptimizationLogs,
  clearPipelineResults,
  clearPipelineStatus,
  clearPipeline,
  clearQueryCacheStatus,

  setPipelineStep,
  setPipelineDefaultSteps,
  setSelectedPipeline,
  updatePipelineStepsWithQuery,

  launchModelOptimization,
  checkOptimizationStatus,

  loadPipelinesHierarchyRules,
  loadPipelineBuilderData,
  loadDataAfterTraining,
  loadPipelineResults,
  loadQueryCacheStatus,
  loadQueryStatistic,
  loadPipeline,

  stopModelOptimization,
  buildQueryCache,
  downloadPipelineStepCache,

  exportPipeline,
  getPipelineStepFeatureStats,
};

// export default connect(mapStateToProps, mapDispatchToProps)(TheFeatureExtractorScreen);
export default TheFeatureExtractorScreen;
