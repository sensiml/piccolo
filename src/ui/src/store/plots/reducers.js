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

import { combineReducers } from "redux";
import { STORE_PLOTS, STORE_PLOT } from "./actionTypes";

const initialPlotState = [];
export function plotsData(state = initialPlotState, action) {
  switch (action.type) {
    case STORE_PLOTS:
      return action.plots;
    default:
      return state;
  }
}

const initialSelectedPlotState = "segment";
export function selectedPlot(state = initialSelectedPlotState, action) {
  switch (action.type) {
    case STORE_PLOT:
      return action.plotId;
    default:
      return state;
  }
}

export default combineReducers({
  selectedPlot,
  plotsData,
});
