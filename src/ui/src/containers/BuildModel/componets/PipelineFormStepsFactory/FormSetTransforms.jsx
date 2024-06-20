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

/* eslint-disable template-curly-spacing */
import React, { useState, useEffect, useMemo } from "react";
import _ from "lodash";

import { useTranslation } from "react-i18next";
import { FormControl, Box, Button } from "@mui/material";

import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import AddIcon from "@mui/icons-material/Add";

import filters from "filters";
import DynamicFormElement from "components/FormElements/DynamicFormElement";
import FormSetTransormFormAdd from "./FormSetTransormFormAdd";
import FormFeatureTransfromForm from "./FormSetTransfromForm";

import useStyles from "./FormStyle";

const FormSetTransforms = ({
  inputData,
  onClose,
  onSubmit,
  onShowInfo,
  onChangeData,
  isUniqueTransforms = false,
}) => {
  /**
   * We use handling by names selectedTransformNames to keep order for submitting data
   */

  const { t } = useTranslation("models");
  const classes = useStyles();

  const [isChangedData, setIsChangedData] = useState(false);
  const [isShowCreateForm, setIsShowCreateForm] = useState(false);
  const [parameters, setParameters] = useState({});

  const [selectedTransforms, setSelectedTransforms] = useState([]);

  const transformsMap = useMemo(() => {
    if (!_.isEmpty(inputData?.featureList)) {
      return inputData.featureList.reduce((acc, el) => {
        acc[el.id] = el;
        return acc;
      }, {});
    }
    return {};
  }, [inputData]);

  const transformsToAdd = useMemo(() => {
    if (isUniqueTransforms) {
      return inputData.featureList.filter(
        (el) => !selectedTransforms.map(({ id }) => id).includes(el.id),
      );
    }
    return inputData.featureList;
  }, [inputData, selectedTransforms, isUniqueTransforms]);

  const transformsToEdit = useMemo(() => {
    if (!_.isEmpty(transformsMap)) {
      return selectedTransforms.map((el) => ({ ...transformsMap[el.id], localId: el.localId }));
    }
    return [];
  }, [transformsMap, selectedTransforms]);

  const getInputContractParameterValue = (inputContract, transformKey) => {
    const { name } = inputContract;
    if (parameters && parameters[transformKey] && parameters[transformKey][name]) {
      return parameters[transformKey][name];
    }
    return inputContract.default;
  };

  const getUpdatedData = () => {
    const features = [];

    transformsToEdit.forEach((transform) => {
      features.push({
        name: transform.name,
        params: transform.inputContract.reduce((acc, el) => {
          acc[el.name] = getInputContractParameterValue(el, transform.localId);
          return acc;
        }, {}),
      });
    });

    return features;
  };

  useEffect(() => {
    const { defaultFeatureList } = inputData || [];

    if (!_.isEmpty(defaultFeatureList)) {
      setIsShowCreateForm(false);
      setSelectedTransforms(defaultFeatureList);
      const defaultParams = defaultFeatureList.reduce((acc, transform) => {
        if (!_.isEmpty(transform?.params)) {
          acc[transform.localId] = { ...transform.params };
        }
        return acc;
      }, {});
      setParameters(defaultParams);
    }
  }, [inputData]);

  useEffect(() => {
    onChangeData(isChangedData, getUpdatedData());
  }, [parameters]);

  const handleShowCreateForm = (isShow) => {
    setIsShowCreateForm(isShow);
  };

  const handleAddNewTransforms = (newTransforms) => {
    setSelectedTransforms((prevVal) => _.concat(prevVal, newTransforms));
    setIsShowCreateForm(false);
  };

  const handleDeleteFeature = (deletingLocalID) => {
    setSelectedTransforms((prevVal) => prevVal.filter((el) => el.localId !== deletingLocalID));
  };

  const handleShowFeatureDecscription = (name, description) => {
    if (description) {
      onShowInfo(name, description);
    }
  };

  const handleChange = (transformKey, name, value) => {
    let isChanged = false;
    // eslint-disable-next-line consistent-return
    const updatedVal = { ...parameters };
    if (updatedVal[transformKey] && updatedVal[transformKey][name]) {
      if (updatedVal[transformKey][name] !== value) {
        updatedVal[transformKey][name] = value;
        isChanged = true;
      }
    } else if (updatedVal[transformKey]) {
      updatedVal[transformKey][name] = value;
      isChanged = true;
    } else {
      updatedVal[transformKey] = {
        [name]: value,
      };
      isChanged = true;
    }
    if (isChanged) {
      setIsChangedData(true);
      setParameters(updatedVal);
    }
  };

  const handleSubmit = () => {
    const updatedData = getUpdatedData();
    onSubmit({
      data: updatedData,
      customName: _.join(
        updatedData.map((el) => el.name),
        ", ",
      ),
    });
  };

  return (
    <Box>
      {!isShowCreateForm && transformsToAdd?.length ? (
        <Box className={classes.addButtonWrapper}>
          <Button
            startIcon={<AddIcon />}
            color="primary"
            onClick={(_e) => handleShowCreateForm(true)}
          >
            {t("model-builder.form-transform-set")}
          </Button>
        </Box>
      ) : null}
      {isShowCreateForm ? (
        <FormSetTransormFormAdd
          transforms={transformsToAdd}
          onClose={(_e) => handleShowCreateForm(false)}
          onSubmit={handleAddNewTransforms}
          onShowInfo={onShowInfo}
          isUniqueTransforms={isUniqueTransforms}
        />
      ) : null}
      {!isShowCreateForm ? (
        <>
          <Box className={classes.subtypesWrapper}>
            {transformsToEdit.map((transform, transformIndex) => (
              <Box
                key={`${transform.name}-${transformIndex}`}
                mb={1}
                p={2}
                className={classes.borderedFormWrapper}
              >
                <FormFeatureTransfromForm
                  key={`feature_transform_form_${transformIndex}`}
                  name={transform.name}
                  subtype={transform.subtype}
                  expanded={true} // tmp
                  isShowInfo={Boolean(transform.description)}
                  onInfo={(_e) =>
                    handleShowFeatureDecscription(transform.name, transform.description)
                  }
                  onDelete={() => handleDeleteFeature(transform.localId)}
                >
                  <Box className={classes.formWrapper}>
                    {transform.inputContract
                      .filter((el) => !el.isFormHidden)
                      .map((el) => (
                        <FormControl
                          key={`input_cntr_fc_${el.name}${transform.id}`}
                          fullWidth={true}
                          className={classes.formControl}
                        >
                          <DynamicFormElement
                            id={`input_cntr_${el.id}`}
                            labelId={`input_cntr_lbl${filters.filterToSnakeCase(
                              el.parent,
                            )}_${filters.filterToSnakeCase(el.name)}`}
                            defaultValue={getInputContractParameterValue(el, transform.localId)}
                            name={el.name}
                            formType={el.type}
                            label={el.label}
                            options={el.options}
                            onChange={(name, value) => handleChange(transform.localId, name, value)}
                            {...el}
                          />
                        </FormControl>
                      ))}
                  </Box>
                </FormFeatureTransfromForm>
              </Box>
            ))}
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
  );
};

export default FormSetTransforms;
