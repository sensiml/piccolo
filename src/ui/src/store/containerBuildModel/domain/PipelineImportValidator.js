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

/* eslint-disable camelcase */
/* eslint-disable no-unused-expressions */
import _ from "lodash";
import { STEP_TYPES } from "store/pipelines/const";

import inputContractAdditionalOptions, {
  constContracts,
} from "./PipelineStepsDataFactory/inputContractAdditionalOptions";

class PipelineImportValidator {
  constructor(pipeline = []) {
    this.pipeline = pipeline;
    this.queryName;
    this.isUseSessionPreprocessor = false;
    this.sensorColumns = [];
    this.metadataColumns = [];
    this.labelColum = "";
    this.labelValues = [];
    this.validationErrors = [];
    this.numberOfSteps = 0;
  }

  get isValidPipeline() {
    return _.isEmpty(this.validationErrors);
  }

  get validationErrorMessage() {
    return this.validationErrors.join(", ");
  }

  get queryInputData() {
    return {
      sensorColumns: this.sensorColumns,
      metadataColumns: this.metadataColumns,
      labelColum: this.labelColum,
      labelValues: this.labelValues,
      numberOfSteps: this.numberOfSteps,
      queryName: this.queryName,
      isUseSessionPreprocessor: this.isUseSessionPreprocessor,
    };
  }

  get queryInputDataParamsToReview() {
    return {
      sensorColumns: this.sensorColumns,
      metadataColumns: this.metadataColumns,
      numberOfSteps: this.numberOfSteps,
    };
  }

  __getInputsByLookup(lookupKey) {
    return _.entries(inputContractAdditionalOptions)
      .filter(([_key, val]) => val.lookup === lookupKey)
      .map(([key, _val]) => key);
  }

  __getInputsByLookups(inputs, itemsLookup = []) {
    //
    return _.entries(inputs).reduce((acc, [key, val]) => {
      let updatedAcc = [...acc];

      if (itemsLookup.includes(key) && !_.isEmpty(val)) {
        updatedAcc = _.union(acc, val);
      }

      return updatedAcc;
    }, []);
  }

  __extractQueryParams() {
    const queryStep = _.find(this.pipeline, (pplItem) => pplItem.type === STEP_TYPES.QUERY);
    this.isUseSessionPreprocessor = !_.isUndefined(queryStep?.use_session_preprocessor)
      ? queryStep?.use_session_preprocessor
      : true;
    this.queryName = queryStep?.name;
  }

  __extractSensorColumns(inputs = {}) {
    const sensorColumnLookups = this.__getInputsByLookup(constContracts.QUERY_COLUMNS);
    const sensorColumns = this.__getInputsByLookups(inputs, sensorColumnLookups);

    if (!_.isEmpty(sensorColumns)) {
      this.sensorColumns = _.union(
        this.sensorColumns,
        sensorColumns.filter((column) => !column.includes("ST")),
      );
    }
  }

  __extractMetadataColumns(inputs = {}) {
    const metadataColumnsLookup = this.__getInputsByLookup(constContracts.QUERY_METADATA_COLUMNS);
    const metadataColumns = this.__getInputsByLookups(inputs, metadataColumnsLookup);

    if (!_.isEmpty(metadataColumns)) {
      this.metadataColumns = _.union(this.metadataColumns, metadataColumns);
    }
  }

  __extractLabelsValues(inputs = {}) {
    const labelValuesLookup = this.__getInputsByLookup(constContracts.FILTERING_LABEL_VALUES);
    const labelValues = this.__getInputsByLookups(inputs, labelValuesLookup);

    if (!_.isEmpty(labelValues)) {
      this.labelValues = _.union(this.labelValues, labelValues);
    }
  }

  __extractLabeColumn(inputs = {}) {
    const labelValuesLookup = this.__getInputsByLookup(constContracts.QUERY_LABEL_COLUMN);

    if (!this.labelColum) {
      _.entries(inputs).forEach(([key, val]) => {
        if (labelValuesLookup.includes(key) && val) {
          this.labelColum = val;
        }
      });
    }
  }

  validatePipeline() {
    //
  }

  extractQueryInputData() {
    if (_.isArray(this.pipeline)) {
      this.__extractQueryParams();
      this.pipeline.forEach((pplItem) => {
        this.numberOfSteps += 1;
        if (!_.isEmpty(pplItem?.inputs)) {
          this.__extractSensorColumns(pplItem?.inputs);
          this.__extractMetadataColumns(pplItem?.inputs);
          this.__extractLabelsValues(pplItem?.inputs);
          this.__extractLabeColumn(pplItem?.inputs);
        }
        if (_.isArray(pplItem?.set) && !_.isEmpty(pplItem?.set)) {
          pplItem?.set.forEach((setEl) => {
            this.__extractSensorColumns(setEl?.inputs);
            this.__extractMetadataColumns(pplItem?.inputs);
            this.__extractLabelsValues(pplItem?.inputs);
            this.__extractLabeColumn(pplItem?.inputs);
          });
        }
      });
    }
    return this.queryInputData;
  }
}

export default PipelineImportValidator;
