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

import React, { useState, useEffect } from "react";
import _ from "lodash";
import { Box, Typography } from "@mui/material";
import Plot from "react-plotly.js";
import useStyles from "./TestModelsStyles";

const FeatureVectorHeatmap = ({
  classificationData,
  featureSummary,
  onHover,
  modelName,
  captureFileName,
}) => {
  const [featureVectorData, setFeatureVectorData] = useState(null);
  const fontFamilies = "Roboto, Helvetica, Arial, sans-serif";
  const fontSize = 20;
  const chartLayout = {
    autosize: true,
    title: `<b>Feature Vector Heat Map - ${modelName} - ${captureFileName}</b>`,
    xaxis: {
      title: "Segment ID",
      titlefont: { family: fontFamilies, size: fontSize },
    },
    yaxis: {
      title: "Feature",
      titlefont: { family: fontFamilies, size: fontSize },
      automargin: true,
      showticklabels: false,
    },
  };
  const hoverAction = (eventdata) => {
    onHover(eventdata);
  };

  useEffect(() => {
    const featureVectors = {
      type: "heatmap",
      colorscale: "YlOrRd",
      reversescale: true,
      hovertemplate: "Segment ID: %{x} <br>Feature: %{y} <br>Value: %{z} <br><extra></extra>",
      y: [],
      z: [],
    };

    if (classificationData) {
      classificationData.forEach((cd) => {
        featureVectors.z.push(cd.FeatureVector);
      });
      // eslint-disable-next-line prefer-spread
      featureVectors.z = _.zip.apply(_, featureVectors.z);
      featureVectors.y = featureSummary.map((fs) => fs.Feature);
      setFeatureVectorData([featureVectors]);
    }
  }, [classificationData]);
  const classes = useStyles();
  return (
    <Box p={1}>
      {" "}
      {featureVectorData ? (
        <Plot
          className={classes.classificationChart}
          data={featureVectorData}
          layout={chartLayout}
          useResizeHandler={true}
          config={{ displayModeBar: false, responsive: true }}
          onHover={hoverAction}
        />
      ) : (
        <Typography variant="h4">No Feature Vector Data</Typography>
      )}
    </Box>
  );
};

export default FeatureVectorHeatmap;
