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
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import ExploreIcon from "@mui/icons-material/Explore";
import PlaylistAddCheckIcon from "@mui/icons-material/PlaylistAddCheck";
import StorageIcon from "@mui/icons-material/Storage";
import SummaryIcon from "@mui/icons-material/Dvr";

import SchoolIcon from "@mui/icons-material/School";
import HelpIcon from "@mui/icons-material/Help";
import DriveEtaIcon from "@mui/icons-material/DriveEta";
import ChromeReaderModeIcon from "@mui/icons-material/ChromeReaderMode";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";

import i18n from "i18n";

import { generatePath } from "react-router-dom";
import { ROUTES } from "routers";

const getMenuProps = (val) => {
  return {
    value: val,
    color: "inherit",
    fontSize: "medium",
  };
};

const MenuTitles = {
  Home: i18n.t("layout:nav-drawer.menu-item-home"),
  Summary: i18n.t("layout:nav-drawer.menu-item-project-summary"),
  DataManager: i18n.t("layout:nav-drawer.menu-item-data-manager"),
  PrepareData: i18n.t("layout:nav-drawer.menu-item-prepare-data"),
  BuildModel: i18n.t("layout:nav-drawer.menu-item-build-model"),
  ExploreModel: i18n.t("layout:nav-drawer.menu-item-explore-model"),
  TestModel: i18n.t("layout:nav-drawer.menu-item-test-model"),
  DownloadModel: i18n.t("layout:nav-drawer.menu-item-download-model"),
};

const MenuItems = [
  {
    title: MenuTitles.Home,
    id: "navHome",
    orderIndex: 0,
    iconfn: (iconProps) => <HomeIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.HOME.path, { ...params }),
  },
  {
    title: "Change Project",
    tooltip: i18n.t("layout:menu-external.get-started-tooltip"),
    id: "navChangeProject",
    orderIndex: 1,
    iconfn: (iconProps) => <ExitToAppIcon {...iconProps} />,
    getPath: () => ROUTES.MAIN.HOME.path,
  },
  {
    title: MenuTitles.Summary,
    id: "navSummary",
    orderIndex: 2,
    iconfn: (iconProps) => <SummaryIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.PROJECT_SUMMARY.path, { ...params }),
  },
  {
    title: MenuTitles.DataManager,
    id: "navDataManager",
    orderIndex: 3,
    iconfn: (iconProps) => <StorageIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.DATA_MANAGER.path, { ...params }),
  },
  {
    title: MenuTitles.PrepareData,
    id: "navPrepareData",
    orderIndex: 4,

    iconfn: (iconProps) => <PollOutlinedIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.DATA_EXPLORER.path, { ...params }),
  },
  {
    title: MenuTitles.BuildModel,
    id: "navBuildModel",
    orderIndex: 5,
    iconfn: (iconProps) => <BuildIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.MODEL_BUILD.path, { ...params }),
  },
  {
    title: MenuTitles.ExploreModel,
    id: "navExploreModel",
    orderIndex: 6,
    iconfn: (iconProps) => <ExploreIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.MODEL_EXPLORE.path, { ...params }),
  },
  {
    title: MenuTitles.TestModel,
    id: "navTestModel",
    orderIndex: 7,
    iconfn: (iconProps) => <PlaylistAddCheckIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.MODEL_TEST.path, { ...params }),
  },
  {
    title: MenuTitles.DownloadModel,
    id: "navDownloadModel",
    orderIndex: 8,
    iconfn: (iconProps) => <CloudDownloadIcon {...iconProps} />,
    getPath: (params = {}) => generatePath(ROUTES.MAIN.MODEL_DOWNLOAD.path, { ...params }),
  },
];

const MenuItemsExternal = [
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

export { MenuItems, MenuTitles, MenuItemsExternal, getMenuProps };
