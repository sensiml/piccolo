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
  clearPipelineExecutionType,
  exportPipeline,
  getPipelineStepFeatureStats,
  setSelectedPipelineName,
} from "store/pipelines/actions";

import {
  loadQueryCacheStatus,
  clearQueryCacheStatus,
  buildQueryCache,
  loadQueryStatistic,
} from "store/queries/actions";

import { selectedQueryData } from "store/containerBuildModel/selectors";
import { selectPipelineStepDescription } from "store/autoML/selectors";

import { getPipelineResultTableData } from "store/pipelines/selectors/";
import { selectLabelValuesColors, selectLabelValuesByName } from "store/labels/selectors";

import getPipelineStepDataClass from "store/containerBuildModel/domain/PipelineStepsDataFactory";
import TheBuilderScreen from "./TheBuilderScreen";

const mapStateToProps = (state) => {
  return {
    alertBuilder: state.containerBuildModel?.alertBuilder || {},
    pipelineValidationError: state.containerBuildModel?.pipelineValidationError,
    defaultOptions: state.router?.location?.state,
    pipelineHierarchyRules: state.autoML.pipelineHierarchyRules?.data,
    iterationMetrics: state.pipelines.iterationMetrics || [],
    pipelineExecutionType: state.pipelines?.pipelineExecutionType,
    transforms: state.transforms?.data,
    selectedPipeline: state.pipelines?.selectedPipeline,
    selectedPipelineName: state.pipelines?.selectedPipelineName,
    pipelineData: state.pipelines?.pipelineData?.data || {},
    selectedProjectObj: state.projects?.selectedProject || {},
    navBarIsOpen: state?.common?.values?.navBarIsOpen,

    getQueryData: (queryName) => selectedQueryData(state, queryName),
    getPipelineStepDataClass: (params) => getPipelineStepDataClass({ ...params, state }),
    getPipelineStepDescription: selectPipelineStepDescription,
    selectLabelValuesColors: (labelName) => selectLabelValuesColors(labelName || "Label")(state),
    selectLabelValuesByName: (labelName) => selectLabelValuesByName(labelName || "Label")(state),

    optimizationLogs: state.pipelines.optimizationLogs || [],
    pipelineRunningStatus: state.pipelines.pipelineRunningStatus || "",
    pipelineStatus: state.pipelines?.pipelineStatus.data,

    pipelineResultData: getPipelineResultTableData(state),
    pipelineResults: state.pipelines?.pipelineResults?.data,
    pipelineResultsIsFetching: state.pipelines?.pipelineResults?.isFetching,
    queryCacheStatusData: state.queries?.queryCacheStatus?.data,
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
  setSelectedPipelineName,
  updatePipelineStepsWithQuery,

  launchModelOptimization,
  checkOptimizationStatus,
  clearPipelineExecutionType,

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

export default connect(mapStateToProps, mapDispatchToProps)(TheBuilderScreen);
