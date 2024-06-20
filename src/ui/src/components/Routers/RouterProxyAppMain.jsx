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

import React, { useEffect, useState, Suspense } from "react";
import _ from "lodash";

import {
  Redirect,
  useLocation,
  useHistory,
  useParams,
  matchPath,
  generatePath,
} from "react-router-dom";
import { useSelector, useDispatch, connect } from "react-redux";

import { useTranslation } from "react-i18next";
import { ROUTES } from "routers";

import { loadProjectData, loadProjectSummaryData } from "store/projects/actions";
import { cancelDownloadRequest, loadModel } from "store/models/actions";
import { BaseAPIError } from "store/api";

import UnSavedChangesDialog from "components/UnSavedChangesDialog";
import AlertDialog from "components/AlertDialog";

import { DialogConfirm } from "components/DialogConfirm";

import { setHasUnsavedChanges } from "store/common/actions";
import { AppLoader } from "components/UILoaders";

const mapDispatchToProps = {
  _setHasUnsavedChanges: setHasUnsavedChanges,
  _cancelDownloadRequest: cancelDownloadRequest,
  _loadModel: loadModel,
}; // to use thunk async dispatch

const DEFAULT_FIELDS = [
  "uuid",
  "sandbox_uuid",
  "name",
  "class_map",
  "feature_file_uuid",
  "query_summary",
];
const MODEL_ROUTERS_FIELDS = {
  [ROUTES.MAIN.MODEL_EXPLORE.child.CONFUSION_MATRIX.path]: [...DEFAULT_FIELDS, "model_results"],
  [ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_VISUALIZATION.path]: [
    ...DEFAULT_FIELDS,
    "feature_summary",
  ],
  [ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_EMBEDDING.path]: [...DEFAULT_FIELDS],
  [ROUTES.MAIN.MODEL_EXPLORE.child.FEATURE_SUMMARY.path]: [...DEFAULT_FIELDS, "feature_summary"],
  [ROUTES.MAIN.MODEL_EXPLORE.child.MODEL_SUMMARY.path]: [
    ...DEFAULT_FIELDS,
    "pipeline_summary",
    "device_configuration",
    "neuron_array",
  ],
  [ROUTES.MAIN.MODEL_EXPLORE.child.PIPELINE_SUMMARY.path]: [
    ...DEFAULT_FIELDS,
    "pipeline_summary",
    "neuron_array",
    "device_configuration",
  ],
  [ROUTES.MAIN.MODEL_EXPLORE.child.KNOWLEDGE_PACK_SUMMARY.path]: [
    ...DEFAULT_FIELDS,
    "knowledgepack_summary",
  ],
  [ROUTES.MAIN.MODEL_TEST.path]: [
    ...DEFAULT_FIELDS,
    "knowledgepack_description",
    "feature_summary",
  ],
  [ROUTES.MAIN.MODEL_DOWNLOAD.path]: [
    ...DEFAULT_FIELDS,
    "knowledgepack_description",
    "sandbox_uuid",
  ],
};

const ROUTERS_WITH_MODEL = [
  ..._.keys(MODEL_ROUTERS_FIELDS),
  ROUTES.MAIN.MODEL_TEST.path,
  ROUTES.MAIN.MODEL_DOWNLOAD.path,
];

const MODELS_SELECTION_MODE = [
  // multiply model explorer type
  ..._.keys(MODEL_ROUTERS_FIELDS).map((_el) => ROUTES.MAIN.MODEL_SELECT.MODES.SELECT_EXPLORE),
  ROUTES.MAIN.MODEL_SELECT.MODES.SELECT_TEST,
  ROUTES.MAIN.MODEL_SELECT.MODES.SELECT_DOWNLOAD,
];

const ScrollToTop = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
};

// eslint-disable-next-line no-shadow
const RouterProxyAppMain = ({
  children,
  _setHasUnsavedChanges,
  _loadModel,
  _cancelDownloadRequest,
}) => {
  const { t } = useTranslation("models");
  const { t: tNavigation } = useTranslation("navigation");
  const dispatch = useDispatch();
  const routersHistory = useHistory();
  const { pathname } = useLocation();

  const loggedIn = useSelector(
    (state) => state.auth?.loggedIn && state.auth?.loggedIn !== "undefined",
  );
  const selectedProject = useSelector((state) => state.projects?.selectedProject);
  const hasUnsavedChanges = useSelector(
    (state) => state.common?.values?.hasUnsavedChanges || false,
  );
  const isDownloading = useSelector(
    (state) => state.models?.downloadStatus?.isDownloading || false,
  );
  const modelData = useSelector((state) => state.models?.modelData?.data || {});

  const [currentPath, setCurrentPath] = useState("");
  const [isShowPrompt, setIsShowPrompt] = useState(false);
  const [isShowDownloadPrompt, setIsShowDownloadPrompt] = useState(false);
  const [isShowChangeProjectPrompt, setIsShowChangeProjectPrompt] = useState(false);

  const { projectUUID, modelUUID } = useParams();

  const getIsBlockRouter = () => {
    // collect all statements to block router redirect
    return hasUnsavedChanges || isDownloading;
  };

  const getIsModelScreen = (_pathname) => {
    let isMatch = matchPath(_pathname, {
      path: ROUTES.MAIN.MODEL_EXPLORE.path,
      sctrict: true,
    })?.isExact;
    ROUTERS_WITH_MODEL.forEach((path) => {
      if (matchPath(_pathname, { path, sctrict: true })?.isExact) {
        isMatch = true;
      }
    });
    return isMatch;
  };

  const getModelSelectionType = () => {
    let index = 0;
    let selection = MODELS_SELECTION_MODE[index];
    ROUTERS_WITH_MODEL.forEach((path) => {
      if (matchPath(pathname, { path, sctrict: false })) {
        selection = MODELS_SELECTION_MODE[index];
      }
      index++;
    });
    return selection;
  };

  const getModelFieldToLoad = (router) => {
    // eslint-disable-next-line consistent-return
    let fields = [];
    _.entries(MODEL_ROUTERS_FIELDS).forEach(([path, _fields]) => {
      if (matchPath(router, { path, sctrict: true })) {
        fields = _fields;
      }
    });
    return fields;
  };

  const isProjectSummaryScreen = () => {
    return Boolean(matchPath(pathname, { path: ROUTES.MAIN.PROJECT_SUMMARY.path, sctrict: false }));
  };

  const setOpenPrompt = () => {
    if (hasUnsavedChanges) {
      setIsShowPrompt(hasUnsavedChanges);
    }
    if (isDownloading) {
      setIsShowDownloadPrompt(isDownloading);
    }
  };

  useEffect(() => {
    // check unsaved change or downloading files
    if (getIsBlockRouter()) {
      routersHistory.block((prompt) => {
        // remember pathname
        setCurrentPath(`${prompt.pathname}${prompt.search}`);
        setOpenPrompt();
        return false;
      });
    } else {
      routersHistory.block((prompt) => {
        if (prompt && prompt?.isConfirmed) {
          return true;
        }
        if (prompt.pathname === "/" && !prompt.state?.isConfirmed) {
          setIsShowChangeProjectPrompt(true);
          return false;
        }
        return true;
      });
    }
  }, [routersHistory, hasUnsavedChanges, isDownloading]);

  useEffect(() => {
    if (isProjectSummaryScreen() || (projectUUID && projectUUID !== selectedProject?.uuid)) {
      // detect when project is changed to load new data clearProjectSelectedData
      dispatch(loadProjectSummaryData(projectUUID));
      dispatch(loadProjectData(projectUUID, isProjectSummaryScreen()));
    }

    const loadModelData = async (router) => {
      try {
        const fieldsToLoad = getModelFieldToLoad(router);
        await _loadModel(modelUUID, fieldsToLoad);
      } catch (err) {
        if (err instanceof BaseAPIError) {
          let { message } = err;

          if (err.errorCode === 404) {
            message = t("model-selected-does-not-exist");
          }
          routersHistory.push({
            pathname: generatePath(ROUTES.MAIN.MODEL_SELECT.path, {
              selectionMode: getModelSelectionType(),
            }),
            state: { message, massageVariant: "warning", parentPath: pathname },
          });
        }
      }
    };

    if (getIsModelScreen(pathname)) {
      if (modelUUID) {
        loadModelData(pathname);
      } else if (!modelUUID || !modelData?.uuid) {
        routersHistory.push({
          pathname: generatePath(ROUTES.MAIN.MODEL_SELECT.path, {
            selectionMode: getModelSelectionType(),
          }),
          state: { parentPath: pathname },
        });
      }
    }
  }, [pathname]);

  const handlePromptContinue = async () => {
    setIsShowPrompt(false);
    await _setHasUnsavedChanges(false);
    routersHistory.push(currentPath);
  };

  const handlePromptCancel = () => {
    setIsShowPrompt(false);
  };

  const handlePromptDownloadContinue = async () => {
    setIsShowDownloadPrompt(false);
    await _cancelDownloadRequest();
    routersHistory.push(currentPath);
  };

  const handlePromptDownloadCancel = () => {
    setIsShowDownloadPrompt(false);
  };

  const handlePromptChangeProjectCancel = () => {
    setIsShowChangeProjectPrompt(false);
  };

  const handlePromptChangeProjectConfirm = () => {
    routersHistory.push({
      pathname: generatePath(ROUTES.MAIN.HOME.path),
      state: {
        isConfirmed: true,
      },
    });
    handlePromptChangeProjectCancel();
  };

  return (
    <>
      <ScrollToTop />
      {loggedIn ? (
        <Suspense fallback={<AppLoader isOpen />}>{children}</Suspense>
      ) : (
        <Redirect to={{ pathname: ROUTES.AUTH.path, state: { successRedirect: pathname } }} />
      )}
      <UnSavedChangesDialog
        openDialog={isShowPrompt}
        buttonOneAction={handlePromptContinue}
        buttonTwoAction={handlePromptCancel}
      />
      <AlertDialog
        openDialog={isShowDownloadPrompt}
        alertTitle={t("download.alert-leave-title")}
        dialogText={t("download.alert-leave-text")}
        buttonOneText={t("download.alert-leave-confirm")}
        buttonTwoText={t("download.alert-leave-cancel")}
        buttonOneAction={handlePromptDownloadContinue}
        buttonTwoAction={handlePromptDownloadCancel}
      />
      <DialogConfirm
        isOpen={isShowChangeProjectPrompt}
        title={tNavigation("alert-change-project.title")}
        text={tNavigation("alert-change-project.text")}
        onConfirm={handlePromptChangeProjectConfirm}
        onCancel={handlePromptChangeProjectCancel}
      />
    </>
  );
};

export default connect(undefined, mapDispatchToProps)(RouterProxyAppMain);
