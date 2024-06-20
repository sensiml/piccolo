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

/* eslint-disable no-confusing-arrow */
import React, { useState, useCallback } from "react";
import PropTypes from "prop-types";

import {
  Box,
  Chip,
  Checkbox,
  FormControl,
  Stack,
  Typography,
  Tooltip,
  IconButton,
} from "@mui/material";

import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";

import DynamicFormElement from "components/FormElements/DynamicFormElement";

import { useTranslation } from "react-i18next";

import useStyles from "./FormStyle";

const MAX_COLUMNS_IN_PREVIEW = 7;

const FormAutoMLFeaturesFormList = ({
  featureList,
  getInputContractParameters,
  onShowInfo,
  onSelectFeature,
  onDeleteFeature,
  onChangeFeatureParams,
  isShowColumns = false,
}) => {
  const classes = useStyles();
  const { t } = useTranslation("common");

  const [expandedFeatures, setExpandedFeatures] = useState([]);

  const getIsExpanded = (feature) => {
    return expandedFeatures.includes(feature.name) || expandedFeatures.includes(feature.localId);
  };

  const handleExpandFeatures = (name) => {
    if (expandedFeatures.includes(name)) {
      setExpandedFeatures((val) => val.filter((el) => el !== name));
    } else {
      setExpandedFeatures((val) => [...val, name]);
    }
  };

  const handleShowFeatureDecscription = (name, description) => {
    if (description) {
      onShowInfo(name, description);
    }
  };

  const handleDeleteFeature = (localId, subtype) => {
    onDeleteFeature(localId, subtype);
  };

  const handleChangeParameters = (parent, paramName, value, localId, defaultValue) => {
    if (localId) {
      // only selected features have localId
      onChangeFeatureParams(localId, paramName, value, defaultValue);
    } else {
      // we pass name at de
      onChangeFeatureParams(parent, paramName, value, defaultValue);
    }
  };

  const getColumns = useCallback(
    (feature) => {
      return (
        getInputContractParameters(
          feature.inputContract.find((el) => el.name === "columns"),
          feature.localId,
        ) || []
      );
    },
    [featureList],
  );

  return (
    <>
      {featureList?.length &&
        featureList.map((feature, i) => (
          <Box
            ml={8}
            mb={1}
            pl={2}
            pr={2}
            key={`${feature.localId}-${i}`}
            className={classes.borderedFormWrapper}
          >
            <Box className={classes.collapseFormSummary}>
              <Box className={classes.wrapperCheckFeatureHeader}>
                {onSelectFeature ? (
                  <Checkbox
                    checked={feature.isSelected}
                    onChange={() => onSelectFeature(feature.name)}
                  />
                ) : null}
                <Typography
                  variant="subtitle1"
                  className={`${classes.featureFormSubtypeHeaderClicked}`}
                  onClick={() => handleExpandFeatures(feature.localId || feature.name)}
                >
                  {feature.name}{" "}
                </Typography>
              </Box>

              <Box className={classes.collapseFormSummaryIconsWrapper}>
                {!getIsExpanded(feature) ? (
                  <Box className={classes.columnsRow}>
                    {getColumns(feature).map((el, index) =>
                      index < MAX_COLUMNS_IN_PREVIEW ? (
                        <Chip key={`${feature.localId}-${el}`} label={el} size="small" />
                      ) : index === MAX_COLUMNS_IN_PREVIEW ? (
                        "..."
                      ) : null,
                    )}
                  </Box>
                ) : null}
                <Stack direction={"row"} alignItems={"flex-start"}>
                  <Tooltip
                    title={getIsExpanded(feature) ? t("tooltip-close") : t("tooltip-open")}
                    placement="top"
                  >
                    <IconButton
                      size="small"
                      onClick={() => handleExpandFeatures(feature.localId || feature.name)}
                    >
                      <EditOutlinedIcon classes={{ root: classes.editIcon }} />
                    </IconButton>
                  </Tooltip>

                  <Tooltip title={t("tooltip-info")} placement="top">
                    <IconButton
                      size="small"
                      onClick={() =>
                        handleShowFeatureDecscription(feature.name, feature.description)
                      }
                    >
                      <InfoOutlinedIcon classes={{ root: classes.infoIcon }} />
                    </IconButton>
                  </Tooltip>

                  {onDeleteFeature ? (
                    <Tooltip title={t("tooltip-delete")} placement="top">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteFeature(feature.localId, feature.subtype)}
                      >
                        <DeleteForeverOutlinedIcon classes={{ root: classes.deleteIcon }} />
                      </IconButton>
                    </Tooltip>
                  ) : null}
                </Stack>
              </Box>
            </Box>
            {getIsExpanded(feature) ? (
              <Box className={`${classes.formWrapper}`} mt={2}>
                {feature.inputContract.map((el) => (
                  <FormControl
                    key={`input_cntr_fc_${el?.name}_${el?.localId}`}
                    fullWidth={true}
                    className={classes.formControl}
                  >
                    <DynamicFormElement
                      id={`cntr_${el?.localId}`}
                      labelId={`cntr_lbl_${el?.localId}`}
                      name={el.name}
                      label={el.label}
                      defaultValue={getInputContractParameters(el, feature.localId)}
                      formType={el.type}
                      range={el.range}
                      options={el.options}
                      onChange={(name, value) => {
                        handleChangeParameters(
                          el.parent,
                          name,
                          value,
                          feature.localId,
                          getInputContractParameters(el, feature.localId),
                        );
                      }}
                    />
                  </FormControl>
                ))}
              </Box>
            ) : isShowColumns &&
              feature.inputContract.find((el) => el.name === "columns") ? null : null}
          </Box>
        ))}
    </>
  );
};

FormAutoMLFeaturesFormList.propTypes = {
  featureList: PropTypes.array,
  onShowInfo: PropTypes.func.isRequired,
  onChangeFeatureParams: PropTypes.func.isRequired,
};

FormAutoMLFeaturesFormList.defaultProps = {
  featureList: [],
};

export default FormAutoMLFeaturesFormList;
