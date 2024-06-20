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

import { FORM_TYPES } from "consts";
import { PIPELINE_STEP_TYPES, DISABLED_TRAINING_ALGO } from "store/autoML/const";
import { selectTransformsByTypeSubType, getTransformByName } from "store/transforms/selectors";
import {
  selectPipelineSteps,
  selectPipelineStedDataValues,
} from "store/containerBuildModel/selectors";

import CommonStepDataTransfrorm from "./CommonStepDataTransfrorm";

class StepDataTvo extends CommonStepDataTransfrorm {
  INPUT_DATA_KEY = "input_data";

  INPUT_CLASSIFIERS = "classifiers";

  INPUT_VALIDATION_METHODS = "validation_methods";

  constructor({ state, type, subtype, id, queryName, isAutoML }) {
    /* args: state, type, subtype */
    super({ state, type, subtype, id, queryName });
    this.isAutoML = isAutoML;
  }

  __isIgronedInputContract(contrctEl) {
    const isIgnored = super.__isIgronedInputContract(contrctEl);
    return isIgnored || Boolean(contrctEl?.handle_by_set);
  }

  __getInputContractFilterName() {
    if (this.type === PIPELINE_STEP_TYPES.TRAINING_ALGORITHM) {
      return this.INPUT_CLASSIFIERS;
    }
    if (this.type === PIPELINE_STEP_TYPES.VALIDATION) {
      return this.INPUT_VALIDATION_METHODS;
    }
    return this.INPUT_CLASSIFIERS;
  }

  filterTranformsByClassifier(transforms, classifierTranform) {
    // TODO HARDCODE DISABLED_TRAINING_ALGO !!!!!
    return transforms
      .filter((trsf) => !DISABLED_TRAINING_ALGO.includes(trsf.name))
      .filter((trsf) => {
        // eslint-disable-next-line camelcase
        const { input_contract } = trsf;
        if (input_contract?.length) {
          const contract = input_contract.find(
            (contr) => contr.name === this.__getInputContractFilterName(),
          );
          if (contract?.options) {
            return Boolean(contract.options.find((option) => option?.name === classifierTranform));
          }
        }
        return false;
      });
  }

  filterTranformsByOptimizer(transforms, optimizerTranform) {
    // eslint-disable-next-line camelcase
    const { input_contract } = getTransformByName(optimizerTranform)(this.state) || {};

    return transforms.filter((trsf) => {
      if (input_contract?.length) {
        const contract = input_contract.find(
          (contr) => contr.name === this.__getInputContractFilterName(),
        );
        if (contract?.options) {
          return Boolean(contract.options.find((option) => option?.name === trsf.name));
        }
      }
      return false;
    });
  }

  getTransforms({ transformList, excludeTransform, exactTransform, prevStepTransform }) {
    const transforms = selectTransformsByTypeSubType(
      this.type,
      this.subtype,
      transformList,
      excludeTransform,
    )(this.state);

    if (exactTransform) {
      return transforms.filter((trsn) => trsn.name === exactTransform);
    }
    // && !this.isAutoML - was disabled for AutoML
    if (this.type === PIPELINE_STEP_TYPES.TRAINING_ALGORITHM) {
      return this.filterTranformsByClassifier(transforms, prevStepTransform) || [];
    }
    if (this.type === PIPELINE_STEP_TYPES.VALIDATION) {
      return this.filterTranformsByOptimizer(transforms, prevStepTransform) || [];
    }
    return transforms;
  }

  getInputsData({ transformList, excludeTransform, exactTransform, prevTransform }) {
    let prevStepTransform = prevTransform;
    if (!prevStepTransform) {
      const selectedPipelineSteps = selectPipelineSteps(this.state);
      const currentIndex = selectedPipelineSteps.findIndex((step) => step.id === this.id);
      const prevStep = selectedPipelineSteps[currentIndex - 1];
      prevStepTransform = prevStep?.data?.transform || "";
    }

    const transforms = this.getTransforms({
      transformList,
      excludeTransform,
      exactTransform,
      prevStepTransform,
    });

    return {
      name: "transform",
      type: FORM_TYPES.FORM_SELECT_TYPE,
      label: `${transforms[0]?.type}`,
      default: this.getSavedTransformOption("transform"),
      options: transforms.map((el) => ({
        uuid: el.uuid,
        name: el.name,
        description: el.description,
        value: el.name,
      })),
      fieldset: this.__getInputContract(transforms),
    };
  }

  getSavedTransformOption(name) {
    const defaultStepDataValues = selectPipelineStedDataValues(this.state, this.id);
    if (defaultStepDataValues?.length) {
      return this.isAutoML
        ? defaultStepDataValues.map((el) => el.transform)
        : defaultStepDataValues[0].transform;
    }
    return defaultStepDataValues[name];
  }

  getOutputData() {
    // console.log("getDefaultInputsData");
  }
}

export default StepDataTvo;
