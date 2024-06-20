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
import { addOrUpdateQuery } from "store/queries/actions";
import { setHasUnsavedChanges } from "store/common/actions";

import TheQueryCreateScreen from "./TheQueryCreateScreen";

const mapStateToProps = (state) => {
  return {
    selectedProject: state.projects.selectedProject.uuid,
    queries: state.queries.queryList.data || [],
    sessions: state.sessions.data,
    labels: state.labels.data,
    metadata: state.metadata.data,
    sources: state.sources.data,
    hasUnsavedChanges: state.common?.values?.hasUnsavedChanges || false,
  };
};

const mapDispatchToProps = {
  addOrUpdateQuery,
  setHasUnsavedChanges,
};

export default connect(mapStateToProps, mapDispatchToProps)(TheQueryCreateScreen);
