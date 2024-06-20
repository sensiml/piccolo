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

/* eslint-disable camelcase */
import React, { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import _ from "lodash";
import Plot from "react-plotly.js";
import { Box, Grid, Typography } from "@mui/material";
import Plotly from "plotly.js-cartesian-dist-min";
import useStyles from "./TestModelsStyles";

const defaultColorPalete = [
  "#1f77b4", // muted blue
  "#2ca02c", // cooked asparagus green
  "#9467bd", // muted purple
  "#8c564b", // chestnut brown
  "#d62728", // brick red
  "#7f7f7f", // middle gray
  "#bcbd22", // curry yellow-green
  "#ff7f0e", // safety orange
  "#17becf", // blue-teal
  "#e377c2", // raspberry yogurt pink
];
const chartDiv = "classificationChart";
const barHeight = 0.89;
const barMarker = 0.7;
const noMatchValue = 0.97;
const ClassificationChart = (
  { classificationData, classMap, activeSession, modelName, captureFileName },
  ref,
) => {
  const unKnownClassifier = "Unknown";
  const fontFamilies = "Roboto, Helvetica, Arial, sans-serif";
  const fontSize = 20;
  const [classificationChartData, setClassificationChartData] = useState(null);
  const [groundTruthShapes, setGroundTruthShapes] = useState({ shapes: [] });
  const [classificationScatterChartData, setClassificationScatterChartData] = useState(null);

  useImperativeHandle(ref, () => ({
    handleHeatMapHover(event) {
      try {
        const classificationRow = classificationData.results[event.points[0].x];
        const classMapIndex = classMap.indexOf(classificationRow.ClassificationName);
        const pointIndex = classificationScatterChartData[classMapIndex].x.indexOf(
          classificationRow.SegmentStart,
        );

        const newCoordinates = {
          curveNumber: classMapIndex,
          pointNumber: pointIndex,
          pointIndex,
        };

        Plotly.Fx.hover(chartDiv, [newCoordinates]);
      } catch (error) {
        //
      }
    },
  }));

  const chartLayout = {
    autosize: true,
    title: `<b>Classification Chart - ${modelName} - ${captureFileName}</b>`,
    titlefont: { family: fontFamilies, size: fontSize },
    hoverdistance: 5,
    xaxis: {
      tickformat: ",d",
      showline: true,
      zeroline: false,
      title: "Time (Samples)",
      titlefont: { family: fontFamilies, size: fontSize },
      fixedrange: true,
    },
    yaxis: {
      title: "Classification",
      showline: true,
      zeroline: false,
      automargin: true,
      titlefont: { family: fontFamilies, size: fontSize },
      fixedrange: true,
      categoryorder: "array",
      categoryarray: [...classMap, unKnownClassifier].reverse(),
      range: [0, classMap.length + 1],
    },
    shapes: [],
    yaxis2: {
      fixedrange: true,
      overlaying: "y",
      side: "right",
      showgrid: false,
      visible: false,
      range: [0, 2],
    },
    yaxis3: {
      fixedrange: true,
      overlaying: "y",
      side: "right",
      showgrid: false,
      visible: false,
      range: [0, 1],
    },
  };

  useEffect(() => {
    const getEmptyBarTrace = (cls, clr) => {
      return {
        x: [null],
        y: [cls],
        mode: "markers",
        xaxis: "x",
        name: cls,
        yaxis: "y2",
        hovertemplate: `Labeled : ${cls}<extra></extra>`,
        showlegend: false,
        marker: { opacity: [0.005], color: clr },
      };
    };

    const getEmptyScatterTrace = (cls, clr) => {
      return {
        x: [null],
        y: [cls],
        type: "scatter",
        hovertemplate: `Predicted : ${cls}<extra></extra>`,
        name: cls,
        mode: "lines",
        line: { color: clr },
      };
    };

    const getRectangleShape = (x_0, x_1, clr) => {
      return {
        type: "rect",
        xref: "x",
        yref: "paper",
        x0: x_0,
        y0: 0,
        x1: x_1,
        y1: barHeight,
        fillcolor: clr,
        opacity: 0.2,
        line: {
          width: 0,
        },
      };
    };

    const colorIndex = {};
    const gtShapes = [];
    const noMatches = {
      x: [],
      y: [],
      mode: "markers",
      marker: {
        symbol: "x",
        color: "#e64646",
        size: 10,
      },
      showlegend: true,
      xaxis: "x",
      name: "Mismatch",
      yaxis: "y3",
      hoverinfo: "none",
    };

    if (classificationData && classificationData.results) {
      const scatter_traces = {};
      const bar_traces = {};
      const sesssionGroundTruth = classificationData.ground_truth.filter(
        (g) => g.Session === activeSession,
      );

      [...classMap, unKnownClassifier].forEach((cm, index) => {
        if (!colorIndex[cm]) colorIndex[cm] = defaultColorPalete[index];
        scatter_traces[cm] = getEmptyScatterTrace(cm, colorIndex[cm]);
        bar_traces[cm] = getEmptyBarTrace(cm, colorIndex[cm]);
      });

      classificationData.results.forEach((cd) => {
        scatter_traces[cd.ClassificationName].x.push(cd.SegmentStart, cd.SegmentEnd, null);
        scatter_traces[cd.ClassificationName].y.push(
          cd.ClassificationName,
          cd.ClassificationName,
          cd.ClassificationName,
        );
        if (
          sesssionGroundTruth.length > 0 &&
          !sesssionGroundTruth.some(
            (gt) =>
              _.inRange((cd.SegmentStart + cd.SegmentEnd) / 2, gt.SegmentStart, gt.SegmentEnd) &&
              cd.ClassificationName === gt.Label_Value,
          )
        ) {
          noMatches.x.push((cd.SegmentStart + cd.SegmentEnd) / 2);
          noMatches.y.push(noMatchValue);
        }
      });

      sesssionGroundTruth.forEach((gt) => {
        if (!bar_traces[gt.Label_Value]) {
          const nextIndex = Object.keys(colorIndex).length + 1;
          colorIndex[gt.Label_Value] = defaultColorPalete[nextIndex];
          bar_traces[gt.Label_Value] = getEmptyBarTrace(gt.Label_Value, colorIndex[gt.Label_Value]);
        }
        gtShapes.push(
          getRectangleShape(gt.SegmentStart, gt.SegmentEnd, colorIndex[gt.Label_Value]),
        );
        bar_traces[gt.Label_Value].x.push(gt.SegmentStart, gt.SegmentEnd);
        bar_traces[gt.Label_Value].y.push(barMarker, barMarker);
      });
      const chartData = [...Object.values(scatter_traces), ...Object.values(bar_traces), noMatches];
      setClassificationScatterChartData(Object.values(scatter_traces));
      setGroundTruthShapes({ shapes: gtShapes });
      setClassificationChartData(chartData);
    }
  }, [classificationData, activeSession]);

  const classes = useStyles();

  return (
    <Box p={1}>
      <Grid container direction="column" className={classes.grid} spacing={0}>
        <Grid item xs={12}>
          {" "}
          {classificationChartData ? (
            <Plot
              className={classes.classificationChart}
              divId={chartDiv}
              data={classificationChartData}
              layout={{ ...chartLayout, ...groundTruthShapes }}
              useResizeHandler={true}
              config={{ displayModeBar: false, responsive: true }}
            />
          ) : (
            <Typography variant="h4">No Classification Data</Typography>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default forwardRef(ClassificationChart);
