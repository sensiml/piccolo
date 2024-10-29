import React, { useMemo } from "react";
import _ from "lodash";

import { Alert, Box, Fade } from "@mui/material";

import { useTranslation } from "react-i18next";

const PipelineBuilderAlertMessage = ({
  pipelineAlert,
  queryStatistic,
  isPipelineHasEmptySteps = false,
  pipelineValidationError = "",
}) => {
  const { t: tQueries } = useTranslation("queries");
  const { t } = useTranslation("models");

  const alertMessage = useMemo(() => {
    if (pipelineValidationError) {
      return { message: pipelineValidationError, type: "error" };
    }
    if (pipelineAlert?.message) {
      return pipelineAlert;
    }
    if (isPipelineHasEmptySteps) {
      return { message: t("model-builder.warning-if-not-filled"), type: "error" };
    }
    if (queryStatistic?.segments && _.isEmpty(_.keys(queryStatistic?.segments))) {
      return {
        message: (
          <>
            {tQueries("validation.no-segments", { queryName: queryStatistic?.name })}
            <Box mt={1}>{tQueries("help.unknow")}</Box>
          </>
        ),
        type: "warning",
      };
    }
    if (queryStatistic?.segments && _.keys(queryStatistic?.segments)?.length < 2) {
      return {
        message: (
          <>
            {tQueries("validation.not-enough-segments", {
              queryName: queryStatistic?.name,
              segments: _.keys(queryStatistic?.segments).join(", "),
            })}
            <Box mt={1}>{tQueries("help.unknow")}</Box>
          </>
        ),
        type: "warning",
      };
    }
    return {};
  }, [pipelineValidationError, pipelineAlert, isPipelineHasEmptySteps, queryStatistic]);

  return alertMessage.message ? (
    <Fade in={Boolean(alertMessage.message)}>
      <Box mb={1}>
        <Alert variant="outlined" severity={alertMessage.type}>
          {alertMessage.message}
        </Alert>
      </Box>
    </Fade>
  ) : null;
};

export default PipelineBuilderAlertMessage;
