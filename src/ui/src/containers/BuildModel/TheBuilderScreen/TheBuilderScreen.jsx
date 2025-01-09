/* eslint-disable no-unused-vars */
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
import React, { useEffect, useState } from "react";
import {
  Button,
  Box,
  CircularProgress,
  Typography,
  Link,
  Tooltip,
  FormControlLabel,
  Checkbox,
  Stack,
} from "@mui/material";

import makeStyles from "@mui/styles/makeStyles";
import DialogInformation from "components/DialogInformation";

const useStyles = (navBarIsOpen) =>
  makeStyles((theme) => ({
    infoTitle: {
      marginBottom: theme.spacing(4),
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(4),
      fontWeight: 500,
      textAlign: "center",
    },
  }))();

const TheBuilderScreen = ({
  children,

  pipelineData,
  selectedPipelineName,
  clearAlertBuilder,
  clearPipelineValidationError,
  clearOptimizationLogs,
  clearPipelineResults,
  clearPipelineStatus,
  clearPipeline,
  clearQueryCacheStatus,
  clearPipelineExecutionType,
  setSelectedPipelineName,
  ...props
}) => {
  const classes = useStyles();
  const [dialogInformationData, setDialogInformationData] = useState({});

  const stopOptimizationChecker = () => {
    clearOptimizationLogs();
    clearPipelineResults();
  };

  useEffect(() => {
    if (pipelineData?.name && pipelineData.name !== selectedPipelineName) {
      setSelectedPipelineName(pipelineData.name);
    }
  }, [pipelineData]);

  useEffect(() => {
    return () => [
      clearPipeline(),
      clearPipelineExecutionType(),
      clearAlertBuilder(),
      clearPipelineValidationError(),
      clearQueryCacheStatus(),
      clearPipelineStatus(),
      stopOptimizationChecker(),
    ];
  }, []);

  const handleShowInformation = (title, text) => {
    setDialogInformationData({ title, text });
  };

  const handleCloseNewStepDialogInformation = () => {
    setDialogInformationData({});
  };

  return (
    <>
      {children({
        clearAlertBuilder,
        clearOptimizationLogs,
        clearPipelineResults,
        clearPipelineStatus,
        clearQueryCacheStatus,
        pipelineData,
        onShowInformation: handleShowInformation,
        ...props,
      })}
      <DialogInformation
        isOpen={Boolean(dialogInformationData.title)}
        onClose={handleCloseNewStepDialogInformation}
      >
        <Typography variant="h2" className={classes.infoTitle}>
          {dialogInformationData.title}
        </Typography>
        <Typography paragraph>
          <p style={{ whiteSpace: "pre-wrap" }}>{dialogInformationData.text}</p>
        </Typography>
      </DialogInformation>
    </>
  );
};

export default TheBuilderScreen;
