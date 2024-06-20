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
import {
  STORE_CAPTURES,
  LOADING_CAPTURES,
  STORE_CAPTURES_STATISTICS,
  LOADING_CAPTURES_STATISTICS,
  CLEAR_CAPTURES_STATISTICS,
  LOADING_CAPTURE_SENSOR_DATA,
  SET_CAPTURE_SENSOR_DATA,
} from "./actionTypes";

const initialCapturesState = { data: [], isFetching: false };
export const captures = (state = initialCapturesState, action) => {
  switch (action.type) {
    case LOADING_CAPTURES:
      return { data: [], isFetching: true };
    case STORE_CAPTURES:
      return { data: action.captures, isFetching: false };
    default:
      return state;
  }
};

const initialCapturesStatisticsState = { data: [], isFetching: false };
export const capturesStatistics = (state = initialCapturesStatisticsState, action) => {
  switch (action.type) {
    case LOADING_CAPTURES_STATISTICS:
      return { data: [], isFetching: true };
    case STORE_CAPTURES_STATISTICS:
      return { data: action.capturesStatistics, isFetching: false };
    case CLEAR_CAPTURES_STATISTICS:
      return { data: [], isFetching: false };
    default:
      return state;
  }
};

const initialCaptureSensorDataState = { data: [[]], isFetching: false };
export const captureSensorData = (state = initialCaptureSensorDataState, action) => {
  switch (action.type) {
    case LOADING_CAPTURE_SENSOR_DATA:
      return { data: [], isFetching: true };
    case SET_CAPTURE_SENSOR_DATA:
      return { data: action.payload, isFetching: false };
    default:
      return state;
  }
};

export default combineReducers({ captures, capturesStatistics, captureSensorData });
