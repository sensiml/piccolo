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
import { loadModels } from "store/models/actions";
import { loadKnowledgepacks } from "store/knowledgepacks/actions";
import { deletePipeline, loadPipelines, exportPipeline } from "store/pipelines/actions";
import PipelinesTable from "./PipelinesTable";

const mapStateToProps = (state) => {
  return {
    selectedProject: state.projects.selectedProject.uuid,
    pipelines: state.pipelines.pipelineList,
    knowledgepacks: state.knowledgepacks,
  };
};

const mapDispatchToProps = {
  loadModels,
  loadKnowledgepacks,
  deletePipeline,
  loadPipelines,
  exportPipeline,
};

export default connect(mapStateToProps, mapDispatchToProps)(PipelinesTable);
