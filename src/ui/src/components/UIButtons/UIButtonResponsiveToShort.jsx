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

import React, { useState, useMemo } from "react";
import { Tooltip, Button } from "@mui/material";

import { useWindowResize } from "hooks";
import { RESPONSIVE } from "consts";

const UIButtonResponsiveToShort = ({
  tooltip,
  text,
  icon,
  shortTextWidth,
  isShort = false,
  ...btnProps
}) => {
  const [isShortText, setIsShortText] = useState(false);

  const isShortMemo = useMemo(() => {
    return isShortText || isShort;
  }, [isShort, isShortText]);

  useWindowResize((data) => {
    const widthTrashHold = shortTextWidth || RESPONSIVE.WIDTH_FOR_SHORT_TEXT;
    setIsShortText(data.innerWidth < widthTrashHold);
  });

  return (
    <span>
      <Tooltip title={tooltip}>
        <span>
          <Button startIcon={!isShortMemo ? icon : null} {...btnProps}>
            {isShortMemo ? icon : text}
          </Button>
        </span>
      </Tooltip>
    </span>
  );
};

export default UIButtonResponsiveToShort;
