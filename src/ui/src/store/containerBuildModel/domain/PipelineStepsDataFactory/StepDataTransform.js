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

/* eslint-disable consistent-return */
import { FORM_TYPES } from "consts";
import { selectTransformsByTypeSubType } from "store/transforms/selectors";
import CommonStepDataTransfrorm from "./CommonStepDataTransfrorm";

class StepDataTransform extends CommonStepDataTransfrorm {
  INPUT_DATA_KEY = "input_data";

  INPUT_FEATURE_PCA_COMPONENTS = "feature_pca_components";

  INPUT_COEFICIENTS = "coefficients";

  INPUT_MIN_BOUND_KEY = "min_bound";

  INPUT_MAX_BOUND_KEY = "max_bound";

  INPUT_SIGNAL_MIN_MAX_PARAMETERS = "signal_min_max_parameters";

  INPUT_FEATURE_MIN_MAX_DEFAULTS = "feature_min_max_defaults";

  INPUT_FEATURE_MIN_MAX_PARAMETERS = "feature_min_max_parameters";

  IGNORED_KEYS = [this.INPUT_DATA_KEY, this.INPUT_FEATURE_PCA_COMPONENTS, this.INPUT_COEFICIENTS];

  HIDDEN_KEYS = [
    this.LABEL_COLUMN_KEY,
    this.COMBINE_LABELS,
    this.FEATERE_COLUMNS,
    this.METADATA_VALUES,
    this.COLUMNS,
  ];

  MIN_MAX_MERGED_KEYS = [this.INPUT_MIN_BOUND_KEY, this.INPUT_MAX_BOUND_KEY];

  FORM_RANGE_MIN_MAX_TYPE_KEYS = [
    this.INPUT_SIGNAL_MIN_MAX_PARAMETERS,
    this.INPUT_FEATURE_MIN_MAX_DEFAULTS,
  ];

  FORM_EMPTY_MIN_MAX_TYPE_KEYS = [this.INPUT_FEATURE_MIN_MAX_PARAMETERS];

  __getInputContractDefaultValue(contrctEl, formFieldType, options) {
    const defaulVal = super.__getInputContractDefaultValue(contrctEl, formFieldType, options);
    if (this.FORM_RANGE_MIN_MAX_TYPE_KEYS.includes(contrctEl?.name)) {
      return [-100, 100];
    }
    if (this.FORM_EMPTY_MIN_MAX_TYPE_KEYS.includes(contrctEl?.name)) {
      return {};
    }

    if (defaulVal !== undefined) {
      return defaulVal;
    }
  }

  __getInputContractRange(contrctEl) {
    const defaultRange = super.__getInputContractRange(contrctEl);
    if (defaultRange) {
      return defaultRange;
    }
    if (this.FORM_RANGE_MIN_MAX_TYPE_KEYS.includes(contrctEl?.name)) {
      return [-200000, 200000];
    }
  }

  __getInputContractTypeForm(contrctEl, options) {
    const type = super.__getInputContractTypeForm(contrctEl, options);
    if (this.FORM_RANGE_MIN_MAX_TYPE_KEYS.includes(contrctEl?.name)) {
      return FORM_TYPES.FORM_RANGE_MIN_MAX_TYPE;
    }
    return type;
  }

  __getInputContractDefaultStep(contrctEl) {
    const defaultStep = super.__getInputContractDefaultStep(contrctEl);
    if (defaultStep) {
      return defaultStep;
    }
    if (this.FORM_RANGE_MIN_MAX_TYPE_KEYS.includes(contrctEl?.name)) {
      return 10;
    }
  }

  __getDefaultTransform(transforms) {
    const savedTransform = this.getSavedInputsData("transform");
    if (savedTransform) {
      return savedTransform;
    }
    if (transforms?.length === 1) {
      return transforms[0].name;
    }
    return "";
  }

  getInputsData({ transformList, excludeTransform, exactTransform }) {
    let transforms = selectTransformsByTypeSubType(
      this.type,
      this.subtype,
      transformList,
      excludeTransform,
    )(this.state);

    if (exactTransform) {
      transforms = transforms.filter((trsn) => trsn.name === exactTransform);
    }

    return {
      name: "transform",
      type: FORM_TYPES.FORM_SELECT_TYPE,
      label: `${transforms[0]?.type}`,
      default: this.__getDefaultTransform(transforms),
      options: transforms.map((el) => ({
        uuid: el.uuid,
        name: el.name,
        description: el.description,
        value: el.name,
      })),
      fieldset: this.__getInputContract(transforms),
    };
  }

  getOutputData() {
    // console.log("getDefaultInputsData");
  }
}

export default StepDataTransform;
