import api, { throwParsedApiError } from "store/api";
import { FEATURE_SAMPLE_SIZE_LIMIT } from "config";
import helper from "store/helper";
import logger from "store/logger";

export const getPipelineStepFeatureStats =
  (projectUUID, pipelineUUID, stepIndex = 0) =>
  async () => {
    let data;
    try {
      const response = await api.get(
        `project/${projectUUID}/sandbox/${pipelineUUID}/features-stats/`,
        {
          params: { pipeline_step: stepIndex, sample_size: FEATURE_SAMPLE_SIZE_LIMIT },
        },
      );
      data = response.data;
    } catch (error) {
      logger.logError(
        "",
        `${helper.getResponseErrorDetails(
          error,
        )}\n--projectId:${projectUUID},pipelineUuid:${pipelineUUID}`,
        error,
        "loadPipelineStats",
      );
      throwParsedApiError(error, "loading pipeline stats");
    }
    return data;
  };
