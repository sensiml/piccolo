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
import arrowIcon from "assets/icons/flow_arrow_add.svg";
import noArrowIcon from "assets/icons/flow_no_arrow_add.svg";
import { useTranslation } from "react-i18next";
import { Tooltip, Link } from "@mui/material";
import FlowBuilderStyles from "./FlowBuilderStyles";

const IconArrowAddWrap = ({ onClick, info, disable, dataTest, isRemoveArrow }) => {
  const { t } = useTranslation("common");
  const classes = FlowBuilderStyles();

  return (
    <Tooltip title={info || t("flow-builder.arrow-add-info")} placement="right">
      <Link
        onClick={onClick}
        className={`${classes.ActionIcon} ${disable && classes.arrDisable}`}
        data-test={dataTest}
      >
        <img src={isRemoveArrow ? noArrowIcon : arrowIcon} alt="" />
      </Link>
    </Tooltip>
  );
};

export default IconArrowAddWrap;
