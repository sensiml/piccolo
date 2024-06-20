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

/* eslint-disable no-unused-vars */
import React, { useState, useMemo } from "react";
import _ from "lodash";
import PropTypes from "prop-types";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import makeStyles from "@mui/styles/makeStyles";

import { Box, Button, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import UploadFileDnD from "./UploadFileDnD";

const useStyles = () =>
  makeStyles((theme) => ({
    uploadWrapper: {
      position: "relative",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "space-around",
      gap: theme.spacing(1),
    },
    errorMsg: {
      color: theme.palette.error.main,
    },
  }))();

const UploadFileJson = ({ onUpload, validationError }) => {
  const classes = useStyles();
  const { t } = useTranslation("forms");

  const [fileName, setFileName] = useState("");
  const [valueError, setValueError] = useState("");

  const errorMessage = useMemo(() => {
    return _.trim(`${validationError} ${valueError}`);
  }, [validationError, valueError]);

  const validateFile = (uploadedFile) => {
    if (uploadedFile?.type !== "application/json") {
      setValueError(t("upload-json.error-validation-type-json"));
      return false;
    }
    return true;
  };

  const handleUpload = (files) => {
    setValueError("");
    setFileName("");
    if (!files?.length) {
      return;
    }
    const uploadedFile = files[0];
    const reader = new FileReader();

    if (!validateFile(uploadedFile)) {
      return;
    }

    reader.readAsText(uploadedFile);

    reader.onload = () => {
      let jsonFile = {};
      try {
        jsonFile = JSON.parse(reader.result);
      } catch (e) {
        setValueError(t("upload-json.error-validation-invalid-json"));
      }
      if (!_.isEmpty(jsonFile)) {
        onUpload(jsonFile);
        setFileName(uploadedFile.name);
      }
    };

    reader.onerror = () => {
      setValueError(t("upload-json.error-reader"));
    };
  };

  const handleUploadButton = (e) => {
    const uploadedFiles = e.target.files;
    handleUpload(uploadedFiles);
  };

  const handleClear = (e) => {
    setValueError("");
    setFileName("");
  };

  return (
    <UploadFileDnD onDrop={handleUpload} isError={errorMessage}>
      <Box className={classes.uploadWrapper}>
        {fileName ? (
          <Box display={"flex"} alignItems={"center"}>
            <Typography color="primary">Imported {fileName}</Typography>
            <IconButton onClick={handleClear} size="large">
              <DeleteIcon color="primary" />
            </IconButton>
          </Box>
        ) : (
          <>
            <Button
              variant="outlined"
              color="primary"
              component="label"
              onChange={handleUploadButton}
            >
              {t("upload-json.btn-upload")}
              <input type="file" hidden />
            </Button>
            {t("upload-json.text-drag")}
          </>
        )}
        {errorMessage ? <Typography className={classes.errorMsg}>{errorMessage}</Typography> : null}
      </Box>
    </UploadFileDnD>
  );
};

UploadFileJson.propTypes = {
  onUpload: PropTypes.func.isRequired,
  validationError: PropTypes.string,
};

UploadFileJson.defaultProps = {
  validationError: "",
};

export default UploadFileJson;
