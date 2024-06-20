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
import { CHART_LOW_VALUES, CHART_MED_VALUES, CHART_BIG_VALUES } from "consts";
import { selectAutoMLParams } from "store/containerBuildModel/selectors";

export const getChartIterationMetrics = (state) => {
  // "fitness", "sram", "latency", "positive_predictive_rate",
  const METRICS_TO_SHOW = ["accuracy", "f1_score", "sensitivity", "classifiers_sram", "features"];
  const DEFAULT_TRACE = {
    type: "box",
    marker: { size: 5 },
    line: { width: 1 },
    showlegend: true,
    boxpoints: "outliers",
  };

  const METRICS_GROUP = {
    fitness: CHART_LOW_VALUES,
    features: CHART_LOW_VALUES,
    accuracy: CHART_MED_VALUES,
    sensitivity: CHART_MED_VALUES,
    f1_score: CHART_MED_VALUES,
    positive_predictive_rate: CHART_MED_VALUES,
    sram: CHART_BIG_VALUES,
    classifiers_sram: CHART_BIG_VALUES,
    latency: CHART_BIG_VALUES,
  };

  const metricsData = state.pipelines?.iterationMetrics?.data;
  const predictionTarget = selectAutoMLParams(state)["prediction_target(%)"];

  const getMetricGroup = (name) => {
    if (METRICS_GROUP[name]) {
      return METRICS_GROUP[name];
    }
    return CHART_MED_VALUES;
  };

  const isHiddenTrace = (name) => {
    // show selected target automl
    if (getMetricGroup(name) === CHART_MED_VALUES) {
      return !_.keys(predictionTarget).includes(name);
    }
    return false;
  };

  // generate chart zero array
  if (!_.isEmpty(metricsData)) {
    const result = Object.entries(metricsData).reduce((acc, [name, val]) => {
      if (METRICS_TO_SHOW.includes(name)) {
        if (!acc[getMetricGroup(name)]) {
          acc[getMetricGroup(name)] = [];
        }

        if (val) {
          const metricsDataChunk = Object.entries(val).reduce(
            (metricsObjAcc, [metrKey, metrVal]) => {
              if (metrVal?.length) {
                metrVal.forEach((el) => {
                  metricsObjAcc.x.push(metrKey);
                  metricsObjAcc.y.push(el);
                });
              }
              return metricsObjAcc;
            },
            {
              ...DEFAULT_TRACE,
              x: [],
              y: [],
              name,
              ...(isHiddenTrace(name) && { visible: "legendonly" }),
            },
          );

          acc[getMetricGroup(name)].push(metricsDataChunk);
        }
      }
      return acc;
    }, {});
    if (!_.isEmpty(result)) {
      return result;
    }
  }

  return {};
};

export default getChartIterationMetrics;
