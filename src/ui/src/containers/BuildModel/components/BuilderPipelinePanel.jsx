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

import React, { useState } from "react";

import PlayArrowOutlinedIcon from "@mui/icons-material/PlayArrowOutlined";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import StopIcon from "@mui/icons-material/Stop";
import IosShareIcon from "@mui/icons-material/IosShare";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

import ControlPanel from "components/ControlPanel";
import PipelineExportMenu from "components/PipelineExportMenu";

import { UIButtonConvertibleToShort } from "components/UIButtons";
import { useTranslation } from "react-i18next";
import { useMainContext, useWindowResize } from "hooks";
import { RESPONSIVE } from "consts";

const BuilderPipelinePanel = ({
  title,
  handleChangePipeline,
  getIsReadyToOptimize,
  isOptimizationRunning,
  handleLaunchOptimize,
  handleKillLaunchOptimize,
  onShowInformation,
  exportPipeline,
  projectUUID,
  pipelineUUID,
}) => {
  const { t } = useTranslation("models");
  const { showMessageSnackbar } = useMainContext();

  const [isShortBtnText, setIsShortBtnText] = useState(false);

  const [anchorExportMenu, setAnchorExportMenu] = useState(null);
  const isOpenExportMenu = Boolean(anchorExportMenu);

  const handleExportPipeline = async (downloadType) => {
    try {
      await exportPipeline(projectUUID, pipelineUUID, downloadType);
    } catch (error) {
      showMessageSnackbar("error", error.message);
    }
  };

  const handleCloseExportMenu = () => {
    setAnchorExportMenu(null);
  };

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < RESPONSIVE.WIDTH_FOR_SHORT_TEXT);
  });

  return (
    <>
      <PipelineExportMenu
        archorEl={anchorExportMenu}
        isOpen={isOpenExportMenu}
        onClose={handleCloseExportMenu}
        onDownloadPipeline={handleExportPipeline}
      />
      <ControlPanel
        title={title}
        truncateLength={
          isShortBtnText ? RESPONSIVE.TRUNCATE_NAME_OVER_SHORT_TEXT : RESPONSIVE.TRUNCATE_NAME_OVER
        }
        onClickBack={isShortBtnText ? null : handleChangePipeline}
        onShowInformation={onShowInformation}
        actionsBtns={
          <>
            <UIButtonConvertibleToShort
              variant={"contained"}
              color={"primary"}
              disabled={!getIsReadyToOptimize() || isOptimizationRunning}
              onClick={() => handleLaunchOptimize()}
              isShort={isShortBtnText}
              tooltip={t("model-builder.pipeline-panel-btn-start-tooltip")}
              text={t("model-builder.pipeline-panel-btn-start")}
              icon={<PlayArrowOutlinedIcon />}
            />
            <UIButtonConvertibleToShort
              variant={"outlined"}
              color={"primary"}
              disabled={false}
              onClick={() => handleKillLaunchOptimize()}
              isShort={isShortBtnText}
              tooltip={t("model-builder.pipeline-panel-btn-stop-tooltip")}
              text={t("model-builder.pipeline-panel-btn-stop")}
              icon={<StopIcon />}
            />

            <UIButtonConvertibleToShort
              color="primary"
              variant={"outlined"}
              onClick={(e) => setAnchorExportMenu(e.currentTarget)}
              isShort={isShortBtnText}
              icon={<IosShareIcon />}
              endIcon={<ArrowDropDownIcon />}
              tooltip={t("model-builder.pipeline-panel-btn-export-tooltip")}
              text={t("Export")}
            />
            <UIButtonConvertibleToShort
              variant={"outlined"}
              color={"primary"}
              disabled={false}
              onClick={() => handleChangePipeline()}
              isShort={isShortBtnText}
              tooltip={"Switch pipelines"}
              text={t("model-builder.pipeline-panel-btn-change")}
              icon={<ArrowBackIcon />}
            />
          </>
        }
      />
    </>
  );
};

export default BuilderPipelinePanel;
