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
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from "@mui/material";
import { useTranslation } from "react-i18next";

const DialogConfirmChildren = ({
  isOpen,
  title,
  cancelText,
  confirmText,
  onClose,
  onConfirm,
  children,
}) => {
  const { t } = useTranslation("common");

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title">{title || ""}</DialogTitle>
      <DialogContent>
        <DialogContentText id="alert-dialog-description">{children}</DialogContentText>
      </DialogContent>
      <DialogActions>
        {onClose ? (
          <Button
            autoFocus
            color="primary"
            variant="contained"
            onClick={onClose}
            data-test="dialog-confirm-cancel"
          >
            {cancelText || t("Cancel")}
          </Button>
        ) : null}
        {onConfirm ? (
          <Button
            color="primary"
            variant="outlined"
            onClick={onConfirm}
            data-testid="dialog-confirm-confirm"
          >
            {confirmText || t("Confirm")}
          </Button>
        ) : null}
      </DialogActions>
    </Dialog>
  );
};

export default DialogConfirmChildren;
