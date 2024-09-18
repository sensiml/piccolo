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
import _ from "lodash";
import PropTypes from "prop-types";
import makeStyles from "@mui/styles/makeStyles";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";

import {
  Box,
  Select,
  InputLabel,
  OutlinedInput,
  MenuItem,
  FormControl,
  Chip,
  Checkbox,
  ListItemText,
} from "@mui/material";

const useStyles = makeStyles((theme) => ({
  chips: {
    display: "flex",
    flexWrap: "wrap",
    gap: theme.spacing(0.25),
  },
  chip: {
    margin: theme.spacing(0.5),
  },
}));

const SelectMultiChip = ({
  defaultValue,
  name,
  label,
  id,
  labelId,
  size,
  options,
  onChange,
  disabledOptions = [],
  fullWidth = true,
  isUpdateWithDefault = true,
  isObserveDefaultValue = false,
  isFormHidden,
  defaultStep,
  maxElements,
  minElements,
  ...restProps
}) => {
  const classes = useStyles();
  const [value, setValue] = useState([]);

  useEffect(() => {
    if (_.isEmpty(defaultValue)) {
      const defaultOptions = options.filter((el) => el.isDefault).map((item) => item.value);
      setValue([...defaultOptions]);
      if (isUpdateWithDefault) {
        onChange(name, [...defaultOptions]);
      }
    } else {
      setValue([...defaultValue]);
      if (isUpdateWithDefault) {
        onChange(name, defaultValue);
      }
    }
  }, []);

  useEffect(() => {
    if (isObserveDefaultValue) {
      setValue([...defaultValue]);
    }
  }, [defaultValue]);

  const handleChange = (e) => {
    setValue(e?.target?.value);
    onChange(name, e?.target?.value);
  };

  return (
    <FormControl fullWidth={fullWidth} size={size}>
      <InputLabel id={labelId}>{label}</InputLabel>
      {value !== undefined ? (
        <Select
          {...restProps}
          id={id}
          labelId={labelId}
          value={value || []}
          onChange={handleChange}
          name={name}
          input={<OutlinedInput id={`${id}_input`} label={label} />}
          renderValue={(selected) => (
            <div className={classes.chips}>
              {selected.map((val) => (
                <Box key={val} sx={{ display: "flex", flexWrap: "wrap" }}>
                  <Chip label={val} />
                </Box>
              ))}
            </div>
          )}
          multiple
        >
          {options?.length &&
            options.map((el, index) => (
              <MenuItem
                key={`${id}_${index}`}
                value={el.value}
                disabled={disabledOptions.includes(el.value)}
              >
                <ListItemText primary={el.name} />
                {value.indexOf(el.value) > -1 ? <CheckOutlinedIcon color="primary" /> : " "}
              </MenuItem>
            ))}
        </Select>
      ) : null}
    </FormControl>
  );
};

SelectMultiChip.propTypes = {
  id: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
};

export default SelectMultiChip;
