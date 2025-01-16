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

import React, { useEffect, useMemo, useState } from "react";
// eslint-disable-next-line no-unused-vars
import { useHistory, useParams, generatePath, useLocation, matchPath } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Box } from "@mui/material";
import { ROUTES } from "routers";

import KnowledgepacksTable from "components/KnowledgepacksTable";
import { UISnackBar } from "components/UISnackBar";

import ControlPanelSelect from "./components/ControlPanelSelect";
import ControlPanelChange from "./components/ControlPanelChange";

const ROUTERS_WITH_MODEL = [
  { title: "model-select.open-table-explore", path: ROUTES.MAIN.MODEL_EXPLORE.path },
  { title: "model-select.open-table-test", path: ROUTES.MAIN.MODEL_TEST.path },
  { title: "model-select.open-table-download", path: ROUTES.MAIN.MODEL_DOWNLOAD.path },
];

const MODELS_SELECTION_MODE = {
  [ROUTES.MAIN.MODEL_SELECT.MODES.SELECT_EXPLORE]: "Explore Model",
  [ROUTES.MAIN.MODEL_SELECT.MODES.SELECT_TEST]: "Test Model",
  [ROUTES.MAIN.MODEL_SELECT.MODES.SELECT_DOWNLOAD]: "Download Model",
};

const ModelSelect = ({ selectedProject, modelData, loadKnowledgepacks }) => {
  const routersHistory = useHistory();
  const { t } = useTranslation("models");
  const { selectionMode } = useParams();
  const { state } = useLocation();

  const [isShowAlerSnackBar, setIsShowAlertSnackBar] = useState(false);

  const tableOpenData = useMemo(() => {
    let res = {};
    ROUTERS_WITH_MODEL.forEach(({ title, path }) => {
      if (matchPath(state?.parentPath, { path, sctrict: false })) {
        res = { title: t(title), path };
      }
    });
    return res;
  }, []);

  useEffect(() => {
    if (state?.message) {
      setIsShowAlertSnackBar(true);
    }
    loadKnowledgepacks(selectedProject);
  }, [state]);

  useEffect(() => {
    if (!selectionMode) {
      routersHistory.push(
        generatePath(ROUTES.MAIN.MODEL_SELECT.path, {
          selectionMode: ROUTES.MAIN.MODEL_SELECT.MODES.SELECT,
        }),
      );
    }
  }, [routersHistory]);

  const handleClickBack = () => {
    routersHistory.push(state?.parentPath);
  };

  const getChangeModelName = () => {
    if (modelData?.name) {
      return `Model: ${modelData.name}`;
    }
    if (state?.parentPath !== undefined) {
      return `Select model to open in ${MODELS_SELECTION_MODE[state?.parentPath.split("/")[1]]}`;
    }

    return "Select Model";
  };

  const handleCloseAlert = () => {
    setIsShowAlertSnackBar(false);
  };

  const handleLoadKnowledgepacks = () => {
    loadKnowledgepacks(selectedProject);
  };

  return (
    <div>
      <Box mb={2}>
        {selectionMode === ROUTES.MAIN.MODEL_SELECT.MODES.CHANGE ? (
          <ControlPanelChange
            onClose={handleClickBack}
            title={getChangeModelName()}
            backTitle={tableOpenData?.title}
          />
        ) : (
          <ControlPanelSelect title={getChangeModelName()} />
        )}
      </Box>
      {/* isShowAlerSnackBar */}
      <UISnackBar
        isOpen={isShowAlerSnackBar && state?.message}
        onClose={handleCloseAlert}
        message={state?.message}
        variant={state?.massageVariant || "info"}
      />
      <KnowledgepacksTable
        tableTitle={t("model-select.table-header")}
        openRouterRedirect={tableOpenData?.path}
        onLoadKnowledgepacks={handleLoadKnowledgepacks}
        openTitle={tableOpenData?.title}
      />
    </div>
  );
};

export default ModelSelect;
