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

/* eslint-disable no-unused-vars */
import React from "react";
import filters from "filters";
import { useTranslation } from "react-i18next";

import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { Alert, AlertTitle, Drawer, Box, Button, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import useStyles from "./BuildModeStyle";

const DrawerInformationMessage = ({ isOpen, header, message, onClose, parameters = [] }) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const theme = useTheme();

  return (
    <Drawer
      BackdropProps={{ style: { backgroundColor: theme.backgroundBackDoor } }}
      classes={{
        paperAnchorRight: classes.formDrawerSizing,
        root: classes.formDrawerRoot,
      }}
      style={{ zIndex: 3000 }}
      open={isOpen}
      onClose={onClose}
      anchor={"right"}
      variant="temporary"
    >
      <Box className={classes.formStepDrawerContext}>
        <Typography variant="h2" className={`${classes.drawerHeader} ${classes.drawerHeaderAlert}`}>
          <InfoOutlinedIcon classes={{ root: classes.drawerHeaderAlertIcon }} color="primary" />
          {header}
        </Typography>
        <Typography paragraph>{message}</Typography>
        {parameters.map((paramName, paramIndex) => (
          <Typography paragraph key={paramIndex} color="primary">
            {paramName}
          </Typography>
        ))}
        <Box className={classes.drawerContent}>
          <Box className={classes.drawerFormButtonWrapper}>
            <Button
              className={`${classes.drawerFormButton} ${classes.mr2}`}
              size="large"
              variant="contained"
              color="primary"
              onClick={onClose}
              data-testid={"new-step-drawer-close"}
            >
              {t("model-builder.alert-review-btn")}
            </Button>
          </Box>
        </Box>
      </Box>
    </Drawer>
  );
};

export default DrawerInformationMessage;
