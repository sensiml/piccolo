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
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";
import { Box, Tooltip, Link, Collapse, Typography } from "@mui/material";

import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import ArrowDownwardOutlinedIcon from "@mui/icons-material/ArrowDownwardOutlined";
import ArrowUpwardOutlinedIcon from "@mui/icons-material/ArrowUpwardOutlined";

import { useTheme } from "@mui/material/styles";

import useStyles from "./FormStyle";

const FormSetTransfromForm = ({
  expanded,
  name,
  isShowInfo,
  onChange,
  onEdit,
  onInfo,
  onDelete,
  onUp,
  onDown,
  children,
}) => {
  /*
   For creating
  */
  const { t } = useTranslation("models");
  const classes = useStyles();
  const theme = useTheme();

  const [isFocused, setIsFocused] = useState(false);

  return (
    <Box
      onChange={onChange}
      className={classes.collapseFormWrapper}
      onMouseEnter={() => setIsFocused(true)}
      onMouseLeave={() => setIsFocused(false)}
    >
      <Box mb={2} className={classes.collapseFormSummary}>
        <Box>
          <Typography
            variant="subtitle1"
            className={`${isFocused || expanded ? classes.collapseFormHeaderHovered : null}`}
          >
            {name}
          </Typography>
        </Box>
        <Box className={classes.collapseFormSummaryIconsWrapper}>
          <Box>
            {onUp ? (
              <Tooltip title={"move up"} placement="top">
                <Link className={classes.actionIcon} onClick={onUp}>
                  <ArrowUpwardOutlinedIcon color={"primary"} />
                </Link>
              </Tooltip>
            ) : null}
            {onDown ? (
              <Tooltip title={"move down"} placement="top">
                <Link className={classes.actionIcon} onClick={onDown}>
                  <ArrowDownwardOutlinedIcon color={"primary"} />
                </Link>
              </Tooltip>
            ) : null}
            {onInfo && isShowInfo ? (
              <Tooltip title={t("tooltip-info")} placement="top">
                <Link className={classes.actionIcon} onClick={onInfo}>
                  <InfoOutlinedIcon style={{ color: theme.colorInfoLinks }} />
                </Link>
              </Tooltip>
            ) : null}
            {onEdit ? (
              <Tooltip title={t("tooltip-edit")} placement="top">
                <Link className={classes.actionIcon} onClick={onEdit}>
                  <EditOutlinedIcon style={{ color: theme.colorEditIcons }} />
                </Link>
              </Tooltip>
            ) : null}
            {onDelete ? (
              <Tooltip title={t("tooltip-delete")} placement="top">
                <Link className={classes.actionIcon} onClick={onDelete}>
                  <DeleteForeverOutlinedIcon style={{ color: theme.colorDeleteIcons }} />
                </Link>
              </Tooltip>
            ) : null}
          </Box>
        </Box>
      </Box>
      <Box>
        <Collapse timeout={300} in={Boolean(expanded)}>
          {children || null}
        </Collapse>
      </Box>
    </Box>
  );
};

FormSetTransfromForm.propTypes = {
  expanded: PropTypes.bool,
};

FormSetTransfromForm.defaultProps = {
  expanded: true,
};

export default FormSetTransfromForm;
