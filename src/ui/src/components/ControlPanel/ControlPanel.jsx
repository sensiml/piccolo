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
import { Box, Grid, IconButton, Typography, Tooltip } from "@mui/material";
import { useTranslation } from "react-i18next";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import makeStyles from "@mui/styles/makeStyles";

import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

import { filterTruncateMiddle } from "filters";
import { UIControlPanel } from "components/UIPanels";
import { IconButtonRounded } from "components/UIButtons";

const useStyles = () =>
  makeStyles((theme) => ({
    panelWrapper: {
      padding: "0.75rem 1rem",
    },
    textWrapper: {
      display: "flex",
      alignItems: "center",
    },

    actionWrapper: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-end",
      gap: theme.spacing(0.5),
      marginLeft: "auto",
    },
    stepperBackButton: {
      marginRight: theme.spacing(2),
    },
    titleRoot: {
      fontSize: theme.spacing(2.5),
    },
  }))();

const ControlPanel = ({
  title,
  subtitle,
  onClickBack,
  onShowInformation,
  actionsBtns,
  truncateLength = 0,
}) => {
  const { t } = useTranslation("components");
  const classes = useStyles();

  return (
    <UIControlPanel>
      <Grid container className={classes.panelWrapper}>
        <Grid item className={classes.textWrapper}>
          {onClickBack ? (
            <IconButtonRounded
              className={classes.stepperBackButton}
              onClick={onClickBack}
              color="primary"
              size="small"
            >
              <ArrowBackIcon />
            </IconButtonRounded>
          ) : null}
          <Typography variant={"h2"} classes={{ root: classes.titleRoot }}>
            {title && filterTruncateMiddle(title, truncateLength)}
            {onShowInformation ? (
              <Tooltip title={t("control-panel.tooltip-info-button")} placement="top">
                <IconButton onClick={onShowInformation}>
                  <InfoOutlinedIcon color="primary" />
                </IconButton>
              </Tooltip>
            ) : null}
          </Typography>
          <Box alignItems="center" ml={2}>
            {subtitle}
          </Box>
        </Grid>
        <Grid item className={classes.actionWrapper}>
          {actionsBtns}
        </Grid>
      </Grid>
    </UIControlPanel>
  );
};

export default ControlPanel;
