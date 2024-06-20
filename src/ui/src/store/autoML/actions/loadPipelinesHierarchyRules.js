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

import api from "store/api";
import logger from "store/logger";
import helper from "store/helper";
import "regenerator-runtime/runtime";
import { getUniqueId } from "utils";
import { STORE_PIPELINE_HIERACHY_RULES } from "../actionTypes";

const loadPipelinesHierarchyRules = () => async (dispatch) => {
  const getType = (transformFilter) => {
    if (transformFilter?.length) {
      return transformFilter[0].Type;
    }
    return "";
  };

  const getSubtypes = (transformFilter) => {
    if (transformFilter?.length) {
      return transformFilter.filter((el) => el.Subtype).map((el) => el.Subtype);
    }
    return [];
  };

  const formatToJsObj = (rule) => ({
    name: rule.Name,
    customName: null,
    nextSteps: rule["Next Step"],
    mandatory: rule.Mandatory,
    type: getType(rule.TransformFilter),
    subtype: getSubtypes(rule.TransformFilter),
    transformFilter: rule.TransformFilter || [],
    transformList: rule.TransformList || [],
    excludeTransform: rule.Exclude || [],
    limit: rule.Limit || null,
    set: rule.Set,
    id: getUniqueId(), // magic from lodash
  });

  try {
    const { data } = await api.get("automl/pipeline-hierarchy-rules/");
    dispatch({
      type: STORE_PIPELINE_HIERACHY_RULES,
      payload: data.map((rule) => formatToJsObj(rule)),
    });
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(err)}`,
      err,
      "loadPipelinesHierarchyRules",
    );
  }
};

export default loadPipelinesHierarchyRules;
