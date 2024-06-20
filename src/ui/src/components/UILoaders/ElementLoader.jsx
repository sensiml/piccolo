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
import { Box } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import Loader from "react-loader-spinner";
import useStyles from "./UILoadersStyles";

const ElementLoader = ({ message = "", isOpen = true, style = {}, type = "Bars" }) => {
  /*
     "Audio"
      |"BallTriangle"
      |"Bars"
      |"Circles"
      |"Grid"
      |"Hearts"
      |"Oval"
      |"Puff"
      |"Rings"
      |"TailSpin"
      |"ThreeDots"
      |"Watch"
      |"RevolvingDot"
      |"Triangle"
      |"Plane"
      |"MutatingDots"
      |"CradleLoader";
  */
  const classes = useStyles();
  const theme = useTheme();

  return (
    <Box style={{ ...style }} className={classes.elementBackdrop}>
      <Loader
        visible={isOpen}
        transitionDuration={{ appear: 0, enter: 0, exit: 500 }}
        type={type}
        color={theme.colorLoader}
        className={classes.apploaderIcon}
        height={50}
        width={50}
      />
      <p className={classes.messageLoader}>{message}</p>
    </Box>
  );
};

export default ElementLoader;
