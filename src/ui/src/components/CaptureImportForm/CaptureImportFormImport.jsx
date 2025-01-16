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

import DeleteIcon from "@mui/icons-material/Delete";

import { Alert, Button, Box, TextField, Zoom, FormControl } from "@mui/material";
import UploadFile from "components/FormElements/UploadFile";

import { useTranslation } from "react-i18next";

import { getFileExtension, getFileName } from "utils";
import { IconButtonRounded } from "components/UIButtons";
import useStyles from "./PipelineImportStyles";

const ALLOWED_EXT_LIST = ["csv", "wav"];
const MAX_FILES_LIMIT = 20;

const CaptureImportFormImport = ({ captureNames, onSubmit, errorUpload }) => {
  const { t } = useTranslation("components");
  const classes = useStyles();

  const [uploadedFiles, setUploadedFiles] = useState({});

  const uploadedFileNameList = useMemo(() => {
    return _.entries(uploadedFiles).map(([id, file]) => [id, file.name]) || [];
  }, [uploadedFiles]);

  const getLowerFileName = (name) => {
    return _.toLower(getFileName(name));
  };

  const errorCaptureNames = useMemo(() => {
    if (!_.isEmpty(uploadedFileNameList)) {
      return uploadedFileNameList.reduce((acc, [id, name]) => {
        const ext = getFileExtension(name);

        if (!ext || !ALLOWED_EXT_LIST.includes(ext)) {
          acc[id] = t("capture-form-import.error-capture-name-extension", {
            extension: _.join(ALLOWED_EXT_LIST, ", "),
          });
        }
        if (captureNames.map((_name) => getLowerFileName(_name)).includes(getLowerFileName(name))) {
          acc[id] = t("capture-form-import.error-capture-name-exist", { name });
        }
        if (
          uploadedFileNameList
            .filter(([_id, _name]) => _id !== id)
            .map(([_id, _name]) => getLowerFileName(_name))
            .includes(getLowerFileName(name))
        ) {
          acc[id] = t("capture-form-import.error-capture-should-be-unique");
        }
        return acc;
      }, {});
    }
    return {};
  }, [uploadedFiles, captureNames]);

  const isSubmitDisabled = useMemo(() => {
    return Boolean(!_.isEmpty(errorCaptureNames));
  }, [errorCaptureNames]);

  const handeAddFile = (file) => {
    setUploadedFiles((value) => {
      const updatedValue = { ...value };
      updatedValue[_.uniqueId()] = {
        name: file.name,
        file,
      };
      return updatedValue;
    });
  };

  const handeRemoveFile = (id) => {
    setUploadedFiles((value) => {
      const updatedValue = { ...value };
      return _.entries(updatedValue).reduce((acc, [_id, file]) => {
        if (_id !== id) {
          acc[_id] = { ...file };
        }
        return acc;
      }, {});
    });
  };

  const handleSubmit = () => {
    onSubmit(uploadedFiles);
  };

  const handleUpdateCaptureName = (id, e) => {
    setUploadedFiles((value) => {
      const updatedValue = { ...value };
      updatedValue[id].name = e.target.value;
      return updatedValue;
    });
  };

  return (
    <Box>
      {!_.isEmpty(uploadedFiles)
        ? uploadedFileNameList.map(([id, fileName], index) => (
            <Zoom key={`imported-${id}-${index}`} in={Boolean(!_.isEmpty(uploadedFiles))}>
              <FormControl className={classes.importFormWrap}>
                <TextField
                  id="name"
                  name="name"
                  fullWidth
                  variant="outlined"
                  value={fileName}
                  onChange={(e) => handleUpdateCaptureName(id, e)}
                  error={Boolean(errorCaptureNames[id])}
                  helperText={errorCaptureNames[id]}
                />
                <Box className={classes.importFormWrapAction}>
                  <IconButtonRounded
                    aria-label="delete"
                    color="primary"
                    onClick={() => handeRemoveFile(id)}
                  >
                    <DeleteIcon />
                  </IconButtonRounded>
                </Box>
              </FormControl>
            </Zoom>
          ))
        : null}
      {uploadedFileNameList?.length >= MAX_FILES_LIMIT ? (
        <Alert severity="info" variant="outlined">
          {t("capture-form-import.alert-importing-limit")}
        </Alert>
      ) : (
        <Box className={classes.importFormWrap}>
          <UploadFile onUpload={handeAddFile} validationError={errorUpload} />
        </Box>
      )}

      <Box className={classes.importFormWrapper}>
        <Button
          className={classes.submitBtn}
          color="primary"
          variant="contained"
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
        >
          {t("capture-form-import.btn-import-submit")}
        </Button>
      </Box>
    </Box>
  );
};

export default CaptureImportFormImport;
