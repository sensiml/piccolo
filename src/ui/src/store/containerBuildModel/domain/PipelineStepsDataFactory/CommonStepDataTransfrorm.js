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

import AbstractStepData from "./AbstractStepData";

class CommonStepDataTransfrorm extends AbstractStepData {
  IGNORED_KEYS = [];

  constructor({
    state,
    type,
    subtype,
    id,
    queryName,
    selectedSteps,
    isAfterSegment,
    isAddFeatureTransform,
    isAddSensorTransform,
  }) {
    /* args: state, type, subtype */
    super();
    this.state = state;
    this.type = type;
    this.subtype = subtype;
    this.id = id;
    this.selectedSteps = selectedSteps;
    this.isAfterSegment = isAfterSegment || false;
    this.isAddFeatureTransform = isAddFeatureTransform || false;
    this.isAddSensorTransform = isAddSensorTransform || false;
    this.__setQuery(queryName);
  }

  __getInputContract(transforms) {
    const mainArr = [];
    const mergedArr = [];
    if (!transforms?.length) {
      return [];
    }

    transforms.forEach((transform) => {
      transform.input_contract.forEach((contrctEl) => {
        if (!this.__isIgronedInputContract(contrctEl)) {
          // dynamic options depend on selected query
          const options = this.__getInputContractOptions(contrctEl);
          const formFieldType = this.__getInputContractTypeForm(contrctEl, options);
          const defaultValue = this.__getInputContractDefaultValue(
            contrctEl,
            formFieldType,
            options,
          );

          let isFormHidden = this.__isFormHiddenInputContract(contrctEl);
          // only form element types
          if (Object.values(FORM_TYPES).includes(formFieldType)) {
            if (this.TYPES_WITH_OPTIONS.includes(formFieldType) && !options?.length) {
              // hide selectors without options for keep empy elements as default
              isFormHidden = true;
            }

            if (this.__isInputContractHasUseParam(contrctEl)) {
              const defaultValueIsUseParam = this.getSavedInputsData(
                this.constructor.getIsUseParamName(contrctEl.name),
                contrctEl.name,
              );
              const defaultParentValue = this.getSavedInputsData(contrctEl.name, transform.name);
              const data = {
                parent: transform.name,
                name: this.constructor.getIsUseParamName(contrctEl.name),
                description: contrctEl.description,
                type: FORM_TYPES.FORM_BOOLEAN_TYPE,
                label: `Use ${this.__getInputContractLabel(contrctEl)}`,
                // show use param if parent value is not undefined
                default: !_.isUndefined(defaultValueIsUseParam)
                  ? defaultValueIsUseParam
                  : !_.isUndefined(defaultParentValue),
                isServiceField: true,
              };
              mainArr.push(data);
            }

            mainArr.push({
              parent: transform.name,
              name: contrctEl.name,
              description: contrctEl.description,
              type: formFieldType,
              label: this.__getInputContractLabel(contrctEl),
              default: this.getSavedInputsData(
                contrctEl.name,
                transform.name,
                defaultValue,
                isFormHidden,
                options,
              ),
              range: this.__getInputContractRange(contrctEl),
              minElements: contrctEl.min_elements,
              maxElements: contrctEl.max_elements,
              defaultStep: this.__getInputContractDefaultStep(contrctEl),
              isFormHidden,
              options,
              ...(this.__isInputContractHasUseParam(contrctEl) && {
                isUseName: this.constructor.getIsUseParamName(contrctEl.name),
              }),
            });
          }
        }
      });
    });

    return [...mainArr, ...mergedArr];
  }

  getSavedInputsData(name, parent, defaultValue, isFormHidden, options) {
    if (isFormHidden) {
      return defaultValue;
    }
    const defaultStepDataValues = this.__getSavedPipelineStepData();
    if (_.isArray(defaultStepDataValues) && !_.isEmpty(defaultStepDataValues)) {
      const dataObj = defaultStepDataValues.find((el) => el.transform === parent);
      return dataObj ? dataObj[name] : null;
    }
    if (defaultStepDataValues && !_.isUndefined(defaultStepDataValues[name])) {
      // if default values is list and has options values shoud be in the options
      if (_.isArray(defaultStepDataValues[name])) {
        const optionValues = _.map(options, (option) => option.value);
        if (!_.isEmpty(optionValues)) {
          return defaultStepDataValues[name].filter((el) => optionValues.includes(el));
        }
        return defaultStepDataValues[name];
      }
      return defaultStepDataValues[name];
    }
    return defaultValue;
  }
}

export default CommonStepDataTransfrorm;
