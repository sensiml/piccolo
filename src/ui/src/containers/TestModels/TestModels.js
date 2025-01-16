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

/* eslint-disable prettier/prettier */
/* eslint-disable indent */
/* eslint-disable array-callback-return */
/* eslint-disable no-restricted-syntax */
/* eslint-disable guard-for-in */
/* eslint-disable vars-on-top */
/* eslint-disable prefer-const */
/* eslint-disable no-var */
/* eslint-disable max-len */
/* eslint-disable no-use-before-define */
/* eslint-disable camelcase */
import React, { useState, useEffect, useRef } from "react";
import _ from "lodash";
import {
  Alert,
  AlertTitle,
  Box,
  FormControl,
  Grid,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Snackbar,
  Paper,
} from "@mui/material";

import ToastMessage from "components/ToastMessage";
import ProjectStatisticsTable from "components/ProjectStatisticsTable";
import ModelControlPanel from "components/ModelControlPanel";
import { AppLoader } from "components/UILoaders";

import { useMainContext, useReadFileText } from "hooks";

import infoFile from "i18n/locales/en/info-model-test.md";

import useStyles from "./TestModelsStyles";
import ClassificationResults from "./ClassificationResults";

const COMPUTE_FAILED = "Classification Run Failed.";
const TERMINATED_PIPELINE_STATUS = "Status: Pipeline was terminated.";
const COMPUTE_TERMINATED = "Classifier run was terminated.";

const COMPUTE_SUMMARY_SUCCEEDED = "Summary has been computed and displayed below.";
const COMPUTE_ACCURACY_SUCCEEDED = `Accuracy Computation completed, click on the "Results" button to view the results`;
const NO_DATA_FILES_SELECTED = "A Capture or Data File is required to compute summary.";
const RUN_STATUS = {
  STOPPED: "STOPPED",
  SUCCESS: "SUCCESS",
  ERROR: "ERROR",
};

const fileTypeNames = {
  CAPTURES: "Captures",
  FEATURE_FILES: "featurefile",
};
const status_message_type = {
  ERROR: "error",
  SUCCESS: "success",
  WARNING: "warning",
};

const TestModels = ({
  selectedProject,
  isFetchingModelData,
  modelData,
  sessions,
  classifierCache,
  submitClassifier,
  stopClassifierRun,
  checkClassifierRunStatus,
  loadCapturesStatistics,
}) => {
  let setTimerHandle = null;

  const resultRef = useRef();

  const [rerenderFlag, setRerenderFlag] = useState(true);
  // eslint-disable-next-line no-unused-vars
  const [fileType, setFileType] = useState(fileTypeNames.CAPTURES);
  const [selectedProjectId, setSelectedProjectId] = useState(selectedProject);

  const [model, setModel] = useState(modelData);
  const [classifierCacheSet, setClassifierCacheSet] = useState(classifierCache);
  const [computeSummary, setComputeSummary] = useState(false);

  const [summaryConfusionMatrix, setSummaryConfusionMatrix] = useState({});
  // const [capturesSelected, setCapturesSelected] = useState(null);
  const [classifierIsRunning, setClassifierIsRunning] = useState(false);
  const [classifierResults, setClassifierResults] = useState(null);
  const [showClassifierResults, setShowClassifierResults] = useState(false);
  const [selectedCaptureSets, setSelectedCaptureSets] = useState([]);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [stoppingRun, setStoppingRun] = useState(true);
  const [snackBarVariant, setSnackBarVariant] = useState("success");
  const [snackBarMessage, setSnackBarMessage] = useState("");
  const [completed, setCompleted] = React.useState(0);
  const [activeSession, setActiveSession] = React.useState("");
  const [sessionList, setSessionList] = React.useState("");
  const [modelClassMap, setModelClassMap] = useState([]);

  const { showInformationWindow } = useMainContext();
  const screenInfoMd = useReadFileText(infoFile);

  const handleSessionChange = (event) => {
    setActiveSession(event.target.value);
  };

  const stopStatusCheck = () => {
    if (setTimerHandle !== null) {
      clearInterval(setTimerHandle);
    }
  };

  const incrementProgressBar = () => {
    setCompleted((oldCompleted) => {
      if (oldCompleted === 100) {
        return 0;
      }
      const diff = Math.random() * 20;
      return Math.min(oldCompleted + diff, 100);
    });
  };

  const handleStopClassierRun = () => {
    setStoppingRun(true);
    stopClassifierRun(selectedProjectId, modelData?.sandbox_uuid, modelData?.uuid).then(
      (dispObj) => {
        if (dispObj.status === RUN_STATUS.STOPPED) {
          stopStatusCheck();
        } else if (dispObj.status === RUN_STATUS.ERROR) {
          showMessage(status_message_type.ERROR, dispObj.response);
          stopStatusCheck();
          setClassifierIsRunning(false);
        }
      },
    );
  };

  const getCacheKey = (pipelineId, modelId, fileId) => {
    const cachKey = `${pipelineId}-${modelId}-${fileId}`;
    return cachKey;
  };

  const handleComputeSummary = () => {
    setComputeSummary(true);
    classifyierRun(true);
  };

  const handleClassifierRun = () => {
    setComputeSummary(false);
    classifyierRun(false);
  };

  // const getCaptureResults = () => {
  //   return selectedCaptureSets.map(
  //     (selectedCapture) =>
  //       classifierCacheSet[
  //         getCacheKey(selectedPipelineId, selectedModelId, selectedCapture.uuid)
  //       ]
  //   );
  // };

  const classifyierRun = (showSummary) => {
    setStoppingRun(false);
    setCompleted(0);
    setShowClassifierResults(false);
    setClassifierIsRunning(true);
    setClassifierResults([]);
    if (!selectedCaptureSets || selectedCaptureSets.length === 0) {
      showMessage(status_message_type.ERROR, NO_DATA_FILES_SELECTED);
      setClassifierResults([]);
      setClassifierIsRunning(false);
    } else {
      const uncachedFiles = selectedCaptureSets.filter(
        (sc) => !classifierCacheSet[getCacheKey(modelData?.sandbox_uuid, modelData?.uuid, sc.uuid)],
      );
      if (!uncachedFiles || uncachedFiles.length === 0) {
        if (showSummary === true) {
          computeSummaryConfusionMatrix();
          showMessage(status_message_type.SUCCESS, "");
        }
        showResults([], showSummary);
        showMessage(
          status_message_type.SUCCESS,
          showSummary ? COMPUTE_SUMMARY_SUCCEEDED : COMPUTE_ACCURACY_SUCCEEDED,
        );
        return;
      }

      let kpDesc = null;
      if (model && model.knowledgepack_description && model.knowledgepack_description.Parent) {
        kpDesc = model.knowledgepack_description;
        delete kpDesc.Parent.source;
      }
      submitClassifier(
        selectedProjectId,
        modelData?.sandbox_uuid,
        modelData?.uuid,
        uncachedFiles,
        model && model.query_summary ? model.query_summary.label_column : null,
        kpDesc ? JSON.stringify(kpDesc) : null,
      );
      incrementProgressBar();
      setTimerHandle = setTimeout(
        checkClassifierStatus,
        process.env.REACT_APP_ASYNC_CHECK_INTERVAL,
      );
    }
  };

  const getResultFromcache = (fileUuid) => {
    return classifierCacheSet[getCacheKey(modelData?.sandbox_uuid, modelData?.uuid, fileUuid)];
  };

  const handleScroll = (scrollTo = resultRef.current.offsetTop) => {
    window.scrollTo({
      left: 0,
      top: scrollTo,
      behavior: "smooth",
    });
  };

  const showCaptureRunResult = (pipelineId, modelId, fileUuid) => {
    setComputeSummary(false);
    if (!fileUuid) return;

    const result = classifierCacheSet[getCacheKey(pipelineId, modelId, fileUuid)];

    if (result) {
      setClassifierResults([result]);
      setShowClassifierResults(true);
      showMessage(
        status_message_type.SUCCESS,
        `Test results for ${result.fileName} are displayed below.`,
      );
      handleScroll();
    } else {
      setShowClassifierResults(false);
    }
  };

  const checkClassifierStatus = () => {
    checkClassifierRunStatus(
      selectedProjectId,
      modelData?.sandbox_uuid,
      modelData?.uuid,
      selectedCaptureSets,
      activeSession,
    ).then((dispObj) => {
      if (dispObj) {
        incrementProgressBar();
        if (dispObj.status === RUN_STATUS.SUCCESS) {
          computeSummaryConfusionMatrix();
          showResults([], computeSummary);
          showMessage(
            status_message_type.SUCCESS,
            computeSummary ? COMPUTE_SUMMARY_SUCCEEDED : COMPUTE_ACCURACY_SUCCEEDED,
          );
        } else if (dispObj.status === RUN_STATUS.ERROR) {
          let errMsg = COMPUTE_FAILED;
          if (dispObj.response && dispObj.response.message) {
            errMsg = dispObj.response.message.includes(TERMINATED_PIPELINE_STATUS)
              ? COMPUTE_TERMINATED
              : dispObj.response.message;
          }
          showMessage(status_message_type.ERROR, errMsg);
          stopStatusCheck();
          setClassifierIsRunning(false);
        } else {
          setClassifierIsRunning(true);
          setTimerHandle = setTimeout(
            checkClassifierStatus,
            process.env.REACT_APP_ASYNC_CHECK_INTERVAL,
          );
        }
      }
    });
  };

  const computeSummaryConfusionMatrix = () => {
    const confusionMatrix = {};
    const captures = [];
    // eslint-disable-next-line array-callback-return
    selectedCaptureSets.map((sc) => {
      const cacheKey = getCacheKey(modelData?.sandbox_uuid, modelData?.uuid, sc.uuid);
      const scConfusionMatrix =
        classifierCacheSet[cacheKey] && activeSession
          ? classifierCacheSet[cacheKey].confusion_matrices[activeSession]
          : null;

      if (scConfusionMatrix) {
        captures.push(sc.uuid);
        Object.keys(scConfusionMatrix).map((k1) => {
          if (!confusionMatrix[k1]) confusionMatrix[k1] = {};
          Object.keys(scConfusionMatrix[k1]).map((k2) => {
            confusionMatrix[k1][k2] =
              (confusionMatrix[k1][k2] ? confusionMatrix[k1][k2] : 0) + scConfusionMatrix[k1][k2];
          });
        });
      }
    });
    // setCapturesSelected(captures);
    setSummaryConfusionMatrix(confusionMatrix);
  };

  const showResults = (results, displayResults) => {
    setRerenderFlag((prevState) => !prevState);
    setCompleted(99);
    setClassifierResults(results);
    setCompleted(100);
    stopStatusCheck();
    setClassifierIsRunning(false);
    setShowClassifierResults(displayResults);
  };

  useEffect(() => {
    setClassifierCacheSet(classifierCache);
  }, [classifierCache]);

  useEffect(() => {
    setSelectedProjectId(selectedProject);
    setShowClassifierResults(false);
    setClassifierResults(null);
  }, [selectedProject]);

  useEffect(() => {
    setModel(modelData);

    if (sessions) setSessionList(sessions);
    // modelClassMap
    if (modelData && modelData.class_map) {
      const cms = Object.values(modelData.class_map);
      if (modelData.child_models) {
        // TODO FIX THIS
        for (var index in modelData.child_models) {
          let childModelClasses = modelData.child_models[index].data.class_map;
          Object.keys(childModelClasses).forEach((key) => {
            if (!cms.includes(childModelClasses[key])) {
              cms.push(childModelClasses[key]);
            }
          });
        }
      }
      setModelClassMap(cms);
    }
    if (modelData && modelData.query_summary && sessions) {
      setActiveSession(
        (
          sessions.find((s) => s.id === modelData.query_summary.segmenter.id) || {
            name: "",
          }
        ).name,
      );
    }
  }, [modelData, sessions]);

  useEffect(() => {
    if (showCaptureRunResult) {
      handleScroll(resultRef.current.offsetTop);
    }
  }, [showClassifierResults]);

  const handleRowSelection = (event, row) => {
    updateCaptureSelection([row]);
  };

  const handleRowsSelection = (event, rows) => {
    updateCaptureSelection(rows);
  };

  const getFilteredCaptureSets = (selectedRows) => {
    return selectedRows.map(({ uuid, name }) => {
      if (selectedCaptureSets.findIndex((s) => s.uuid === uuid) === -1) {
        return fileType === fileTypeNames.CAPTURES
          ? { uuid, name, type: "capture" }
          : {
              uuid,
              name: checkForCsv(name),
              type: "featurefile",
            };
      }
      return {};
    });
  };

  const updateCaptureSelection = (rows) => {
    const selectedRows = rows.filter((row) => row.captureSelected === 1);

    const unSelectedUUIDs = rows.filter((row) => row.captureSelected === 0).map((row) => row.uuid);

    let unSelectedRowSet = selectedCaptureSets.filter(
      (s) => s !== undefined && !unSelectedUUIDs.includes(s.uuid),
    );

    let newRowSet = [...unSelectedRowSet, ...getFilteredCaptureSets(selectedRows)].filter(
      (x) => !_.isEmpty(x),
    );

    setSelectedCaptureSets(newRowSet);
  };

  const checkForCsv = (fileName) => {
    if (fileName) {
      // eslint-disable-next-line no-param-reassign
      fileName = fileName.trim();
      // eslint-disable-next-line no-param-reassign
      if (!fileName.endsWith(".csv")) fileName = `${fileName}.csv`;
    }
    return fileName;
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setOpenSnackbar(false);
  };

  const handleRefresh = () => {
    loadCapturesStatistics(selectedProject);
  };

  const showMessage = (variant, message) => {
    setSnackBarVariant(variant);
    setSnackBarMessage(message);
    setOpenSnackbar(true);
  };

  const classes = useStyles();
  return (
    <>
      <Box className={classes.box}>
        <Grid item xs={12}>
          <ModelControlPanel
            onShowInformation={() => showInformationWindow("Testing a Model", screenInfoMd)}
            modelData={modelData}
          />
        </Grid>
        <Paper elevation={0}>
          <Grid container className={classes.sessionWrapper} spacing={2}>
            <Grid item xs={12} md={6}>
              <Alert severity="info">
                <AlertTitle>
                  Evaluate your model by selecting one or more capture files for classification.
                </AlertTitle>
              </Alert>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth={true}>
                <>
                  <InputLabel htmlFor="session">Session</InputLabel>
                  <Select
                    label="Sessions"
                    name="session"
                    value={activeSession}
                    onChange={handleSessionChange}
                  >
                    <MenuItem key="" value="" disabled />
                    {sessionList &&
                      sessionList.map((s) => {
                        return (
                          <MenuItem key={s.id} value={s.name}>
                            {s.name}
                          </MenuItem>
                        );
                      })}
                  </Select>
                </>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>
        <Grid item xs>
          <Grid container className={classes.grid} spacing={0}>
            <Grid item xs={12}>
              <Grid container className={classes.testModelControlGrid} spacing={0}>
                {!_.isEmpty(modelData) ? (
                  <Grid item xs={12}>
                    {completed ? (
                      <LinearProgress
                        className={classes.progressbar}
                        variant="determinate"
                        value={completed}
                      />
                    ) : null}
                    {fileType === "Captures" ? (
                      <ProjectStatisticsTable
                        headerText="Captures"
                        reRender={rerenderFlag}
                        onRowSelectionAction={handleRowSelection}
                        onRowsSelectionAction={handleRowsSelection}
                        showResultsAction={showCaptureRunResult}
                        recognizingSignal={() => classifierIsRunning}
                        getResultFromcache={getResultFromcache}
                        selectedPipeline={modelData?.sandbox_uuid}
                        selectedModel={modelData?.uuid}
                        activeSession={activeSession}
                        isInTestModel={true}
                        onRefresh={handleRefresh}
                        handleClassifierRun={handleClassifierRun}
                        handleComputeSummary={handleComputeSummary}
                        handleStopClassierRun={handleStopClassierRun}
                        classiferIsRunning={classifierIsRunning}
                      />
                    ) : (
                      <div />
                      // <FeatureFilesTable
                      //  onRowSelectionAction={handleRowSelection}
                      // />
                    )}
                  </Grid>
                ) : null}
              </Grid>
              <Grid item xs>
                <Grid
                  container
                  direction="row"
                  justifyContent="flex-start"
                  alignContent="flex-start"
                >
                  <Grid item xs={12}>
                    <Snackbar
                      anchorOrigin={{
                        vertical: "top",
                        horizontal: "right",
                      }}
                      open={openSnackbar}
                      autoHideDuration={6000}
                      onClose={handleCloseSnackbar}
                    >
                      <ToastMessage
                        onClose={handleCloseSnackbar}
                        variant={snackBarVariant}
                        message={snackBarMessage}
                      />
                    </Snackbar>
                  </Grid>
                  <Grid ref={resultRef} item xs={12} className={classes.classifierResults}>
                    {showClassifierResults ? (
                      <ClassificationResults
                        classifierResults={classifierResults}
                        modelName={model ? model.name : ""}
                        classMap={modelClassMap}
                        featureSummary={model ? model.feature_summary : []}
                        activeSession={activeSession}
                        showSummary={computeSummary}
                        summaryConfusionMatrix={summaryConfusionMatrix}
                      />
                    ) : null}
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Box>
      <AppLoader isOpen={isFetchingModelData} />
    </>
  );
};

export default TestModels;
