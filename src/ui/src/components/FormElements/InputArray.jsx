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
import React, { useState, useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import { useTranslation } from "react-i18next";
import { TextField, InputAdornment } from "@mui/material";

export const getArrayFromValue = (val) => {
  if (_.isString(val)) {
    return val
      .split(",")
      .map((el) => el.trim())
      .filter((el) => el);
  }
  return [];
};

const InputArrayForm = ({
  id,
  labelId,
  name,
  label,
  defaultValue,
  validationError,
  range,
  onChange,
  onUpdate,
  helperText,
  minElements,
  maxElements,
  ...restProps
}) => {
  const { t } = useTranslation("forms");
  const [value, setValue] = useState("");
  const [errorText, setErrorText] = useState("");
  const [limitHelperText, setLimitHelperText] = useState("");

  const getValueFromArray = (val) => {
    if (_.isArray(val)) {
      return val.join(", ");
    }
    return [];
  };

  const helperInputText = useMemo(() => {
    if (errorText || validationError) {
      return _.trim(`${errorText || ""} ${validationError || ""}`);
    }
    return _.trim(`${helperText || ""} ${limitHelperText}`);
  }, [errorText, validationError, helperText, limitHelperText]);

  const validateInputValue = (val) => {
    // should be any word chars * separated by ,+spaces or , * ends with char or ,
    if (!val) {
      setErrorText("");
    }
    if (minElements && getArrayFromValue(val)?.length < minElements) {
      setErrorText(limitHelperText);
    } else if (maxElements && getArrayFromValue(val)?.length > maxElements) {
      setErrorText(limitHelperText);
    } else {
      setErrorText("");
    }
  };

  useEffect(() => {
    if (defaultValue !== undefined) {
      const arrayVal = getValueFromArray(defaultValue);
      setValue(arrayVal);
      onUpdate(name, defaultValue);
    }
    if (minElements && maxElements && minElements === maxElements) {
      setLimitHelperText(t("array-field.helper-text-limit-equal", { minElements, maxElements }));
    } else if (minElements && maxElements) {
      setLimitHelperText(t("array-field.helper-text-limit-between", { minElements, maxElements }));
    } else if (maxElements) {
      setLimitHelperText(t("array-field.helper-text-limit-max", { maxElements }));
    } else if (minElements) {
      setLimitHelperText(t("array-field.helper-text-limit-min", { minElements }));
    }
  }, [minElements, maxElements]);

  useEffect(() => {
    validateInputValue(value);
  }, [value]);

  const handleChange = (e) => {
    onChange(e?.target?.value);
    setValue(e?.target?.value);
  };

  const handleBlur = () => {
    onUpdate(name, getArrayFromValue(value));
  };

  return (
    <TextField
      id={`text_field_${id}`}
      label={label}
      value={value}
      fullWidth
      onChange={handleChange}
      onBlur={handleBlur}
      helperText={helperInputText}
      InputProps={{
        startAdornment: <InputAdornment position="start">[</InputAdornment>,
        endAdornment: <InputAdornment position="end">]</InputAdornment>,
      }}
      error={Boolean(errorText) || Boolean(validationError)}
      {...restProps}
    />
  );
};

InputArrayForm.propTypes = {
  id: PropTypes.string.isRequired,
  defaultValue: PropTypes.array,
  validationError: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  onUpdate: PropTypes.func.isRequired,
};

InputArrayForm.defaultProps = {
  defaultValue: [],
};

export default InputArrayForm;
