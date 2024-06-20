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

import { selectTransformsByTypeSubType } from "store/transforms/selectors";
import CommonStepDataFeatures from "./CommonStepDataFeatures";

class StepDataFeatureSelector extends CommonStepDataFeatures {
  INPUT_DATA_KEY = "input_data";

  PARENT_NAME_CORRELATION = "Correlation Threshold";

  PARENT_NAME_VARIANCE = "Variance Threshold";

  SELECT_FORM_TYPE = [];

  RANGE_FLOAT_TYPE = [this.PARENT_NAME_CORRELATION, this.PARENT_NAME_VARIANCE];

  IGNORED_KEYS = [];

  MIN_MAX_MERGED_KEYS = [];

  __isIgronedInputContract(contrctEl) {
    const isIgnored = super.__isIgronedInputContract(contrctEl);
    return isIgnored || Boolean(contrctEl?.handle_by_set);
  }

  getInputsData({ transformList, excludeTransform }) {
    const transforms = selectTransformsByTypeSubType(
      this.type,
      this.subtype,
      transformList,
      excludeTransform,
    )(this.state);
    const addedSubtypes = [];
    const featureList = this.__getTransformSet(transforms) || [];
    const defaultFeatureList = this.getSavedFeatures(featureList, addedSubtypes) || [];

    return {
      subtypes: this.__getSubTypes(transforms) || [],
      featureList,
      defaultFeatureList,
      addedSubtypes,
    };
  }

  getOutputData() {
    // console.log("getDefaultInputsData");
  }
}

export default StepDataFeatureSelector;
