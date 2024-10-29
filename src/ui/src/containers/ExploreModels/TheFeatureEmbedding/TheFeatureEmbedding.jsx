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

import React, { useState, useEffect, useMemo, useRef } from "react";
import _ from "lodash";
import {
  Box,
  FormControl,
  FormHelperText,
  InputLabel,
  Select,
  Stack,
  Paper,
  MenuItem,
} from "@mui/material";

import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import FeaturesChart from "components/FeaturesChart";
import TableFeatureSegments from "components/TableFeatureSegments";

import IconSpinneAutoRenew from "components/UIIcons/IconSpinneAutoRenew";
import useStyles from "containers/ExploreModels/ExploreModelsStyles";

const FEATURE_ANALYSIS_TYPES = ["UMAP", "PCA", "TSNE"];

const TheFeatureEmbedding = ({
  modelData,
  selectLabelColorHashMap,
  selectLabelValuesByName,

  loadFeatureAnalysisList,
  loadFeatureAnalysisData,
  generateFeatureAnalysis,
}) => {
  const classes = useStyles();
  const { projectUUID } = useParams();
  const { t } = useTranslation("explore-models");

  const [classNames, setClassNames] = useState([]);

  const [labelColumn, setLabelColumn] = useState("");
  const [labelColorHashMap, setLabelColorHashMap] = useState({});

  const [selectedAnalysisType, setSelectedAnalysisType] = useState(FEATURE_ANALYSIS_TYPES[0]);
  const [selectedSegmentIndex, setSelectedSegmentIndex] = useState(-1);

  const [isGenerating, setIsGenerating] = useState(false);
  const [featureAnalysisData, setFeatureAnalysisData] = useState({});
  const [typeHashMap, setTypeHashMap] = useState({});
  const [generatingError, setGeneratingError] = useState("");

  const chartGridRef = useRef(null);

  const handleSelectSegmemtIndex = (segmentIndex) => {
    setSelectedSegmentIndex(segmentIndex);
  };

  const handleGenerateFeatureAnalysis = async (analysisType) => {
    const { uuid, analysis_type } = await generateFeatureAnalysis(
      projectUUID,
      modelData.feature_file_uuid,
      {
        analysis_type: analysisType,
      },
    );
    setTypeHashMap((val) => {
      const prevVal = { ...val };
      prevVal[analysis_type] = uuid;
      return prevVal;
    });
    return uuid;
  };

  const handleSelectFeatureAnalysisType = async ({ target }) => {
    if (generatingError) {
      setGeneratingError("");
    }
    if (target?.value) {
      setFeatureAnalysisData({});
      setIsGenerating(true);
      setSelectedAnalysisType(target.value);
      let analysisUUID = "";

      if (typeHashMap[target.value]) {
        analysisUUID = typeHashMap[target.value];
      } else {
        try {
          analysisUUID = await handleGenerateFeatureAnalysis(target.value);
        } catch (e) {
          setGeneratingError(e.message);
        }
      }
      if (analysisUUID) {
        const data = await loadFeatureAnalysisData(projectUUID, analysisUUID);
        setFeatureAnalysisData(data);
      }
      setIsGenerating(false);
    }
  };

  const loadFeatures = async () => {
    setIsGenerating(true);
    const features = await loadFeatureAnalysisList(projectUUID, modelData.feature_file_uuid);

    if (!_.isEmpty(features)) {
      const hashMapData = features.reduce((acc, el) => {
        acc[el.analysis_type] = el.uuid;
        return acc;
      });

      let uuid = "";
      if (hashMapData[selectedAnalysisType]) {
        uuid = hashMapData[selectedAnalysisType];
      } else {
        const lastEl = _.last(features);
        uuid = lastEl.uuid;
        setSelectedAnalysisType(lastEl.analysis_type);
      }
      const data = await loadFeatureAnalysisData(projectUUID, uuid);
      setFeatureAnalysisData(data);
      setTypeHashMap(hashMapData);
    } else {
      await handleSelectFeatureAnalysisType({ target: { value: selectedAnalysisType } });
    }
    setIsGenerating(false);
  };

  useEffect(() => {
    if (!_.isEmpty(modelData)) {
      loadFeatures();
      setLabelColumn(modelData?.query_summary?.label_column || "Label");
      setLabelColorHashMap(
        selectLabelColorHashMap(modelData?.query_summary?.label_column || "Label"),
      );
      setClassNames(_.values(modelData.class_map).map((el) => ({ name: el, value: el })));
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
      <Paper className={classes.featureItemPaper} elevation={0}>
        <Box ref={chartGridRef}>
          <Stack direction="column" p={2}>
            <Stack direction="row" spacing={1}>
              <FormControl
                size="small"
                fullWidth
                helperText={generatingError}
                error={Boolean(generatingError)}
              >
                <InputLabel id="analysisTypeLabelId">{"Analysis Type"}</InputLabel>
                <Select
                  labelId="analysisTypeLabelId"
                  id="analysisTypeId"
                  label="Analysis Type"
                  name="analysisTypeId"
                  value={selectedAnalysisType}
                  onChange={handleSelectFeatureAnalysisType}
                  disabled={isGenerating}
                  displayEmpty
                >
                  {FEATURE_ANALYSIS_TYPES.map((type) => (
                    <MenuItem key={`analysis_type${type}`} value={type}>
                      <div style={{ display: "flex", alignItems: "center" }}>
                        {type}{" "}
                        {isGenerating && selectedAnalysisType === type ? (
                          <IconSpinneAutoRenew
                            style={{ marginLeft: "0.25rem" }}
                            size="small"
                            color="primary"
                          />
                        ) : null}
                      </div>
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>{generatingError}</FormHelperText>
              </FormControl>
            </Stack>
          </Stack>
          <FeaturesChart
            key={`key-feature-embeding`}
            featureData={featureAnalysisData}
            colorHashMap={labelColorHashMap}
            labelColumn={labelColumn}
            featureX={`${selectedAnalysisType}_0`}
            featureY={`${selectedAnalysisType}_1`}
            parentRef={chartGridRef}
            selectedSegmentIndex={selectedSegmentIndex}
            title={`<b>${t("feature-embedding.chart-title")}</b>`}
            isFetching={isGenerating}
            fetchingText={t("feature-embedding.chart-fetching-text")}
            onSelectPoint={handleSelectSegmemtIndex}
            selectedClasses={classNames.map((el) => el.value)}
            isAutoRangeXaxis={true}
            maxChartSize={500}
          />
        </Box>
      </Paper>
      <Paper className={classes.featureItemPaper} elevation={0}>
        <TableFeatureSegments
          featureData={featureAnalysisData}
          labelColumn={labelColumn}
          labelValues={labelValues}
          colorHashMap={labelColorHashMap}
          selectedSegmentIndex={selectedSegmentIndex}
          onSelectSegmemtIndex={handleSelectSegmemtIndex}
        />
      </Paper>
    </Box>
  );
};

export default TheFeatureEmbedding;
