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

import { Alert, Box, Button, Divider, IconButton, Tooltip, Typography } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";

import { useTranslation } from "react-i18next";
import { DialogConfirm } from "components/DialogConfirm";

import ElementLoader from "components/UILoaders/ElementLoader";
import DialogInformation from "components/DialogInformation";
import DialogFormAPIKey from "components/DialogFormAPIKey";
import { UISnackBar } from "components/UISnackBar";

import makeStyles from "@mui/styles/makeStyles";

const useStyles = () =>
  makeStyles((theme) => ({
    infoTitle: {
      marginBottom: theme.spacing(4),
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(4),
      fontWeight: 500,
      textAlign: "center",
    },
    dialogTable: {
      marginTop: theme.spacing(1),
      width: "100%",
    },
    dialogTableRow: {
      "& h6": {
        display: "table-cell",
        padding: theme.spacing(0.5),
      },
    },
    utitCell: {
      width: "100px",
      textAlign: "center",
    },
  }))();

const DialogAPIKeys = ({
  isOpen,
  isLoading,
  title,
  APIKeys,
  onCreateAPIKey,
  onDeleteAPIKey,
  onClose,
}) => {
  const { t } = useTranslation("components");
  const classes = useStyles();
  const [isOpenCreationForm, setIsOpenCreationForm] = useState(false);
  const [deletingAPIKeyUUID, setDeletingAPIKeyUUID] = useState("");
  const [deletingErrorMessage, setDeletingErrorMessage] = useState("");
  const [deletingSuccessMessage, setDeletingSuccessMessage] = useState("");

  const APIKeyNames = useMemo(() => {
    if (!_.isUndefined(APIKeys)) {
      return APIKeys.map((el) => el.name);
    }
    return [];
  }, [APIKeys]);

  const deletingAPIKeyName = useMemo(() => {
    if (!_.isUndefined(APIKeys)) {
      return APIKeys.find((el) => el.uuid === deletingAPIKeyUUID)?.name || "";
    }
    return "";
  }, [deletingAPIKeyUUID]);

  const clearState = () => {
    setDeletingErrorMessage();
    setDeletingSuccessMessage();
    setIsOpenCreationForm();
    setDeletingSuccessMessage();
  };

  const handleCloseCrationForm = () => {
    setIsOpenCreationForm(false);
  };

  const handleCreateAPIKey = (name) => {
    return onCreateAPIKey(name);
  };

  const handleDeleteAPIKey = (APIKeyUUID) => {
    setDeletingAPIKeyUUID(APIKeyUUID);
  };

  const handleDeleteConfirmAPIKey = async () => {
    try {
      await onDeleteAPIKey(deletingAPIKeyUUID);
      setDeletingSuccessMessage(
        t("table-api-keys.dialog-delete-success-message", { name: deletingAPIKeyName }),
      );
    } catch (e) {
      setDeletingErrorMessage(e.message);
    }
    setDeletingAPIKeyUUID("");
  };

  const handleDeleteCancelAPIKey = () => {
    setDeletingAPIKeyUUID("");
  };

  useState(() => {
    return () => clearState();
  }, []);

  return (
    <DialogInformation isOpen={isOpen} onClose={onClose}>
      <Box>
        {title ? (
          <Typography variant="h2" className={classes.infoTitle}>
            {title}
          </Typography>
        ) : null}
        <Box mt={1} mb={2}>
          <Alert severity="info">{t("table-api-keys.description")}</Alert>
        </Box>
        <Divider />
        <Box p={1}>
          <Button variant="contained" color="primary" onClick={(_e) => setIsOpenCreationForm(true)}>
            {t("table-api-keys.btn-create")}
          </Button>
        </Box>
        <Divider />
        {isLoading ? (
          <ElementLoader isOpen={true} />
        ) : (
          <Box className={classes.dialogTable} display="table">
            <Box className={classes.dialogTableRow} display="table-row">
              <Typography variant="subtitle1" color="primary" gutterBottom>
                <b>{t("table-api-keys.header-name")}</b>
              </Typography>
              <Typography variant="subtitle1" color="primary" gutterBottom>
                <b>{t("table-api-keys.header-prefix")}</b>
              </Typography>
              <Typography
                variant="subtitle1"
                color="primary"
                className={classes.utitCell}
                gutterBottom
              >
                <b>{t("table-api-keys.header-delete")}</b>
              </Typography>
            </Box>
            {APIKeys.map((el) => (
              <Box
                key={`api_key_name_${el.prefix}`}
                display="table-row"
                className={classes.dialogTableRow}
              >
                <Typography variant="subtitle1" gutterBottom>
                  {el.name}
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                  {el.prefix}
                </Typography>
                <Box className={classes.utitCell}>
                  <Tooltip title={t("table-api-keys.tooltip-delete")}>
                    <IconButton
                      onClick={(_e) => handleDeleteAPIKey(el.uuid)}
                      variant="contained"
                      color="primary"
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </Box>
      <DialogFormAPIKey
        title={t("table-api-keys.title-create-api-key")}
        isOpen={isOpenCreationForm}
        onClose={handleCloseCrationForm}
        onSubmit={handleCreateAPIKey}
        existingNames={APIKeyNames}
      />
      <DialogConfirm
        isOpen={Boolean(deletingAPIKeyUUID)}
        title={t("table-api-keys.dialog-delete-alert-title")}
        text={t("table-api-keys.dialog-delete-alert-description", {
          name: deletingAPIKeyName,
        })}
        onConfirm={handleDeleteConfirmAPIKey}
        onCancel={handleDeleteCancelAPIKey}
        cancelText={t("dialog-confirm-delete.cancel")}
        confirmText={t("dialog-confirm-delete.delete")}
      />
      <UISnackBar
        isOpen={Boolean(deletingErrorMessage)}
        message={deletingErrorMessage}
        variant="error"
        onClose={() => setDeletingErrorMessage("")}
      />
      <UISnackBar
        isOpen={Boolean(deletingSuccessMessage)}
        message={deletingSuccessMessage}
        variant="success"
        onClose={() => setDeletingSuccessMessage("")}
        autoHideDuration={1500}
      />
    </DialogInformation>
  );
};

DialogAPIKeys.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onCreateAPIKey: PropTypes.func,
  onDeleteAPIKey: PropTypes.func,
  onClose: PropTypes.func,
};

DialogAPIKeys.defaultProps = {
  onCreateAPIKey: () => {},
  onDeleteAPIKey: () => {},
  onClose: () => {},
};

export default DialogAPIKeys;
