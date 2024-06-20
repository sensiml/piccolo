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
import DeleteIcon from "@mui/icons-material/Delete";
import makeStyles from "@mui/styles/makeStyles";

import { Box, IconButton, Tooltip, Typography, Skeleton } from "@mui/material";
import { useTranslation } from "react-i18next";
import { DialogConfirm } from "components/DialogConfirm";
import { UISnackBar } from "components/UISnackBar";

const useStyles = () =>
  makeStyles((theme) => ({
    infoTitle: {
      marginBottom: theme.spacing(4),
      marginTop: theme.spacing(4),
      fontSize: theme.spacing(4),
      fontWeight: 500,
      textAlign: "center",
    },
    dialogTable: {
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

const AccountTableAPIKeys = ({ isLoading, APIKeys, onDeleteAPIKey }) => {
  const { t } = useTranslation("components");
  const classes = useStyles();

  const [deletingAPIKeyUUID, setDeletingAPIKeyUUID] = useState("");
  const [deletingErrorMessage, setDeletingErrorMessage] = useState("");
  const [deletingSuccessMessage, setDeletingSuccessMessage] = useState("");

  const deletingAPIKeyName = useMemo(() => {
    if (!_.isUndefined(APIKeys)) {
      return APIKeys.find((el) => el.uuid === deletingAPIKeyUUID)?.name || "";
    }
    return "";
  }, [deletingAPIKeyUUID]);

  const clearState = () => {
    setDeletingErrorMessage();
    setDeletingSuccessMessage();

    setDeletingSuccessMessage();
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
    <>
      {isLoading ? (
        <>
          <Skeleton animation="wave" width={"100%"} />
          <Skeleton animation="wave" width={"100%"} />
          <Skeleton animation="wave" width={"100%"} />
          <Skeleton animation="wave" width={"100%"} />
          <Skeleton animation="wave" width={"100%"} />
        </>
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
    </>
  );
};

AccountTableAPIKeys.propTypes = {
  onDeleteAPIKey: PropTypes.func,
};

AccountTableAPIKeys.defaultProps = {
  onDeleteAPIKey: () => {},
};

export default AccountTableAPIKeys;
