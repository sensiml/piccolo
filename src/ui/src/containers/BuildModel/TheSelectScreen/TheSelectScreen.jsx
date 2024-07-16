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

import React, { useEffect, useState, useMemo } from "react";
import _ from "lodash";
import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";

import logger from "store/logger";
import { useHistory, generatePath, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Box, Typography } from "@mui/material";
import { ROUTES } from "routers";
import { useWindowResize } from "hooks";
import { RESPONSIVE } from "consts";
import { UIButtonConvertibleToShort } from "components/UIButtons";

import PipelinesTable from "components/PipelinesTable";
import DialogInformation from "components/DialogInformation/DialogInformation";
import PipelineImportForm from "components/PipelineImportForm";
import ControlPanel from "components/ControlPanel";
import PipelineCreateForm from "components/PipelineCreateForm";
import PipelineTemplateCreateForm from "components/PipelineTemplateCreateForm";

import { DEFAULT_CLASSIFIER, PIPELINE_STEP_TYPES } from "store/autoML/const";

import useStyles from "../BuildModeStyle";
import SelectCard from "../componets/SelectCard";

const TheSelectScreen = ({
  selectedProject,
  classifiers,
  isPipelinesFetching,
  pipleneTemplates,
  queries,
  getPipelineStepDataClass,
  loadingPipelineSteps,
  // actions
  addPipeline,
  loadPipelines,
  loadQueries,
  loadPipelineTemplates,
  clearPipelinesteps,
  setLoadingPipelineSteps,
}) => {
  const classes = useStyles();
  const routersHistory = useHistory();
  const { projectUUID } = useParams();
  const { t } = useTranslation("models");

  const [pipelineError, setPipelineError] = useState(null);
  const [isOpenBuildModal, setIsOpenBuildModal] = useState(false);
  const [isOpenImportPipeline, setIsOpenImportPipeline] = useState(false);
  const [isOpenPipelineTemplate, setIsOpenPipelineTemplate] = useState(false);
  const [selectedPipelineTemplate, setSelectedPipelineTemplate] = useState({});
  const [queryInputData, setQueryInputData] = useState(true);

  const [isShortBtnText, setIsShortBtnText] = useState(false);

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < RESPONSIVE.WIDTH_FOR_SHORT_TEXT);
  });

  const isDisableToBuildPipeline = useMemo(() => {
    return isPipelinesFetching;
  }, [isPipelinesFetching]);

  const queriesFormOptions = useMemo(() => {
    return _.map(queries, (query) => ({ name: query.name, value: query.name }));
  }, [queries]);

  const getCrateTooltipDescriptionPoints = useMemo(() => {
    const descPoints = t("model-builder-select.ppl-btn-create-desc-points", {
      returnObjects: true,
    });
    if (_.isArray(descPoints)) {
      return descPoints;
    }
    return [];
  });

  const handleOpenBuildNewPipeline = (isOpen) => {
    setPipelineError("");
    setIsOpenBuildModal(isOpen);
  };

  const handleOpenImportPipeline = (isOpen) => {
    setPipelineError("");
    setIsOpenImportPipeline(isOpen);
  };

  const handleOpenPipelineTemplate = (isOpen, template = {}) => {
    setPipelineError("");
    setIsOpenPipelineTemplate(isOpen);
    setSelectedPipelineTemplate(template);
  };

  const handleLoadPipelines = () => {
    loadPipelines(projectUUID);
  };

  const handleBuildNewPipeline = async ({
    pipelineName,
    isAutoMLOptimization,
    selectedClassifier,
    queryName,
    pipelineJson,
    replacedColumns,
    isUseSessionPreprocessor,
  }) => {
    setPipelineError("");
    if (!selectedProject) {
      setPipelineError(t("add-pipelines.errors.not-selected-project"));
      return;
    }
    if (!pipelineName) {
      setPipelineError(t("add-pipelines.errors.no-pipeline-name"));
      return;
    }

    setLoadingPipelineSteps(true, "Creating piplene ...");

    const response = await addPipeline(projectUUID, pipelineName);

    if (!response.isSuccess) {
      setPipelineError(response.details);
      setLoadingPipelineSteps(false, "");
      return;
    }

    logger.logInfo("", "create_pipeline", {
      template_name: selectedPipelineTemplate.name || "",
      is_automl: isAutoMLOptimization || false,
      classification_algorithm: !isAutoMLOptimization ? selectedClassifier || "" : "",
      project_uuid: projectUUID,
    });

    setIsOpenImportPipeline(false);

    routersHistory.push({
      pathname: generatePath(ROUTES.MAIN.MODEL_BUILD.child.AUTOML_BUILDER_SCREEN.path, {
        projectUUID,
        pipelineUUID: response.details,
      }),
      state: {
        isAutoMLOptimization,
        selectedClassifier,
        queryName,
        pipelineJson,
        replacedColumns,
        isUseSessionPreprocessor,
      },
    });
  };

  useEffect(() => {
    if (isOpenBuildModal || isOpenImportPipeline || isOpenPipelineTemplate) {
      loadQueries(projectUUID);
    }
  }, [isOpenBuildModal, isOpenImportPipeline, isOpenPipelineTemplate]);

  useEffect(() => {
    const inputData = getPipelineStepDataClass({
      type: PIPELINE_STEP_TYPES.QUERY,
      subtype: [PIPELINE_STEP_TYPES.QUERY],
      isAutoML: true,
    }).getInputsData();
    setQueryInputData(inputData);
  }, [queries]);

  useEffect(() => {
    handleLoadPipelines();
    loadPipelineTemplates();
    clearPipelinesteps();
  }, []);

  useEffect(() => {
    setLoadingPipelineSteps(false, "");
    setIsOpenImportPipeline(false);
  }, []);

  const renderedCreateDesc = useMemo(() => {
    return (
      <>
        {t("model-builder-select.ppl-btn-create-tooltip")}
        <ul className={classes.createCardDescList}>
          {getCrateTooltipDescriptionPoints.map((el, index) => (
            <li className={classes.createCardDescListItem} key={`import_desc_point_${index}`}>
              {el}
            </li>
          ))}
        </ul>
      </>
    );
  }, []);

  return (
    <Box className={classes.root}>
      <Box mb={2}>
        <ControlPanel
          title={"Build Model 1"}
          actionsBtns={
            <>
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                onClick={() => handleOpenBuildNewPipeline(true)}
                isShort={isShortBtnText}
                tooltip={renderedCreateDesc}
                text={t("model-builder-select.create-dialog-header")}
                icon={<AddOutlinedIcon />}
              />
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                onClick={() => handleOpenImportPipeline(true)}
                isShort={isShortBtnText}
                tooltip={t("model-builder-select.ppl-btn-import-tooltip")}
                text={t("model-builder-select.ppl-btn-import")}
                icon={<CloudUploadOutlinedIcon />}
              />
            </>
          }
        />
      </Box>
      <Box mb={2} spacing={2} className={classes.selectCardGridWrapper}>
        <SelectCard
          header={t("model-builder-select.create-dialog-header")}
          btnText={t("model-builder-select.create-dialog-header")}
          onClickBuild={() => handleOpenBuildNewPipeline(true)}
          isBuildDisabled={isDisableToBuildPipeline}
        >
          {renderedCreateDesc}
        </SelectCard>
        {pipleneTemplates.map((template, index) => (
          <SelectCard
            key={`template_card_${index}`}
            image={template.img}
            header={template.name}
            btnText={"Select template"}
            onClickBuild={() => handleOpenPipelineTemplate(true, template)}
            isBuildDisabled={isDisableToBuildPipeline}
          >
            {template.brief}
          </SelectCard>
        ))}
      </Box>
      <DialogInformation
        isOpen={isOpenBuildModal}
        onClose={() => handleOpenBuildNewPipeline(false)}
      >
        <Typography variant="h2" className={classes.createDialogTitle}>
          {t("model-builder-select.create-dialog-header")}
        </Typography>
        <PipelineCreateForm
          pipelineError={pipelineError}
          loadingPipelineSteps={loadingPipelineSteps}
          queriesFormOptions={queriesFormOptions}
          queryInputData={queryInputData}
          onSubmit={handleBuildNewPipeline}
          classifiers={classifiers}
          defaultClassifier={DEFAULT_CLASSIFIER}
        />
      </DialogInformation>

      <DialogInformation
        isOpen={isOpenImportPipeline}
        onClose={() => handleOpenImportPipeline(false)}
      >
        <Typography variant="h2" className={classes.createDialogTitle}>
          {t("model-builder-select.import-dialog-header")}
        </Typography>
        <PipelineImportForm
          pipelineError={pipelineError}
          loadingPipelineSteps={loadingPipelineSteps}
          queriesFormOptions={queriesFormOptions}
          queryInputData={queryInputData}
          onSubmit={handleBuildNewPipeline}
        />
      </DialogInformation>
      <DialogInformation
        isOpen={isOpenPipelineTemplate}
        onClose={() => handleOpenPipelineTemplate(false)}
      >
        <Typography variant="h2" className={classes.createDialogTitle}>
          {t("model-builder-select.template-dialog-header")}
        </Typography>
        <PipelineTemplateCreateForm
          pipelineError={pipelineError}
          pipelineTemplate={selectedPipelineTemplate}
          loadingPipelineSteps={loadingPipelineSteps}
          queriesFormOptions={queriesFormOptions}
          queryInputData={queryInputData}
          onSubmit={handleBuildNewPipeline}
        />
      </DialogInformation>
      <PipelinesTable />
    </Box>
  );
};

export default TheSelectScreen;
