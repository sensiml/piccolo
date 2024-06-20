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

import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { OutlinedInput, InputLabel } from "@mui/material";

const InputNumberForm = ({
  defaultValue,
  name,
  label,
  onChange,
  id,
  labelId,
  isFloat,
  fullWidth = false,
}) => {
  const [value, setValue] = useState(0);
  const [step, setStep] = useState(1);

  const updateValue = (newValue) => {
    setValue(newValue);
  };

  useEffect(() => {
    setStep(isFloat ? 0.01 : 1);
    if (defaultValue !== undefined) {
      setValue(defaultValue);
      onChange(name, defaultValue);
    }
  }, []);

  const handleChange = (e) => {
    updateValue(isFloat ? parseFloat(e?.target?.value) : parseInt(e?.target?.value, 10));
  };

  const handleUpdate = () => {
    onChange(name, value);
  };

  return (
    <>
      {label ? (
        <InputLabel htmlFor={id} id={labelId}>
          {label}
        </InputLabel>
      ) : null}
      {value !== undefined ? (
        <OutlinedInput
          id={id}
          label={label}
          value={value}
          fullWidth={fullWidth}
          margin="dense"
          onChange={handleChange}
          onBlur={handleUpdate}
          inputProps={{
            step,
            type: "number",
            "aria-labelledby": label,
          }}
        />
      ) : null}
    </>
  );
};

InputNumberForm.propTypes = {
  id: PropTypes.string.isRequired,
};

export default InputNumberForm;
