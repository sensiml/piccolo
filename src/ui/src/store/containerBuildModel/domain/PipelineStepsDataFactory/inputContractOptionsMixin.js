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

/* eslint-disable no-case-declarations */
/* eslint-disable consistent-return */
import {
  selectSelectedQueryColumns,
  selectSelectedQueryMetadataColumns,
  selectSelectedQueryLabelColumn,
  selectSelectedQueryCombineLabels,
  selectSelectedQueryLabelValues,
  selectSelectedFilteredLabelValues,
} from "store/containerBuildModel/selectors";
import { selectedSampleRate } from "store/captureConfigurations/selectors";

import inputContractAdditionalOptions, { constContracts } from "./inputContractAdditionalOptions";

const inputContractOptionsMixin = {
  selectSelectedQueryMetadataColumns,
  selectSelectedQueryColumns,

  isHasUseParam(name) {
    const option = inputContractAdditionalOptions[name];
    return Boolean(option?.default_use_param !== undefined);
  },

  getDefaultUseParam(name) {
    const option = inputContractAdditionalOptions[name];
    return Boolean(option?.default_use_param);
  },

  isQueryColumnsLookup(name) {
    const option = inputContractAdditionalOptions[name];
    return option?.lookup === constContracts.QUERY_COLUMNS;
  },

  isMetadataLabels(name) {
    const option = inputContractAdditionalOptions[name];
    return option?.lookup === constContracts.FILTERING_LABEL_VALUES;
  },

  isIgrored(name) {
    const option = inputContractAdditionalOptions[name];
    return Boolean(option?.is_ignored);
  },

  isHiddenFormEl(name) {
    const option = inputContractAdditionalOptions[name];
    return Boolean(option?.is_hidden);
  },

  isAdditionalyDefaultLookup(name) {
    const option = inputContractAdditionalOptions[name];
    return Boolean(option?.defaultLookup);
  },

  isAdditionalyLookup(name) {
    const option = inputContractAdditionalOptions[name];
    return Boolean(option?.lookup);
  },

  getDynamicDefaultValue(name) {
    /**
     * @returns {any || undefined} defualtValue
     */
    const option = inputContractAdditionalOptions[name];
    if (!option?.defaultLookup) {
      return;
    }
    switch (option?.defaultLookup) {
      case constContracts.SAMPLE_RATE:
        return selectedSampleRate()(this.state);
      case constContracts.QUERY_LABEL_COLUMN:
        return selectSelectedQueryLabelColumn(this.state, this.queryName);
      default:
        // eslint-disable-next-line no-useless-return
        return;
    }
  },

  getDynamicOptions(name, isAddSegmentId, isAddFeatureTransform, sensorTransformNames) {
    /**
     * @param isAddSegmentId - means that we should add SegmentID to group columns
     * @param isAddFeatureTransform - means that we should add FeatureTransform to group columns
     * @param isAddSensorTransform - means that we should add SensorTransform to group columns
     */
    // mixin to handle dynamic options for transform input contracts at entry point
    const option = inputContractAdditionalOptions[name];
    if (!option?.lookup) {
      return [];
    }
    switch (option?.lookup) {
      case constContracts.QUERY_COLUMNS:
        const res = this.selectSelectedQueryColumns(
          this.state,
          this.queryName,
          sensorTransformNames,
        ).map((column) => ({
          name: column,
          value: column,
          isDefault: true,
        }));
        return res;
      case constContracts.QUERY_METADATA_COLUMNS:
        return this.selectSelectedQueryMetadataColumns(
          this.state,
          this.queryName,
          isAddSegmentId,
          isAddFeatureTransform,
        ).map((column) => ({ name: column, value: column, isDefault: true }));
      case constContracts.QUERY_LABEL_COLUMN:
        // eslint-disable-next-line no-case-declarations
        const labelColumn = selectSelectedQueryLabelColumn(this.state, this.queryName);
        return [{ name: labelColumn, value: labelColumn, isDefault: true }];
      case constContracts.QUERY_COMBINE_COLUMNS:
        return selectSelectedQueryCombineLabels(this.state, this.queryName).map((column) => ({
          name: column,
          value: column,
          isDefault: true,
        }));
      case constContracts.LABEL_VALUES:
        return selectSelectedQueryLabelValues(this.state, this.queryName).map((column) => ({
          name: column,
          value: column,
          isDefault: true,
        }));
      case constContracts.FILTERING_LABEL_VALUES:
        return selectSelectedFilteredLabelValues(this.state, this.queryName).map((column) => ({
          name: column,
          value: column,
          isDefault: true,
        }));
      case constContracts.METADATA_NAMES:
        return this.selectSelectedQueryMetadataColumns(
          this.state,
          this.queryName,
          isAddSegmentId,
          isAddFeatureTransform,
        ).map((column) => ({ name: column, value: column, isDefault: true }));
      case constContracts.METADATA_LABEL_VALUES:
        // eslint-disable-next-line no-case-declarations
        return this.selectSelectedQueryMetadataColumns(
          this.state,
          this.queryName,
          isAddSegmentId,
          isAddFeatureTransform,
        ).map((column) => ({ name: column, value: column, isDefault: true }));
      default:
        return [];
    }
  },
};

export default inputContractOptionsMixin;
