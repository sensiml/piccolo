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

import makeStyles from "@mui/styles/makeStyles";
import { Alert, Box, Button, TextField, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import UIDialogForm from "components/UIDialogFormMedium";

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
  description = "",
  existingNames = [],
  validationError,

  onClose,
  onSubmit,
}) => {
  const { t } = useTranslation("components");
  const classes = useStyles();

  const [name, setName] = useState("");
  const [errorName, setErrorName] = useState();

  const isDisabledSubmit = useMemo(() => {
    return !name;
  }, [name]);

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
      setErrorName(t("dialog-form-project.validation-error-duplicate", { name: _name }));
      return false;
    }
    return [];
  };

  const handleClose = () => {
    onClose();
  };

  const handleSubmit = () => {
    if (validateName(name)) {
      onSubmit(name);
    }
  };

  useEffect(() => {
    if (validationError) {
      setErrorName(validationError);
    }
  }, [validationError]);

  useEffect(() => {
    return () => setErrorName("");
  }, []);

  useEffect(() => {
    return () => setName("");
  }, []);

  return (
    <UIDialogForm
      disableEscapeKeyDown
      isOpen={isOpen}
      onClose={handleClose}
      aria-labelledby={title}
      actionsComponent={
        <>
          <Button onClick={handleClose} color="primary" variant="outlined" fullWidth>
            {t("dialog-form-project.btn-action-cancel")}
          </Button>
          <Button
            onClick={handleSubmit}
            color="primary"
            variant="contained"
            disabled={isDisabledSubmit}
            fullWidth
          >
            {t("dialog-form-project.btn-action-save")}
          </Button>
        </>
      }
    >
      <Box>
        {title ? (
          <Typography variant="h2" className={classes.createDialogTitle}>
            {title}
          </Typography>
        ) : null}
        {description ? (
          <Box mt={1} mb={2}>
            <Alert severity="info">{description}</Alert>
          </Box>
        ) : null}
        <Box className={classes.formWrap}>
          <TextField
            error={Boolean(errorName)}
            helperText={errorName}
            autoFocus
            id="projectName"
            label={t("dialog-form-project.label-name")}
            variant="outlined"
            required
            defaultValue={defaultName}
            onChange={handleChangeName}
            fullWidth
          />
        </Box>
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
