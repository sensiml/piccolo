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

/* eslint-disable jsx-a11y/anchor-is-valid */

import React from "react";
import { useTranslation } from "react-i18next";
import { Box, Paper, Tooltip, Link, Zoom } from "@mui/material";

import { useTheme } from "@mui/material/styles";

import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import FileDownloadOutlinedIcon from "@mui/icons-material/FileDownloadOutlined";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";

import FlowBuilderStyles from "../FlowBuilderStyles";

const CardStep = ({
  className,
  dataTest,
  disable,
  icon,
  style,
  children,
  helpInfo,
  helpEdit,
  helpDelete,
  isFlashingEdit,
  onEdit,
  onDelete,
  onDownloadCache,
  onOpenCacheChart,
}) => {
  const { t } = useTranslation("common");
  const classes = FlowBuilderStyles();
  const theme = useTheme();

  return (
    <Zoom in>
      <Paper
        elevation={0}
        data-test={dataTest}
        className={`${classes.cardStepWrapper} ${classes.cardStepRegular} ${
          disable && classes.cardDisable
        } ${className}`}
        style={style}
      >
        <Box className={classes.IconWrap}>{icon}</Box>
        <Box className={classes.TextWrap}>{children || null}</Box>
        <Box className={classes.ActionWrap}>
          {onDelete ? (
            <Tooltip title={helpDelete || t("flow-builder.card-step-delete-info")} placement="top">
              <Link className={classes.ActionIcon} onClick={onDelete} data-test="delete-link">
                <DeleteForeverOutlinedIcon
                  className={classes.cardStepActionIcon}
                  style={{ color: theme.colorDeleteIcons }}
                />
              </Link>
            </Tooltip>
          ) : null}
          {onOpenCacheChart ? (
            <Tooltip title={helpEdit || t("flow-builder.card-step-open-cache")} placement="top">
              <Link className={classes.ActionIcon} onClick={onOpenCacheChart} data-test="edit-link">
                <BarChartOutlinedIcon
                  className={`${classes.cardStepActionIcon} ${
                    isFlashingEdit ? classes.flashingAction : ""
                  }`}
                  style={{ color: theme.colorEditIcons }}
                />
              </Link>
            </Tooltip>
          ) : null}
          {onDownloadCache ? (
            <Tooltip
              title={helpInfo || t("flow-builder.card-step-export-cache-info")}
              placement="top"
            >
              <Link className={classes.ActionIcon} onClick={onDownloadCache} data-test="info-link">
                <FileDownloadOutlinedIcon
                  className={classes.cardStepActionIcon}
                  style={{ color: theme.colorEditIcons }}
                />
              </Link>
            </Tooltip>
          ) : null}
          {onEdit ? (
            <Tooltip title={helpEdit || t("flow-builder.card-step-edit-info")} placement="top">
              <Link className={classes.ActionIcon} onClick={onEdit} data-test="edit-link">
                <EditOutlinedIcon
                  className={`${classes.cardStepActionIcon} ${
                    isFlashingEdit ? classes.flashingAction : ""
                  }`}
                  style={{ color: theme.colorEditIcons }}
                />
              </Link>
            </Tooltip>
          ) : null}
        </Box>
      </Paper>
    </Zoom>
  );
};

export default CardStep;
