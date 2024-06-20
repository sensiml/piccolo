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
  LOADING_TEAM_INFO,
  STORE_TEAM_INFO,
  LOADING_ACCOUNT_API_KEYS,
  STORE_ACCOUNT_API_KEYS,
} from "./actionTypes";

const initialTeamInfoState = { data: {}, isFetching: false };
const initialAccountApiKeysState = { data: [], isFetching: false };

export const teamInfo = (state = initialTeamInfoState, action) => {
  switch (action.type) {
    case LOADING_TEAM_INFO:
      return { data: [], isFetching: true };
    case STORE_TEAM_INFO:
      return { data: action.payload, isFetching: false };
    default:
      return state;
  }
};

export const accountApiKeys = (state = initialAccountApiKeysState, action) => {
  switch (action.type) {
    case LOADING_ACCOUNT_API_KEYS:
      return { data: [], isFetching: true };
    case STORE_ACCOUNT_API_KEYS:
      return { data: action.payload, isFetching: false };
    default:
      return state;
  }
};

export default combineReducers({ teamInfo, accountApiKeys });
