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

import { RUNNING_STATUSES } from "consts";
import { useTheme } from "@mui/material/styles";

const ConsoleRunningStatusText = ({ status, className, children }) => {
  const theme = useTheme();

  const getColor = () => {
    switch (status) {
      case RUNNING_STATUSES.RUNNING:
        return theme.colorConsoleInfoIcon;

      case RUNNING_STATUSES.KILLING:
        return theme.colorConsoleWarningIcon;

      case RUNNING_STATUSES.KILLING_ABORTED:
        return theme.colorConsoleWarningIcon;

      case RUNNING_STATUSES.KILLED:
        return theme.colorConsoleWarningIcon;

      case RUNNING_STATUSES.FAILED:
        return theme.colorConsoleErrorIcon;

      case RUNNING_STATUSES.COMPLETED:
        return theme.colorConsoleSuccessIcon;
      default:
        return theme.colorConsoleSuccessIcon;
    }
  };

  return (
    <span className={className} style={{ color: getColor() }}>
      {children}
    </span>
  );
};

export default ConsoleRunningStatusText;
