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
import { useTranslation } from "react-i18next";
import { Box, Paper, Tooltip } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import AddBoxOutlinedIcon from "@mui/icons-material/AddBoxOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import FlowBuilderStyles from "../FlowBuilderStyles";

const NewCardStep = ({ className, icon, children, helpInfo, helpEdit, helpDelete }) => {
  const { t } = useTranslation("common");
  const classes = FlowBuilderStyles();
  const theme = useTheme();

  return (
    <Paper
      elevation={0}
      className={`${classes.cardStepWrapper} ${classes.cardStepRegularNew} ${className || ""}`}
      style={{ borderColor: theme.IconWrap }}
    >
      <Box className={classes.IconWrap}>{icon || <AddBoxOutlinedIcon color="primary" />}</Box>
      <Box className={classes.TextWrap}>{children || null}</Box>
      <Box className={classes.ActionWrap}>
        <Tooltip title={helpInfo || t("flow-builder.card-step-help-info")} placement="top">
          <InfoOutlinedIcon style={{ color: theme.colorNewItems }} />
        </Tooltip>
        <Tooltip title={helpEdit || t("flow-builder.card-step-edit-info")} placement="top">
          <EditOutlinedIcon style={{ color: theme.colorNewItems }} />
        </Tooltip>
        <Tooltip title={helpDelete || t("flow-builder.card-step-delete-info")} placement="top">
          <DeleteForeverOutlinedIcon style={{ color: theme.colorNewItems }} />
        </Tooltip>
      </Box>
    </Paper>
  );
};

export default NewCardStep;
