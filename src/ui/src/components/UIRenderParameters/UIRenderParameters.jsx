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
import { Box, Chip, Checkbox } from "@mui/material";
import makeStyles from "@mui/styles/makeStyles";
import { filterToSnakeCase } from "filters";

const useStyles = () =>
  makeStyles((theme) => ({
    descriptionContainer: {
      width: "100%",
      margin: `${theme.spacing(2)} 0`,
    },
    descriptionParamsWrapper: {
      display: "flex",
      flexDirection: "row",
    },
    descriptionParamsWrap: {
      justifyContent: "flex-start",
      alignItems: "center",
      display: "flex",
      flex: 2,
      marginTop: theme.spacing(1),
      marginBottom: theme.spacing(1),
      "&:first-child": {
        fontWeight: 600,
        flex: 1,
        color: theme.colorBrandText,
      },
    },
    paramChipItem: {
      margin: `0 ${theme.spacing(0.5)}`,
    },
  }))();

const UIRenderParameters = ({ parameters }) => {
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
      if (_.isBoolean(value)) {
        return <Checkbox defaultChecked checked={value} />;
      }
      if (!_.isObject(value) && value) {
        return value;
      }
      if (isValidElement(value)) {
        return value;
      }
      return "";
    },
    [parameters],
  );

  const renderParamKey = useCallback(
    (value) => {
      if (!_.isObject(value)) {
        /* convert to text */
        return _.startCase(value);
      }
      return "";
    },
    [parameters],
  );

  return (
    <>
      {!_.isEmpty(parameters) ? (
        <>
          <Box className={classes.descriptionContainer}>
            {/* protected from undefined  */}
            {_.entries(parameters).map(([paramKey, paramValue], index) => (
              <Box
                key={`desc_param_${index}_${filterToSnakeCase(paramValue)}`}
                className={classes.descriptionParamsWrapper}
              >
                {!_.isUndefined(paramValue) ? (
                  <>
                    <Box className={classes.descriptionParamsWrap}>{renderParamKey(paramKey)}</Box>
                    <Box className={classes.descriptionParamsWrap}>{renderParam(paramValue)}</Box>
                  </>
                ) : null}
              </Box>
            ))}
          </Box>
        </>
      ) : null}
    </>
  );
};

export default UIRenderParameters;
