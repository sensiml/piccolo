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
import { Backdrop } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import Loader from "react-loader-spinner";
import useStyles from "./UILoadersStyles";

const ScreenLoader = ({ isOpen }) => {
  const classes = useStyles();
  const theme = useTheme();

  return (
    <Backdrop
      style={{ zIndex: 100, backgroundColor: "" }}
      className={classes.appBackdrop}
      open={isOpen}
    >
      <Loader
        transitionDuration={{ appear: 0, enter: 0, exit: 500 }}
        type="Bars"
        color={theme.colorLoader}
        className={classes.apploaderIcon}
        height={100}
        width={100}
      />
    </Backdrop>
  );
};

export default ScreenLoader;
