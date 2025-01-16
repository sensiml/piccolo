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

import React, { useState, useEffect, useMemo } from "react";
import _ from "lodash";

import { Box } from "@mui/material";

import { ScatterHistogramChart } from "components/UICharts";
import { useWindowResize } from "hooks";
import { ElementLoader } from "components/UILoaders";

const scatterPlot = {
  mode: "markers",
  name: "scatter",
  type: "scatter",
  x: [],
  y: [],
  marker: {
    size: 12,
    line: {
      width: 1,
      color: "#6c6d6c",
    },
    opacity: 0.8,
  },
  autorange: true,
  showlegend: false,
};

const histogramPlot = {
  name: "histogram",
  type: "histogram",
  xaxis: "x2",
  yaxis: "y2",
  width: [0.4],
  opacity: 0.8,
  showlegend: false,
  autorange: true,
  marker: {
    size: 12,
    opacity: 0.8,
    line: { color: "#6c6d6c", width: 0.5, opacity: 0.5 },
  },
};

const annotationTemplate = {
  arrowhead: 6,
  ax: 0,
  ay: 0,
  bgcolor: "rgba(255, 255, 255, 0.9)",
  font: { size: 12 },
  borderwidth: 3,
  borderpad: 5,
  text: "",
  opacity: 0.4,
};

const SCALE_CHART_SIZE = 0.9;
const MAX_CHART_SIZE = 700;

const FeaturesChart = ({
  featureData,
  colorHashMap,
  labelColumn,
  featureX,
  featureY,
  parentRef,
  selectedClasses,
  title,
  selectedSegmentIndex,
  isFetching,
  fetchingText,
  onSelectPoint,
  maxChartSize = MAX_CHART_SIZE,
  isAutoRangeXaxis = false,
  isShowLegend = false,
}) => {
  const [layoutHistogram, setLayoutHistogram] = useState({});
  const [chartSize, setChartSize] = useState({ width: maxChartSize, height: maxChartSize });
  const [chartRange, setChartRange] = useState([-10, 265]);
  const [chartData, setChartData] = useState([]);

  useWindowResize(() => {
    if (parentRef?.current && parentRef.current.offsetWidth * SCALE_CHART_SIZE < maxChartSize) {
      setChartSize({
        width: parentRef.current.offsetWidth * SCALE_CHART_SIZE,
        height: parentRef.current.offsetWidth * SCALE_CHART_SIZE,
      });
    } else if (parentRef?.current) {
      setChartSize({ width: maxChartSize, height: maxChartSize });
    }
  });

  const labelIndices = useMemo(() => {
    if (!_.isEmpty(featureData[labelColumn])) {
      return featureData[labelColumn].reduce((acc, label, labelInx) => {
        if (selectedClasses && !selectedClasses.includes(label)) {
          return acc;
        }
        if (!acc[label]) {
          acc[label] = [];
        }
        acc[label].push(labelInx);
        return acc;
      }, {});
    }
    return [];
  }, [featureData, selectedClasses]);

  useEffect(() => {
    const res = [];
    const maxRanges = [];
    const minRanges = [];

    let maxRangeVal = -10;
    let minRangeVal = 260;

    _.entries(labelIndices).forEach(([label, labelInds]) => {
      const [x, y] = [featureX, featureY].map((feature) => {
        if (featureData[feature]) {
          const filteredFeatures = featureData[feature].filter((_el, index) =>
            labelInds.includes(index),
          );
          return filteredFeatures;
        }
        return [];
      });
      if (isAutoRangeXaxis) {
        [x, y].forEach((el) => {
          if (!_.isEmpty(el)) {
            maxRangeVal = _.max([maxRangeVal, _.max(el)]);
            minRangeVal = _.min([minRangeVal, _.min(el)]);
            maxRanges.push(_.max(el));
            minRanges.push(_.min(el));
          }
        });
      }
      res.push({
        ...scatterPlot,
        name: label,
        ids: labelInds,
        x,
        y,
        hovertext: "Click to show related segment",
        marker: {
          ...scatterPlot.marker,
          color: colorHashMap[label],
        },
        mode: "markers",
        type: "scatter2d",
      });

      res.push({
        ...histogramPlot,
        xaxis: null, // to keep only xaxis
        name: label,
        x,
        marker: {
          ...histogramPlot.marker,
          color: colorHashMap[label],
        },
        showlegend: isShowLegend,
      });

      res.push({
        ...histogramPlot,
        yaxis: null, // to keep only yaxis
        name: label,
        y,
        marker: {
          ...histogramPlot.marker,
          color: colorHashMap[label],
        },
        showlegend: false,
      });
    });
    if (isAutoRangeXaxis) {
      setChartRange([
        // add 5 gap based on max value
        _.round(minRangeVal - maxRangeVal * 0.05, 0),
        _.round(maxRangeVal + maxRangeVal * 0.05, 0),
      ]);
    }
    setChartData(res);
  }, [labelIndices, featureX, featureY, colorHashMap]);

  const handleClick = (e) => {
    const point = e?.points[0];
    if (featureData.segment_uuid && point.data.ids) {
      onSelectPoint(point.data.ids[point.pointIndex]);

      const newAnnotation = {
        ...annotationTemplate,
        x: point.xaxis.d2l(point.x),
        y: point.yaxis.d2l(point.y),
        bordercolor: point.fullData.marker.color,
      };
      setLayoutHistogram((prev) => ({ ...prev, annotations: [newAnnotation] }));
    }
  };

  useEffect(() => {
    if (!_.isEmpty(featureData.segment_uuid) && featureX && featureY) {
      const newAnnotation = {
        ...annotationTemplate,
        x: featureData[featureX][selectedSegmentIndex],
        y: featureData[featureY][selectedSegmentIndex],
        bordercolor: colorHashMap[featureData[labelColumn][selectedSegmentIndex]],
      };

      setLayoutHistogram((prev) => ({ ...prev, annotations: [newAnnotation] }));
    }
  }, [selectedSegmentIndex]);

  useEffect(() => {
    setLayoutHistogram((prev) => ({ ...prev, annotations: [] }));
  }, [featureX, featureY]);

  return (
    <Box mt={2} style={chartSize} margin={"auto"}>
      {isFetching ? (
        <ElementLoader
          isOpen
          message={fetchingText}
          style={{ justifyContent: "flex-start", marginTop: "4rem" }}
        />
      ) : (
        <ScatterHistogramChart
          data={chartData}
          layout={layoutHistogram}
          title={title}
          onClick={handleClick}
          $xaxis={{
            title: {
              text: featureX,
              standoff: 20,
            },
            range: chartRange,
          }}
          $yaxis={{
            title: {
              text: featureY,
              standoff: 15,
            },
            range: chartRange,
          }}
        />
      )}
    </Box>
  );
};

export default FeaturesChart;
