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
import _ from "lodash";

import Plot from "react-plotly.js";
import helper from "store/helper";
import { Grid, Typography } from "@mui/material";

import Title from "./Title";
import useStyles from "./QuerySegmentChartStyles";

const chartConfig = {
  displayModeBar: false,
  displaylogo: false,
  responsive: false,
};

const getChartData = (qd) => {
  if (!qd || helper.isNullOrEmpty(qd.label)) return null;

  if (!qd.segment_statistics) return null;

  const labels = Object.keys(qd.segment_statistics);
  const data = [];
  for (let i = 0; i < labels.length; i++) {
    data.push({
      x: qd.segment_statistics[labels[i]].x,
      y: qd.segment_statistics[labels[i]].histogram,
      type: "bar",
      name: labels[i],
      marker: {
        opacity: 0.8,
      },

      /*
      marker: {
        color: [
          "rgba(204,204,204,1)",
          "rgba(222,45,38,0.8)",
          "rgba(204,204,204,1)",
          "rgba(204,204,204,1)",
          "rgba(204,204,204,1)",
        ],
      },
      */
    });
  }
  return data;
};

export default function QuerySegmentChart({ queryData, chartLabelColors }) {
  const chartLayout = {
    xaxis: {
      showgrid: true,
      showline: true,
      showticklabels: true,
      title: "Segment Sample Size",
    },
    yaxis: {
      showgrid: true,
      showline: true,
      tickformat: ",d",
      title: "Count",
    },
    margin: { t: 10, b: 40, l: 90, r: 0 },
    hoverlabel: {
      bgcolor: "#FFF",
      font: { color: "black" },
    },
    font: {
      family: "Arial, Helvetica, sans-serif",
      size: 12,
      color: "#7f7f7f",
    },
    autosize: true,
    barmode: "stack",
    ...(!_.isEmpty(chartLabelColors) && { colorway: chartLabelColors }),
  };

  const data = getChartData(queryData);
  const classes = useStyles();
  return data ? (
    <Grid
      container
      className={classes.plotGrid}
      direction="row"
      alignItems="center"
      justifyContent="center"
      spacing={0}
    >
      <Grid item xs={12}>
        <Title> Segment Length Distribution</Title>
      </Grid>
      <Grid item xs={12}>
        <Plot
          style={{ width: "100%", height: "100%" }}
          key={`querySegment`}
          data={data}
          layout={chartLayout}
          useResizeHandler
          config={chartConfig}
        />
      </Grid>
    </Grid>
  ) : (
    <Typography style={{ paddingLeft: 12 }} variant="h5">
      No Data to Display
    </Typography>
  );
}
