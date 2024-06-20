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

import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

import { SketchPicker } from "react-color";

import makeStyles from "@mui/styles/makeStyles";
import { Box, TextField } from "@mui/material";

import InputAdornment from "@mui/material/InputAdornment";

const useStyles = () =>
  makeStyles((theme) => ({
    colorBox: {
      marginRight: theme.spacing(1),
      height: theme.spacing(3),
      width: theme.spacing(3),
      cursor: "pointer",
      transition: theme.transitions.create(["all"], {
        duration: theme.transitions.duration.complex,
      }),
      "&:hover": {
        transform: "scale(1.15)",
      },
    },
  }))();

const InputColorPicker = ({ presetColors, defautColor, label, onUpdate }) => {
  const popover = {
    position: "fixed",
    zIndex: "2",
  };

  const cover = {
    position: "fixed",
    top: "0px",
    right: "0px",
    bottom: "0px",
    left: "0px",
  };
  const classes = useStyles();

  const [isOpen, setIsOpen] = useState(false);
  const [color, setColor] = useState("");

  const handleChangeColor = (colorValue) => {
    setColor(colorValue);
    onUpdate(colorValue);
  };

  useEffect(() => {
    setColor(defautColor);
  }, [defautColor]);

  return (
    <div style={{ width: "100%" }}>
      <TextField
        autoFocus
        margin="dense"
        id="labelColorPicker"
        label={label}
        value={color}
        onChange={(e) => handleChangeColor(e?.target?.value || "")}
        fullWidth
        variant="outlined"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Box
                className={classes.colorBox}
                onClick={() => setIsOpen(true)}
                style={{ background: color }}
              />
            </InputAdornment>
          ),
        }}
      />
      {isOpen ? (
        <>
          <Box style={cover} onClick={() => setIsOpen(false)} />
          <div style={popover}>
            <SketchPicker
              color={color}
              disableAlpha={true}
              onChange={(e) => handleChangeColor(e.hex)}
              presetColors={presetColors}
            />
          </div>
        </>
      ) : null}
    </div>
  );
};

InputColorPicker.propTypes = {
  presetColors: PropTypes.array,
  defautColor: PropTypes.string.isRequired,
  onUpdate: PropTypes.func,
};

InputColorPicker.defaultProps = {
  presetColors: [],
  onUpdate: () => {},
};

export default InputColorPicker;
