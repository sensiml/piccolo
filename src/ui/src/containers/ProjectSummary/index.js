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

import { setIsMainScreenLoading } from "store/common/actions";
import {
  setSelectedProject,
  loadProjectData,
  loadProjectSummaryData,
} from "store/projects/actions";
import { createLabelValue, updateLabelValue, deleteLabelValue } from "store/labels/actions";
import {
  loadMetadata,
  createMetadata,
  updateMetadata,
  deleteMetadata,
  createMetadataValue,
  updateMetadataValue,
  deleteMetadataValue,
} from "store/metadata/actions";

import { selectLabelTableValues, selectDefaultLabelData } from "store/labels/selectors";
import { selectMetadataTableData } from "store/metadata/selectors";

import { connect } from "react-redux";
import ProjectSummary from "./ProjectSummary";

const mapStateToProps = (state) => {
  return {
    projectData: state?.projects?.selectedProject || {},
    defaultLabel: selectDefaultLabelData(state),
    labelValues: selectLabelTableValues()(state),
    labels: state.labels?.data || [],
    metadataData: selectMetadataTableData(state),
    metadataDataIsFetching: state.metadata?.data?.isFetching || false,
    labelsIsFetching: state.labels?.data?.isFetching || false,
  };
};

const mapDispatchToProps = {
  loadProjectData,
  loadProjectSummaryData,
  setIsMainScreenLoading,
  setSelectedProject,
  createLabelValue,
  updateLabelValue,
  deleteLabelValue,
  loadMetadata,
  createMetadata,
  updateMetadata,
  deleteMetadata,
  createMetadataValue,
  updateMetadataValue,
  deleteMetadataValue,
};

export default connect(mapStateToProps, mapDispatchToProps)(ProjectSummary);
