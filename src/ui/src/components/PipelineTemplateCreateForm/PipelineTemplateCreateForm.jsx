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

import PipelineImportValidator from "store/containerBuildModel/domain/PipelineImportValidator";

import PipelineTemplateCreateInformation from "./PipelineTemplateCreateInformation";
import PipelineTemplateCreateFormParameters from "./PipelineTemplateCreateFormParameters";
import useStyles from "./PipelineTemplateCreateFormStyle";

const STEP_INFORMATION = 0;
const STEP_SENSORS = 1;
const STEP_CREATE = 2;

const PipelineTemplateCreateForm = ({
  pipelineTemplate,
  pipelineError,
  queriesFormOptions,
  queryInputData,
  onSubmit,
  loadingPipelineSteps,
}) => {
  const steps = ["Template Information", "Select Pipeline", "Select Parameters"];
  const classes = useStyles();
  const [activeStep, setActiveStep] = useState(STEP_INFORMATION);

  const [pipelineJson, setPipelineJson] = useState({});
  const [pipelineParams, setPipelineParams] = useState({});

  const importedColumns = useMemo(() => {
    return pipelineParams?.sensorColumns || [];
  }, [pipelineParams]);

  const handleSensorNext = (index) => {
    setPipelineJson({ ...pipelineTemplate.pipelines[index] });
    const validator = new PipelineImportValidator(pipelineTemplate.pipelines[index].pipeline);
    validator.validatePipeline();
    if (validator.isValidPipeline) {
      setPipelineParams(validator.extractQueryInputData());
    }
    setActiveStep(STEP_CREATE);
  };

  const handleInfoNext = () => {
    setActiveStep(STEP_SENSORS);
  };

  const handleCreate = (pipelineName, queryName, isUseSessionPreprocessor, replacedColumns) => {
    const disableAutoML = pipelineJson.hyper_params?.params?.disable_automl || false;
    onSubmit({
      pipelineName,
      isAutoMLOptimization: !disableAutoML,
      pipelineJson,
      queryName,
      replacedColumns,
      isUseSessionPreprocessor,
    });
  };

  return (
    <Box className={classes.dialogFormContainer}>
      <Stepper
        classes={{ root: classes.dialogStepperRoot }}
        alternativeLabel
        activeStep={activeStep}
      >
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      {activeStep === STEP_INFORMATION ? (
        <PipelineTemplateCreateInformation
          img={pipelineTemplate.img}
          name={pipelineTemplate.name}
          summary={pipelineTemplate.summary}
          onSubmit={handleInfoNext}
        />
      ) : activeStep === STEP_SENSORS ? (
        <PipelineTemplateCreateFormParameters
          pipelines={pipelineTemplate.pipelines}
          onSubmit={handleSensorNext}
        />
      ) : (
        <PipelineQueryCreateForm
          importedColumns={importedColumns}
          importedQueryName={pipelineParams?.queryName}
          importedIsUseSessionPreprocessor={pipelineParams?.isUseSessionPreprocessor}
          pipelineError={pipelineError}
          loadingPipelineSteps={loadingPipelineSteps}
          queriesFormOptions={queriesFormOptions}
          queryInputData={queryInputData}
          onSubmit={handleCreate}
        />
      )}
    </Box>
  );
};

export default PipelineTemplateCreateForm;
