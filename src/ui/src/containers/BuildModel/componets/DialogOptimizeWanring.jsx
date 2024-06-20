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

import React from "react";
import { Alert, Box, Typography, Button } from "@mui/material";

import { useTranslation } from "react-i18next";
import { DialogConfirmChildren } from "components/DialogConfirm";

import useStyles from "../BuildModeStyle";

const DialogOptimizeWarningModels = ({
  isOpen,
  notRenamedModels,
  onCancel,
  onConfirm,
  onRenameModel,
}) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  return (
    <DialogConfirmChildren
      isOpen={isOpen}
      confirmText={t("model-builder.dialog-warning-models-confirm-btn")}
      cancelText={t("model-builder.dialog-warning-models-cancel-btn")}
      title={t("model-builder.dialog-warning-models-title")}
      onClose={() => {
        onCancel();
      }}
      onConfirm={() => {
        onConfirm();
      }}
    >
      <>
        <Box mb={2}>
          <Alert severity="warning">{t("model-builder.dialog-warning-models-subtitle")}</Alert>
        </Box>
        <Box className={classes.dialogTable} display="table">
          <Box className={classes.dialogTableRow} display="table-row">
            <Typography variant="subtitle1" gutterBottom>
              <b>{t("model-builder.dialog-warning-models-rename-table-name")}</b>
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
              <b>{t("model-builder.dialog-warning-models-rename-table-accuracy")}</b>
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
              <b>{t("model-builder.dialog-warning-models-rename-table-size")}</b>
            </Typography>
            <Typography>{""}</Typography>
          </Box>
          {notRenamedModels.map((el, index) => (
            <Box
              key={`warning_modal_rename_${index}`}
              display="table-row"
              className={classes.dialogTableRow}
            >
              <Typography variant="subtitle1" gutterBottom>
                {el.name}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                {el.accuracy}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                {el.model_size}
              </Typography>
              <Button color="primary" onClick={() => onRenameModel(el)}>
                {t("model-builder.dialog-warning-models-rename-btn")}
              </Button>
            </Box>
          ))}
        </Box>
      </>
    </DialogConfirmChildren>
  );
};

export default DialogOptimizeWarningModels;
