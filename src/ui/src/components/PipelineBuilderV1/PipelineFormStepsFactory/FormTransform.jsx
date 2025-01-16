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

import React, { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { FormControl, Collapse, Box, Tooltip, Link, Button, FormHelperText } from "@mui/material";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import filters from "filters";
import HelpIcon from "components/HelpIcon";
import DynamicFormElement from "components/FormElements/DynamicFormElement";
import { useTheme } from "@mui/material/styles";

import useStyles from "../../../containers/BuildModel/BuildModeStyle";

const FormTransform = ({
  inputData,
  onClose,
  onSubmit,
  onShowInfo,
  onChangeData,
  isFormOptionsDisabled,
  editFormKeyId,
}) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const theme = useTheme();
  const [transform, setTransform] = useState("");
  const [disabledTransform, setDisabledTransform] = useState({});
  const [secondValues, setSecondValues] = useState({});
  const [topValuesError, setTopValuesError] = useState({});
  const [secondValuesError, setSecondValuesError] = useState({});
  const [isRendered, setIsRendered] = useState(false);

  useEffect(() => {
    if (isFormOptionsDisabled) {
      if (inputData?.default) {
        setDisabledTransform(inputData?.default);
      }
    }
  }, [isFormOptionsDisabled]);

  useEffect(() => {
    if (secondValues) {
      setSecondValuesError({});
    }
  }, [secondValues]);

  const getDecscription = (name, options) => {
    if (options?.length) {
      return options.find((el) => el.name === name)?.description;
    }
    return "";
  };

  const getDefault = (el) => {
    return el.default;
  };

  const getSecondLvlIsUseParam = (isUseName) => {
    if (isUseName !== undefined) {
      return Boolean(secondValues[isUseName]);
    }
    return true;
  };

  const getSecondLvlFieldSet = (transformName = transform) => {
    const secondLvlFieldSet = inputData?.fieldset?.filter(
      (el) => el.parent === transformName && !el.isFormHidden,
    );
    // set values for hidden elements
    return secondLvlFieldSet;
  };

  const validateForm = () => {
    let isValid = true;
    if (transform === undefined) {
      setTopValuesError((prevValue) => ({
        ...prevValue,
        transform: t("model-builder.drawer-edit-step-err-req"),
      }));
      isValid = false;
    }
    if (inputData?.fieldset?.length) {
      getSecondLvlFieldSet(transform).forEach((el) => {
        if (secondValues[el.name] === undefined) {
          setSecondValuesError((prevValue) => ({
            ...prevValue,
            [el.name]: t("model-builder.drawer-edit-step-err-req"),
          }));
          isValid = false;
        }
      });
    }
    return isValid;
  };

  const handleTopLvlEL = (name, value, defaultValue) => {
    const data = getSecondLvlFieldSet(value).reduce((acc, el) => {
      acc[el.name] = getDefault(el);
      return acc;
    }, {});
    onChangeData(value !== defaultValue, { transform: value, ...data }, true);
    setSecondValues({});
    setTopValuesError({});
    setTransform(value);
  };

  const handleSecondLvlEL = useCallback(
    (name, value, defaultValue) => {
      onChangeData(value !== defaultValue || isRendered, { [name]: value }, false, name);
      setSecondValues((prevValue) => {
        return { ...prevValue, [name]: value };
      });
      setIsRendered(true);
    },
    [isRendered],
  );

  const handleClickTopDecscription = (name, options) => {
    if (options?.length) {
      onShowInfo(name, getDecscription(name, options));
    }
  };

  const handleSubmit = () => {
    if (validateForm()) {
      const hiddenValues = {};
      let customName = "";

      const secondLvlHiddenFieldSet = inputData.fieldset?.filter(
        (el) => el.parent === transform && el.isFormHidden,
      );
      customName = inputData?.customName || transform;
      // set hidden fields
      if (secondLvlHiddenFieldSet?.length) {
        secondLvlHiddenFieldSet.forEach((field) => {
          hiddenValues[field.name] = field.default;
        });
      }
      onSubmit({ data: { transform, ...secondValues, ...hiddenValues }, customName });
    }
  };

  return (
    <>
      <Box>
        <FormControl
          fullWidth={true}
          className={classes.formControl}
          error={Boolean(topValuesError[inputData.name])}
        >
          <DynamicFormElement
            {...inputData}
            id={`top_level_${filters.filterToSnakeCase(inputData.type)}`}
            labelId={`top_level_label_${filters.filterToSnakeCase(inputData.type)}`}
            formType={inputData.type}
            value={transform}
            defaultValue={inputData.default}
            onChange={(name, value) => handleTopLvlEL(name, value, inputData.default)}
            name={inputData.name}
            label={inputData.label}
            options={inputData.options}
          />
          {getDecscription(topValuesError[inputData.name], inputData.options) ? (
            <FormHelperText>{topValuesError[inputData.name]}</FormHelperText>
          ) : null}
          {transform ? (
            <Box className={classes.helpIcon}>
              <Tooltip title={t("Info")} placement="top">
                <Link onClick={() => handleClickTopDecscription(transform, inputData.options)}>
                  <InfoOutlinedIcon style={{ color: theme.colorInfoLinks }} />
                </Link>
              </Tooltip>
            </Box>
          ) : null}
        </FormControl>
        {disabledTransform !== transform &&
          getSecondLvlFieldSet(transform).map((el, index) => (
            <Collapse
              key={`${transform}-${el.name}-${editFormKeyId}-${index}`}
              in={getSecondLvlIsUseParam(el.isUseName)}
            >
              <FormControl
                fullWidth={true}
                className={classes.formControl}
                error={Boolean(secondValuesError[el.name])}
              >
                <DynamicFormElement
                  id={`2nd_el_${filters.filterToSnakeCase(el.parent)}_${filters.filterToSnakeCase(
                    el.name,
                  )}`}
                  labelId={`2nd_el_lbl_${filters.filterToSnakeCase(
                    el.parent,
                  )}_${filters.filterToSnakeCase(el.name)}`}
                  {...el}
                  defaultValue={getDefault(el)}
                  onChange={(name, value) => handleSecondLvlEL(name, value, getDefault(el))}
                  name={el.name}
                  formType={el.type}
                  label={el.label}
                  options={el.options}
                />
                {secondValuesError[el.name] ? (
                  <FormHelperText>{secondValuesError[el.name]}</FormHelperText>
                ) : null}
                {el.description ? (
                  <Box className={classes.helpIcon}>
                    <HelpIcon toolTip={el.description} />
                  </Box>
                ) : null}
              </FormControl>
            </Collapse>
          ))}
        {disabledTransform !== transform ? (
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
        ) : null}
      </Box>
    </>
  );
};

export default FormTransform;
