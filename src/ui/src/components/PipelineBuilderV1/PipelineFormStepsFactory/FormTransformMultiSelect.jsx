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
import { useTranslation } from "react-i18next";
import { FormControl, Box, Button } from "@mui/material";

import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import AddIcon from "@mui/icons-material/Add";

import filters from "filters";
import DynamicFormElement from "components/FormElements/DynamicFormElement";

import FormFeatureFormCreate from "./FormSetTransormFormAdd";
import FormFeatureTransfromForm from "./FormSetTransfromForm";
import useStyles from "../../../containers/BuildModel/BuildModeStyle";

const FormTransformMultiSelect = ({ inputData, onClose, onSubmit, onShowInfo }) => {
  const { t } = useTranslation("models");
  const classes = useStyles();

  // show select tranform form
  const [isShowAddTranformForm, setIsShowAddTranformForm] = useState(true);
  const [selectedTransforms, setSelectedTransforms] = useState([]);
  const [transformsParameters, setTransformsParameters] = useState({});

  const getTransformsToAdd = () => {
    return inputData.options.filter(
      (el) => !selectedTransforms.find((trsf) => trsf.name === el.name),
    );
  };

  const getTransformParameter = (el) => {
    if (transformsParameters && transformsParameters[el.parent]) {
      return transformsParameters[el.parent][el.name];
    }
    return el.default;
  };

  useEffect(() => {
    if (inputData?.default) {
      let defaultList = [];
      if (inputData?.default) {
        defaultList = Array.isArray(inputData?.default)
          ? [...inputData?.default]
          : [inputData?.default];
      }
      if (defaultList?.length) {
        const transformList = [];
        inputData.options.forEach((option) => {
          if (defaultList.includes(option.name)) {
            transformList.push({ ...option });
          }
        });
        setIsShowAddTranformForm(false);
        setSelectedTransforms([...transformList]);
      }
    }
  }, []);

  const handleShowAddTransformForm = (isShow) => {
    setIsShowAddTranformForm(isShow);
  };

  const handleSubmitCreateForm = (newTransforms) => {
    const transformList = inputData.options.filter((trsf) => newTransforms.includes(trsf.name));
    handleShowAddTransformForm(false);
    setSelectedTransforms((prevVal) => [...prevVal, ...transformList]);
  };

  const handleShowFeatureDecscription = (name, description) => {
    if (description) {
      onShowInfo(name, description);
    }
  };

  const handleChange = (parent, name, value) => {
    setTransformsParameters((prevVal) => {
      const updatedVal = { ...prevVal };

      if (updatedVal[parent] && updatedVal[parent][name]) {
        // if value is in obj
        updatedVal[parent][name] = value;
      } else if (updatedVal[parent]) {
        const otherVal = { ...updatedVal[parent] };
        updatedVal[parent] = {
          ...otherVal,
          [name]: value,
        };
      } else {
        updatedVal[parent] = {
          [name]: value,
        };
      }
      return updatedVal;
    });
  };

  const handleDeleteFeature = (uuid) => {
    const updatedTransforms = selectedTransforms.filter((el) => el.uuid !== uuid); // copy
    setSelectedTransforms(updatedTransforms);
  };

  const handleSubmit = () => {
    const transfroms = [];
    selectedTransforms.forEach((transform) => {
      transfroms.push({
        transform: transform.name,
        ...inputData.fieldset
          .filter((option) => option.parent === transform.name)
          .reduce((acc, el) => {
            acc[el.name] = getTransformParameter(el);
            return acc;
          }, {}),
      });
    });
    onSubmit({ data: transfroms, customName: selectedTransforms.map((el) => el.name).join(", ") });
  };

  return (
    <>
      <Box>
        {!isShowAddTranformForm ? (
          <Box className={classes.addButtonWrapper}>
            <Button
              startIcon={<AddIcon />}
              color="primary"
              onClick={(_e) => handleShowAddTransformForm(true)}
            >
              {t("model-builder.drawer-edit-step-add-btn")}
            </Button>
          </Box>
        ) : null}
        {isShowAddTranformForm ? (
          <FormFeatureFormCreate
            features={getTransformsToAdd()}
            onClose={(_e) => handleShowAddTransformForm(false)}
            onSubmit={handleSubmitCreateForm}
            onShowInfo={onShowInfo}
          />
        ) : null}
        {!isShowAddTranformForm ? (
          <>
            <Box className={classes.subtypesWrapper}>
              {selectedTransforms?.length ? (
                selectedTransforms.map((transform, i) => (
                  <FormFeatureTransfromForm
                    key={`feature_transform_form_${i}`}
                    name={transform.name}
                    subtype={transform.subtype}
                    expanded={true} // tmp
                    isShowInfo={Boolean(transform.description)}
                    onInfo={(_) => {
                      handleShowFeatureDecscription(transform.name, transform.description);
                    }}
                    onDelete={(_) => handleDeleteFeature(transform.uuid)}
                  >
                    <Box className={classes.formWrapper}>
                      {inputData.fieldset
                        .filter((option) => option.parent === transform.name)
                        .map((el) => (
                          <FormControl
                            key={`input_cntr_fc_${filters.filterToSnakeCase(
                              el.parent,
                            )}_${filters.filterToSnakeCase(el.name)}`}
                            fullWidth={true}
                            className={classes.formControl}
                          >
                            <DynamicFormElement
                              key={`params_${filters.filterToSnakeCase(
                                el.parent,
                              )}_${filters.filterToSnakeCase(el.name)}`}
                              id={`params_${filters.filterToSnakeCase(
                                el.parent,
                              )}_${filters.filterToSnakeCase(el.name)}`}
                              labelId={`params_${filters.filterToSnakeCase(
                                el.parent,
                              )}_${filters.filterToSnakeCase(el.name)}`}
                              defaultValue={getTransformParameter(el)}
                              name={el.name}
                              formType={el.type}
                              label={el.label}
                              options={el.options}
                              onChange={(name, value) => handleChange(el.parent, name, value)}
                              {...el}
                            />
                          </FormControl>
                        ))}
                    </Box>
                  </FormFeatureTransfromForm>
                ))
              ) : (
                <></>
              )}
            </Box>
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
          </>
        ) : null}
      </Box>
    </>
  );
};

export default FormTransformMultiSelect;
