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

export { default as getChartIterationMetrics } from "./getChartIterationMetrics";
export { default as getPipelinesWithStats } from "./getPipelinesWithStats";

export const getSelectedPipeline = (state) => {
  return state.pipelines?.selectedPipeline;
};

export const getPipelineObj = (pipelineUUID) => (state) => {
  if (state.pipelines?.pipelineList?.data?.length) {
    return state.pipelines?.pipelineList?.data?.find((ppl) => ppl.uuid === pipelineUUID);
  }
  return {};
};

export const getPipelineJSON = (pipelineData) => {
  // eslint-disable-next-line camelcase
  const { pipeline = [], hyper_params = {} } = pipelineData;
  return JSON.stringify({ pipeline, hyper_params });
};

export const getSelectedPipelineObj = (state) => {
  return state.pipelines?.pipelineData?.data || {};
};

export const getPipelineResultTableData = (state) => {
  // convert objet of arrays to array of object
  const pipelineResultData = state.pipelines?.pipelineResults?.data || {};

  if (_.isEmpty(pipelineResultData)) {
    return {};
  }
  const res = [];
  Object.entries(pipelineResultData).forEach(([key, valArr], dataIndex) => {
    if (_.isArray(valArr)) {
      valArr.forEach((value, index) => {
        if (dataIndex === 0) {
          res.push({ [key]: value });
        } else if (res[index]) {
          res[index][key] = value;
        }
      });
    }
  });

  return res;
};
