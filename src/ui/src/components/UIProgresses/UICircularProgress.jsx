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
import PropTypes from "prop-types";

import { CircularProgress, Box } from "@mui/material";
// import useStyles from "./UIProgressesStyles";

// "rgba(255, 255, 255, 0.2)"
// "white"

const NumberCircularProgress = ({ size, value, colorData, colorEmpty, className, children }) => {
  return (
    <Box className={className} position="relative" display="flex">
      <Box top={0} left={0} bottom={0} right={0} position="absolute">
        <CircularProgress
          classes={{ circle: { strokeLinecap: "round" } }}
          style={colorEmpty ? { color: colorEmpty } : {}}
          size={size}
          variant="determinate"
          value={100}
        />
      </Box>
      <CircularProgress
        style={colorData ? { color: colorData } : {}}
        color="primary"
        size={size}
        variant="determinate"
        value={value}
      />
      <Box
        top={0}
        left={0}
        bottom={0}
        right={0}
        position="absolute"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        {children}
      </Box>
    </Box>
  );
};

NumberCircularProgress.propTypes = {
  size: PropTypes.string,
  value: PropTypes.number,
  colorData: PropTypes.string,
  colorEmpty: PropTypes.string,
};

NumberCircularProgress.defaultProps = {
  size: "3rem",
  value: 0,
  colorData: "",
  colorEmpty: "transparent",
};

export default NumberCircularProgress;
