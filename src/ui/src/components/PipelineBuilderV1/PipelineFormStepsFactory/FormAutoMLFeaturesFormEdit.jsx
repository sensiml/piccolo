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

import React from "react";
import _ from "lodash";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import KeyboardArrowDownOutlinedIcon from "@mui/icons-material/KeyboardArrowDownOutlined";
import KeyboardArrowUpOutlinedIcon from "@mui/icons-material/KeyboardArrowUpOutlined";
import UndoOutlinedIcon from "@mui/icons-material/UndoOutlined";

import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";

import { Box, Button, Tooltip, Typography, IconButton } from "@mui/material";

import FormAutoMLFeaturesFormList from "./FormAutoMLFeaturesFormList";
import useStyles from "./FormStyle";

const FormAutoMLFeaturesFormEdit = ({
  groupedFeatures,
  selectedFeatures,
  expandedSuptypes,
  subtypes,
  onSetDefaultData,
  onDeleteFeature,
  onDeleteSubtype,
  onExpandSubtype,
  onShowInfo,
  onClose,
  onSave,
  onChangeParam,
}) => {
  const { t } = useTranslation("models");
  const classes = useStyles();

  const getInputContractParameters = (el, localId) => {
    const feature = _.find(selectedFeatures, (fg) => fg.localId === localId);
    return feature.params[el.name];
  };

  const handleExpandSubtype = (subtype) => {
    onExpandSubtype(subtype);
  };

  return (
    <>
      <Box className={classes.subtypesWrapper}>
        {subtypes.map((subtype, index) => (
          <Box className={classes.subtypesWrap} key={`feature_${index}`}>
            <Box className={classes.featureFormSubtypeHeader}>
              <Box className={classes.wrapperCheckHeader}>
                <Tooltip
                  title={
                    expandedSuptypes.includes(subtype) ? t("tooltip-close") : t("tooltip-open")
                  }
                  placement="top"
                >
                  <IconButton onClick={() => handleExpandSubtype(subtype)}>
                    {expandedSuptypes.includes(subtype) ? (
                      <KeyboardArrowDownOutlinedIcon color="primary" />
                    ) : (
                      <KeyboardArrowUpOutlinedIcon color="primary" />
                    )}
                  </IconButton>
                </Tooltip>
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
                <Tooltip title={t("tooltip-delete")} placement="top">
                  <IconButton size="small" onClick={() => onDeleteSubtype(subtype)}>
                    <DeleteForeverOutlinedIcon classes={{ root: classes.deleteIcon }} />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
            {expandedSuptypes.includes(subtype) ? (
              <FormAutoMLFeaturesFormList
                onShowInfo={onShowInfo}
                subtype={subtype}
                featureList={groupedFeatures[subtype] || []}
                getInputContractParameters={getInputContractParameters}
                onChangeFeatureParams={onChangeParam}
                onDeleteFeature={onDeleteFeature}
                isShowColumns={true}
              />
            ) : null}
          </Box>
        ))}
      </Box>
      <Box className={classes.drawerFormButtonWrapper}>
        <Button
          className={`${classes.drawerFormButton} ${classes.mr2}`}
          size="large"
          startIcon={<UndoOutlinedIcon />}
          color="primary"
          onClick={onSetDefaultData}
          variant="outlined"
        >
          {t("model-builder.drawer-edit-step-fg-btn-discard")}
        </Button>
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
          onClick={onSave}
          data-testid="edit-step-form-submit"
          className={classes.drawerFormButton}
          size="large"
          variant="contained"
          color="primary"
        >
          {t("model-builder.drawer-edit-step-btn-add")}
        </Button>
      </Box>
    </>
  );
};

FormAutoMLFeaturesFormEdit.propTypes = {
  selectedFeatures: PropTypes.array,
  subtypes: PropTypes.array,
  onShowInfo: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

FormAutoMLFeaturesFormEdit.defaultProps = {
  selectedFeatures: [],
  subtypes: [],
};

export default FormAutoMLFeaturesFormEdit;
