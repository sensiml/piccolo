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
import { Tooltip } from "@mui/material";
import HelpRoundedIcon from "@mui/icons-material/HelpRounded";
import ErrorBoundary from "components/ErrorBoundary";
import useStyles from "./HelpIconStyles";

export default function Icons({ className, toolTip }) {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const open = Boolean(anchorEl);
  const id = open ? "simple-popover" : undefined;

  const renderTextWithBr = () => {
    // add `\n` to first space after each nth char
    const nodeArr = [];
    let i = 0;
    while (i < toolTip?.length) {
      // add \n each 65th symbols
      if ((i + 1) % 65 === 0) {
        // if nth's char
        while (i < toolTip?.length) {
          // traverse till space
          if (toolTip[i] === " ") {
            nodeArr.push("\n");
            i++;
            break;
          }
          nodeArr.push(toolTip[i]);
          i++;
        }
      }
      nodeArr.push(toolTip[i]);
      i++;
    }
    return nodeArr.join("");
  };

  return (
    <ErrorBoundary>
      <Tooltip
        placement="right"
        classes={{ tooltip: classes.tooltip }}
        title={
          <>
            {" "}
            <span className={classes.typography}>
              <pre style={{ fontFamily: "inherit" }}>{renderTextWithBr()}</pre>
            </span>
          </>
        }
      >
        <HelpRoundedIcon
          fontSize="small"
          className={className}
          aria-describedby={id}
          onClick={handleClick}
        />
      </Tooltip>
    </ErrorBoundary>
  );
}
