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

import makeStyles from "@mui/styles/makeStyles";
import RefreshIcon from "@mui/icons-material/Refresh";

import { Paper, Grid, Typography, IconButton } from "@mui/material";

const useStyles = () =>
  makeStyles((theme) => ({
    panelWrapper: {
      minHeight: theme.spacing(7),
      display: "flex",
    },
    gridItem: {
      margin: "0",
      boxSizing: "border-box",
      padding: `${theme.spacing(1)} ${theme.spacing(2)}`,
      display: "flex",
      alignItems: "center",
    },
    actionWrapper: {
      display: "flex",
      justifyContent: "flex-end",
    },
  }))();

const UITablePanel = ({ title, onRefresh, ActionComponent }) => {
  const classes = useStyles();

  return (
    <Paper className={classes.panelWrapper} elevation={0}>
      <Grid container justifyContent={"space-between"}>
        <Grid item md={6} classes={{ item: classes.gridItem }}>
          <Typography variant={"h4"}>{title}</Typography>
        </Grid>
        <Grid item md={6} classes={{ item: classes.gridItem }} className={classes.actionWrapper}>
          <>
            {ActionComponent || null}
            {onRefresh ? (
              <IconButton color="primary" onClick={onRefresh} size="large">
                <RefreshIcon />
              </IconButton>
            ) : null}
          </>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default UITablePanel;
