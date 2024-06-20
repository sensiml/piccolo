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
import InputDictArrayString from "components/FormElements/InputDictArrayString";

/**
 * Primary UI component for user interaction
 */

export default {
  title: "UIFormElements/InputDictArrayString",
  component: InputDictArrayString,
};

const Template = (args) => {
  return (
    <div style={{ width: "420px" }}>
      <InputDictArrayString {...args} />
    </div>
  );
};

export const InputDictArrayStringBase = Template.bind({});

InputDictArrayStringBase.args = {
  id: "1",
  name: "primary",
  label: "InputDictArrayString",
  fullWidth: true,
  defaultValue: {
    key1: ["value1", "value2"],
    key2: ["value1", "value2"],
    key3: ["value1", "value2"],
  },
};
