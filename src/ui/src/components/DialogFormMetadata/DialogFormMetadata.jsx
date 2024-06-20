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

import React, { useState, useEffect } from "react";
import _ from "lodash";

import PropTypes from "prop-types";

import { Alert, Box, Button, Radio, FormControlLabel, TextField, Typography } from "@mui/material";

import makeStyles from "@mui/styles/makeStyles";

import { useTranslation } from "react-i18next";

import UIDialogForm from "components/UIDialogFormMedium";

const useStyles = () =>
  makeStyles((theme) => ({
    formWrap: {
      width: "100%",
      display: "flex",
      flexDirection: "column",
      marginBottom: theme.spacing(3),
    },
  }))();

const DialogFormMetadata = ({
  isOpen,
  defaultName,
  defaultIsDropDown,

  title = "",
  description = "",
  metadataNames = [],
  validationError,

  onClose,
  onSubmit,
}) => {
  const { t } = useTranslation("components");
  const classes = useStyles();

  const [name, setName] = useState();
  const [isTypeDropDown, setIsTypeDropDown] = useState(true);
  const [errorName, setErrorName] = useState();

  const handleChangeName = (e) => {
    setErrorName("");
    setName(e?.target?.value);
  };

  const handleTypeIsDropdownChange = (value) => {
    setIsTypeDropDown(value);
  };

  const validateName = (_name) => {
    if (
      !_.isEmpty(
        metadataNames
          .filter((elName) => elName !== defaultName)
          .find((elName) => _.toLower(_.trim(_name)) === _.toLower(_.trim(elName))),
      )
    ) {
      setErrorName(t("dialog-form-metadata-values.validation-error-duplicate", { name: _name }));
      return false;
    }
    return [];
  };

  const handleClose = () => {
    onClose();
  };

  const handleSubmit = () => {
    if (validateName(name)) {
      onSubmit(name || defaultName, isTypeDropDown);
    }
  };

  useEffect(() => {
    return () => setErrorName("");
  }, []);

  useEffect(() => {
    if (!_.isUndefined(defaultIsDropDown)) {
      handleTypeIsDropdownChange(defaultIsDropDown);
    }
  }, [defaultIsDropDown]);

  useEffect(() => {
    return () => setName("");
  }, []);

  return (
    <UIDialogForm
      title={title}
      disableEscapeKeyDown
      isOpen={isOpen}
      onClose={handleClose}
      aria-labelledby={title}
      actionsComponent={
        <>
          <Button onClick={handleClose} color="primary" variant="outlined" fullWidth>
            {t("dialog-form-metadata.btn-action-cancel")}
          </Button>
          <Button onClick={handleSubmit} color="primary" variant="contained" fullWidth>
            {t("dialog-form-metadata.btn-action-save")}
          </Button>
        </>
      }
    >
      <Box>
        {description || validationError ? (
          <Box mt={1} mb={2}>
            {validationError ? (
              <Alert severity="error">{validationError}</Alert>
            ) : (
              <Alert severity="info">{description}</Alert>
            )}
          </Box>
        ) : null}
        <Box className={classes.formWrap}>
          <TextField
            error={Boolean(errorName)}
            helperText={errorName}
            autoFocus
            margin="dense"
            id="metadataName"
            label={t("dialog-form-metadata.label-name")}
            required
            defaultValue={defaultName}
            onChange={handleChangeName}
            fullWidth
          />
        </Box>
        <Box className={classes.formWrap}>
          <Typography gutterBottom>{t("dialog-form-metadata.label-type")}</Typography>
          <Box>
            <FormControlLabel
              value="top"
              control={
                <Radio
                  id="isDropdownRaio"
                  color="primary"
                  checked={isTypeDropDown}
                  onChange={(_e) => handleTypeIsDropdownChange(true)}
                />
              }
              label={t("dialog-form-metadata.label-type-dropdown")}
              labelPlacement="start"
            />
            <FormControlLabel
              value="top"
              control={
                <Radio
                  id="isTextRaio"
                  color="primary"
                  checked={!isTypeDropDown}
                  onChange={(_e) => handleTypeIsDropdownChange(false)}
                />
              }
              label={t("dialog-form-metadata.label-type-text")}
              labelPlacement="start"
            />
          </Box>
          <Typography variant="caption">
            {isTypeDropDown
              ? t("dialog-form-metadata.type-dropdown-help")
              : t("dialog-form-metadata.type-text-help")}
          </Typography>
        </Box>
      </Box>
    </UIDialogForm>
  );
};

DialogFormMetadata.propTypes = {
  onSubmit: PropTypes.func,
  onClose: PropTypes.func,
};

DialogFormMetadata.defaultProps = {
  onSubmit: () => {},
  onClose: () => {},
};

export default DialogFormMetadata;
