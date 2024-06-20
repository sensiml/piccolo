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

import { React, useState } from "react";
import ControlPanel from "components/ControlPanel";
import { generatePath, useHistory, useLocation } from "react-router-dom";

import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";

import { useTranslation } from "react-i18next";
import { ROUTES } from "routers";

import { useWindowResize } from "hooks";
import { RESPONSIVE } from "consts";
import { UIButtonConvertibleToShort } from "components/UIButtons";

const ModelControlPanel = ({
  modelData,
  isChangePlatform,
  onChangePlatform,
  downloading,
  handleDownloadRequest,
}) => {
  const { t } = useTranslation("models");
  const routersHistory = useHistory();
  const { pathname } = useLocation();

  const handleSwitchModel = () => {
    const path = generatePath(ROUTES.MAIN.MODEL_SELECT.path, {
      selectionMode: ROUTES.MAIN.MODEL_SELECT.MODES.CHANGE,
    });
    routersHistory.push(path, { parentPath: pathname });
  };

  const handleChangePlatform = () => {
    onChangePlatform();
  };

  const [isShortBtnText, setIsShortBtnText] = useState(false);

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < RESPONSIVE.WIDTH_FOR_SHORT_TEXT);
  });

  return (
    <ControlPanel
      title={
        isShortBtnText
          ? modelData?.name
          : t("model-select.control-panel-change", { modelName: modelData?.name })
      }
      onClickBack={isShortBtnText ? null : handleSwitchModel}
      turncateLenght={
        isShortBtnText ? RESPONSIVE.TRUNCATE_NAME_OVER_SHORT_TEXT : RESPONSIVE.TRUNCATE_NAME_OVER
      }
      actionsBtns={
        <>
          {isChangePlatform ? (
            <>
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                disabled={false}
                onClick={() => handleChangePlatform()}
                isShort={isShortBtnText}
                tooltip={t("model-panel.change-platform-btn")}
                text={t("model-panel.change-platform-btn")}
                icon={<EditOutlinedIcon />}
              />
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                disabled={downloading}
                onClick={() => handleDownloadRequest()}
                isShort={isShortBtnText}
                tooltip={t("model-panel.download-model-btn")}
                text={t("model-panel.download-model-btn")}
                icon={<CloudDownloadIcon />}
              />
            </>
          ) : null}
          <UIButtonConvertibleToShort
            variant={"outlined"}
            color={"primary"}
            onClick={() => handleSwitchModel()}
            isShort={isShortBtnText}
            tooltip={t("model-panel.change-btn")}
            text={t("model-panel.change-btn")}
            icon={<ArrowBackIcon />}
          />
        </>
      }
    />
  );
};

export default ModelControlPanel;
