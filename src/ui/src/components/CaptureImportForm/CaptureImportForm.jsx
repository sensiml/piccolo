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

import React, { useState, useMemo, useEffect } from "react";
import _ from "lodash";
import Alert from "@mui/material/Alert";
import {
  Box,
  Button,
  Stepper,
  Step,
  StepLabel,
  Stack,
  Typography,
  List,
  ListItemIcon,
  ListItem,
  ListItemText,
} from "@mui/material";
import DoneAllOutlinedIcon from "@mui/icons-material/DoneAllOutlined";
import CloseOutlinedIcon from "@mui/icons-material/CloseOutlined";

import logger from "store/logger";
import CaptureMetadataForm from "components/CaptureMetadataForm";

import { useTranslation } from "react-i18next";
import { IconSpinneAutoRenew } from "components/UIIcons";
import { ElementLoader } from "components/UILoaders";

import useStyles from "./PipelineImportStyles";
import CaptureImportFormImport from "./CaptureImportFormImport";

const STEP_IMPORT = 0;
const STEP_FORM = 1;

const PipelineImportForm = ({
  projectUUID,
  queriesFormOptions,
  captureNames = [],
  loadCaptures,
  loadCapturesMetadata,
  loadDataAfterUpload,
  updateCapturesMetadata,
  updateCapture,
  onClose,
  onSubmitFile,
  getCaptureMetadataFormData,
  getCaptureConfigurationFormData,
  getSampleRate,
}) => {
  const { t } = useTranslation("components");

  const STEPS = [
    t("capture-form-import.step-header-import"),
    t("capture-form-import.step-header-metadata"),
  ];

  const classes = useStyles();

  const [activeStep, setActiveStep] = useState(STEP_IMPORT);
  const [isImportFormOpened, setIsImportFormOpened] = useState(true);
  const [isErrorFormOpened, setIsErrorFormOpened] = useState(false);

  const [updatedMetadataData, setUpdatedMetadataData] = useState({});
  const [updatedCaptureData, setUpdatedCaptureData] = useState({});

  const [captureMetadataFormData, setCaptureMetadataFormData] = useState([]);
  const [captureConfigurationFromData, setCaptureConfigurationFromData] = useState([]);

  const [uploadingCaptures, setUploadingCaptures] = useState([]);
  const [uploadedCaptureInfo, setUploadedCaptureInfo] = useState({});

  const [submitingCaptureName, setSubmitingCaptureName] = useState("");
  const [metadataFormErrors, setMetadataFormErrors] = useState([]);

  // to keep counter for log outside of state context
  let updatedAmountForLog = 0;
  let simpleRateForLog = null;

  const validUploadingCaptures = useMemo(() => {
    return uploadingCaptures.filter(([id]) => !uploadedCaptureInfo[id]?.error);
  }, [uploadingCaptures, uploadedCaptureInfo]);

  const handleOpenMetadata = () => {
    setCaptureMetadataFormData(getCaptureMetadataFormData());
    setCaptureConfigurationFromData(getCaptureConfigurationFormData());
    setActiveStep(STEP_FORM);
  };

  const handleImport = async (files) => {
    setIsImportFormOpened(false);
    setIsErrorFormOpened(false);
    let isSuccess = true;

    // eslint-disable-next-line no-restricted-syntax
    for (const [_id, file] of _.entries(files)) {
      const newCaptupre = { name: file.name };
      setUploadingCaptures((val) => [[_id, file.name], ...val]);
      try {
        // eslint-disable-next-line no-await-in-loop
        newCaptupre.uuid = await onSubmitFile(file.file, file.name);
        updatedAmountForLog += 1;
      } catch (error) {
        isSuccess = false;
        newCaptupre.error = error.message;
      }
      setUploadedCaptureInfo((val) => ({ ...val, [_id]: newCaptupre }));
    }

    if (isSuccess) {
      handleOpenMetadata();
    } else {
      setIsErrorFormOpened(true);
    }
    loadDataAfterUpload();
  };

  const handleEfforFormOpenImport = () => {
    setIsErrorFormOpened(false);
    setUploadingCaptures(validUploadingCaptures);
    setIsImportFormOpened(true);
  };

  const handleSubmitForm = async () => {
    const errorMessages = [];

    try {
      if (!_.isEmpty(updatedCaptureData)) {
        // eslint-disable-next-line no-restricted-syntax
        for (const [id] of uploadingCaptures) {
          setSubmitingCaptureName(uploadedCaptureInfo[id].name);
          // eslint-disable-next-line no-await-in-loop
          await updateCapture(projectUUID, uploadedCaptureInfo[id].uuid, updatedCaptureData);
        }
      }
    } catch (error) {
      errorMessages.push(`${"Sensor Configuration: "} ${error.message}`);
    }
    try {
      await updateCapturesMetadata(
        projectUUID,
        validUploadingCaptures.map(([id]) => uploadedCaptureInfo[id].uuid),
        updatedMetadataData,
      );
    } catch (error) {
      errorMessages.push(`${"Metadata: "} ${error.message}`);
    }
    if (_.isEmpty(errorMessages)) {
      loadCapturesMetadata(projectUUID);
      loadCaptures(projectUUID);
      onClose();
    } else {
      setMetadataFormErrors(errorMessages);
    }

    setSubmitingCaptureName("");
  };

  const handleUpdateMetadataField = (name, value) => {
    if (!_.isEmpty(metadataFormErrors)) {
      setMetadataFormErrors([]);
    }
    setUpdatedMetadataData((prevVal) => {
      return {
        ...prevVal,
        [name]: value,
      };
    });
  };

  const handleUpdateCaptureField = (name, value) => {
    if (!_.isEmpty(metadataFormErrors)) {
      setMetadataFormErrors([]);
    }
    simpleRateForLog = getSampleRate(value);
    setUpdatedCaptureData((prevVal) => {
      return {
        ...prevVal,
        [name]: value,
      };
    });
  };

  useEffect(() => {
    return () => {
      logger.logInfo("", "import_files", {
        number_of_files: updatedAmountForLog,
        sample_rate: simpleRateForLog,
        project_uuid: projectUUID,
      });
    };
  }, []);

  return (
    <Box className={classes.dialogFormContainer}>
      <Stepper
        classes={{ root: classes.importDialogStepperRoot }}
        alternativeLabel
        activeStep={activeStep}
      >
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      <Box className={classes.importFormWrapper}>
        {activeStep === STEP_IMPORT ? (
          <>
            <Box xs={12} md={12} className={classes.importFormDescriptionWrapper}>
              {isErrorFormOpened ? (
                // You can try to reupload them or finish importing with metadata form
                <Box width={"100%"}>
                  <Alert severity="warning" classes={{ root: classes.alertMessage }}>
                    {t("capture-form-import.alert-importing-error-form")}
                  </Alert>
                  <Stack mt={2} direction="row" justifyContent={"center"} gap={2}>
                    <Button onClick={handleEfforFormOpenImport} color="primary" variant="outlined">
                      {t("capture-form-import.btn-import-more-files")}
                    </Button>
                    <Button
                      onClick={handleOpenMetadata}
                      color="primary"
                      variant="outlined"
                      disabled={_.isEmpty(validUploadingCaptures)}
                    >
                      {t("capture-form-import.btn-import-open-metadata-form")}
                    </Button>
                  </Stack>
                </Box>
              ) : (
                <Alert severity="info" classes={{ root: classes.alertMessage }}>
                  {t("capture-form-import.help-text")}
                </Alert>
              )}
            </Box>
            {isImportFormOpened ? (
              <CaptureImportFormImport
                captureNames={captureNames}
                queriesFormOptions={queriesFormOptions}
                onSubmit={handleImport}
              />
            ) : null}
            {!_.isEmpty(uploadingCaptures) ? (
              <>
                {isImportFormOpened ? (
                  <Typography mt={2} variant="h3" color={"primary"}>
                    {t("capture-form-import.header-imported-files")}
                  </Typography>
                ) : null}
                <List dense>
                  {uploadingCaptures.map(([id, name]) => (
                    <ListItem key={`uploaded-capture-${name}`}>
                      <ListItemIcon>
                        {uploadedCaptureInfo[id]?.uuid ? (
                          <DoneAllOutlinedIcon color="success" />
                        ) : uploadedCaptureInfo[id]?.error ? (
                          <>
                            <CloseOutlinedIcon color="error" />
                          </>
                        ) : (
                          <IconSpinneAutoRenew color="primary" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <>
                            <Typography variant="subtitle1">{name}</Typography>
                            <Typography
                              variant="caption"
                              gutterBottom
                              color={"error"}
                              style={{ whiteSpace: "pre-wrap" }}
                            >
                              {uploadedCaptureInfo[id]?.error}
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </>
            ) : null}
          </>
        ) : (
          <Box className={classes.dialogFormContainer}>
            <Alert>{t("capture-form-import.alert-success-import", {})}</Alert>
            {!_.isEmpty(submitingCaptureName) ? (
              <ElementLoader
                isOpen
                type="TailSpin"
                message={t("captures-table.updating-message", { name: submitingCaptureName })}
              />
            ) : (
              <CaptureMetadataForm
                validationErrors={metadataFormErrors}
                captureMetadataFormData={captureMetadataFormData}
                captureConfigurationFromData={captureConfigurationFromData}
                onUpdateCaptureField={handleUpdateCaptureField}
                onUpdateMetadataField={handleUpdateMetadataField}
              />
            )}
            <Box className={classes.importFormWrapper}>
              <Button
                className={classes.submitBtn}
                color="primary"
                variant="contained"
                onClick={handleSubmitForm}
              >
                {t("capture-form-import.btn-submit")}
              </Button>
            </Box>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default PipelineImportForm;
