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

import { useParams } from "react-router-dom";
import { Box, FormControl, InputLabel, Select, Paper, MenuItem, Stack } from "@mui/material";

import FeaturesChart from "components/FeaturesChart";

import TableFeatureSegments from "components/TableFeatureSegments";
import FeatureSegmenstHeatmapChart from "components/FeatureSegmenstHeatmapChart";
import SelectMultiChip from "components/FormElements/SelectMultiChip";

import useStyles from "containers/ExploreModels/ExploreModelsStyles";

const TheFeatureVector = ({
  modelData,
  selectLabelColorHashMap,
  selectLabelValuesByName,
  featureVectorData,
  featureFileUUID,
  labelValuesHashMap,
  loadFeatureVectorData,
  isFetchingFeatureVectorData,
}) => {
  const classes = useStyles();
  const { projectUUID } = useParams();
  const [classNames, setClassNames] = useState([]);
  const [selectedClasses, setSelectedClasses] = useState([]);

  const [featureNames, setFeatureNames] = useState([]);
  const [labelColumn, setLabelColumn] = useState("");
  const [labelColorHashMap, setLabelColorHashMap] = useState({});

  const [selectedSegmentIDs, setSelectedSegmentIDs] = useState([]);
  const [selectedSegmentIndex, setSelectedSegmentIndex] = useState(-1);
  const [featureX, setFeatureX] = useState("");
  const [featureY, setFeatureY] = useState("");
  const [featureZ, setFeatureZ] = useState("");

  const chartGridRef = useRef(null);

  const getData = useCallback(() => {
    // to speed up rendering
    if (!_.isEmpty(modelData)) {
      return modelData;
    }
    return [];
  }, [modelData]);

  const getFeatureVectorData = useCallback(() => {
    // to speed up rendering
    if (!_.isEmpty(featureVectorData)) {
      return featureVectorData;
    }
    return [];
  }, [featureVectorData]);

  const handleSelectSegmemts = (selectedIDs) => {
    setSelectedSegmentIDs(selectedIDs);
  };

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

  useEffect(() => {
    if (!_.isEmpty(modelData?.feature_summary)) {
      if (featureFileUUID !== modelData.feature_file_uuid) {
        loadFeatureVectorData(projectUUID, modelData.feature_file_uuid);
      }
      const features = modelData?.feature_summary.map((el) => el.Feature);

      setFeatureX(features[0]);
      setFeatureY(features[1]);
      setFeatureZ(features[2]);

      setLabelColumn(modelData?.query_summary?.label_column || "Label");
      setLabelColorHashMap(
        selectLabelColorHashMap(modelData?.query_summary?.label_column || "Label"),
      );

      setFeatureNames(features);
      setClassNames(_.values(modelData.class_map).map((el) => ({ name: el, value: el })));
      setSelectedClasses(_.values(modelData.class_map));
    }
  }, [modelData]);

  const labelValues = useMemo(() => {
    if (labelColumn) {
      return selectLabelValuesByName(modelData?.query_summary?.label_column || "Label");
    }
    return [];
  }, [labelColumn, modelData]);

  return (
    <Box display="grid" gridTemplateColumns="repeat(12, 1fr)" gridAutoRows={"max-content"} gap={2}>
      <Paper className={classes.featureItemPaper} elevation={0} ref={chartGridRef}>
        {/* <Box> */}
        <Stack direction="column" p={1}>
          <Stack mb={2}>
            <SelectMultiChip
              id="classMap"
              labelId="classMapLabel"
              name="classMap"
              label="Classes"
              size="small"
              isUpdateWithDefault={false}
              isObserveDefaultValue={true}
              defaultValue={selectedClasses || []}
              options={classNames}
              onChange={handleSelectClasses}
              disabledOptions={["segment_uuid"]}
            />
          </Stack>
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
              >
                {featureNames.map((name) => (
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
              >
                {featureNames.map((name) => (
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
          featureNames={featureNames}
          labelColumn={labelColumn}
          featureX={featureX}
          featureY={featureY}
          featureZ={featureZ}
          parentRef={chartGridRef}
          colorHashMap={labelColorHashMap}
          selectedClasses={selectedClasses}
          selectedSegmentIndex={selectedSegmentIndex}
          title={"<b>Feature Vector Plot</b>"}
          isFetching={isFetchingFeatureVectorData}
          onSelectPoint={handleSelectSegmemtIndex}
        />
        {/* </Box> */}
      </Paper>
      <Paper className={classes.featureItemPaper} elevation={0}>
        <TableFeatureSegments
          featureData={featureVectorData}
          labelColumn={labelColumn}
          labelValues={labelValues}
          colorHashMap={labelColorHashMap}
          selectedSegmentIndex={selectedSegmentIndex}
          selectionField="id"
          onSelectSegmemts={handleSelectSegmemts}
          onSelectSegmemtIndex={handleSelectSegmemtIndex}
        />
      </Paper>
      <Box gridColumn="span 12">
        <FeatureSegmenstHeatmapChart
          featureVectorData={getFeatureVectorData()}
          modelData={getData()}
          labelColumn={labelColumn}
          selectedSegmentIDs={selectedSegmentIDs}
          labelHashMap={labelValuesHashMap}
        />
      </Box>
    </Box>
  );
};

export default TheFeatureVector;
