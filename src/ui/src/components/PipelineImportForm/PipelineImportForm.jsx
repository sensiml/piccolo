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

import React, { useState, useMemo } from "react";
import { Box, Stepper, Step, StepLabel } from "@mui/material";

import PipelineQueryCreateForm from "components/PipelineQueryCreateForm";

import useStyles from "./PipelineImportStyles";
import PipelineImportFormImport from "./PipelineImportFormImport";

const steps = ["Import Pipeline", "Verify data"];

const STEP_IMPORT = 0;
const STEP_REVIEW = 1;

const PipelineImportForm = ({
  pipelineError,
  queriesFormOptions,
  queryInputData,
  onSubmit,
  loadingPipelineSteps,
}) => {
  const classes = useStyles();
  const [activeStep, setActiveStep] = useState(STEP_IMPORT);
  const [pipelineJson, setPipelineJson] = useState({});
  const [pipelineParams, setPipelineParams] = useState({});

  const importedColumns = useMemo(() => {
    return pipelineParams?.sensorColumns || [];
  }, [pipelineParams]);

  const handleImport = (data, params) => {
    setActiveStep(STEP_REVIEW);
    setPipelineJson(data);
    setPipelineParams(params);
  };

  const handleCreate = (pipelineName, queryName, isUseSessionPreprocessor, replacedColumns) => {
    onSubmit({
      pipelineName,
      pipelineJson,
      queryName,
      replacedColumns,
      isUseSessionPreprocessor,
    });
  };

  return (
    <Box className={classes.dialogFormContainer}>
      <Stepper
        classes={{ root: classes.importDialogStepperRoot }}
        alternativeLabel
        activeStep={activeStep}
      >
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      <Box className={classes.builderFormWrapper}>
        {activeStep === STEP_IMPORT ? (
          <PipelineImportFormImport
            queriesFormOptions={queriesFormOptions}
            onSubmit={handleImport}
          />
        ) : (
          <PipelineQueryCreateForm
            importedColumns={importedColumns}
            importedQueryName={pipelineParams?.queryName}
            importedIsUseSessionPreprocessor={pipelineParams?.isUseSessionPreprocessor}
            queryInputData={queryInputData}
            pipelineError={pipelineError}
            onSubmit={handleCreate}
            loadingPipelineSteps={loadingPipelineSteps}
          />
        )}
      </Box>
    </Box>
  );
};

export default PipelineImportForm;
