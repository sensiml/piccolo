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

import React from "react";
import { PIPELINE_STEP_TYPES } from "store/autoML/const";

import FormQuery from "./FormQuery";
import FormTransform from "./FormTransform";
import FormSetTransforms from "./FormSetTransforms";
import FormAutoMLFeatureGenerator from "./FormAutoMLFeatureGenerator";
import FormAutoMLParams from "./FormAutoMLParams";

const FormPipelineStep = (props) => {
  const { type, name } = props;

  if (!type && name) {
    return <FormTransform {...props} />;
  }

  switch (type) {
    case PIPELINE_STEP_TYPES.QUERY:
      return <FormQuery {...props} />;
    case PIPELINE_STEP_TYPES.TRANSFORM:
      return <FormTransform {...props} />;
    case PIPELINE_STEP_TYPES.SEGMENTER:
      return <FormTransform {...props} />;
    case PIPELINE_STEP_TYPES.SAMPLER:
      return <FormTransform {...props} />;
    // set
    case PIPELINE_STEP_TYPES.FEATURE_GENERATOR:
      return <FormAutoMLFeatureGenerator {...props} />;
    case PIPELINE_STEP_TYPES.FEATURE_SELECTOR:
      return <FormSetTransforms isUniqueTransforms={true} {...props} />;
    case PIPELINE_STEP_TYPES.AUGMENTATION:
      return <FormSetTransforms {...props} />;
    // TVO
    case PIPELINE_STEP_TYPES.TRAINING_ALGORITHM:
      return <FormTransform {...props} />;
    case PIPELINE_STEP_TYPES.CLASSIFIER:
      return <FormTransform {...props} />;
    case PIPELINE_STEP_TYPES.VALIDATION:
      return <FormTransform {...props} />;
    case PIPELINE_STEP_TYPES.AUTOML_PARAMS:
      return <FormAutoMLParams {...props} />;
    default:
      return <div>Form is not supported</div>;
  }
};

export default FormPipelineStep;
