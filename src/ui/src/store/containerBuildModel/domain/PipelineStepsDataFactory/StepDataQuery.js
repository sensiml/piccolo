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
import { FORM_TYPES } from "consts";

import { selectPipelineStedDataValues } from "store/containerBuildModel/selectors";
import { selectedSessionName } from "store/sessions/selectors";

import AbstractStepData from "./AbstractStepData";

class StepDataQuery extends AbstractStepData {
  constructor({ state, type, subtype, id, isAutoML }) {
    super();
    this.state = state;
    this.type = type;
    this.subtype = subtype;
    this.id = id;
    this.isAutoML = isAutoML;
  }

  __getDefault(name, defaultValue) {
    const savedValue = this.getSavedInputsData(name);
    if (savedValue === undefined) {
      return defaultValue;
    }
    return savedValue;
  }

  getInputsData() {
    const descriptionParameters = _.map(this.state.queries?.queryList?.data, (el) => ({
      name: el.name,
      label_column: el.label_column,
      columns: el.columns,
      metadata_columns: el.metadata_columns,
      session: selectedSessionName(el.segmenter_id)(this.state),
      // cacheStatus: el.task_status, // TODO: return cache status
    }));
    return [
      { descriptionParameters },
      {
        options:
          _.map(this.state.queries?.queryList?.data, (el) => {
            return {
              name: el.name,
              value: el.name,
            };
          }) || [],
        name: "name",
        label: "Query",
        type: FORM_TYPES.FORM_SELECT_TYPE,
        default: this.getSavedInputsData("name"),
      },
      {
        name: "use_session_preprocessor",
        label: "Use session preprocessor",
        type: FORM_TYPES.FORM_BOOLEAN_TYPE,
        isFormHidden: this.isAutoML,
        default: this.__getDefault("use_session_preprocessor", true),
      },
    ];
  }

  getSavedInputsData(name) {
    const res = selectPipelineStedDataValues(this.state, this.id);
    return res[name];
  }

  getOutputData() {
    // console.log("getDefaultInputsData");
  }
}

export default StepDataQuery;
