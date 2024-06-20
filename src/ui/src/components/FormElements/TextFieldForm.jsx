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
import { FormControl, TextField } from "@mui/material";

const TextFieldForm = ({
  defaultValue,
  helperText,
  error,
  name,
  label,
  onChange,
  className,
  id,
  fullWidth = true,
  isUpdateWithDefault = true,
  isObserveDefaultValue = false,
  ...restProps
}) => {
  const [value, setValue] = useState("");

  const updateValue = (newValue) => {
    setValue(newValue);
  };

  useEffect(() => {
    if (defaultValue !== undefined) {
      setValue(defaultValue);
      if (isUpdateWithDefault) {
        onChange(name, defaultValue);
      }
    }
  }, []);

  useEffect(() => {
    if (defaultValue !== undefined && isObserveDefaultValue) {
      setValue(defaultValue);
      if (isObserveDefaultValue) {
        onChange(name, defaultValue);
      }
    }
  }, [defaultValue]);

  const handleChange = (e) => {
    updateValue(e.target.value);
    onChange(name, e.target.value);
  };

  return (
    <FormControl fullWidth={fullWidth}>
      <TextField
        id={id}
        className={className}
        value={value}
        label={label}
        error={error}
        onChange={handleChange}
        helperText={helperText}
        {...restProps}
      />
    </FormControl>
  );
};

TextFieldForm.propTypes = {
  id: PropTypes.string.isRequired,
};

export default TextFieldForm;
