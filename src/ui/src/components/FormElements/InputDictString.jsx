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

/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

import _ from "lodash";

import InputDict from "./InputDict";
import TextFieldForm from "./TextFieldForm";

const InputDictString = ({ id, labelId, label, name, defaultValue, onChange }) => {
  const handleChagne = (inputName, inputValue) => {
    onChange(inputName, inputValue);
  };

  return (
    <InputDict
      id={id || "input_dict"}
      label={label}
      labelId={labelId}
      name={name}
      defaultValue={defaultValue}
      ValueInputComponent={TextFieldForm}
      onChange={handleChagne}
    />
  );
};

InputDictString.propTypes = {
  id: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  defaultValue: PropTypes.objectOf(PropTypes.arrayOf(PropTypes.string)).isRequired,
};

InputDictString.defaultProps = {
  // defaultValue: [],
};

export default InputDictString;
