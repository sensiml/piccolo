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
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import { useTheme } from "@mui/material/styles";

import { RUNNING_STATUSES } from "consts";

import { CircularProgress } from "@mui/material";

const StatusRunningIcon = ({ status }) => {
  const theme = useTheme();

  switch (status) {
    case RUNNING_STATUSES.RUNNING:
      return <CircularProgress style={{ color: theme.colorConsoleInfoIcon }} size="1rem" />;
    case RUNNING_STATUSES.KILLING:
      return <CircularProgress style={{ color: theme.colorConsoleWarningIcon }} size="1rem" />;
    case RUNNING_STATUSES.KILLING_ABORTED:
      return <ErrorOutlineIcon style={{ color: theme.colorConsoleWarningIcon }} fontSize="small" />;
    case RUNNING_STATUSES.KILLED:
      return <DoneAllIcon style={{ color: theme.colorConsoleWarningIcon }} fontSize="small" />;
    case RUNNING_STATUSES.FAILED:
      return <ErrorOutlineIcon style={{ color: theme.colorConsoleErrorIcon }} fontSize="small" />;
    case RUNNING_STATUSES.COMPLETED:
      return <DoneAllIcon style={{ color: theme.colorConsoleSuccessIcon }} fontSize="small" />;
    default:
      return <></>;
  }
};

export default StatusRunningIcon;
