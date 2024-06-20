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

import { getTransformByName } from "store/transforms/selectors";
import { selectLabelByName } from "store/labels/selectors";
import { PIPELINE_STEP_TYPES, TRANSFORM_TYPES } from "store/autoML/const";

export const getSelectedPipeline = (state) => {
  return state.pipelines?.selectedPipeline;
};

export const selectTranformSegmentColumns = (state) => {
  // eslint-disable-next-line no-use-before-define
  const featureTransformColumns = selectTransformSegmentOutputData(
    state,
    TRANSFORM_TYPES.FEATURE_TRANSFORM,
    "metadata_columns",
  );

  // eslint-disable-next-line no-use-before-define
  const segmentColumns = selectTransformSegmentOutputData(
    state,
    PIPELINE_STEP_TYPES.SEGMENTER,
    "metadata_columns",
  );
  return [featureTransformColumns, segmentColumns];
};

export const selectedQueryData = (
  state,
  queryName,
  isAddFeatureTransform = false,
  isAddSegmentId = false,
) => {
  let featureTransformColumns = [];
  let segmentColumns = [];

  if (isAddFeatureTransform) {
    // eslint-disable-next-line no-use-before-define
    featureTransformColumns = selectTransformSegmentOutputData(
      state,
      TRANSFORM_TYPES.FEATURE_TRANSFORM,
      "metadata_columns",
    );
  }

  if (isAddSegmentId) {
    // eslint-disable-next-line no-use-before-define
    segmentColumns = selectTransformSegmentOutputData(
      state,
      PIPELINE_STEP_TYPES.SEGMENTER,
      "metadata_columns",
    );
  }

  const res = state.queries?.queryList?.data.find((q) => q.name === queryName);
  return (
    {
      ...res,
      metadata_columns: _.union(res?.metadata_columns || [], [
        ...featureTransformColumns,
        ...segmentColumns,
      ]),
    } || {}
  );
};

export const selectSelectedQueryObj = (state) => {
  const pipelineStepData = state.containerBuildModel?.pipelineStepData[getSelectedPipeline(state)];
  if (pipelineStepData?.length) {
    const queryName =
      _.find(pipelineStepData, (step) => step.type === PIPELINE_STEP_TYPES.QUERY)?.customName || "";
    const selectedQuery = selectedQueryData(state, queryName);
    return selectedQuery || {};
  }
  return {};
};

export const selectPipelineSteps = (state) => {
  const pipelineStepData = state.containerBuildModel?.pipelineStepData[getSelectedPipeline(state)];
  return _.map(pipelineStepData, (data, index) => ({ ...data, index })) || [];
};

export const selectTransformSegmentOutputData = (state, type, outputDataKey) => {
  const pipelineSteps = selectPipelineSteps(state);
  const featureStep = pipelineSteps.find((step) => step.name === type || step.type === type);
  const featureTransform = getTransformByName(featureStep?.data?.transform)(state);

  if (!_.isEmpty(featureTransform?.output_contract)) {
    const outputData = featureTransform?.output_contract.find((el) => {
      return ["df_out", "output_data"].includes(el.name);
    });
    return outputData[outputDataKey] || [];
  }
  return [];
};

export const selectSensorTransformsOutputData = (sensorTransforms) => (state) => {
  /**
   * extract output data from sensor transforms
   */
  let sensorTransformColumns = [];
  const getName = (name, index) => `${name}_ST_000${index}`;

  if (!_.isEmpty(sensorTransforms)) {
    const uniqueIndexes = {};
    sensorTransformColumns = sensorTransforms.reduce((acc, transormName) => {
      const transform = getTransformByName(transormName)(state);

      if (_.isUndefined(uniqueIndexes[transormName])) {
        uniqueIndexes[transormName] = 0;
      } else {
        uniqueIndexes[transormName] += 1;
      }

      if (_.isArray(transform?.output_contract)) {
        if (!_.isEmpty(transform?.output_contract[0])) {
          acc.push(getName(transform?.output_contract[0].name, uniqueIndexes[transormName]));
        }
      }

      return acc;
    }, []);
  }
  return sensorTransformColumns;
};

export const selectSelectedQueryColumns = (state, queryName, sensorTransformNames = []) => {
  const selectedQuery = selectedQueryData(state, queryName);
  let sensorTransformColumns = [];
  if (!_.isEmpty(sensorTransformNames)) {
    sensorTransformColumns = selectSensorTransformsOutputData(sensorTransformNames)(state);
  }
  return _.union(selectedQuery?.columns || [], sensorTransformColumns);
};

export const selectSelectedQueryLabelColumn = (state, queryName) => {
  const selectedQuery = selectedQueryData(state, queryName);
  return selectedQuery?.label_column || "";
};

export const selectSelectedQueryCombineLabels = (state, queryName) => {
  const selectedQuery = selectedQueryData(state, queryName);
  return selectedQuery?.combine_labels || [];
};

export const selectSelectedQueryLabelValues = (state, queryName) => {
  const selectedQuery = selectedQueryData(state, queryName);
  const label = selectLabelByName(selectedQuery?.label_column)(state);
  if (label?.label_values?.length) {
    return label.label_values.map((el) => el.value);
  }
  return [];
};

export const selectSelectedFilteredLabelValues = (state, queryName) => {
  const selectedQuery = selectedQueryData(state, queryName) || {};
  // eslint-disable-next-line camelcase
  const { label_column, metadata_filter } = selectedQuery;
  let res = [];
  // eslint-disable-next-line camelcase
  if (metadata_filter && label_column) {
    const wholeFiltersArray = _.split(metadata_filter, "AND").map((el) => _.trim(el));
    // find query with label_column in key to extract filtered data
    wholeFiltersArray.forEach((el) => {
      // eslint-disable-next-line no-shadow
      const [filterKey, filterValues] = _.split(el, "IN").map((el) => {
        return _.trim(el).replace(/[[\]]/g, "");
      });

      // eslint-disable-next-line camelcase
      if (filterKey === label_column && filterValues) {
        res = filterValues.split(",");
      }
    });
  }
  if (_.isEmpty(res)) {
    return selectSelectedQueryLabelValues(state, queryName);
  }
  return res;
};

export const selectPipelineStedDataValues = (state, idPipelineStepData) => {
  const pipelineStepData = state.containerBuildModel?.pipelineStepData[getSelectedPipeline(state)];
  const res = pipelineStepData?.find((step) => step?.id === idPipelineStepData);
  return res?.data || {};
};

export const selectPipelineJson = (state) => {
  const pipelineStepData = state.containerBuildModel?.pipelineJsonData[getSelectedPipeline(state)];
  return pipelineStepData || [];
};

export const selectReplacedToSessionSteps = (state) => {
  if (state.containerBuildModel?.replacedToSessionSteps) {
    const pipelineStepData =
      state.containerBuildModel?.replacedToSessionSteps[getSelectedPipeline(state)];
    return pipelineStepData || [];
  }
  return [];
};

export const selectAutoMLParams = (state) => {
  const pipelineStepData = state.containerBuildModel?.pipelineStepData[getSelectedPipeline(state)];
  if (_.isArray(pipelineStepData)) {
    return (
      pipelineStepData.find((step) => step.type === PIPELINE_STEP_TYPES.AUTOML_PARAMS)?.data || {}
    );
  }
  return [];
};

export const selectSelectedQueryMetadataColumns = (
  state,
  queryName,
  isAddSegmentId = false,
  isAddFeatureTransform = false,
) => {
  const selectedQuery = selectedQueryData(state, queryName, isAddFeatureTransform, isAddSegmentId);
  if (selectedQuery?.metadata_columns?.length) {
    const metadataColumns = [...selectedQuery?.metadata_columns] || []; // copy
    const res = _.union(metadataColumns, [selectedQuery?.label_column]);

    return res;
  }
  return [];
};
