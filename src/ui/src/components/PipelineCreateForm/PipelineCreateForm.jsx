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

import React, { useState } from "react";
import { Box, Stepper, Step, StepLabel } from "@mui/material";
import { useTranslation } from "react-i18next";
import { DEFAULT_CLASSIFIER } from "consts";

import PipelineQueryCreateForm from "components/PipelineQueryCreateForm";

import useStyles from "./PipelineCreateStyles";
import PipelineCreateFormParameters from "./PipelineCreateFormParameters";

const STEP_PARAMS = 0;
const STEP_CREATE = 1;

const PipelineCreateForm = ({
  classifiers,
  pipelineError,
  queriesFormOptions,
  queryInputData,
  onSubmit,
  loadingPipelineSteps,
}) => {
  const { t } = useTranslation("pipelines");
  const steps = [t("form-create.step-select-params"), t("form-create.step-create-pipeline")];
  const classes = useStyles();
  const [activeStep, setActiveStep] = useState(STEP_PARAMS);

  const [isAutoMLOptimization, setIsAutoMLOptimization] = useState(true);
  const [selectedClassifier, setSelectedClassifier] = useState();

  const handleSubmitParams = (params) => {
    setIsAutoMLOptimization(params.isAutoMLOptimization);
    setSelectedClassifier(params.selectedClassifier);
    setActiveStep(STEP_CREATE);
  };

  const handleCreate = (pipelineName, queryName, isUseSessionPreprocessor) => {
    onSubmit({
      pipelineName,
      queryName,
      isUseSessionPreprocessor,
      isAutoMLOptimization,
      selectedClassifier,
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
      {activeStep === STEP_PARAMS ? (
        <PipelineCreateFormParameters
          classifiers={classifiers}
          defaultClassifier={DEFAULT_CLASSIFIER}
          onSubmit={handleSubmitParams}
        />
      ) : (
        <PipelineQueryCreateForm
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

export default PipelineCreateForm;
