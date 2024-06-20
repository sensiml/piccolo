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

import React, { useCallback, isValidElement } from "react";
import _ from "lodash";
import { Box, Chip, Divider } from "@mui/material";

import useStyles from "../BuildModeStyle";

const FormUIDescriptionParameters = ({ descriptionParameters }) => {
  const classes = useStyles();

  const renderParam = useCallback(
    (value) => {
      if (_.isArray(value)) {
        return (
          <Box>
            {value.map((val, index) => (
              <Chip className={classes.paramChipItem} key={`param_${index}`} label={val} />
            ))}
          </Box>
        );
      }
      if (!_.isObject(value)) {
        return value;
      }
      if (isValidElement(value)) {
        return value;
      }
      return "";
    },
    [descriptionParameters],
  );

  const renderParamKey = useCallback(
    (value) => {
      if (!_.isObject(value)) {
        /* convert to text */
        return _.startCase(value);
      }
      return "";
    },
    [descriptionParameters],
  );

  return (
    <>
      {!_.isEmpty(descriptionParameters) ? (
        <>
          <Divider />
          <Box className={classes.descriptionContainer}>
            {/* protected from undefined  */}
            {_.entries(descriptionParameters).map(([paramKey, paramValue], index) => (
              <Box key={`desc_param_${index}`} className={classes.descriptionParamsWrapper}>
                <Box className={classes.descriptionParamsWrap}>{renderParamKey(paramKey)}</Box>
                <Box className={classes.descriptionParamsWrap}>{renderParam(paramValue)}</Box>
              </Box>
            ))}
          </Box>
          <Divider />
        </>
      ) : null}
    </>
  );
};

export default FormUIDescriptionParameters;
