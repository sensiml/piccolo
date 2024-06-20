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

/* eslint-disable no-param-reassign */
/* eslint-disable no-use-before-define */
/* eslint-disable import/no-cycle */
import React, { Fragment } from "react";
import ColorizeIcon from "@mui/icons-material/Colorize";
import TransformIcon from "@mui/icons-material/Transform";
import InputIcon from "@mui/icons-material/Input";
import DynamicFeedIcon from "@mui/icons-material/DynamicFeed";
import SettingsEthernetIcon from "@mui/icons-material/SettingsEthernet";
import AccountTreeIcon from "@mui/icons-material/AccountTree";
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
import AcUnitIcon from "@mui/icons-material/AcUnit";
import { Grid, Tooltip, Typography } from "@mui/material";
import helper from "store/helper";
import InputCard from "./DetailViews/InputCard";
import TransformCard from "./DetailViews/TransformCard";
import SamplerCard from "./DetailViews/SamplerCard";
import SetCard from "./DetailViews/SetCard";
import ClassifierCard from "./DetailViews/ClassifierCard";
import SegmenterCard from "./DetailViews/SegmenterCard";

const stepTypes = {
  query: {
    label: "Input",
    styleName: "nodeColor1",
    Icon: () => <InputIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <InputCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
  file: {
    label: "Input",
    styleName: "nodeColor1",
    Icon: () => <InputIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <InputCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
  transform: {
    label: "Transform",
    styleName: "nodeColor2",
    Icon: () => <TransformIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <TransformCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
  generatorset: {
    label: "Feature Generators",
    styleName: "nodeColor3",
    Icon: () => <DynamicFeedIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <SetCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
  selectorset: {
    label: "Feature Selectors",
    styleName: "nodeColor4",
    Icon: () => <SettingsEthernetIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <SetCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
  sampler: {
    label: "Sampler",
    styleName: "nodeColor5",
    Icon: () => <ColorizeIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <SamplerCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
  tvo: {
    label: "Test Validate Optimize",
    styleName: "nodeColor6",
    Icon: () => <AccountTreeIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <ClassifierCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
  segmenter: {
    label: "Segmenter",
    styleName: "nodeColor7",
    Icon: () => <AcUnitIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <SegmenterCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
  default: {
    label: "",
    styleName: "nodeColor8",
    Icon: () => <CheckBoxOutlineBlankIcon />,
    getDetailView: (pipeline, transforms, columns, classes) => (
      <InputCard pipeline={pipeline} transforms={transforms} columns={columns} cls={classes} />
    ),
  },
};

const getDetailView = (pipeline, transforms, columns, classes) => {
  return (stepTypes[pipeline.type.toLowerCase()] || stepTypes.default).getDetailView(
    pipeline,
    transforms,
    columns,
    classes,
  );
};

const getNodeStyle = (type, styles) => {
  return styles[(stepTypes[type.toLowerCase()] || stepTypes.default).styleName];
};

const getTitle = (type) => {
  return (stepTypes[type.toLowerCase()] || { label: type }).label;
};

const getIcon = (type) => {
  const stepNode = stepTypes[type.toLowerCase()] || stepTypes.default;
  return <Tooltip title={stepNode.label === "" ? type : stepNode.label}>{stepNode.Icon()}</Tooltip>;
};

const getInputRow = (inputContract, inputs) => {
  if (!inputContract) return null;
  const inputRow = {};
  inputContract.forEach((i) => {
    inputRow[i.name] = inputs[i.name] !== null ? inputs[i.name] : i.default || "";
  });
  return inputRow;
};

const renderInputRows = (transform, inputs, cls) => {
  return (transform && transform.input_contract) || inputs
    ? Object.entries(getInputRow((transform || {}).input_contract || [], inputs || {})).map(
        ([k, val]) => renderInputRow(k, val, cls),
      )
    : null;
};

const renderInputRow = (name, value, cls) => {
  if (name === "input_data") return null;
  if (typeof value === "number") value = value.toString();
  const data = Array.isArray(value) ? value.join(", ") : value;
  if (helper.isNullOrEmpty(data)) return null;
  return (
    <Fragment key={name}>
      <Grid item xs={3}>
        <Typography className={cls.title}>
          {helper.capitalizeWords(name.replace("_", " "))}:
        </Typography>
      </Grid>
      <Grid item xs={8}>
        <Typography className={cls.pos}>{data}</Typography>
      </Grid>
      <Grid item xs={1} />
    </Fragment>
  );
};

export { getNodeStyle, getIcon, getDetailView, getTitle, renderInputRow, renderInputRows };
