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

import helper from "store/helper";

const X = "x";
const Y = "y";
const noOpPanModes = ["zoom", "pan", "select", "lasso"];
const noOpHoverModes = ["closet", "closest", X, Y];
const eventRangesX = ["xaxis.range[0]", "xaxis.range[1]"];
const eventRangesY = ["yaxis.range[0]", "yaxis.range[1]"];
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
const contourScales = [
  "Blues",
  "Greens",
  "Viridis",
  "Earth",
  "Hot",
  "Greys",
  "Bluered",
  "Blackbody",
  "YlGnBu",
  "YlOrRd",
  "Jet",
  "Reds",
  "Rainbow",
  "Electric",
  "Portland",
  "Cividis",
  "Picnic",
];
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
const chartTitle = {
  text: ``,
  font: {
    size: 14,
    weight: "bold",
    fontFamily: ["Open Sans", "verdana", "arial", "sans-serif"],
  },
  xref: "paper",
};
const chartDimensions = {
  histogramHeight: 630,
  histogramWidth: 800,
  heatMapHeight: 630,
  heatMapWidth: 800,
};
const statsMetrics = ["count", "mean", "min", "25%", "median", "75%", "max"];

const statsTable = {
  title: "Feature Statistics",
  options: {
    rowsPerPage: 15,
    showPagination: true,
    applyFilters: true,
    noContentText: "No Feature Statistics",
    isDarkHeader: true,
  },
};

const heatMapLayout = {
  title: ``,
  height: chartDimensions.heatMapHeight,
  width: chartDimensions.heatMapWidth,
  hovermode: "closest",
  xaxis: {
    domain: [0, 0.85],
    showgrid: false,
    zeroline: true,
    autosize: false,
    title: {
      text: "",
      standoff: 20,
    },
    range: [0, 255],
  },
  yaxis: {
    domain: [0, 0.85],
    showgrid: false,
    zeroline: true,
    autosize: false,
    title: {
      text: "",
      standoff: 20,
    },
    range: [0, 255],
  },
  autosize: true,
};

const histogramLayout = {
  title: ``,
  hovermode: "closest",
  xaxis: {
    domain: [0, 0.85],
    showgrid: true,
    zeroline: true,
    title: {
      text: "",
      standoff: 20,
    },
    range: [0, 255],
  },
  yaxis: {
    domain: [0, 0.85],
    showgrid: true,
    zeroline: true,
    title: {
      text: "",
      standoff: 20,
    },
    range: [0, 255],
  },
  bargap: 0.3,
  height: chartDimensions.histogramHeight,
  width: chartDimensions.histogramWidth,
  barmode: "stack",

  legend: {
    x: 1,
    xanchor: "right",
    yanchor: "top",
    y: 1,
  },
  margin: { t: 65 },
  xaxis2: {
    domain: [0.85, 1],
    showgrid: true,
    zeroline: true,
    autosize: false,
  },
  yaxis2: {
    domain: [0.85, 1],
    showgrid: true,
    zeroline: true,
    autosize: false,
  },
  autosize: true,
};

const scatterPlot = {
  mode: "markers",
  name: "scatter",
  type: "scatter",
  x: [],
  y: [],
  marker: {
    size: 7,
    color: "red",
    line: {
      width: 0.5,
    },
    opacity: 0.8,
  },
  showlegend: false,
};

const histogramPlot = {
  name: "histogram",
  type: "histogram",
  xaxis: "x2",
  yaxis: "y2",
  marker: {
    color: "red",
    line: { width: 0.0 },
  },
  width: [0.4],
  opacity: 0.8,
  showlegend: false,
};

const contourPlot = {
  name: "histogram2dcontour",
  type: "histogram2dcontour",
  x: [],
  y: [],
  ncontours: 50,
  bingroup: 1,
  opacity: 0.7,
  showscale: true,
  zmin: 0,
  zmax: 10,
  colorscale: "Hot",
  reversescale: true,
};

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
    },
  },
  variant: "menu",
  getContentAnchorEl: null,
};

const setXAxisTitle = (layOut, newTitle) => ({
  ...layOut,
  xaxis: {
    ...layOut.xaxis,
    title: {
      ...layOut.xaxis.title,
      text: `<b>${newTitle}</b>`,
    },
  },
});

const setYAxisTitle = (layOut, newTitle) => ({
  ...layOut,
  yaxis: {
    ...layOut.yaxis,
    title: {
      ...layOut.yaxis.title,
      text: `<b>${newTitle}</b>`,
    },
  },
});

const setChartTitle = (layout, newTitle) => ({
  ...layout,
  title: {
    ...chartTitle,
    text: newTitle,
  },
});

const setAxisRange = (prevState, eventData) => {
  let xRange = [0, 255];
  let yRange = [0, 255];

  if (helper.hasAllProperties(eventData, eventRangesX)) {
    xRange = eventRangesX.map((r) => eventData[r]);
  }

  if (helper.hasAllProperties(eventData, eventRangesY)) {
    yRange = eventRangesY.map((r) => eventData[r]);
  }

  return {
    ...prevState,
    xaxis: {
      ...prevState.xaxis,
      range: xRange,
    },
    yaxis: {
      ...prevState.yaxis,
      range: yRange,
    },
  };
};

export {
  chartConfig,
  chartDimensions,
  chartTitle,
  contourScales,
  contourPlot,
  defaultColorPalete,
  heatMapLayout,
  histogramLayout,
  histogramPlot,
  MenuProps,
  noOpHoverModes,
  noOpPanModes,
  scatterPlot,
  statsTable,
  statsMetrics,
  setAxisRange,
  setChartTitle,
  setXAxisTitle,
  setYAxisTitle,
  X,
  Y,
};
