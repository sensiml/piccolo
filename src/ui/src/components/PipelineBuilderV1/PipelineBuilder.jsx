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
import React, { useState, useCallback, useRef, useEffect, useMemo } from "react";

import { useTranslation } from "react-i18next";
import {
  Button,
  Box,
  CircularProgress,
  Typography,
  Link,
  Tooltip,
  FormControlLabel,
  Checkbox,
  Stack,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";

import PanoramaFishEyeOutlinedIcon from "@mui/icons-material/PanoramaFishEyeOutlined";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import DoneAllOutlinedIcon from "@mui/icons-material/DoneAllOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

import { filterTruncate } from "filters";
import { useMainContext } from "hooks";
import { DialogConfirm } from "components/DialogConfirm";
import DialogInformation from "components/DialogInformation";
import UIDialogForm from "components/UIDialogFormMedium";
import PipelineStepDrawerStatistic from "components/PipelineStepDrawerStatistic";

import api, { parseApiError } from "store/api";
import fileDownload from "js-file-download";

import {
  CardStep,
  NewCardStep,
  IconArrowAddWrap,
  IconArrowWrap,
  IconArrowFullWidthWrap,
} from "components/FlowBuilder";
import {
  PARENT_KEY,
  PIPELINE_STEP_TYPES,
  AUTOML_PARAMS_NAME,
  PIPELINE_GROUPS,
} from "store/autoML/const";
import DrawerNewStep from "./DrawerNewStep";
import DrawerEditStep from "./DrawerEditStep";
import DrawerInformationMessage from "./DrawerInformationMessage";
import DraweInformationStep from "./DrawerInformationStep";
import FormPipelineStep from "./PipelineFormStepsFactory";
import FormStepEditor from "./FormStepEditor";
import PipelineBuilderSkeleton from "./PipelineBuilderSkeleton";

import useStyles from "./BuildModeStyle";

const STEP_COLORS = {
  Query: "rgba(255,210,21,0.7)",
  Segmenter: "#3EC15C",
  Augmentation: "#ffbc58",
  "Feature Generator": "#0071c5",
  "Feature Selector": "#ff937e",
  Transform: "#3EC15C",
  Sampler: "#5290E9",
  Optimizer: "#0071c5",
  Classifier: "rgba(35,113,185,1)",
  "Validation Method": "#0071c5",
  "Training Algorithm": "#0071c5",
  AUTOML_PARAMS: "rgba(130, 130, 129,0.7)",
  MODEL_SETTINGS: "rgba(35,113,185,1)",
  DEFAULT: "rgba(0,160,198,1.0)",
};

const CircularProgressWithLabel = ({ current, total, ...props }) => {
  const { t } = useTranslation("models");
  return (
    <Box sx={{ position: "relative", display: "inline-flex" }}>
      <CircularProgress variant="determinate" {...props} />

      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: "absolute",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Tooltip title={t("pipeline-builder.executing-automl-step")}>
          <Typography
            variant="caption"
            component="div"
            color="text.secondary"
            style={{ fontSize: "0.75rem" }}
          >
            {`${current}/${total}`}
          </Typography>
        </Tooltip>
      </Box>
    </Box>
  );
};

let downloadingCache = false;

const PipelineBuilder = ({
  isAutoML,
  isModel,
  alertBuilder,
  pipelineSettings,
  selectedSteps,
  allSteps,
  transforms,
  isOptimizationRunning,
  pipelineStatus,
  pipelineUUID,
  pipelineData,
  projectUUID,
  getPipelineStepDataClass,
  getPipelineStepDescription,
  getPipelineStepFeatureStats,
  labelColors,
  classMap,
  selectLabelValuesColors,
  onCloseAlertBuilder,
  onCreateNewStep,
  onDeleteStep,
  onEditStep,
  onEditPipelineSettings,
}) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const { showMessageSnackbar } = useMainContext();
  const abortControllerRef = useRef();
  const theme = useTheme();

  const [activeInfoStep, setActiveInfoStep] = useState({ index: -1 });
  const [activeEditStep, setActiveEditStep] = useState({ index: -1 });
  const [activeEditStepData, setActiveEditStepData] = useState({});
  const [newStepAfter, setNewStepAfter] = useState({ index: -1 }); // need for sequense check
  const [newStepData, setNewStepData] = useState({});
  const [deleteStepData, setDeleteStepData] = useState({});
  const [newStepDialogInformation, setNewStepDialogInformation] = useState({});
  const [editStepDialogInformation, setEditStepDialogInformation] = useState({});
  const [cardParams, setCardParams] = useState({});

  const [selectedStepCacheItems, setSelectedStepCacheItems] = useState([]);
  const [stepCacheItemsToSelect, setStepCacheItemsToSelect] = useState({});
  const [downloadedCacheItems, setDownloadedCacheItems] = useState([]);
  const [isDownloadingCache, setIsDownloadingCache] = useState(false);

  const [cacheDistributionData, setCacheDistributionData] = useState({});
  const [featureStatsData, setFeatureStatsData] = useState({});

  const [isOpenCacheDownloadMenu, setIsOpenCacheDownloadMenu] = useState(false);
  const [isOpenDialogDistribution, setIsOpenDialogDistribution] = useState(false);
  const [isPipelineHasUnsavedUpdate, setIsPipelineHasUnsavedUpdate] = useState(false);
  const [isShowUnsavedAlertDialog, setIsShowUnsavedAlertDialog] = useState(false);
  const [isEditModeJson, setIsEditModeJson] = useState(false);
  const [editFormKeyId, setEditFormKeyId] = useState(_.uniqueId());

  const getStepColor = useCallback(
    (_type) => {
      switch (_type) {
        case PIPELINE_STEP_TYPES.AUTOML_PARAMS:
          return STEP_COLORS.AUTOML_PARAMS;
        case PIPELINE_STEP_TYPES.QUERY:
          return STEP_COLORS.DEFAULT;
        case PIPELINE_STEP_TYPES.CLASSIFIER:
          return STEP_COLORS.DEFAULT;
        case PIPELINE_STEP_TYPES.TRAINING_ALGORITHM:
          return STEP_COLORS.DEFAULT;
        case PIPELINE_STEP_TYPES.VALIDATION:
          return STEP_COLORS.DEFAULT;
        case PIPELINE_STEP_TYPES.MODEL_SETTINGS:
          return STEP_COLORS.MODEL_SETTINGS;
        default:
          return STEP_COLORS.DEFAULT;
      }
    },
    [selectedSteps],
  );

  useEffect(() => {
    abortControllerRef.current = new AbortController();
  }, []);

  const getStepStyle = useCallback(
    (_type) => {
      const borderColor = getStepColor(_type);
      const style = { borderColor };
      switch (_type) {
        case PIPELINE_STEP_TYPES.CLASSIFIER:
          style.borderBottom = `4px solid ${borderColor}`;
          break;
        case PIPELINE_STEP_TYPES.TRAINING_ALGORITHM:
          style.borderBottom = `4px solid ${borderColor}`;
          break;
        case PIPELINE_STEP_TYPES.VALIDATION:
          style.borderBottom = `4px solid ${borderColor}`;

          break;
        case PIPELINE_STEP_TYPES.MODEL_SETTINGS:
          break;
        default:
          style.borderBottom = `4px solid ${borderColor}`;
      }
      return style;
    },
    [selectedSteps],
  );

  const getCardIsDisableToEdit = useCallback(
    (step) => {
      if (step?.type === PIPELINE_STEP_TYPES.AUTOML_PARAMS) {
        return false;
      }
      if (step?.options?.isSession && step?.type !== PIPELINE_STEP_TYPES.INPUT_DATA) {
        return true;
      }
      if (step?.options?.isOptimizedByAutoML) {
        return true;
      }

      return isOptimizationRunning;
    },
    [selectedSteps, pipelineSettings, isOptimizationRunning],
  );

  const getAvailableNextSteps = (index, stepObj) => {
    let nextAvailableSteps = [];
    if (!selectedSteps?.length) {
      return [];
    }
    if (stepObj?.nextSteps?.includes(PARENT_KEY)) {
      let i = index;
      let nextParentSteps = selectedSteps[i]?.nextSteps;
      while (nextParentSteps?.includes(PARENT_KEY) && --i >= 0) {
        nextParentSteps = selectedSteps[i]?.nextSteps;
      }
      if (!selectedSteps[i]?.nextSteps?.includes(PARENT_KEY)) {
        nextAvailableSteps = nextParentSteps;
      }
    } else if (stepObj?.nextSteps) {
      nextAvailableSteps = [...stepObj?.nextSteps];
    }
    // nextAvailableSteps
    if (!nextAvailableSteps) {
      return [];
    }
    const filteredSteps = nextAvailableSteps.filter((stepName) => {
      const st = selectedSteps?.filter((stFilted) => stFilted.name === stepName);
      const allStep = allSteps?.find((stFilted) => stFilted.name === stepName);
      // check mandatory
      if (allStep?.mandatory && allStep.type !== PIPELINE_STEP_TYPES.SEGMENTER) {
        return false;
      }
      if (st?.length) {
        // check limit
        if (st[0]?.limit === null) {
          return true;
        }
        if (st[0].limit <= st.length) {
          return false;
        }
      }
      return true;
    });
    return filteredSteps.filter((stepName) => allSteps.find((step) => step.name === stepName));
  };

  const inputDataByTypeSubType = useMemo(() => {
    if (!_.isEmpty(activeEditStep)) {
      const { type, subtype, transformList, excludeTransform, id } = activeEditStep;
      const dataClass = getPipelineStepDataClass({
        type,
        subtype,
        id,
        isAutoML,
        selectedSteps: [activeEditStep],
      });
      return {
        inputData: dataClass.getInputsData({ transformList, excludeTransform }),
        queryColumns: dataClass.queryColumns,
      };
    }
    return {};
  }, [activeEditStep]);

  const activeEditStepOptions = useMemo(() => {
    if (!_.isEmpty(activeEditStep?.options)) {
      return { ...activeEditStep?.options, queryColumns: inputDataByTypeSubType.queryColumns };
    }
    return activeEditStep?.options;
  }, [activeEditStep, inputDataByTypeSubType]);

  const getInputCardParamsByTypeSubType = (id) => {
    return cardParams[id] || [];
  };

  const getQueriesDescriptionParameters = (queryInputData) => {
    // extract descriptionParameters
    const { descriptionParameters: res = [] } =
      queryInputData?.find((el) => el.descriptionParameters?.length) || {};
    return res;
  };

  useEffect(() => {
    // each time when selectedSteps updating looking for is_should_be_reviewed
    if (selectedSteps?.length) {
      const reviwedStep = selectedSteps.find((step) => step?.options?.is_should_be_reviewed);
      if (reviwedStep) {
        setActiveEditStep(reviwedStep);
      }
      const cardParamObj = selectedSteps.reduce((acc, { type, subtype, id }) => {
        acc[id] = getPipelineStepDataClass({
          type,
          subtype,
          id,
          isAutoML,
          selectedSteps,
        }).getCardParams();
        return acc;
      }, {});
      setCardParams(cardParamObj);
    }
  }, [selectedSteps]);

  const nextStepsIsNotNone = (nextSteps) => {
    return nextSteps && nextSteps[0] !== "None" && nextSteps[0];
  };

  const isNextStepIsSessionPreprocessed = (currentIndex) => {
    if (selectedSteps[currentIndex + 1]) {
      return selectedSteps[currentIndex + 1]?.options?.isSessionPreprocess;
    }
    return false;
  };

  const isNextStepAvailableToAdd = (currentIndex, stepObj) => {
    // if next step options contain the next step and is pipeline in not running
    return (
      !isNextStepIsSessionPreprocessed(currentIndex) &&
      Boolean(getAvailableNextSteps(currentIndex, stepObj)?.length) &&
      !isOptimizationRunning
    );
  };

  const isStepAvailableToEdit = (currentIndex) => {
    // if prev step obj has data
    let isAvailable = true;
    if (
      currentIndex > 0 &&
      selectedSteps[currentIndex]?.type !== PIPELINE_STEP_TYPES.AUTOML_PARAMS
    ) {
      let index;
      for (index = 0; index < currentIndex; ++index) {
        if (!selectedSteps[index]?.data) {
          isAvailable = false;
        }
      }
    }
    return isAvailable;
  };

  const isFormOptionsDisabled = () => {
    return (
      activeEditStep?.options?.isSessionPreprocess || activeEditStep?.options?.isSessionSegmenter
    );
  };

  const isStepAvailableToDeleteForm = (step) => {
    return !step.mandatory && !step?.options?.isSession && !isOptimizationRunning;
  };

  const handleNewStep = (index, stepObj) => {
    const filteredStepObj = { ...stepObj };
    filteredStepObj.nextSteps = getAvailableNextSteps(index, stepObj);
    setNewStepAfter({ ...filteredStepObj, index });
  };

  const handleCloseNewStep = () => {
    setNewStepAfter({ index: -1 });
    setNewStepData({});
  };

  const handleNewStepChange = (stepObj) => {
    setNewStepData(stepObj);
  };

  const handleCreateNewStep = () => {
    const id = onCreateNewStep(newStepAfter.index + 1, newStepData);
    setNewStepAfter({ index: -1 });
    setActiveEditStep({ index: newStepAfter.index + 1, ...newStepData, id });
  };

  const handleDeleteStep = (index, deletedStepData) => {
    setDeleteStepData({ ...deletedStepData, index });
  };

  const handleDeleteStepCancel = () => {
    setDeleteStepData({});
  };

  const handleDeleteStepConfirm = () => {
    onDeleteStep(deleteStepData);
    setDeleteStepData({});
  };

  const handleShowNewStepInformation = (name) => {
    const { descpription, docLink } = getPipelineStepDescription(name);
    setNewStepDialogInformation({ title: name, descpription, docLink });
  };

  const handleCloseNewStepDialogInformation = () => {
    setNewStepDialogInformation({});
  };

  const handleEditStepInformation = (title, descpription) => {
    setEditStepDialogInformation({ title, descpription });
  };

  const handleCloseEditStepDialogInformation = () => {
    setEditStepDialogInformation({});
  };

  const handleStepInfo = (stepObj) => {
    const { descpription, docLink } = getPipelineStepDescription(stepObj.name);
    const { type, subtype, transformList, excludeTransform, id } = stepObj;

    const transformObj =
      _.find(transforms, (trnsf) => trnsf.name === stepObj?.data?.transform) || {};
    const { QUERY, FEATURE_GENERATOR, FEATURE_SELECTOR } = PIPELINE_STEP_TYPES;

    const extracDescriptionParametersForQuery = () => {
      const queryInputData = getPipelineStepDataClass({
        type,
        subtype,
        id,
        isAutoML,
        selectedSteps,
      }).getInputsData({ transformList, excludeTransform });
      const queryParams = getQueriesDescriptionParameters(queryInputData);
      return queryParams.find((paramsObj) => paramsObj.name === stepObj.customName) || {};
    };

    let dataParams = [];

    if (![QUERY, FEATURE_GENERATOR, FEATURE_SELECTOR].includes(stepObj.type)) {
      dataParams = stepObj.data;
    }

    let descriptionParameters = {};

    if ([QUERY].includes(stepObj.type)) {
      // for the step query descriptionParameters may be updated
      descriptionParameters = extracDescriptionParametersForQuery();
    }

    setActiveInfoStep({
      isOpen: true,
      ...stepObj,
      options: { descriptionParameters },
      descpription,
      transformName: stepObj?.data?.transform,
      transformDescription: transformObj.description,
      dataParams,
      docLink,
    });
  };

  const handleCloseStepInfo = () => {
    setActiveInfoStep({});
  };

  const handleOpenStepEdit = (index, stepObj) => {
    setActiveEditStep({});
    setActiveEditStep({ ...stepObj, index });
  };

  const handleCloseStepEdit = () => {
    if (isPipelineHasUnsavedUpdate) {
      setIsShowUnsavedAlertDialog(true);
    } else {
      setIsEditModeJson(false);
      setActiveEditStep({});
    }
  };

  const handleStepEditChangeView = () => {
    /**
     * handle change view mode for edit step form
     * to tranfer data between form and editor we set edited data to setActiveEditStep
     */
    setEditFormKeyId(_.uniqueId());
    setIsEditModeJson(!isEditModeJson);
    if (isPipelineHasUnsavedUpdate) {
      setActiveEditStep((prevData) => ({ ...prevData, data: activeEditStepData }));
    }
  };

  const handleUpdatePipelineStep = (isChanged, updatedData, isResetData, name) => {
    if (!isPipelineHasUnsavedUpdate && isChanged) {
      setIsPipelineHasUnsavedUpdate(isChanged);
    }
    if (isChanged) {
      if (_.isArray(updatedData)) {
        setActiveEditStepData(updatedData);
      } else if (isResetData) {
        setActiveEditStepData({ ...updatedData });
      } else {
        const data = activeEditStep.data || {};
        if (_.includes(name, "is_use_") && updatedData[name] === false) {
          // remove parent data of is_use_ field
          const parentName = _.replace(name, "is_use_", "");
          data[parentName] = undefined;
        }
        setActiveEditStepData((prevData) => ({ ...data, ...prevData, ...updatedData }));
      }
    }
  };

  const handleStepEditSubmit = ({ data, customName, options, type }) => {
    if (type === PIPELINE_STEP_TYPES.AUTOML_PARAMS) {
      onEditPipelineSettings({ ...activeEditStep, data, customName, options });
    } else {
      onEditStep({ ...activeEditStep, data, customName, options });
    }
    setIsPipelineHasUnsavedUpdate(false);

    setIsEditModeJson(false);
    setActiveEditStep({});
  };

  const handleUnsavedStepBack = () => {
    setIsEditModeJson(false);
    setIsShowUnsavedAlertDialog(false);
  };

  const handleUnsavedStepSkip = () => {
    setIsPipelineHasUnsavedUpdate(false);
    setIsEditModeJson(false);
    setIsShowUnsavedAlertDialog(false);
    setActiveEditStepData({});
    setActiveEditStep({});
  };

  const handleUnsavedStepSave = () => {
    setIsPipelineHasUnsavedUpdate(false);
    handleStepEditSubmit({
      data: activeEditStepData,
      customName: activeEditStepData?.transform || activeEditStep?.customName,
    });
    setIsEditModeJson(false);
    setIsShowUnsavedAlertDialog(false);
    setActiveEditStepData({});
    setActiveEditStep({});
  };

  const handleOpenDownloadCacheMenu = (e, step) => {
    setIsOpenCacheDownloadMenu(true);

    setSelectedStepCacheItems(_.keys(step?.options?.cacheData));
    setStepCacheItemsToSelect(step?.options?.cacheData);
  };

  const handleCancelDownloadCache = () => {
    if (isDownloadingCache) {
      downloadingCache = false;
      abortControllerRef.current.abort();
      setIsDownloadingCache(false);
      setDownloadedCacheItems([]);
    }
    setIsOpenCacheDownloadMenu(false);
    setSelectedStepCacheItems([]);
    setStepCacheItemsToSelect({});
  };

  const handleCloseDownloadCacheMenu = () => {
    if (!isDownloadingCache) {
      setIsOpenCacheDownloadMenu(false);
      setIsDownloadingCache(false);
      setDownloadedCacheItems([]);
      setSelectedStepCacheItems([]);
      setStepCacheItemsToSelect({});
    }
  };

  const handleSelectChacheToDownload = (itemName) => {
    if (!selectedStepCacheItems.includes(itemName)) {
      setSelectedStepCacheItems((preVal) => {
        return [...preVal, itemName];
      });
    } else {
      setSelectedStepCacheItems((preVal) => {
        return preVal.filter((name) => name !== itemName);
      });
    }
  };

  const handleSubmitDownloadCache = async () => {
    downloadingCache = true;
    setIsDownloadingCache(true);

    // eslint-disable-next-line no-restricted-syntax
    for (const itemName of selectedStepCacheItems) {
      const { indexStep, indexPage, stepName } = stepCacheItemsToSelect[itemName];
      if (!downloadingCache) {
        // stop downloading if user close menu
        break;
      }
      try {
        // eslint-disable-next-line no-await-in-loop
        const { data } = await api.get(`/project/${projectUUID}/sandbox/${pipelineUUID}/data/`, {
          signal: abortControllerRef.current.signal,
          params: { pipeline_step: indexStep, page_index: indexPage },
        });

        setDownloadedCacheItems((preVal) => {
          return [...preVal, `${indexStep}_${indexPage}`];
        });

        if (data?.results && downloadingCache) {
          // remove all extension
          fileDownload(
            JSON.stringify(data.results),
            `${pipelineData?.name}.${stepName}.cache.${indexPage}.json`,
          );
        }
      } catch (error) {
        const apiError = parseApiError(error, "ds");
        showMessageSnackbar("error", apiError.message);
      }
    }

    handleCloseDownloadCacheMenu();
  };

  const handleOpenDialogDistributionChart = async (_e, _step) => {
    setIsOpenDialogDistribution(true);
    setCacheDistributionData({
      data: _step?.options?.cacheData,
      step: {
        isLoadFeatures: _step.options.isAfterFeatureGenerator,
        stepName: _step.name,
      },
    });
    if (_step.options.isAfterFeatureGenerator) {
      try {
        const data = await getPipelineStepFeatureStats(projectUUID, pipelineUUID, _step.index);
        setFeatureStatsData(data);
      } catch (apiError) {
        showMessageSnackbar("error", apiError.message);
      }
    }
  };

  const handleCloseDialogDistributionChart = (_e, _step) => {
    setIsOpenDialogDistribution(false);
    setCacheDistributionData({});
    setFeatureStatsData({});
  };

  const getStatuStepIndex = (_step_index) => {
    // server has logic step_index + 1
    return _step_index - 1;
  };

  const componentCardIcon = useCallback(
    (step, groupItem) => {
      if (
        pipelineStatus?.step_name === "tvo" &&
        pipelineStatus?.step_name === groupItem.type &&
        pipelineStatus.status === "FAILURE"
      ) {
        return (
          <Tooltip title={t("pipeline-builder.step-failed")}>
            <CancelOutlinedIcon style={{ color: "red" }} />
          </Tooltip>
        );
      }
      if (
        step.index === getStatuStepIndex(pipelineStatus?.step_index) &&
        pipelineStatus.status === "FAILURE"
      ) {
        return (
          <Tooltip title={t("pipeline-builder.step-failed")}>
            <CancelOutlinedIcon style={{ color: "red" }} />
          </Tooltip>
        );
      }

      if (!isOptimizationRunning) {
        // if not running read cache
        if (step?.options?.isCached && step?.options?.type !== PIPELINE_GROUPS.TVO.type) {
          return (
            <Tooltip title={t("pipeline-builder.cached-step")}>
              <CheckCircleIcon style={{ color: "rgb(112, 206, 128)" }} />
            </Tooltip>
          );
        }
        if (pipelineStatus?.status === "SUCCESS") {
          return (
            <Tooltip title={t("pipeline-builder.automl-completed-step")}>
              <CheckCircleOutlineIcon style={{ color: "rgb(112, 206, 128)" }} />
            </Tooltip>
          );
        }
      } else {
        if (
          pipelineStatus?.step_name === PIPELINE_GROUPS.TVO.type &&
          pipelineStatus?.step_name === groupItem.type
        ) {
          return (
            <Tooltip title={t("pipeline-builder.executing-step")}>
              <CircularProgress size={"1.5rem"} color="primary" />
            </Tooltip>
          );
        }
        if (
          pipelineStatus?.step_name !== PIPELINE_GROUPS.TVO.type &&
          step.index === getStatuStepIndex(pipelineStatus?.step_index)
        ) {
          return (
            <Tooltip title={t("pipeline-builder.executing-step")}>
              <CircularProgress size={"1.5rem"} color="primary" />
            </Tooltip>
          );
        }
        if (step.index < getStatuStepIndex(pipelineStatus?.step_index)) {
          if (
            pipelineStatus?.iteration !== "RCL" &&
            !_.isUndefined(pipelineStatus?.iteration_start_index) &&
            step?.index >= getStatuStepIndex(pipelineStatus?.iteration_start_index)
          ) {
            return (
              <CircularProgressWithLabel
                size={"2rem"}
                color="primary"
                variant="determinate"
                value={_.divide(pipelineStatus.iteration, pipelineStatus?.total_iterations) * 100}
                current={pipelineStatus.iteration}
                total={pipelineStatus.total_iterations}
              />
            );
          }
          if (
            _.isUndefined(pipelineStatus?.iteration_start_index) ||
            step.index < getStatuStepIndex(pipelineStatus?.iteration_start_index)
          ) {
            return (
              <Tooltip title={t("pipeline-builder.cached-step")}>
                <CheckCircleIcon style={{ color: "rgb(112, 206, 128)" }} />
              </Tooltip>
            );
          }
          return (
            <Tooltip title={t("pipeline-builder.automl-completed-step")}>
              <CheckCircleOutlineIcon style={{ color: "rgb(112, 206, 128)" }} />
            </Tooltip>
          );
        }
      }
      return (
        <Tooltip title={t("pipeline-builder.non-run-step")}>
          <PanoramaFishEyeOutlinedIcon style={{ color: "silver" }} />
        </Tooltip>
      );
    },
    [selectedSteps, activeEditStep, pipelineStatus, isOptimizationRunning],
  );

  const CardInformationIcon = ({ step }) => (
    <Tooltip title={t("flow-builder.card-step-help-info")} placement="top">
      <Link
        className={`${classes.cardInfoIcon}`}
        onClick={(_e) => handleStepInfo(step)}
        data-test="info-link"
      >
        <InfoOutlinedIcon style={{ color: theme.colorEditIcons }} fontSize="xsmall" />
      </Link>
    </Tooltip>
  );

  return (
    <Box data-test={"ppl-step-builder"} className={classes.pipelineBuilderWrapper}>
      {isAutoML ? (
        <CardStep
          dataTest="ppl-card-step"
          className={getCardIsDisableToEdit(pipelineSettings) ? classes.cardStepDisabledToEdit : ""}
          disable={!isStepAvailableToEdit(pipelineSettings)}
          style={{
            margin: "auto",
            marginBottom: "1rem",
            borderBottom: `4px solid ${STEP_COLORS.AUTOML_PARAMS}`,
          }}
          onInfo={(_e) => handleStepInfo(pipelineSettings)}
          onEdit={(_e) => setActiveEditStep(pipelineSettings)}
        >
          <Box className={classes.cardTextWrap}>
            <span>{"AutoML Settings"}</span>
            <Box className={classes.cardParamsWrapper}>
              {getInputCardParamsByTypeSubType(pipelineSettings.id).map((el, ind) => (
                <Tooltip key={`${el.name}_${ind}`} title={el?.tooltip}>
                  <Box className={`${classes.cardParamsWrap}`}>
                    <span>{el.label}</span>
                    <span>{el.value}</span>
                  </Box>
                </Tooltip>
              ))}
            </Box>
          </Box>
        </CardStep>
      ) : null}
      {_.entries(PIPELINE_GROUPS)
        .filter((el) => (el[1].type !== PIPELINE_GROUPS.TVO.type && !isModel) || isModel)
        .map(([_groupKey, groupItem]) => {
          const stepsToRender = selectedSteps.filter(
            (_el) => groupItem.type === _el?.options?.type,
          );
          return (
            <Box key={`group_${groupItem.type}`}>
              <Box className={classes.groupBox}>
                <div className={classes.groupHeader}>{groupItem.name}</div>
                {_.isEmpty(stepsToRender) ? (
                  <PipelineBuilderSkeleton isShow={!selectedSteps?.length} amount={2} />
                ) : (
                  stepsToRender.map((step) => (
                    <Box
                      className={classes.stepWrapper}
                      key={`step_${groupItem.type}_${step.name}${step.index}`}
                      data-test={"ppl-step-wapper"}
                      data-cy={step.name}
                    >
                      <CardStep
                        dataTest="ppl-card-step"
                        className={
                          getCardIsDisableToEdit(step) ? classes.cardStepDisabledToEdit : ""
                        }
                        icon={componentCardIcon(step, groupItem)}
                        disable={!isStepAvailableToEdit(step.index)}
                        isFlashingEdit={isStepAvailableToEdit(step.index) && !step?.data}
                        style={getStepStyle(step.type)}
                        onInfo={(_e) => handleStepInfo(step)}
                        onEdit={
                          !getCardIsDisableToEdit(step)
                            ? (_e) => handleOpenStepEdit(step.index, step)
                            : undefined
                        }
                        onDelete={
                          isStepAvailableToDeleteForm(step)
                            ? (_e) => handleDeleteStep(step.index, step)
                            : undefined
                        }
                        onDownloadCache={
                          !isOptimizationRunning && step?.options?.isCached
                            ? (e) => handleOpenDownloadCacheMenu(e, step)
                            : null
                        }
                        onOpenCacheChart={
                          !isOptimizationRunning && step?.options?.isHasDistributionData
                            ? (e) => handleOpenDialogDistributionChart(e, step)
                            : null
                        }
                      >
                        <Box className={classes.cardTextWrap}>
                          {step.customName !== step.name && !step?.options?.isOptimizedByAutoML ? (
                            <>
                              <Box display={"flex"} alignItems={"center"}>
                                <span>{step.name}</span>
                                <CardInformationIcon step={step} />
                              </Box>
                              {[
                                PIPELINE_STEP_TYPES.CLASSIFIER,
                                PIPELINE_STEP_TYPES.TRAINING_ALGORITHM,
                              ].includes(step.name) &&
                              !pipelineSettings?.data?.disable_automl &&
                              isAutoML ? null : (
                                <span>{filterTruncate(step.customName, 50)}</span>
                              )}
                              {isStepAvailableToEdit(step.index) && !step?.data ? (
                                <span className={classes.dangerColor}>{" *"}</span>
                              ) : (
                                <span />
                              )}
                            </>
                          ) : (
                            <>
                              <Box display={"flex"} alignItems={"center"}>
                                {" "}
                                <span>
                                  {t("model-builder.card-type-prefix", {
                                    FunctionSubType: step.name,
                                  })}
                                </span>
                                <CardInformationIcon step={step} />
                              </Box>
                            </>
                          )}
                        </Box>
                      </CardStep>

                      {newStepAfter?.index === step.index ? (
                        <Box className={classes.NewCardWrapper}>
                          <IconArrowFullWidthWrap className={classes.fullWidthIcon} />
                          <NewCardStep
                            className={getStepStyle(newStepData.type)}
                            borderColor={getStepColor(newStepData.type)}
                          >
                            <Box className={classes.cardTextWrap}>
                              <span>{newStepData.name}</span>
                              <span>{filterTruncate(newStepData.customName, 50)}</span>
                            </Box>
                          </NewCardStep>
                        </Box>
                      ) : nextStepsIsNotNone(step.nextSteps) &&
                        groupItem.type !== "tvo" &&
                        !isNextStepAvailableToAdd(step.index, step) ? (
                        <Box className={classes.IconWrapper}>
                          <IconArrowWrap
                            dataTest={"ppl-step-next"}
                            disable={
                              !isStepAvailableToEdit(step.index) ||
                              !isStepAvailableToEdit(step.index + 1)
                            }
                            isRemoveArrow={true}
                            onClick={(_e) => handleNewStep(step.index, step)}
                          />
                        </Box>
                      ) : nextStepsIsNotNone(step.nextSteps) && groupItem.type !== "tvo" ? (
                        <Box className={classes.IconWrapper}>
                          <IconArrowAddWrap
                            dataTest={"ppl-step-add"}
                            disable={
                              !isStepAvailableToEdit(step.index) ||
                              !isStepAvailableToEdit(step.index + 1)
                            }
                            onClick={(_e) => handleNewStep(step.index, step)}
                            isRemoveArrow={true}
                          />
                        </Box>
                      ) : (
                        <Box mb={2} />
                      )}
                    </Box>
                  ))
                )}
              </Box>
              {(isModel && groupItem.type !== "tvo") ||
              (!isModel && groupItem.type !== "feature_extractor") ? (
                <Box className={classes.IconWrapper}>
                  <Box style={{ marginTop: "-1rem" }}>
                    <IconArrowWrap dataTest={"ppl-step-add"} />
                  </Box>
                </Box>
              ) : null}
            </Box>
          );
        })}
      {newStepAfter.nextSteps ? (
        <DrawerNewStep
          isOpen={Boolean(newStepAfter.nextSteps)}
          availableSteps={newStepAfter.nextSteps || []}
          allSteps={allSteps || []}
          getPipelineStepDescription={getPipelineStepDescription}
          onCreate={handleCreateNewStep}
          onChangeStep={handleNewStepChange}
          onClose={() => handleCloseNewStep()}
          onShowInformation={handleShowNewStepInformation}
        />
      ) : null}
      <DraweInformationStep
        isOpen={Boolean(activeInfoStep?.isOpen)}
        onClose={() => handleCloseStepInfo()}
        content={activeInfoStep?.descpription}
        docLink={activeInfoStep?.docLink}
        name={activeInfoStep?.name}
        descriptionParameters={activeInfoStep?.options?.descriptionParameters}
        dataParams={activeInfoStep?.dataParams || {}}
        transformDescription={activeInfoStep?.transformDescription}
        transformName={activeInfoStep?.transformName}
        type={activeInfoStep?.type}
      />
      <DrawerEditStep
        isOpen={Boolean(activeEditStep.name)} // && Boolean(!alertBuilder.message)
        onClose={() => handleCloseStepEdit()}
        name={activeEditStep.name}
        type={activeEditStep.type}
        onChangeEditMode={handleStepEditChangeView}
        isJsonEditMode={isEditModeJson}
        jsonEditModeLabel={t("model-builder.drawer-edit-step-json-mode")}
        alertMessage={activeEditStep?.options?.message}
        alertSeverity={activeEditStep?.options?.messageType}
      >
        {isEditModeJson ? (
          <FormStepEditor
            name={activeEditStep.name}
            type={activeEditStep.type}
            data={activeEditStep.data}
            transforms={transforms}
            onChangeData={handleUpdatePipelineStep}
            onClose={() => handleCloseStepEdit()}
            onSubmit={handleStepEditSubmit}
          />
        ) : (
          <FormPipelineStep
            type={activeEditStep.type}
            name={activeEditStep.name}
            options={activeEditStepOptions}
            isAutoML={isAutoML}
            transforms={transforms}
            isFormOptionsDisabled={isFormOptionsDisabled()} // disable session default values
            inputData={inputDataByTypeSubType.inputData}
            onSubmit={handleStepEditSubmit}
            onShowInfo={handleEditStepInformation}
            onClose={() => handleCloseStepEdit()}
            onChangeData={handleUpdatePipelineStep}
            getQueriesDescriptionParameters={getQueriesDescriptionParameters} // for query
            editFormKeyId={editFormKeyId}
          />
        )}
      </DrawerEditStep>
      <DrawerInformationMessage
        isOpen={Boolean(alertBuilder.message)}
        message={alertBuilder.message}
        parameters={alertBuilder.parameters}
        header={alertBuilder.title}
        onClose={() => onCloseAlertBuilder()}
      />
      <DialogConfirm
        isOpen={Boolean(deleteStepData.type)}
        title={t("model-builder.dialog-confirm-delete-title", { name: deleteStepData.customName })}
        text={t("model-builder.dialog-confirm-delete-text", { name: deleteStepData.customName })}
        onCancel={handleDeleteStepCancel}
        onConfirm={handleDeleteStepConfirm}
        cancelText={t("dialog-confirm-delete.cancel")}
        confirmText={t("dialog-confirm-delete.delete")}
      />
      {!_.isEmpty(activeEditStep) ? (
        <DialogConfirm
          isOpen={Boolean(isShowUnsavedAlertDialog)}
          title={t("model-builder.dialog-confirm-skip-unsaved-title", {
            name: activeEditStep.customName,
          })}
          text={t(
            activeEditStep.customName === AUTOML_PARAMS_NAME
              ? "model-builder.dialog-confirm-skip-unsaved-text"
              : "model-builder.dialog-confirm-save-unsaved-text",
            {
              name: activeEditStep.customName,
            },
          )}
          backText={t("model-builder.dialog-confirm-skip-unsaved-btn-back")}
          cancelText={t("model-builder.dialog-confirm-skip-unsaved-btn-cancel")}
          confirmText={t("model-builder.dialog-confirm-skip-unsaved-btn-confirm")}
          onBack={handleUnsavedStepBack}
          onCancel={handleUnsavedStepSkip}
          onConfirm={activeEditStep.customName !== AUTOML_PARAMS_NAME && handleUnsavedStepSave}
          isCancelSecondary
        />
      ) : null}
      {/* show description for editStepDialogInformation element */}
      <DialogInformation
        isOpen={Boolean(editStepDialogInformation.descpription)}
        onClose={handleCloseEditStepDialogInformation}
      >
        <Typography variant="h2" className={classes.infoTitle}>
          {editStepDialogInformation.title}
        </Typography>
        <Typography>
          <pre style={{ fontFamily: "inherit" }}>{editStepDialogInformation.descpription}</pre>
        </Typography>
      </DialogInformation>
      {/* show documentation */}
      <DialogInformation
        isOpen={Boolean(newStepDialogInformation.title)}
        onClose={handleCloseNewStepDialogInformation}
      >
        <Typography variant="h2" className={classes.infoTitle}>
          {newStepDialogInformation.title}
        </Typography>
        <Typography paragraph>{newStepDialogInformation.descpription}</Typography>
        <Typography paragraph>
          <Link href={newStepDialogInformation.docLink} target="_blank">
            {t("model-builder.drawer-step-info-doc-link")}
          </Link>
        </Typography>
      </DialogInformation>
      {isOpenDialogDistribution ? (
        <PipelineStepDrawerStatistic
          onClose={handleCloseDialogDistributionChart}
          isOpen={isOpenDialogDistribution}
          labelColors={labelColors}
          data={cacheDistributionData?.data || {}}
          featureVectorData={featureStatsData?.featureVectorData || {}}
          featureStatistics={featureStatsData?.featureStatistics || {}}
          featureSummary={featureStatsData?.featureSummary || {}}
          features={featureStatsData?.featureNames || {}}
          labelColumn={featureStatsData?.labelColumn || ""}
          labelValues={featureStatsData?.labelValues || []}
          selectLabelValuesColors={selectLabelValuesColors}
          classMap={classMap}
          classes={classes}
          isLoadFeatures={cacheDistributionData?.step?.isLoadFeatures}
          stepName={cacheDistributionData?.step?.stepName || ""}
        />
      ) : null}
      <UIDialogForm
        isOpen={isOpenCacheDownloadMenu}
        isCloseDisabled={isDownloadingCache}
        onClose={handleCloseDownloadCacheMenu}
        maxWidth="sm"
        actionsComponent={
          <>
            <Button
              onClick={handleCancelDownloadCache}
              color="primary"
              variant="outlined"
              fullWidth
            >
              {t("model-builder.download-cache-btn-cancel")}
            </Button>
            <Button
              fullWidth
              variant="contained"
              disableElevation
              onClick={handleSubmitDownloadCache}
              disabled={_.isEmpty(selectedStepCacheItems) || isDownloadingCache}
            >
              {t("model-builder.download-cache-btn")}
            </Button>
          </>
        }
      >
        <Stack justifyContent={"center"} width={"100%"}>
          {_.entries(stepCacheItemsToSelect).map(([name, { stepName, indexStep, indexPage }]) => (
            <Box key={`cache_download_menu_${name}`} mt={2}>
              {isDownloadingCache && selectedStepCacheItems.includes(name) ? (
                <Stack pt={1} pb={1} spacing={1} direction="row">
                  {downloadedCacheItems.includes(`${indexStep}_${indexPage}`) ? (
                    <DoneAllOutlinedIcon size={"1.5rem"} color="success" />
                  ) : (
                    <CircularProgress size={"1.5rem"} />
                  )}
                  <Typography>
                    {`${pipelineData?.name}.${stepName}.cache.${indexPage}.json`}
                  </Typography>
                </Stack>
              ) : (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={selectedStepCacheItems.includes(name)}
                      onClick={(_e) => handleSelectChacheToDownload(name)}
                      disabled={isDownloadingCache}
                    />
                  }
                  label={`${pipelineData?.name}.${stepName}.cache.${indexPage}.json`}
                />
              )}
            </Box>
          ))}
        </Stack>
      </UIDialogForm>
    </Box>
  );
};

export default PipelineBuilder;
