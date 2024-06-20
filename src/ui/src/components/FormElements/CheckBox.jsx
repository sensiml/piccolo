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
import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { FormControlLabel, Switch } from "@mui/material";

const CheckBox = ({ className, id, value, defaultValue, name, label, onChange }) => {
  const [localVal, setLocalVal] = useState();

  useEffect(() => {
    if (defaultValue) {
      onChange(name, defaultValue);
      setLocalVal(defaultValue);
    } else {
      onChange(name, false);
      setLocalVal(false);
    }
  }, []);

  useEffect(() => {
    setLocalVal(value);
  }, [value]);

  const handleChange = () => {
    onChange(name, !localVal);
    setLocalVal(!localVal);
  };

  return (
    <>
      {localVal !== undefined ? (
        <FormControlLabel
          id={id}
          className={className}
          control={<Switch checked={value} onChange={handleChange} name={name} color="primary" />}
          label={label}
        />
      ) : null}
    </>
  );
};

CheckBox.propTypes = {
  id: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
};

export default CheckBox;
