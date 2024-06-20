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

/* eslint-disable no-unused-vars */
import React, { useState, useEffect, useMemo } from "react";
import _ from "lodash";

import { useTranslation } from "react-i18next";
import { PIPELINE_STEP_TYPES } from "store/autoML/const";
import { FormControl, Box, Button } from "@mui/material";

import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import AddIcon from "@mui/icons-material/Add";

import filters from "filters";
import DynamicFormElement from "components/FormElements/DynamicFormElement";
import FormFeatureFormCreate from "./FormSetTransormFormAdd";
import FormFeatureTransfromForm from "./FormSetTransfromForm";

import useStyles from "./FormStyle";

const FormFeatureSelector = ({ inputData, onClose, onSubmit, onShowInfo, onChangeData }) => {
  /**
   * We use handling by names selectedFeatureNames to keep order for submitting data
   */

  const { t } = useTranslation("models");
  const classes = useStyles();

  const [isChangedData, setIsChangedData] = useState(false);
  const [isShowCreateForm, setIsShowCreateForm] = useState(false);
  const [featuresParameters, setFeaturesParameters] = useState({});
  const [selectedFeatureNames, setSelectedFeatureNames] = useState([]);

  const defaultParams = useMemo(() => {
    //
    if (!_.isEmpty(inputData?.defaultFeatureList)) {
      return inputData?.defaultFeatureList.reduce((acc, feature) => {
        //
        acc[feature.name] = {};

        if (!_.isEmpty(feature?.inputContract) && !_.isEmpty(feature?.params)) {
          feature?.inputContract.forEach((contactEl) => {
            acc[feature.name][contactEl.name] = feature.params[contactEl.name];
          });
        }

        return acc;
      }, {});
    }
    return {};
  }, [inputData, selectedFeatureNames]);

  const featuresToAdd = useMemo(() => {
    return inputData.featureList.filter((el) => !selectedFeatureNames.includes(el.name));
  }, [inputData, selectedFeatureNames]);

  const featuresToEdit = useMemo(() => {
    return selectedFeatureNames.reduce((acc, featureName) => {
      acc.push(inputData.featureList.find((el) => el.name === featureName));
      return acc;
    }, []);
  }, [inputData, selectedFeatureNames]);

  const getInputContractParameters = (el) => {
    if (
      featuresParameters &&
      featuresParameters[el.parent] &&
      featuresParameters[el.parent][el.name]
    ) {
      return featuresParameters[el.parent][el.name];
    }
    if (defaultParams[el.parent] && defaultParams[el.parent][el.name]) {
      return defaultParams[el.parent][el.name];
    }
    return el.default;
  };

  const updatedFeatures = useMemo(() => {
    const features = [];

    featuresToEdit.forEach((feature) => {
      features.push({
        name: feature.name,
        params: feature.inputContract.reduce((acc, el) => {
          acc[el.name] = getInputContractParameters(el);
          return acc;
        }, {}),
      });
    });

    return features;
  }, [featuresToEdit, featuresParameters, selectedFeatureNames]);

  useEffect(() => {
    const { defaultFeatureList } = inputData || [];

    if (!_.isEmpty(defaultFeatureList)) {
      setSelectedFeatureNames(defaultFeatureList.map((el) => el.name));
      setIsShowCreateForm(false);
    }
  }, [inputData]);

  useEffect(() => {
    setFeaturesParameters(defaultParams);
  }, []);

  useEffect(() => {
    onChangeData(isChangedData, updatedFeatures);
  }, [featuresToEdit, featuresParameters]);

  const handleShowCreateForm = (isShow) => {
    setIsShowCreateForm(isShow);
  };

  const handleSubmitCreateForm = (newFeatures) => {
    setSelectedFeatureNames((prevVal) => [...prevVal, ...newFeatures]);
    setIsShowCreateForm(false);
  };

  const handleDeleteFeature = (name) => {
    setSelectedFeatureNames((prevVal) => prevVal.filter((ftName) => ftName !== name));
  };

  const handleShowFeatureDecscription = (name, description) => {
    if (description) {
      onShowInfo(name, description);
    }
  };

  const handleChange = (parent, name, value) => {
    // eslint-disable-next-line consistent-return
    setFeaturesParameters((prevVal) => {
      const updatedVal = { ...prevVal };

      if (updatedVal[parent] && updatedVal[parent][name]) {
        if (updatedVal[parent][name] !== value) {
          updatedVal[parent][name] = value;
          setIsChangedData(true);
        }
      } else if (updatedVal[parent]) {
        const otherVal = { ...updatedVal[parent] };
        updatedVal[parent] = {
          ...otherVal,
          [name]: value,
        };
        setIsChangedData(true);
      } else {
        updatedVal[parent] = {
          [name]: value,
        };
        setIsChangedData(true);
      }
      return updatedVal;
    });
  };

  const handleSubmit = () => {
    onSubmit({
      data: updatedFeatures,
      customName: _.join(
        updatedFeatures.map((el) => el.name),
        ", ",
      ),
    });
  };

  return (
    <Box>
      {!isShowCreateForm && featuresToAdd?.length ? (
        <Box className={classes.addButtonWrapper}>
          <Button
            startIcon={<AddIcon />}
            color="primary"
            onClick={(_e) => handleShowCreateForm(true)}
          >
            {t("model-builder.form-feature-add-selector")}
          </Button>
        </Box>
      ) : null}
      {isShowCreateForm ? (
        <FormFeatureFormCreate
          features={featuresToAdd}
          onClose={(_e) => handleShowCreateForm(false)}
          onSubmit={handleSubmitCreateForm}
          onShowInfo={onShowInfo}
        />
      ) : null}
      {!isShowCreateForm ? (
        <>
          <Box className={classes.subtypesWrapper}>
            {featuresToEdit.map((feature, featureIndex) => (
              <FormFeatureTransfromForm
                key={`feature_transform_form_${featureIndex}`}
                name={feature.name}
                subtype={feature.subtype}
                expanded={true} // tmp
                isShowInfo={Boolean(feature.description)}
                onInfo={(_e) => handleShowFeatureDecscription(feature.name, feature.description)}
                onDelete={(_e) => handleDeleteFeature(feature.name)}
              >
                <Box className={classes.formWrapper}>
                  {feature.inputContract
                    .filter((el) => !el.isFormHidden)
                    .map((el) => (
                      <FormControl
                        key={`input_cntr_fc_${filters.filterToSnakeCase(
                          el.parent,
                        )}_${filters.filterToSnakeCase(el.name)}`}
                        fullWidth={true}
                        className={classes.formControl}
                      >
                        <DynamicFormElement
                          id={`input_cntr_${filters.filterToSnakeCase(
                            el.parent,
                          )}_${filters.filterToSnakeCase(el.name)}`}
                          labelId={`input_cntr_lbl${filters.filterToSnakeCase(
                            el.parent,
                          )}_${filters.filterToSnakeCase(el.name)}`}
                          defaultValue={getInputContractParameters(el)}
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

export default FormFeatureSelector;
