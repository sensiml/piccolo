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

import React, { useState, useCallback, useEffect } from "react";
import _ from "lodash";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";
import { Box, Tooltip, Typography, IconButton, Button, Checkbox } from "@mui/material";

import KeyboardArrowDownOutlinedIcon from "@mui/icons-material/KeyboardArrowDownOutlined";
import KeyboardArrowUpOutlinedIcon from "@mui/icons-material/KeyboardArrowUpOutlined";

import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import AddIcon from "@mui/icons-material/Add";

import SelectMultiChip from "components/FormElements/SelectMultiChip";

import FormAutoMLFeaturesFormList from "./FormAutoMLFeaturesFormList";
import useStyles from "./FormStyle";

const FormAutoMLFeaturesFormAdd = ({
  inputData,
  onShowInfo,
  onClose,
  onAdd,
  queryColumns = [],
}) => {
  const { t } = useTranslation("models");
  const classes = useStyles();

  const [expandedSuptypes, setExpandedSuptypes] = useState([]);
  const [featuresParameters, setFeaturesParameters] = useState({});

  const [selectedSubtype, setSelectedSubtype] = useState([]);
  const [selectedFeatures, setSelectedFeatures] = useState([]);

  const [defaultColumns, setDefaultColumns] = useState([]);

  const getFeaturesBySubtype = (subtype) => {
    const features = inputData.featureList.filter((feature) => feature.subtype === subtype);
    // return inputData.featureList.filter(feature => feature.subtype === subtype);
    const res = features.map((feature) => {
      return { ...feature, isSelected: selectedFeatures.includes(feature.name) };
    });

    return res;
  };

  const getInputContractParameters = useCallback(
    (el) => {
      if (featuresParameters && featuresParameters[el.parent]) {
        return featuresParameters[el.parent][el.name];
      }
      return el.name === "columns" ? defaultColumns : el.default;
    },
    [defaultColumns, featuresParameters], // update with default columns
  );

  const handleSelectSubType = async (subtype) => {
    const featureList = inputData.featureList
      .filter((ft) => ft.subtype === subtype)
      .map((ft) => ft.name);

    if (!selectedSubtype.includes(subtype)) {
      setSelectedSubtype([...selectedSubtype, subtype]);
      setSelectedFeatures((prevFeatures) => [...prevFeatures, ...featureList]);
    } else {
      setSelectedSubtype(selectedSubtype.filter((subtypeEl) => subtypeEl !== subtype));
      setSelectedFeatures((prevFeatures) => prevFeatures.filter((ft) => !featureList.includes(ft)));
    }
  };

  const handleExpandSubtype = (subtype) => {
    if (expandedSuptypes.includes(subtype)) {
      setExpandedSuptypes((val) => _.filter(val, (el) => el !== subtype));
    } else {
      setExpandedSuptypes((val) => [...val, subtype]);
    }
  };

  const handleSelectFeature = (feature) => {
    if (!selectedFeatures.includes(feature)) {
      setSelectedFeatures([...selectedFeatures, feature]);
    } else {
      setSelectedFeatures(selectedFeatures.filter((ftEl) => ftEl !== feature));
    }
  };

  const handleChangeFeatureParams = (parent, name, value) => {
    setFeaturesParameters((prevVal) => {
      const updatedVal = { ...prevVal };

      if (updatedVal[parent] && updatedVal[parent][name]) {
        // if value is in obj
        updatedVal[parent][name] = value;
      } else if (updatedVal[parent]) {
        // assign value to object
        const otherVal = { ...updatedVal[parent] };
        updatedVal[parent] = { ...otherVal, [name]: value };
      } else {
        // create parent
        updatedVal[parent] = { [name]: value };
      }
      return updatedVal;
    });
  };

  const handleAdd = () => {
    const features = [];
    const subtypes = [];

    inputData.featureList.forEach((feature) => {
      if (selectedFeatures.includes(feature.name)) {
        if (feature?.subtype && !subtypes.includes(feature.subtype)) {
          subtypes.push(feature.subtype);
        }

        features.push({
          ...feature,
          isSelected: true,
          params: feature.inputContract.reduce((acc, el) => {
            acc[el.name] = getInputContractParameters(el); // includes hidden feilds
            return acc;
          }, {}),
        });
      }
    });

    onAdd(features, subtypes);
  };

  const handeChangeDefaultColumns = (_name, selectedColumns) => {
    setDefaultColumns(selectedColumns);
    setFeaturesParameters((params) => {
      _.keys(params).forEach((parentKey) => {
        handleChangeFeatureParams(parentKey, "columns", selectedColumns);
      });
    });
  };

  useEffect(() => {
    setDefaultColumns(queryColumns);
  }, []);

  return (
    <>
      <Box className={classes.subtypesWrapper}>
        <Box className={classes.subtypesWrap} mb={2}>
          <SelectMultiChip
            name="queryColumns"
            id="queryColumnsId"
            label="Default Columns"
            options={queryColumns.map((column) => ({ name: column, value: column }))}
            defaultValue={queryColumns}
            onChange={handeChangeDefaultColumns}
          />
        </Box>
        {inputData?.subtypes?.length ? (
          inputData.subtypes.map((subtype, index) => (
            <Box className={classes.subtypesWrap} key={`feature_${index}`}>
              <Box className={classes.featureFormSubtypeHeader}>
                <Box className={classes.wrapperCheckHeader}>
                  <Checkbox
                    checked={_.includes(selectedSubtype, subtype)}
                    onChange={() => handleSelectSubType(subtype)}
                  />
                  <Typography
                    variant="subtitle1"
                    onClick={() => handleExpandSubtype(subtype)}
                    // eslint-disable-next-line max-len
                    className={`${classes.featureFormSubtypeHeaderTitle} ${classes.featureFormSubtypeHeaderClicked}`}
                  >
                    {subtype}
                  </Typography>
                </Box>
                <Box>
                  <Tooltip
                    title={
                      expandedSuptypes.includes(subtype) ? t("tooltip-close") : t("tooltip-open")
                    }
                    placement="top"
                  >
                    <IconButton onClick={() => handleExpandSubtype(subtype)} type="outline">
                      {expandedSuptypes.includes(subtype) ? (
                        <KeyboardArrowUpOutlinedIcon color="primary" />
                      ) : (
                        <KeyboardArrowDownOutlinedIcon color="primary" />
                      )}
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              {expandedSuptypes.includes(subtype) ? (
                <FormAutoMLFeaturesFormList
                  onShowInfo={onShowInfo}
                  subtype={subtype}
                  featureList={getFeaturesBySubtype(subtype)}
                  getInputContractParameters={getInputContractParameters}
                  onSelectFeature={handleSelectFeature}
                  onChangeFeatureParams={handleChangeFeatureParams}
                />
              ) : null}
            </Box>
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
        >
          {t("model-builder.drawer-edit-step-fg-btn-cancel")}
        </Button>
        <Button
          onClick={handleAdd}
          data-testid="edit-step-form-submit"
          className={classes.drawerFormButton}
          startIcon={<AddIcon />}
          // disabled={}
          size="large"
          variant="contained"
          color="primary"
        >
          {t("model-builder.drawer-edit-step-fg-btn-add")}
        </Button>
      </Box>
    </>
  );
};

FormAutoMLFeaturesFormAdd.propTypes = {
  inputData: PropTypes.object,
  onShowInfo: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
  onAdd: PropTypes.func.isRequired,
};

FormAutoMLFeaturesFormAdd.defaultProps = {
  inputData: { featureList: [], subtypes: [] },
};

export default FormAutoMLFeaturesFormAdd;
