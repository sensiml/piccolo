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

import React, { useCallback } from "react";
import _ from "lodash";

import { Box } from "@mui/material";

import HeatMapChart from "components/UICharts/HeatMapChart";

const FeaturesChart = ({ featureVectorData, modelData, selectedSegmentIDs, labelColumn }) => {
  const getChartData = useCallback(() => {
    const charts = [];

    const getHeight = (yLength = 1) => {
      // for 1 y 100px whole height for multipy 10 each
      return yLength === 1 ? 100 : yLength * 10 + 50;
    };

    if (!_.isEmpty(modelData?.feature_summary) && !_.isEmpty(featureVectorData)) {
      const featureCascadeHashMap = modelData?.feature_summary.reduce((acc, { Feature }) => {
        const cascadeName = Feature.includes("gen_c") ? Feature.substr(4, 5) : "";
        const fetatureName = Feature.includes("gen_c") ? Feature.substr(10) : Feature;

        if (_.isUndefined(acc[cascadeName])) {
          acc[cascadeName] = [];
        }
        acc[cascadeName].push(fetatureName);
        return acc;
      }, {});

      selectedSegmentIDs.forEach((segmentID, indexSegment) => {
        const y = [];
        const z = [];
        let x = [];
        const segmentInx = segmentID - 1;

        _.entries(featureCascadeHashMap).forEach(([cascade, features], index) => {
          if (index === 0) {
            x = features.map((el) => el.replaceAll("gen", ""));
          }
          y.push(cascade);
          const data = features.map((feature) => {
            const featureKey = cascade ? `gen_${cascade}_${feature}` : feature;
            return featureVectorData[featureKey][segmentInx] || 0;
          });
          z.push(data);
        });
        charts.push({
          x,
          y,
          z,
          title: `${featureVectorData[labelColumn][segmentInx]} ID(${segmentID})`,
          colorscale: [
            [0, "#2dc937"],
            [0.3, "#99c140"],
            [0.5, "#e7b416"],
            [0.7, "#db7b2b"],
            [1, "#cc3232"],
          ],
          height: getHeight(y.length),
          ygap: 0.1,
          xgap: 0.1,
          type: "heatmap",
          showscale: false,
          isLast: indexSegment === selectedSegmentIDs.length - 1,
        });
      });
    }

    return charts;
  }, [modelData, featureVectorData, selectedSegmentIDs]);

  return (
    <Box width={"100%"}>
      {getChartData().map((data) => (
        <HeatMapChart
          key={data.title}
          data={[data]}
          title={data.title || ""}
          height={data.isLast ? data.height + 200 : data.height} // +200px for last xaxis bottom
          hideX={!data.isLast}
        />
      ))}
    </Box>
  );
};

export default FeaturesChart;
