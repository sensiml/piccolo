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
/* eslint-disable no-prototype-builtins */
/* eslint-disable no-return-assign */
/* eslint-disable no-param-reassign */
/* eslint-disable no-restricted-syntax */
/* eslint-disable array-callback-return */
/* eslint-disable no-shadow */
/* eslint-disable no-use-before-define */
import React, { useState, useEffect } from "react";
import StandardTable from "components/StandardTable";
import { Box, FormControl, Grid, InputLabel, MenuItem, Select, Typography } from "@mui/material";
import Plot from "react-plotly.js";
import { ColumnType } from "components/StandardTable/StandardTableConstants";
import helper from "store/helper";

// import SelectForm from "components/FormElements/SelectForm";
import SelectMultiChip from "components/FormElements/SelectMultiChip";
// import TextFieldForm from "components/FormElements/TextFieldForm";

import useStyles from "./FeatureVectorChartStyles";
import {
  chartConfig,
  contourPlot,
  defaultColorPalete,
  heatMapLayout,
  histogramLayout,
  histogramPlot,
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
} from "./FeatureVectorChartConsts";

const FeatureVectorChart = ({ model }) => {
  const [labelColumn, setLabelColumn] = useState(null);
  const [features, setFeatures] = useState(null);
  const [featureX, setFeatureX] = useState(null);
  const [featureY, setFeatureY] = useState(null);
  const [featureVectorData, setFeatureVectorData] = useState([]);
  const [featureHeatMapData, setFeatureHeatMapData] = useState([]);
  const [classMap, setClassMap] = useState([]);
  const [selectedClasses, setSelectedClasses] = useState([]);
  const [featureStatistics, setFeatureStatistics] = useState([]);
  const [featureStatsColumns, setFeatureStatsColumns] = useState([]);
  const [featureStatsData, setFeatureStatsData] = useState([]);
  const [layoutHeatMap, setLayoutHeatMap] = useState(heatMapLayout);
  const [layoutHistogram, setLayoutHistogram] = useState(histogramLayout);

  const handleHeatMapRelayout = (event) => {
    if (noOpPanModes.includes(event.dragmode) || noOpHoverModes.includes(event.hovermode)) return;
    setLayoutHistogram((prev) => setAxisRange(prev, event));
  };

  const handleFeatureVectorChartRelayout = (event) => {
    if (noOpPanModes.includes(event.dragmode) || noOpHoverModes.includes(event.hovermode)) return;
    setLayoutHeatMap((prev) => setAxisRange(prev, event));
  };

  const handleClassMapChange = (_name, value) => {
    loadData(
      model.data.feature_vector_data,
      labelColumn,
      featureStatistics,
      classMap,
      value,
      featureX,
      featureY,
    );
  };

  const handleChangeX = (event) => {
    setAxisFeature(event.target.value, X);
    loadData(
      model.data.feature_vector_data,
      labelColumn,
      featureStatistics,
      classMap,
      selectedClasses,
      event.target.value,
      featureY,
    );
  };

  const handleChangeY = (event) => {
    setAxisFeature(event.target.value, Y);
    loadData(
      model.data.feature_vector_data,
      labelColumn,
      featureStatistics,
      classMap,
      selectedClasses,
      featureX,
      event.target.value,
    );
  };

  const setAxisFeature = (featureName, axisType) => {
    if (axisType === X) {
      setFeatureX(featureName);
      setLayoutHeatMap((prev) => setXAxisTitle(prev, featureName));
      setLayoutHistogram((prev) => setXAxisTitle(prev, featureName));
      return;
    }
    setFeatureY(featureName);
    setLayoutHeatMap((prev) => setYAxisTitle(prev, featureName));
    setLayoutHistogram((prev) => setYAxisTitle(prev, featureName));
  };

  const loadFeatures = (featureSummaries) => {
    const featureNames = featureSummaries.map((f) => f.Feature);
    if (featureNames.length > 0) setAxisFeature(featureNames[0], X);
    if (featureNames.length > 1) setAxisFeature(featureNames[1], Y);
    setFeatures(featureNames);
    return featureNames;
  };

  const drawLabel = (column) => column.title;
  const drawLabelData = (data) => (isNaN(data) || data === "" ? data : Number(data).toFixed(2));

  const getStatsColumn = (titleText, fieldName, isNumeric) => {
    return {
      title: titleText,
      field: fieldName,
      sortable: true,
      type: isNumeric ? ColumnType.Numeric : ColumnType.Text,
      filterable: true,
      renderLabel: drawLabel,
      render: drawLabelData,
    };
  };
  const loadData = (
    featureVectorData,
    labelField,
    featureStatisticsData,
    allClasses,
    classesToInclude,
    featureXValue,
    featureYValue,
  ) => {
    const selectedFeatures = [featureXValue, featureYValue];

    const fsColumns = [];
    fsColumns.push(getStatsColumn("Feature", "feature"));
    fsColumns.push(getStatsColumn("Class", "class"));
    statsMetrics.map((sm) => fsColumns.push(getStatsColumn(sm, sm, true)));
    setFeatureStatsColumns(fsColumns);

    const fsData = [];
    if (helper.hasAllProperties(featureStatisticsData, selectedFeatures)) {
      if (!classesToInclude) return;
      Object.entries(allClasses)
        .filter((c) => classesToInclude.includes(c[1]))
        .map((cls) => {
          selectedFeatures.map((feature) => {
            const fd = {
              feature,
              class: cls[1],
            };
            statsMetrics.map((statsMetric) => {
              fd[statsMetric] = featureStatisticsData[feature][cls[0]][statsMetric];
            });
            fsData.push(fd);
          });
        });
    }
    setFeatureStatsData({ data: fsData, isLoading: false });

    const fvHistData = [];
    const fvHmData = [];
    let maxZValue = 0;
    if (helper.hasAllProperties(featureVectorData, selectedFeatures)) {
      const labeledData = {};
      let labelIndex = 0;
      for (const [key, value] of Object.entries(featureVectorData[labelField])) {
        if (!labeledData[value]) {
          labeledData[value] = {
            name: value,
            index: labelIndex++,
            x: [],
            y: [],
          };
        }
        labeledData[value].x.push(featureVectorData[featureXValue][key]);
        labeledData[value].y.push(featureVectorData[featureYValue][key]);
      }

      for (const [key, ld] of Object.entries(labeledData)) {
        const labelsMaxZValue = Math.max(
          helper.getModeFrequency(ld.x).frequency,
          helper.getModeFrequency(ld.y).frequency,
        );
        maxZValue = Math.max(maxZValue, labelsMaxZValue);

        if (!classesToInclude.includes(key)) continue;
        const cmIndex = helper.getKeyByValue(allClasses, ld.name) - 1;
        const labelColor = defaultColorPalete[cmIndex];

        fvHistData.push(
          {
            ...scatterPlot,
            name: ld.name,
            x: ld.x,
            y: ld.y,
            marker: {
              ...scatterPlot.marker,
              color: labelColor,
            },
          },
          {
            ...histogramPlot,
            xaxis: null,
            name: ld.name,
            x: ld.x,
            marker: {
              ...scatterPlot.marker,
              color: labelColor,
            },
            showlegend: true,
          },
          {
            ...histogramPlot,
            yaxis: null,
            name: ld.name,
            y: ld.y,
            marker: {
              ...scatterPlot.marker,
              color: labelColor,
            },
            showlegend: false,
          },
        );
        fvHmData.push({
          ...contourPlot,
          name: ld.name,
          x: ld.x,
          y: ld.y,
          zmax: labelsMaxZValue,
        });
      }
    }
    helper.sortObjects(fvHmData, "zmax", false).map((f) => (f.zmax = maxZValue));
    setFeatureVectorData(fvHistData);
    setFeatureHeatMapData(fvHmData);
  };

  const getLabelColumn = (m) => {
    if (m.pipeline_summary.length > 1 && m.pipeline_summary[0].label_column) {
      return m.pipeline_summary[0].label_column;
    }

    if (m.query_summary.label_column) return m.query_summary.label_column;

    return null;
  };

  useEffect(() => {
    if (
      (!model.hasOwnProperty("isFetching") || !model.isFetching) &&
      model.data &&
      model.data.feature_vector_data
    ) {
      const modelData = model.data;
      const classMapValues = Object.values(modelData.class_map);
      setClassMap(modelData.class_map);
      setSelectedClasses(classMapValues);

      // LoadFeatures and Charting Data
      const fNms = loadFeatures(modelData.feature_summary);
      if (fNms.length >= 1) {
        const featureStats =
          modelData.model_results && modelData.model_results.feature_statistics
            ? modelData.model_results.feature_statistics.validation
            : [];
        setFeatureStatistics(featureStats);

        const label_column = getLabelColumn(modelData);
        setLabelColumn(label_column);
        loadData(
          modelData.feature_vector_data,
          label_column,
          featureStats,
          modelData.class_map,
          classMapValues,
          fNms[0],
          fNms[1],
        );

        setLayoutHeatMap((prev) => {
          return setAxisRange(setChartTitle(prev, `<b>Density Map : ${modelData.name}</b>`));
        });
        setLayoutHistogram((prev) => {
          return setAxisRange(
            setChartTitle(prev, `<b>Feature Vector Plot : ${modelData.name}</b>`),
          );
        });
      }
    } else {
      setFeatures(null);
    }
  }, [model]);

  const classes = useStyles();
  return features ? (
    <Box p={0} className={classes.box}>
      <Grid container className={classes.grid} spacing={0}>
        <Grid item xs={12}>
          <Grid
            container
            className={classes.controlsGrid}
            direction="row"
            alignItems="center"
            justifyContent="center"
            spacing={2}
          >
            <Grid item xs={4}>
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="featureX">Feature X</InputLabel>
                <Select
                  id="featureXList"
                  labelId="featureX"
                  name="featureX"
                  label={"Feature X"}
                  value={featureX || ""}
                  onChange={handleChangeX}
                >
                  <MenuItem key="" value="" disabled />
                  {features &&
                    features.map((featureName) => {
                      return (
                        <MenuItem key={featureName} value={featureName}>
                          {featureName}
                        </MenuItem>
                      );
                    })}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={4} classes={classes.formControl}>
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="featureY">Feature Y</InputLabel>
                <Select
                  id="featureYList"
                  labelId="featureY"
                  name="featureY"
                  label={"Feature X"}
                  value={featureY || ""}
                  onChange={handleChangeY}
                >
                  <MenuItem key="" value="" disabled />
                  {features &&
                    features.map((featureName) => {
                      return (
                        <MenuItem key={featureName} value={featureName}>
                          {featureName}
                        </MenuItem>
                      );
                    })}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={4} classes={classes.formControl}>
              <SelectMultiChip
                id="classMap"
                labelId="classMapLabel"
                name="classMap"
                label="Classes"
                isUpdateWithDefault={false}
                isObserveDefaultValue={true}
                defaultValue={selectedClasses || []}
                options={
                  classMap &&
                  Object.values(classMap || {}).map((cm) => ({
                    name: cm,
                    value: cm,
                  }))
                }
                onChange={handleClassMapChange}
                disabledOptions={["segment_uuid"]}
              />
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs>
          <Grid
            container
            direction="row"
            alignItems="center"
            justifyContent="flex-start"
            spacing={0}
          >
            <Grid item xs className={classes.plotGrid}>
              <Plot
                key={`featureVectorChart`}
                data={featureVectorData}
                layout={layoutHistogram}
                useResizeHandler={true}
                config={chartConfig}
                onRelayout={handleFeatureVectorChartRelayout}
                onLegendClick={(_e) => {
                  return false;
                }}
              />
            </Grid>
            <Grid item xs className={classes.plotGrid}>
              <Plot
                key={`heatMap`}
                data={featureHeatMapData}
                layout={layoutHeatMap}
                useResizeHandler={true}
                config={chartConfig}
                onRelayout={handleHeatMapRelayout}
              />
            </Grid>
            <Grid item xs={12} className={classes.tableGrid}>
              <StandardTable
                tableId="featureStatsTable"
                tableColumns={featureStatsColumns}
                tableData={featureStatsData}
                tableTitle={statsTable.title}
                tableOptions={statsTable.options}
              />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  ) : (
    <Box p={0} className={classes.box}>
      <div className={classes.noContentWrapper}>
        <Typography variant="body1" className={classes.noContent}>
          {
            // eslint-disable-next-line max-len
            "No feature data found, You may not have built the model yet. There is no data to display visualizations."
          }
        </Typography>
      </div>
    </Box>
  );
};

export default FeatureVectorChart;
