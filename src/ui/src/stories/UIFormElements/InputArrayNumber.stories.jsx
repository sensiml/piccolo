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

/* eslint-disable import/no-extraneous-dependencies */
import React from "react";
import _ from "lodash";
import InputArrayNumber from "components/FormElements/InputArrayNumber";

/**
 * Primary UI component for user interaction
 */

export default {
  title: "UIFormElements/InputArrayNumber",
  component: InputArrayNumber,
};

const Template = (args) => {
  return (
    <div style={{ width: "300px" }}>
      <InputArrayNumber {...args} />
    </div>
  );
};

export const InputArrayBase = Template.bind({});

InputArrayBase.args = {
  id: "1",
  name: "primary",
  label: "InputArrayNumber",
  defaultValue: [21, 2, 123],
};

export const InputArrayRangeIn = Template.bind({});

InputArrayRangeIn.args = {
  id: "1",
  name: "primary",
  label: "InputArrayRangeIn",
  range: [1, 100],
  defaultValue: [1, 21, 100],
};

export const InputArrayRangeOut = Template.bind({});

InputArrayRangeOut.args = {
  id: "1",
  name: "primary",
  label: "InputArrayRangeOut",
  range: [1, 100],
  defaultValue: [1, 21, 101],
};

export const InputArrayFloat = Template.bind({});

InputArrayFloat.args = {
  id: "1",
  name: "primary",
  isFloat: true,
  label: "InputArrayFloat",
  range: [1, 100],
  defaultValue: [1, 21],
};

export const InputArrayFloatRangeEqualLimit = Template.bind({});

InputArrayFloatRangeEqualLimit.args = {
  id: "1",
  name: "primary",
  isFloat: true,
  label: "InputArrayFloatRangeEqualLimit",
  range: [1, 100],
  minElements: 2,
  maxElements: 2,
  defaultValue: [1, 21],
};

export const InputArrayFloatRangeBetweenLimit = Template.bind({});

InputArrayFloatRangeBetweenLimit.args = {
  id: "1",
  name: "primary",
  isFloat: true,
  label: "InputArrayFloatRangeBetweenLimit",
  range: [1, 100],
  minElements: 2,
  maxElements: 4,
  defaultValue: [1, 21],
};

export const InputArrayFloatRangeOnlyMinLimit = Template.bind({});

InputArrayFloatRangeOnlyMinLimit.args = {
  id: "1",
  name: "primary",
  isFloat: true,
  label: "InputArrayFloatRangeOnlyMinLimit",
  range: [1, 100],
  minElements: 2,
  defaultValue: [1, 21],
};

export const InputArrayFloatRangeOnlyMaxLimit = Template.bind({});

InputArrayFloatRangeOnlyMaxLimit.args = {
  id: "1",
  name: "primary",
  isFloat: true,
  label: "InputArrayFloatRangeOnlyMaxLimit",
  range: [1, 100],
  maxElements: 2,
  defaultValue: [1, 21],
};
