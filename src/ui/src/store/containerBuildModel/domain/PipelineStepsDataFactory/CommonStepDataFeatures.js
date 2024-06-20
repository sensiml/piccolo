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
import { getUniqueId } from "utils";
import { selectPipelineStedDataValues } from "store/containerBuildModel/selectors";
import AbstractStepData from "./AbstractStepData";

class CommonStepDataFeatures extends AbstractStepData {
  IGNORED_KEYS = [];

  constructor({
    state,
    type,
    subtype,
    queryName,
    id,
    selectedSteps,
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

    this.isAddFeatureTransform = isAddFeatureTransform || false;
    this.isAddSensorTransform = isAddSensorTransform || false;
    this.__setQuery(queryName);
  }

  __getSubTypes(transforms) {
    const subTypes = [];
    transforms.forEach((trsf) => {
      if (!subTypes.includes(trsf.subtype)) {
        subTypes.push(trsf.subtype);
      }
    });
    return subTypes;
  }

  __getTransformSet(transforms) {
    return transforms.map((trsf) => {
      // let numColumns = -1;
      const [inputContract, numColumns] = this.__getInputContract(trsf);
      return {
        id: trsf.uuid,
        uuid: trsf.uuid,
        name: trsf.name,
        description: trsf.description,
        type: trsf.type,
        subtype: trsf.subtype,
        inputContract,
        numColumns,
      };
    });
  }

  __getInputContract(transform) {
    const mainArr = [];
    const mergedArr = [];
    let numColumns = -1;

    transform.input_contract.forEach((contrctEl) => {
      if (!this.__isIgronedInputContract(contrctEl)) {
        const options = this.__getInputContractOptions(contrctEl);
        const formFieldType = this.__getInputContractTypeForm(contrctEl, options);
        const defaultValue = this.__getInputContractDefaultValue(contrctEl, formFieldType, options);
        let isFormHidden = this.__isFormHiddenInputContract(contrctEl);

        if (contrctEl?.num_columns > 0) {
          // looking for num_columns > 0
          numColumns = contrctEl?.num_columns;
        }

        // only form element types
        if (Object.values(FORM_TYPES).includes(formFieldType)) {
          if (this.TYPES_WITH_OPTIONS.includes(formFieldType) && !options?.length) {
            isFormHidden = true; // hide selectors withot options for keep empy elements as default
          }
          mainArr.push({
            parent: transform.name,
            name: contrctEl.name,
            description: contrctEl.description,
            type: formFieldType,
            label: this.__getInputContractLabel(contrctEl),
            default: defaultValue,
            range: this.__getInputContractRange(contrctEl),
            minElements: contrctEl.min_elements,
            maxElements: contrctEl.max_elements,
            defaultStep: this.__getInputContractDefaultStep(contrctEl),
            isFormHidden,
            options,
          });
        }
      }
    });

    return [[...mainArr, ...mergedArr], numColumns];
  }

  __getIsFeatureSelected(savedFeature) {
    return savedFeature.isSelected === undefined ? true : savedFeature.isSelected;
  }

  getSavedFeatures(features, addedSubtypes) {
    /**
     * get feature objects with saved params
     */
    const savedFeatures = this.__getSavedPipelineStepData();
    const featureList = [];

    if (savedFeatures?.length) {
      savedFeatures.forEach((savedFeature) => {
        const featureObj = _.find(features, (feature) => feature.name === savedFeature.name);
        const isSelected = this.__getIsFeatureSelected(savedFeature);

        if (!addedSubtypes.includes(featureObj?.subtype) && isSelected) {
          // eslint-disable-next-line no-param-reassign
          addedSubtypes.push(featureObj?.subtype);
        }

        if (!_.isEmpty(featureObj)) {
          featureList.push({
            ...featureObj,
            params: savedFeature?.params,
            localId: getUniqueId(),
            isSelected,
          });
        }
      });
    }

    return featureList;
  }

  getSavedInputsData(transformName, contractName, defaultValue) {
    if (this.savedData[transformName]) {
      const { params } = this.savedData[transformName];
      if (params && params[contractName] !== undefined) {
        return params[contractName];
      }
      return defaultValue;
    }
    return defaultValue;
  }

  getSavedData() {
    const res = selectPipelineStedDataValues(this.state, this.id);
    let resObj = {};
    const featureList = [];

    if (res?.length) {
      resObj = res.reduce((acc, currEl) => {
        acc[currEl.name] = { ...currEl };
        featureList.push(currEl.name);
        return acc;
      }, {});
    }
    this.savedData = resObj;
    return featureList;
  }
}

export default CommonStepDataFeatures;
