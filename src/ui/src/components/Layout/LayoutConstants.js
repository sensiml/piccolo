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

/* eslint-disable react/jsx-filename-extension */
import React from "react";
import HomeIcon from "@mui/icons-material/Home";
import PollOutlinedIcon from "@mui/icons-material/PollOutlined";
import BuildIcon from "@mui/icons-material/Build";
import FilterAltOutlinedIcon from "@mui/icons-material/FilterAltOutlined";

import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import ExploreIcon from "@mui/icons-material/Explore";
import AutoModeOutlinedIcon from "@mui/icons-material/AutoModeOutlined";
import ModelTrainingOutlinedIcon from "@mui/icons-material/ModelTrainingOutlined";
import PlaylistAddCheckIcon from "@mui/icons-material/PlaylistAddCheck";
import StorageIcon from "@mui/icons-material/Storage";
import SummaryIcon from "@mui/icons-material/Dvr";
import SchoolIcon from "@mui/icons-material/School";
import HelpIcon from "@mui/icons-material/Help";
import DriveEtaIcon from "@mui/icons-material/DriveEta";
import ChromeReaderModeIcon from "@mui/icons-material/ChromeReaderMode";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import DataObjectOutlinedIcon from "@mui/icons-material/DataObjectOutlined";

import i18n from "i18n";

import { generatePath } from "react-router-dom";
import { ROUTES } from "routers";

const getMenuProps = (val) => {
  return {
    value: val,
    color: "inherit",
    fontSize: "small",
  };
};

const MENU_ITEMS_INFO = {
  HOME: {
    title: i18n.t("layout:nav-drawer.menu-item-home"),
    id: "navHome",
    orderIndex: 0,
    iconfn: (iconProps) => <HomeIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.HOME.path, { ...params }),
  },
  CHANGE_PROJECT: {
    title: i18n.t("layout:nav-drawer.menu-item-change-project"),
    tooltip: i18n.t("layout:menu-external.get-started-tooltip"),
    id: "navChangeProject",
    orderIndex: 1,
    iconfn: (iconProps) => <ExitToAppIcon {...iconProps} />,
    getPath: () => ROUTES.MAIN.HOME.path,
  },
  SUMMARY: {
    title: i18n.t("layout:nav-drawer.menu-item-project-summary"),
    id: "navSummary",
    orderIndex: 2,
    iconfn: (iconProps) => <SummaryIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.PROJECT_SUMMARY.path, { ...params }),
  },
  DATAMANAGER: {
    title: i18n.t("layout:nav-drawer.menu-item-data-manager"),
    id: "navDataManager",
    orderIndex: 3,
    iconfn: (iconProps) => <StorageIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.DATA_MANAGER.path, { ...params }),
  },
  PRERARE_DATA: {
    title: i18n.t("layout:nav-drawer.menu-item-queries"),
    id: "navPrepareData",
    orderIndex: 4,
    iconfn: (iconProps) => <PollOutlinedIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.DATA_EXPLORER.path, { ...params }),
  },
  BUILD_MODEL: {
    title: i18n.t("layout:nav-drawer.menu-item-build-model"),
    id: "navBuildModel",
    orderIndex: 5,
    iconfn: (iconProps) => <BuildIcon {...iconProps} />,
    getPath: (params = {}) =>
      generatePath(ROUTES.MAIN.MODEL_BUILD.child.SELECT_SCREEN.path, { ...params }),
    subItems: [
      {
        title: i18n.t("layout:nav-drawer.menu-item-feature-extractor"),
        tooltip: i18n.t("layout:nav-drawer.menu-item-pipeline-fe-tooltip"),
        id: "navFeatureExtractor",
        orderIndex: 1,
        iconfn: (iconProps) => <FilterAltOutlinedIcon {...iconProps} />,
        getPath: (params = {}) =>
          generatePath(ROUTES.MAIN.MODEL_BUILD.child.FEATURE_EXTRACTOR.path, { ...params }),
      },
      {
        title: i18n.t("layout:nav-drawer.menu-item-pipeline-custom"),
        tooltip: i18n.t("layout:nav-drawer.menu-item-pipeline-custom-tooltip"),
        id: "navPipelineCustom",
        orderIndex: 3,
        iconfn: (iconProps) => <ModelTrainingOutlinedIcon {...iconProps} fontSize="medium" />,
        getPath: (params = {}) =>
          generatePath(ROUTES.MAIN.MODEL_BUILD.child.CUSTOM.path, {
            ...params,
          }),
      },
      {
        title: i18n.t("layout:nav-drawer.menu-item-pipeline-automl"),
        tooltip: i18n.t("layout:nav-drawer.menu-item-pipeline-automl-tooltip"),
        id: "navPipelineAutoML",
        orderIndex: 2,
        iconfn: (iconProps) => <AutoModeOutlinedIcon {...iconProps} />,
        getPath: (params = {}) =>
          generatePath(ROUTES.MAIN.MODEL_BUILD.child.AUTOML.path, {
            ...params,
          }),
      },
    ],
  },
  MODELS: {
    title: i18n.t("layout:nav-drawer.menu-item-models"),
    id: "navOpenModel",
    orderIndex: 6,
    iconfn: (iconProps) => <DataObjectOutlinedIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.MODEL_SELECT.path, { ...params }),
    subItems: [
      {
        title: i18n.t("layout:nav-drawer.menu-item-explore-model"),
        id: "navExploreModel",
        orderIndex: 7,
        iconfn: (iconProps) => <ExploreIcon {...iconProps} />,
        getPath: (params = {}) => generatePath(ROUTES.MAIN.MODEL_EXPLORE.path, { ...params }),
      },
      {
        title: i18n.t("layout:nav-drawer.menu-item-test-model"),
        id: "navTestModel",
        orderIndex: 8,
        iconfn: (iconProps) => <PlaylistAddCheckIcon {...iconProps} />,
        getPath: (params = {}) => generatePath(ROUTES.MAIN.MODEL_TEST.path, { ...params }),
      },
      {
        title: i18n.t("layout:nav-drawer.menu-item-download-model"),
        id: "navDownloadModel",
        orderIndex: 9,
        iconfn: (iconProps) => <CloudDownloadIcon {...iconProps} />,
        getPath: (params = {}) => generatePath(ROUTES.MAIN.MODEL_DOWNLOAD.path, { ...params }),
      },
    ],
  },
};

const MENU_ITEMS = [
  { ...MENU_ITEMS_INFO.HOME },
  { ...MENU_ITEMS_INFO.CHANGE_PROJECT },
  { ...MENU_ITEMS_INFO.SUMMARY },
  { ...MENU_ITEMS_INFO.DATAMANAGER },
  { ...MENU_ITEMS_INFO.PRERARE_DATA },
  { ...MENU_ITEMS_INFO.BUILD_MODEL },
  { ...MENU_ITEMS_INFO.MODELS },
];

const MENU_ITEMS_EXTERNAL = [
  {
    title: i18n.t("layout:menu-external.get-started-title"),
    tooltip: i18n.t("layout:menu-external.get-started-tooltip"),
    id: "navGetStarted",
    target: "_blank",
    orderIndex: 0,
    isHidden: false,
    iconfn: (iconProps) => <SchoolIcon {...iconProps} />,
    getPath: () => ROUTES.GET_STARTED.path,
  },
  {
    title: i18n.t("layout:menu-external.demo-title"),
    tooltip: i18n.t("layout:menu-external.demo-tooltip"),
    id: "navDemos",
    target: "_blank",
    orderIndex: 1,
    isHidden: false,
    iconfn: (iconProps) => <DriveEtaIcon {...iconProps} />,
    getPath: () => ROUTES.DEMO.path,
  },
  {
    title: i18n.t("layout:menu-external.documentation-title"),
    tooltip: i18n.t("layout:menu-external.documentation-tooltip"),
    id: "navDocumentation",
    target: "_blank",
    orderIndex: 2,
    isHidden: false,
    iconfn: (iconProps) => <ChromeReaderModeIcon {...iconProps} />,
    getPath: () => ROUTES.DOCUMENTATION.path,
  },
  {
    title: i18n.t("layout:menu-external.support-title"),
    tooltip: i18n.t("layout:menu-external.support-tooltip"),
    id: "navSupport",
    target: "_blank",
    orderIndex: 3,
    isHidden: false,
    iconfn: (iconProps) => <HelpIcon {...iconProps} />,
    getPath: () => ROUTES.SUPPORT.path,
  },
];

export { MENU_ITEMS, MENU_ITEMS_INFO, MENU_ITEMS_EXTERNAL, getMenuProps };
