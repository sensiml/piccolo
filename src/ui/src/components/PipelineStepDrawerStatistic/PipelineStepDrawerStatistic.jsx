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

import React, { useState, useMemo, useRef } from "react";
import _ from "lodash";
import Sticky from "react-stickynode";
import { Box, Drawer, Divider, Tabs, Tab, Paper, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";

import FeatureSummary from "components/FeatureSummary";
import FeatureVectorChart from "components/FeatureVectorChart";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

import { IconButtonRounded } from "components/UIButtons";
import { BoxChart } from "components/UICharts";

const PipelineStepDrawerStatistic = ({
  isOpen,
  onClose,
  data,
  featureSummary,
  featureStatistics,
  features,
  featureVectorData,
  labelColumn,
  labelValues,
  selectLabelValuesColors,
  classes,
  stepName,
  isLoadFeatures = false,
  labelColors = {},
}) => {
  // const [chartWidth, setChartWidth] = useState();
  // eslint-disable-next-line no-unused-vars
  const [tabValue, setTabValue] = useState(0);

  const theme = useTheme();
  const chartGridRef = useRef(null);

  const DISTRIBUTION_TYPES = [
    "distributionSegments",
    "distributionFeatureVectors",
    "distributionSamples",
  ];

  const DISTRIBUTION_TYPE_TITLES = {
    distributionSegments: "Distribution by Segments",
    distributionSamples: "Distribution by Samples",
    distributionFeatureVectors: "Distribution by Feature Vectors",
  };

  const getChartData = (dataKey) => {
    return _.values(data).reduce((acc, el) => {
      _.entries(el[dataKey]).forEach(([key, value]) => {
        if (acc[key]) {
          acc[key] += value;
        } else {
          acc[key] = value;
        }
      });
      return acc;
    }, {});
  };

  const dataSegmentsChart = useMemo(() => {
    return DISTRIBUTION_TYPES.reduce((acc, typeKey) => {
      const _dataSegmentsChart = getChartData(typeKey);
      if (!_.isEmpty(_dataSegmentsChart) && typeKey in DISTRIBUTION_TYPE_TITLES) {
        acc.push({
          key: typeKey,
          title: DISTRIBUTION_TYPE_TITLES[typeKey],
          data: _dataSegmentsChart,
        });
      }
      return acc;
    }, []);
  }, [data]);

  const handleChangeTab = (_name, val) => {
    setTabValue(val);
  };

  return (
    <Drawer
      // BackdropProps={{ style: { backgroundColor: theme.backgroundBackDoor } }}
      classes={{
        root: classes.formDrawerRoot,
        paperAnchorRight: classes.formDrawerSizing,
      }}
      open={isOpen}
      onClose={onClose}
      anchor={"right"}
      variant="temporary"
    >
      <Sticky top={0.1} innerZ={101}>
        <Paper elevation={0}>
          <Box display={"flex"} alignItems={"center"} p={2}>
            <IconButtonRounded onClick={onClose} color="primary" size="small">
              <ArrowBackIcon />
            </IconButtonRounded>
            <Typography variant="h2" align="center" flex={1}>
              {stepName}
            </Typography>
          </Box>
          <Divider mt={2} />
          {isLoadFeatures ? (
            <Tabs
              variant="fullWidth"
              value={tabValue}
              onChange={handleChangeTab}
              indicatorColor="primary"
              textColor="primary"
              scrollButtons="auto"
              aria-label="scrollable auto tabs"
              style={{ borderBottom: `1px solid ${theme.borderBrandTransparent}` }}
            >
              <Tab label={"Feature Visualization"} />
              <Tab label={"Feature Statistics"} />
            </Tabs>
          ) : null}
        </Paper>
      </Sticky>
      <Box m={2} mt={16}>
        <Box ref={chartGridRef}>
          {tabValue === 0 ? (
            <>
              {dataSegmentsChart.map((chartObj) => (
                <Box>
                  <BoxChart
                    id={chartObj.key}
                    key={chartObj.key}
                    title={chartObj.title}
                    height={350}
                    data={[
                      {
                        y: _.values(chartObj.data),
                        x: _.keys(chartObj.data),
                        marker: {
                          color: _.keys(chartObj.data).map((l) => labelColors[l]),
                          opacity: 0.8,
                        },
                        type: "bar",
                      },
                    ]}
                  />
                </Box>
              ))}
              {isLoadFeatures ? (
                <FeatureVectorChart
                  features={features}
                  featureVectorData={featureVectorData}
                  parentRef={chartGridRef}
                  labelColumn={labelColumn}
                  classes={labelValues}
                  selectLabelColorHashMap={selectLabelValuesColors}
                  isFetchingFeatureVectorData={_.isEmpty(featureVectorData)}
                  moveClassesDown
                />
              ) : null}
            </>
          ) : (
            <FeatureSummary
              featureSummary={featureSummary}
              featureStatistics={featureStatistics}
              isFetching={_.isEmpty(featureSummary)}
            />
          )}
        </Box>
      </Box>
    </Drawer>
  );
};

export default PipelineStepDrawerStatistic;
