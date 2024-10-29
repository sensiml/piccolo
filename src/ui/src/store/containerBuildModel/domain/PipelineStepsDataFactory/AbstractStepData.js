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
import { FORM_TYPES, NUMERIC_ARR } from "consts";
import {
  selectPipelineSteps,
  selectPipelineStedDataValues,
} from "store/containerBuildModel/selectors";
import { PIPELINE_STEP_TYPES, TRANSFORM_TYPES } from "store/autoML/const";
import { getSelectedPipeline } from "store/pipelines/selectors";

import inputContractOptionsMixin from "./inputContractOptionsMixin";
/**
 * @class StepData
 */
class AbstractStepData {
  TYPES_WITH_OPTIONS = [FORM_TYPES.FORM_SELECT_TYPE, FORM_TYPES.FORM_MULTI_SELECT_TYPE];

  constructor() {
    if (this.constructor === AbstractStepData) {
      throw new TypeError("Can not construct abstract class.");
    }
    if (this.getInputsData === AbstractStepData.prototype.getInputsData) {
      throw new TypeError("Please implement abstract method getInputsData.");
    }
    if (this.getOutputData === AbstractStepData.prototype.getInputsData) {
      throw new TypeError("Please implement abstract method getOutputData.");
    }
  }

  __setQuery(queryName) {
    if (queryName) {
      this.queryName = queryName;
    } else {
      const selectedPipeline = getSelectedPipeline(this.state);
      const pipelineStepData = this.state.containerBuildModel?.pipelineStepData[selectedPipeline];
      if (pipelineStepData?.length) {
        // we can have QUERY or INPUT_DATA as selectedQuery
        this.queryName = pipelineStepData.find((step) => {
          return [PIPELINE_STEP_TYPES.QUERY, PIPELINE_STEP_TYPES.INPUT_DATA].includes(step.type);
        })?.data?.name;
      }
    }
  }

  __getSavedPipelineStepData() {
    if (!_.isEmpty(this.selectedSteps)) {
      return this.selectedSteps.find((step) => step.id === this.id)?.data;
    }
    return selectPipelineStedDataValues(this.state, this.id);
  }

  getInputsData() {
    // data to build dynamic form
    this.validateStaticMethod("getInputsData");
  }

  getOutputData() {
    // transform output data to request
    this.validateStaticMethod("getOutputData");
  }

  __isInputContractHasUseParam(contrctEl) {
    return this.isHasUseParam(contrctEl?.name);
  }

  __isIgronedInputContract(contrctEl) {
    return this.isIgrored(contrctEl.name);
  }

  __isFormHiddenInputContract(contrctEl) {
    return this.isHiddenFormEl(contrctEl.name) || contrctEl.no_display;
  }

  __getDefaultUseParam(contrctEl) {
    return this.getDefaultUseParam(contrctEl.name);
  }

  // eslint-disable-next-line class-methods-use-this
  __getInputContractRange(contrctEl) {
    return contrctEl?.range;
  }

  // eslint-disable-next-line consistent-return
  __getInputContractDefaultValue(contrctEl, formFieldType, options) {
    if (this.isAdditionalyDefaultLookup(contrctEl.name)) {
      const dynamicDefaultValue = this.getDynamicDefaultValue(contrctEl.name);
      if (!_.isUndefined(dynamicDefaultValue)) {
        return dynamicDefaultValue;
      }
    }

    if (_.isArray(contrctEl?.default) && contrctEl?.default?.length) {
      return contrctEl?.default;
    }

    if (!_.isArray(contrctEl?.default)) {
      if (
        !_.isEmpty(contrctEl?.default) &&
        !_.isNull(contrctEl?.default) &&
        !_.isUndefined(contrctEl?.default)
      ) {
        return contrctEl?.default;
      }
    }

    if (formFieldType === FORM_TYPES.FORM_SELECT_TYPE) {
      // .find(option => option.isDefault)
      if (options?.length) {
        const defaultObj = options[0] || {};
        return defaultObj?.value || defaultObj?.name || "";
      }
    }
    if (formFieldType === FORM_TYPES.FORM_MULTI_SELECT_TYPE) {
      // filter(option => option.isDefault)
      return _.map(options, (option) => option?.value) || [];
    }
    if (NUMERIC_ARR.includes(formFieldType)) {
      return contrctEl?.default || 0;
    }
    return contrctEl?.default;
  }

  __getIsAnySessionSteps() {
    /**
     * check if any of steps are extracted from session
     */
    const pipelineSteps = selectPipelineSteps(this.state);
    if (pipelineSteps?.length) {
      return Boolean(pipelineSteps.filter((step) => step?.options?.isSession)?.length);
    }
    return false;
  }

  __getIsSegmenterFromSession() {
    /**
     * check if segmenter is extracted from session
     */
    const pipelineSteps = selectPipelineSteps(this.state);
    if (pipelineSteps?.length) {
      return Boolean(pipelineSteps.indexOf((step) => step?.options?.isSessionSegmenter) !== -1);
    }
    return false;
  }

  __getIsAfterSegmenter() {
    const pipelineSteps = selectPipelineSteps(this.state);
    const currentIndex = pipelineSteps.findIndex((step) => step.id === this.id);
    const segmentIndex = pipelineSteps.findIndex(
      (step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER,
    );
    if (segmentIndex !== -1) {
      return currentIndex > segmentIndex;
    }
    return false;
  }

  __getIsAfterFeatureTransform() {
    /**
     * ckeck if current step located after feature transform
     */
    const pipelineSteps = selectPipelineSteps(this.state);
    const currentIndex = pipelineSteps.findIndex((step) => step.id === this.id);
    const featureTransormIndex = pipelineSteps.findIndex(
      (step) => step.name === TRANSFORM_TYPES.FEATURE_TRANSFORM,
    );
    if (featureTransormIndex !== -1) {
      return currentIndex > featureTransormIndex || this.isAddFeatureTransform;
    }
    return this.isAddFeatureTransform;
  }

  __getIsAfterSensorTransforms() {
    /**
     * ckeck if current step located after sensor transform
     */
    const pipelineSteps = selectPipelineSteps(this.state);
    const currentIndex = pipelineSteps.findIndex((step) => step.id === this.id);
    const featureTransormIndex = pipelineSteps.findIndex(
      (step) => step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM,
    );
    if (featureTransormIndex !== -1) {
      return currentIndex > featureTransormIndex || this.isAddFeatureTransform;
    }
    return this.isAddSensorTransform;
  }

  __getSensorTransformNames() {
    /**
     * find all transforms above currentstep
     */
    const pipelineSteps = selectPipelineSteps(this.state);
    const currentIndex = pipelineSteps.findIndex((step) => step.id === this.id);
    const featureTransorms = pipelineSteps.filter(
      (step, ftIndex) => step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM && currentIndex > ftIndex,
    );
    return featureTransorms.map((step) => step.customName);
  }

  __getIsAddSegmentId() {
    return this.__getIsAfterSegmenter() || this.isAfterSegment;
  }

  // eslint-disable-next-line consistent-return
  __getInputContractOptions(contrctEl) {
    /**
     * @returns {Array} options
     */
    const buildResult = (options) => {
      return options;
    };

    if (contrctEl?.options?.length) {
      const options = _.map(contrctEl?.options, (el) => {
        if (el.name) {
          return { name: el.name, value: el.name };
        }
        return { name: el, value: el };
      });
      if (contrctEl.default && contrctEl.type === "str") {
        // some contract have default values out of options
        if (options.findIndex((el) => el.value === contrctEl.default) === -1) {
          return _.union(options, [{ name: contrctEl.default, value: contrctEl.default }]);
        }
      }
      return options;
    }
    const dynamicOptions = this.getDynamicOptions(
      contrctEl?.name,
      this.__getIsAddSegmentId(),
      this.__getIsAfterFeatureTransform(),
      this.__getSensorTransformNames(),
    );
    if (dynamicOptions?.length) {
      return buildResult(dynamicOptions);
    }
  }

  // eslint-disable-next-line class-methods-use-this
  __getInputContractLabel(contractEl) {
    return (
      contractEl.display_name ||
      (contractEl?.name || "")
        .split("_")
        .map((el) => _.capitalize(el))
        .join(" ")
    );
  }

  // eslint-disable-next-line class-methods-use-this
  __getInputContractDefaultStep(contrctEl) {
    if (
      [
        FORM_TYPES.FORM_INT_TYPE,
        FORM_TYPES.FORM_INT_16T_TYPE,
        FORM_TYPES.FORM_NUMERIC_TYPE,
      ].includes(contrctEl?.type)
    ) {
      return 1;
    }
    if (FORM_TYPES.FORM_FLOAT_TYPE === contrctEl?.type) {
      return 0.1;
    }
    return 1;
  }

  __getInputContractTypeForm(contrctEl, options) {
    if (contrctEl.type === "dict" && options) {
      return `${contrctEl.type}_${contrctEl.element_type || "list"}`;
    }
    if (contrctEl.type === "dict") {
      return `${contrctEl.type}_editable_${contrctEl.element_type || "list"}`;
    }
    if (contrctEl.type === "list" && !options) {
      return `editable_list_${contrctEl.element_type || "str"}`;
    }
    if (contrctEl.range) {
      return `range_${contrctEl.type}`;
    }
    if (contrctEl.type === "str" && options?.length) {
      return "select";
    }
    if (contrctEl.type === "str" && this.isAdditionalyLookup(contrctEl.name)) {
      return "select";
    }
    return contrctEl.type;
  }

  // eslint-disable-next-line class-methods-use-this
  getCardParams() {
    return [];
  }

  get queryColumns() {
    const res = this.selectSelectedQueryColumns(
      this.state,
      this.queryName,
      this.__getSensorTransformNames(),
    );
    return res;
  }

  static getIsUseParamName(name) {
    return `is_use_${name}`;
  }

  static validateStaticMethod(methodName) {
    if (this === AbstractStepData) {
      throw new TypeError(`Can't call static abstract method ${methodName}`);
    } else {
      throw new Error(`method ${methodName} must be implemented`);
    }
  }
}

Object.assign(AbstractStepData.prototype, inputContractOptionsMixin);

export default AbstractStepData;
