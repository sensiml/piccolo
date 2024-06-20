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
import { combineReducers } from "redux";
import {
  START_CLASSIFIER_RUN,
  ADD_CLASSIFIER_TO_CACHE,
  CLEAR_CLASSIFIER_TO_CACHE,
  END_CLASSIFIER_RUN,
  STOP_CLASSIFIER_RUN,
  STOPPED_CLASSIFIER_RUN,
} from "./actionTypes";

const initialClassifierRunState = { data: [], isFetching: false };
export function classifierRun(state = initialClassifierRunState, action) {
  switch (action.type) {
    case START_CLASSIFIER_RUN:
      return { status: action.status, isFetching: true };
    case STOP_CLASSIFIER_RUN:
      return { status: action.status, isFetching: true };
    case STOPPED_CLASSIFIER_RUN:
      return { status: action.status, isFetching: false };
    case END_CLASSIFIER_RUN:
      return { isFetching: false };
    default:
      return state;
  }
}

export function classifierCache(state = [], action) {
  switch (action.type) {
    case ADD_CLASSIFIER_TO_CACHE:
      if (action.classifierData && Object.keys(action.classifierData).length > 0) {
        // eslint-disable-next-line array-callback-return
        Object.values(action.classifierData).map((cd) => {
          if (state[cd.cacheKey] === undefined) {
            state[cd.cacheKey] = cd;
          }
        });
      }
      return state;
    case CLEAR_CLASSIFIER_TO_CACHE:
      return [];
    default:
      return state;
  }
}

export default combineReducers({
  classifierRun,
  classifierCache,
});
