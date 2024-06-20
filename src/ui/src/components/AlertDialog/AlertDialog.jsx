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

/* eslint-disable react/prop-types */
import React, { useEffect } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from "@mui/material";
import CancelIcon from "@mui/icons-material/Cancel";
import ContinueIcon from "@mui/icons-material/CheckBox";

const AlertDialog = (props) => {
  const {
    openDialog,
    alertTitle,
    dialogText,
    buttonOneText,
    buttonTwoText,
    buttonOneAction,
    buttonTwoAction,
  } = props;
  const [open, setOpen] = React.useState(openDialog);

  const handleButtonOneAction = () => {
    buttonOneAction();
    setOpen(false);
  };

  const handleButtonTwoAction = () => {
    buttonTwoAction();
    setOpen(false);
  };

  useEffect(() => {
    setOpen(openDialog);
  }, [openDialog]);

  return (
    <div>
      <Dialog
        disableEscapeKeyDown
        open={open}
        onClose={handleButtonTwoAction}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{alertTitle}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">{dialogText}</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleButtonTwoAction}
            startIcon={<CancelIcon />}
            color="primary"
            variant="outlined"
            autoFocus
          >
            {buttonTwoText}
          </Button>
          <Button
            onClick={handleButtonOneAction}
            startIcon={<ContinueIcon />}
            color="primary"
            variant="contained"
          >
            {buttonOneText}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default AlertDialog;
