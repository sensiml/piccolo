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

import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

import { scatterHistogramLayout } from "./layouts";
import { scatterHistogramConfig } from "./config";

const ScatterHistogramChart = ({
  data,
  title,
  height,
  width,
  onClick,
  $xaxis,
  $yaxis,
  $xaxis2,
  $yaxis2,
  layout,
}) => {
  const [revision, setRevision] = useState(0);

  const handleClick = (e) => {
    setRevision(revision + 1);
    onClick(e);
  };

  useEffect(() => {
    setRevision(revision + 1);
  }, [data, layout, $xaxis, $yaxis]);

  return (
    <Plot
      data={data}
      config={scatterHistogramConfig}
      key={`key-${revision}`}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%" }}
      onClick={handleClick}
      onHover={() => {
        // eslint-disable-next-line prefer-destructuring
        const dragLayer = document.getElementsByClassName("nsewdrag")[0];
        if (dragLayer?.style) {
          dragLayer.style.cursor = "pointer";
        }
      }}
      layout={{
        ...scatterHistogramLayout,
        ...(height && { height }),
        ...(width && { width }),
        xaxis: {
          ...scatterHistogramLayout.xaxis,
          ...$xaxis,
        },
        yaxis: {
          ...scatterHistogramLayout.yaxis,
          ...$yaxis,
        },
        xaxis2: {
          ...scatterHistogramLayout.xaxis2,
          ...$xaxis2,
        },
        yaxis2: {
          ...scatterHistogramLayout.yaxis2,
          ...$yaxis2,
        },
        title: {
          text: title,
          font: {
            size: 16,
            weight: "bold",
            fontFamily: ["Open Sans", "verdana", "arial", "sans-serif"],
          },
          xref: "paper",
        },
        ...layout,
      }}
      revision={revision}
    />
  );
};

export default ScatterHistogramChart;
