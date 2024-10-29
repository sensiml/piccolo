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

/* eslint-disable max-len */
import React, { useState, useEffect } from "react";
import { Box, Tab, Tabs, Paper } from "@mui/material";

import PipelineBuilder from "components/PipelineBuilder";
import FeatureSummary from "components/FeatureSummary";
import ModelSummary from "components/ModelSummary";

import TabPanel from "components/TabPanel";
import NoContent from "components/ResponsiveTable/NoContent";
import ModelControlPanel from "components/ModelControlPanel";
import TheFeatureVector from "containers/ExploreModels/TheFeatureVector";
import TheFeatureEmbedding from "containers/ExploreModels/TheFeatureEmbedding";
import TheConfusionMatrix from "containers/ExploreModels/TheConfusionMatrix";

import { Switch, Route, Link, Redirect, generatePath, useParams } from "react-router-dom";

import { ROUTES } from "routers";

import { AppLoader } from "components/UILoaders";

import useStyles from "./ExploreModelsStyles";

function a11yProps(index) {
  return {
    id: `full-width-tab-${index}`,
    "aria-controls": `full-width-tabpanel-${index}`,
  };
}

const ExploreModels = ({ model, selectedModel, setSelectedModel }) => {
  const classes = useStyles();
  const { projectUUID, modelUUID } = useParams();

  const [loadingModelData, setLoadingModelData] = useState(false);
  const [modelData, setModelData] = useState(model);

  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  useEffect(() => {
    setModelData(model);
    if (model) setLoadingModelData(model.isFetching);
  }, [model]);

  useEffect(() => {
    if (modelUUID && modelUUID !== selectedModel) {
      setSelectedModel(modelUUID);
    }
  }, [modelUUID]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <Box className={classes.box}>
      <Box mb={2}>
        <ModelControlPanel modelData={modelData?.data || {}} />
      </Box>

      <Paper elevation={0}>
        <Tabs
          value={value}
          onChange={handleChange}
          indicatorColor="primary"
          textColor="primary"
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab
            label="Confusion Matrix"
            component={Link}
            to={{
              pathname: generatePath(ROUTES.MAIN.MODEL_EXPLORE.child.CONFUSION_MATRIX.path, {
                projectUUID,
                modelUUID,
              }),
            }}
            {...a11yProps(0)}
          />
          <Tab
            label="Feature Visualization"
            component={Link}
            to={{
              pathname: generatePath(ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_VISUALIZATION.path, {
                projectUUID,
                modelUUID,
              }),
            }}
            {...a11yProps(1)}
          />
          <Tab
            label="Feature Embedding"
            component={Link}
            to={{
              pathname: generatePath(ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_EMBEDDING.path, {
                projectUUID,
                modelUUID,
              }),
            }}
            {...a11yProps(1)}
          />
          <Tab
            label="Feature Summary"
            component={Link}
            to={{
              pathname: generatePath(ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_SUMMARY.path, {
                projectUUID,
                modelUUID,
              }),
            }}
            {...a11yProps(1)}
          />
          <Tab
            label="Model Summary"
            component={Link}
            to={{
              pathname: generatePath(ROUTES.MAIN.MODEL_EXPLORE.child.MODEL_SUMMARY.path, {
                projectUUID,
                modelUUID,
              }),
            }}
            {...a11yProps(1)}
          />
          <Tab
            label="Pipeline Summary"
            component={Link}
            to={{
              pathname: generatePath(ROUTES.MAIN.MODEL_EXPLORE.child.PIPELINE_SUMMARY.path, {
                projectUUID,
                modelUUID,
              }),
            }}
            {...a11yProps(1)}
          />
          <Tab
            label="Knowledge Pack Summary"
            component={Link}
            to={{
              pathname: generatePath(ROUTES.MAIN.MODEL_EXPLORE.child.KNOWLEDGE_PACK_SUMMARY.path, {
                projectUUID,
                modelUUID,
              }),
            }}
            {...a11yProps(1)}
          />
        </Tabs>
      </Paper>
      <Switch>
        <Route path={ROUTES.MAIN.MODEL_EXPLORE.child.CONFUSION_MATRIX.path}>
          <TabPanel value={value} index={0}>
            <TheConfusionMatrix model={modelData} />
          </TabPanel>
        </Route>
        <Route path={ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_VISUALIZATION.path}>
          <TheFeatureVector />
        </Route>
        <Route path={ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_EMBEDDING.path}>
          <TheFeatureEmbedding />
        </Route>
        <Route path={ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_SUMMARY.path}>
          <TabPanel value={value} index={3}>
            {value === 3 ? (
              <FeatureSummary
                featureSummary={modelData?.data.feature_summary}
                featureStatistics={modelData?.data?.model_results?.feature_statistics?.validation}
                classMap={model?.data?.class_map}
              />
            ) : null}
          </TabPanel>
        </Route>
        <Route path={ROUTES.MAIN.MODEL_EXPLORE.child.MODEL_SUMMARY.path}>
          <TabPanel value={value} index={4}>
            <ModelSummary model={modelData} />
          </TabPanel>
        </Route>
        <Route path={ROUTES.MAIN.MODEL_EXPLORE.child.PIPELINE_SUMMARY.path}>
          <TabPanel value={value} index={5}>
            {modelData.data.pipeline_summary ? (
              <PipelineBuilder pipelineSteps={modelData.data.pipeline_summary} />
            ) : (
              <Box p={1} className={classes.box}>
                <NoContent text="You may not have built the model yet. There is no Pipeline Summary to display." />
              </Box>
            )}
          </TabPanel>
        </Route>
        <Route path={ROUTES.MAIN.MODEL_EXPLORE.child.KNOWLEDGE_PACK_SUMMARY.path}>
          <TabPanel value={value} index={6}>
            {modelData.data.knowledgepack_summary ? (
              <PipelineBuilder
                pipelineSteps={modelData.data.knowledgepack_summary.recognition_pipeline}
              />
            ) : (
              <Box m="auto" p={1} className={classes.box}>
                <NoContent text="You may not have built the model yet. There is no Knowledge Pack Summary to display." />
              </Box>
            )}
          </TabPanel>
        </Route>
        <Route>
          {modelUUID ? (
            <Redirect
              from={ROUTES.MAIN.MODEL_EXPLORE.path}
              to={{
                pathname: generatePath(ROUTES.MAIN.MODEL_EXPLORE.child.CONFUSION_MATRIX.path, {
                  projectUUID,
                  modelUUID,
                }),
              }}
            />
          ) : null}
        </Route>
      </Switch>
      <AppLoader isOpen={loadingModelData} />
    </Box>
  );
};

export default ExploreModels;
