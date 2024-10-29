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

import React, { useState, useEffect, useCallback } from "react";
import _ from "lodash";

import { useParams } from "react-router-dom";
import { Box } from "@mui/material";

import FeatureSegmenstHeatmapChart from "components/FeatureSegmenstHeatmapChart";
import FeatureVectorChart from "components/FeatureVectorChart";

const TheFeatureVector = ({
  modelData,
  selectLabelColorHashMap,
  featureVectorData,
  featureFileUUID,
  labelValuesHashMap,
  loadFeatureVectorData,
  isFetchingFeatureVectorData,
}) => {
  const { projectUUID } = useParams();

  const [labelColumn, setLabelColumn] = useState("");

  const [selectedSegmentIDs, setSelectedSegmentIDs] = useState([]);
  const [features, setFeatures] = useState([]);

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

  useEffect(() => {
    if (!_.isEmpty(modelData?.feature_summary)) {
      if (featureFileUUID !== modelData.feature_file_uuid) {
        loadFeatureVectorData(projectUUID, modelData.feature_file_uuid);
      }
      const _features = modelData?.feature_summary.map((el) => el.Feature);

      setFeatures(_features);

      setLabelColumn(modelData?.query_summary?.label_column || "Label");
    }
  }, [modelData]);

  return (
    <>
      <FeatureVectorChart
        featureVectorData={featureVectorData}
        features={features}
        selectLabelColorHashMap={selectLabelColorHashMap}
        isFetchingFeatureVectorData={isFetchingFeatureVectorData}
        classes={_.values(modelData.class_map || [])}
        labelColumn={labelColumn}
        onSelectSegmemts={handleSelectSegmemts}
      />
      <Box gridColumn="span 12">
        <FeatureSegmenstHeatmapChart
          featureVectorData={getFeatureVectorData()}
          modelData={getData()}
          labelColumn={labelColumn}
          selectedSegmentIDs={selectedSegmentIDs}
          labelHashMap={labelValuesHashMap}
        />
      </Box>
    </>
  );
};

export default TheFeatureVector;
