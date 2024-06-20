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

import React, { useState, useEffect, useMemo } from "react";

import _ from "lodash";
import PropTypes from "prop-types";

import { Alert, Box, Button, TextField, Typography } from "@mui/material";
import makeStyles from "@mui/styles/makeStyles";

import ElementLoader from "components/UILoaders/ElementLoader";
import UIDialogForm from "components/UIDialogFormMedium";

import { useTranslation } from "react-i18next";

const useStyles = () =>
  makeStyles((theme) => ({
    createDialogTitle: {
      marginBottom: theme.spacing(2),
      textAlign: "center",
    },
    formWrap: {
      width: "100%",
      display: "flex",
      flexDirection: "column",
      marginTop: theme.spacing(3),
      marginBottom: theme.spacing(2),
    },
  }))();

const DialogFormProject = ({
  isOpen,
  defaultName,

  title = "",
  existingNames = [],
  validationError,

  onClose,
  onSubmit,
}) => {
  const { t } = useTranslation("components");
  const classes = useStyles();

  const [name, setName] = useState("");
  const [errorName, setErrorName] = useState();
  const [createdApiKey, setCreatedApiKey] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const isDisabledSubmit = useMemo(() => {
    return !name;
  }, [name]);

  const clearState = () => {
    setCreatedApiKey();
    setErrorName();
    setName();
  };

  const handleChangeName = (e) => {
    setErrorName("");
    setName(e?.target?.value);
  };

  const validateName = (_name = "") => {
    if (
      !_.isEmpty(
        existingNames.find((elName) => _.toLower(_.trim(_name)) === _.toLower(_.trim(elName))),
      )
    ) {
      setErrorName(t("dialog-form-api-key.validation-error-duplicate", { name: _name }));
      return false;
    }
    return [];
  };

  const handleClose = () => {
    clearState();
    onClose();
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    if (validateName(name)) {
      try {
        const apiKey = await onSubmit(name);
        setCreatedApiKey(apiKey);
      } catch (e) {
        setErrorName(e.message);
      }
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (validationError) {
      setErrorName(validationError);
    }
  }, [validationError]);

  useEffect(() => {
    return () => clearState();
  }, []);

  return (
    <UIDialogForm
      disableEscapeKeyDown
      isOpen={isOpen}
      onClose={handleClose}
      aria-labelledby={title}
      maxWidth="sm"
      actionsComponent={
        <>
          <Button onClick={handleClose} color="primary" variant="outlined" fullWidth>
            {t("dialog-form-api-key.btn-action-cancel")}
          </Button>
          {!createdApiKey ? (
            <Button
              onClick={handleSubmit}
              color="primary"
              variant="contained"
              disabled={isDisabledSubmit}
              fullWidth
            >
              {t("dialog-form-api-key.btn-action-save")}
            </Button>
          ) : null}
        </>
      }
    >
      <Box>
        {title ? (
          <Typography variant="h2" className={classes.createDialogTitle}>
            {title}
          </Typography>
        ) : null}
        {isLoading ? (
          <ElementLoader isOpen={true} />
        ) : (
          <>
            <Box mt={1} mb={2}>
              <Alert severity="info">
                {createdApiKey
                  ? t("dialog-form-api-key.description-is-created", { name })
                  : t("dialog-form-api-key.description-create")}
              </Alert>
            </Box>
            {createdApiKey ? (
              <Box className={classes.formWrap}>
                <TextField
                  autoFocus
                  id="projectName"
                  label={t("dialog-form-api-key.label-token")}
                  variant="outlined"
                  value={createdApiKey}
                  fullWidth
                />
              </Box>
            ) : (
              <Box className={classes.formWrap}>
                <TextField
                  error={Boolean(errorName)}
                  helperText={errorName}
                  autoFocus
                  id="projectName"
                  label={t("dialog-form-api-key.label-name")}
                  variant="outlined"
                  required
                  defaultValue={defaultName}
                  onChange={handleChangeName}
                  fullWidth
                />
              </Box>
            )}
          </>
        )}
      </Box>
    </UIDialogForm>
  );
};

DialogFormProject.propTypes = {
  onSubmit: PropTypes.func,
  onClose: PropTypes.func,
};

DialogFormProject.defaultProps = {
  onSubmit: () => {},
  onClose: () => {},
};

export default DialogFormProject;
