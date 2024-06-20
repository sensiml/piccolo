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

import React, { useState, lazy } from "react";
import { Header } from "components/Layout";
import { Switch, Route } from "react-router-dom";
import { Box, Grid, Snackbar } from "@mui/material";

import { MainContext } from "contexts";
import RouterProxyAppMain from "components/Routers/RouterProxyAppMain";
import ErrorBoundary from "components/ErrorBoundary";
import ToastMessage from "components/ToastMessage/ToastMessage";

import { BannerMaintenance } from "components/Banners";
import { AppLoader } from "components/UILoaders";

import { ROUTES } from "routers";

import useStyles from "./MainStyles";

const Home = lazy(() => import("containers/Home"));
const ProjectSummary = lazy(() => import("containers/ProjectSummary"));
const TheDataExplorer = lazy(() => import("containers/DataExplorer"));
const BuildModel = lazy(() => import("containers/BuildModel"));
const ExploreModels = lazy(() => import("containers/ExploreModels"));
const TestModels = lazy(() => import("containers/TestModels"));
const DownloadModel = lazy(() => import("containers/DownloadModel"));
const ModelSelect = lazy(() => import("containers/ModelSelect"));
const Demo = lazy(() => import("containers/Demo"));
const TheDataManager = lazy(() => import("containers/DataManager"));

const Main = ({
  isMainScreenLoading,
  isShowBannerMaintenance,
  headerTitle,
  setIsShowBannerMaintenance,
}) => {
  const classes = useStyles();

  const handleCloseBanner = () => {
    setIsShowBannerMaintenance(false);
  };

  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackBarMessage, setSnackBarMessage] = useState("");
  const [snackBarVariant, setSnackBarVariant] = useState("success");

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpenSnackbar(false);
  };

  const showMessageSnackbar = (variant, message) => {
    setSnackBarMessage(message);
    setSnackBarVariant(variant);
    setOpenSnackbar(true);
  };

  return (
    <>
      <Box className={classes.root}>
        <ErrorBoundary>
          <Header headerTitle={headerTitle} />
        </ErrorBoundary>
        <MainContext.Provider value={{ showMessageSnackbar }}>
          <main className={classes.content}>
            {isShowBannerMaintenance ? (
              <BannerMaintenance
                // eslint-disable-next-line max-len
                text="Our servers will be temporarily unavailable due to scheduled maintenance on May 15, 2023 from 8:00 PM to 9:00 PM PST. We apologize for any inconvenience caused and appreciate your patience!"
                onClose={handleCloseBanner}
              />
            ) : null}
            <Grid container direction="row">
              <Grid item xs={12}>
                {/* <ErrorBoundary> */}
                {isMainScreenLoading ? <AppLoader isOpen={isMainScreenLoading} /> : null}
                <Switch>
                  <Route exact path={ROUTES.MAIN.HOME.path}>
                    <RouterProxyAppMain>
                      <Home />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.MAIN.PROJECT_SUMMARY.path}>
                    <RouterProxyAppMain>
                      <ProjectSummary />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.MAIN.DATA_MANAGER.path}>
                    <RouterProxyAppMain>
                      <TheDataManager />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.MAIN.DATA_EXPLORER.path}>
                    <RouterProxyAppMain>
                      <TheDataExplorer />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.MAIN.MODEL_BUILD.path}>
                    <RouterProxyAppMain>
                      <BuildModel />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.MAIN.MODEL_EXPLORE.path}>
                    <RouterProxyAppMain>
                      <ExploreModels />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.MAIN.MODEL_TEST.path}>
                    <RouterProxyAppMain>
                      <TestModels />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.MAIN.MODEL_DOWNLOAD.path}>
                    <RouterProxyAppMain>
                      <DownloadModel />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.MAIN.MODEL_SELECT.path}>
                    <RouterProxyAppMain>
                      <ModelSelect />
                    </RouterProxyAppMain>
                  </Route>
                  <Route path={ROUTES.DEMO.path}>
                    <RouterProxyAppMain>
                      <Demo />
                    </RouterProxyAppMain>
                  </Route>
                </Switch>
                {/* </ErrorBoundary> */}
              </Grid>
            </Grid>
          </main>
        </MainContext.Provider>
        <Snackbar
          anchorOrigin={{
            vertical: "top",
            horizontal: "right",
          }}
          open={openSnackbar}
          autoHideDuration={2000}
          onClose={handleCloseSnackbar}
        >
          <ToastMessage
            onClose={handleCloseSnackbar}
            variant={snackBarVariant}
            message={snackBarMessage}
          />
        </Snackbar>
      </Box>
    </>
  );
};

export default Main;
