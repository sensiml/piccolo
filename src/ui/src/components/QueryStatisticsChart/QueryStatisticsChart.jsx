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
import useStyles from "./QueryStatisticsChartStyles";

const chartConfig = {
  displayModeBar: false,
  displaylogo: false,
  responsive: false,
};

const plotTypes = {
  segment: "segment",
  samples: "samples",
};

const getChartData = (plotType, qd, chartLabelColors) => {
  if (!qd || helper.isNullOrEmpty(qd.label)) return null;

  const cd = (() => {
    switch (plotType) {
      case plotTypes.segment:
        return qd.segmentsCharts;
      case plotTypes.samples:
        return qd.samplesCharts;
      default:
        return null;
    }
  })();

  if (!cd) return null;

  const data = {
    x: [],
    y: [],
    hovertemplate: `%{x}<br>${_.capitalize(plotType)} : %{y:,d}<extra></extra>`,
    type: "bar",
    marker: {
      opacity: 0.8,
      ...(!_.isEmpty(chartLabelColors) && chartLabelColors[0] && { color: chartLabelColors }),
    },
  };
  Object.entries(cd).forEach(([key, value]) => {
    data.x.push(key);
    data.y.push(value);
  });
  return data;
};

export const QueryStatisticsChart = ({ queryData, selectedPlotType, chartLabelColors }) => {
  const chartLayout = {
    xaxis: {
      showgrid: true,
      showline: true,
      showticklabels: true,
    },
    yaxis: {
      showgrid: true,
      showline: true,
      tickformat: ",d",
    },
    margin: { t: 10, b: 20, l: 90, r: 0 },
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
  };

  const data = getChartData(selectedPlotType, queryData, chartLabelColors);
  const classes = useStyles();
  return data ? (
    <Grid container className={classes.plotGrid} direction="row" alignItems="center" spacing={0}>
      <Grid item xs={12}>
        <Title> Label Distribution by {selectedPlotType} </Title>
      </Grid>
      <Grid item xs={12}>
        <Plot
          style={{ width: "100%", height: "100%" }}
          key={`queryStatistics`}
          data={[data]}
          layout={chartLayout}
          useResizeHandler
          config={chartConfig}
          onLegendClick={() => false}
        />
      </Grid>
    </Grid>
  ) : (
    <Typography style={{ paddingLeft: 12 }} variant="h5">
      No Data to Display
    </Typography>
  );
};

export default QueryStatisticsChart;
