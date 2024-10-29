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

import _ from "lodash";
import React, { useEffect, useState, useRef } from "react";
import Sticky from "react-stickynode";
import { useHistory, useParams, generatePath } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Box, Grid, Paper, Tabs, Tab } from "@mui/material";

import {
  ConsoleView,
  ConsoleBodySimpleView,
  ConsoleInformation,
  StatusRunningIcon,
  ConsoleRunningStatusText,
} from "components/LogsView";

import { getUniqueId } from "utils";
import { useInterval, useMainContext } from "hooks";
import { ROUTES } from "routers";
import { RUNNING_STATUSES } from "consts";
import { PIPELINE_STEP_TYPES } from "store/autoML/const";

import FeatureVectorChart from "components/FeatureVectorChart";

import FeatureSummary from "components/FeatureSummary";
import PipelineBuilderFeatureExtraction from "../componets/PipelineBuilderFeatureExtraction";

import QueryCacheAlertMessage from "../componets/QueryCacheAlertMessage";
import BuilderPipelinePanel from "../componets/BuilderPipelinePanel";
import PipelineBuilderAlertMessage from "../componets/PipelineBuilderAlertMessage";
import useStyles from "../BuildModeStyle";
import UIPaperNoContent from "components/UIPaperNoContent";

const RESULT_MODES = {
  CHART: 0,
  SUMMARY: 1,
  LOGS: 2,
};

const TheFeatureExtractorScreen = ({
  alertBuilder,
  pipelineValidationError,
  defaultOptions,
  pipelineHierarchyRules,
  transforms,
  selectedPipeline,
  pipelineData,
  selectedProjectObj,
  navBarIsOpen,
  getQueryData,
  getPipelineStepDataClass,
  getPipelineStepDescription,

  queryCacheStatusData,
  optimizationLogs,
  pipelineRunningStatus,
  pipelineStatus,
  pipelineResults,
  pipelineResultsIsFetching,

  selectLabelValuesColors,
  selectLabelValuesByName,

  clearAlertBuilder,
  clearOptimizationLogs,
  clearPipelineResults,
  clearPipelineStatus,
  clearQueryCacheStatus,

  setPipelineStep,
  setPipelineDefaultSteps,
  setSelectedPipeline,
  updatePipelineStepsWithQuery,

  launchModelOptimization,
  checkOptimizationStatus,

  loadPipelinesHierarchyRules,
  loadPipelineBuilderData,
  loadDataAfterTraining,
  loadPipelineResults,
  loadQueryCacheStatus,
  loadQueryStatistic,
  loadPipeline,

  stopModelOptimization,
  buildQueryCache,
  downloadPipelineStepCache,

  exportPipeline,
  getPipelineStepFeatureStats,
}) => {
  const routersHistory = useHistory();
  const scrollTop = useRef();
  const classes = useStyles(navBarIsOpen);

  const { t } = useTranslation("models");
  const { projectUUID, pipelineUUID } = useParams();
  const { showMessageSnackbar } = useMainContext();

  const [selectedSteps, setSelectedSteps] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [selectedQueryStepData, setSelectedQueryStepData] = useState({});
  const [dismissedCacheQueryList, setDismissedCacheQueryList] = useState([]);
  const [isOptimizationRunning, setIsOptimizationRunning] = useState(false);

  const [resultMode, setResultMode] = useState(RESULT_MODES.LOGS);

  const [isPipelineHasEmptySteps, setIsPipelineHasEmptySteps] = useState(false);
  const [pipelineAlert, setPipelineAlert] = useState({});

  const [queryStatistic, setQueryStatistic] = useState({});

  const chartGridRef = useRef(null);

  const getOptimizationStatus = async () => {
    const isLaunching = await checkOptimizationStatus(selectedProjectObj.uuid, selectedPipeline);
    if (!isLaunching) {
      // clear setInterval hook
      setIsOptimizationRunning(false);
      loadDataAfterTraining(
        selectedProjectObj.uuid,
        selectedPipeline,
        selectedQueryStepData?.label_column,
      );
    }
  };

  const getIsReadyToOptimize = () => {
    return !isPipelineHasEmptySteps && selectedPipeline && !_.isEmpty(pipelineData);
  };

  const getIsShowQueryCacheAlert = () => {
    return (
      !_.isUndefined(queryCacheStatusData.status) &&
      !queryCacheStatusData.status &&
      !dismissedCacheQueryList.includes(selectedQueryStepData?.uuid)
    );
  };

  const startOptimizationChecker = () => {
    setIsOptimizationRunning(true);
  };

  const clearPipelineResult = () => {
    clearOptimizationLogs();
    clearPipelineResults();
  };

  const setPipelineSteps = async () => {
    const [pipelineSteps] = await setPipelineDefaultSteps(defaultOptions);

    if (pipelineSteps?.length) {
      setSelectedSteps([...pipelineSteps]);
    }
    routersHistory.replace({ ...routersHistory.location, state: undefined });
  };

  useInterval(
    async () => {
      await getOptimizationStatus();
    },
    isOptimizationRunning ? 5000 : null,
  );

  useEffect(() => {
    // async funtions start
    const loadData = async () => {
      if (!pipelineData?.uuid || pipelineData?.uuid !== pipelineUUID) {
        await loadPipeline(projectUUID, pipelineUUID);
      }

      if (_.isEmpty(pipelineHierarchyRules)) {
        await loadPipelinesHierarchyRules();
      }
      setPipelineSteps();
    };
    const startIfRunning = async () => {
      const isRunning = await loadPipelineResults(
        projectUUID,
        pipelineUUID,
        selectedQueryStepData?.label_column,
      );
      if (isRunning) {
        startOptimizationChecker();
      } else {
        loadPipelineBuilderData(projectUUID, pipelineUUID);
      }
      return isRunning;
    };
    // async funtions end

    if (pipelineUUID && selectedPipeline !== pipelineUUID) {
      setSelectedPipeline(pipelineUUID);
    }

    loadData();
    startIfRunning();
  }, [pipelineHierarchyRules, pipelineUUID]);

  useEffect(() => {
    if (selectedQueryStepData?.uuid) {
      loadQueryCacheStatus(projectUUID, selectedQueryStepData.uuid);
    }
  }, [selectedQueryStepData]);

  useEffect(async () => {
    const queryStep = selectedSteps.find((step) => step.type === PIPELINE_STEP_TYPES.QUERY);

    if (queryStep && queryStep?.customName !== selectedQueryStepData?.name) {
      clearQueryCacheStatus();
      setSelectedQueryStepData(getQueryData(queryStep?.customName));
    }
    if (queryStep?.options?.descriptionParameters?.uuid) {
      const { uuid, name } = queryStep?.options?.descriptionParameters;
      const data = await loadQueryStatistic(projectUUID, uuid);
      setQueryStatistic({ ...data, uuid, name });
    }
  }, [selectedSteps]);

  useEffect(() => {
    const isEmptySteps = Boolean(selectedSteps.find((step) => !step.data));
    if (isEmptySteps !== isPipelineHasEmptySteps) {
      setIsPipelineHasEmptySteps(isEmptySteps);
    }
  }, [selectedSteps]);

  useEffect(() => {
    if (pipelineRunningStatus === RUNNING_STATUSES.COMPLETED) {
      setResultMode(RESULT_MODES.SUMMARY);
    } else if (isOptimizationRunning) {
      setResultMode(RESULT_MODES.LOGS);
    }
  }, [pipelineRunningStatus, isOptimizationRunning]);

  const handleScroll = (toTop) => {
    window.scrollTo({
      left: 0,
      top: toTop,
      behavior: "smooth",
    });
  };

  const handleChangePipeline = async () => {
    routersHistory.push(
      generatePath(ROUTES.MAIN.MODEL_BUILD.child.SELECT_SCREEN.path, { projectUUID }),
    );
  };

  const handleCloseAlertBuilder = () => {
    clearAlertBuilder();
  };

  const handleChangeResultMode = (_name, newVal) => {
    setResultMode(newVal);
  };

  const handleSetPipeline = async (updatedSteps) => {
    let errorMessage = "";
    setPipelineAlert({});
    try {
      await setPipelineStep(selectedPipeline, updatedSteps);
    } catch (err) {
      handleScroll(scrollTop);
      setPipelineAlert({ message: err.message, type: "error" });
      errorMessage = err.message;
    }
    clearPipelineStatus();
    clearPipelineResult();
    return errorMessage;
  };

  const handleCreateNewStep = (index, newStepData) => {
    const newSelectedSteps = selectedSteps.map((el) => el); // copy
    const id = getUniqueId();
    newSelectedSteps.splice(index, 0, { ...newStepData, mandatory: false, id });
    setSelectedSteps(newSelectedSteps);
    handleSetPipeline(newSelectedSteps);
    return id;
  };

  const handleDeleteStep = (stepData) => {
    const deletedStepIndex = selectedSteps.findIndex((step) => step.id === stepData.id);
    const updatedSelectedSteps = [...selectedSteps]; // copy

    updatedSelectedSteps.splice(deletedStepIndex, 1);
    setSelectedSteps([...updatedSelectedSteps]);
    handleSetPipeline([...updatedSelectedSteps]);
  };

  const handleEditStep = async (stepData) => {
    const editingStepIndex = selectedSteps.findIndex((step) => step.id === stepData.id);
    let updatedSelectedSteps = [...selectedSteps]; // copy

    if (stepData.type === PIPELINE_STEP_TYPES.QUERY) {
      // if query is change we should check session default step
      updatedSelectedSteps = await updatePipelineStepsWithQuery(stepData);
    }
    updatedSelectedSteps[editingStepIndex] = { ...stepData };
    setSelectedSteps(updatedSelectedSteps);
    const errorMessage = handleSetPipeline([...updatedSelectedSteps]);
    return errorMessage;
  };

  const handleEditPipelineSettings = (pipelineSettingsStep) => {
    handleSetPipeline(selectedSteps, pipelineSettingsStep);
  };

  const handleKillLaunchOptimize = async () => {
    await stopModelOptimization(projectUUID, pipelineUUID);
    setIsOptimizationRunning(false);
  };

  const handleBuildQueryCache = (queryUUID) => {
    buildQueryCache(projectUUID, queryUUID);
  };

  const handleDismissQueryCache = (queryUUID) => {
    setDismissedCacheQueryList((value) => {
      return [...value, queryUUID];
    });
  };

  const handleLaunchOptimize = async () => {
    setIsOptimizationRunning(true); // prevent double click
    const err = await handleSetPipeline(
      selectedSteps.filter(
        (step) => !["Classifier", "Training Algorithm", "Validation Method"].includes(step?.type),
      ),
    );

    if (!err) {
      try {
        setResultMode(RESULT_MODES.SUMMARY);
        await launchModelOptimization(selectedSteps, {}, "pipeline");
        startOptimizationChecker();
        // Query cache will be built with model
        handleDismissQueryCache(selectedQueryStepData?.uuid);
      } catch (error) {
        setIsOptimizationRunning(false);
        showMessageSnackbar("error", error.message);
      }
    }
  };

  return (
    <Box>
      <Box mb={2} className={classes.toptopPanelWrapperFixed}>
        <div className={classes.topPanelTopOverlap} />
        <Box className={classes.topPanelWrapper}>
          <BuilderPipelinePanel
            pipelineData={pipelineData}
            handleChangePipeline={handleChangePipeline}
            getIsReadyToOptimize={getIsReadyToOptimize}
            isOptimizationRunning={isOptimizationRunning}
            handleLaunchOptimize={handleLaunchOptimize}
            handleKillLaunchOptimize={handleKillLaunchOptimize}
            exportPipeline={exportPipeline}
            projectUUID={projectUUID}
            pipelineUUID={pipelineUUID}
          />
        </Box>
        <div className={classes.topPanelBottomOverlap} />
      </Box>
      <Grid container spacing={4}>
        <Grid item lg={5} md={6} xs={12} mt={10}>
          {getIsShowQueryCacheAlert() ? (
            <Box mb={1}>
              <QueryCacheAlertMessage
                isShowQueryCacheAlert={getIsShowQueryCacheAlert()}
                selectedQuery={selectedQueryStepData?.uuid}
                queryCacheStatusData={queryCacheStatusData}
                loadQuery={() => loadQueryCacheStatus(projectUUID, selectedQueryStepData?.uuid)}
                onBuildCache={handleBuildQueryCache}
                onDismiss={handleDismissQueryCache}
                isButtonsPanel
              />
            </Box>
          ) : null}
          <PipelineBuilderAlertMessage
            pipelineAlert={pipelineAlert}
            queryStatistic={queryStatistic}
            isPipelineHasEmptySteps={isPipelineHasEmptySteps}
            pipelineValidationError={pipelineValidationError}
          />
          <Box className={classes.builderWrapper}>
            <PipelineBuilderFeatureExtraction
              alertBuilder={alertBuilder}
              onCloseAlertBuilder={handleCloseAlertBuilder}
              selectedSteps={selectedSteps}
              pipelineUUID={pipelineUUID}
              projectUUID={projectUUID}
              allSteps={pipelineHierarchyRules}
              transforms={transforms}
              labelColors={selectLabelValuesColors(selectedQueryStepData?.label_column)}
              isOptimizationRunning={isOptimizationRunning}
              getPipelineStepDescription={getPipelineStepDescription}
              getPipelineStepDataClass={getPipelineStepDataClass}
              pipelineData={pipelineData}
              pipelineStatus={pipelineStatus}
              onCreateNewStep={handleCreateNewStep}
              onDeleteStep={handleDeleteStep}
              onEditStep={handleEditStep}
              onEditPipelineSettings={handleEditPipelineSettings}
              downloadPipelineStepCache={downloadPipelineStepCache}
              getPipelineStepFeatureStats={getPipelineStepFeatureStats}
              classMap={pipelineResults.classMap}
              selectLabelValuesColors={selectLabelValuesColors}
              selectLabelValuesByName={selectLabelValuesByName}
            />
          </Box>
        </Grid>
        <Grid item lg={7} md={6} xs={12} mt={10} ref={chartGridRef}>
          <Box style={{ width: "100%" }}>
            <Sticky top={150}>
              <Box mb={1}>
                <Paper elevation={0}>
                  <Tabs
                    variant="fullWidth"
                    value={resultMode}
                    onChange={handleChangeResultMode}
                    indicatorColor="primary"
                    textColor="primary"
                    scrollButtons="auto"
                    aria-label="scrollable auto tabs"
                  >
                    <Tab label={"Feature Graph"} />
                    <Tab label={"Feature Summary"} />
                    <Tab
                      label={
                        <Box className={classes.tabWithCircularProgress}>
                          <div>{t("model-builder.tab-result-label-logs")}</div>
                          {pipelineRunningStatus ? (
                            <StatusRunningIcon status={pipelineRunningStatus} />
                          ) : null}
                        </Box>
                      }
                    />
                  </Tabs>
                </Paper>
              </Box>
              {resultMode === RESULT_MODES.LOGS ? (
                <ConsoleView>
                  <>
                    <ConsoleInformation
                      consoleInfoChild={
                        <>
                          <StatusRunningIcon status={pipelineRunningStatus} />
                          <ConsoleRunningStatusText
                            className={classes.ml1}
                            status={pipelineRunningStatus}
                          >
                            {pipelineRunningStatus}
                          </ConsoleRunningStatusText>
                        </>
                      }
                    />
                    <ConsoleBodySimpleView logs={optimizationLogs} />
                  </>
                </ConsoleView>
              ) : resultMode === RESULT_MODES.SUMMARY ? (
                <FeatureSummary
                  featureSummary={pipelineResults.featureSummary}
                  featureStatistics={pipelineResults.featureStatistics}
                  classMap={pipelineResults.classMap}
                  isFetching={pipelineResultsIsFetching}
                />
              ) : !_.isEmpty(pipelineResults.featureVectorData) ? (
                <FeatureVectorChart
                  features={pipelineResults.features}
                  featureVectorData={pipelineResults.featureVectorData}
                  parentRef={chartGridRef}
                  labelColumn={selectedQueryStepData?.label_column}
                  classes={pipelineResults.labelValues || []}
                  selectLabelColorHashMap={selectLabelValuesColors}
                  isFetchingFeatureVectorData={pipelineResultsIsFetching}
                  movelClassesDown
                />
              ) : (
                <UIPaperNoContent text={t("model-builder.feature-extractor-chart-no-data")} />
              )}
            </Sticky>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TheFeatureExtractorScreen;
