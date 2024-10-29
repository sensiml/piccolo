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

/* eslint-disable guard-for-in */
/* eslint-disable nonblock-statement-body-position */
/* eslint-disable no-return-assign */
/* eslint-disable no-restricted-syntax */
import React, { useState, useEffect } from "react";
import _ from "lodash";
import Plot from "react-plotly.js";
import useStyles from "./FeatureStatsChartStyles";

const numberOfBoxesPerRor = 4;
const chartConfig = {
  displayModeBar: true,
  displaylogo: false,
  responsive: true,
  modeBarButtonsToRemove: [
    "pan2d",
    "select2d",
    "lasso2d",
    "autoScale2d",
    "toggleSpikelines",
    "hoverClosestCartesian",
    "hoverCompareCartesian",
  ],
};
const FeatureStatsChart = ({ featureStatistics, usedFeatureNames, classMap, title = "" }) => {
  const [featureStatisticsData, setFeatureStatisticsData] = useState(null);
  const [versionKey, setVersionKey] = useState(0);

  const chartLayout = {
    boxmode: "group",
    title: `<b>${title} Feature Vector Distribution</b>`,
    hovermode: "closest",
    xaxis: {
      autosize: true,
    },
    yaxis: {
      autosize: true,
      title: {
        text: "Feature Values",
        font: {
          size: 18,
          color: "#7f7f7f",
        },
      },
    },
  };

  const loadData = (rawData, featureNames) => {
    if (rawData) {
      const listOftraces = [];
      let offsetgroup = 1;
      const dataFieldMap = {
        lowerfence: "4.5%",
        q1: "25%",
        median: "median",
        q3: "75%",
        upperfence: "95.5%",
        y: "outlier",
      };
      let featureFunctionCount = 0;
      let traces = [];

      for (const featureKey in featureNames) {
        const featureFunctionName = featureNames[featureKey];
        if (featureFunctionCount > numberOfBoxesPerRor - 1) {
          listOftraces.push(traces);
          featureFunctionCount = 0;
          traces = [];
        }
        for (const labelId in rawData[featureFunctionName]) {
          // if (!classMap[labelId]) return;
          const labelName = classMap[labelId] || labelId;
          let trace = traces.find((t) => t.name === labelName);

          if (!trace) {
            trace = {
              name: labelName,
              offsetgroup: offsetgroup++,
              type: "box",
              boxpoints: "outliers",
              x: [],
            };
            Object.keys(dataFieldMap).forEach((key) => (trace[key] = []));
            traces.push(trace);
          }

          if (!trace.x.includes(featureFunctionName)) {
            trace.x.push(featureFunctionName);
          }

          Object.keys(dataFieldMap).forEach((key) => {
            if (key === "y" && rawData[featureFunctionName][labelId][dataFieldMap.y].length === 0) {
              trace[key].push([rawData[featureFunctionName][labelId][dataFieldMap.lowerfence]]);
            } else {
              trace[key].push(rawData[featureFunctionName][labelId][dataFieldMap[key]]);
            }
          });
        }
        featureFunctionCount++;
      }
      listOftraces.push(traces);
      setFeatureStatisticsData(listOftraces);
    }
  };

  useEffect(() => {
    if (featureStatistics) {
      loadData(featureStatistics, usedFeatureNames);
    }
    setVersionKey(_.uniqueId());
  }, [featureStatistics, usedFeatureNames]);

  const classes = useStyles();
  return featureStatisticsData ? (
    <>
      {featureStatisticsData.map((fs, fsIndex) => (
        <div key={`featureStatsChart_div_${versionKey}_${fsIndex}`}>
          <Plot
            className={classes.featurestatsChart}
            data={fs}
            layout={fsIndex === 0 ? chartLayout : { ...chartLayout, title: "" }}
            config={chartConfig}
          />
        </div>
      ))}
    </>
  ) : (
    <></>
  );
};

export default FeatureStatsChart;
