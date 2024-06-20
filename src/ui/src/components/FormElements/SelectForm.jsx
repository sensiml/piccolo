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
import _ from "lodash";
import PropTypes from "prop-types";
import IconButton from "@mui/material/IconButton";
import AddIcon from "@mui/icons-material/Add";

import makeStyles from "@mui/styles/makeStyles";
import { Select, InputLabel, MenuItem, FormControl, Box, Button } from "@mui/material";
import CloseOutlinedIcon from "@mui/icons-material/CloseOutlined";

const useStyles = () =>
  makeStyles(() => ({
    selectRoot: {
      width: "100%",
      display: "inline-grid",
    },
    selectWrapper: {
      display: "inline-grid",
      gridTemplateColumns: "auto 3rem",
      alignItems: "center",
    },
    addBtn: {
      display: "flex",
      justifyContent: "flex-start",
      paddingLeft: "1rem",
    },
  }))();

const SelectForm = ({
  name,
  label,
  variant,
  options,
  defaultValue,
  id,
  labelId,
  addBtnText,
  onChange,
  onClickAdd,
  isCleared,
  fullWidth,
  isUpdateWithDefault = true,
  isObserveDefaultValue = false,
  disabled,
  ...restProps
}) => {
  const classes = useStyles();
  const [value, setValue] = useState("");

  const updateValue = () => {
    if (!_.isUndefined(defaultValue)) {
      setValue(defaultValue);
      if (isUpdateWithDefault) {
        onChange(name, defaultValue);
      }
    }
  };

  useEffect(() => {
    if (!isObserveDefaultValue) {
      updateValue();
    }
  }, []);

  useEffect(() => {
    if (isObserveDefaultValue) {
      updateValue();
    }
  }, [defaultValue]);

  const handleChange = (e) => {
    if (e?.target?.value === value) {
      setValue("");
      onChange(name, null);
    } else if (e?.target?.value) {
      setValue(e?.target?.value);
      onChange(name, e?.target?.value);
    }
  };

  const handleClear = () => {
    setValue("");
    onChange(name, null);
  };

  const handleClickAdd = () => {
    if (onClickAdd) {
      onClickAdd();
    }
  };

  return (
    <>
      {value !== undefined ? (
        <Box className={`${classes.selectRoot} ${isCleared && classes.selectWrapper}`}>
          <FormControl fullWidth={fullWidth} variant={variant}>
            {label ? <InputLabel id={labelId}>{label}</InputLabel> : null}
            <Select
              {...restProps}
              labelId={labelId}
              id={id}
              value={value || ""}
              onChange={handleChange}
              name={name}
              label={label}
              disabled={disabled}
            >
              {options?.length ? (
                options.map((el, index) => (
                  <MenuItem
                    key={`${id}_${index}_${el.value}`}
                    id={`${id}_${index}`}
                    value={el.value}
                  >
                    {el.name}
                  </MenuItem>
                ))
              ) : (
                <></>
              )}
              {onClickAdd ? (
                <Button
                  className={classes.addBtn}
                  color="primary"
                  fullWidth
                  startIcon={<AddIcon />}
                  onClick={handleClickAdd}
                >
                  {addBtnText}
                </Button>
              ) : null}
            </Select>
          </FormControl>
          {isCleared ? (
            <IconButton onClick={handleClear} aria-label="delete" size="large">
              <CloseOutlinedIcon />
            </IconButton>
          ) : null}
        </Box>
      ) : null}
    </>
  );
};

SelectForm.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  isCleared: PropTypes.bool,
  fullWidth: PropTypes.bool,
};

SelectForm.defaultProps = {
  isCleared: false,
  fullWidth: true,
};

export default SelectForm;
