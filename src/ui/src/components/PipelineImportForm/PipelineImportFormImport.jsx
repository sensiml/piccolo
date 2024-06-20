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

import React, { useState } from "react";
import _ from "lodash";

import Alert from "@mui/material/Alert";
import { Button, Box, Zoom } from "@mui/material";
import { useTranslation } from "react-i18next";

import PipelineImportValidator from "store/containerBuildModel/domain/PipelineImportValidator";
import UIRenderParameters from "components/UIRenderParameters";
import UploadFileJson from "components/FormElements/UploadFileJson";

import useStyles from "./PipelineImportStyles";

const PipelineImportFormImport = ({ onSubmit }) => {
  const { t } = useTranslation("pipelines");
  const classes = useStyles();

  const [validationError, setValidationError] = useState("");
  const [pipelineJson, setPipelineJson] = useState({});
  const [pipelineParams, setPipelineParams] = useState({});

  const handleSubmit = () => {
    if (_.isEmpty(pipelineJson)) {
      setValidationError(t("form-import.error-required-json"));
    } else {
      onSubmit(pipelineJson, pipelineParams);
    }
  };

  const resetState = () => {
    setPipelineJson({});
    setPipelineParams({});
    setValidationError("");
  };

  const parseUploadedJson = (uploadedJson = {}) => {
    if (uploadedJson.pipeline && _.isArray(uploadedJson.pipeline)) {
      return { pipeline: uploadedJson.pipeline, hyper_params: uploadedJson.hyper_params };
    }
    if (_.isArray(uploadedJson)) {
      return { pipeline: [...uploadedJson] };
    }
    return {};
  };

  const handleUploadPipelineJson = (uploadedJson) => {
    resetState();
    const parsedJson = parseUploadedJson(uploadedJson);
    if (_.isEmpty(parsedJson)) {
      setValidationError(t("form-import.error-validation-json"));
      return;
    }
    const validator = new PipelineImportValidator(parsedJson.pipeline);
    validator.validatePipeline();
    if (validator.isValidPipeline) {
      setPipelineJson(uploadedJson);
      setPipelineParams(validator.extractQueryInputData());
    } else {
      setValidationError(validator.validationErrorMessage);
    }
  };

  return (
    <Box className={classes.dialogFormContainer}>
      <Box>
        <Box xs={12} md={12} className={classes.builderDescriptionWrapper}>
          <Alert severity="info" height={"150px"} classes={{ root: classes.alertMessage }}>
            {t("form-import.from-import-alert-msg")}
          </Alert>
        </Box>
        <Zoom in={!_.isEmpty(pipelineParams)}>
          <Box className={classes.builderFormWrap}>
            <UIRenderParameters parameters={pipelineParams} />
          </Box>
        </Zoom>
        <Box className={classes.builderFormWrap}>
          <UploadFileJson onUpload={handleUploadPipelineJson} validationError={validationError} />
        </Box>
      </Box>
      <Box className={classes.builderFormWrapper}>
        <Button
          className={classes.submitBtn}
          color="primary"
          variant="contained"
          onClick={handleSubmit}
        >
          {t("form-import.import-btn")}
        </Button>
      </Box>
    </Box>
  );
};

export default PipelineImportFormImport;
