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
import { PIPELINE_STEP_TYPES } from "store/autoML/const";
import { selectTransformsByTypeSubType } from "store/transforms/selectors";
import { addPipeline, loadPipelines } from "store/pipelines/actions";
import { loadQueries } from "store/queries/actions";
import { clearPipelinesteps, setLoadingPipelineSteps } from "store/containerBuildModel/actions";
import { loadPipelineTemplates } from "store/pipelineTemplates/actions";
import getPipelineStepDataClass from "store/containerBuildModel/domain/PipelineStepsDataFactory";

import TheSelectScreen from "./TheSelectScreen";

const mapStateToProps = (state) => {
  return {
    selectedProject: state.projects.selectedProject.uuid,
    selectedPipeline: state.pipelines.selectedPipeline,
    isPipelinesFetching: state.pipelines?.pipelineList?.isFetching || false,
    pipleneTemplates: state.pipelineTemplates?.templates?.data || [],
    queries: state.queries.queryList.data || [],
    getPipelineStepDataClass: (params) => getPipelineStepDataClass({ ...params, state }),
    classifiers: selectTransformsByTypeSubType(PIPELINE_STEP_TYPES.CLASSIFIER)(state),
    loadingPipelineSteps: state.containerBuildModel?.loadingPipelineSteps,
  };
};

const mapDispatchToProps = {
  addPipeline,
  loadPipelines,
  loadQueries,
  loadPipelineTemplates,
  clearPipelinesteps,
  setLoadingPipelineSteps,
};

export default connect(mapStateToProps, mapDispatchToProps)(TheSelectScreen);
