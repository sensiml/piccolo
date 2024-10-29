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

import PipelineDataBuilderDefault from "store/containerBuildModel/domain/PipelineDataDefault";

import PipelineDataDecomposer from "store/containerBuildModel/domain/PipelineDataDecomposer";
// eslint-disable-next-line max-len
import PipelineImportDecomposer from "store/containerBuildModel/domain/PipelineImportDecomposer";
// import { getSelectedPipelineObj } from "store/pipelines/selectors";
import { updatePipelineStepsWithQuery } from "./updatePipelineStepsWithQuery";

export { updatePipelineStepsWithQuery };
export { clearPipelinesteps } from "./clearPipelinesteps";

const getPipelineDecomposerClass = (state, defaultOptions = {}) => {
  const { pipelineJson, queryName, ...restDefaultOptions } = defaultOptions;

  if (pipelineJson && !_.isEmpty(pipelineJson)) {
    return [
      new PipelineImportDecomposer(state, pipelineJson, queryName, restDefaultOptions),
      false,
    ];
  }

  const pipelineData = state.pipelines.pipelineData?.data;

  if (!_.isEmpty(pipelineData?.pipeline)) {
    return [new PipelineDataDecomposer(state, pipelineData), false];
  }

  return [new PipelineDataBuilderDefault(state, restDefaultOptions, queryName), false];
};

export default getPipelineDecomposerClass;
