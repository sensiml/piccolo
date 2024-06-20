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

import { PIPELINE_STEP_TYPES, TRANSFORM_LIST, TVO_LIST } from "store/autoML/const";
import StepDataQuery from "./StepDataQuery";
import StepDataTransform from "./StepDataTransform";
import StepDataTvo from "./StepDataTvo";
import StepDataFeatureGenerator from "./StepDataFeatureGenerator";
import StepDataFeatureSelector from "./StepDataFeatureSelector";
import StepDataSetAugmentation from "./StepDataSetAugmentation";
import StepDataAutoMLParameters from "./StepDataAutoMLParameters";

const getPipelineStepDataClass = ({ type, ...params }) => {
  if (TRANSFORM_LIST.includes(type)) {
    return new StepDataTransform({ type, ...params });
  }
  if (TVO_LIST.includes(type)) {
    return new StepDataTvo({ type, ...params });
  }
  switch (type) {
    case PIPELINE_STEP_TYPES.QUERY:
      return new StepDataQuery({ type, ...params });
    case PIPELINE_STEP_TYPES.FEATURE_GENERATOR:
      return new StepDataFeatureGenerator({ type, ...params });
    case PIPELINE_STEP_TYPES.FEATURE_SELECTOR:
      return new StepDataFeatureSelector({ type, ...params });
    case PIPELINE_STEP_TYPES.AUGMENTATION:
      return new StepDataSetAugmentation({ type, ...params });
    case PIPELINE_STEP_TYPES.AUTOML_PARAMS:
      return new StepDataAutoMLParameters({ type, ...params });
    default:
      return new StepDataTransform({ type, ...params });
  }
};

export {
  StepDataQuery,
  StepDataTransform,
  StepDataTvo,
  StepDataFeatureGenerator,
  StepDataFeatureSelector,
  StepDataSetAugmentation,
  StepDataAutoMLParameters,
};

export default getPipelineStepDataClass;
