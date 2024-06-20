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

import React, { useMemo } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from "@mui/material";
import CancelIcon from "@mui/icons-material/Cancel";
import ContinueIcon from "@mui/icons-material/CheckBox";
import { useTranslation } from "react-i18next";

import { IconSpinneAutoRenew } from "components/UIIcons";

const DialogConfirm = ({
  isOpen,
  title,
  text,
  backText,
  cancelText,
  confirmText,
  onBack,
  onCancel,
  onConfirm,
  isLoading = false,
  isBackPrimary = false,
  isCancelPrimary = false,
  isConfirmPrimary = false,
  isBackSecondary = false,
  isCancelSecondary = false,
  isConfirmSecondary = false,
  isUseIcons = false,
}) => {
  const { t } = useTranslation("common");

  const _isConfirmPrimary = useMemo(() => {
    return isBackPrimary || isCancelPrimary || isConfirmPrimary ? isConfirmPrimary : true;
  }, [isBackPrimary, isCancelPrimary, isConfirmPrimary]);

  const buttonsToRender = [
    {
      method: onBack,
      isShow: Boolean(onBack),
      startIcon: isUseIcons && <CancelIcon />,
      variant: isBackPrimary ? "contained" : "outlined",
      text: backText || t("Back"),
      isLoading,
      isPrimary: isBackPrimary ? 2 : 0,
      isSecondary: isBackSecondary ? 1 : 0,
    },
    {
      method: onCancel,
      isShow: Boolean(onCancel),
      startIcon: isUseIcons && <CancelIcon />,
      variant: isCancelPrimary ? "contained" : "outlined",
      text: cancelText || t("Cancel"),
      isLoading,
      isPrimary: isCancelPrimary ? 2 : 0,
      isSecondary: isCancelSecondary ? 1 : 0,
    },
    {
      method: onConfirm,
      isShow: Boolean(onConfirm),
      startIcon: isLoading ? <IconSpinneAutoRenew /> : isUseIcons && <ContinueIcon />,
      variant: _isConfirmPrimary ? "contained" : "outlined",
      text: confirmText || t("Confirm"),
      isLoading,
      isPrimary: _isConfirmPrimary ? 2 : 0,
      isSecondary: isConfirmSecondary ? 1 : 0,
    },
  ];

  return (
    <Dialog
      open={isOpen}
      onClose={onCancel}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title">{title || ""}</DialogTitle>
      <DialogContent>
        <DialogContentText id="alert-dialog-description">{text}</DialogContentText>
      </DialogContent>
      <DialogActions>
        {buttonsToRender
          .sort((a, b) => (a.isPrimary + a.isSecondary > b.isPrimary + b.isSecondary ? 1 : -1))
          .filter((el) => el.method)
          .map((el) => (
            <Button
              key={el.text}
              autoFocus
              color="primary"
              variant={el.variant}
              onClick={el.method}
              data-test="dialog-confirm-back"
              startIcon={el.startIcon}
              disabled={el.isLoading || false}
            >
              {el.text}
            </Button>
          ))}
      </DialogActions>
    </Dialog>
  );
};

export default DialogConfirm;
