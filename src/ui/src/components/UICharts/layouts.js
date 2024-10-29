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

export const baseLayout = {
  autosize: true,
  margin: {
    l: 70,
    r: 50,
    b: 70,
    t: 50,
    pad: 10,
  },
  legend: {
    borderwidth: 0,
    orientation: "h",
  },
  xaxis: {
    autorange: true,
    rangemode: "tozero",
    showline: false,
    color: "#455a64",
    zerolinecolor: "#eee",
    zerolinewidth: 3,
    standoff: 20,
  },
  yaxis: {
    autosize: true,
    rangemode: "tozero",
    autorange: true,
    showline: false,
    color: "#455a64",
    zerolinecolor: "#eee",
    zerolinewidth: 3,
  },
};

export const lineChartLayout = {
  ...baseLayout,
  colorway: [
    "#26c0c7",
    "#5151d3",
    "#e68619",
    "#ffd215",
    "#E65F8E",
    "#A86BD1",
    "#3AA5D1",
    "#3BB58F",
    "#3A63AD",
  ],
  legend: {
    ...baseLayout.legend,
    x: 0,
    y: 1.2,
  },
};

export const boxChartLayout = {
  ...baseLayout,
  margin: {
    l: 80,
    r: 80,
    b: 60,
    t: 60,
    pad: 10,
  },
  colorway: [
    "#26c0c7",
    "#5151d3",
    "#e68619",
    "#ffd215",
    "#E65F8E",
    "#A86BD1",
    "#3AA5D1",
    "#3BB58F",
    "#3A63AD",
  ],
  yaxis: {
    autosize: true,
    anchor: "free",
    overlaying: "y",
    side: "right",
    position: 1,
  },
  legend: {
    ...baseLayout.legend,
  },
  legend2: {
    ...baseLayout.legend,
  },
};

export const scatterHistogramLayout = {
  ...baseLayout,
  hovermode: "closest",
  mode: "markers",
  type: "scatter",
  x: [],
  y: [],
  autosize: true,
  bargap: 0.3,
  barmode: "stack",

  xaxis: {
    ...baseLayout.xaxis,
    domain: [0, 0.84],
    autorange: false,
    showgrid: true,
    title: {
      standoff: 20,
    },
    range: [0, 255],
  },
  yaxis: {
    ...baseLayout.xaxis,
    domain: [0, 0.84],
    autorange: false,
    showgrid: true,

    title: {
      standoff: 20,
    },
    range: [0, 255],
  },
  legend: {
    x: 1,
    xanchor: "right",
    yanchor: "top",
    y: 1,
  },
  xaxis2: {
    ...baseLayout.xaxis,
    domain: [0.85, 1],
    autosize: false,
    showgrid: true,
    zeroline: true,
  },
  yaxis2: {
    ...baseLayout.xaxis,
    domain: [0.85, 1],
    autosize: false,
    showgrid: true,
    zeroline: true,
  },
};

export const HeatMapLayout = {
  ...baseLayout,
  margin: {
    l: 50,
    r: 150,
    b: 200,
    t: 50,
    pad: 10,
  },
  hovermode: "closest",
  mode: "markers",
  type: "scatter",
  autosize: true,
  bargap: 0,
  barmode: "stack",
  yaxis: {
    autosize: true,
    anchor: "free",
    overlaying: "y",
    side: "right",
    position: 1,
  },
};
