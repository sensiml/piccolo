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
import React from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import InputDict from "./InputDict";
import InputArrayString from "./InputArrayString";

const InputDictArrayString = ({ id, labelId, label, name, defaultValue, onChange }) => {
  const handleChagne = (inputName, inputValues) => {
    onChange(
      inputName,
      inputValues
        .filter((el) => !_.isEmpty(el.objVal)) // values should be not empty
        .reduce((acc, el) => {
          acc[el.objKey] = el.objVal;
          return acc;
        }, {}),
    );
  };

  return (
    <InputDict
      id={id || "input_dict"}
      label={label}
      labelId={labelId}
      name={name}
      defaultValue={defaultValue}
      ValueInputComponent={InputArrayString}
      onChange={handleChagne}
    />
  );
};

InputDictArrayString.propTypes = {
  id: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  defaultValue: PropTypes.objectOf(PropTypes.arrayOf(PropTypes.string)).isRequired,
};

InputDictArrayString.defaultProps = {
  // defaultValue: [],
};

export default InputDictArrayString;
