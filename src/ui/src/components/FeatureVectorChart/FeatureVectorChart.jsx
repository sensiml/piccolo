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

import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import _ from "lodash";

import { Box, FormControl, InputLabel, Select, Paper, MenuItem, Stack } from "@mui/material";
import { useTranslation } from "react-i18next";

import FeaturesChart from "components/FeaturesChart";
import TableFeatureSegments from "components/TableFeatureSegments";
import SelectMultiChip from "components/FormElements/SelectMultiChip";

const FeatureVectorChart = ({
  features,
  featureVectorData,
  selectLabelColorHashMap,
  isFetchingFeatureVectorData,
  onSelectSegmemts,
  labelColumn = "Label",
  movelClassesDown = false,
  classes = [],
}) => {
  const { t } = useTranslation("components");

  const [classOptions, setClassOptions] = useState([]);
  const [selectedClasses, setSelectedClasses] = useState([]);

  const [labelColorHashMap, setLabelColorHashMap] = useState({});

  const [selectedSegmentIndex, setSelectedSegmentIndex] = useState(-1);
  const [featureX, setFeatureX] = useState("");
  const [featureY, setFeatureY] = useState("");

  const chartGridRef = useRef(null);
  const containerRef = useRef(null);

  const getFeatureVectorData = useCallback(() => {
    // to speed up rendering
    if (!_.isEmpty(featureVectorData)) {
      return featureVectorData;
    }
    return [];
  }, [featureVectorData]);

  const handleSelectSegmemtIndex = (segmentIndex) => {
    setSelectedSegmentIndex(segmentIndex);
  };

  const handleSelectFeatureX = ({ target }) => {
    if (target?.value) {
      setFeatureX(target.value);
    }
  };

  const handleSelectFeatureY = ({ target }) => {
    if (target?.value) {
      setFeatureY(target.value);
    }
  };

  const handleSelectClasses = (_name, values) => {
    setSelectedClasses(values);
  };

  const filteredFeatures = useMemo(() => {
    if (!_.isEmpty(features)) {
      return features.filter((el) => el.includes("gen_"));
    }
    return [];
  }, [features]);

  useEffect(() => {
    setFeatureX(filteredFeatures[0]);
    setFeatureY(filteredFeatures[1]);

    setLabelColorHashMap(selectLabelColorHashMap(labelColumn || "Label"));
    if (!_.isEmpty(classes)) {
      setClassOptions(classes.map((el) => ({ name: el, value: el })));
      setSelectedClasses(classes);
    }
  }, [classes, filteredFeatures]);

  const ClassSelector = () => {
    return (
      <SelectMultiChip
        id="classesSelect"
        labelId="classesSelectLabel"
        name="classesSelect"
        label="Classes"
        size="small"
        isUpdateWithDefault={false}
        isObserveDefaultValue={false}
        defaultValue={selectedClasses}
        options={classOptions}
        onChange={handleSelectClasses}
        disabled={isFetchingFeatureVectorData}
      />
    );
  };

  return (
    <Box
      display="grid"
      gridTemplateColumns={"repeat(auto-fit, minmax(500px, 1fr))"}
      ref={containerRef}
      gridAutoRows={"max-content"}
      gap={2}
    >
      <Paper elevation={0}>
        <Box p={2}>
          {!movelClassesDown ? (
            <Stack mb={2}>
              <ClassSelector />
            </Stack>
          ) : null}
          <Stack direction="column" mb={2}>
            <Stack direction="row" spacing={1}>
              <FormControl size="small" fullWidth>
                <InputLabel id="featureXLabel">{"featureX"}</InputLabel>
                <Select
                  labelId="featureXLabel"
                  id="featureXSelect"
                  label="featureX"
                  name="featureX"
                  value={featureX}
                  onChange={handleSelectFeatureX}
                  displayEmpty
                  disabled={isFetchingFeatureVectorData}
                >
                  {filteredFeatures.map((name) => (
                    <MenuItem key={`featureX_${name}`} value={name}>
                      {name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl size="small" fullWidth>
                <InputLabel id="featureYLabel">{"featureY"}</InputLabel>
                <Select
                  labelId="featureYLabel"
                  id="featureYSelect"
                  label="featureY"
                  name="featureY"
                  value={featureY}
                  onChange={handleSelectFeatureY}
                  disabled={isFetchingFeatureVectorData}
                >
                  {filteredFeatures.map((name) => (
                    <MenuItem key={`featureY_${name}`} value={name}>
                      {name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>
          </Stack>
          <FeaturesChart
            key={`key-feature-vector-chart`}
            featureData={getFeatureVectorData()}
            colorHashMap={labelColorHashMap}
            labelColumn={labelColumn}
            featureX={featureX}
            featureY={featureY}
            parentRef={chartGridRef}
            selectedClasses={selectedClasses}
            selectedSegmentIndex={selectedSegmentIndex}
            title={`<b>${t("feature-vector-chart.chart-title")}</b>`}
            onSelectPoint={handleSelectSegmemtIndex}
            isAutoRangeXaxis={true}
            isFetching={isFetchingFeatureVectorData}
            fetchingText={t("feature-vector-chart.fetching-text")}
            maxChartSize={500}
          />
          {movelClassesDown ? (
            <Stack mb={2}>
              <ClassSelector />
            </Stack>
          ) : null}
        </Box>
      </Paper>

      <Paper elevation={0}>
        <Box p={2}>
          <TableFeatureSegments
            featureData={featureVectorData}
            labelColumn={labelColumn}
            labelValues={classes}
            colorHashMap={labelColorHashMap}
            selectedSegmentIndex={selectedSegmentIndex}
            selectionField="id"
            onSelectSegmemts={onSelectSegmemts}
            onSelectSegmemtIndex={handleSelectSegmemtIndex}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default FeatureVectorChart;
