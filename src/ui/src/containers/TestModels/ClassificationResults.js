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
/* eslint-disable indent */
import React, { useState, useEffect, useRef } from "react";
import _ from "lodash";
import { AppBar, Grid, Tab, Tabs, Typography } from "@mui/material";
import TabPanel from "components/TabPanel";
import ConfusionMatrix from "components/ConfusionMatrix";
import useStyles from "./TestModelsStyles";
import ClassificationChart from "./ClassificationChart";
import FeatureVectorHeatmap from "./FeatureVectorHeatmap";

const ClassificationResults = ({
  classifierResults,
  modelName,
  classMap,
  featureSummary,
  activeSession,
  showSummary,
  summaryConfusionMatrix,
}) => {
  const classes = useStyles();
  const classificationChartRef = useRef();
  const [value, setValue] = useState(0);
  const [mdlName, setMdlName] = useState("");
  const [selectedSession, setSelectedSession] = useState("");

  const handleHeatMapHover = (event, curRef) => {
    if (curRef.current) {
      curRef.current.handleHeatMapHover(event);
    }
  };

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  function a11yProps(index) {
    return {
      id: `full-width-tab-${index}`,
      "aria-controls": `full-width-tabpanel-${index}`,
    };
  }

  useEffect(() => {
    setValue(0);
  }, [showSummary]);

  useEffect(() => {
    setSelectedSession(activeSession);
  }, [activeSession]);

  useEffect(() => {
    setMdlName(modelName);
  }, [modelName]);

  return (
    <div className={classes.classifierResultsTabPanel}>
      <AppBar position="static" color="default">
        <Tabs
          value={value}
          onChange={handleChange}
          indicatorColor="primary"
          textColor="primary"
          variant="scrollable"
          scrollButtons="auto"
        >
          {showSummary ? (
            <Tab label="Summary" {...a11yProps(0)} />
          ) : (
            classifierResults.map((classifierResult, index) => {
              return (
                <Tab
                  key={classifierResult.captureUuid}
                  label={classifierResult.fileName}
                  {...a11yProps(index + (showSummary ? 1 : 0))}
                />
              );
            })
          )}
        </Tabs>
      </AppBar>
      {showSummary ? (
        <TabPanel p={2} value={value} index={0}>
          <ConfusionMatrix
            model={{
              isFetching: false,
              data:
                summaryConfusionMatrix && !_.isEmpty(summaryConfusionMatrix)
                  ? summaryConfusionMatrix
                  : null,
            }}
            showTitle={true}
          />
        </TabPanel>
      ) : (
        classifierResults.map((classifierResult, idx) => {
          return (
            <TabPanel
              value={value}
              key={classifierResult.captureUuid}
              index={idx + (showSummary ? 1 : 0)}
            >
              <Grid container className={classes.classifierResultsTabGrid} spacing={1}>
                <Grid item xs={12}>
                  {classifierResult.confusion_matrices[selectedSession] ? (
                    <ConfusionMatrix
                      model={{
                        isFetching: false,
                        data: classifierResult.confusion_matrices[selectedSession],
                      }}
                      modelName={modelName}
                      fileName={`${classifierResult.fileName}`}
                      showTitle={true}
                      fea
                    />
                  ) : (
                    <Typography variant="h6">
                      {`${classifierResult.fileName} - Session ${selectedSession} has no confusion matrix`}
                    </Typography>
                  )}
                </Grid>
                <Grid item xs={12}>
                  <ClassificationChart
                    ref={classificationChartRef}
                    classificationData={classifierResult}
                    classMap={classMap}
                    activeSession={selectedSession}
                    modelName={mdlName}
                    captureFileName={classifierResult.fileName}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FeatureVectorHeatmap
                    classificationData={classifierResult.results}
                    featureSummary={featureSummary}
                    onHover={(event) => handleHeatMapHover(event, classificationChartRef)}
                    modelName={mdlName}
                    captureFileName={classifierResult.fileName}
                  />
                </Grid>
              </Grid>
            </TabPanel>
          );
        })
      )}
    </div>
  );
};

export default ClassificationResults;
