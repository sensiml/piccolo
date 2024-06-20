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

import DoneAllIcon from "@mui/icons-material/DoneAll";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import CodeOutlinedIcon from "@mui/icons-material/CodeOutlined";
import { useTheme } from "@mui/material/styles";

import { STATUSES } from "consts";

const StatusIcon = (status) => {
  const theme = useTheme();
  switch (status) {
    case STATUSES.DEBUG:
      return <CodeOutlinedIcon style={{ color: theme.colorConsoleBody }} fontSize="small" />;
    case STATUSES.INFO:
      return <CheckOutlinedIcon style={{ color: theme.colorConsoleInfoIcon }} fontSize="small" />;
    case STATUSES.SUCCESS:
      return <DoneAllIcon style={{ color: theme.colorConsoleSuccessIcon }} fontSize="small" />;
    case STATUSES.WARNING:
      return <ErrorOutlineIcon style={{ color: theme.colorConsoleWarningIcon }} fontSize="small" />;
    case STATUSES.ERROR:
      return <ErrorOutlineIcon style={{ color: theme.colorConsoleErrorIcon }} fontSize="small" />;
    default:
      return <></>;
  }
};

export default StatusIcon;
