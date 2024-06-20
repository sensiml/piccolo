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
import React, { useState } from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import { useTranslation } from "react-i18next";
import InputArray from "./InputArray";

const InputArrayString = ({ onChange, key, ...restProps }) => {
  const { t } = useTranslation("forms");
  const [validationError, setValidationError] = useState("");

  const handleValidateValue = (val) => {
    /* should be any word or chars with 1 space between them
     * separated by ,+spaces or ,
     * ends with char or , or space
     */
    if (val && !new RegExp(/^((\w+\s?)+,\s*)*((\w+\s?)+,?\s*)$/).test(val)) {
      setValidationError(
        t("array-field.error-validation", { point: val.replace(/((\w+\s?)+,\s*)*/, "") }),
      );
    } else {
      setValidationError("");
    }
  };

  const handleChange = (value) => {
    handleValidateValue(value);
  };

  const handleUpdate = (name, value) => {
    if (_.isArray(value) && !validationError) {
      onChange(name, value);
    }
  };

  return (
    <InputArray
      key={key}
      validationError={validationError}
      onChange={handleChange}
      onUpdate={handleUpdate}
      {...restProps}
    />
  );
};

InputArrayString.propTypes = {
  id: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  defaultValue: PropTypes.arrayOf(PropTypes.string),
};

InputArrayString.defaultProps = {
  defaultValue: [],
};

export default InputArrayString;
