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
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";
import Menu from "@mui/material/Menu";
import Tooltip from "@mui/material/Tooltip";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { getOperators, getOperatorText, getOperatorIcon } from "./FilterUtils";

const useStyles = makeStyles((theme) => ({
  typography: {
    padding: theme.spacing(2),
  },
  opButton: {
    padding: 0,
    minWidth: 20,
  },
}));

export default function FiterOptions({ column, onChange }) {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleOperatorClick = (operator) => {
    onChange(operator);
    handleClose();
  };

  const options = getOperators(column).map((row) => ({
    key: row,
    icon: getOperatorIcon(row),
    text: getOperatorText(row),
  }));
  return (
    <div>
      <Tooltip title={column.filterOperator || "Filter"}>
        <Button
          size="small"
          color={column.filterValue ? "primary" : undefined}
          aria-controls="split-button-menu"
          aria-expanded="true"
          aria-label="select merge strategy"
          aria-haspopup="menu"
          className={classes.opButton}
          onClick={handleClick}
        >
          {getOperatorIcon(column.filterOperator)}
          <ArrowDropDownIcon />
        </Button>
      </Tooltip>
      <Menu
        id="split-button-menu"
        open={Boolean(anchorEl)}
        onClose={handleClose}
        anchorEl={anchorEl}
      >
        {options.map((option) => (
          <MenuItem
            key={option.text}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            selected={column.currentOperator === option.key}
            onClick={() => handleOperatorClick(option.key)}
          >
            {getOperatorIcon(option.key)}
            <span style={{ marginLeft: 10 }}>{option.text}</span>
          </MenuItem>
        ))}
      </Menu>
    </div>
  );
}
