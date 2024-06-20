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

import _ from "lodash";
import React, { useState, useEffect, useMemo } from "react";
import { Box, Skeleton } from "@mui/material";

import AddIcon from "@mui/icons-material/Add";

import { useTranslation } from "react-i18next";
import { PIPELINE_STEP_TYPES } from "store/autoML/const";
// eslint-disable-next-line max-len
import combineFeaturesToNumColumns from "store/containerBuildModel/domain/utilCombineFeaturesToNumColumns";

import UnfoldMoreOutlinedIcon from "@mui/icons-material/UnfoldMoreOutlined";
import UnfoldLessOutlinedIcon from "@mui/icons-material/UnfoldLessOutlined";

import { UIButtonConvertibleToShort } from "components/UIButtons";
import { useWindowResize } from "hooks";

import FormAutoMLFeaturesFormAdd from "./FormAutoMLFeaturesFormAdd";
import FormAutoMLFeaturesFormEdit from "./FormAutoMLFeaturesFormEdit";

import useStyles from "./FormStyle";

const WIDTH_FOR_SHORT_TEXT = 1650;

const FormAutoMLFeatureGenerator = ({
  inputData,
  onClose,
  onSubmit,
  onShowInfo,
  onChangeData,
  options = {},
}) => {
  const classes = useStyles();
  const { t } = useTranslation("models");

  const [isShortBtnText, setIsShortBtnText] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isShowCreateFrom, setIsShowCreateFrom] = useState(false);
  const [isChangedData, setIsChangedData] = useState(false);

  const [addedSubtypes, setAddedSubtypes] = useState([]);
  const [addedFeatures, setAddedFeatures] = useState([]);

  const [expandedSuptypes, setExpandedSuptypes] = useState([]);

  const groupedFeatures = useMemo(() => {
    return addedFeatures.reduce((acc, feature) => {
      if (!acc[feature.subtype]) {
        acc[feature.subtype] = [];
      }
      acc[feature.subtype].push(feature);
      return acc;
    }, {});
  }, [addedFeatures]);

  const handleShowCreateForm = (isShow) => {
    setIsShowCreateFrom(isShow);
  };

  const handleAddSelectedFeatures = (features, subtypes) => {
    /**
     * handleAddSelectedFeatures
     */
    const updatedFeatures = combineFeaturesToNumColumns(features);
    const featuresToAdd = _.concat(addedFeatures, updatedFeatures);
    setIsChangedData(true);

    setAddedFeatures(_.sortBy(featuresToAdd, ["name"]));
    setAddedSubtypes(_.union(addedSubtypes, subtypes));
    handleShowCreateForm(false);
  };

  const handleEditFormChangeParam = (localId, paramName, value, defaultValue) => {
    setIsChangedData(value !== defaultValue);
    setAddedFeatures((features) => {
      return features.map((feature) => {
        if (feature.localId === localId) {
          const params = feature.params || {};
          return { ...feature, params: { ...params, [paramName]: value } };
        }
        return feature;
      });
    });
  };

  const handleSetDefaultData = () => {
    setAddedFeatures(inputData?.defaultFeatureList);
    setAddedSubtypes(inputData?.addedSubtypes);
  };

  const handleExpandSubtypes = () => {
    setExpandedSuptypes(inputData.subtypes);
  };

  const handleCollapseSubtypes = () => {
    setExpandedSuptypes([]);
  };

  const handleExpandSubtype = (subtype) => {
    if (expandedSuptypes.includes(subtype)) {
      setExpandedSuptypes((val) => _.filter(val, (el) => el !== subtype));
    } else {
      setExpandedSuptypes((val) => [...val, subtype]);
    }
  };

  const handleDeleteFeature = (localId, subtype) => {
    // if last feature delete subtype
    if (addedFeatures.filter((feature) => feature.subtype === subtype)?.length === 1) {
      setAddedSubtypes(addedSubtypes.filter((_subtype) => _subtype !== subtype));
    }
    setAddedFeatures(addedFeatures.filter((feature) => feature.localId !== localId));
  };

  const handleDeleteSubtype = (subtype) => {
    setAddedSubtypes(addedSubtypes.filter((_subtype) => _subtype !== subtype));
    setAddedFeatures(addedFeatures.filter((feature) => feature.subtype !== subtype));
  };

  const handleSubmit = () => {
    const features = addedFeatures.map((feature) => {
      return {
        name: feature.name,
        params: feature.params,
        isSelected: feature.isSelected,
      };
    });

    onSubmit({ data: features, customName: PIPELINE_STEP_TYPES.FEATURE_GENERATOR });
  };

  useEffect(() => {
    setTimeout(() => setLoading(false), 100);
    handleSetDefaultData();
    if (_.isEmpty(inputData?.defaultFeatureList)) {
      setIsShowCreateFrom(true);
    }
  }, []);

  useEffect(() => {
    if (!_.isEmpty(addedFeatures)) {
      handleExpandSubtypes();
      const features = addedFeatures.map((feature) => {
        return {
          name: feature.name,
          params: feature.params,
          isSelected: feature.isSelected,
        };
      });
      onChangeData(isChangedData, features);
    }
  }, [addedFeatures]);

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < WIDTH_FOR_SHORT_TEXT);
  });

  return (
    <Box>
      <Box className={classes.addButtonWrapper}>
        {!isShowCreateFrom ? (
          <UIButtonConvertibleToShort
            icon={<AddIcon />}
            isShort={isShortBtnText}
            tooltip={t("model-builder.drawer-edit-step-fg-btn-open-adding-tooltip")}
            text={t("model-builder.drawer-edit-step-fg-btn-open-adding")}
            color="primary"
            variant={"outlined"}
            onClick={() => handleShowCreateForm(true)}
          />
        ) : null}
        {!isShowCreateFrom ? (
          <>
            <UIButtonConvertibleToShort
              icon={<UnfoldMoreOutlinedIcon />}
              isShort={isShortBtnText}
              tooltip={t("model-builder.drawer-edit-step-fg-btn-expand-subtypes-tooltip")}
              text={t("model-builder.drawer-edit-step-fg-btn-expand-subtypes")}
              color="primary"
              variant={"outlined"}
              onClick={handleExpandSubtypes}
            />
            <UIButtonConvertibleToShort
              icon={<UnfoldLessOutlinedIcon />}
              isShort={isShortBtnText}
              tooltip={t("model-builder.drawer-edit-step-fg-btn-collapse-subtypes-tooltip")}
              text={t("model-builder.drawer-edit-step-fg-btn-collapse-subtypes")}
              color="primary"
              variant={"outlined"}
              onClick={handleCollapseSubtypes}
            />
          </>
        ) : null}
      </Box>
      {isShowCreateFrom ? (
        <FormAutoMLFeaturesFormAdd
          inputData={inputData}
          queryColumns={options.queryColumns}
          onShowInfo={onShowInfo}
          onAdd={handleAddSelectedFeatures}
          onClose={() => handleShowCreateForm(false)}
        />
      ) : loading ? (
        [1, 2, 3, 4].map((key) => (
          <Box key={`skeleton-${key}`}>
            <Skeleton width={"50%"} height={"2rem"} />
            <Box ml={"4rem"}>
              <Skeleton height={"5rem"} />
            </Box>
            <Box ml={"4rem"}>
              <Skeleton height={"5rem"} />
            </Box>
            <Box ml={"4rem"}>
              <Skeleton height={"5rem"} />
            </Box>
          </Box>
        ))
      ) : (
        <FormAutoMLFeaturesFormEdit
          groupedFeatures={groupedFeatures}
          selectedFeatures={addedFeatures}
          expandedSuptypes={expandedSuptypes}
          subtypes={addedSubtypes}
          onExpandSubtype={handleExpandSubtype}
          onShowInfo={onShowInfo}
          onSave={handleSubmit}
          onClose={onClose}
          onChangeParam={handleEditFormChangeParam}
          onDeleteFeature={handleDeleteFeature}
          onDeleteSubtype={handleDeleteSubtype}
          onSetDefaultData={handleSetDefaultData}
        />
      )}
    </Box>
  );
};

export default FormAutoMLFeatureGenerator;
