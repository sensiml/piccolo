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

/* eslint-disable no-param-reassign */
/* eslint-disable no-use-before-define */
import { combineReducers } from "redux";
import { SET_PLATFORM_LOGOS, SET_LOADING_PLATFORM_LOGOS } from "./actionTypes";

export const platformLogos = (state = { data: [], isFetching: false }, action) => {
  const { type, payload } = action;
  switch (type) {
    case SET_LOADING_PLATFORM_LOGOS:
      return { data: {}, isFetching: true };
    case SET_PLATFORM_LOGOS:
      return { data: payload, isFetching: false };
    default:
      return state;
  }
};

export default combineReducers({ platformLogos });
