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

import React, { useState, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { Box, Button, FormControl, Typography, Collapse } from "@mui/material";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import filters from "filters";

import HelpIcon from "components/HelpIcon";
import DynamicFormElement from "components/FormElements/DynamicFormElement";
import { AUTOML_PARAM_GROUPS, DISABLE_AUTOML_SELECTION_PARAM_NAME } from "store/autoML/const";

import useStyles from "../../BuildModeStyle";
import useFormStyles from "./FormStyle";

const FormAutoMLParams = ({
  inputData,
  type,
  onSubmit,
  onClose,
  onChangeData,
  name: customName,
}) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const classesForm = useFormStyles();
  const [params, setParams] = useState({});
  const [secondLVLparams, setSecondLVLparams] = useState({});

  const getSecondLvlFieldSet = (parentName, isFormHidden) => {
    const inputDataObj = inputData.find((inputD) => inputD.name === parentName);
    if (inputDataObj?.fieldset?.length && params[parentName]?.length) {
      // show nested params following selected values and hidden prop
      const fieldset = inputDataObj?.fieldset.filter(
        (el) =>
          (params[parentName].includes(el.name) || params[parentName] === el.name) &&
          Boolean(el.isFormHidden) === isFormHidden,
      );
      return fieldset;
    }
    return [];
  };

  const getIsAutoMLSelection = useCallback(() => {
    return params[DISABLE_AUTOML_SELECTION_PARAM_NAME] || false;
  }, [inputData, params]);

  const getIsShowParam = useCallback(
    (paramName, isShowIfParamName) => {
      /*
     some fileds may have parent fields that response on showing that fields
    */
      if (isShowIfParamName) {
        return Boolean(params[isShowIfParamName]) && !getIsAutoMLSelection();
      }
      return !getIsAutoMLSelection() || paramName === DISABLE_AUTOML_SELECTION_PARAM_NAME;
    },
    [params],
  );

  const handleTopParams = (name, value, oppositeValue, defaultValue) => {
    onChangeData(value !== defaultValue);
    setParams((prevValue) => {
      const newVal = { ...prevValue }; // copy
      newVal[name] = value;
      if (oppositeValue && newVal[oppositeValue] !== undefined) {
        if (!newVal[oppositeValue] && !value) {
          newVal[oppositeValue] = !value;
        }
      }
      return newVal;
    });
  };

  const handleSecondLVLParams = (name, value, parent, defaultValue) => {
    onChangeData(value !== defaultValue);
    setSecondLVLparams((prevValue) => {
      const newVal = { ...prevValue }; // copy
      if (!prevValue[parent]) {
        newVal[parent] = { [name]: value };
      } else {
        newVal[parent][name] = value;
      }
      return newVal;
    });
  };

  const handleSubmit = () => {
    const data = Object.entries(params).reduce((acc, [paramKey, paramVal]) => {
      // merge hidden params
      const secondLVLHiddenParams = getSecondLvlFieldSet(paramKey, true);
      const allSecondLVLParams = {
        ...secondLVLparams,
        ...secondLVLHiddenParams.reduce((hiddenAcc, el) => {
          if (!hiddenAcc[el.parent]) {
            hiddenAcc[el.parent] = {};
          }
          hiddenAcc[el.parent][el.name] = el.default;
          return hiddenAcc;
        }, {}),
      };

      acc[paramKey] = {};
      if (allSecondLVLParams[paramKey]) {
        // if has nested value
        if (Array.isArray(paramVal) && paramVal?.length) {
          // isArray
          paramVal.forEach((param) => {
            acc[paramKey][param] = allSecondLVLParams[paramKey][param];
          });
        } else {
          // if
          acc[paramKey][paramVal] = allSecondLVLParams[paramKey][paramVal];
        }
      } else {
        acc[paramKey] = paramVal;
      }
      return acc;
    }, {});
    onSubmit({ data, customName, type });
  };

  return (
    <Box>
      {Object.values(AUTOML_PARAM_GROUPS).map((groupName, index) => (
        <Box mb={2} key={`group_automl_form_${index}`}>
          {inputData?.length &&
            inputData
              .filter((data) => data.group === groupName)
              .map((formEl, inptIndex) => (
                <Collapse
                  key={`${formEl.name}-${inptIndex}`}
                  in={getIsShowParam(formEl.name, formEl.isShowIfParamName)}
                >
                  <Typography
                    variant="subtitle1"
                    className={classesForm.featureFormSubtypeHeaderTitle}
                  >
                    {groupName}
                  </Typography>
                  <Box>
                    <FormControl required fullWidth={true} className={classes.formControl}>
                      <DynamicFormElement
                        key={`top_level_${filters.filterToSnakeCase(formEl.type)}`}
                        id={`top_level_${filters.filterToSnakeCase(formEl.type)}`}
                        labelId={`top_level_label_${filters.filterToSnakeCase(formEl.type)}`}
                        {...formEl}
                        formType={formEl.type}
                        value={params[formEl.name]}
                        defaultValue={formEl.default}
                        onChange={(name, value) => {
                          handleTopParams(name, value, formEl.opposite_value, formEl.default);
                        }}
                        name={formEl.name}
                        label={formEl.label}
                        options={formEl.options}
                      />
                      {formEl.description ? (
                        <Box className={classes.helpIcon}>
                          <HelpIcon toolTip={formEl.description} />
                        </Box>
                      ) : null}
                    </FormControl>
                    {getSecondLvlFieldSet(formEl.name, false).map((el) => (
                      <FormControl
                        required
                        key={`2nd_fc_${filters.filterToSnakeCase(
                          el.parent,
                        )}_${filters.filterToSnakeCase(el.name)}`}
                        fullWidth={true}
                        className={classes.formControl}
                      >
                        <DynamicFormElement
                          key={`second_level_${filters.filterToSnakeCase(el.name)}`}
                          id={`second_level_${filters.filterToSnakeCase(el.name)}`}
                          labelId={`second_level_label${filters.filterToSnakeCase(el.name)}`}
                          {...el}
                          defaultValue={el.default}
                          onChange={(name, value) => {
                            handleSecondLVLParams(name, value, el.parent, el.default);
                          }}
                          name={el.name}
                          formType={el.type}
                          label={el.label}
                          options={el.options}
                        />
                      </FormControl>
                    ))}
                  </Box>
                </Collapse>
              ))}
        </Box>
      ))}
      <Box className={classes.drawerFormButtonWrapper}>
        <Button
          className={`${classes.drawerFormButton} ${classes.mr2}`}
          size="large"
          startIcon={<CancelOutlinedIcon />}
          variant="outlined"
          color="primary"
          onClick={onClose}
          data-testid={"edit-step-form-close"}
        >
          {t("model-builder.drawer-edit-step-btn-cancel")}
        </Button>
        <Button
          onClick={handleSubmit}
          className={classes.drawerFormButton}
          size="large"
          variant="contained"
          color="primary"
          data-testid={"edit-step-form-submit"}
        >
          {t("model-builder.drawer-edit-step-btn-add")}
        </Button>
      </Box>
    </Box>
  );
};

export default FormAutoMLParams;
