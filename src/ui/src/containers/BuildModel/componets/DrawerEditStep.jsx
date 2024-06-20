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

import { Alert, Drawer, Box, Typography, Switch, FormControlLabel } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import useStyles from "../BuildModeStyle";

const DrawerEditStep = ({
  name,
  type,
  children,
  isOpen,
  onClose,
  alertMessage,
  onChangeEditMode,
  isJsonEditMode,
  jsonEditModeLabel,
  alertSeverity = "info",
}) => {
  const classes = useStyles();
  const theme = useTheme();

  const handleChangeEditMode = () => {
    onChangeEditMode();
  };

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
          {name}
        </Typography>
        <Box className={classes.drawerInfoText}>
          <Box>{type}</Box>
          <FormControlLabel
            control={
              <Switch
                checked={isJsonEditMode}
                onChange={() => handleChangeEditMode()}
                color="primary"
                name="checkedB"
                inputProps={{ "aria-label": "primary checkbox" }}
              />
            }
            label={jsonEditModeLabel}
          />
        </Box>
        {alertMessage ? <Alert severity={alertSeverity}>{alertMessage}</Alert> : null}
        <Box data-test={"drawer-edit-step-form"} className={classes.drawerContent}>
          {children}
        </Box>
      </Box>
    </Drawer>
  );
};

export default DrawerEditStep;
