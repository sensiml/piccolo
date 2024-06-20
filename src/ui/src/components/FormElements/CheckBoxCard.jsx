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
import makeStyles from "@mui/styles/makeStyles";
import { Paper, Typography } from "@mui/material";

const useStyles = ({ width }) =>
  makeStyles((theme) => ({
    paperRoot: {
      borderStyle: "solid",
      width: width || theme.spacing(16),
      minHeight: theme.spacing(16),
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      borderWidth: "2px",
      cursor: "pointer",
      padding: `${theme.spacing(1)} ${theme.spacing(2)}`,
      boxSizing: "border-box",
      textAlign: "center",
      "&:hover": {
        background: theme.bakgroundPrimaryHighligth,
      },
    },
    checked: {
      borderColor: theme.palette.primary.main,
      background: theme.bakgroundPrimaryHighligth,
    },
  }))();

const CheckBoxCard = ({ id, value, width, defaultValue, name, label, onChange }) => {
  const classes = useStyles({ width });
  const [localVal, setLocalVal] = useState();

  useEffect(() => {
    if (!onChange) return;
    if (defaultValue) {
      onChange(name, defaultValue);
      setLocalVal(defaultValue);
    } else {
      onChange(name, false);
      setLocalVal(false);
    }
  }, []);

  useEffect(() => {
    setLocalVal(value);
  }, [value]);

  const handleChange = () => {
    if (localVal) {
      return;
    }
    if (onChange) {
      onChange(name, !localVal);
    }
    setLocalVal(!localVal);
  };

  return (
    <Paper
      classes={{ root: classes.paperRoot }}
      className={localVal ? classes.checked : ""}
      id={id}
      variant="outlined"
      onClick={handleChange}
    >
      <Typography component="span">{label}</Typography>
    </Paper>
  );
};

export default CheckBoxCard;
