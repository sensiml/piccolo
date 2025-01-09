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
import _ from "lodash";

import { useTranslation } from "react-i18next";
import InputArray, { getArrayFromValue } from "./InputArray";

const InputArrayNumber = ({ onChange, range, isFloat, ...restProps }) => {
  const floatRegexp = new RegExp(/^(-?\d+\.?\d*,\s*)*(-?\d+\.?\d*,?\s*)$/);
  const intRegexp = new RegExp(/^(-?\d+\.?\d*,\s*)*(-?\d+\.?\d*,?\s*)$/);

  const intReplacedValidPartRegexp = new RegExp(/(\d+,\s*)*/);
  const floatReplacedValidPartRegexp = new RegExp(/(\d+\.?\d*,\s*)*/);

  const { t } = useTranslation("forms");
  const [validationError, setValidationError] = useState("");
  const [helperText, setHelperText] = useState("");

  const validateRange = (values) => {
    const [startRange, endRange] = range;
    const notInRangeVals = [];
    setHelperText(t("array-field.helper-text-range", { startRange, endRange }));

    const checkInRange = (val) => {
      if (isFloat) {
        return startRange <= parseFloat(val, 10) && parseFloat(val, 10) <= endRange;
      }
      return startRange <= parseInt(val, 10) && parseInt(val, 10) <= endRange;
    };

    if (_.isArray(values)) {
      values.forEach((elVal) => {
        if (!checkInRange(elVal)) {
          notInRangeVals.push(elVal);
        }
      });
    }
    if (notInRangeVals?.length) {
      setValidationError(
        t("array-field.error-out-of-range", {
          values: _.join(notInRangeVals, ", "),
          startRange,
          endRange,
        }),
      );
    } else {
      setValidationError("");
    }
  };

  useEffect(() => {
    if (_.isArray(range) && range?.length === 2) {
      validateRange(restProps.defaultValue);
    }
  }, []);

  const handleValidateValue = (val) => {
    /* should be any word or chars with 1 space between them
     * separated by ,+spaces or ,
     * ends with char or , or space
     */
    const testVal = () => {
      return isFloat ? !floatRegexp.test(val) : !intRegexp.test(val);
    };
    if (val && testVal()) {
      setValidationError(
        t("array-field.error-validation", {
          point: val.replace(
            isFloat ? floatReplacedValidPartRegexp : intReplacedValidPartRegexp,
            "",
          ),
        }),
      );
    } else if (val && !_.isArray(range) && range?.length === 2) {
      validateRange(getArrayFromValue(val));
    } else {
      setValidationError("");
    }
  };

  const handleChange = (value) => {
    handleValidateValue(value);
  };

  const handleUpdate = (name, value) => {
    if (_.isArray(value) && !validationError) {
      onChange(
        name,
        value.map((el) => (isFloat ? parseFloat(el) : parseInt(el, 10))),
      );
    }
  };

  return (
    <InputArray
      validationError={validationError}
      helperText={helperText}
      onChange={handleChange}
      onUpdate={handleUpdate}
      {...restProps}
    />
  );
};

InputArrayNumber.propTypes = {
  id: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  defaultValue: PropTypes.arrayOf(PropTypes.number),
};

InputArrayNumber.defaultProps = {
  defaultValue: [],
};

export default InputArrayNumber;
