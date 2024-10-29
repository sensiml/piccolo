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

/* eslint-disable no-shadow */
import React, { useState, useEffect, useMemo } from "react";

import { filterTruncateResponsive } from "filters";
import { matchPath, useLocation, useHistory, generatePath } from "react-router-dom";
import { connect } from "react-redux";
import { useTranslation } from "react-i18next";
import { RESPONSIVE } from "consts";
import { ROUTES } from "routers";

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  useMediaQuery,
} from "@mui/material";

import CloseIcon from "@mui/icons-material/Close";

import { logOut } from "store/auth/actions";
import { getIsFreeAccount } from "store/auth/selectors";
import { setNavBarState } from "store/common/actions";
import {
  loadTeamInfo,
  loadAccountApiKeys,
  createAccountApiKey,
  deleteApiKey,
} from "store/team/actions";
import { useWindowResize } from "hooks";

import useStyles from "components/Layout/Header.style";
import NavDrawer from "components/Layout/NavDrawer";
import HeaderMenu from "components/Layout/HeaderMenu";

import HeaderAppBar from "components/Layout/HeaderAppBar";

const mapStateToProps = (state) => {
  return {
    userId: state?.auth?.userId,
    selectedProject: state.projects?.selectedProject?.uuid || "",
    selectedPipeline: state.pipelines?.selectedPipeline || "",
    selectedPipelineName: state.pipelines?.selectedPipelineName,
    selectedPipelineData: state.pipelines?.pipelineData?.data || {},
    selectedPipelineExecutionType: state.pipelines?.pipelineExecutionType,
    setPipelineIsActiveStatus: state.pipelines?.setPipelineIsActiveStatus,
    selectedModel: state.models?.selectedModel || "",
    selectedProjectName: state.projects?.selectedProject?.name,
    isFreeAccount: getIsFreeAccount(state),
    pipelineRunningStatus: state.pipelines?.pipelineRunningStatus,
  };
};

const mapDispatchToProps = {
  logOut,
  setNavBarState,
  loadTeamInfo,
  loadAccountApiKeys,
  createAccountApiKey,
  deleteApiKey,
};

const Header = ({
  userId,
  selectedProject,
  selectedPipeline,
  selectedPipelineName,
  selectedModel,
  selectedProjectName,
  isFreeAccount,
  pipelineRunningStatus,
  selectedPipelineExecutionType,

  logOut,
  setNavBarState,
}) => {
  const { t } = useTranslation(["layout", "team"]);
  const { pathname } = useLocation();
  const routersHistory = useHistory();
  const classes = useStyles();
  const smallScreenSize = useMediaQuery("(min-width:800px)");

  const [open, setOpen] = useState(smallScreenSize);
  const [showVersion, setShowVersion] = useState(false);
  const [isShortBtnText, setIsShortBtnText] = useState(false);
  const [windowSize, setWindowSize] = useState(900);
  const [anchorEl, setAnchorEl] = useState(null);

  const isMenuOpen = Boolean(anchorEl);

  const appENV = useMemo(() => {
    return process.env.REACT_APP_NODE_ENV === "Production"
      ? ""
      : `${process.env.REACT_APP_NODE_ENV}`;
  }, []);

  const handleDrawerOpen = () => {
    setOpen(true);
    setNavBarState(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
    setNavBarState(false);
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMenuShowAbout = () => {
    setAnchorEl(null);
    setShowVersion(true);
  };

  const handleMenuLogOut = () => {
    logOut();
  };

  const handleMenuAccountSettings = () => {
    routersHistory.push(ROUTES.ACCOUNT_SETTINGS.path);
  };

  const handleChangePipeline = async () => {
    routersHistory.push(
      generatePath(ROUTES.MAIN.MODEL_BUILD.child.SELECT_SCREEN.path, {
        projectUUID: selectedProject,
      }),
    );
  };

  const headerTitle = useMemo(() => {
    const matchHome = matchPath(pathname, { path: ROUTES.MAIN.HOME.path, exact: true });
    if (matchHome) {
      return t("header.title-home", { appENV });
    }
    return t("header.project-title", {
      projectName: filterTruncateResponsive(selectedProjectName, windowSize),
    });
  }, [pathname, appENV, windowSize, selectedProjectName]);

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < RESPONSIVE.WIDTH_FOR_SHORT_TEXT);
    setWindowSize(data.innerWidth);
  });

  useEffect(() => {
    setOpen(smallScreenSize);
    setNavBarState(smallScreenSize);
  }, [setNavBarState, smallScreenSize]);

  return (
    <div className={classes.root}>
      <HeaderAppBar
        isOpen={open}
        isShortBtnText={isShortBtnText}
        userId={userId}
        headerTitle={headerTitle}
        onDrawerClose={handleDrawerClose}
        onDrawerOpen={handleDrawerOpen}
        onOpenMenu={handleProfileMenuOpen}
      />
      <Dialog
        disableEscapeKeyDown
        open={showVersion}
        id="versionDialog"
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">SensiML™ Analytics Studio</DialogTitle>
        <DialogContent>
          <DialogContentText style={{ textAlign: "center" }} id="alert-dialog-description">
            {t("app-version", { appVersion: process.env.REACT_APP_VERSION })}
          </DialogContentText>
        </DialogContent>
        <DialogActions style={{ justifyContent: "center" }}>
          <Button
            id="closeVersionDialog"
            onClick={() => setShowVersion(false)}
            startIcon={<CloseIcon />}
            color="primary"
            variant="contained"
          >
            {t("btn-close-app-version")}
          </Button>
        </DialogActions>
      </Dialog>
      <NavDrawer
        isOpen={open}
        isSmallScreen={!smallScreenSize}
        selectedProject={selectedProject}
        selectedModel={selectedModel}
        selectedPipeline={selectedPipeline}
        selectedPipelineName={selectedPipelineName}
        handleChangePipeline={handleChangePipeline}
        pipelineRunningStatus={pipelineRunningStatus}
        selectedPipelineExecutionType={selectedPipelineExecutionType}
        onClose={() => handleDrawerClose()}
      />
      <HeaderMenu
        isOpen={isMenuOpen}
        anchorEl={anchorEl}
        isFreeAccount={isFreeAccount}
        onClose={handleMenuClose}
        onClickAccountSetting={handleMenuAccountSettings}
        onClickShowAbout={handleMenuShowAbout}
        onClickLogOut={handleMenuLogOut}
      />
    </div>
  );
};
export default connect(mapStateToProps, mapDispatchToProps)(Header);
