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
import React, { useEffect, useState, useRef, useMemo } from "react";
import Sticky from "react-stickynode";
import { useHistory, useParams, generatePath } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Box, Grid, Paper, Tabs, Tab, Fade, Snackbar } from "@mui/material";
import Alert from "@mui/material/Alert";
import PlayArrowOutlinedIcon from "@mui/icons-material/PlayArrowOutlined";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import StopIcon from "@mui/icons-material/Stop";
import IosShareIcon from "@mui/icons-material/IosShare";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

import ControlPanel from "components/ControlPanel";
import PipelineExportMenu from "components/PipelineExportMenu";
import ToastMessage from "components/ToastMessage/ToastMessage";

import {
  ConsoleView,
  ConsoleBodySimpleView,
  ConsoleInformation,
  StatusRunningIcon,
  ConsoleRunningStatusText,
} from "components/LogsView";
import { UITablePanel } from "components/UIPanels";

import { UIButtonConvertibleToShort } from "components/UIButtons";

import { getUniqueId } from "utils";
import { useInterval, useWindowResize } from "hooks";
import { ROUTES } from "routers";
import { RUNNING_STATUSES, RESPONSIVE } from "consts";
import { EXECUTION_TYPES, PIPELINE_STEP_TYPES } from "store/autoML/const";

import { UISnackBar } from "components/UISnackBar";

import PipelineBuilderAutoML from "../componets/PipelineBuilderAutoML";
import TableAutoSenseMetrics from "../componets/TableAutoSenseMetrics";
import TableIterationMetrics from "../componets/TableIterationMetrics";
import QueryCacheAlertMessage from "../componets/QueryCacheAlertMessage";

import useStyles from "../BuildModeStyle";

const WINDOWS_SIZE_KEYS = ["window_size", "min_segment_length"];

const RESULT_MODES = {
  RESULT: 0,
  LOGS: 1,
  TRAINING_SUMMARY: 2,
};

const TheBuilderScreen = ({
  alertBuilder,
  pipelineValidationError,
  isAdvancedBuilding,
  defaultOptions,
  pipelineHierarchyRules,
  transforms,
  selectedPipeline,
  pipelineData,
  selectedProjectObj,
  autoMLParams,
  navBarIsOpen,
  getQueryData,
  getPipelineStepDataClass,
  getPipelineStepDescription,

  queryList,
  queryCacheStatusData,

  clearAlertBuilder,
  clearPipelineValidationError,

  loadPipelinesHierarchyRules,
  iterationMetrics,
  optimizationLogs,
  pipelineRunningStatus,
  pipelineStatus,
  pipelineResultData,
  labelColors,
  setIsAdvancedBuilding,
  clearOptimizationLogs,
  clearPipelineResults,
  clearPipelineStatus,
  setPipelineStep,
  setPipelineDefaultSteps,
  updatePipelineStepsWithQuery,
  launchModelOptimization,
  checkOptimizationStatus,
  loadPipelineBuilderData,
  loadDataAfterTraining,
  stopModelOptimization,
  loadPipelineResults,
  loadQueryCacheStatus,
  buildQueryCache,
  clearQueryCacheStatus,
  loadQueryStatistic,
  loadQuerySegmentStatistic,
  loadPipeline,
  clearPipeline,
  downloadPipelineStepCache,
  setSelectedPipeline,

  exportPipeline,
}) => {
  const { t } = useTranslation("models");
  const { t: tQueries } = useTranslation("queries");
  const scrollBottom = useRef();
  const scrollTop = useRef();
  const classes = useStyles(navBarIsOpen);
  const routersHistory = useHistory();
  const [isShortBtnText, setIsShortBtnText] = useState(false);
  const { projectUUID, pipelineUUID } = useParams();

  const [selectedSteps, setSelectedSteps] = useState([]);
  const [pipelineSettings, setPipelineSettings] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [selectedQueryStepData, setSelectedQueryStepData] = useState({});
  const [dismissedCacheQueryList, setDismissedCacheQueryList] = useState([]);
  const [isOptimizationRunning, setIsOptimizationRunning] = useState(false);

  const [resultMode, setResultMode] = useState(RESULT_MODES.RESULT);

  const [isPipelineHasNotFilledSteps, setIsPipelineHasNotFilledSteps] = useState(false);
  const [pipelineAlert, setPipelineAlert] = useState({});
  const [pipelineErrorMessage, setPipelineErrorMessage] = useState("");

  const [queryStatistic, setQueryStatistic] = useState({});
  const [querySegmentStatistic, setQuerySegmentStatistic] = useState({});
  const [segmenterWindowSize, setSegmenterWindowSize] = useState(-1);

  const [anchorExportMenu, setAnchorExportMenu] = useState(null);
  const isOpenExportMenu = Boolean(anchorExportMenu);

  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackBarMessage, setSnackBarMessage] = useState("");
  const [snackBarVariant, setSnackBarVariant] = useState("success");

  const getIsAutoMLMode = () => {
    // we use only automl
    return true;
  };

  const getOptimizationStatus = async () => {
    const isLaunching = await checkOptimizationStatus(selectedProjectObj.uuid, selectedPipeline);
    if (!isLaunching) {
      // clear setInterval hook
      setIsOptimizationRunning(false);
      loadDataAfterTraining(selectedProjectObj.uuid, selectedPipeline);
    }
  };

  const getIsHasNotFilledStep = () => {
    return Boolean(selectedSteps.find((step) => !step.data));
  };

  const getIsReadyToOptimize = () => {
    return !isPipelineHasNotFilledSteps && selectedPipeline && !_.isEmpty(pipelineData);
  };

  const getIsShowQueryCacheAlert = () => {
    return (
      !_.isUndefined(queryCacheStatusData.status) &&
      !queryCacheStatusData.status &&
      !dismissedCacheQueryList.includes(selectedQueryStepData?.uuid)
    );
  };

  const getSegementerWindowSize = () => {
    const segmenterStep = selectedSteps.find((step) => step.type === PIPELINE_STEP_TYPES.SEGMENTER);
    const entry = _.entries(segmenterStep?.data).find(([key, _value]) =>
      WINDOWS_SIZE_KEYS.includes(key),
    );
    return !_.isEmpty(entry) ? entry[1] : -1;
  };

  const startOptimizationChecker = () => {
    setIsOptimizationRunning(true);
  };

  const stopOptimizationChecker = () => {
    setIsOptimizationRunning(false);
    clearOptimizationLogs();
    clearPipelineResults();
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
  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < RESPONSIVE.WIDTH_FOR_SHORT_TEXT);
  });

  const alertMessage = useMemo(() => {
    if (pipelineValidationError) {
      setIsAdvancedBuilding(true);
      return { message: pipelineValidationError, type: "error" };
    }
    if (pipelineAlert?.message) {
      setIsAdvancedBuilding(true);
      return pipelineAlert;
    }
    if (isPipelineHasNotFilledSteps) {
      setIsAdvancedBuilding(true);
      return { message: t("model-builder.warning-if-not-filled"), type: "error" };
    }
    if (queryStatistic?.segments && _.isEmpty(_.keys(queryStatistic?.segments))) {
      return {
        message: (
          <>
            {tQueries("validation.no-segments", { queryName: queryStatistic?.name })}
            <Box mt={1}>{tQueries("help.unknow")}</Box>
          </>
        ),
        type: "warning",
      };
    }
    if (queryStatistic?.segments && _.keys(queryStatistic?.segments)?.length < 2) {
      return {
        message: (
          <>
            {tQueries("validation.not-enough-segments", {
              queryName: queryStatistic?.name,
              segments: _.keys(queryStatistic?.segments).join(", "),
            })}
            <Box mt={1}>{tQueries("help.unknow")}</Box>
          </>
        ),
        type: "warning",
      };
    }
    if (
      segmenterWindowSize !== -1 &&
      !_.isEmpty(querySegmentStatistic) &&
      !_.isEmpty(querySegmentStatistic["Segment Length"])
    ) {
      let message = "";
      if (
        _.isEmpty(
          querySegmentStatistic["Segment Length"].filter((val) => val >= segmenterWindowSize),
        )
      ) {
        message = tQueries("validation.too-large-window-size", {
          windowSize: segmenterWindowSize,
        });
      } else if (
        querySegmentStatistic["Segment Length"]?.length * 0.2 >
        querySegmentStatistic["Segment Length"].filter((val) => val >= segmenterWindowSize)?.length
      ) {
        // dataset loses 80% of labels
        message = tQueries("validation.possible-too-large-window-size", {
          windowSize: segmenterWindowSize,
        });
      }
      if (message) {
        return {
          message,
          type: "warning",
        };
      }
    }
    return {};
  }, [
    pipelineValidationError,
    pipelineAlert,
    isPipelineHasNotFilledSteps,
    queryStatistic,
    querySegmentStatistic,
    segmenterWindowSize,
  ]);

  const isAutoML = useMemo(() => {
    return !autoMLParams?.disable_automl;
  }, [autoMLParams]);

  useInterval(
    async () => {
      await getOptimizationStatus();
    },
    isOptimizationRunning ? 5000 : null,
  );

  useEffect(() => {
    return () => clearAlertBuilder();
  }, []);

  useEffect(() => {
    return () => clearPipeline();
  }, []);

  useEffect(() => {
    return () => clearPipelineValidationError();
  }, []);

  useEffect(() => {
    return () => clearQueryCacheStatus();
  }, []);

  useEffect(() => {
    return () => clearPipelineStatus();
  }, []);

  useEffect(() => {
    return stopOptimizationChecker();
  }, []);

  useEffect(() => {
    const loadData = async () => {
      await loadPipeline(projectUUID, pipelineUUID);
      if (_.isEmpty(pipelineHierarchyRules)) {
        await loadPipelinesHierarchyRules();
      }
      setPipelineSteps();
    };
    const startIfRunning = async () => {
      const isRunning = await loadPipelineResults(projectUUID, pipelineUUID);
      if (isRunning) {
        startOptimizationChecker();
      } else {
        loadPipelineBuilderData(projectUUID, pipelineUUID);
      }
      return isRunning;
    };
    loadData();
    startIfRunning();
    if (pipelineUUID && selectedPipeline !== pipelineUUID) {
      setSelectedPipeline(pipelineUUID);
    }
    return () => setIsOptimizationRunning(false);
  }, []);

  useEffect(() => {
    if (selectedQueryStepData?.uuid) {
      loadQueryCacheStatus(projectUUID, selectedQueryStepData.uuid);
    }
  }, [selectedQueryStepData]);

  const getQueryStatistic = async (uuid, name) => {
    const data = await loadQueryStatistic(projectUUID, uuid);

    setQueryStatistic({ ...data, uuid, name });
  };

  // eslint-disable-next-line no-unused-vars
  const getSegmentQueryStatistic = async (uuid, name) => {
    const dataSegment = await loadQuerySegmentStatistic(projectUUID, uuid);
    setQuerySegmentStatistic({ ...dataSegment, uuid, name });
  };

  useEffect(() => {
    const windowSize = getSegementerWindowSize();
    setSegmenterWindowSize(windowSize);

    const queryStep = selectedSteps.find((step) => step.type === PIPELINE_STEP_TYPES.QUERY);
    if (queryStep && queryStep?.customName !== selectedQueryStepData?.name) {
      clearQueryCacheStatus();
      setSelectedQueryStepData(getQueryData(queryStep?.customName));
    }
    if (queryStep?.options?.descriptionParameters?.uuid) {
      getQueryStatistic(
        queryStep?.options?.descriptionParameters?.uuid,
        queryStep?.options?.descriptionParameters?.name,
      );
      getSegmentQueryStatistic(
        queryStep?.options?.descriptionParameters?.uuid,
        queryStep?.options?.descriptionParameters?.name,
      );
    }
  }, [selectedSteps, queryList]);

  useEffect(() => {
    const isNotFilled = getIsHasNotFilledStep();
    if (isNotFilled && !isAdvancedBuilding) {
      // open advancedbuilding
      setIsAdvancedBuilding(isNotFilled);
    }
    if (isNotFilled !== isPipelineHasNotFilledSteps) {
      setIsPipelineHasNotFilledSteps(isNotFilled);
    }

    setIsAdvancedBuilding(true);
  }, [selectedSteps]);

  useEffect(() => {
    if (pipelineRunningStatus === RUNNING_STATUSES.COMPLETED) {
      setResultMode(RESULT_MODES.RESULT);
    } else if (isOptimizationRunning) {
      setResultMode(RESULT_MODES.LOGS);
    }
  }, [pipelineRunningStatus, isOptimizationRunning]);

  const openSnackBarWithMsg = (variant, message) => {
    setSnackBarMessage(message);
    setSnackBarVariant(variant);
    setOpenSnackbar(true);
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpenSnackbar(false);
  };

  const handleScroll = (toTop = scrollBottom.current.offsetTop) => {
    window.scrollTo({
      left: 0,
      top: toTop,
      behavior: "smooth",
    });
  };

  const handleChangePipeline = async () => {
    await setSelectedPipeline("");
    routersHistory.push(
      generatePath(ROUTES.MAIN.MODEL_BUILD.child.SELECT_SCREEN.path, { projectUUID }),
    );
  };

  const handleCloseAlertBuilder = () => {
    clearAlertBuilder();
  };

  const handleChangeIsAutoMLAdvanced = (_name, newVal) => {
    setIsAdvancedBuilding(newVal);
  };

  const handleChangeResultMode = (_name, newVal) => {
    setResultMode(newVal);
  };

  const handleSetPipeline = async (updatedSteps, _pipelineSettings = pipelineSettings) => {
    let errorMessage = "";
    setPipelineAlert({});
    try {
      await setPipelineStep(selectedPipeline, updatedSteps, _pipelineSettings);
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
      updatedSelectedSteps = await updatePipelineStepsWithQuery(stepData, getIsAutoMLMode());
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
    const errorMessage = handleSetPipeline([...updatedSelectedSteps]);
    return errorMessage;
  };

  const handleEditPipelineSettings = (pipelineSettingsStep) => {
    handleSetPipeline(selectedSteps, pipelineSettingsStep);
    setPipelineSettings(pipelineSettingsStep);
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
        );
        startOptimizationChecker();
      } catch (error) {
        setIsOptimizationRunning(false);
        setPipelineErrorMessage(error.message);
      }
    }
  };

  const handleKillLaunchOptimize = async () => {
    await stopModelOptimization();
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

  const handleExportPipeline = async (downloadType) => {
    try {
      await exportPipeline(projectUUID, pipelineUUID, downloadType);
    } catch (error) {
      openSnackBarWithMsg("error", error.message);
    }
  };

  const handleCloseExportMenu = () => {
    setAnchorExportMenu(null);
  };

  return (
    <Box className={classes.root}>
      <Box mb={2} className={classes.toptopPanelWrapperFixed}>
        <div className={classes.topPanelTopOverlap} />
        <Box className={classes.topPanelWrapper}>
          <ControlPanel
            title={
              isShortBtnText
                ? pipelineData.name
                : t("model-builder.pipeline-panel-header", {
                    pipelineName: pipelineData.name,
                  })
            }
            turncateLenght={
              isShortBtnText
                ? RESPONSIVE.TRUNCATE_NAME_OVER_SHORT_TEXT
                : RESPONSIVE.TRUNCATE_NAME_OVER
            }
            onClickBack={isShortBtnText ? null : handleChangePipeline}
            actionsBtns={
              <>
                <UIButtonConvertibleToShort
                  variant={"contained"}
                  color={"primary"}
                  disabled={!getIsReadyToOptimize() || isOptimizationRunning}
                  onClick={() => handleLaunchOptimize(EXECUTION_TYPES.AUTO_ML_V2)}
                  isShort={isShortBtnText}
                  tooltip={t("model-builder.pipeline-panel-btn-start-tooltip")}
                  text={t("model-builder.pipeline-panel-btn-start")}
                  icon={<PlayArrowOutlinedIcon />}
                />
                <UIButtonConvertibleToShort
                  variant={"outlined"}
                  color={"primary"}
                  disabled={false}
                  onClick={() => handleKillLaunchOptimize()}
                  isShort={isShortBtnText}
                  tooltip={t("model-builder.pipeline-panel-btn-stop-tooltip")}
                  text={t("model-builder.pipeline-panel-btn-stop")}
                  icon={<StopIcon />}
                />

                <UIButtonConvertibleToShort
                  color="primary"
                  variant={"outlined"}
                  onClick={(e) => setAnchorExportMenu(e.currentTarget)}
                  isShort={isShortBtnText}
                  icon={<IosShareIcon />}
                  endIcon={<ArrowDropDownIcon />}
                  tooltip={t("model-builder.pipeline-panel-btn-export-tooltip")}
                  text={t("Export")}
                />
                <UIButtonConvertibleToShort
                  variant={"outlined"}
                  color={"primary"}
                  disabled={false}
                  onClick={() => handleChangePipeline()}
                  isShort={isShortBtnText}
                  tooltip={"Switch pipelines"}
                  text={t("model-builder.pipeline-panel-btn-change")}
                  icon={<ArrowBackIcon />}
                />
              </>
            }
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
          {alertMessage.message ? (
            <Fade in={Boolean(alertMessage.message)}>
              <Box mb={1}>
                <Alert variant="outlined" severity={alertMessage.type}>
                  {alertMessage.message}
                </Alert>
              </Box>
            </Fade>
          ) : null}
          <Box className={classes.builderWrapper}>
            <PipelineBuilderAutoML
              alertBuilder={alertBuilder}
              onCloseAlertBuilder={handleCloseAlertBuilder}
              isCollapsed={!isAdvancedBuilding}
              selectedSteps={selectedSteps}
              pipelineSettings={pipelineSettings}
              pipelineUUID={pipelineUUID}
              projectUUID={projectUUID}
              allSteps={pipelineHierarchyRules}
              isAutoML={true}
              transforms={transforms}
              isOptimizationRunning={isOptimizationRunning}
              getPipelineStepDescription={getPipelineStepDescription}
              pipelineData={pipelineData}
              pipelineStatus={pipelineStatus}
              labelColors={labelColors}
              onCreateNewStep={handleCreateNewStep}
              onDeleteStep={handleDeleteStep}
              onEditStep={handleEditStep}
              onEditPipelineSettings={handleEditPipelineSettings}
              getPipelineStepDataClass={getPipelineStepDataClass}
              handleChangeIsAutoMLAdvanced={handleChangeIsAutoMLAdvanced}
              downloadPipelineStepCache={downloadPipelineStepCache}
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

      <UISnackBar
        isOpen={Boolean(pipelineErrorMessage)}
        onClose={() => setPipelineErrorMessage("")}
        message={pipelineErrorMessage}
        variant={"error"}
        autoHideDuration={5000}
      />
      <Snackbar
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        open={openSnackbar}
        autoHideDuration={2000}
        onClose={handleCloseSnackbar}
      >
        <ToastMessage
          onClose={handleCloseSnackbar}
          variant={snackBarVariant}
          message={snackBarMessage}
        />
      </Snackbar>
      <PipelineExportMenu
        archorEl={anchorExportMenu}
        isOpen={isOpenExportMenu}
        onClose={handleCloseExportMenu}
        onDownloadPipeline={handleExportPipeline}
      />
    </Box>
  );
};

export default TheBuilderScreen;
