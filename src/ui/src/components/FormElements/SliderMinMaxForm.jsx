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
import { Box, Typography, Slider } from "@mui/material";

const SliderMinMaxForm = ({
  name,
  label,
  id,
  testid,
  labelId,
  defaultValue,
  range,
  defaultStep,
  onChange,
  isFloat,
  size = "small",
}) => {
  const [value, setValue] = useState(0);
  const [rangeMax, setRangeMax] = useState(isFloat ? 1 : 100);
  const [rangeMin, setRangeMin] = useState(isFloat ? 0.01 : 1);
  const [step, setStep] = useState(1);

  const getLabelValue = () => {
    if (value?.length) {
      return value?.join(", ");
    }
    return "";
  };

  const updateValue = (newValue) => {
    setValue(newValue);
    onChange(name, newValue);
  };

  const handleSliderChange = (event, newValue) => {
    updateValue(newValue);
  };

  useEffect(() => {
    if (range?.length) {
      const [minRange, maxRange] = range;
      setRangeMax(maxRange);
      setRangeMin(minRange);
      if (!_.isEmpty(defaultStep)) {
        setStep(defaultStep);
      } else {
        setStep(maxRange > 1 ? 1 : 0.01);
      }
      if (!_.isEmpty(defaultValue)) {
        updateValue(defaultValue);
      } else {
        updateValue([
          _.floor(_.divide(minRange, 2), isFloat ? 2 : 0),
          _.floor(_.divide(maxRange, 2), isFloat ? 2 : 0),
        ]);
      }
    }
  }, []);

  return (
    <Box id={id}>
      <Box>
        <Typography id={labelId} gutterBottom>
          {`${label} (${getLabelValue()})`}
        </Typography>
        {value !== undefined ? (
          <Slider
            value={value}
            valueLabelDisplay="auto"
            onChange={handleSliderChange}
            aria-labelledby="input-slider"
            data-testid={testid}
            marks={[
              { value: rangeMin, label: rangeMin },
              { value: rangeMax, label: rangeMax },
            ]}
            step={step}
            min={rangeMin}
            max={rangeMax}
            size={size}
          />
        ) : null}
      </Box>
    </Box>
  );
};

SliderMinMaxForm.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
};

export default SliderMinMaxForm;
