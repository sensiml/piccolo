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
import arrowIcon from "assets/icons/flow_arrow_down.svg";
import noArrowIcon from "assets/icons/flow_no_arrow_down.svg";
import FlowBuilderStyles from "./FlowBuilderStyles";

const IconArrowWrap = ({ disable, dataTest, isRemoveArrow }) => {
  const classes = FlowBuilderStyles();
  return (
    // eslint-disable-next-line jsx-a11y/anchor-is-valid
    <a data-test={dataTest}>
      <img
        src={isRemoveArrow ? noArrowIcon : arrowIcon}
        alt=""
        className={`${disable && classes.arrDisable}`}
      />
    </a>
  );
};

export default IconArrowWrap;
