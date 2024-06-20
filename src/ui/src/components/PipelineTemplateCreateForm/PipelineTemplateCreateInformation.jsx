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

import { Box, Button, Grow, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";
import { ElementLoader } from "components/UILoaders";

import useStyles from "./PipelineTemplateCreateFormStyle";

const PipelineTemplateCreateInformation = ({ img, name, summary, onSubmit }) => {
  const { t } = useTranslation("pipelines");
  const classes = useStyles();

  const [isImageLoaded, setIsImageLoaded] = useState(false);

  const handleSubmit = () => {
    onSubmit();
  };

  return (
    <Box className={classes.dialogFormWrapper}>
      <Box>
        <Grow in={isImageLoaded}>
          <Box className={classes.imageWrapper || !img}>
            {!isImageLoaded ? <ElementLoader isOpen={!isImageLoaded} /> : null}
            <img src={img} alt={"img"} onLoad={() => setIsImageLoaded(true)} />
          </Box>
        </Grow>
        <Typography align="center" display="block" variant="h2">
          {name}
        </Typography>
        <Box mt={2} mb={2}>
          <p className={classes.description}>{summary}</p>
        </Box>
      </Box>
      <Box className={classes.formWrapperButton}>
        <Button
          className={classes.submitBtn}
          color="primary"
          variant="contained"
          onClick={handleSubmit}
        >
          {t("form-template-create.step-info-btn")}
        </Button>
      </Box>
    </Box>
  );
};

export default PipelineTemplateCreateInformation;
