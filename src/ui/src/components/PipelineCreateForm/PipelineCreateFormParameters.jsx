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

import React, { useState, useCallback, useEffect } from "react";
import _ from "lodash";

import { Button, Box, FormControlLabel, Switch, Typography, Collapse } from "@mui/material";
import { useTranslation } from "react-i18next";
import CheckBoxCard from "components/FormElements/CheckBoxCard";

import { UIAlertScrolled } from "components/UIAlerts";

import useStyles from "./PipelineCreateStyles";

const PipelineCreateFormParameters = ({ classifiers, defaultClassifier, onSubmit }) => {
  const { t } = useTranslation("pipelines");
  const classes = useStyles();
  const [description, setDescription] = useState(t("form-create.create-new-pipeline-decs-automl"));
  const [isAutoMLOptimization, setIsAutoMLOptimization] = useState(true);
  const [selectedClassifier, setSelectedClassifier] = useState();

  const getIsSelectedClassifier = useCallback(
    (name) => {
      return selectedClassifier === name;
    },
    [selectedClassifier],
  );

  useEffect(() => {
    if (!selectedClassifier && defaultClassifier) {
      setSelectedClassifier(defaultClassifier);
    }
  }, []);

  const handleSetDescription = (desc) => {
    setDescription(desc);
  };

  const handleChangeIsAutoML = () => {
    setIsAutoMLOptimization((value) => {
      if (!value) {
        handleSetDescription(t("form-create.create-new-pipeline-decs-automl"));
      } else if (selectedClassifier) {
        const classifierToSet = classifiers.find((el) => el.name === selectedClassifier);
        setDescription(classifierToSet.description);
      }
      return !value;
    });
  };

  const handleSelectClassifier = (name, desc) => {
    setSelectedClassifier(name);
    if (!isAutoMLOptimization) {
      handleSetDescription(desc);
    }
  };

  const handleSubmit = () => {
    onSubmit({ isAutoMLOptimization, selectedClassifier });
  };

  return (
    <Box className={classes.dialogFormWrapper}>
      <Box>
        <Box xs={12} md={12} className={classes.descriptionWrapper}>
          <UIAlertScrolled severity="info" className={classes.builderDescription}>
            {description}
          </UIAlertScrolled>
        </Box>
        <Box className={classes.formIsAutoMLWrapper}>
          <FormControlLabel
            control={
              <Switch
                // disabled={isPipelineHasNotFilledSteps}
                onChange={handleChangeIsAutoML}
                checked={isAutoMLOptimization}
                name="isAutoMLOptimization"
                inputProps={{ "aria-label": "primary checkbox" }}
              />
            }
            label={t("form-create.parameter-form-is-automl-label")}
          />
        </Box>
        <Box>
          <Collapse in={!isAutoMLOptimization}>
            <Box className={classes.formClassifiersWrapper} textAlign="center">
              <Typography component="p" variant={"h4"}>
                {t("form-create.parameter-form-classification-desc")}
              </Typography>
              <Box xs={12} md={12} className={classes.formCheckBoxWrapper}>
                {_.map(classifiers, (classifier, index) => (
                  <CheckBoxCard
                    key={`classifier_checkbox_${index}`}
                    width={"100%"}
                    label={classifier.name}
                    name={classifier.name}
                    defaultValue={defaultClassifier === classifier.name}
                    value={getIsSelectedClassifier(classifier.name)}
                    onChange={() => {
                      handleSelectClassifier(classifier.name, classifier.description || "");
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Collapse>
        </Box>
      </Box>
      <Box className={classes.formWrapper}>
        <Button color="primary" variant="contained" onClick={handleSubmit}>
          {t("form-create.parameter-form-button")}
        </Button>
      </Box>
    </Box>
  );
};

export default PipelineCreateFormParameters;
