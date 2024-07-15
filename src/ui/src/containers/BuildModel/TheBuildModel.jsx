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

import React, { Suspense, useEffect, lazy } from "react";

import { Redirect, Switch, Route, useParams, generatePath } from "react-router-dom";
import { Box } from "@mui/material";
import { ROUTES } from "routers";

import { AppLoader } from "components/UILoaders";

const TheSelectScreen = lazy(() => import("./TheSelectScreen"));
const TheBuilderScreen = lazy(() => import("./TheBuilderScreen"));

const TheBuildModel = ({ selectedPipeline, loadingPipelineSteps, setLoadingPipelineSteps }) => {
  const { projectUUID } = useParams();

  useEffect(() => {
    setLoadingPipelineSteps(false, "");
  }, []);

  return (
    <Box>
      <Switch>
        <Route path={ROUTES.MAIN.MODEL_BUILD.child.AUTOML_BUILDER_SCREEN.path}>
          <>
            {loadingPipelineSteps.isLoading ? (
              <AppLoader
                isOpen={loadingPipelineSteps.isLoading}
                message={loadingPipelineSteps.message}
                // loadingPipelineSteps
              />
            ) : null}
            <Suspense fallback={<AppLoader isOpen />}>
              <TheBuilderScreen />
            </Suspense>
          </>
        </Route>
        <Route path={ROUTES.MAIN.MODEL_BUILD.child.SELECT_SCREEN.path}>
          <Suspense fallback={<AppLoader isOpen />}>
            <TheSelectScreen />
          </Suspense>
        </Route>
        <Route>
          {selectedPipeline ? (
            <Redirect
              from={ROUTES.MAIN.MODEL_BUILD.path}
              to={{
                pathname: generatePath(ROUTES.MAIN.MODEL_BUILD.child.AUTOML_BUILDER_SCREEN.path, {
                  projectUUID,
                  pipelineUUID: selectedPipeline,
                }),
              }}
            />
          ) : (
            <Redirect
              from={ROUTES.MAIN.MODEL_BUILD.path}
              to={{
                pathname: generatePath(ROUTES.MAIN.MODEL_BUILD.child.SELECT_SCREEN.path, {
                  projectUUID,
                }),
              }}
            />
          )}
        </Route>
      </Switch>
    </Box>
  );
};

export default TheBuildModel;
