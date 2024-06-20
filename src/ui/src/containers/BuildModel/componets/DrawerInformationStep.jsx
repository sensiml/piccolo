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
import { Drawer, Box, Typography, Link } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { useTranslation } from "react-i18next";

import FormUIDescriptionParameters from "./DrawerDescriptionParameters";
import useStyles from "../BuildModeStyle";

const DrawerInformationStep = ({
  name,
  type,
  content,
  descriptionParameters,
  dataParams,
  transformName,
  transformDescription,
  docLink,
  isOpen,
  onClose,
}) => {
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
      open={isOpen}
      onClose={onClose}
      anchor={"right"}
      variant="temporary"
    >
      <Box className={classes.infoDrawerContext}>
        <Typography variant="h2" className={classes.drawerHeader}>
          {name}
        </Typography>
        <Typography paragraph className={classes.drawerInfoText}>
          {type}
        </Typography>
        {descriptionParameters ? (
          <FormUIDescriptionParameters descriptionParameters={descriptionParameters} />
        ) : null}
        <Typography paragraph className={classes.drawerContent}>
          {content}
        </Typography>
        {docLink ? (
          <Typography paragraph className={classes.drawerContent}>
            <Link href={docLink} title={docLink} target="_blank">
              {t("model-builder.drawer-step-info-doc-link")}
            </Link>
          </Typography>
        ) : null}
        <FormUIDescriptionParameters descriptionParameters={dataParams} />
        <Typography variant="h4" className={classes.drawerHeader}>
          {transformName}
        </Typography>
        <Typography>
          <pre className={classes.drawerInfoPreDescription} style={{ fontFamily: "inherit" }}>
            {transformDescription}
          </pre>
        </Typography>
      </Box>
    </Drawer>
  );
};

export default DrawerInformationStep;
