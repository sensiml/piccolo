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

import React, { forwardRef } from "react";
import { Tab } from "@mui/material";

import makeStyles from "@mui/styles/makeStyles";

const useStyles = () =>
  makeStyles((theme) => ({
    ...theme.common,
    root: {
      textTransform: "none",
      color: "white",
      minWidth: theme.spacing(20),
      minHeight: theme.spacing(2),
      fontWeight: theme.typography.fontWeightLight,
      borderTopRightRadius: "5px",
      borderTopLeftRadius: "5px",
      position: "relative",

      display: "inline-flex",
      alignItems: "center",
      flexDirection: "row",
      justifyContent: "flex-start",

      "&:hover": {
        opacity: 1,
      },
      "&:selected": {
        background: "#2d2d2d",
        fontWeight: theme.typography.fontWeightRegular,
      },
      "&:focus": {
        color: "",
      },
    },
    selected: {
      background: "#2d2d2d",
    },
  }))();

const ConsoleTab = forwardRef((props, ref) => {
  const classes = useStyles();
  return (
    <Tab
      disableRipple
      classes={{ root: classes.root, selected: classes.selected }}
      {...props}
      ref={ref}
    />
  );
});

export default ConsoleTab;
