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

/* eslint-disable react/jsx-curly-newline */
/* eslint-disable max-len */
import _ from "lodash";
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { PIPELINE_STEP_TYPES } from "store/autoML/const";
import {
  FormControl,
  FormHelperText,
  Box,
  Tooltip,
  Typography,
  Link,
  Button,
  Collapse,
} from "@mui/material";

import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import AspectRatioIcon from "@mui/icons-material/AspectRatio";
import AddIcon from "@mui/icons-material/Add";

import { useTheme } from "@mui/material/styles";

import filters from "filters";
import DynamicFormElement from "components/FormElements/DynamicFormElement";
import FormCreateFromSubtype from "./FormFeatureFromCreateBySubtype";
import FormFeatureFormCreate from "./FormSetTransormFormAdd";
import FormFeatureTransfromForm from "./FormSetTransfromForm";

import useStyles from "./FormStyle";

const FormFeatureGenerator = ({ inputData, onClose, onSubmit, onChangeData, onShowInfo }) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const theme = useTheme();

  const [isShowCreateFromSubtype, setIsShowCreateFromSubtype] = useState(true);
  const [isShowCreateFrom, setIsShowCreateFrom] = useState(false);
  const [featureExpanded, setFeatureExpanded] = useState("");
  const [subtypeExpanded, setSubtypeExpanded] = useState("");
  const [defaultInputContracts, setDefaultInputContracts] = useState({});
  const [defaultParameters, setDefaultParameters] = useState({});
  const [featuresParameters, setFeaturesParameters] = useState({});
  const [selectedSubtype, setSelectedSubtype] = useState([]);
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [defaultValuesError, setDefaultValuesError] = useState({});

  const getSubtypesToAdd = () => {
    if (!inputData?.subtypes?.length) {
      return [];
    }
    return inputData.subtypes.filter((subtype) => !selectedSubtype.includes(subtype));
  };

  const getFeaturesToAdd = () => {
    return (
      inputData.featureList
        .filter((el) => !selectedFeatures.find((feature) => feature.name === el.name))
        .sort((a, b) => (a.subtype > b.subtype ? 1 : -1)) || []
    );
  };

  const getFeaturesBySubtype = (subtype) => {
    return selectedFeatures.filter((feature) => feature.subtype === subtype);
  };

  const getDefaultInputContractParameters = (el) => {
    if (defaultParameters[el.name]) {
      return defaultParameters[el.name];
    }
    return el.default;
  };

  const getInputContractParameters = (el) => {
    if (featuresParameters && featuresParameters[el.parent]) {
      return featuresParameters[el.parent][el.name];
    }
    if (defaultParameters[el.name]) {
      return defaultParameters[el.name];
    }
    return el.default;
  };

  useEffect(() => {
    const { defaultFeatureList } = inputData;
    if (defaultFeatureList?.length) {
      const subtypeList = [];
      const featureList = [];
      inputData.featureList.forEach((el) => {
        if (defaultFeatureList.includes(el.name)) {
          featureList.push(el);
          if (!subtypeList.includes(el.subtype)) {
            subtypeList.push(el.subtype);
          }
        }
      });
      if (subtypeList?.length) {
        setIsShowCreateFromSubtype(false);
      }
      setSelectedFeatures(featureList);
      setSelectedSubtype(subtypeList);
    }
  }, []);

  useEffect(() => {
    if (defaultParameters) {
      setDefaultValuesError({});
    }
  }, [defaultParameters]);

  useEffect(() => {
    if (selectedFeatures) {
      const inputContract = {};
      selectedFeatures.forEach((feature) => {
        feature.inputContract.forEach((inpContr) => {
          if (inputContract[inpContr.name] === undefined) {
            inputContract[inpContr.name] = { ...inpContr };
          } else if (inputContract[inpContr.name].default === undefined) {
            inputContract[inpContr.name].default = inpContr.default;
          }
        });
      });
      setDefaultInputContracts(Object.values(inputContract));
    }
  }, [selectedFeatures]);

  const upateDefaultParameters = async (name, value) => {
    // uses for async update default parameters
    setDefaultParameters((prevValue) => {
      return { ...prevValue, [name]: value };
    });
  };

  const validateDefaultForm = () => {
    let isValid = true;
    defaultInputContracts
      .filter((el) => !el.isFormHidden)
      .forEach((el) => {
        if (defaultParameters[el.name] === undefined) {
          isValid = false;
          setDefaultValuesError((prevValue) => ({
            ...prevValue,
            [el.name]: t("model-builder.drawer-edit-step-err-req"),
          }));
        }
      });
    return isValid;
  };

  const handleShowCreateFormSubtype = (isShow) => {
    setIsShowCreateFromSubtype(isShow);
  };

  const handleShowCreateForm = (isShow) => {
    setIsShowCreateFrom(isShow);
  };

  const handleFeatureExpand = (uuid) => {
    if (featureExpanded !== uuid) {
      setFeatureExpanded(uuid);
    } else {
      setFeatureExpanded("");
    }
  };

  const handleShowFeatureDecscription = (name, description) => {
    if (description) {
      onShowInfo(name, description);
    }
  };

  const handleDefaultChange = (name, value) => {
    // set only 1 defaultCurrentParameter for optimization,
    // see at useEffect of defaultCurrentParameter
    upateDefaultParameters(name, value);
  };

  const handleExpandSubTypeForm = (subtype) => {
    setSubtypeExpanded((prevVal) => {
      if (prevVal === subtype) {
        return "";
      }
      return subtype;
    });
  };

  const handleSubmitCreateFormSubtype = (newSubtypes) => {
    // eslint-disable-next-line prettier/prettier
    const featureList = inputData.featureList.filter((feature) => {
      return newSubtypes.includes(feature.subtype);
    });
    onChangeData(true);
    handleShowCreateFormSubtype(false);
    setSelectedSubtype((prevVal) => [...prevVal, ...newSubtypes]);
    setSelectedFeatures((prevVal) => [...prevVal, ...featureList]);
  };

  const handleSubmitCreateForm = (newFeatures) => {
    const newSubtypes = [];
    // eslint-disable-next-line prettier/prettier
    const featureList = inputData.featureList.filter((feature) => {
      return newFeatures.includes(feature.name);
    });
    onChangeData(true);
    handleShowCreateForm(false);
    featureList.forEach((feature) => {
      if (!selectedSubtype.includes(feature.subtype) && !newSubtypes.includes(feature.subtype)) {
        newSubtypes.push(feature.subtype);
      }
    });
    setSelectedSubtype((prevVal) => [...prevVal, ...newSubtypes]);
    setSelectedFeatures((prevVal) => [...prevVal, ...featureList]);
  };

  const handleDeleteSubType = (subtype) => {
    onChangeData(true);
    const updatedSubtypes = selectedSubtype.filter((subtypeEl) => subtypeEl !== subtype); // copy;
    setSelectedSubtype(updatedSubtypes);
    const updatedFeatures = selectedFeatures.filter((feature) => feature.subtype !== subtype); // copy;
    setSelectedFeatures(updatedFeatures);
    if (_.isEmpty(updatedSubtypes)) {
      handleShowCreateFormSubtype(true);
    }
  };

  const handleDeleteFeature = (subtype, uuid) => {
    onChangeData(true);
    setSelectedFeatures((prevVal) => {
      const updatedFetures = prevVal.filter((el) => el.uuid !== uuid); // copy
      if (!updatedFetures.find((el) => el.subtype === subtype)) {
        // when it last feture delete subtype
        handleDeleteSubType(subtype);
      }
      return updatedFetures;
    });
  };

  const handleChange = (parent, name, value, defaultValue) => {
    onChangeData(value !== defaultValue);
    setFeaturesParameters((prevVal) => {
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

  const handleSubmit = () => {
    const features = [];
    if (validateDefaultForm()) {
      selectedFeatures.forEach((feature) => {
        features.push({
          name: feature.name,
          params: feature.inputContract.reduce((acc, el) => {
            acc[el.name] = getInputContractParameters(el); // includes hidden feilds
            return acc;
          }, {}),
        });
      });
      onSubmit({ data: features, customName: PIPELINE_STEP_TYPES.FEATURE_GENERATOR });
    }
  };

  return (
    <Box>
      {!isShowCreateFromSubtype && !isShowCreateFrom ? (
        <Box className={classes.addButtonWrapper}>
          <Button
            startIcon={<AddIcon />}
            color="primary"
            onClick={(_e) => handleShowCreateFormSubtype(true)}
          >
            {t("model-builder.form-feature-add-subtype-btn")}
          </Button>
          <Button
            startIcon={<AddIcon />}
            color="primary"
            onClick={(_e) => handleShowCreateForm(true)}
          >
            {t("model-builder.form-feature-add-individual-btn")}
          </Button>
        </Box>
      ) : null}
      {isShowCreateFromSubtype ? (
        <>
          <Typography variant="subtitle1" className={classes.featureFormSubtypeHeaderTitle}>
            {t("model-builder.form-feature-add-subtype-header")}
          </Typography>
          <FormCreateFromSubtype
            subtypes={getSubtypesToAdd()}
            onClose={(_e) => handleShowCreateFormSubtype(false)}
            onSubmit={handleSubmitCreateFormSubtype}
            onShowInfo={onShowInfo}
          />
        </>
      ) : null}
      {isShowCreateFrom ? (
        <FormFeatureFormCreate
          features={getFeaturesToAdd()}
          onClose={(_e) => handleShowCreateForm(false)}
          onSubmit={handleSubmitCreateForm}
          onShowInfo={onShowInfo}
        />
      ) : null}
      {!isShowCreateFromSubtype && !isShowCreateFrom ? (
        <>
          <Box className={classes.subtypesWrapper}>
            {defaultInputContracts?.length ? (
              <Box className={classes.formDefaultWrapper}>
                <Typography variant="subtitle1" className={classes.featureFormSubtypeHeaderTitle}>
                  Default Parameters
                </Typography>
                {defaultInputContracts
                  .filter((el) => !el.isFormHidden)
                  .map((el) => (
                    <FormControl
                      key={`input_cntr_fc_${filters.filterToSnakeCase(
                        el.parent,
                      )}_${filters.filterToSnakeCase(el.name)}`}
                      fullWidth={true}
                      className={classes.formControl}
                      error={Boolean(defaultValuesError[el.name])}
                    >
                      <DynamicFormElement
                        key={`input_cntr_${filters.filterToSnakeCase(
                          el.parent,
                        )}_${filters.filterToSnakeCase(el.name)}`}
                        id={`input_cntr_${filters.filterToSnakeCase(
                          el.parent,
                        )}_${filters.filterToSnakeCase(el.name)}`}
                        labelId={`input_cntr_lbl${filters.filterToSnakeCase(
                          el.parent,
                        )}_${filters.filterToSnakeCase(el.name)}`}
                        defaultValue={getDefaultInputContractParameters(el)}
                        name={el.name}
                        formType={el.type}
                        label={el.label}
                        options={el.options}
                        onChange={handleDefaultChange}
                        {...el}
                      />
                      {defaultValuesError[el.name] ? (
                        <FormHelperText>{defaultValuesError[el.name]}</FormHelperText>
                      ) : null}
                    </FormControl>
                  ))}
              </Box>
            ) : null}
            {selectedSubtype.map((subtype, index) => (
              <Box className={classes.subtypesWrap} key={`feature_${index}`}>
                <Box className={classes.featureFormSubtypeHeader}>
                  <Box>
                    <Typography
                      variant="subtitle1"
                      className={classes.featureFormSubtypeHeaderTitle}
                    >
                      {subtype}
                    </Typography>
                  </Box>
                  <Box>
                    <Tooltip title={t("tooltip-edit")} placement="top">
                      <Link
                        onClick={(_e) => handleExpandSubTypeForm(subtype)}
                        className={classes.actionIcon}
                      >
                        <AspectRatioIcon style={{ color: theme.colorEditIcons }} />
                      </Link>
                    </Tooltip>
                    <Tooltip title={t("tooltip-delete")} placement="top">
                      <Link
                        onClick={(_e) => handleDeleteSubType(subtype)}
                        className={classes.actionIcon}
                      >
                        <DeleteForeverOutlinedIcon style={{ color: theme.colorDeleteIcons }} />
                      </Link>
                    </Tooltip>
                  </Box>
                </Box>
                <Collapse timeout={300} in={Boolean(subtype === subtypeExpanded)}>
                  <>
                    {getFeaturesBySubtype(subtype).map((feature, i) => (
                      <FormFeatureTransfromForm
                        key={`feature_transform_form_${i}`}
                        name={feature.name}
                        expanded={Boolean(feature.uuid === featureExpanded)}
                        isShowInfo={Boolean(feature.description)}
                        onEdit={(_e) => handleFeatureExpand(feature.uuid)}
                        // eslint-disable-next-line prettier/prettier
                        onInfo={(_e) =>
                          handleShowFeatureDecscription(feature.name, feature.description)
                        }
                        onDelete={(_e) => handleDeleteFeature(subtype, feature.uuid)}
                      >
                        {feature.uuid === featureExpanded ? (
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
                                    key={`input_cntr_${filters.filterToSnakeCase(
                                      el.parent,
                                    )}_${filters.filterToSnakeCase(el.name)}`}
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
                                    onChange={(name, value) => {
                                      handleChange(
                                        el.parent,
                                        name,
                                        value,
                                        getInputContractParameters(el),
                                      );
                                    }}
                                    {...el}
                                  />
                                </FormControl>
                              ))}
                          </Box>
                        ) : null}
                      </FormFeatureTransfromForm>
                    ))}
                  </>
                </Collapse>
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

export default FormFeatureGenerator;
