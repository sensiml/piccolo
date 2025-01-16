import _ from "lodash";

import api, { throwParsedApiError } from "store/api";
import { FEATURE_SAMPLE_SIZE_LIMIT } from "config";
import helper from "store/helper";
import logger from "store/logger";

export const getPipelineStepFeatureStats =
  (projectUUID, pipelineUUID, stepIndex = 0) =>
  async () => {
    const getLabelValuesFromDataTable = (dataTable, labelKey) => {
      if (dataTable && dataTable[labelKey]) {
        return [...new Set(dataTable[labelKey])];
      }
      return [];
    };

    let data;
    try {
      const response = await api.get(
        `project/${projectUUID}/sandbox/${pipelineUUID}/features-stats/`,
        {
          params: { pipeline_step: stepIndex, sample_size: FEATURE_SAMPLE_SIZE_LIMIT },
        },
      );

      const featureStatsData = response.data;

      const labelValues = getLabelValuesFromDataTable(
        featureStatsData.feature_data,
        featureStatsData.label_column,
      );

      data = {
        featureVectorData: featureStatsData.feature_data,
        featureStatistics: featureStatsData.feature_statistics,
        featureSummary: featureStatsData.feature_summary,
        featureNames: _.keys(featureStatsData.feature_data),
        labelColumn: featureStatsData.label_column,
        labelValues,
      };
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
