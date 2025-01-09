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

import React, { useState, useEffect, useCallback, useRef, useMemo } from "react";
import _ from "lodash";
import fileDownload from "js-file-download";
import { useTranslation } from "react-i18next";

import {
  Box,
  Button,
  Grid,
  Paper,
  LinearProgress,
  Typography,
  Snackbar,
  CircularProgress,
  Fade,
} from "@mui/material";

import { ASYNC_CECK_INTERVAL, SUPPORT_URL } from "config";
import ToastMessage from "components/ToastMessage";
import ErrorBoundary from "components/ErrorBoundary";
import ModelControlPanel from "components/ModelControlPanel";

import { AppLoader } from "components/UILoaders";

import { useMainContext, useReadFileText } from "hooks";

import infoFile from "i18n/locales/en/info-model-download.md";

import TargetDeviceOptions from "./components/TargetDeviceOptions";
import InfoClassOptions from "./components/InfoClassOptions";
import InfoCaptureConfiguration from "./components/InfoCaptureConfiguration";
import InfoApplication from "./components/InfoApplication";
import InfoProfilingSummary from "./components/InfoProfilingSummary";
import InfoPlatform from "./components/InfoPlatform";

import useStyles from "./DownloadModelStyles";

const PIPELINE_RUNNING_CODE = 409;

const defaultPlatformInformation = {
  description: "Platform to build libraries for ARM devices with ARM-GCC.",
  documentation:
    // eslint-disable-next-line max-len, max-len
    "https://sensiml.com/documentation/firmware/arm-cortex-generic/cortex-arm-generic-platforms.html",
  name: "ARM GCC Generic",
  platform_type: "compiler",
  manufacturer: "ARM",
};

const DownloadModel = ({
  platformList,
  isFetchingModelData,
  modelData,
  captureConfigurations,
  captures,
  selectedProjectId,
  downloadFormData,
  isLoadedDownloadFormData,
  submitDownloadRequest,
  deviceProfile,
  deviceProfileIsFetching,
  platformLogos,
  // actions
  loadDownloadLogs,
  checkDownloadRequestStatus,
  dispatchSetDownloadFormData,
  dispatchDeviceProfileUpdate,
  dispatchClearDeviceProfileInformation,
}) => {
  const targetDeviceOptionsdRef = useRef();

  let setTimerHandle = null;
  const classes = useStyles();
  const { t } = useTranslation("models");
  const { targetOptions, downloadFormat, dataSource, advSettings } = downloadFormData;
  const [isFirstLoading, setIsFirstLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [completed, setCompleted] = useState(0);
  const [downloadingMassageFailed, setDownloadingMassageFailed] = useState(null);
  const [selectedPlatformInformation, setSelectedPlatformInformation] = useState(
    defaultPlatformInformation,
  );
  const [downloadingCode, setDownloadingCode] = useState(0);
  const [snackBarMessage, setSnackBarMessage] = useState(null);
  const [snackBarVariant, setSnackBarVariant] = useState("success");

  const { showInformationWindow } = useMainContext();
  const screenInfoMd = useReadFileText(infoFile);

  const showMessage = (variant, message) => {
    setSnackBarVariant(variant);
    setSnackBarMessage(message);
  };

  // eslint-disable-next-line no-shadow
  const updateOptions = async (
    selectedOptions,
    selectedDownloadFormat,
    selectedDataSource,
    selectedAdvSettings,
    platformInformation,
  ) => {
    setSelectedPlatformInformation(platformInformation);
    if (
      !_.isEmpty(selectedOptions) &&
      (targetOptions?.target_processor?.uuid !== selectedOptions.target_processor?.uuid ||
        targetOptions?.hardware_accelerator !== selectedOptions.hardware_accelerator ||
        isFirstLoading)
    ) {
      dispatchDeviceProfileUpdate(
        selectedProjectId,
        modelData.uuid,
        selectedOptions.target_processor,
        selectedOptions.hardware_accelerator,
      );
    }
    await dispatchSetDownloadFormData(selectedProjectId, {
      targetOptions: selectedOptions,
      downloadFormat: selectedDownloadFormat,
      dataSource: selectedDataSource,
      advSettings: selectedAdvSettings,
    });
  };

  const clearDeviceProfileInformation = () => {
    dispatchClearDeviceProfileInformation();
  };

  const getKbDescription = () => {
    let results = {};
    if (!modelData) {
      return {};
    }

    // clear name and leave only word character \w+ splitted by _ with uppercase transform
    const updatedModelName = _.toUpper(_.snakeCase(modelData.name));

    if (modelData.knowledgepack_description) {
      results = { ...modelData.knowledgepack_description }; // copy knowledgepack_description
      Object.entries(modelData.knowledgepack_description).forEach(([key, value]) => {
        if (!value?.parent) {
          // only children obj has "parent" key, for parent we change source
          results[key].source = dataSource;
        }
      });
      return results;
    }

    Object.keys(modelData?.class_map || {}).forEach((key) => {
      results[key] = "Report";
    });

    return {
      [updatedModelName]: {
        uuid: modelData.uuid,
        results,
        source: dataSource,
      },
    };
  };

  const getCurrenctApplicationInfo = useCallback(() => {
    const selectedProject = platformList.find((el) => el?.uuid === targetOptions?.target_platform);
    if (!selectedProject) {
      return {};
    }
    return selectedProject?.applications[targetOptions?.application];
  }, [targetOptions, platformList]);

  const getIsReadyToDownload = () => {
    return selectedProjectId && modelData.sandbox_uuid && modelData.uuid;
  };

  useEffect(() => {
    return clearDeviceProfileInformation();
  }, []);

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackBarMessage(null);
  };

  const handleDownloadLogs = async () => {
    const response = await loadDownloadLogs(modelData.uuid);
    if (response?.errorMessage) {
      showMessage("warning", response?.errorMessage);
    }
  };

  const handleCloseDownloadingMassageFailed = () => {
    setDownloadingMassageFailed(null);
  };

  const incrementProgressBar = () => {
    setCompleted((oldCompleted) => {
      if (oldCompleted === 100) {
        return 0;
      }
      const diff = Math.random() * 5;
      return Math.min(oldCompleted + diff, 100);
    });
  };
  const startDownloadStatusCheck = () => {
    setDownloading(true);
    incrementProgressBar();
    // eslint-disable-next-line no-use-before-define
    setTimerHandle = setTimeout(checkDownloadStatus, ASYNC_CECK_INTERVAL);
  };

  const stopDownloadStatusCheck = (restart) => {
    if (setTimerHandle) {
      clearInterval(setTimerHandle);
    }
    setDownloading(false);
    if (!restart) {
      setCompleted(0);
    }
  };

  const handleDownloadRequest = async () => {
    setDownloading(true);
    try {
      const response = await submitDownloadRequest(
        selectedProjectId,
        modelData.sandbox_uuid,
        modelData.uuid,
        downloadFormat,
        {
          ...targetOptions,
          kb_description: JSON.stringify(getKbDescription()),
          ...advSettings,
        },
      );
      if (response && response.error) {
        setDownloadingMassageFailed(t("download.error-download-w-err", { error: response.error }));
        setDownloadingCode(response?.code);
        stopDownloadStatusCheck();
      } else {
        startDownloadStatusCheck();
      }
    } catch (error) {
      setDownloadingMassageFailed(t("download.error-download-failed"));
      setDownloadingCode(500);
      stopDownloadStatusCheck();
    }
  };

  const checkDownloadStatus = async () => {
    const [SUCCESS, CANCELED] = ["SUCCESS", "CANCELED"];
    const response = await checkDownloadRequestStatus(
      selectedProjectId,
      modelData.sandbox_uuid,
      modelData.uuid,
      downloadFormat,
    );
    incrementProgressBar();
    if (response?.status === SUCCESS) {
      setCompleted(99);
      fileDownload(response.data, response.filename);
      stopDownloadStatusCheck();
      setCompleted(100);
      showMessage("success", t("download.success-dowload", { filename: response.filename }));
      setDownloadingCode(response?.code);
      stopDownloadStatusCheck();
    } else if (response.status === CANCELED) {
      setDownloadingCode(response?.code);
      stopDownloadStatusCheck();
    } else if (response.error) {
      setDownloadingMassageFailed(t("download.error-download-w-err", { error: response.error }));
      setDownloadingCode(response?.code);
      stopDownloadStatusCheck();
    } else {
      // restart ?
      stopDownloadStatusCheck(true);
      startDownloadStatusCheck();
    }
  };

  const isChangePlatform = useMemo(() => {
    if (targetDeviceOptionsdRef.current?.isSelectPlatform) {
      return targetDeviceOptionsdRef.current.isSelectPlatform();
    }
    return false;
  }, [selectedPlatformInformation, targetDeviceOptionsdRef]);

  return (
    <>
      <Box className={classes.root}>
        <Grid container className={classes.downloadWrapper} spacing={2}>
          <Grid item xs={12}>
            <ModelControlPanel
              modelData={modelData}
              isChangePlatform={isChangePlatform}
              onChangePlatform={() =>
                targetDeviceOptionsdRef.current.handleDeleteSelectedPlatform()
              }
              onShowInformation={() => showInformationWindow("Downloading Model", screenInfoMd)}
              downloading={downloading}
              handleDownloadRequest={handleDownloadRequest}
            />
          </Grid>
          <Grid item md={6} xs={12}>
            <Paper elevation={0} className={classes.cardWrapper}>
              {platformList && platformList.length && !(downloading || downloadingMassageFailed) ? (
                <Box className={classes.cardElementWrapper}>
                  <Box className={classes.downloadFormWrapper}>
                    {isLoadedDownloadFormData && !_.isEmpty(modelData) ? (
                      <ErrorBoundary>
                        <TargetDeviceOptions
                          platformList={platformList}
                          modelData={modelData}
                          captureConfigurations={captureConfigurations}
                          defaultTargetOptions={targetOptions || {}}
                          defaultDownloadFormat={downloadFormat || {}}
                          defaultDataSource={dataSource || {}}
                          defaultAdvSettings={advSettings || {}}
                          updateOptions={updateOptions}
                          captures={captures}
                          getIsReadyToDownload={getIsReadyToDownload}
                          handleDownloadRequest={handleDownloadRequest}
                          downloading={downloading}
                          platformLogos={platformLogos}
                          setIsFirstLoading={setIsFirstLoading}
                          ref={targetDeviceOptionsdRef}
                        />
                      </ErrorBoundary>
                    ) : null}
                  </Box>
                </Box>
              ) : downloading ? (
                <Box className={classes.progressbarWrapper}>
                  <Typography
                    className={classes.progressText}
                    variant={"subtitle2"}
                    color={"primary"}
                  >
                    {t("download.waiting-text")}
                  </Typography>
                  <LinearProgress
                    className={classes.progressbar}
                    variant="determinate"
                    value={completed}
                  />
                </Box>
              ) : downloadingMassageFailed ? (
                <Box className={classes.progressbarWrapper}>
                  <Typography
                    className={classes.progressTextWarning}
                    variant={"subtitle2"}
                    color={"error"}
                  >
                    {downloadingMassageFailed}
                  </Typography>
                  {downloadingCode !== PIPELINE_RUNNING_CODE ? (
                    <Grid
                      className={classes.errorButtonWrapper}
                      justifyContent="space-around"
                      container
                    >
                      <Button
                        variant="outlined"
                        onClick={() => handleDownloadLogs()}
                        color="primary"
                      >
                        {t("download.btn-download-logs")}
                      </Button>
                    </Grid>
                  ) : null}
                  <Grid
                    className={classes.errorButtonWrapper}
                    justifyContent="space-around"
                    container
                  >
                    <Button
                      className={classes.goBackBtn}
                      variant="outlined"
                      size="medium"
                      color="primary"
                      onClick={handleCloseDownloadingMassageFailed}
                    >
                      {t("download.go-back-loading-btn")}
                    </Button>
                    <Button
                      target="_blank"
                      href={SUPPORT_URL}
                      className={classes.goBackBtn}
                      variant="contained"
                      size="medium"
                      color="primary"
                    >
                      {t("download.go-back-loading-support")}
                    </Button>
                  </Grid>
                </Box>
              ) : (
                <CircularProgress />
              )}
            </Paper>
          </Grid>
          {!_.isEmpty(selectedPlatformInformation) ? (
            <Grid item container direction="row" alignContent="flex-start" md={6} xs={12}>
              <Grid item xs={12}>
                <Paper elevation={0} className={classes.cardWrapper}>
                  <Box className={classes.cardElementWrapper}>
                    {!_.isEmpty(selectedPlatformInformation) ? (
                      <Box>
                        <Typography variant="subtitle1" className={classes.formTitle}>
                          {"Platform"}
                        </Typography>
                        <InfoPlatform info={selectedPlatformInformation} />
                      </Box>
                    ) : (
                      <></>
                    )}
                  </Box>
                </Paper>
              </Grid>

              <Grid item xs={12} className={classes.mt2}>
                <Paper elevation={0} className={classes.cardWrapper}>
                  <Box className={classes.cardElementWrapper}>
                    <Box className={classes.downloadFormWrapper}>
                      <Box mb={2}>
                        <Typography variant="subtitle1" className={classes.formTitle}>
                          {t("info.class-map")}:
                        </Typography>
                        <Box className={classes.classMaps}>
                          {modelData?.class_map ? (
                            <InfoClassOptions modelData={modelData} classes={classes} />
                          ) : null}
                        </Box>
                      </Box>
                    </Box>
                    <Box className={classes.profileList}>
                      <Fade in={!deviceProfileIsFetching && !_.isEmpty(deviceProfile)}>
                        <div>
                          <Typography variant="subtitle1" className={classes.formTitle}>
                            {t("info.profile-header")}
                          </Typography>
                          <InfoProfilingSummary classes={classes} deviceProfile={deviceProfile} />
                        </div>
                      </Fade>
                    </Box>
                  </Box>
                </Paper>
              </Grid>

              <Grid item xs={12} className={classes.mt2}>
                <Paper elevation={0} className={classes.cardWrapper}>
                  <Box className={classes.cardElementWrapper}>
                    <Typography variant="h2" className={classes.header}>
                      {t("info.header-configuration")}
                    </Typography>
                    <Box mt={2}>
                      {captureConfigurations.filter((el) => el.uuid === dataSource)?.length ? (
                        <>
                          <Typography variant="subtitle1" className={classes.formTitle}>
                            {t("info.capture-header")}
                          </Typography>
                          <InfoCaptureConfiguration
                            captureConfigurations={captureConfigurations}
                            dataSource={dataSource}
                          />
                        </>
                      ) : (
                        <></>
                      )}
                    </Box>
                    <Box>
                      <Fade in={Boolean(targetOptions?.application)}>
                        <div>
                          <Typography variant="subtitle1" className={classes.formTitle}>
                            {t("info.app-header")}
                          </Typography>
                          <InfoApplication
                            name={targetOptions?.application}
                            info={getCurrenctApplicationInfo()}
                          />
                        </div>
                      </Fade>
                    </Box>
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <></>
          )}
        </Grid>

        <Snackbar
          anchorOrigin={{
            vertical: "top",
            horizontal: "right",
          }}
          open={snackBarMessage}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
        >
          <ToastMessage
            onClose={handleCloseSnackbar}
            variant={snackBarVariant}
            message={snackBarMessage}
          />
        </Snackbar>
      </Box>
      <AppLoader isOpen={isFetchingModelData} />
    </>
  );
};

export default DownloadModel;
