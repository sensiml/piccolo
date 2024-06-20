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
import Alert from "@mui/material/Alert";

const useStyles = () =>
  makeStyles((theme) => ({
    message: {
      height: "240px",
      overflowY: "auto",
      paddingTop: theme.spacing(4),
      width: "100%",
      whiteSpace: "pre-line",
      marginRight: theme.spacing(2),
      "&::-webkit-scrollbar": {
        width: theme.spacing(0.75),
        cursor: "pointer",
      },
      "&::-webkit-scrollbar-track": {
        boxShadow: "none",
        webkitBoxShadow: "none",
        backgroundColor: "transparent",
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: theme.palette.notSelected.light,
        cursor: "pointer",
        borderRadius: "3px",
        // outline: "1px solid slategrey",
      },
    },
    icon: {
      padding: theme.spacing(1),
    },
  }))();

const UIAlertScrolled = ({ children, ...restProps }) => {
  const classes = useStyles();

  return (
    <Alert classes={{ ...classes }} {...restProps}>
      {children}
    </Alert>
  );
};

export default UIAlertScrolled;
