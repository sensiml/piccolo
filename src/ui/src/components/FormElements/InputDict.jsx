/* eslint-disable no-unused-vars */
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

import React, { useState, useEffect, useMemo } from "react";
import PropTypes from "prop-types";

import _ from "lodash";

import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";

import { useTranslation } from "react-i18next";
import {
  TextField,
  Box,
  FormHelperText,
  IconButton,
  Button,
  Tooltip,
  Typography,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import makeStyles from "@mui/styles/makeStyles";
import { filterToSnakeCase } from "filters";

const useStyles = () =>
  makeStyles((theme) => ({
    deleteBtn: {
      height: theme.spacing(6),
      width: theme.spacing(6),
      justifyContent: "flex-start",
      alignItems: "flex-start",
    },
    inputLabel: {
      marginBottom: theme.spacing(1),
    },
    dictWrapper: {
      width: "100%",
      display: "flex",
      flexDirection: "column",
    },
    dictItemWrapper: {
      width: "100%",
      display: "inline-grid",
      gridTemplateColumns: "10rem auto 2rem",
    },
    ...theme.common,
  }))();

const InputDict = ({
  id,
  labelId,
  label,
  name,
  defaultValue,
  options,
  ValueInputComponent,
  onChange,
}) => {
  /**
   * onChange @returns Object { name: str, values: Array of { objKey: "", objVal: [] } }
   */
  const { t } = useTranslation("forms");
  const classes = useStyles();
  const theme = useTheme();

  const [values, setValues] = useState([{ objKey: "", objVal: [] }]);
  const [keyErrors, setKeyErrors] = useState({});
  const [disabledOptions, setDisabledOptions] = useState([]);

  const isDisabledAction = useMemo(() => {
    return !_.isEmpty(_.values(keyErrors).filter((val) => val));
  }, [keyErrors]);

  const updateKeyError = (key, error) => {
    setKeyErrors((errors) => ({ ...errors, [key]: error }));
  };

  const updateDisabledOptions = (inputValues) => {
    const disabledValues = inputValues.reduce((acc, el) => {
      if (_.isArray(el.objVal)) {
        _.forEach(el.objVal, (val) => {
          acc.push(val);
        });
      }
      return acc;
    }, []);
    setDisabledOptions(
      options.filter((el) => disabledValues.includes(el.value)).map((el) => el.value),
    );
  };

  useEffect(() => {
    if (!_.isUndefined(defaultValue)) {
      const updatedValues = _.entries(defaultValue).map(([objKey, objVal]) => ({ objKey, objVal }));
      setValues(updatedValues);
      onChange(name, updatedValues);
      updateDisabledOptions(updatedValues);
    }
  }, []);

  const handleUpdate = (updatedValues) => {
    if (!_.isEqual(values, updatedValues)) {
      onChange(name, updatedValues);
      updateDisabledOptions(updatedValues);
    }
  };

  const handleValidateUpdatingKey = (e, mapIndex) => {
    const newKey = e.target.value;
    if (!values.find((el) => el.objKey === newKey)) {
      updateKeyError(mapIndex, "");
    } else {
      updateKeyError(mapIndex, t("dict-field.error-unique-keys"));
    }
  };

  const handleCreateNewItemSetValue = () => {
    const emptyValueIndex = values.findIndex((el) => !el.objKey);
    if (emptyValueIndex !== -1) {
      updateKeyError(emptyValueIndex, t("dict-field.error-fill-field"));
    } else {
      setValues((el) => [...el, { objKey: "", objVal: [] }]);
    }
  };

  const handleUpdateKey = (e, mapIndex) => {
    // use map to do deep copy with updated value
    const updatedValues = values.map((el, currIndex) => {
      // && !keyErrors[currIndex]
      if (currIndex === mapIndex) {
        return { ...el, objKey: e.target.value };
      }
      return el;
    });
    handleUpdate(updatedValues);
    setValues(updatedValues);
  };

  const handleUpdateValue = (val, mapIndex) => {
    // use map to do deep copy with updated value
    const updatedValues = values.map((el, currIndex) => {
      if (currIndex === mapIndex) {
        return { ...el, objVal: [...val] };
      }
      return el;
    });
    handleUpdate(updatedValues);
    setValues(updatedValues);
  };

  const handleDelete = (mapIndex) => {
    const updatedValues = _.reduce(
      values,
      (acc, elObj, currIndex) => {
        if (mapIndex !== currIndex) {
          acc.push({ ...elObj });
        }
        return acc;
      },
      [],
    );
    updateKeyError(mapIndex, "");
    handleUpdate(updatedValues);
    setValues(updatedValues);
  };

  return (
    <Box id={id}>
      <Typography variant="subtitle1" id={labelId}>
        {label}
      </Typography>
      {_.map(values, ({ objKey, objVal }, mapIndex) => (
        <Box
          className={classes.dictWrapper}
          display={"flex"}
          key={`dict_item_${id}_${objVal.length}_${filterToSnakeCase(objKey)}`}
        >
          <Box className={classes.dictItemWrapper}>
            <Box display={"flex"} alignItems={"flex-end"} flex={5} mt={1}>
              <TextField
                id={`${id}_${mapIndex}_key_input`}
                disabled={isDisabledAction && !keyErrors[mapIndex]}
                defaultValue={objKey}
                onChange={(e) => handleValidateUpdatingKey(e, mapIndex)}
                onBlur={(e) => handleUpdateKey(e, mapIndex)}
              />
            </Box>
            <Box display={"flex"} alignItems={"flex-end"} flex={10} ml={1} mt={1}>
              <ValueInputComponent
                id={`${id}_${mapIndex}_value_input`}
                disabled={isDisabledAction && !keyErrors[mapIndex]}
                defaultValue={objVal}
                onChange={(_name, val) => handleUpdateValue(val, mapIndex)}
                name={objKey}
                options={_.union(
                  options.filter((el) => !_.includes(disabledOptions, el.value)),
                  options.filter((el) => _.includes(objVal, el.value)),
                )}
              />
            </Box>
            <Box display={"flex"} alignItems={"flex-end"} flex={1}>
              <Tooltip title="" placement="top">
                <IconButton
                  disabled={isDisabledAction}
                  className={classes.deleteBtn}
                  onClick={() => handleDelete(mapIndex)}
                  size="large"
                >
                  <DeleteForeverOutlinedIcon
                    style={{
                      color: isDisabledAction
                        ? theme.palette.notSelected.light
                        : theme.colorDeleteIcons,
                    }}
                  />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          <Box className={classes.dictItemWrapper}>
            <Box>
              <FormHelperText error={Boolean(keyErrors[mapIndex])}>
                {keyErrors[mapIndex]}
              </FormHelperText>
            </Box>
            <Box />
          </Box>
        </Box>
      ))}
      <Box display={"flex"} mt={2}>
        <Button
          disabled={isDisabledAction}
          variant="outlined"
          color="primary"
          onClick={handleCreateNewItemSetValue}
        >
          {t("dict-field.btn-add")}
        </Button>
      </Box>
    </Box>
  );
};

InputDict.propTypes = {
  id: PropTypes.string.isRequired,
  ValueInputComponent: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
  options: PropTypes.array,
};

InputDict.defaultProps = {
  options: [],
  // defaultValue: [],
};

export default InputDict;
