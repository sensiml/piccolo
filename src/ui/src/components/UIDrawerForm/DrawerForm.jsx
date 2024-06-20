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

import { Alert, Button, Drawer, Box, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";

import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import useStyles from "./DrawerFormStyles";

const DrawerForm = ({
  title,
  subTitle,
  children,
  isOpen,
  onClose,
  onSubmit,
  alertMessage,
  alertSeverity = "info",
  isConfirmDisabled = false,
}) => {
  const classes = useStyles();
  const theme = useTheme();

  return (
    <Drawer
      BackdropProps={{ style: { backgroundColor: theme.backgroundBackDoor } }}
      classes={{
        root: classes.formDrawerRoot,
        paperAnchorRight: classes.formDrawerSizing,
      }}
      open={isOpen}
      onClose={onClose}
      anchor={"right"}
      variant="temporary"
    >
      <Box className={classes.formStepDrawerContext}>
        <Typography variant="h2" className={classes.drawerHeader}>
          {title}
        </Typography>
        <Typography paragraph className={classes.drawerInfoText}>
          {subTitle}
        </Typography>
        {alertMessage ? <Alert severity={alertSeverity}>{alertMessage}</Alert> : null}
        <Box data-test={"drawer-edit-step-form"} className={classes.drawerContent}>
          {children}
        </Box>
        <Box className={classes.drawerFormButtonWrapper}>
          <Button
            className={`${classes.drawerFormButton} ${classes.mr2}`}
            size="large"
            startIcon={<CancelOutlinedIcon />}
            variant="outlined"
            color="primary"
            onClick={onClose}
            data-testid={"edit-step-form-close"}
          >
            {"Cancel"}
          </Button>
          <Button
            onClick={onSubmit}
            className={classes.drawerFormButton}
            size="large"
            variant="contained"
            color="primary"
            data-testid={"edit-step-form-submit"}
            disabled={isConfirmDisabled}
          >
            {"Save"}
          </Button>
        </Box>
      </Box>
    </Drawer>
  );
};

export default DrawerForm;
