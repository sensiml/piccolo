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
import _ from "lodash";

import { useTranslation } from "react-i18next";
import { Alert, Box, Button } from "@mui/material";

import CheckBoxCard from "components/FormElements/CheckBoxCard";

import useStyles from "./PipelineTemplateCreateFormStyle";

const PipelineTemplateCreateFormParameters = ({ pipelines, onSubmit }) => {
  const { t } = useTranslation("pipelines");
  const classes = useStyles();

  const [selectedPipelineIndex, setSelectedPipelineindex] = useState(0);

  const handleSetSensorPipelineIndex = (index) => {
    setSelectedPipelineindex(index);
  };

  const handleSubmit = () => {
    onSubmit(selectedPipelineIndex);
  };

  const CheckBoxCardLabel = (sensors, info) => {
    return (
      <>
        <p>{info}</p>
        <p>
          {t("form-template-create.form-parameter-label-sensor", { sensors: _.join(sensors, ",") })}
        </p>
      </>
    );
  };

  return (
    <Box className={classes.dialogFormWrapper}>
      <Box>
        <Box className={classes.informationWrapper}>
          <Alert severity="info" height={"150px"} classes={{ root: classes.alertMessage }}>
            {t("form-template-create.alert-msg-parameters")}
          </Alert>
        </Box>
        {!_.isEmpty(pipelines) &&
          pipelines.map(({ sensors, info }, inx) => (
            <Box key={`${_.join(sensors, "_")}_${inx}`} className={classes.boxSelect}>
              <CheckBoxCard
                key={`pipline_checkbox_${inx}`}
                width={"100%"}
                name={"name"}
                label={CheckBoxCardLabel(sensors, info)}
                value={selectedPipelineIndex === inx}
                onChange={() => handleSetSensorPipelineIndex(inx)}
              />
            </Box>
          ))}
      </Box>
      <Box>
        <Button
          className={classes.submitBtn}
          color="primary"
          variant="contained"
          onClick={handleSubmit}
        >
          {t("form-template-create.step-parameters-btn")}
        </Button>
      </Box>
    </Box>
  );
};

export default PipelineTemplateCreateFormParameters;
