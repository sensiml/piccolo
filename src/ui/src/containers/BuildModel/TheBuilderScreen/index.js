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
  setIsAdvancedBuilding,
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
} from "store/pipelines/actions";

import {
  loadQueryCacheStatus,
  clearQueryCacheStatus,
  buildQueryCache,
  loadQueryStatistic,
  loadQuerySegmentStatistic,
} from "store/queries/actions";

import {
  selectPipelineSteps,
  selectedQueryData,
  selectAutoMLParams,
} from "store/containerBuildModel/selectors";
import { selectPipelineStepDescription } from "store/autoML/selectors";

import { getPipelineResultTableData } from "store/pipelines/selectors/";

import { selectLabelValuesColors } from "store/labels/selectors";

import getPipelineStepDataClass from "store/containerBuildModel/domain/PipelineStepsDataFactory";
import TheBuilderScreen from "./TheBuilderScreen";

const mapStateToProps = (state) => {
  return {
    alertBuilder: state.containerBuildModel?.alertBuilder || {},
    pipelineValidationError: state.containerBuildModel?.pipelineValidationError,
    isAdvancedBuilding: state.containerBuildModel?.isAdvancedBuilding || false,
    defaultOptions: state.router?.location?.state,
    pipelineHierarchyRules: state.autoML.pipelineHierarchyRules?.data,
    transforms: state.transforms?.data,
    pipelines: state.pipelines.pipelineList.data,
    selectedPipeline: state.pipelines?.selectedPipeline,
    pipelineData: state.pipelines?.pipelineData?.data || {},
    selectedProjectObj: state.projects?.selectedProject || {},
    selectedSteps: selectPipelineSteps(state),
    autoMLParams: selectAutoMLParams(state),
    navBarIsOpen: state?.common?.values?.navBarIsOpen,
    labelColors: selectLabelValuesColors("Label")(state),
    getQueryData: (queryName) => selectedQueryData(state, queryName),
    getPipelineStepDataClass: (params) => getPipelineStepDataClass({ ...params, state }),
    getPipelineStepDescription: selectPipelineStepDescription,

    iterationMetrics: state.pipelines.iterationMetrics || [],
    optimizationLogs: state.pipelines.optimizationLogs || [],
    pipelineRunningStatus: state.pipelines.pipelineRunningStatus || "",
    pipelineStatus: state.pipelines?.pipelineStatus.data,
    pipelineResultData: getPipelineResultTableData(state),
    queryList: state.queries?.queryList?.data || [],
    queryCacheStatusData: state.queries?.queryCacheStatus?.data,
  };
};

const mapDispatchToProps = {
  clearAlertBuilder,
  clearPipelineValidationError,

  setIsAdvancedBuilding,
  setPipelineStep,
  setPipelineDefaultSteps,
  updatePipelineStepsWithQuery,
  loadPipelinesHierarchyRules,

  checkOptimizationStatus,
  loadPipelineBuilderData,
  loadDataAfterTraining,
  clearOptimizationLogs,

  clearPipelineResults,
  clearPipelineStatus,
  launchModelOptimization,
  stopModelOptimization,
  loadPipelineResults,
  loadQueryCacheStatus,
  buildQueryCache,
  clearQueryCacheStatus,
  loadQueryStatistic,
  loadQuerySegmentStatistic,
  clearPipeline,
  downloadPipelineStepCache,
  loadPipeline,
  setSelectedPipeline,
  exportPipeline,
};

export default connect(mapStateToProps, mapDispatchToProps)(TheBuilderScreen);
