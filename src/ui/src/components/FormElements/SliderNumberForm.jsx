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
import makeStyles from "@mui/styles/makeStyles";
import { Input, Box, Typography, FormControl, Slider } from "@mui/material";

const useStyles = makeStyles(() => ({
  sliderWrap: {
    display: "inline-grid",
    gridTemplateColumns: "auto 4rem",
  },
  sliderInputWrapper: {
    display: "flex",
    alignItems: "center",
    marginLeft: "0.5rem",
    marginBottom: "1.5rem",
  },
}));

const SliderNumberForm = ({
  className,
  id,
  labelId,
  name,
  label,
  defaultValue,
  range,
  onChange,
  isFloat,
  size = "small",
}) => {
  const classes = useStyles();
  const [value, setValue] = useState(0);
  const [rangeMax, setRangeMax] = useState(isFloat ? 1 : 100);
  const [rangeMin, setRangeMin] = useState(isFloat ? 0.01 : 1);
  const [step, setStep] = useState(1);

  const updateValue = (newValue) => {
    // can't use useEffect for testing library
    onChange(name, newValue);
    setValue(newValue);
  };

  const handleSliderChange = (event, newValue) => {
    updateValue(newValue);
  };

  const handleInputChange = (event) => {
    let val = event?.target?.value;
    if (val < rangeMin) {
      val = rangeMin;
    } else if (val > rangeMax) {
      val = rangeMax;
    }
    updateValue(val === "" ? "" : Number(val));
  };

  const handleBlur = () => {
    if (value < rangeMin) {
      updateValue(rangeMin);
    } else if (value > rangeMax) {
      updateValue(rangeMax);
    }
  };

  useEffect(() => {
    if (range?.length) {
      const [minRange, maxRange] = range;
      setRangeMax(maxRange);
      setRangeMin(minRange);
      setStep(maxRange > 1 ? 1 : 0.01);
      if (defaultValue !== undefined) {
        updateValue(defaultValue);
      } else {
        updateValue(_.floor(_.divide(maxRange, 2), isFloat ? 2 : 0)); // half
      }
    }
  }, []);

  return (
    <FormControl className={`${classes.sliderWrap} ${className}`} id={id}>
      <Box>
        <Typography id={labelId} gutterBottom>
          {`${label}`}
        </Typography>
        {value !== undefined ? (
          <Slider
            id={`slider_${id}`}
            value={value}
            onChange={handleSliderChange}
            aria-labelledby="input-slider"
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
      <Box className={classes.sliderInputWrapper}>
        {value !== undefined ? (
          <Input
            id={`input_${id}`}
            className={classes.input}
            value={value}
            margin="dense"
            onChange={handleInputChange}
            onBlur={handleBlur}
            inputProps={{
              step,
              min: rangeMin,
              max: rangeMax,
              type: "number",
              "aria-labelledby": "input-slider",
            }}
          />
        ) : null}
      </Box>
    </FormControl>
  );
};

SliderNumberForm.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  size: PropTypes.string,
};

SliderNumberForm.defaultProps = {
  size: "small",
};

export default SliderNumberForm;
