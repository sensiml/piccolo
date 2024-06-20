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
import InputDictSelectMultiChip from "components/FormElements/InputDictSelectMultiChip";

/**
 * Primary UI component for user interaction
 */

export default {
  title: "UIFormElements/InputDictSelectMultiChip",
  component: InputDictSelectMultiChip,
};

const Template = (args) => {
  return (
    <div style={{ width: "420px" }}>
      <InputDictSelectMultiChip {...args} />
    </div>
  );
};

export const InputDictSelectMultiChipBase = Template.bind({});

InputDictSelectMultiChipBase.args = {
  id: "1",
  name: "primary",
  label: "InputDictArrayString",
  fullWidth: true,
  defaultValue: {
    key1: ["value1", "value2"],
    key2: ["value3", "value4"],
  },
  options: [
    { name: "value1", value: "value1" },
    { name: "value2", value: "value2" },
    { name: "value3", value: "value3" },
    { name: "value4", value: "value4" },
    { name: "value5", value: "value5" },
    { name: "value6", value: "value6" },
  ],
};
