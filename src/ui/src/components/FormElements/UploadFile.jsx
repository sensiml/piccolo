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

import React, { useState, useMemo } from "react";
import _ from "lodash";
import PropTypes from "prop-types";

import { useTranslation } from "react-i18next";

import makeStyles from "@mui/styles/makeStyles";

import { Box, Button, Typography } from "@mui/material";

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
      whiteSpace: "pre-wrap",
    },
  }))();

const UploadFile = ({ onUpload, validationError }) => {
  const classes = useStyles();
  const { t } = useTranslation("forms");

  const [valueError, setValueError] = useState("");

  const errorMessage = useMemo(() => {
    return _.trim(`${validationError} ${valueError}`);
  }, [validationError, valueError]);

  const handleUpload = (files) => {
    setValueError("");
    if (!files?.length) {
      return;
    }

    _.entries(files).forEach(([_key, uploadedFile]) => {
      const reader = new FileReader();
      reader.readAsArrayBuffer(uploadedFile);

      reader.onload = () => {
        onUpload(uploadedFile, uploadedFile.name);
      };

      reader.onerror = () => {
        setValueError(t("upload-json.error-reader"));
      };
    });
  };

  const handleUploadButton = (e) => {
    const { files } = e.target;
    handleUpload(files);
  };

  return (
    <UploadFileDnD onDrop={handleUpload} isError={Boolean(errorMessage)}>
      <Box className={classes.uploadWrapper}>
        <>
          <Button
            variant="outlined"
            color="primary"
            component="label"
            onChange={handleUploadButton}
          >
            {t("upload-json.btn-upload")}
            <input type="file" multiple="multiple" hidden />
          </Button>
          {t("upload-json.text-drag")}
        </>
        {errorMessage ? <Typography className={classes.errorMsg}>{errorMessage}</Typography> : null}
      </Box>
    </UploadFileDnD>
  );
};

UploadFile.propTypes = {
  onUpload: PropTypes.func.isRequired,
  validationError: PropTypes.string,
};

UploadFile.defaultProps = {
  validationError: "",
};

export default UploadFile;
