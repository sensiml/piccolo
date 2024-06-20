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

import { useArgs } from "@storybook/client-api";
import CheckBox from "components/FormElements/CheckBox";

export default {
  title: "UIFormElements/CheckBox",
  component: CheckBox,
};

const Template = (args) => {
  const [{ value }, updateArgs] = useArgs();
  const handleChange = (name, val) => {
    updateArgs({ value: val });
  };

  return <CheckBox {...args} value={value} onChange={handleChange} />;
};

export const CheckedCheckBox = Template.bind({});
// More on args: https://storybook.js.org/docs/react/writing-stories/args
CheckedCheckBox.args = {
  id: "1",
  defaultValue: true,
  value: false,
  name: "primary",
  label: "CheckedCheckBox",
};

export const UnCheckedCheckBox = Template.bind({});
// More on args: https://storybook.js.org/docs/react/writing-stories/args
UnCheckedCheckBox.args = {
  id: "1",
  defaultValue: false,
  value: false,
  name: "primary",
  label: "UnCheckedCheckBox",
};
