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
import { useTheme } from "@mui/material/styles";
import { lineChartLayout } from "./layouts";
import { lineChartConfig } from "./config";

const LineChartToZero = ({ data, title, height, $xaxis, $yaxis }) => {
  const theme = useTheme();
  const [revision, setRevision] = useState(0);
  // eslint-disable-next-line no-unused-vars
  const [opacity, setOpacity] = useState("1");

  useEffect(() => {
    setRevision(revision + 1);
  }, [data]);

  return (
    <div style={{ width: "100%", position: "relative" }}>
      <Plot
        data={data}
        revision={revision}
        style={{ width: "100%", height: "100%", opacity }}
        layout={{
          type: "scatter",
          ...lineChartLayout,
          ...(height && { height }),
          plot_bgcolor: theme.plotBG,
          xaxis: {
            ...lineChartLayout.xaxis,
            ...$xaxis,
          },
          yaxis: {
            ...lineChartLayout.yaxis,
            ...$yaxis,
          },
          title,
        }}
        config={lineChartConfig}
      />
    </div>
  );
};

export default LineChartToZero;
