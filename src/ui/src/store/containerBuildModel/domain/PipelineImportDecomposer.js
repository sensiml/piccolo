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

import _, { isArray } from "lodash";

import i18n from "i18n";
import { selectFirstQuery } from "store/queries/selectors";
import { PIPELINE_STEP_TYPES, TRANSFORM_TYPES, AUTOML_PARAMS_NAME } from "store/autoML/const";
// import { getTransformByName } from "store/transforms/selectors";

import PipelineDataDecomposer from "./PipelineDataDecomposer";
import inputContractOptionsMixin from "./PipelineStepsDataFactory/inputContractOptionsMixin";

Object.assign(PipelineDataDecomposer.prototype, inputContractOptionsMixin);

class PipelineImportDecomposer extends PipelineDataDecomposer {
  constructor(state, pipelineData, queryName, defaultOptions = {}) {
    super(state, pipelineData);
    this.state = state;
    this.pipelineSteps = [];
    this.queryName = queryName;

    this.name = "";
    this.reviewedStepsParams = [];

    this.isAutoMLOptimization = defaultOptions?.isAutoMLOptimization;
    this.selectedClassifier = defaultOptions?.selectedClassifier;
    this.replacedColumns = defaultOptions?.replacedColumns || {};
    this.isUseSessionPreprocessor = !_.isUndefined(defaultOptions.isUseSessionPreprocessor)
      ? defaultOptions.isUseSessionPreprocessor
      : true;
    this.prevTransform = "";
    this.isAddSegmentId = false;
    this.isAddFeatureTransform = false;
  }

  __getParamsWithReplacement = (paramName, paramVal) => {
    /**
     * replace params according replaced params
     * in case when some columns are not in replacedColumns
     *  - leave static params
     *  - only transform should be added ({name}_ST_000{index})
     */
    let replacedParams;
    if (!this.isAdditionalyLookup(paramName)) {
      return paramVal;
    }
    if (this.isAdditionalyDefaultLookup(paramName)) {
      return paramVal;
    }
    if (_.isEmpty(this.replacedColumns) && this.isQueryColumnsLookup(paramName)) {
      return paramVal;
    }
    if (_.isArray(paramVal) && this.isQueryColumnsLookup(paramName)) {
      replacedParams = paramVal.reduce((acc, param) => {
        if (this.replacedColumns[param]) {
          acc.push(this.replacedColumns[param]);
        } else if (param.includes("ST")) {
          acc.push(param);
        }
        return acc;
      }, []);
    } else if (this.replacedColumns[paramVal] && this.isQueryColumnsLookup(paramName)) {
      replacedParams = this.replacedColumns[paramVal];
    }
    return replacedParams;
  };

  __getDefaultLookupValue = (name, paramVal, inputContract = {}) => {
    if (this.isAdditionalyLookup(name) || this.isAdditionalyDefaultLookup(name)) {
      const defaultValue = this.getDynamicDefaultValue(name);

      if (!_.isUndefined(defaultValue)) {
        return defaultValue;
      }
      const options =
        this.getDynamicOptions(name, this.isAddSegmentId, this.isAddFeatureTransform) || [];
      if (inputContract.type === "list") {
        return options.map((el) => el.value);
      }
      if (inputContract.type === "dict") {
        return { "": options.map((el) => el.value) };
      }
      if (!_.isEmpty(options)) {
        return options[0]?.value;
      }
    }
    return paramVal;
  };

  __getUpdatedOptions = (customName, paramName, isDefaultDynamicValue = false, options = {}) => {
    if (isArray(options.reviewed_steps_params) && !_.isEmpty(options.reviewed_steps_params)) {
      this.reviewedStepsParams = _.union(this.reviewedStepsParams, options.reviewed_steps_params);
    }
    if (
      this.isMetadataLabels(paramName) ||
      (this.isAdditionalyDefaultLookup(paramName) && isDefaultDynamicValue)
    ) {
      const paramNameLabel = paramName
        .split("_")
        .map((el) => _.capitalize(el))
        .join(" ");

      this.reviewedStepsParams = _.union(this.reviewedStepsParams, [
        `Step: ${customName}`,
        `Parameter: ${paramNameLabel}`,
      ]);

      return {
        ...options,
        is_should_be_reviewed: true,
        message: i18n.t("pipelines:form-import.alert-waring-select-metadata-params", {
          paramNameLabel,
        }),
      };
    }
    return options;
  };

  __setTransformStep(name, customName, data, options = {}) {
    /**
     * set transforms steps with replacing dynamic fields like group_columns, sample_rate
     */
    // eslint-disable-next-line camelcase
    const { input_contract: inputContracts = [] } = this.__getTransform(customName) || {};
    let updatedOptions = { ...options };

    const updatedData = _.entries(data).reduce((acc, [paramName, paramVal]) => {
      const inputContract = inputContracts.find((el) => el.name === paramName);
      const allowedParams = ["is_use_feature_min_max_defaults"];
      let isDefaultDynamicValue = false;

      if (inputContract || allowedParams.includes(paramName) || paramName === "transform") {
        acc[paramName] = this.__getParamsWithReplacement(paramName, paramVal);
        if (!acc[paramName]) {
          isDefaultDynamicValue = true;
          acc[paramName] = this.__getDefaultLookupValue(paramName, paramVal, inputContract);
        }
        updatedOptions = this.__getUpdatedOptions(
          customName,
          paramName,
          isDefaultDynamicValue,
          updatedOptions,
        );
      }
      return acc;
    }, {});

    super.__setPipelineStep(name, customName, updatedData, updatedOptions);
  }

  __setPipelineStepWithSet(name, customName, data = [], options) {
    /**
     * set feature generators or feature selectors steps
     * with replacing dynamic fields like group_columns, sample_rate
     */
    const updatedData = _.reduce(
      data,
      (acc, features) => {
        const { input_contract: inputContracts = [] } = this.__getTransform(features.name) || {};
        let params = features.params || {};
        let isHasEmptyColumns = false; // don't add features withot sensor columns

        if (!_.isEmpty(inputContracts)) {
          // eslint-disable-next-line camelcase
          params = _.entries(params).reduce((paramsAcc, [paramName, paramVal]) => {
            const inputContract = inputContracts.find((el) => el.name === paramName);
            if (inputContract) {
              paramsAcc[paramName] =
                this.__getParamsWithReplacement(paramName, paramVal) ||
                this.__getDefaultLookupValue(name);
              if (this.isQueryColumnsLookup(paramName) && _.isEmpty(paramsAcc[paramName])) {
                isHasEmptyColumns = true;
              }
            }
            return paramsAcc;
          }, {});
        }
        if (!isHasEmptyColumns) {
          acc.push({ name: features.name, params });
        }
        return acc;
      },
      [],
    );
    super.__setPipelineStep(name, customName, updatedData, options);
  }

  __parseQueryStepData() {
    // set new query data from contructor or first from state insate from pipeline
    const queryStepIndex = this.decomposedSteps.findIndex(
      (step) => step.name === PIPELINE_STEP_TYPES.QUERY,
    );
    if (queryStepIndex !== -1 && this.decomposedSteps[queryStepIndex]) {
      this.decomposedSteps[queryStepIndex].data = {
        name: this.queryName,
        use_session_preprocessor: this.isUseSessionPreprocessor,
      };
      return;
    }
    if (!this.queryName) {
      const query = selectFirstQuery(this.state);
      this.queryName = query.name;
    }
    super.__parseQueryStepData({
      name: this.queryName,
      use_session_preprocessor: this.isUseSessionPreprocessor,
    });
  }

  __setPipelineStep(name, customName, data, options) {
    if (name === PIPELINE_STEP_TYPES.SEGMENTER) {
      this.isAddSegmentId = true;
    }
    if (name === TRANSFORM_TYPES.FEATURE_TRANSFORM) {
      this.isAddFeatureTransform = true;
    }

    if (PIPELINE_STEP_TYPES.FEATURE_GENERATOR === name) {
      this.__setPipelineStepWithSet(name, customName, data, options);
    } else if (PIPELINE_STEP_TYPES.FEATURE_SELECTOR === name) {
      this.__setPipelineStepWithSet(name, customName, data, options);
    } else if (PIPELINE_STEP_TYPES.AUGMENTATION === name) {
      this.__setPipelineStepWithSet(name, customName, data, options);
    } else if (AUTOML_PARAMS_NAME === name) {
      super.__setPipelineStep(name, customName, data, options);
    } else if (PIPELINE_STEP_TYPES.QUERY === name) {
      super.__setPipelineStep(name, customName, data, options);
    } else {
      this.__setTransformStep(name, customName, data, options);
    }
  }

  getPipelineStepData() {
    if (!this.pipelineList?.length) {
      return [];
    }
    // super.__extractAutoMLParams();
    this.__parseQueryStepData();
    super.__parsePipelineList();
    return this.decomposedSteps;
  }

  getAutoMLStep() {
    return super.getAutoMLStep();
  }
}

export default PipelineImportDecomposer;
