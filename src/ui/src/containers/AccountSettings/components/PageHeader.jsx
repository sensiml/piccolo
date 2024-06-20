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
import { Box, Typography } from "@mui/material";

const useStyles = () =>
  makeStyles((theme) => ({
    header: {
      fontSize: theme.spacing(4.5),
      textAlign: "center",
      fontWeight: 500,
      lineHeight: theme.spacing(4.5),
      marginBottom: theme.spacing(2),
      marginTop: theme.spacing(2),
    },
    description: {
      fontSize: theme.spacing(2.5),
      textAlign: "center",
      fontWeight: 500,
      lineHeight: theme.spacing(2.5),
    },
  }))();

const PageHeader = ({ title, description }) => {
  const classes = useStyles();

  return (
    <Box mb={"3.5rem"}>
      <Typography className={classes.header} variant={"h2"}>
        {title}
      </Typography>
      <Typography className={classes.description} variant={"subtitle1"} color={"text.secondary"}>
        {description}
      </Typography>
    </Box>
  );
};

export default PageHeader;
