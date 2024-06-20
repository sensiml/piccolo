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

import React from "react";

import { useTheme } from "@mui/material/styles";
import makeStyles from "@mui/styles/makeStyles";
import LocalParkingIcon from "@mui/icons-material/LocalParking";
import { Box } from "@mui/material";
import { useTranslation } from "react-i18next";
import filters from "filters";
import { IconKnowledgepack, IconDateEdit } from "components/UIIcons";
import Typography from "@mui/material/Typography";

const useStyles = () =>
  makeStyles(() => ({
    pipelineDataWrapper: {
      boxSizing: "border-box",
      width: "100%",
      padding: "0 1rem",
    },
    pipelineDataItemWrapper: {
      display: "grid",
      gridTemplateColumns: "2.5rem auto",
      alignContent: "center",
      justifyContent: "start",
      alignItems: "center",
      marginBottom: "1rem",
    },
  }))();

export default ({ pipelineName, KPCount, editDate }) => {
  const classes = useStyles();
  const theme = useTheme();
  const { t } = useTranslation("models");

  return (
    <Box className={classes.pipelineDataWrapper}>
      <Box className={classes.pipelineDataItemWrapper}>
        <LocalParkingIcon style={{ color: theme.colorLightBrandIcon }} />
        <Box>
          <Typography variant="h5">{t("model-builder-select.ppl-card-name")}</Typography>
          <Typography>{pipelineName}</Typography>
        </Box>
      </Box>
      <Box className={classes.pipelineDataItemWrapper}>
        <IconKnowledgepack style={{ color: theme.colorLightBrandIcon }} />
        <Box>
          <Typography variant="h5">{t("model-builder-select.ppl-card-kp-data-count")}</Typography>
          <Typography>{KPCount}</Typography>
        </Box>
      </Box>
      <Box className={classes.pipelineDataItemWrapper}>
        <IconDateEdit style={{ color: theme.colorLightBrandIcon }} />
        <Box>
          <Typography variant="h5">{t("model-builder-select.ppl-card-edit-date")}</Typography>
          <Typography>{filters.filterFormatDate(editDate)}</Typography>
        </Box>
      </Box>
    </Box>
  );
};
