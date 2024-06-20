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

import { Box } from "@mui/material";

const useStyles = () =>
  makeStyles((theme) => ({
    wrapper: {
      display: "flex",
      alignItems: "center",
      width: "100%",
    },
    colorBox: {
      marginRight: theme.spacing(1),
      height: "1rem",
      width: "1rem",
    },
  }))();

const LabelColoredName = ({ name, color, className = "" }) => {
  const classes = useStyles();
  return (
    <Box className={classes.wrapper}>
      <Box className={classes.colorBox} style={{ background: color }} />
      <span className={`${classes.name} ${className}`}>{name}</span>
    </Box>
  );
};

export default LabelColoredName;
