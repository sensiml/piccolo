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
  DELETING_PROJECT,
  DELETED_PROJECT,
  LOADING_PROJECT_STATISTICS,
  STORE_PROJECT_STATISTICS,
  LOADING_PROJECTS,
  STORE_PROJECTS,
  STORE_SELECTED_PROJECT,
  STORE_LAST_SELECTED_PROJECT,
  UPDATING_PROJECT,
  UPDATED_PROJECT,
  DIRTY_PROJECT,
} from "./actionTypes";

const initalProjectList = { data: [], isFetching: false };
export function projectList(state = initalProjectList, action) {
  switch (action.type) {
    case LOADING_PROJECTS:
      return { data: [], isFetching: true };
    case STORE_PROJECTS:
      return { data: action.projects, isFetching: false };
    case DELETING_PROJECT:
      return { data: [], isFetching: true };
    case DELETED_PROJECT:
      return { data: action.projects, isFetching: false };
    case UPDATING_PROJECT:
      return { data: [], isFetching: true };
    case UPDATED_PROJECT:
      return { data: action.projects, isFetching: false };
    case DIRTY_PROJECT:
      return { data: action.projects, isFetching: false };
    default:
      return state;
  }
}

export function selectedProject(state = {}, action) {
  switch (action.type) {
    case STORE_SELECTED_PROJECT:
      return action.selectedProject || "";
    default:
      return state;
  }
}

export const lastSelectedProjects = (state = {}, action) => {
  switch (action.type) {
    case STORE_LAST_SELECTED_PROJECT:
      return { ...state, ...action.selectedProject };
    default:
      return state;
  }
};

export function projectStatistics(state = [], action) {
  switch (action.type) {
    case LOADING_PROJECT_STATISTICS:
      return { data: [], isFetching: true };
    case STORE_PROJECT_STATISTICS:
      return { data: action.statistics, isFetching: false };
    default:
      return state;
  }
}

export default combineReducers({
  selectedProject,
  lastSelectedProjects,
  projectList,
  projectStatistics,
});
