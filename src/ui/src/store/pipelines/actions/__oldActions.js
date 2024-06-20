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

// doesn't use 
export const preparePipeline = (
  projectUuid,
  pipelineUuid,
  pipelineName,
  pipelineSteps,
  cacheEnabled,
  deviceConfig
) => async (dispatch) => {
  await updatePipeline({
    projectUuid,
    pipelineUuid,
    pipelineName,
    pipelineSteps: [],
    cacheEnabled,
    deviceConfig
  })(dispatch);
  await updatePipeline({
    projectUuid,
    pipelineUuid,
    pipelineName,
    pipelineSteps,
    cacheEnabled,
    deviceConfig
  })(dispatch);
};

// Dosen't use with new version
export const checkOptimizationRequestStatus = (
  projectUuid,
  pipelineUuid,
  details
) => async (dispatch) => {
  /// old version TODO
  let dispatchObject = {};
  if (
    !helper.isNullOrEmpty(projectUuid) &&
    !helper.isNullOrEmpty(pipelineUuid)
  ) {
    try {
      if (details !== undefined) {
        details = await checkOptimizationRequestDetailedStatus(
          pipelineUuid,
          (details && details.results) || [],
          (details && details.timestamp) || undefined
        );
      }
      const { data: responseBody } = await api.get(
        `project/${projectUuid}/sandbox-async/${pipelineUuid}/`
      );
      if (responseBody && !responseBody.status) {
        dispatchObject = {
          type: FINISHED_OPTIMIZATION,
          pipelineUuid: pipelineUuid,
          status: "SUCCESS",
          message: "Automation Pipeline Completed.",
          details: details,
        };
      } else if (
        responseBody &&
        API_RUNNING_STATUS.includes(responseBody.status)
      ) {
        dispatchObject = {
          type: RUNNING_OPTIMIZATION,
          pipelineUuid: pipelineUuid,
          status: "RUNNING",
          message: responseBody.message,
          details: details,
        };
      } else if (responseBody && API_ERROR_STATUS.includes(responseBody.status)) {
        console.log(`ERROR ..`);
        console.log(responseBody);
        dispatchObject = {
          type: FAILED_OPTIMIZATION,
          pipelineUuid: pipelineUuid,
          status: "FAILURE",
          message: responseBody.message,
          details: details,
        };
      } else {
        dispatchObject = {
          type: RUNNING_OPTIMIZATION,
          pipelineUuid: pipelineUuid,
          status: "RUNNING",
          message: "Running Pipeline.",
          details: details,
        };
      }
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          err
        )}\n--projectId:${projectUuid},pipelineUuid:${pipelineUuid}`,
        err,
        "checkOptimizationRequestStatus"
      );
      dispatchObject = {
        type: RUNNING_OPTIMIZATION,
        pipelineUuid: pipelineUuid,
        status: "RUNNING",
        message: `Encountered an error while checking optimization status, will retry status check in ${process.env.REACT_APP_ASYNC_CHECK_INTERVAL / 1000
          } seconds....`,
        details: details,
      };
    }
    dispatch(dispatchObject);
  }
  return dispatchObject;
};

const checkOptimizationRequestDetailedStatus = async (
  pipelineUuid,
  details,
  endTimeStamp
) => {
  const detailedLogApi = axios.create({
    baseURL: process.env.REACT_APP_PIPELINE_RUN_LOG_API_URL,
    withCredentials: false,
    crossdomain: true,
    headers: {
      "X-Api-Key": process.env.REACT_APP_PIPELINE_RUN_LOG_API_KEY,
    },
  });

  const addMessages = (
    pipelineUuid,
    endIndex,
    sourceArray,
    lastMessage,
    lastTimeStamp
  ) => {
    let targetArray = [];
    let index = endIndex;
    try {
      while (
        index > 0 &&
        sourceArray[index].message &&
        sourceArray[index].message !== lastMessage &&
        (!lastTimeStamp || sourceArray[index].timestamp === lastTimeStamp)
      ) {
        index = index - 1;
      }
      for (var i = endIndex; i >= index; i--) {
        targetArray.push({ ...sourceArray[i], logid: uuidv4() });
      }
    } catch (err) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          err
        )}\n--checkOptimizationRequestDetailedStatus-addMessages--pipelineUuid:${pipelineUuid}`,
        err,
        "checkOptimizationRequestDetailedStatus-addMessages"
      );
    }
    return targetArray;
  };
  let end_time_stamp = undefined;
  try {
    const { data: responseBody } = await detailedLogApi.get(
      "/pipeline-run-log/",
      {
        params: { id: pipelineUuid, start_time_utc: endTimeStamp },
      }
    );
    if (responseBody && responseBody.results !== undefined) {
      const len = responseBody.results.length - 1;
      let startMessage = "Begining AutoML Execution";
      let lastTimeStamp = undefined;
      if (
        details &&
        details.length > 0 &&
        details[details.length - 1] !== undefined
      ) {
        startMessage = details[details.length - 1].message;
        lastTimeStamp = details[details.length - 1].timestamp;
      }
      details = addMessages(
        pipelineUuid,
        len,
        responseBody.results,
        startMessage,
        lastTimeStamp
      );
    }
    end_time_stamp = responseBody ? responseBody.timestamp : undefined;
  } catch (err) {
    logger.logError(
      "",
      `${helper.getResponseErrorDetails(
        err
      )}\n--checkOptimizationRequestDetailedStatus--pipelineUuid:${pipelineUuid}`,
      err,
      "checkOptimizationRequestDetailedStatus"
    );
  }
  return { timestamp: end_time_stamp, results: details };
};

