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
import {
  ADD_PIPELINE,
  UPDATING_PIPELINE,
  UPDATED_PIPELINE,
  STORE_SELECTED_PIPELINE,
  STORE_PIPELINES,
  LOADING_PIPELINES,
  LOADING_PIPELINE_DATA,
  STORE_PIPELINE_DATA,
  LOADING_PIPELINE_SEEDS,
  STORE_PIPELINE_SEEDS,
  LOADING_PIPELINES_RESULTS,
  STORE_PIPELINE_RESULTS,
  CLEAR_PIPELINE_RESULTS,
  SUBMITING_OPTIMIZATION_REQUEST,
  SUBMITED_OPTIMIZATION_REQUEST,
  FINISHED_OPTIMIZATION,
  RUNNING_OPTIMIZATION,
  FAILED_OPTIMIZATION,
  KILLING_OPTIMIZATION_REQUEST,
  KILLING_OPTIMIZATION_FAILED,
  OPTIMIZATION_REQUEST_KILLED,
  OPTIMIZATION_REQUEST_NOT_STARTED,
  CLEAR_OPTIMIZATION_REQUEST_STATUS,
  UPDATE_OPTIMIATION_LOGS,
  CLEAR_OPTIMIATION_LOGS,
  UPDATE_OPTIMIATION_DETAILED_LOGS,
  CLEAR_OPTIMIATION_DETAILED_LOGS,
  LOAD_ITERATION_METRICS,
  UPDATE_ITERATION_METRICS,
  CLEAR_ITERATION_METRICS,
  STORE_PIPELINE_STATUS,
} from "./actionTypes";
import { RUNNING_STATUS } from "./status";

const initialPipelinesState = { data: [], isFetching: false };
export function pipelineList(state = initialPipelinesState, action) {
  switch (action.type) {
    case LOADING_PIPELINES:
      return { data: [], isFetching: true };
    case STORE_PIPELINES:
      return { data: action.pipelines, isFetching: false };
    default:
      return state;
  }
}

export function selectedPipeline(state = "", action) {
  switch (action.type) {
    case STORE_SELECTED_PIPELINE:
      return action.selectedPipeline;
    case ADD_PIPELINE:
      return action.selectedPipeline;
    case UPDATING_PIPELINE:
      return action.updatingPipeline;
    case UPDATED_PIPELINE:
      return action.updatedPipeline;
    default:
      return state;
  }
}

export const pipelineResults = (state = { data: {}, isFetching: false }, action) => {
  switch (action.type) {
    case LOADING_PIPELINES_RESULTS:
      return { data: [], isFetching: true };
    case STORE_PIPELINE_RESULTS:
      return { data: action.results, isFetching: false };
    case CLEAR_PIPELINE_RESULTS:
      return { data: {}, isFetching: false };
    default:
      return state;
  }
};

const initialPipelineSeedsState = { data: [], isFetching: false };
export function seedList(state = initialPipelineSeedsState, action) {
  switch (action.type) {
    case LOADING_PIPELINE_SEEDS:
      return { data: [], isFetching: true };
    case STORE_PIPELINE_SEEDS:
      return { data: action.seeds, isFetching: false };
    default:
      return state;
  }
}

const initialPipelineDataState = { data: {}, isFetching: false };
export const pipelineData = (state = initialPipelineDataState, action) => {
  switch (action.type) {
    case LOADING_PIPELINE_DATA:
      return { data: {}, isFetching: true };
    case STORE_PIPELINE_DATA:
      return { data: action.payload, isFetching: false };
    default:
      return state;
  }
};

export function pipelineRun(state = [], action) {
  // TODO not using keeping for support first version until get stable 2nd version
  switch (action.type) {
    case SUBMITING_OPTIMIZATION_REQUEST:
      setPipelineStatus(state, action, "SUBMITTING");
      return state;
    case SUBMITED_OPTIMIZATION_REQUEST:
      setPipelineStatus(state, action, "SUBMITTED");
      return state;
    case FINISHED_OPTIMIZATION:
      setPipelineStatus(state, action, "FINISHED");
      return state;
    case RUNNING_OPTIMIZATION:
      setPipelineStatus(state, action, "RUNNING");
      return state;
    case FAILED_OPTIMIZATION:
      setPipelineStatus(state, action, "FAILED");
      return state;
    case KILLING_OPTIMIZATION_REQUEST:
      setPipelineStatus(state, action, "KILLING");
      return state;
    case KILLING_OPTIMIZATION_FAILED:
      setPipelineStatus(state, action, "FAILED_ABORT");
      return state;
    case OPTIMIZATION_REQUEST_KILLED:
      setPipelineStatus(state, action, "KILLED");
      return state;
    default:
      return state;
  }
}

export const pipelineRunningStatus = (state = "", action) => {
  switch (action.type) {
    // submitting
    case SUBMITING_OPTIMIZATION_REQUEST:
      return RUNNING_STATUS.RUNNING;

    case SUBMITED_OPTIMIZATION_REQUEST:
      return RUNNING_STATUS.RUNNING;

    // runnig
    case RUNNING_OPTIMIZATION:
      return RUNNING_STATUS.RUNNING;

    case FINISHED_OPTIMIZATION:
      return RUNNING_STATUS.COMPLETED;

    case FAILED_OPTIMIZATION:
      return RUNNING_STATUS.FAILED;

    // killing
    case KILLING_OPTIMIZATION_REQUEST:
      return RUNNING_STATUS.KILLING;

    case KILLING_OPTIMIZATION_FAILED:
      return RUNNING_STATUS.KILLING_ABORTED;

    case OPTIMIZATION_REQUEST_KILLED:
      return RUNNING_STATUS.KILLED;

    case OPTIMIZATION_REQUEST_NOT_STARTED:
      return RUNNING_STATUS.NOT_STARTED;

    case CLEAR_OPTIMIZATION_REQUEST_STATUS:
      return "";

    default:
      return state;
  }
};

const pipelineDetailedStatusState = { data: {} };
export const pipelineStatus = (state = pipelineDetailedStatusState, action) => {
  switch (action.type) {
    case STORE_PIPELINE_STATUS:
      return { data: action.payload };
    default:
      return state;
  }
};

function setPipelineStatus(state, retStatus, optRequestStatus) {
  if (!state[retStatus.pipelineUuid]) {
    state[retStatus.pipelineUuid] = {
      uuid: retStatus.pipelineUuid,
      status: "",
      messages: [],
    };
  }
  /**
   * If re-running the pipeline clear the previous messages and status
   */

  if (["FINISHED", "SUCCESS", "FAILED", "KILLED"].includes(state[retStatus.pipelineUuid].status)) {
    state[retStatus.pipelineUuid].messages = [];
    state[retStatus.pipelineUuid].status = "";
  }
  state[retStatus.pipelineUuid].uuid = retStatus.pipelineUuid;
  state[retStatus.pipelineUuid].status = optRequestStatus;
  state[retStatus.pipelineUuid].messages.push(retStatus.message);
}

export const optimizationLogs = (state = [{ message: [] }], action) => {
  const { type, payload } = action;
  switch (type) {
    case UPDATE_OPTIMIATION_LOGS:
      return [...payload];
    case CLEAR_OPTIMIATION_LOGS:
      return [];
    default:
      return state;
  }
};

export const optimizationDetailedLogs = (
  state = { logs: [], lastTimeStamp: undefined },
  action,
) => {
  const { type, payload } = action;
  switch (type) {
    case UPDATE_OPTIMIATION_DETAILED_LOGS:
      return { ...payload };
    case CLEAR_OPTIMIATION_DETAILED_LOGS:
      return { ...state, logs: [] };
    default:
      return state;
  }
};

export const iterationMetrics = (state = { data: [] }, action) => {
  const { type, payload } = action;
  switch (type) {
    case UPDATE_ITERATION_METRICS:
      return { data: [...payload] };
    case LOAD_ITERATION_METRICS:
      return { data: [] };
    case CLEAR_ITERATION_METRICS:
      return { data: [] };
    default:
      return state;
  }
};

export default combineReducers({
  selectedPipeline,
  pipelineList,
  pipelineData,
  pipelineResults,
  seedList,
  pipelineRunningStatus,
  pipelineStatus,
  pipelineRun,
  optimizationLogs,
  optimizationDetailedLogs,
  iterationMetrics,
});
