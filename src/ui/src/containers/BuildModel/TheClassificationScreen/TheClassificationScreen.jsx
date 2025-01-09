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
import { UITablePanel } from "components/UIPanels";

import { getUniqueId } from "utils";
import { useInterval, useMainContext } from "hooks";

import { ROUTES } from "routers";
import { RUNNING_STATUSES } from "consts";
import { EXECUTION_TYPES, PIPELINE_STEP_TYPES } from "store/autoML/const";

import PipelineBuilderClassification from "../componets/PipelineBuilderClassification";
import TableAutoSenseMetrics from "../componets/TableAutoSenseMetrics";
import TableIterationMetrics from "../componets/TableIterationMetrics";
import QueryCacheAlertMessage from "../componets/QueryCacheAlertMessage";
import PipelineBuilderAlertMessage from "../componets/PipelineBuilderAlertMessage";
import BuilderPipelinePanel from "../componets/BuilderPipelinePanel";

import useStyles from "../BuildModeStyle";

const RESULT_MODES = {
  RESULT: 0,
  LOGS: 1,
  TRAINING_SUMMARY: 2,
};

const TheClassificationScreen = ({
  isAutoML,
  alertBuilder,
  pipelineValidationError,
  defaultOptions,
  pipelineHierarchyRules,
  iterationMetrics,
  transforms,
  selectedPipeline,
  pipelineData,
  selectedProjectObj,
  navBarIsOpen,

  getQueryData,
  getPipelineStepDataClass,
  getPipelineStepDescription,
  selectLabelValuesColors,
  selectLabelValuesByName,

  optimizationLogs,
  pipelineRunningStatus,
  pipelineStatus,
  pipelineExecutionType,
  pipelineResultData,
  pipelineResults,
  queryCacheStatusData,

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
  onShowInformation,
}) => {
  const routersHistory = useHistory();
  const scrollTop = useRef();
  const classes = useStyles(navBarIsOpen);

  const { t } = useTranslation("models");
  const { projectUUID, pipelineUUID } = useParams();
  const { showMessageSnackbar } = useMainContext();

  const [selectedSteps, setSelectedSteps] = useState([]);
  const [pipelineSettings, setPipelineSettings] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [selectedQueryStepData, setSelectedQueryStepData] = useState({});
  const [dismissedCacheQueryList, setDismissedCacheQueryList] = useState([]);
  const [isOptimizationRunning, setIsOptimizationRunning] = useState(false);

  const [resultMode, setResultMode] = useState(RESULT_MODES.RESULT);

  const [isPipelineHasEmptySteps, setIsPipelineHasEmptySteps] = useState(false);
  const [pipelineAlert, setPipelineAlert] = useState({});

  const [queryStatistic, setQueryStatistic] = useState({});

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
    const [pipelineSteps, _pipelineSettings] = await setPipelineDefaultSteps(defaultOptions);
    setPipelineSettings(_pipelineSettings);
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
        routersHistory.push(
          generatePath(ROUTES.MAIN.MODEL_BUILD.child[pipelineExecutionType].path, {
            projectUUID,
            pipelineUUID,
          }),
        );
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
  }, [isAutoML, pipelineHierarchyRules, pipelineUUID]);

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
      setResultMode(RESULT_MODES.RESULT);
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

  const handleSetPipeline = async (updatedSteps, _pipelineSettings = pipelineSettings) => {
    let errorMessage = "";
    setPipelineAlert({});
    try {
      await setPipelineStep(selectedPipeline, updatedSteps, _pipelineSettings, isAutoML);
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
    const editedStepIndex = selectedSteps.findIndex((step) => step.id === stepData.id);
    let updatedSelectedSteps = [...selectedSteps]; // copy

    if (stepData.type === PIPELINE_STEP_TYPES.QUERY) {
      // if query is change we should check session default step
      updatedSelectedSteps = await updatePipelineStepsWithQuery(stepData);
    }

    if (stepData.type === PIPELINE_STEP_TYPES.CLASSIFIER) {
      // clean TrainingAlgorithm step when classifier is changing
      const classifierStep = selectedSteps.find(
        (step) => step.type === PIPELINE_STEP_TYPES.CLASSIFIER,
      );
      const indexOfTrainingAlgorithm = updatedSelectedSteps.findIndex(
        (step) => step.type === PIPELINE_STEP_TYPES.TRAINING_ALGORITHM,
      );

      if (
        !_.isEqual(classifierStep.customName, stepData.customName) &&
        indexOfTrainingAlgorithm !== -1
      ) {
        updatedSelectedSteps[indexOfTrainingAlgorithm].data = null;
        updatedSelectedSteps[indexOfTrainingAlgorithm].customName = "";
      }
    }

    updatedSelectedSteps[editedStepIndex] = { ...stepData };
    setSelectedSteps(updatedSelectedSteps);
    handleSetPipeline([...updatedSelectedSteps]);
  };

  const handleEditPipelineSettings = (pipelineSettingsStep) => {
    handleSetPipeline(selectedSteps, pipelineSettingsStep);
    setPipelineSettings(pipelineSettingsStep);
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

  const handleLaunchOptimize = async (executionType) => {
    setIsOptimizationRunning(true); // prevent double click
    const err = await handleSetPipeline(selectedSteps);
    if (!err) {
      try {
        setResultMode(RESULT_MODES.LOGS);
        await launchModelOptimization(
          selectedSteps,
          pipelineSettings,
          executionType || EXECUTION_TYPES.AUTO_ML_V2,
          isAutoML,
        );
        // Query cache will be built with model
        handleDismissQueryCache(selectedQueryStepData?.uuid);
        startOptimizationChecker();
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
            title={
              isAutoML
                ? t("model-builder.pipeline-panel-header-automl")
                : t("model-builder.pipeline-panel-header-custom")
            }
            onShowInformation={() => {
              onShowInformation(
                isAutoML
                  ? t("model-builder.pipeline-panel-header-automl")
                  : t("model-builder.pipeline-panel-header-custom"),
                isAutoML
                  ? t("model-builder.pipeline-panel-automl-description")
                  : t("model-builder.pipeline-panel-custom-description"),
              );
            }}
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
            <PipelineBuilderClassification
              alertBuilder={alertBuilder}
              onCloseAlertBuilder={handleCloseAlertBuilder}
              selectedSteps={selectedSteps}
              pipelineSettings={pipelineSettings}
              pipelineUUID={pipelineUUID}
              projectUUID={projectUUID}
              allSteps={pipelineHierarchyRules}
              isAutoML={isAutoML}
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
        <Grid item lg={7} md={6} xs={12} mt={10}>
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
                    <Tab label={t("model-builder.tab-result-label-result")} />
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
                    <Tab
                      label={
                        <Box className={classes.tabWithCircularProgress}>
                          <div>{"Training Summary"}</div>
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
              ) : resultMode === RESULT_MODES.TRAINING_SUMMARY ? (
                <>
                  {isAutoML ? (
                    <>
                      <UITablePanel title={t("model-builder.automl-summary-table-title")} />
                      <TableIterationMetrics iterationMetrics={iterationMetrics} />
                    </>
                  ) : (
                    <UITablePanel title={t("model-builder.summary-table-title")} />
                  )}
                </>
              ) : (
                <>
                  <UITablePanel
                    title={
                      isAutoML
                        ? t("model-builder.automl-result-table-title")
                        : t("model-builder.result-table-title")
                    }
                  />
                  <TableAutoSenseMetrics
                    autosenseMetrics={pipelineResultData}
                    projectUUID={selectedProjectObj.uuid}
                    pipelineUUID={selectedPipeline}
                  />
                </>
              )}
            </Sticky>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TheClassificationScreen;
