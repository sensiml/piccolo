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
import { Button, ButtonGroup } from "@mui/material";

import AppsIcon from "@mui/icons-material/Apps";
import MenuIcon from "@mui/icons-material/Menu";

const GRID_VIEW = 0;
const TABLE_VIEW = 1;

const UISwitchViewTableGrid = ({ gridValue, tableValue, activeView, onChange }) => {
  const getColor = (view) => {
    return view === activeView ? "primary" : "red";
  };

  const handleSwitch = (view) => {
    onChange(view);
  };

  return (
    <ButtonGroup size="large">
      <Button
        onClick={() => handleSwitch(gridValue || GRID_VIEW)}
        color={getColor(gridValue || GRID_VIEW)}
      >
        <AppsIcon />
      </Button>
      <Button
        onClick={() => handleSwitch(tableValue || TABLE_VIEW)}
        color={getColor(tableValue || TABLE_VIEW)}
      >
        <MenuIcon />
      </Button>
    </ButtonGroup>
  );
};

export default UISwitchViewTableGrid;
