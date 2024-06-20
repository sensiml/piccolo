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
import { Grid, Paper, IconButton, Typography } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import makeStyles from "@mui/styles/makeStyles";
import { useTranslation } from "react-i18next";

const useStyles = () =>
  makeStyles((theme) => ({
    pipelinePanelWrapper: {
      marginBottom: theme.spacing(2),
    },
    textWrapper: {
      display: "flex",
      alignItems: "center",
      padding: theme.spacing(2),
    },

    actionWrapper: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-end",
      gap: theme.spacing(2),
      padding: theme.spacing(2),
    },

    stepperBackButton: {
      border: `1px solid ${theme.palette.primary.main}`,
      marginRight: theme.spacing(2),
    },
  }))();

const BuilderPipelinePanel = ({ pipelineName, onClickBack, actionsBtns }) => {
  const classes = useStyles();
  const { t } = useTranslation("models");

  return (
    <Paper elevation={0}>
      <Grid container className={classes.pipelinePanelWrapper}>
        <Grid item md={6} className={classes.textWrapper}>
          <IconButton
            onClick={onClickBack}
            className={classes.stepperBackButton}
            color="primary"
            size="small"
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant={"h4"}>
            {t("model-builder.pipeline-panel-header", { pipelineName })}
          </Typography>
        </Grid>
        <Grid item md={6} className={classes.actionWrapper}>
          {actionsBtns}
        </Grid>
      </Grid>
    </Paper>
  );
};

export default BuilderPipelinePanel;
