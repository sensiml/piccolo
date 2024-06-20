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

import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import makeStyles from "@mui/styles/makeStyles";

import { Box, Divider } from "@mui/material";

const useStyles = ({ height }) =>
  makeStyles((theme) => ({
    collapseWrapper: {
      height: theme.spacing(height),
      display: "flex",
      position: "relative",
    },
    dividerWrapper: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      width: "100%",
    },
    divider: {
      width: "100%",
    },
    buttonWrapper: {
      cursor: "pointer",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      "&:hover .icon-down": {
        "margin-top": "5px",
      },
      "&:hover .icon-up": {
        "margin-top": "-5px",
      },
    },
    textWrapper: {
      minWidth: "200px",
      textAlign: "center",
      color: theme.palette.primary.dark,
    },
    Icon: {
      transform: "scale(0.85)",
      transition: "all 500ms",
    },
  }))();

const FormCurtain = ({ text, onClickHandler, isOpen, height = 6 }) => {
  const classes = useStyles({ height });

  const handleClick = () => {
    if (onClickHandler) {
      onClickHandler(!isOpen);
    }
  };
  return (
    <Box className={classes.collapseWrapper}>
      <Box className={classes.dividerWrapper}>
        <Divider className={classes.divider} />
      </Box>
      <Box>
        <Box className={classes.buttonWrapper} onClick={handleClick}>
          <span variant="span" className={classes.textWrapper}>
            {text}
          </span>
          <Box>
            {isOpen ? (
              <KeyboardArrowUpIcon className={`icon-up ${classes.Icon}`} color="primary" />
            ) : (
              <KeyboardArrowDownIcon className={`icon-down ${classes.Icon}`} color="primary" />
            )}
          </Box>
        </Box>
      </Box>
      <Box className={classes.dividerWrapper}>
        <Divider className={classes.divider} />
      </Box>
    </Box>
  );
};

export default FormCurtain;
